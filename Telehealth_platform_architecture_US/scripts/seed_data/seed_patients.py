"""
Seed Patient Data (Synthetic PHI)
Generates HIPAA-compliant synthetic patient data for testing
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict


def generate_synthetic_patients(count: int = 100) -> List[Dict]:
    """Generate synthetic patient records"""
    
    first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa',
                   'James', 'Maria', 'William', 'Jennifer', 'Richard', 'Linda', 'Joseph']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
                  'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez']
    
    states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
    
    patients = []
    
    for i in range(count):
        # Generate patient UUID for anonymization
        patient_uuid = str(uuid.uuid4())
        
        # Random birthdate (18-75 years old)
        age_days = random.randint(18*365, 75*365)
        dob = datetime.now() - timedelta(days=age_days)
        
        patient = {
            "patient_uuid": patient_uuid,
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "date_of_birth": dob.date().isoformat(),
            "gender": random.choice(['M', 'F', 'Other']),
            "email": f"patient{i+1}@example.com",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "address_line1": f"{random.randint(100, 9999)} Main St",
            "city": random.choice(['Los Angeles', 'New York', 'Houston', 'Chicago', 'Phoenix']),
            "state": random.choice(states),
            "zip_code": f"{random.randint(10000, 99999)}",
            "ssn": f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        patients.append(patient)
    
    return patients


def generate_medical_history(patient_uuids: List[str]) -> List[Dict]:
    """Generate synthetic medical history records"""
    
    conditions = [
        'Hypertension',
        'Type 2 Diabetes',
        'Obesity',
        'Depression',
        'Anxiety',
        'GERD',
        'Hypothyroidism',
        'Erectile Dysfunction',
        'Menopause',
        'PCOS'
    ]
    
    medical_records = []
    
    for patient_uuid in patient_uuids:
        # Each patient has 0-3 conditions
        num_conditions = random.randint(0, 3)
        patient_conditions = random.sample(conditions, k=num_conditions)
        
        for condition in patient_conditions:
            record = {
                "patient_uuid": patient_uuid,
                "condition": condition,
                "diagnosed_date": (datetime.now() - timedelta(days=random.randint(30, 3650))).isoformat(),
                "status": random.choice(['ACTIVE', 'MANAGED', 'RESOLVED']),
                "notes": f"Patient reports {condition.lower()}",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            medical_records.append(record)
    
    return medical_records


def save_seed_data():
    """Save patient seed data to JSON files"""
    patients = generate_synthetic_patients(100)
    patient_uuids = [p['patient_uuid'] for p in patients]
    medical_history = generate_medical_history(patient_uuids)
    
    with open('patients_seed.json', 'w') as f:
        json.dump(patients, f, indent=2)
    
    with open('medical_history_seed.json', 'w') as f:
        json.dump(medical_history, f, indent=2)
    
    print(f"Generated {len(patients)} synthetic patients")
    print(f"Generated {len(medical_history)} medical history records")
    print("⚠️  WARNING: This is SYNTHETIC DATA for testing only")


if __name__ == "__main__":
    save_seed_data()
