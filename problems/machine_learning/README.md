# Machine Learning Problem: Customer Churn Prediction

## Problem Description

Build a machine learning model to predict customer churn for a subscription-based service. The goal is to identify customers who are likely to cancel their subscription so the company can take proactive retention measures.

## Dataset Overview

The dataset includes:
- Customer demographics (age, location, etc.)
- Account information (tenure, contract type)
- Service usage patterns
- Customer service interactions
- Target variable: Churn (Yes/No)

## Tasks

1. **Data Preparation**
   - Load and explore the dataset
   - Handle missing values
   - Encode categorical variables
   - Split data into training and testing sets

2. **Feature Engineering**
   - Create new features from existing data
   - Perform feature scaling/normalization
   - Select relevant features

3. **Model Selection**
   - Train multiple classification models:
     - Logistic Regression
     - Decision Trees
     - Random Forest
     - Gradient Boosting
   - Compare model performance

4. **Model Evaluation**
   - Evaluate using appropriate metrics:
     - Accuracy
     - Precision
     - Recall
     - F1-Score
     - ROC-AUC
   - Analyze confusion matrix
   - Consider class imbalance

5. **Model Optimization**
   - Perform hyperparameter tuning
   - Use cross-validation
   - Address overfitting/underfitting

6. **Feature Importance**
   - Identify most important features
   - Interpret model predictions
   - Generate business insights

## Expected Output

- Trained machine learning models
- Performance comparison report
- Feature importance analysis
- Recommendations for customer retention
- Model deployment strategy

## Sample Code Structure

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_prepare_data(filepath):
    """Load and prepare the dataset"""
    df = pd.read_csv(filepath)
    return df

def preprocess_data(df):
    """Preprocess the data"""
    # Handle missing values
    df = df.fillna(df.median(numeric_only=True))
    
    # Encode categorical variables
    label_encoders = {}
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if col != 'Churn':
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le
    
    return df, label_encoders

def feature_engineering(df):
    """Create new features"""
    # Add your feature engineering logic here
    return df

def train_models(X_train, y_train):
    """Train multiple models"""
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(random_state=42)
    }
    
    trained_models = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        trained_models[name] = model
        print(f"{name} trained successfully")
    
    return trained_models

def evaluate_models(models, X_test, y_test):
    """Evaluate all models"""
    results = {}
    for name, model in models.items():
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        results[name] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        print(f"\n{name} Performance:")
        for metric, value in results[name].items():
            print(f"{metric}: {value:.4f}")
    
    return results

def plot_feature_importance(model, feature_names, top_n=10):
    """Plot feature importance"""
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        indices = np.argsort(importance)[::-1][:top_n]
        
        plt.figure(figsize=(10, 6))
        plt.title('Top Feature Importances')
        plt.bar(range(top_n), importance[indices])
        plt.xticks(range(top_n), [feature_names[i] for i in indices], rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Load data
    df = load_and_prepare_data("customer_data.csv")
    
    # Preprocess
    df, encoders = preprocess_data(df)
    df = feature_engineering(df)
    
    # Split features and target
    X = df.drop('Churn', axis=1)
    y = df['Churn']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    models = train_models(X_train_scaled, y_train)
    
    # Evaluate models
    results = evaluate_models(models, X_test_scaled, y_test)
    
    # Plot feature importance for best model (using original feature names)
    best_model_original = RandomForestClassifier(random_state=42)
    best_model_original.fit(X_train, y_train)
    plot_feature_importance(best_model_original, X.columns)
    
    print("\nModel training and evaluation completed!")
```

## Learning Objectives

- Building end-to-end machine learning pipelines
- Comparing different classification algorithms
- Evaluating model performance with multiple metrics
- Handling imbalanced datasets
- Interpreting model results for business decisions
- Understanding feature importance
