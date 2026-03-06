# Plan: Telehealth Platform Data Architecture & ETL Pipeline (GCP + PostgreSQL/Prisma)

**TL;DR**: Design a HIPAA-compliant, multi-brand (men's/women's health) telehealth data platform on GCP with separate PHI isolation, real-time inventory tracking, and comprehensive analytics. Architecture uses Cloud SQL PostgreSQL (operational), BigQuery (warehouse), Debezium CDC, Airflow orchestration, and dbt transformations with Great Expectations validation across bronze/silver/gold layers.

---

## Database Architecture

### 1. Database Separation Strategy
**Operational Databases (Cloud SQL PostgreSQL)**:
- `telehealth_men_prod` - Men's health brand operational database
- `telehealth_women_prod` - Women's health brand operational database
- `telehealth_phi_prod` - Isolated PHI database (separate project, stricter IAM)
- `telehealth_shared_prod` - Shared resources (providers, protocols, reference data)

**Analytics Warehouse (BigQuery)**:
- `analytics_prod` dataset - De-identified analytics data
- `compliance_audit_prod` dataset - Audit logs and compliance reporting
- `ml_features_prod` dataset - Feature store for ML models

### 2. Data Domain Schemas

**Pharmaceutical Data** (men's/women's databases):
- Products catalog (GLP-1, peptides, ED, hair growth, stamina, HRT)
- Inventory (real-time stock levels by fulfillment partner)
- Drug interactions and contraindications
- FDA/DEA tracking metadata

**Protected Health Information (PHI)** (phi database):
- Patient demographics (name, DOB, SSN, address)
- Medical history and conditions
- Consultation notes and assessments
- Prescriptions (linked to anonymized patient_id in operational DBs)
- Lab results
- Adverse event reports
- Consent forms and authorizations

**Healthcare/Clinical Data** (operational databases):
- Anonymized patient records (using patient_uuid)
- Consultation sessions (async/video)
- Treatment plans and clinical protocols
- Prescription states (pending/approved/filled/shipped)
- Refill schedules and auto-refill preferences
- Quality metrics and clinical outcomes

**Operational Data** (operational databases):
- Orders and order line items
- Fulfillment workflows (compounding pharmacy integration)
- Shipping and logistics tracking
- Return/refund management
- Inventory adjustments and transfers

**Customer/Marketing/Sales Data** (operational databases):
- Customer profiles (anonymized, no PHI)
- Marketing campaigns and attribution
- Subscription management (billing cycles)
- One-time purchase transactions
- Customer segmentation tags
- Support tickets and interactions

**Provider/Practitioner Data** (shared database):
- Provider credentials and licensing
- Multi-state licensing validation
- DEA registration for controlled substances
- Availability schedules
- Performance metrics

### 3. Cross-Cutting Concerns

**Audit Logging** (all databases):
- PHI access logs (who, what, when, why)
- Data modification history (temporal tables)
- Authentication/authorization events
- Prescription approval audit trail

**Reference Data** (shared database):
- State telehealth regulations
- Drug formularies and NDC codes
- ICD-10 / CPT codes
- Insurance payer information

---

## Data Pipeline Architecture

### 1. Data Flow Layers (Medallion Architecture)

**Bronze Layer (Raw)** - Landing zone in BigQuery:
- Ingest raw data from all sources via Debezium CDC, API webhooks, batch uploads
- Minimal transformations (type casting, timestamp standardization)
- Preserve complete history and audit trail
- Tables: `bronze_<source>_<table>`

**Silver Layer (Staging/Cleaned)** - Curated data in BigQuery:
- Data cleaning and validation (Great Expectations)
- Schema normalization and deduplication
- Join related entities across sources
- Apply business rules
- Tables: `silver_<domain>_<entity>`

**Gold Layer (Production)** - Analytics-ready in BigQuery:
- Denormalized dimensional models (star/snowflake)
- Pre-aggregated metrics
- De-identified datasets for analytics
- ML feature engineering
- Tables: `gold_<use_case>_<entity>`

### 2. Real-Time vs Batch Processing

**Real-Time (Debezium CDC)**:
- Inventory changes → BigQuery for real-time dashboards
- Order status updates → BigQuery for customer-facing tracking
- Prescription approvals → BigQuery for provider dashboards
- PHI access events → BigQuery compliance dataset

**Batch Processing (Airflow DAGs)**:
- Nightly: External integrations (EMR/EHR, lab results, shipping updates)
- Hourly: Marketing attribution, customer segmentation
- Daily: Financial reconciliation, compliance reports
- Weekly: ML model training, churn prediction

### 3. Pipeline Components

**Ingestion**:
- Debezium (Kafka Connect) → PostgreSQL WAL → Pub/Sub → BigQuery Streaming
- Cloud Functions for webhook handlers (Stripe, shipping providers)
- Scheduled batch jobs (Airflow) for EMR/EHR, lab partners, CRM
- Identity verification API polling

**Transformation (dbt)**:
- Bronze → Silver: data cleaning, validation, deduplication
- Silver → Gold: dimensional modeling, aggregations, de-identification
- Incremental models for large fact tables
- dbt tests for schema validation and business rules

