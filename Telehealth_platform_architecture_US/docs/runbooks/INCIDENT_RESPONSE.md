# Incident Response Runbook

## Purpose
This runbook provides step-by-step procedures for responding to incidents in the Telehealth Platform.

---

## 1. Database Outage

### Symptoms
- Application errors: "Database connection failed"
- Elevated latency (>5 seconds)
- Cloud SQL monitoring alerts

### Immediate Response

1. **Check Cloud SQL instance status:**
   ```bash
   gcloud sql instances describe telehealth-men-prod --project=your-project-id
   gcloud sql instances describe telehealth-women-prod --project=your-project-id
   gcloud sql instances describe telehealth-phi-prod --project=phi-project-id
   ```

2. **Verify network connectivity:**
   ```bash
   gcloud compute networks subnets list
   gcloud sql instances describe [INSTANCE] | grep ipAddress
   ```

3. **Check for active operations:**
   ```bash
   gcloud sql operations list --instance=telehealth-men-prod
   ```

### Recovery Steps

**If instance is stopped:**
```bash
gcloud sql instances patch [INSTANCE] --activation-policy=ALWAYS
```

**If regional outage:**
1. Promote read replica to master:
   ```bash
   gcloud sql instances promote-replica telehealth-men-replica \
     --project=your-project-id
   ```

2. Update connection strings in application
3. Notify engineering team

**If data corruption:**
1. Identify latest good backup:
   ```bash
   gcloud sql backups list --instance=telehealth-men-prod
   ```

2. Restore from backup:
   ```bash
   gcloud sql backups restore [BACKUP_ID] \
     --backup-instance=telehealth-men-prod \
     --backup-project=your-project-id
   ```

### Post-Incident
- Document timeline in incident report
- Run data integrity checks
- Review and update monitoring thresholds

---

## 2. PHI Data Breach

### Immediate Actions (within 15 minutes)

1. **Isolate affected systems:**
   ```bash
   # Revoke compromised service account permissions
   gcloud projects remove-iam-policy-binding phi-project-id \
     --member=serviceAccount:compromised@project.iam.gserviceaccount.com \
     --role=roles/cloudsql.client
   ```

2. **Enable audit log export:**
   ```bash
   gcloud logging read "resource.type=cloudsql_database" \
     --limit=1000 \
     --format=json > phi_access_logs_$(date +%Y%m%d_%H%M%S).json
   ```

3. **Alert compliance team** via PagerDuty

### Investigation (within 1 hour)

1. **Query PHI access logs:**
   ```sql
   SELECT 
     accessed_at,
     user_email,
     patient_uuid,
     access_type,
     ip_address
   FROM compliance_audit_prod.phi_access_log
   WHERE accessed_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
     AND (
       is_suspicious = TRUE 
       OR access_count > 100
     )
   ORDER BY accessed_at DESC;
   ```

2. **Identify scope of breach:**
   - Number of patient records accessed
   - Type of PHI exposed (name, SSN, medical history)
   - Duration of unauthorized access

### Notification Requirements

**If >500 patients affected:**
- Notify HHS within 60 days
- Notify affected individuals within 60 days
- Issue public statement if >500 patients in same jurisdiction

**If <500 patients affected:**
- Maintain log for annual HHS report
- Notify affected individuals within 60 days

### Remediation
1. Rotate all credentials
2. Implement additional access controls
3. Schedule security audit
4. Update incident response procedures

---

## 3. BigQuery Query Failure

### Symptoms
- dbt run failures
- Looker dashboards showing "Query timeout"
- High query costs

### Diagnosis

1. **Check running queries:**
   ```bash
   bq ls -j -a --max_results=10 --project_id=your-project-id
   ```

2. **Identify slow queries:**
   ```sql
   SELECT
     job_id,
     user_email,
     query,
     total_slot_ms,
     total_bytes_processed
   FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
   WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
     AND total_slot_ms > 10000000
   ORDER BY total_slot_ms DESC
   LIMIT 10;
   ```

### Resolution

**Cancel expensive queries:**
```bash
bq cancel [JOB_ID]
```

**Optimize table partitioning:**
```sql
CREATE OR REPLACE TABLE analytics_prod.gold_patient_journey
PARTITION BY DATE(created_at)
CLUSTER BY patient_uuid, product_id
AS SELECT * FROM analytics_prod.gold_patient_journey_old;
```

**Set query cost limits:**
```bash
bq update --maximum_bytes_billed=10000000000 your-project-id
```

---

## 4. Debezium CDC Pipeline Failure

### Symptoms
- Replication lag >5 minutes
- Kafka Connect errors in logs
- Real-time dashboards stale

### Diagnosis

1. **Check connector status:**
   ```bash
   curl http://kafka-connect:8083/connectors/men-health-connector/status
   ```

2. **View connector logs:**
   ```bash
   kubectl logs -f deployment/kafka-connect -n telehealth
   ```

3. **Check Kafka lag:**
   ```bash
   kafka-consumer-groups --bootstrap-server kafka:9092 \
     --group debezium-connector --describe
   ```

### Recovery

**Restart failed connector:**
```bash
curl -X POST http://kafka-connect:8083/connectors/men-health-connector/restart
```

**Reset connector position (if corrupted):**
```bash
curl -X DELETE http://kafka-connect:8083/connectors/men-health-connector
curl -X POST -H "Content-Type: application/json" \
  --data @debezium/connectors/men-health-connector.json \
  http://kafka-connect:8083/connectors
```

**Manual sync if CDC broken:**
```bash
cd dbt
dbt run --select bronze --full-refresh
```

---

## 5. Airflow DAG Failure

### Symptoms
- DAG marked as failed in Airflow UI
- Data freshness alerts
- Downstream dependencies blocked

### Investigation

1. **Check DAG run logs:**
   - Navigate to Airflow UI → DAGs → [DAG_NAME] → Graph View
   - Click failed task → View Logs

2. **Common failure causes:**
   - External API timeout
   - BigQuery quota exceeded
   - Data validation failure (Great Expectations)

### Recovery

**Retry failed task:**
```bash
gcloud composer environments run telehealth-composer \
  --location us-central1 \
  tasks clear dbt_transformations_dag -t [TASK_ID] -s [EXECUTION_DATE]
```

**Backfill missed runs:**
```bash
gcloud composer environments run telehealth-composer \
  --location us-central1 \
  dags backfill dbt_transformations_dag \
  -s 2026-03-01 -e 2026-03-14
```

**Manual data fix:**
```sql
-- If transformation failed, fix source data
DELETE FROM analytics_prod.bronze_men_products
WHERE processed_at >= '2026-03-14';

-- Re-run dbt
dbt run --select bronze_men_products+
```

---

## Escalation Contacts

| Incident Type | Primary Contact | Secondary Contact |
|---------------|----------------|-------------------|
| PHI Breach | CISO | Legal Team |
| Database Outage | DevOps Lead | Database Admin |
| Infrastructure | Cloud Architect | DevOps Team |
| Application Bug | Engineering Lead | On-call Engineer |

## On-Call Schedule
- PagerDuty schedule: https://telehealth.pagerduty.com/schedules
- Escalation policy: Page → 15 min → Escalate to manager

---

*Last Updated: March 14, 2026*
