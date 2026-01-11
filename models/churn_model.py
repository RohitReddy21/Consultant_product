import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
import joblib

class ChurnModel:
    def __init__(self):
        self.model = None
        
    def train(self, df):
        """Trains the model to predict churn probability."""
        X = df[['segment', 'price', 'discount_percent', 'units_sold']] # units_sold might be leakage if future, but maybe current usage. 
        # Requirement says: Price increase -> Churn risk.
        # So we should probably predict churn based on the proposed price compared to some baselines or just absolute price.
        # Ideally we'd have 'price_change', but we train on static snapshots. 
        # We assume the 'price' in the row is the price they saw.
        
        y = df['churned']
        
        categorical_features = ['segment']
        numerical_features = ['price', 'discount_percent', 'units_sold']
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])
            
        # Using Logistic Regression for explainability (coefficients) or CalibratedClassifierCV
        self.model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', LogisticRegression(class_weight='balanced', random_state=42))
        ])
        
        self.model.fit(X, y)
        print("Churn Model Trained.")
        
    def predict_churn_prob(self, segment, price, discount_percent, units_sold):
        """Predicts probability of churn."""
        data = pd.DataFrame({
            'segment': [segment],
            'price': [price],
            'discount_percent': [discount_percent],
            'units_sold': [units_sold] # We might estimate this from the revenue model
        })
        
        prob = self.model.predict_proba(data)[0][1]
        return prob
        
    def save(self, filepath):
        joblib.dump(self.model, filepath)
        
    def load(self, filepath):
        self.model = joblib.load(filepath)
