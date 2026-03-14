# Disaster Recovery Runbook

## Overview
This runbook provides procedures for disaster recovery scenarios including regional outages, data loss, and catastrophic failures.

**Recovery Objectives:**
- **RPO (Recovery Point Objective):** < 1 minute
- **RTO (Recovery Time Objective):** < 1 minute for automated failover

---

## Pre-Disaster Preparation Checklist

- [ ] Automated backups enabled (every 4 hours)
- [ ] Cross-region replication active
- [ ] Failover procedures tested quarterly
- [ ] Recovery contact list updated
- [ ] Backup restoration tested monthly

---

## Scenario 1: Regional GCP Outage

### Detection
- Multiple Cloud SQL instances unreachable
- BigQuery queries failing with regional errors
- Cloud Monitoring alerts: "Regional outage detected"

### Immediate Actions (within 5 minutes)

1. **Verify outage scope:**
   - Check GCP Status Dashboard: https://status.cloud.google.com
   - Confirm multi-service impact in region

2. **Activate failover to secondary region:**

   ```bash
   # Promote read replicas to primary
   gcloud sql instances promote-replica telehealth-men-prod-us-west1 \
     --project=your-project-id
   
   gcloud sql instances promote-replica telehealth-women-prod-us-west1 \
     --project=your-project-id
   
   gcloud sql instances promote-replica telehealth-phi-prod-us-west1 \
     --project=phi-project-id
   ```

3. **Update DNS to point to secondary region:**
   ```bash
   gcloud dns record-sets transaction start --zone=telehealth-zone
   gcloud dns record-sets transaction remove \
     --zone=telehealth-zone \
     --name=api.telehealth.com \
     --type=A \
     --ttl=300 \
     [PRIMARY_REGION_IP]
   
   gcloud dns record-sets transaction add \
     --zone=telehealth-zone \
     --name=api.telehealth.com \
     --type=A \
     --ttl=300 \
     [SECONDARY_REGION_IP]
   
   gcloud dns record-sets transaction execute --zone=telehealth-zone
   ```

4. **Redirect BigQuery workloads:**
   - Update dbt profiles.yml to use multi-region dataset
   - Restart Airflow DAGs with new configuration

### Validation (within 10 minutes)

1. **Test database connectivity:**
   ```bash
   psql "host=[FAILOVER_IP] port=5432 dbname=telehealth_men_prod" \
     -c "SELECT COUNT(*) FROM products;"
   ```

2. **Verify application health:**
   ```bash
   curl https://api.telehealth.com/health
   ```

3. **Check data replication lag:**
   ```sql
   SELECT 
     pg_last_wal_receive_lsn(),
     pg_last_wal_replay_lsn(),
     pg_last_wal_replay_lsn() = pg_last_wal_receive_lsn() AS is_synced
   FROM pg_stat_wal_receiver;
   ```

### Post-Recovery

- Monitor for 24 hours
- Document timeline
- Schedule post-mortem
- Test failback when primary region restored

---

## Scenario 2: Data Corruption / Accidental Deletion

### Detection
- Data validation tests failing
- User reports of missing data
- Unexpected row count drops

### Immediate Actions

1. **Identify corruption scope:**
   ```sql
   -- Check for data anomalies
   SELECT 
     DATE(updated_at) as date,
     COUNT(*) as row_count
   FROM products
   GROUP BY DATE(updated_at)
   ORDER BY date DESC
   LIMIT 7;
   
   -- Compare with yesterday
   SELECT COUNT(*) FROM products 
   WHERE created_at < CURRENT_DATE;
   ```

2. **Stop all write operations:**
   ```bash
   # Pause Airflow DAGs
   gcloud composer environments run telehealth-composer \
     --location us-central1 \
     dags pause dbt_transformations_dag
   
   # Put application in read-only mode
   kubectl scale deployment telehealth-api --replicas=0
   ```

3. **Identify good backup:**
   ```bash
   gcloud sql backups list --instance=telehealth-men-prod \
     --limit=10
   ```

### Recovery

**Option A: Point-in-time recovery (if <7 days ago)**

```bash
gcloud sql instances clone telehealth-men-prod \
  telehealth-men-prod-clone \
  --point-in-time='2026-03-14T10:00:00Z'

# Verify clone
psql "host=[CLONE_IP] dbname=telehealth_men_prod" \
  -c "SELECT COUNT(*) FROM products;"

# If verified, swap instances
gcloud sql instances delete telehealth-men-prod --quiet
gcloud sql instances clone telehealth-men-prod-clone \
  telehealth-men-prod
```

**Option B: Restore from backup**

```bash
gcloud sql backups restore [BACKUP_ID] \
  --backup-instance=telehealth-men-prod \
  --backup-project=your-project-id
```

### Post-Recovery Validation

1. **Run data quality tests:**
   ```bash
   cd dbt
   dbt test --select bronze silver gold
   ```

