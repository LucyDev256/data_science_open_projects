# Deployment Runbook

## Overview
Standard operating procedures for deploying changes to the Telehealth Platform.

---

## Pre-Deployment Checklist

- [ ] All tests passing in CI/CD
- [ ] Code review approved (2+ reviewers)
- [ ] Database migrations tested in staging
- [ ] Rollback plan documented
- [ ] Stakeholders notified (if customer-facing)
- [ ] Deployment window scheduled (prefer off-peak hours)

---

## Database Schema Changes

### 1. Prisma Schema Updates

**Development:**
```bash
cd prisma/men_health  # or women_health, phi, shared

# 1. Edit schema.prisma
# 2. Generate migration
npx prisma migrate dev --name add_product_categories

# 3. Review generated SQL
cat prisma/migrations/[TIMESTAMP]_add_product_categories/migration.sql

# 4. Test locally
npx prisma migrate reset  # Drops and recreates DB
npx prisma db seed  # Re-seeds data
```

**Staging Deployment:**
```bash
# Deploy to staging Cloud SQL
export DATABASE_URL="postgresql://user:pass@staging-ip:5432/db"

npx prisma migrate deploy  # Applies pending migrations
npx prisma generate  # Updates Prisma Client
```

**Production Deployment:**
```bash
# ALWAYS create backup first
gcloud sql backups create --instance=telehealth-men-prod

# Apply migration
export DATABASE_URL="postgresql://user:pass@prod-ip:5432/db"
npx prisma migrate deploy

# Verify schema
psql $DATABASE_URL -c "\d+ products"  # Check table structure

# If issues, rollback
npx prisma migrate resolve --rolled-back [MIGRATION_NAME]
```

---

## dbt Model Changes

### 1. Development

```bash
cd dbt

# 1. Create/edit model in models/
# 2. Run locally against dev dataset
dbt run --select my_new_model --target dev

# 3. Test
dbt test --select my_new_model

# 4. Document
# Add to models/schema.yml
```

### 2. Staging Deployment

```bash
# Run in staging BigQuery project
dbt run --select my_new_model+ --target staging

# Validate results
dbt test --target staging

# Run Great Expectations
great_expectations checkpoint run my_checkpoint
```

### 3. Production Deployment

```bash
# Full refresh if schema changed
dbt run --select my_new_model --full-refresh --target prod

# Incremental if data changes only
dbt run --select my_new_model --target prod

# Run all downstream dependencies
dbt run --select my_new_model+ --target prod
```

---

## Airflow DAG Changes

### 1. Test Locally

```bash
cd airflow/dags

# Validate DAG syntax
python dbt_transformations_dag.py

# Test with Airflow locally (Docker)
docker-compose up
# Navigate to localhost:8080
```

### 2. Deploy to Cloud Composer

```bash
# Upload new/updated DAGs
gcloud composer environments storage dags import \
  --environment=telehealth-composer \
  --location=us-central1 \
  --source=airflow/dags/dbt_transformations_dag.py

# Verify DAG appears in Airflow UI
# Check for parsing errors in Logs

# Test run
gcloud composer environments run telehealth-composer \
  --location=us-central1 \
  dags trigger dbt_transformations_dag
```

### 3. Monitor First Run

1. Watch Airflow UI for task status
2. Check task logs for errors
3. Verify BigQuery tables updated
4. Alert on-call if failures

---

## Infrastructure Changes (Terraform)

### 1. Plan Changes

```bash
cd terraform

# Initialize
terraform init

# Plan changes
terraform plan -out=infra.tfplan

# Review plan carefully
# Look for unexpected resource deletions/recreations
```

### 2. Apply to Staging

```bash
terraform workspace select staging
terraform apply infra.tfplan
```

### 3. Apply to Production

```bash
# CRITICAL: Review plan again
terraform workspace select production
terraform plan -out=prod.tfplan

# Require approval from 2+ engineers
# Apply during maintenance window
terraform apply prod.tfplan

# Monitor Cloud Console for errors
```

