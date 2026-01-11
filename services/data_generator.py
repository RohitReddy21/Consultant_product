import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_synthetic_data(num_records=1000):
    """
    Generates synthetic SaaS pricing data for training and simulation.
    Schema: customer_id, segment, price, units_sold, discount_percent, churned, month
    """
    np.random.seed(42)
    
    segments = ['SMB', 'Mid', 'Enterprise']
    segment_weights = [0.5, 0.3, 0.2]
    
    base_prices = {'SMB': 100, 'Mid': 500, 'Enterprise': 2000}
    price_variance = {'SMB': 20, 'Mid': 100, 'Enterprise': 500}
    
    data = []
    
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(num_records):
        customer_id = f"CUST_{i+1:04d}"
        segment = np.random.choice(segments, p=segment_weights)
        
        # Base price fluctuations
        price = base_prices[segment] + np.random.normal(0, price_variance[segment])
        price = max(price, base_prices[segment] * 0.5) # Minimum price constraint
        
        # Discount logic: Higher for Enterprise, higher if price is high
        discount_base = 0.0
        if segment == 'Enterprise':
            discount_base = 0.10
        elif segment == 'Mid':
            discount_base = 0.05
            
        discount_percent = max(0, min(0.3, np.random.normal(discount_base, 0.05)))
        
        # Units sold (Demand) - Negative correlation with price (Price Elasticity)
        # Elasticity varies by segment
        elasticity = {'SMB': -1.5, 'Mid': -1.0, 'Enterprise': -0.5}
        
        base_units = {'SMB': 10, 'Mid': 20, 'Enterprise': 50} # Average seats/units
        
        # Demand function: log(Q) = a + b * log(P) + noise -> Q = A * P^b
        # Simplified: Linear approximation around base
        
        price_factor = (price * (1 - discount_percent)) / base_prices[segment]
        units_sold = int(base_units[segment] * (price_factor ** elasticity[segment]) * np.random.normal(1, 0.1))
        units_sold = max(1, units_sold)
        
        # Churn logic
        # High price increase -> High churn probability
        # High discount -> Low churn probability
        # Segment sensitivity
        churn_prob_base = 0.05
        if segment == 'SMB':
            churn_prob_base += 0.05 # Higher churn for SMB
            
        prob_churn = churn_prob_base + (0.1 * (price_factor - 1)) - (0.1 * discount_percent)
        prob_churn = max(0, min(1, prob_churn))
        
        churned = 1 if np.random.rand() < prob_churn else 0
        
        # Random month within last year
        month_offset = np.random.randint(0, 12)
        month_date = start_date + timedelta(days=30*month_offset)
        month_str = month_date.strftime("%Y-%m")
        
        data.append({
            "customer_id": customer_id,
            "segment": segment,
            "price": round(price, 2),
            "units_sold": units_sold,
            "discount_percent": round(discount_percent, 2),
            "churned": churned,
            "month": month_str
        })
        
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_synthetic_data(2000)
    output_path = "C:/Users/PC/.gemini/antigravity/scratch/pricing-ai-consultant/data/raw/synthetic_saas_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Synthetic data generated at {output_path}")
    print(df.head())
