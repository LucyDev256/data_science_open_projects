# Exploratory Data Analysis Problem: Sales Dataset

## Problem Description

Perform comprehensive exploratory data analysis (EDA) on a sales dataset to uncover patterns, trends, and insights that can inform business decisions.

## Dataset Overview

The sales dataset contains:
- Transaction records
- Product information
- Customer demographics
- Time-series data (dates, seasons)
- Geographic information

## Tasks

1. **Data Overview**
   - Load and inspect the dataset
   - Check data types and dimensions
   - Identify potential issues

2. **Univariate Analysis**
   - Analyze distribution of numerical variables
   - Examine frequency of categorical variables
   - Calculate summary statistics

3. **Bivariate Analysis**
   - Explore relationships between variables
   - Calculate correlations
   - Identify trends and patterns

4. **Time Series Analysis**
   - Analyze sales trends over time
   - Identify seasonal patterns
   - Detect anomalies

5. **Geographic Analysis**
   - Analyze sales by region
   - Identify top-performing locations
   - Map geographic patterns

6. **Customer Segmentation**
   - Analyze customer demographics
   - Identify customer segments
   - Profile different customer groups

## Expected Output

- Comprehensive EDA report with visualizations
- Key findings and insights
- Statistical summaries
- Recommendations based on analysis

## Sample Code Structure

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_inspect(filepath):
    """Load data and perform initial inspection"""
    df = pd.read_csv(filepath)
    print(df.info())
    print(df.describe())
    return df

def univariate_analysis(df):
    """Analyze individual variables"""
    # Numerical distributions
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    for col in numerical_cols:
        plt.figure(figsize=(10, 4))
        plt.subplot(1, 2, 1)
        df[col].hist(bins=30)
        plt.title(f'Distribution of {col}')
        plt.subplot(1, 2, 2)
        df.boxplot(column=col)
        plt.show()

def bivariate_analysis(df):
    """Analyze relationships between variables"""
    # Correlation matrix
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    correlation_matrix = df[numerical_cols].corr()
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Matrix')
    plt.show()

def time_series_analysis(df, date_column='date', value_column='sales'):
    """Analyze trends over time"""
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.sort_values(date_column)
    
    # Plot time series
    plt.figure(figsize=(15, 5))
    plt.plot(df[date_column], df[value_column])
    plt.title('Sales Over Time')
    plt.xlabel('Date')
    plt.ylabel('Sales')
    plt.show()

def geographic_analysis(df, location_column='region', value_column='sales'):
    """Analyze geographic patterns"""
    regional_sales = df.groupby(location_column)[value_column].sum().sort_values(ascending=False)
    
    plt.figure(figsize=(12, 6))
    regional_sales.plot(kind='bar')
    plt.title('Sales by Region')
    plt.xlabel('Region')
    plt.ylabel('Total Sales')
    plt.show()

def generate_insights(df):
    """Generate key insights from the analysis"""
    insights = []
    # Add your insight generation logic here
    return insights

if __name__ == "__main__":
    df = load_and_inspect("sales_data.csv")
    univariate_analysis(df)
    bivariate_analysis(df)
    time_series_analysis(df)
    geographic_analysis(df)
    insights = generate_insights(df)
    print("EDA completed!")
```

## Learning Objectives

- Conducting systematic exploratory data analysis
- Creating effective visualizations
- Identifying patterns and trends in data
- Generating actionable insights
- Communicating findings effectively
