import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

class RevenueModel:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        
    def train(self, df):
        """Trains the model to predict units_sold based on price and segment."""
        X = df[['segment', 'price', 'discount_percent']]
        y = df['units_sold']
        
        # Categorical features
        categorical_features = ['segment']
        numerical_features = ['price', 'discount_percent']
        
        # Preprocessing pipeline
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', 'passthrough', numerical_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])
        
        # Model pipeline
        self.model = Pipeline(steps=[
            ('preprocessor', self.preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        
        self.model.fit(X, y)
        print("Revenue Model Trained.")
        
    def predict_demand(self, segment, price, discount_percent):
        """Predicts units sold for a given scenario."""
        data = pd.DataFrame({
            'segment': [segment],
            'price': [price],
            'discount_percent': [discount_percent]
        })
        predicted_units = self.model.predict(data)[0]
        predicted_units = max(0, predicted_units) # Check non-negative
        
        predicted_revenue = predicted_units * price * (1 - discount_percent)
        return predicted_units, predicted_revenue

    def save(self, filepath):
        joblib.dump(self.model, filepath)
        
    def load(self, filepath):
        self.model = joblib.load(filepath)

if __name__ == "__main__":
    # Test
    pass
