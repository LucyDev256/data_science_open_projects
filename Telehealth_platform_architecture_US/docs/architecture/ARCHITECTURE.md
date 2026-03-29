# Data Architecture Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     OPERATIONAL LAYER (Cloud SQL)                    │
├──────────────┬──────────────┬──────────────┬───────────────────────┤
│   Men's DB   │  Women's DB  │  Shared DB   │    PHI DB (Separate)  │
│   (PostgreSQL│  (PostgreSQL)│  (PostgreSQL)│    (PostgreSQL)       │
└──────┬───────┴──────┬───────┴──────┬───────┴───────────┬───────────┘
       │              │              │                   │
       │              │              │                   │ No CDC!
       └──────────────┴──────────────┘                   │
                      │                                   │
                      ▼                                   │
         ┌────────────────────────┐                      │
         │   Debezium CDC (WAL)   │                      │
         └────────────┬───────────┘                      │
                      │                                   │
                      ▼                                   │
              ┌──────────────┐                           │
              │ Kafka/Pub/Sub│                           │
              └──────┬───────┘                           │
                      │                                   │
                      ▼                                   │
┌─────────────────────────────────────────────────────────┼───────────┐
│              ANALYTICS LAYER (BigQuery)                 │           │
├─────────────────────────────────────────────────────────┘           │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │ BRONZE LAYER (Raw Data)                                  │      │
│  │ - Minimal transformations                                │      │
│  │ - Complete history preserved                             │      │
│  │ - Real-time via CDC                                      │      │
│  └────────────────────┬─────────────────────────────────────┘      │
│                       │                                             │
│                       │ dbt transformations                         │
│                       ▼                                             │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │ SILVER LAYER (Cleaned & Validated)                       │      │
│  │ - Data quality checks (Great Expectations)               │      │
│  │ - Schema normalization                                   │      │
│  │ - De-identification applied                              │      │
│  │ - Business rules applied                                 │      │
│  └────────────────────┬─────────────────────────────────────┘      │
│                       │                                             │
│                       │ dbt transformations                         │
│                       ▼                                             │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │ GOLD LAYER (Analytics-Ready)                             │      │
│  │ - Dimensional models (star schema)                       │      │
│  │ - Pre-aggregated metrics                                 │      │
│  │ - Dashboard-optimized                                    │      │
│  │ - ML features                                            │      │
│  └──────────────────────┬───────────────────────────────────┘      │
│                         │                                           │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  BI Tools & Analytics │
              │  - Looker Studio      │
              │  - Data Science       │
              │  - ML Models          │
              └───────────────────────┘
```

## Database Design

### Operational Databases

#### Men's Health Database
**Purpose**: Transaction processing for men's health brand  
**Tables**: 15+ tables including products, inventory, orders, prescriptions  
**Size**: ~500GB estimated  
**Connections**: Debezium CDC → BigQuery

#### Women's Health Database
**Purpose**: Transaction processing for women's health brand  
**Tables**: Similar structure to men's DB with category adaptations  
**Size**: ~500GB estimated  
**Connections**: Debezium CDC → BigQuery

#### PHI Database (Separate Project)
**Purpose**: Secure storage of Protected Health Information  
**Tables**: Patient demographics, medical history, clinical assessments, lab results  
**Size**: ~200GB estimated  
**Connections**: Direct API access only (no CDC)

#### Shared Database
**Purpose**: Reference data shared across brands  
**Tables**: Providers, clinical protocols, drug formulary, state regulations  
**Size**: ~50GB estimated  
**Connections**: Batch sync to BigQuery

### Data Warehouse (BigQuery)

#### Bronze Layer
- **Purpose**: Raw data landing zone
- **Retention**: Unlimited (historical record)
- **Partitioning**: By ingestion timestamp
- **Clustering**: By primary keys
- **Update Pattern**: Append-only via CDC

#### Silver Layer
- **Purpose**: Cleaned, validated, business-ready data
- **Retention**: 2 years hot, archive after
- **Partitioning**: By business date
- **Clustering**: By commonly queried dimensions
- **Update Pattern**: Daily dbt runs

#### Gold Layer
- **Purpose**: Analytics-ready dimensional models
- **Retention**: 1 year hot, 5 years archive
- **Partitioning**: By date
- **Materialization**: Tables for performance
- **Update Pattern**: Every 4 hours

## Data Flow Patterns

### Real-Time CDC Pipeline
```
PostgreSQL WAL
  → Debezium (Kafka Connect)
  → Kafka Topics (Confluent Cloud)
  → Pub/Sub (GCP)
  → BigQuery Streaming API
  → Bronze Tables
Latency: < 30 seconds end-to-end
```

### Batch Integration Pipeline
```
External APIs (Lab, Pharmacy, Shipping, Payments)
  → API Polling (Airflow)
  → Cloud Storage (JSON/CSV)
  → BigQuery Load Jobs
  → Bronze Tables
Schedule: Hourly or daily depending on source
```

### Transformation Pipeline
```
Bronze → dbt → Silver → dbt → Gold
           ↓              ↓
    Great Expectations  Great Expectations
           ↓              ↓
       Alerts         Alerts
Schedule: Every 4 hours
```

## Key Design Decisions

### 1. Why Separate Databases per Brand?
- **Isolation**: Independent scaling and maintenance
- **Compliance**: Separate audit trails
- **Performance**: Smaller indexes, faster queries
- **Business**: Different product catalogs and workflows

### 2. Why BigQuery over Snowflake?
- **Native GCP Integration**: Simpler architecture
- **Cost**: Pay-per-query model better for 10K-100K users
- **Streaming**: Native support for real-time CDC
- **ML**: Built-in ML capabilities

### 3. Why Debezium over Airbyte/Fivetran?
- **Open Source**: No per-row pricing
- **PostgreSQL WAL**: Minimal impact on source database
- **Flexibility**: Full control over transformations
- **Maturity**: Battle-tested in production

### 4. Why dbt over Custom ETL?
- **Testing**: Built-in data quality tests
- **Documentation**: Auto-generated lineage
- **Version Control**: SQL in Git
- **Community**: Large ecosystem of packages

## Performance Characteristics

### Query Performance (p95)
- **Operational Databases**: < 100ms for single-row reads
- **Bronze Layer**: < 2 seconds for recent data queries
- **Silver Layer**: < 5 seconds for aggregations
- **Gold Layer**: < 3 seconds for dashboard queries

### Data Freshness
- **Real-Time CDC**: < 30 seconds from commit to BigQuery
- **Batch Integrations**: 1-24 hours depending on source
- **dbt Transformations**: 4-hour refresh cycle
- **Dashboards**: 4-hour refresh (matches dbt schedule)

### Scalability
- **Cloud SQL**: Supports up to 96 vCPU, 624GB RAM per instance
- **BigQuery**: Petabyte-scale, automatic scaling
- **Kafka**: Horizontally scalable (add brokers)
- **Airflow**: Vertically scalable (Composer node size)

## Data Quality Framework

### Validation Layers
1. **Application Layer**: Input validation, type checking
2. **Database Layer**: Constraints, foreign keys, triggers
3. **Bronze Layer**: Schema validation on ingestion
4. **Silver Layer**: Great Expectations full suite
5. **Gold Layer**: Business logic validation

### Monitoring & Alerting
- **Data Quality**: Great Expectations → Slack
- **Pipeline Failures**: Airflow → PagerDuty
- **Query Performance**: Cloud Monitoring → Email
- **Cost Overruns**: Billing alerts → Slack

## Disaster Recovery

### RPO/RTO Targets
- **Operational Databases**: RPO < 5 minutes, RTO < 1 minute
- **BigQuery**: RPO ~0 (immutable), RTO < 5 minutes
- **Kafka**: RPO < 1 minute, RTO < 5 minutes

### Backup Strategy
- **Cloud SQL**: Automated daily backups, 30 days retention, point-in-time recovery
- **BigQuery**: 7-day time travel, table snapshots for critical data
- **Kafka**: Multi-zone replication, 7-day retention

### Failover Procedures
See [docs/runbooks/DISASTER_RECOVERY.md](runbooks/DISASTER_RECOVERY.md)

## Cost Estimates

### Monthly Infrastructure Costs (Production)
- **Cloud SQL**: $2,000/month (4 instances)
- **BigQuery**: $3,000/month (storage + queries)
- **Kafka/Confluent**: $1,500/month
- **Composer/Airflow**: $800/month
- **Networking**: $500/month
- **Monitoring**: $200/month
- **Total**: ~$8,000/month

### Cost Optimization
- BigQuery: Partition pruning, clustering, materialized views
- Cloud SQL: Right-sizing based on metrics
- Kafka: Topic retention tuning
- Storage: Lifecycle policies (hot → cold → archive)

## Maintenance Windows

**Production**:
- Database maintenance: Sundays 2-6 AM ET
- dbt deployments: Business hours (blue-green)
- Schema changes: Requires approval + rollback plan

**Development**:
- No maintenance windows
- Deployments anytime

## Contact & Support

**On-Call Rotation**: PagerDuty integration  
**Slack Channels**: #data-engineering, #data-incidents  
**Team Email**: data-team@telehealth.com