2. **Verify BigQuery sync:**
   ```sql
   SELECT 
     MAX(processed_at) as latest_sync
   FROM analytics_prod.bronze_men_products;
   ```

3. **Resume operations:**
   ```bash
   kubectl scale deployment telehealth-api --replicas=3
   gcloud composer environments run telehealth-composer \
     --location us-central1 \
     dags unpause dbt_transformations_dag
   ```

---

## Scenario 3: Total Infrastructure Loss

### Rebuilding from Scratch

1. **Restore infrastructure via Terraform:**
   ```bash
   cd terraform
   terraform init
   terraform plan -out=recovery.tfplan
   terraform apply recovery.tfplan
   ```

2. **Restore databases from backups:**
   ```bash
   # Databases will be created by Terraform
   # Restore latest backups automatically applied
   ```

3. **Recreate BigQuery datasets:**
   ```bash
   bq mk --dataset --location=US analytics_prod
   bq mk --dataset --location=US compliance_audit_prod
   bq mk --dataset --location=US ml_features_prod
   ```

4. **Rebuild dbt models:**
   ```bash
   cd dbt
   dbt deps
   dbt run --full-refresh
   ```

5. **Deploy Airflow DAGs:**
   ```bash
   gcloud composer environments storage dags import \
     --environment=telehealth-composer \
     --location=us-central1 \
     --source=airflow/dags/*.py
   ```

6. **Restore Debezium connectors:**
   ```bash
   for connector in debezium/connectors/*.json; do
     curl -X POST -H "Content-Type: application/json" \
       --data @$connector \
       http://kafka-connect:8083/connectors
   done
   ```

---

## Scenario 4: Ransomware Attack

### Immediate Containment

1. **Isolate affected systems:**
   ```bash
   # Remove all IAM permissions
   gcloud projects remove-iam-policy-binding your-project-id \
     --member=allUsers \
     --role=roles/viewer
   
   # Disable all service accounts
   gcloud iam service-accounts disable [SERVICE_ACCOUNT_EMAIL]
   ```

2. **Snapshot current state (for forensics):**
   ```bash
   gcloud compute disks snapshot [DISK_NAME] \
     --snapshot-names=ransomware-forensics-$(date +%Y%m%d)
   ```

3. **Do NOT pay ransom** - consult with legal and law enforcement

### Recovery

1. **Restore from backups before infection:**
   - Use procedure from Scenario 2
   - Ensure backups are from before ransomware activation

2. **Scan restored systems:**
   ```bash
   # Run security scans on all instances
   gcloud compute instances get-serial-port-output [INSTANCE]
   ```

3. **Rotate all credentials:**
   ```bash
   # Rotate database passwords
   gcloud sql users set-password [USER] \
     --instance=[INSTANCE] \
     --password=[NEW_PASSWORD]
   
   # Rotate service account keys
   gcloud iam service-accounts keys create new-key.json \
     --iam-account=[SERVICE_ACCOUNT_EMAIL]
   ```

---

## Backup Verification Procedure

**Run monthly to ensure backups are restorable:**

```bash
#!/bin/bash
# Monthly backup restoration test

# 1. Create test restore
gcloud sql instances clone telehealth-men-prod \
  backup-test-$(date +%Y%m) \
  --point-in-time='yesterday'

# 2. Run validation queries
psql "host=[TEST_IP] dbname=telehealth_men_prod" <<EOF
SELECT 'Products count:', COUNT(*) FROM products;
SELECT 'Orders count:', COUNT(*) FROM orders;
SELECT 'Prescriptions count:', COUNT(*) FROM prescriptions;
EOF

# 3. Delete test instance
gcloud sql instances delete backup-test-$(date +%Y%m) --quiet

echo "Backup verification complete. Document results."
```

---

## Recovery Time Estimates

| Scenario | RTO Target | Actual (tested) | Notes |
|----------|-----------|-----------------|-------|
| Regional failover | 1 minute | 45 seconds | Automated |
| Database restore (point-in-time) | 30 minutes | 25 minutes | Depends on DB size |
| Full infrastructure rebuild | 2 hours | 1.5 hours | Terraform automation |
| BigQuery full rebuild | 4 hours | 3.5 hours | dbt full-refresh |

---

## Communication Templates

### Customer Notification (Outage)

```
Subject: Service Disruption Notice - [DATE]

Dear Valued Customer,

We are currently experiencing technical difficulties that may affect 
your ability to access our telehealth services. Our engineering team 
is actively working to resolve the issue.

Expected Resolution: [TIME]
Status Updates: Check status.telehealth.com

We apologize for any inconvenience.

Telehealth Platform Team
```

### HIPAA Breach Notification

```
Subject: Important Notice Regarding Your Protected Health Information

[Full legal template - consult with legal team]
```

---

*Last Updated: March 14, 2026*  
*Next DR Test Scheduled: June 14, 2026*
