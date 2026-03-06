# Data Cleaning Problem: Customer Dataset

## Problem Description

You are given a customer dataset with various data quality issues. Your task is to clean and preprocess the data for analysis.

## Dataset Issues

The dataset contains the following problems:
- Missing values in critical columns
- Inconsistent data formats (dates, phone numbers)
- Duplicate records
- Outliers in numerical columns
- Inconsistent categorical values (e.g., "Male"/"M"/"male")

## Tasks

1. **Handle Missing Values**
   - Identify columns with missing data
   - Decide on appropriate strategies (imputation, removal, etc.)
   - Document your decisions

2. **Fix Data Format Issues**
   - Standardize date formats
   - Clean and validate phone numbers
   - Normalize text fields

3. **Remove Duplicates**
   - Identify duplicate records
   - Determine which duplicates to keep
   - Remove redundant data

4. **Handle Outliers**
   - Detect outliers using statistical methods
   - Decide whether to remove, cap, or transform outliers
   - Justify your approach

5. **Standardize Categorical Data**
   - Identify inconsistent categorical values
   - Create a standardized mapping
   - Apply transformations

## Expected Output

- A cleaned dataset ready for analysis
- Documentation of all cleaning steps performed
- Summary statistics before and after cleaning
- A report explaining your decisions

## Sample Code Structure

```python
import pandas as pd
import numpy as np

def load_data(filepath):
    """Load the raw dataset"""
    pass

def handle_missing_values(df):
    """Handle missing values in the dataset"""
    pass

def standardize_formats(df):
    """Standardize date and text formats"""
    pass

def remove_duplicates(df):
    """Remove duplicate records"""
    pass

def handle_outliers(df):
    """Detect and handle outliers"""
    pass

def clean_dataset(filepath):
    """Main function to clean the dataset"""
    df = load_data(filepath)
    df = handle_missing_values(df)
    df = standardize_formats(df)
    df = remove_duplicates(df)
    df = handle_outliers(df)
    return df

if __name__ == "__main__":
    cleaned_df = clean_dataset("raw_data.csv")
    cleaned_df.to_csv("cleaned_data.csv", index=False)
    print("Data cleaning completed!")
```

## Learning Objectives

- Understanding data quality issues
- Implementing data cleaning strategies
- Making informed decisions about data preprocessing
- Documenting data transformations
