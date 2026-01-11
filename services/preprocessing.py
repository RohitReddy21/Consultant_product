import pandas as pd
import numpy as np

def load_data(filepath):
    """Loads data from CSV."""
    df = pd.read_csv(filepath)
    return df

def clean_data(df):
    """Cleans the dataset."""
    # Basic cleaning
    df = df.dropna()
    
    # Type conversion
    if 'churned' in df.columns:
        df['churned'] = df['churned'].astype(int)
        
    return df

def feature_engineering(df):
    """Adds necessary features for modeling."""
    # Effective Price
    df['effective_price'] = df['price'] * (1 - df['discount_percent'])
    
    # Revenue per customer
    df['revenue'] = df['effective_price'] * df['units_sold']
    
    return df

def preprocess_pipeline(filepath):
    """Full preprocessing pipeline."""
    df = load_data(filepath)
    df = clean_data(df)
    df = feature_engineering(df)
    return df
