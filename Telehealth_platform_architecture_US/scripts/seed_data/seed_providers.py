"""
Seed Provider/Practitioner Data
Generates sample healthcare providers with licensing information
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict
import random


def generate_providers() -> List[Dict]:
    """Generate sample healthcare providers"""
    
    states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
    specialties = [
        'Family Medicine',
        'Internal Medicine',
        'Endocrinology',
        'Urology',
        'Obstetrics & Gynecology',
        'Dermatology'
    ]
    
    providers = []
    
    for i in range(1, 21):  # Generate 20 providers
        provider = {
            "provider_id": f"PROV-{i:04d}",
            "first_name": f"Provider{i}",
            "last_name": f"Lastname{i}",
            "npi_number": f"1{random.randint(100000000, 999999999)}",
            "dea_number": f"A{random.choice(['A', 'B', 'C', 'F', 'G', 'M'])}{random.randint(1000000, 9999999)}",
            "specialty": random.choice(specialties),
            "email": f"provider{i}@telehealth.example.com",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "license_states": random.sample(states, k=random.randint(3, 7)),
            "telemedicine_certified": True,
            "is_active": True,
            "hire_date": (datetime.now() - timedelta(days=random.randint(365, 1825))).isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        providers.append(provider)
    
    return providers


def generate_provider_licenses() -> List[Dict]:
    """Generate provider state licenses"""
    
    licenses = []
    
    # Generate licenses for each provider in their licensed states
    for prov_id in range(1, 21):
        num_states = random.randint(3, 7)
        states = random.sample(
            ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'],
            k=num_states
        )
        
        for state in states:
            license = {
                "license_id": f"LIC-{prov_id:04d}-{state}",
                "provider_id": f"PROV-{prov_id:04d}",
                "state": state,
                "license_number": f"{state}{random.randint(100000, 999999)}",
                "license_type": "MD",
                "issue_date": (datetime.now() - timedelta(days=random.randint(365, 3650))).isoformat(),
                "expiration_date": (datetime.now() + timedelta(days=random.randint(365, 730))).isoformat(),
                "status": "ACTIVE",
                "verified_at": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            licenses.append(license)
    
    return licenses


def save_seed_data():
    """Save provider seed data to JSON files"""
    providers = generate_providers()
    licenses = generate_provider_licenses()
    
    with open('providers_seed.json', 'w') as f:
        json.dump(providers, f, indent=2)
    
    with open('provider_licenses_seed.json', 'w') as f:
        json.dump(licenses, f, indent=2)
    
    print(f"Generated {len(providers)} providers")
    print(f"Generated {len(licenses)} provider state licenses")


if __name__ == "__main__":
    save_seed_data()
