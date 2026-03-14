"""
Seed Order Data
Generates sample orders and prescriptions
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict


def generate_orders(patient_uuids: List[str], product_skus: List[str], count: int = 200) -> List[Dict]:
    """Generate sample orders"""
    
    orders = []
    
    for i in range(count):
        order_date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        order = {
            "order_id": f"ORD-{i+1:06d}",
            "patient_uuid": random.choice(patient_uuids),
            "order_date": order_date.isoformat(),
            "status": random.choice(['PENDING', 'APPROVED', 'FULFILLED', 'SHIPPED', 'DELIVERED']),
            "order_type": random.choice(['SUBSCRIPTION', 'ONE_TIME']),
            "total_amount": round(random.uniform(20.0, 300.0), 2),
            "payment_status": random.choice(['PAID', 'PENDING', 'FAILED']),
            "fulfillment_partner": random.choice(['PharmacyA', 'PharmacyB', 'PharmacyC']),
            "created_at": order_date.isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        orders.append(order)
    
    return orders


def generate_prescriptions(patient_uuids: List[str], provider_ids: List[str], count: int = 150) -> List[Dict]:
    """Generate sample prescriptions"""
    
    medications = [
        'Sildenafil 50mg',
        'Tadalafil 20mg',
        'Finasteride 1mg',
        'Semaglutide 2.4mg',
        'Estradiol 1mg',
        'Progesterone 200mg',
        'Tirzepatide 5mg'
    ]
    
    prescriptions = []
    
    for i in range(count):
        prescribed_date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        prescription = {
            "prescription_id": f"RX-{i+1:06d}",
            "patient_uuid": random.choice(patient_uuids),
            "provider_id": random.choice(provider_ids),
            "medication": random.choice(medications),
            "dosage_instructions": "Take as directed",
            "quantity": random.choice([30, 60, 90]),
            "refills_allowed": random.randint(0, 5),
            "prescribed_date": prescribed_date.isoformat(),
            "expiration_date": (prescribed_date + timedelta(days=365)).isoformat(),
            "status": random.choice(['ACTIVE', 'FILLED', 'EXPIRED', 'CANCELLED']),
            "is_controlled_substance": random.choice([True, False]),
            "created_at": prescribed_date.isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        prescriptions.append(prescription)
    
    return prescriptions


def save_seed_data():
    """Save order and prescription seed data"""
    
    # Sample UUIDs and IDs (would come from patients_seed.json and providers_seed.json)
    patient_uuids = [str(uuid.uuid4()) for _ in range(100)]
    provider_ids = [f"PROV-{i:04d}" for i in range(1, 21)]
    product_skus = [
        'MEN-ED-001', 'MEN-ED-002', 'MEN-HAIR-001', 'MEN-PEP-001',
        'WOM-HRT-001', 'WOM-HRT-002', 'WOM-GLP-001'
    ]
    
    orders = generate_orders(patient_uuids, product_skus, 200)
    prescriptions = generate_prescriptions(patient_uuids, provider_ids, 150)
    
    with open('orders_seed.json', 'w') as f:
        json.dump(orders, f, indent=2)
    
    with open('prescriptions_seed.json', 'w') as f:
        json.dump(prescriptions, f, indent=2)
    
    print(f"Generated {len(orders)} orders")
    print(f"Generated {len(prescriptions)} prescriptions")


if __name__ == "__main__":
    save_seed_data()
