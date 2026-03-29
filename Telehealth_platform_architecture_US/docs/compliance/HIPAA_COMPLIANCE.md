# HIPAA Compliance Guide

## Overview
This document outlines the HIPAA compliance measures implemented in the telehealth data architecture.

## Architecture for Compliance

### 1. PHI Isolation
- **Separate GCP Project**: PHI database resides in a dedicated GCP project (`telehealth-phi-prod`)
- **Network Isolation**: Private VPC with strict firewall rules
- **Access Control**: Separate IAM policies with principle of least privilege
- **Encryption**: 
  - At rest: Google-managed encryption keys + column-level encryption for SSN
  - In transit: TLS 1.3 enforced for all connections

### 2. De-identification Strategy

#### Patient UUID Tokenization
```
Operational DBs (men's/women's health):
  └─> patient_uuid (anonymous identifier)
  
PHI Database:
  ├─> patient_uuid (links to operational DBs)
  ├─> Full PHI (name, DOB, SSN, address, etc.)
  └─> token_vault (reversible mapping)
  
Analytics (BigQuery):
  └─> patient_token_hash (one-way hash)
```

#### HIPAA Safe Harbor Method
All analytics datasets remove/mask the 18 identifiers:
1. Names
2. Geographic subdivisions smaller than state
3. Dates (except year) 
4. Phone numbers
5. Fax numbers
6. Email addresses
7. SSN
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers/serial numbers
14. Web URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photos
18. Any other unique identifying number

#### K-Anonymity Validation
- All published datasets validated for k≥5
- dbt macro `validate_k_anonymity` checks group sizes
- Failed validations trigger alerts

### 3. Access Control

#### Role-Based Access Control (RBAC)

**Clinical Staff**:
- Read access to PHI database
- Limited to patients under their care
- MFA required
- Access logged with justification

**Data Engineers**:
- No direct PHI access
- Access to de-identified analytics only
- Development in separate project/environment

**Break-Glass Access**:
- Emergency access for critical situations
- Requires approval workflow
- Automatically logged and reviewed
- Alerts sent to security team

#### IAM Policies
```
PHI Project:
- healthcare.piiReader - Clinical staff only
- bigquery.dataViewer - NO ONE (prevent query access)
- logging.viewer - Compliance team only

Analytics Project:
- bigquery.dataViewer - Data analysts, BI team
- bigquery.user - Data scientists for queries
```

### 4. Audit Logging

#### What We Log
1. **PHI Access Logs** (`phi_access_logs` table):
   - User ID and role
   - Patient UUID accessed
   - Access type (read/write/export)
   - Timestamp
   - IP address and user agent
   - Access reason/justification
   - Break-glass flag

2. **Database Audit Logs** (`audit_logs` table):
   - All INSERT/UPDATE/DELETE operations
   - Before/after snapshots
   - User context

3. **BigQuery Audit Logs**:
   - All queries executed
   - Data accessed
   - Export operations

#### Retention
- **7 years**: All PHI access logs (stored in GCS Archive)
- **7 years**: Database audit logs
- **1 year**: Application logs (hot storage)
- **90 days**: BigQuery query logs (hot storage)

### 5. Data Lifecycle

#### Ingestion
```
Operational DB (PHI removed) 
  → Debezium CDC 
  → Kafka 
  → Pub/Sub 
  → BigQuery Bronze (anonymous)
```

#### PHI Handling
- PHI NEVER leaves PHI database
- PHI NEVER enters Kafka/Pub/Sub/BigQuery
- Patient identifiers tokenized at source

#### Deletion Requests (Right to be Forgotten)
1. Patient requests deletion
2. Compliance team validates request
3. Script runs to:
   - Delete from PHI database
   - Tombstone operational records
   - Invalidate token hash in analytics
   - Audit trail preserved (without PHI)

### 6. Security Measures

#### Network Security
- Private VPC with no internet egress
- Cloud SQL private IP only
- VPC peering for cross-project access
- Cloud Armor for DDoS protection

#### Application Security
- Service accounts with workload identity
- Secrets stored in Secret Manager (rotated quarterly)
- No credentials in code/config
- API authentication via OAuth 2.0

#### Monitoring & Alerting
- Real-time anomaly detection on PHI access
- Alert on bulk exports
- Alert on access outside business hours
- Alert on repeated failed access attempts

### 7. Business Associate Agreements (BAAs)

Required BAAs in place for:
- ✅ GCP (Google Cloud Platform)
- ✅ Debezium/Confluent Cloud (Kafka)
- ✅ Compounding pharmacy partners
- ✅ Lab partners (Quest, LabCorp)
- ✅ EMR/EHR integration vendors
- ✅ Identity verification services

### 8. Compliance Validation

#### Regular Audits
- **Weekly**: Automated compliance checks
- **Monthly**: Access log review
- **Quarterly**: Security audit
- **Annually**: Third-party penetration test

#### Validation Queries
```sql
-- Check for PHI in analytics datasets
SELECT column_name
FROM `analytics_prod.INFORMATION_SCHEMA.COLUMNS`
WHERE column_name IN (
  'ssn', 'social_security_number', 'first_name', 
  'last_name', 'email', 'phone_number', 'date_of_birth'
)
-- Should return 0 rows

-- Verify all PHI access is logged
SELECT COUNT(*) 
FROM `telehealth-phi-prod.phi.phi_access_logs`
WHERE DATE(accessed_at) = CURRENT_DATE()
-- Should match daily active users

-- Check k-anonymity
SELECT COUNT(*) as group_count
FROM (
  SELECT state, age_bucket, gender, COUNT(*) as patients
  FROM `analytics_prod.gold.patient_demographics_aggregate`
  GROUP BY state, age_bucket, gender
  HAVING COUNT(*) < 5
)
-- Should be 0
```

### 9. Incident Response

#### Data Breach Protocol
1. **Detect**: Automated alerts + manual review
2. **Contain**: Revoke access, isolate systems
3. **Assess**: Determine scope of breach
4. **Notify**: 
   - Affected patients (within 60 days)
   - HHS OCR (within 60 days if >500 individuals)
   - Media (if >500 individuals in same state/jurisdiction)
5. **Remediate**: Fix vulnerability
6. **Document**: Full incident report

#### Contact
- Security Team: security@telehealth.com
- Compliance Officer: compliance@telehealth.com
- 24/7 Hotline: 1-800-xxx-xxxx

## Training Requirements

All staff with PHI access must complete:
- HIPAA Privacy Rule training (annually)
- HIPAA Security Rule training (annually)
- Data handling procedures (quarterly refresher)
- Incident response procedures (annually)

## References
- [45 CFR Part 160](https://www.hhs.gov/hipaa/for-professionals/privacy/laws-regulations/index.html) - HIPAA Privacy Rule
- [45 CFR Part 164](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html) - HIPAA Security Rule
- [GCP HIPAA Implementation Guide](https://cloud.google.com/security/compliance/hipaa)
