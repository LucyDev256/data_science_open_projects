"""
Generate sample customer data for the customer segmentation project.
This creates a synthetic dataset with realistic customer attributes.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_customer_data(n_customers=1000, random_state=42):
    """
    Generate synthetic customer data for segmentation analysis.
    
    Args:
        n_customers (int): Number of customers to generate
        random_state (int): Random seed for reproducibility
    
    Returns:
        pd.DataFrame: Customer dataset
    """
    np.random.seed(random_state)
    
    # Generate customer IDs
    customer_ids = [f"CUST{str(i).zfill(6)}" for i in range(1, n_customers + 1)]
    
    # Generate demographics
    ages = np.random.randint(18, 70, n_customers)
    
    # Generate income with some correlation to age
    base_income = 20000 + (ages - 18) * 1000
    income_variation = np.random.normal(0, 15000, n_customers)
    annual_income = np.clip(base_income + income_variation, 15000, 150000).astype(int)
    
    # Generate spending scores (1-100)
    # Create some clusters naturally
    cluster_centers = [20, 40, 60, 80]
    cluster_assignments = np.random.choice(len(cluster_centers), n_customers)
    spending_scores = []
    
    for i in range(n_customers):
        center = cluster_centers[cluster_assignments[i]]
        score = np.random.normal(center, 10)
        spending_scores.append(np.clip(score, 1, 100))
    
    spending_scores = np.array(spending_scores)
    
    # Generate purchase frequency (monthly)
    purchase_frequency = np.random.poisson(5, n_customers)
    purchase_frequency = np.clip(purchase_frequency, 1, 30)
    
    # Generate member since dates
    days_offset = np.random.randint(1, 1825, n_customers)  # Up to 5 years
    member_since = [(datetime.now() - timedelta(days=int(d))).strftime('%Y-%m-%d') 
                    for d in days_offset]
    
    # Generate preferred product categories
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Food & Beverage']
    preferred_category = np.random.choice(categories, n_customers)
    
    # Generate gender
    gender = np.random.choice(['Male', 'Female', 'Other'], n_customers, p=[0.48, 0.48, 0.04])
    
    # Create DataFrame
    df = pd.DataFrame({
        'Customer_ID': customer_ids,
        'Age': ages,
        'Gender': gender,
        'Annual_Income': annual_income,
        'Spending_Score': spending_scores.round(1),
        'Purchase_Frequency': purchase_frequency,
        'Preferred_Category': preferred_category,
        'Member_Since': member_since
    })
    
    return df


def save_customer_data(df, filepath='data/customer_data.csv'):
    """Save customer data to CSV file."""
    df.to_csv(filepath, index=False)
    print(f"Customer data saved to {filepath}")
    print(f"Shape: {df.shape}")
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nBasic statistics:")
    print(df.describe())


def main():
    """Generate and save sample customer data."""
    print("Generating sample customer data...")
    
    # Generate data
    customer_data = generate_customer_data(n_customers=1000, random_state=42)
    
    # Save data
    save_customer_data(customer_data)
    
    print("\nData generation completed successfully!")


if __name__ == "__main__":
    main()