**Validation (Great Expectations)**:
- Pre-transformation: validate raw data quality
- Post-transformation: validate business rules
- Alert on data quality issues (PagerDuty/Slack)

**Orchestration (Cloud Composer/Airflow)**:
- DAG for each data domain (pharmaceutical, clinical, operational, marketing)
- Dependency management across domains
- Retry policies and alerting
- Backfill support for historical data

---

## HIPAA Compliance Architecture

### 1. PHI Isolation
- Separate GCP project for PHI database (stricter IAM, VPC, audit logging)
- Encryption at rest (Google-managed keys) and in transit (TLS 1.3)
- Column-level encryption for highly sensitive fields (SSN, consent forms)
- No PHI in application logs or error messages

### 2. De-identification Strategy
- Generate `patient_uuid` in operational databases (reversible via secure token vault in PHI DB)
- BigQuery analytics uses only de-identified data
- HIPAA Safe Harbor method: remove 18 identifiers
- k-anonymity checks before publishing analytics datasets

### 3. Access Control
- Role-based access control (RBAC) via IAM
- Minimum necessary access principle
- Break-glass access for emergencies (logged and reviewed)
- Time-limited access grants for contractors/auditors

### 4. Audit & Monitoring
- All PHI access logged to immutable audit tables
- 7-year retention in cold storage (GCS Nearline/Archive)
- Real-time alerts for anomalous access patterns
- Quarterly audit reports for compliance review

---

## Steps

### Phase 1: Foundation (Weeks 1-3)
1. **Set up GCP infrastructure** - Create projects (operational, PHI, analytics), VPCs, IAM roles, Cloud SQL instances, BigQuery datasets
2. **Define Prisma schemas** - Model all data domains (pharmaceutical, clinical, operational, etc.) across 4 operational databases
3. **Implement PHI tokenization** - Secure token vault for patient_uuid ↔ PHI mapping, encryption for sensitive columns
4. **Set up audit logging** - Temporal tables in PostgreSQL, audit log tables in BigQuery compliance dataset

### Phase 2: Data Ingestion (Weeks 3-5)
5. **Deploy Debezium CDC pipeline** - PostgreSQL → Kafka (Confluent Cloud) → Pub/Sub → BigQuery for real-time sync
6. **Build external integration adapters** (*parallel with step 5*) - Airflow DAGs for EMR/EHR, lab partners, pharmacy partners, payment processors, shipping APIs, CRM, identity verification
7. **Create bronze layer tables in BigQuery** - Raw data landing zone with schema evolution enabled

### Phase 3: Transformation & Quality (Weeks 5-7)
8. **Develop dbt models** - Bronze → Silver → Gold transformations for each data domain
9. **Implement Great Expectations suites** (*parallel with step 8*) - Data quality validation at bronze/silver boundaries
10. **Build de-identification logic** - dbt macros for HIPAA Safe Harbor de-identification, k-anonymity validation

### Phase 4: Analytics & Reporting (Weeks 7-9)
11. **Design dimensional models in gold layer** - Star schemas for business intelligence (patient journey, product performance, provider metrics, financial reporting)
12. **Set up Looker Studio dashboards** - Real-time inventory, operational metrics, provider dashboards, financial reconciliation
13. **Build ML feature pipelines** (*parallel with step 12*) - Feature engineering for customer segmentation, churn prediction, product recommendations, clinical decision support

### Phase 5: Migration & Cutover (Weeks 9-11)
14. **Migrate existing database (100GB-1TB)** - Use Database Migration Service for minimal downtime, parallel validation
15. **Backfill historical data** - Run dbt models for all historical data, validate completeness
16. **Load testing and optimization** - Simulate 10K-100K user load, optimize indexes, partitioning, and query performance

### Phase 6: Compliance & Production Readiness (Weeks 11-12)
17. **Security & compliance audit** - Penetration testing, HIPAA compliance review, SOC 2 readiness
18. **Disaster recovery testing** - Multi-region failover, RPO/RTO validation (< 1 min), backup restoration
19. **Production cutover** - Blue-green deployment, staged rollout per state/brand

---

## Relevant Files & Technologies

**Database Layer**:
- Prisma schema files defining models for each database
- PostgreSQL temporal tables for audit history
- Trigger functions for PHI access logging

**Ingestion Layer**:
- Debezium connector configurations (JSON)
- Airflow DAG files for batch ingestion
- Cloud Functions for webhook handlers

**Transformation Layer**:
- dbt project with models/, macros/, tests/, seeds/
- Great Expectations checkpoint configurations
- De-identification SQL functions

**Infrastructure as Code**:
- Terraform modules for GCP resources (Cloud SQL, VPCs, IAM, BigQuery)
- Kubernetes manifests for Debezium connectors (if self-hosted)

**Monitoring & Alerting**:
- Cloud Monitoring dashboards for pipeline health
- Alerting policies for data quality failures
- PagerDuty integration for on-call

---

## Verification

