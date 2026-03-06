# Telehealth Platform Data Architecture & ETL Pipeline

A HIPAA-compliant, multi-brand telehealth data platform on GCP with separate PHI isolation, real-time inventory tracking, and comprehensive analytics.

## 🏗️ Architecture Overview

This project implements a complete data architecture for a telehealth platform serving men's and women's health products (GLP-1, peptides, ED medication, HRT, etc.) with:

- **Multi-database strategy**: Separate databases for brand isolation and PHI compliance
- **Real-time CDC pipeline**: Debezium → Kafka → Pub/Sub → BigQuery
- **Medallion architecture**: Bronze (raw) → Silver (cleaned) → Gold (analytics-ready)
- **HIPAA compliance**: PHI isolation, de-identification, audit logging, encryption

## 🗄️ Database Architecture

### Operational Databases (Cloud SQL PostgreSQL)
- `telehealth_men_prod` - Men's health brand operational database
- `telehealth_women_prod` - Women's health brand operational database
- `telehealth_phi_prod` - Isolated PHI database (separate project, stricter IAM)
- `telehealth_shared_prod` - Shared resources (providers, protocols, reference data)

### Analytics Warehouse (BigQuery)
- `analytics_prod` - De-identified analytics data
- `compliance_audit_prod` - Audit logs and compliance reporting
- `ml_features_prod` - Feature store for ML models

## 📊 Data Domains

1. **Pharmaceutical Data**: Products, inventory, drug interactions, FDA/DEA tracking
2. **Protected Health Information (PHI)**: Demographics, medical history, prescriptions, lab results
3. **Healthcare/Clinical**: Consultations, treatment plans, clinical outcomes
4. **Operational**: Orders, fulfillment, shipping, inventory management
5. **Customer/Marketing**: Profiles, campaigns, subscriptions, segmentation
6. **Provider/Practitioner**: Credentials, licensing, scheduling, performance metrics

## 🚀 Technology Stack

- **Databases**: PostgreSQL (Cloud SQL), BigQuery
- **ORM**: Prisma
- **CDC**: Debezium, Kafka/Confluent Cloud, Pub/Sub
- **Orchestration**: Apache Airflow (Cloud Composer)
- **Transformation**: dbt, Great Expectations
- **Infrastructure**: GCP, Terraform
- **Monitoring**: Cloud Monitoring, PagerDuty
- **BI**: Looker Studio

## 📁 Project Structure

```
.
├── prisma/                     # Database schemas and migrations
│   ├── men_health/
│   ├── women_health/
│   ├── phi/
│   └── shared/
├── dbt/                        # Data transformations
│   ├── models/
│   │   ├── bronze/            # Raw data landing
│   │   ├── silver/            # Cleaned and validated
│   │   └── gold/              # Analytics-ready
│   ├── macros/                # Custom functions
│   └── tests/                 # Data quality tests
├── airflow/                   # ETL orchestration
│   ├── dags/
│   └── plugins/
├── debezium/                  # CDC configurations
│   └── connectors/
├── terraform/                 # Infrastructure as Code
│   ├── cloud_sql/
│   ├── bigquery/
│   ├── iam/
│   └── networking/
├── great_expectations/        # Data validation
│   ├── expectations/
│   └── checkpoints/
├── scripts/                   # Utility scripts
│   ├── migration/
│   ├── seed_data/
│   └── testing/
└── docs/                      # Documentation
    ├── architecture/
    ├── compliance/
    └── runbooks/
```

## 🏃 Getting Started

### Prerequisites
- GCP account with billing enabled
- Terraform >= 1.0
- Node.js >= 18 (for Prisma)
- Python >= 3.9 (for dbt, Airflow)
- Docker (for local development)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Telehealth_platform_architecture_US
   ```

2. **Configure GCP credentials**
   ```bash
   gcloud auth application-default login
   export GOOGLE_PROJECT_ID=your-project-id
   ```

3. **Deploy infrastructure**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

4. **Set up databases**
   ```bash
   cd prisma
   npm install
   npx prisma generate
   npx prisma migrate deploy
   ```

5. **Configure dbt**
   ```bash
   cd dbt
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   dbt deps
   dbt run
   ```

6. **Deploy Airflow DAGs**
   ```bash
   gcloud composer environments storage dags import \
     --environment=telehealth-composer \
     --location=us-central1 \
     --source=airflow/dags
   ```

## 🔐 HIPAA Compliance Features

- ✅ PHI isolated in separate GCP project with stricter IAM
- ✅ Encryption at rest (Google-managed keys) and in transit (TLS 1.3)
- ✅ Column-level encryption for highly sensitive fields
- ✅ De-identification using HIPAA Safe Harbor method
- ✅ Comprehensive audit logging (7-year retention)
- ✅ Role-based access control (RBAC)
- ✅ Break-glass access with monitoring
- ✅ Real-time anomaly detection

## 📈 Implementation Timeline

- **Phase 1**: Foundation (Weeks 1-3)
- **Phase 2**: Data Ingestion (Weeks 3-5)
- **Phase 3**: Transformation & Quality (Weeks 5-7)
- **Phase 4**: Analytics & Reporting (Weeks 7-9)
- **Phase 5**: Migration & Cutover (Weeks 9-11)
- **Phase 6**: Compliance & Production (Weeks 11-12)

See [teleheath_architecture_plan.md](teleheath_architecture_plan.md) for detailed implementation steps.

## 🧪 Testing

```bash
# Run dbt tests
cd dbt && dbt test

# Run Great Expectations validation
cd great_expectations && great_expectations checkpoint run daily_validation

# Run integration tests
pytest tests/integration/

# Load testing
k6 run scripts/load_test.js
```

## 📊 Monitoring & Alerting

- Real-time dashboard: Cloud Monitoring
- Data quality alerts: Great Expectations → PagerDuty
- Pipeline failures: Airflow → Slack
- PHI access anomalies: Cloud Logging → Security Operations

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## 📄 License

This project is proprietary and confidential.

## 📞 Support

For questions or issues, contact the data engineering team.
