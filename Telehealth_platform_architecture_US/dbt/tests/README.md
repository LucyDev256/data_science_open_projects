# dbt Tests Directory

This directory contains custom data quality tests for the Telehealth Platform.

## Test Categories

### 1. **PHI Compliance Tests**
- `no_phi_in_analytics.sql` - Ensures no raw PHI in analytics tables
- Tests that all patient identifiers are properly hashed

### 2. **Business Logic Tests**
- `valid_product_pricing.sql` - Validates product pricing logic
- `dea_product_compliance.sql` - Ensures DEA-required products are properly tracked
- `provider_licensing_compliance.sql` - Validates provider licenses match consultation states

### 3. **Data Integrity Tests**
- `no_duplicate_patients.sql` - Checks for duplicate patient records
- `no_orphaned_prescriptions.sql` - Ensures referential integrity
- `data_freshness_24h.sql` - Validates data is updated within 24 hours

## Running Tests

### Run all tests:
```bash
dbt test
```

### Run specific test:
```bash
dbt test --select no_phi_in_analytics
```

### Run tests for a specific model:
```bash
dbt test --select silver_products
```

### Run tests with specific severity:
```bash
dbt test --select test_type:generic
dbt test --select test_type:singular
```

## Test Results

Tests will fail if they return any rows. An empty result set indicates the test passed.

### Example output:
```
Completed with 0 errors, 0 warnings, 7 tests passed
```

## Adding New Tests

1. Create a new `.sql` file in this directory
2. Write a SELECT query that returns rows for failures
3. Add documentation comment at the top
4. Run `dbt test --select <test_name>` to validate

## Integration with CI/CD

These tests run automatically in the CI/CD pipeline:
- On every PR to validate changes
- After every deployment to production
- Nightly for ongoing monitoring

Failures trigger alerts to:
- Slack #data-quality channel
- PagerDuty for critical failures
- Email to engineering team

## Test Coverage Goals

- **Bronze layer**: Schema validation, freshness
- **Silver layer**: Business logic, referential integrity
- **Gold layer**: PHI de-identification, aggregation accuracy

Target: 95%+ test pass rate