1. **HIPAA Compliance Validation** - Run penetration test, verify no PHI in analytics datasets, confirm all PHI access is audited
2. **Data Quality Tests** - Execute Great Expectations suites, verify dbt test pass rates > 99.5%
3. **Performance Testing** - Load test with 100K simulated users, verify query latency < 100ms for operational reads, < 5s for analytics queries
4. **Disaster Recovery Drill** - Simulate regional outage, verify failover time < 1 minute, validate data consistency
5. **End-to-End Data Lineage** - Trace sample patient record from operational DB → BigQuery gold layer, verify de-identification
6. **Real-Time Dashboard Validation** - Verify inventory updates appear in Looker Studio within 30 seconds of DB change
7. **Integration Testing** - Validate all external integrations (EMR/EHR, labs, pharmacy, payment, shipping, CRM, identity verification)
8. **Migration Validation** - Compare row counts, checksums, and sample queries between old and new databases
9. **Multi-State Compliance Check** - Verify data residency and provider licensing tracking for all 50 states
10. **Audit Log Completeness** - Verify 100% of PHI access events are logged with required metadata (who, what, when, why, where)

---

## Decisions & Assumptions

**Decisions**:
- Separate databases for men's/women's brands (isolation, independent scaling, separate compliance audits)
- PHI in dedicated database/project (HIPAA security rule compliance)
- BigQuery for analytics warehouse (cost-effective for 10K-100K users, scales to millions)
- Debezium CDC for real-time sync (mature Kafka ecosystem, supports complex transformations)
- Cloud Composer (Airflow) over Prefect/Dagster (GCP-native, easier for 2-5 engineer team)
- dbt + Great Expectations (industry standard for transformation + validation)
- 7-year retention for all healthcare data (compliance + potential class-action defense)
- Multi-region HA with < 1 min RTO (high patient trust, revenue protection)

**Assumptions**:
- Compounding pharmacy partners have APIs or HL7/FHIR interfaces (not manual data entry)
- State telehealth regulations allow asynchronous consultations for all product categories
- DEA-controlled substances (if any) require additional workflow approval steps
- Payment processing (Stripe) handles PCI-DSS compliance (no raw card data in databases)
- Existing 100GB-1TB database can be migrated with < 4 hours downtime
- Clinical decision support ML models will be trained externally and called via API
- Synthetic PHI for production testing environment can be generated via tools like Synthea

**Scope Inclusions**:
- Complete data architecture for all 4 data domains (pharmaceutical, healthcare, operational, customer/marketing/sales)
- Provider/practitioner data management
- Clinical protocols and treatment plans
- Adverse event reporting (FDA compliance)
- Multi-state provider licensing tracking
- Prescription workflow and refill management
- Subscription billing and one-time purchases
- Data lineage for compliance
- Real-time inventory tracking
- Patient de-identification for analytics

**Scope Exclusions**:
- Insurance claims processing (adjudication, eligibility verification)
- FSA/HSA card processing (requires third-party integration)
- Video consultation platform data storage (vendor-hosted, integration only)
- Mobile app push notification orchestration
- Customer service chatbot/AI agent training
- A/B testing framework
- Email/SMS marketing automation (CRM-owned)

---

## Further Considerations

**1. State Data Residency**: Some states may require patient data to be stored within state borders. **Recommendation**: Start with single GCP region (us-central1), add regional Cloud SQL read replicas if state laws require.

**2. Controlled Substance Tracking**: If offering Schedule II-V substances, need enhanced DEA reporting. **Recommendation**: Implement EPCS (Electronic Prescriptions for Controlled Substances) integration and separate audit tables for controlled substance prescriptions.

**3. Adverse Event Reporting Automation**: FDA requires adverse event reporting within 15 days. **Recommendation**: Build automated detection rules (dbt models) to flag potential adverse events from consultation notes, lab results, and customer support tickets for manual review.

**4. Data Anonymization for Dev/Staging**: Synthetic PHI generation may not cover all edge cases. **Recommendation**: Use tools like PostgreSQL Anonymizer or Gretel.ai to generate realistic synthetic data from production schemas.

**5. Cost Optimization**: BigQuery can get expensive with real-time streaming. **Recommendation**: Use partitioning (by date) and clustering (by patient_uuid, product_id) on all tables, set up query cost alerts.

---

This plan addresses:
✅ **All data domains**: Pharmaceutical, Healthcare/PHI, Operational, Customer/Marketing/Sales, Provider/Practitioner, Clinical Protocols, Adverse Events  
✅ **HIPAA compliance**: Separate PHI database, de-identification, audit logging, encryption  
✅ **Multi-brand architecture**: Separate databases for men's/women's health websites  
✅ **Real-time + batch**: Debezium CDC for inventory/dashboards, Airflow for external integrations  
✅ **Data quality**: Great Expectations + dbt tests across bronze/silver/gold layers  
✅ **Scalability**: Cloud SQL + BigQuery handles 10K-100K users initially, scales to millions  
✅ **Disaster recovery**: Multi-region HA with < 1 min RTO  
✅ **Compliance**: State telehealth laws, FDA (peptides), DEA (controlled substances), PCI-DSS, SOC 2
