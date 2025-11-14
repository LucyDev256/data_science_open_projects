# Data Visualization Problem: Financial Data Dashboard

## Problem Description

Create compelling and informative visualizations to communicate insights from financial data. Your visualizations should tell a story and make complex data accessible to non-technical stakeholders.

## Dataset Overview

The financial dataset includes:
- Stock prices over time
- Company financial metrics (revenue, profit, expenses)
- Market indicators
- Industry comparison data
- Economic indicators

## Tasks

1. **Time Series Visualizations**
   - Create line charts showing trends over time
   - Add moving averages and trend lines
   - Highlight important events or anomalies

2. **Comparison Visualizations**
   - Compare performance across different companies
   - Show market share distribution
   - Visualize year-over-year growth

3. **Distribution Visualizations**
   - Show distribution of returns
   - Create histograms and density plots
   - Identify outliers and patterns

4. **Relationship Visualizations**
   - Create scatter plots showing correlations
   - Visualize multi-variable relationships
   - Build heatmaps for correlation matrices

5. **Interactive Dashboard**
   - Combine multiple visualizations
   - Add filtering capabilities
   - Enable drill-down features

6. **Best Practices**
   - Use appropriate chart types
   - Apply effective color schemes
   - Include clear labels and titles
   - Make visualizations accessible

## Expected Output

- Set of high-quality visualizations
- Interactive dashboard (optional)
- Documentation explaining each visualization
- Design rationale and insights

## Sample Code Structure

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_financial_data(filepath):
    """Load financial data"""
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    return df

def plot_stock_performance(df, ticker, start_date=None, end_date=None):
    """Plot stock price over time with moving averages"""
    # Filter data
    mask = (df['ticker'] == ticker)
    if start_date:
        mask &= (df['date'] >= start_date)
    if end_date:
        mask &= (df['date'] <= end_date)
    
    data = df[mask].sort_values('date')
    
    # Calculate moving averages
    data['MA_30'] = data['close'].rolling(window=30).mean()
    data['MA_90'] = data['close'].rolling(window=90).mean()
    
    # Create plot
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(data['date'], data['close'], label='Close Price', linewidth=2)
    ax.plot(data['date'], data['MA_30'], label='30-Day MA', linestyle='--', alpha=0.7)
    ax.plot(data['date'], data['MA_90'], label='90-Day MA', linestyle='--', alpha=0.7)
    
    ax.set_title(f'{ticker} Stock Performance', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_company_comparison(df, metrics=['revenue', 'profit']):
    """Compare multiple companies across metrics"""
    fig, axes = plt.subplots(1, len(metrics), figsize=(14, 5))
    
    if len(metrics) == 1:
        axes = [axes]
    
    for i, metric in enumerate(metrics):
        company_data = df.groupby('company')[metric].sum().sort_values(ascending=False)
        
        axes[i].bar(range(len(company_data)), company_data.values)
        axes[i].set_xticks(range(len(company_data)))
        axes[i].set_xticklabels(company_data.index, rotation=45, ha='right')
        axes[i].set_title(f'{metric.title()} by Company', fontsize=14)
        axes[i].set_ylabel(metric.title(), fontsize=12)
    
    plt.tight_layout()
    plt.show()

def plot_returns_distribution(df, ticker):
    """Plot distribution of daily returns"""
    # Calculate daily returns
    stock_data = df[df['ticker'] == ticker].sort_values('date')
    stock_data['returns'] = stock_data['close'].pct_change()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram
    ax1.hist(stock_data['returns'].dropna(), bins=50, edgecolor='black', alpha=0.7)
    ax1.axvline(stock_data['returns'].mean(), color='red', linestyle='--', linewidth=2, label='Mean')
    ax1.set_title(f'{ticker} Daily Returns Distribution', fontsize=14)
    ax1.set_xlabel('Returns', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.legend()
    
    # Box plot
    ax2.boxplot(stock_data['returns'].dropna())
    ax2.set_title(f'{ticker} Returns Box Plot', fontsize=14)
    ax2.set_ylabel('Returns', fontsize=12)
    
    plt.tight_layout()
    plt.show()

def plot_correlation_heatmap(df, columns):
    """Create correlation heatmap"""
    correlation = df[columns].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1)
    plt.title('Correlation Heatmap', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

def create_financial_dashboard(df):
    """Create a comprehensive financial dashboard"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Main stock price chart (top row, spanning all columns)
    ax1 = fig.add_subplot(gs[0, :])
    # Add your main chart here
    
    # Additional charts (middle and bottom rows)
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])
    ax4 = fig.add_subplot(gs[1, 2])
    ax5 = fig.add_subplot(gs[2, 0])
    ax6 = fig.add_subplot(gs[2, 1])
    ax7 = fig.add_subplot(gs[2, 2])
    
    # Populate each subplot with relevant visualizations
    
    plt.suptitle('Financial Data Dashboard', fontsize=20, fontweight='bold')
    plt.show()

if __name__ == "__main__":
    # Load data
    df = load_financial_data("financial_data.csv")
    
    # Generate visualizations
    plot_stock_performance(df, 'AAPL')
    plot_company_comparison(df)
    plot_returns_distribution(df, 'AAPL')
    
    # Correlation analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    plot_correlation_heatmap(df, numeric_cols)
    
    # Create dashboard
    create_financial_dashboard(df)
    
    print("Visualizations created successfully!")
```

## Visualization Best Practices

1. **Choose the Right Chart Type**
   - Line charts for time series
   - Bar charts for comparisons
   - Scatter plots for relationships
   - Heatmaps for correlations

2. **Design Principles**
   - Use consistent color schemes
   - Avoid chart junk
   - Label axes clearly
   - Include titles and legends
   - Consider colorblind-friendly palettes

3. **Tell a Story**
   - Highlight key insights
   - Use annotations
   - Guide the viewer's attention
   - Provide context

4. **Make it Accessible**
   - Use readable fonts
   - Ensure sufficient contrast
   - Add alternative text
   - Test on different devices

## Learning Objectives

- Creating effective data visualizations
- Selecting appropriate chart types
- Applying design principles
- Building interactive dashboards
- Communicating insights visually
- Understanding data storytelling
