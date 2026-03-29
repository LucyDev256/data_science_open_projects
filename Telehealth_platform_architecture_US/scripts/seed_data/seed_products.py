"""
Seed Products Data
Generates sample pharmaceutical products for men's and women's health
"""

import json
from datetime import datetime
from typing import List, Dict


def generate_mens_products() -> List[Dict]:
    """Generate sample men's health products"""
    products = [
        {
            "sku": "MEN-ED-001",
            "name": "Sildenafil 50mg",
            "category": "ED_MEDICATION",
            "description": "FDA-approved treatment for erectile dysfunction",
            "active_ingredients": "Sildenafil Citrate",
            "dosage_form": "Tablet",
            "strength": "50mg",
            "requires_dea": False,
            "fda_approved": True,
            "ndc_code": "12345-678-90",
            "base_price": 15.00,
            "subscription_price": 12.00,
            "insurance_coverable": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "MEN-ED-002",
            "name": "Tadalafil 20mg",
            "category": "ED_MEDICATION",
            "description": "Long-acting ED medication (36 hours)",
            "active_ingredients": "Tadalafil",
            "dosage_form": "Tablet",
            "strength": "20mg",
            "requires_dea": False,
            "fda_approved": True,
            "ndc_code": "12345-679-90",
            "base_price": 18.00,
            "subscription_price": 15.00,
            "insurance_coverable": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "MEN-HAIR-001",
            "name": "Finasteride 1mg",
            "category": "HAIR_GROWTH",
            "description": "DHT blocker for male pattern baldness",
            "active_ingredients": "Finasteride",
            "dosage_form": "Tablet",
            "strength": "1mg",
            "requires_dea": False,
            "fda_approved": True,
            "ndc_code": "12345-680-90",
            "base_price": 10.00,
            "subscription_price": 8.00,
            "insurance_coverable": False,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "MEN-PEP-001",
            "name": "Semaglutide 2.4mg",
            "category": "GLP1_PEPTIDE",
            "description": "GLP-1 receptor agonist for weight management",
            "active_ingredients": "Semaglutide",
            "dosage_form": "Injection",
            "strength": "2.4mg/0.75mL",
            "requires_dea": False,
            "fda_approved": True,
            "ndc_code": "12345-681-90",
            "base_price": 250.00,
            "subscription_price": 225.00,
            "insurance_coverable": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "MEN-TEST-001",
            "name": "Testosterone Cypionate 200mg/mL",
            "category": "HORMONE_THERAPY",
            "description": "Testosterone replacement therapy",
            "active_ingredients": "Testosterone Cypionate",
            "dosage_form": "Injection",
            "strength": "200mg/mL",
            "requires_dea": True,  # Schedule III controlled substance
            "fda_approved": True,
            "ndc_code": "12345-682-90",
            "base_price": 75.00,
            "subscription_price": 65.00,
            "insurance_coverable": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    return products


def generate_womens_products() -> List[Dict]:
    """Generate sample women's health products"""
    products = [
        {
            "sku": "WOM-HRT-001",
            "name": "Estradiol 1mg",
            "category": "HORMONE_REPLACEMENT",
            "description": "Bioidentical estrogen for menopause symptoms",
            "active_ingredients": "Estradiol",
            "dosage_form": "Tablet",
            "strength": "1mg",
            "requires_dea": False,
            "fda_approved": True,
            "ndc_code": "23456-678-90",
            "base_price": 20.00,
            "subscription_price": 16.00,
            "insurance_coverable": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "WOM-HRT-002",
            "name": "Progesterone 200mg",
            "category": "HORMONE_REPLACEMENT",
            "description": "Bioidentical progesterone for HRT",
            "active_ingredients": "Micronized Progesterone",
            "dosage_form": "Capsule",
            "strength": "200mg",
            "requires_dea": False,
            "fda_approved": True,
            "ndc_code": "23456-679-90",
            "base_price": 25.00,
            "subscription_price": 20.00,
            "insurance_coverable": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "WOM-GLP-001",
            "name": "Tirzepatide 5mg",
            "category": "GLP1_PEPTIDE",
            "description": "Dual GIP/GLP-1 receptor agonist for weight loss",
            "active_ingredients": "Tirzepatide",
            "dosage_form": "Injection",
            "strength": "5mg/0.5mL",
            "requires_dea": False,
            "fda_approved": True,
            "ndc_code": "23456-680-90",
            "base_price": 275.00,
            "subscription_price": 250.00,
            "insurance_coverable": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "WOM-HAIR-001",
            "name": "Minoxidil 5% Solution",
            "category": "HAIR_GROWTH",
            "description": "Topical treatment for female pattern hair loss",
            "active_ingredients": "Minoxidil",
            "dosage_form": "Topical Solution",
            "strength": "5%",
            "requires_dea": False,
            "fda_approved": True,
            "ndc_code": "23456-681-90",
            "base_price": 30.00,
            "subscription_price": 25.00,
            "insurance_coverable": False,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    return products


def save_seed_data():
    """Save seed data to JSON files"""
    mens_products = generate_mens_products()
    womens_products = generate_womens_products()
    
    with open('mens_products_seed.json', 'w') as f:
        json.dump(mens_products, f, indent=2)
    
    with open('womens_products_seed.json', 'w') as f:
        json.dump(womens_products, f, indent=2)
    
    print(f"Generated {len(mens_products)} men's health products")
    print(f"Generated {len(womens_products)} women's health products")


if __name__ == "__main__":
    save_seed_data()
