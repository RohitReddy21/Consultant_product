def calculate_risk_score(revenue_uplift_pct, churn_probability):
    """
    Calculates a risk score (0-100) and label.
    Logic: 
    - High Revenue Upside + Low Churn = Low Risk, High Confidence
    - Low Revenue Upside + High Churn = High Risk, Low Confidence
    """
    
    # Normalize inputs somewhat
    # sustainable churn is usually < 5-10% depending on business.
    # Revenue uplift 10-20% is good.
    
    # Simple heuristic
    # Risk increases with Churn Probability
    # Risk decreases with Revenue Uplift (if we are making more money, we can tolerate some churn, technically financial risk is lower if net result is positive)
    
    # However, "Risk" usually means "Risk of this going wrong". 
    # Let's define Risk Score as "Danger Level".
    
    score = (churn_probability * 100) * 0.7 - (revenue_uplift_pct * 0.2)
    
    # Clamp to 0-100
    score = max(0, min(100, score))
    
    if score < 20:
        label = "Safe / Low Risk"
    elif score < 50:
        label = "Moderate Risk"
    elif score < 80:
        label = "High Risk"
    else:
        label = "Critical Risk"
        
    return round(score, 1), label
