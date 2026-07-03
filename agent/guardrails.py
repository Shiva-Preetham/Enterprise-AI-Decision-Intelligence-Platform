"""
Enterprise AI Customer Intelligence Platform — Guardrails.

Pre-execution validation to reject unsafe, out-of-domain, or injection attempts.
"""

import re
from typing import Tuple

def check_guardrails(user_input: str) -> Tuple[bool, str]:
    """
    Validates user input before allowing the agent to process it.
    Returns (is_safe, rejection_reason).
    """
    input_lower = user_input.lower()
    
    # 1. SQL Injection Prevention (Hard stop on raw SQL queries)
    sql_keywords = ["select * from", "drop table", "insert into", "delete from", "update ", "truncate table"]
    if any(kw in input_lower for kw in sql_keywords):
        return False, "Direct SQL queries are strictly prohibited by enterprise security policies."
        
    # 2. System Prompt Extraction / Jailbreaks
    jailbreak_keywords = ["ignore previous instructions", "system prompt", "you are a developer", "forget all"]
    if any(kw in input_lower for kw in jailbreak_keywords):
        return False, "I cannot process requests that attempt to modify or extract my core instructions."
        
    # 3. Code Execution
    code_keywords = ["import os", "eval(", "exec(", "subprocess"]
    if any(kw in input_lower for kw in code_keywords):
        return False, "Requests to execute arbitrary code are prohibited."
        
    # 4. Domain Enforcement (Soft check)
    # The agent should only answer business/customer/ml/platform questions.
    domain_keywords = [
        "customer", "churn", "clv", "predict", "model", "shap", "revenue", "order", 
        "coupon", "campaign", "dashboard", "analytics", "health", "redis", "celery", "task"
    ]
    # We only enforce this softly: if it's very short and lacks domain words, maybe it's just "hello".
    # But if it's long and entirely unrelated (e.g. "write a poem about a cat"), reject it.
    if len(input_lower.split()) > 5 and not any(kw in input_lower for kw in domain_keywords):
        return False, "I am a Customer Intelligence Copilot. Please ask questions related to customers, churn, analytics, or platform health."
        
    return True, ""
