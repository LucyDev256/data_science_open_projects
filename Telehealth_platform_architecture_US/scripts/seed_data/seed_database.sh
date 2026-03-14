#!/bin/bash
# Master script to seed all databases with sample data

set -e  # Exit on error

echo "🌱 Starting database seeding process..."

# Set environment variables
export DATABASE_URL_MEN=${DATABASE_URL_MEN:-"postgresql://user:pass@localhost:5432/telehealth_men_prod"}
export DATABASE_URL_WOMEN=${DATABASE_URL_WOMEN:-"postgresql://user:pass@localhost:5432/telehealth_women_prod"}
export DATABASE_URL_PHI=${DATABASE_URL_PHI:-"postgresql://user:pass@localhost:5432/telehealth_phi_prod"}
export DATABASE_URL_SHARED=${DATABASE_URL_SHARED:-"postgresql://user:pass@localhost:5432/telehealth_shared_prod"}

# Generate seed data files
echo "📊 Generating seed data..."
python seed_products.py
python seed_providers.py
python seed_patients.py
python seed_orders.py

# Seed shared database (providers, reference data)
echo "🏥 Seeding shared database (providers)..."
cd ../../prisma/shared
npx prisma db seed

# Seed men's health database
echo "💊 Seeding men's health database..."
cd ../men_health
npx prisma db seed

# Seed women's health database
echo "🏥 Seeding women's health database..."
cd ../women_health
npx prisma db seed

# Seed PHI database (synthetic data only)
echo "🔒 Seeding PHI database with synthetic data..."
cd ../phi
npx prisma db seed

# Verify seed data
echo "✅ Verifying seed data..."
cd ../../scripts/testing
python verify_seed_data.py

echo "✅ Database seeding complete!"
echo ""
echo "Summary:"
echo "  - Men's health products: seeded"
echo "  - Women's health products: seeded"
echo "  - Providers: 20 providers with multi-state licenses"
echo "  - Patients: synthetic PHI data"
echo "  - Orders: sample order history"
echo ""
echo "Next steps:"
echo "  1. Run: dbt run --select bronze"
echo "  2. Run: dbt test"
echo "  3. Verify BigQuery tables populated"
