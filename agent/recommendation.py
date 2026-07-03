"""
Enterprise AI Customer Intelligence Platform — Next Best Action Engine.

A simple rule engine (Version 1) that evaluates customer state and 
suggests a business recommendation. To be replaced by pure AI reasoning in Sprint 7.
"""

import json

def generate_recommendation(customer_profile_json: str) -> str:
    """
    Parses the customer profile JSON output by the tools and applies
    simple business rules to recommend a retention action.
    """
    try:
        profile = json.loads(customer_profile_json)
        
        # If no prediction or features, we can't recommend
        if not profile.get("prediction") or not profile.get("features"):
            return "No action required (Insufficient data)."
            
        prob = profile["prediction"].get("probability", 0.0)
        risk_category = profile["prediction"].get("risk_category", "Low Risk")
        clv = profile["features"].get("total_lifetime_value", 0.0)
        
        if prob >= 0.7:
            if clv > 500:
                return "Priority Outreach & Premium Coupon (High Risk + High CLV)"
            else:
                return "Send Standard 10% Coupon (High Risk + Low CLV)"
        elif prob >= 0.4:
            return "Monitor and send loyalty points (Medium Risk)"
        else:
            return "No campaign required (Low Risk)"
            
    except Exception:
        return "No action required (Could not parse profile)."