---

## Application Code Deployment

### 1. Build & Tag

```bash
# Build Docker image
docker build -t gcr.io/your-project/telehealth-api:v1.2.3 .

# Run tests
docker run gcr.io/your-project/telehealth-api:v1.2.3 npm test

# Push to registry
docker push gcr.io/your-project/telehealth-api:v1.2.3
```

### 2. Deploy to Staging

```bash
kubectl set image deployment/telehealth-api \
  telehealth-api=gcr.io/your-project/telehealth-api:v1.2.3 \
  --namespace=staging

# Watch rollout
kubectl rollout status deployment/telehealth-api -n staging

# Run smoke tests
curl https://staging-api.telehealth.com/health
```

### 3. Deploy to Production (Blue-Green)

```bash
# Deploy to "green" environment
kubectl apply -f k8s/deployment-green.yaml

# Verify green pods healthy
kubectl get pods -l version=green

# Switch traffic (update service selector)
kubectl patch service telehealth-api \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Monitor for 15 minutes
# Check error rates, latency, logs

# If issues, rollback to blue
kubectl patch service telehealth-api \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

---

## Rollback Procedures

### Database Migration Rollback

```bash
# Option 1: Manual rollback migration
npx prisma migrate dev --name rollback_product_categories
# Write inverse SQL in migration file

# Option 2: Restore from backup
gcloud sql backups restore [BACKUP_ID] \
  --backup-instance=telehealth-men-prod
```

### dbt Model Rollback

```bash
# Revert to previous version
git revert [COMMIT_HASH]
dbt run --select model_to_revert+ --target prod
```

### Application Rollback

```bash
# Revert to previous image
kubectl set image deployment/telehealth-api \
  telehealth-api=gcr.io/your-project/telehealth-api:v1.2.2

# Or scale down new version
kubectl scale deployment/telehealth-api --replicas=0
kubectl scale deployment/telehealth-api-previous --replicas=3
```

---

## Post-Deployment Validation

### 1. Automated Tests

```bash
# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e
```

### 2. Manual Validation

- [ ] Health check endpoint returns 200
- [ ] Critical user flows work (signup, consultation, order)
- [ ] BigQuery dashboards show recent data
- [ ] No spike in error rates
- [ ] Latency within acceptable range (<100ms p95)

### 3. Monitoring

**Check for 30 minutes post-deployment:**

- Cloud Monitoring dashboards
- Error logs in Cloud Logging
- Sentry error reports
- PagerDuty alerts

### 4. Communication

**Success:**
```
#deployments Slack channel:
✅ Deployed telehealth-api v1.2.3 to production
- Feature: Added product categories
- Monitoring: All green
- Rollback: Available if needed
```

**Issues:**
```
🚨 Deployment issue detected
- Version: v1.2.3
- Issue: Elevated error rate (5%)
- Action: Investigating, may rollback
- Status: https://status.telehealth.com
```

---

## Deployment Schedule

| Environment | Deployment Window | Approval Required |
|-------------|------------------|-------------------|
| Development | Anytime | No |
| Staging | Business hours | Code review |
| Production | Tue-Thu 2-4am ET | 2+ engineers |

**Avoid deployments:**
- Fridays (limited rollback support)
- Before holidays
- During high-traffic periods (Mon mornings)

---

## Emergency Hotfix Procedure

**For critical production bugs only:**

1. Create hotfix branch from main
2. Make minimal fix
3. Fast-track code review (1 reviewer OK)
4. Deploy directly to production
5. Monitor closely for 1 hour
6. Backport to develop branch

```bash
git checkout -b hotfix/critical-bug main
# Make fix
git commit -m "hotfix: Fix critical authentication bug"
git push origin hotfix/critical-bug

# After review + approval
git checkout main
git merge --no-ff hotfix/critical-bug
git tag v1.2.4
git push origin main --tags

# Deploy
# ... follow production deployment steps
```

---

*Last Updated: March 14, 2026*
