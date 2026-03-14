"""
Verification Script for Seed Data
Validates that all databases are properly seeded
"""

import os
import psycopg2
from psycopg2 import sql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseVerifier:
    """Verifies seed data across all databases"""
    
    def __init__(self):
        self.databases = {
            'men_health': os.getenv('DATABASE_URL_MEN'),
            'women_health': os.getenv('DATABASE_URL_WOMEN'),
            'phi': os.getenv('DATABASE_URL_PHI'),
            'shared': os.getenv('DATABASE_URL_SHARED')
        }
    
    def verify_database(self, db_name: str, expected_tables: dict):
        """Verify row counts in database tables"""
        logger.info(f"Verifying {db_name} database...")
        
        conn_string = self.databases.get(db_name)
        if not conn_string:
            logger.warning(f"Connection string for {db_name} not found")
            return False
        
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            
            for table, min_expected_rows in expected_tables.items():
                cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(
                    sql.Identifier(table)
                ))
                count = cursor.fetchone()[0]
                
                if count >= min_expected_rows:
                    logger.info(f"  ✅ {table}: {count} rows (expected >= {min_expected_rows})")
                else:
                    logger.error(f"  ❌ {table}: {count} rows (expected >= {min_expected_rows})")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error verifying {db_name}: {str(e)}")
            return False
    
    def verify_all(self):
        """Verify all databases"""
        logger.info("Starting database verification...")
        
        # Expected minimum row counts for each database
        expectations = {
            'men_health': {
                'products': 5,
                'inventory': 0  # May be empty initially
            },
            'women_health': {
                'products': 4,
                'inventory': 0
            },
            'phi': {
                'patients': 100,
                'medical_history': 50
            },
            'shared': {
                'providers': 20,
                'provider_licenses': 60
            }
        }
        
        results = {}
        for db_name, expected in expectations.items():
            results[db_name] = self.verify_database(db_name, expected)
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("VERIFICATION SUMMARY")
        logger.info("="*50)
        
        all_passed = all(results.values())
        
        for db_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            logger.info(f"{db_name}: {status}")
        
        if all_passed:
            logger.info("\n🎉 All databases verified successfully!")
        else:
            logger.error("\n⚠️  Some databases failed verification")
        
        return all_passed


def main():
    verifier = DatabaseVerifier()
    success = verifier.verify_all()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
