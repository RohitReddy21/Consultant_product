import pandas as pd
import numpy as np
from services.risk_scoring import calculate_risk_score

class PricingSimulator:
    def __init__(self, revenue_model, churn_model):
        self.revenue_model = revenue_model
        self.churn_model = churn_model
        
    def simulate_scenario(self, current_data_summary, price_change_percent, discount_change_percent=0.0):
        """
        Simulates the impact of a price change on revenue and churn for a given segment summary.
        current_data_summary: dict with 'segment', 'avg_price', 'avg_units', 'avg_discount'
        """
        segment = current_data_summary['segment']
        current_price = current_data_summary['avg_price']
        current_discount = current_data_summary['avg_discount']
        current_units = current_data_summary['avg_units']
        
        # New Parameters
        new_price = current_price * (1 + price_change_percent / 100.0)
        new_discount = max(0, min(1, current_discount + (discount_change_percent / 100.0)))
        
        # Predict Outcome
        pred_units, pred_revenue = self.revenue_model.predict_demand(segment, new_price, new_discount)
        churn_prob = self.churn_model.predict_churn_prob(segment, new_price, new_discount, pred_units)
        
        # Baseline (Approximate using the model on current params to compare apples-to-apples)
        base_units, base_revenue = self.revenue_model.predict_demand(segment, current_price, current_discount)
        base_churn = self.churn_model.predict_churn_prob(segment, current_price, current_discount, base_units)
        
        # Impact
        revenue_uplift_abs = pred_revenue - base_revenue
        revenue_uplift_pct = (revenue_uplift_abs / base_revenue) * 100 if base_revenue > 0 else 0
        
        churn_change_abs = churn_prob - base_churn
        
        # Risk Score
        risk_score, risk_label = calculate_risk_score(revenue_uplift_pct, churn_prob)
        
        # CLTV Approximation (Monthly Revenue / Churn Rate)
        # Handle edge case where churn is 0 or very low
        safe_churn = max(0.01, churn_prob)
        cltv = (new_price * (1 - new_discount)) / safe_churn
        
        return {
            "segment": segment,
            "old_price": current_price,
            "new_price": new_price,
            "revenue_uplift_pct": revenue_uplift_pct,
            "churn_probability": churn_prob,
            "churn_increase": churn_change_abs,
            "risk_score": risk_score,
            "risk_label": risk_label,
            "predicted_units": pred_units,
            "cltv": cltv
        }

    def find_optimal_price(self, current_data_summary, max_increase=50, max_decrease=50):
        """
        Loops through price percentages to find the 'Golden Ratio' for revenue.
        """
        best_scenario = None
        best_revenue_uplift = -float('inf')
        
        # Check every 5% increment
        for change in range(-max_decrease, max_increase + 5, 5):
            scenario = self.simulate_scenario(current_data_summary, change)
            # We want max revenue, but maybe we penalize high risk? 
            # For this 'Magic Button', let's purely optimize Revenue, but return the risk too.
            if scenario['revenue_uplift_pct'] > best_revenue_uplift:
                best_revenue_uplift = scenario['revenue_uplift_pct']
                best_scenario = scenario
                best_scenario['optimal_price_change'] = change
                
        return best_scenario
