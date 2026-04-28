"""
Explainer Service
Uses Ollama to generate brief, factual explanations
"""
from typing import Dict, Any, Optional
from .llm import call_ollama


def generate_explanation(
    amount: float,
    cashback: float,
    is_eligible: bool,
    offer_details: Dict[str, Any],
    reasons: list,
    violations: list
) -> str:
    """
    Generate a user-friendly explanation using Ollama.
    Prompt is short, structured, and factual.
    
    Args:
        amount: Transaction amount
        cashback: Calculated cashback
        is_eligible: Eligibility status
        offer_details: Parsed offer information
        reasons: List of approval reasons
        violations: List of violations/failures
        
    Returns:
        Explanation text
    """
    
    # Build a structured prompt
    if not is_eligible:
        # Explanation for ineligible cases
        violations_text = " ".join(violations)
        prompt = f"""Generate a brief, clear explanation (2-3 sentences) why this cashback offer is NOT eligible.

Transaction: ₹{amount}
Offer: {offer_details.get('percentage')}% cashback
Reasons ineligible: {violations_text}

Be factual. No speculation."""
    else:
        # Explanation for eligible cases
        reasons_text = " ".join(reasons)
        prompt = f"""Generate a brief, clear explanation (2-3 sentences) how the cashback is calculated.

Transaction: ₹{amount}
Cashback earned: ₹{cashback}
Offer: {offer_details.get('percentage')}% cashback
Max cap: ₹{offer_details.get('max_cashback') or 'None'}
Calculation reasons: {reasons_text}

Be factual. Show the math if relevant."""
    
    # Call Ollama
    response = call_ollama(prompt)
    
    if response:
        # Clean up the response
        return response.strip()
    else:
        # Fallback explanation if Ollama fails
        return generate_fallback_explanation(
            amount, cashback, is_eligible, offer_details, reasons, violations
        )


def generate_fallback_explanation(
    amount: float,
    cashback: float,
    is_eligible: bool,
    offer_details: Dict[str, Any],
    reasons: list,
    violations: list
) -> str:
    """
    Generate explanation without Ollama (fallback).
    Deterministic, no AI.
    """
    
    if not is_eligible:
        if violations:
            return f"Not eligible: {violations[0]}"
        return "Not eligible for this offer."
    
    percentage = offer_details.get("percentage")
    max_cap = offer_details.get("max_cashback")
    
    if max_cap and cashback >= max_cap:
        return f"Earned ₹{cashback} cashback ({percentage}% = ₹{amount * percentage / 100}, capped at ₹{max_cap})."
    else:
        return f"Earned ₹{cashback} cashback ({percentage}% of ₹{amount})."


def explain_offer(
    offer_details: Dict[str, Any],
    user_bank: str
) -> str:
    """
    Generate explanation for an offer itself (not a transaction).
    
    Args:
        offer_details: Parsed offer information
        user_bank: User's bank
        
    Returns:
        Explanation text
    """
    
    parts = []
    
    percentage = offer_details.get("percentage")
    max_cashback = offer_details.get("max_cashback")
    min_txn = offer_details.get("min_transaction")
    banks = offer_details.get("banks", [])
    is_first = offer_details.get("is_first_transaction", False)
    
    if percentage:
        parts.append(f"Get {percentage}% cashback")
    
    if max_cashback:
        parts.append(f"up to ₹{max_cashback}")
    
    if min_txn:
        parts.append(f"on purchases of ₹{min_txn} or more")
    
    if banks:
        bank_match = user_bank.upper() in [b.upper() for b in banks]
        if bank_match:
            parts.append(f"with your {user_bank} card")
        else:
            parts.append(f"with {', '.join(banks)} cards")
    
    if is_first:
        parts.append("for your first transaction")
    
    return " ".join(parts) + "."


if __name__ == "__main__":
    # Test fallback explanations
    offer = {
        "percentage": 10,
        "max_cashback": 100,
        "min_transaction": 500,
        "banks": ["HDFC"]
    }
    
    print("Eligible case:")
    print(generate_fallback_explanation(
        amount=700,
        cashback=70,
        is_eligible=True,
        offer_details=offer,
        reasons=["10% on ₹700"],
        violations=[]
    ))
    print()
    
    print("Ineligible case:")
    print(generate_fallback_explanation(
        amount=300,
        cashback=0,
        is_eligible=False,
        offer_details=offer,
        reasons=[],
        violations=["Amount below minimum: ₹500"]
    ))
    print()
    
    print("Offer explanation:")
    print(explain_offer(offer, "HDFC"))
