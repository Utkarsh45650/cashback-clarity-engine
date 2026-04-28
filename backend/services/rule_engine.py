"""
Rule Engine Service
Pure Python logic for calculating cashback eligibility and amount
No AI/ML - deterministic rules only
"""
from typing import Dict, Any, Tuple, Optional


def calculate_cashback(
    amount: float,
    percentage: Optional[float],
    max_cashback: Optional[float],
    min_transaction: Optional[float]
) -> Tuple[bool, float, str]:
    """
    Calculate cashback amount based on rules.
    
    Args:
        amount: Transaction amount
        percentage: Cashback percentage
        max_cashback: Maximum cashback cap
        min_transaction: Minimum transaction required
        
    Returns:
        Tuple of (eligible: bool, cashback_amount: float, reason: str)
    """
    
    # Validation
    if amount <= 0:
        return False, 0.0, "Invalid amount"
    
    if percentage is None or percentage <= 0:
        return False, 0.0, "Invalid percentage"
    
    # Check minimum transaction
    if min_transaction and amount < min_transaction:
        return False, 0.0, f"Amount below minimum: ₹{min_transaction}"
    
    # Calculate raw cashback
    raw_cashback = (amount * percentage) / 100
    
    # Apply max cashback cap
    if max_cashback and raw_cashback > max_cashback:
        final_cashback = max_cashback
        reason = f"Capped at maximum: ₹{max_cashback}"
    else:
        final_cashback = raw_cashback
        reason = f"Eligible: {percentage}% on ₹{amount}"
    
    return True, final_cashback, reason


def check_bank_eligibility(
    user_bank: str,
    offer_banks: list
) -> Tuple[bool, str]:
    """
    Check if user's bank is eligible for this offer.
    
    Args:
        user_bank: User's bank name
        offer_banks: List of eligible banks for offer
        
    Returns:
        Tuple of (eligible: bool, reason: str)
    """
    
    if not offer_banks:
        return True, "Offer applies to all banks"
    
    if user_bank.upper() in [b.upper() for b in offer_banks]:
        return True, f"Eligible with {user_bank}"
    
    return False, f"Not eligible. Offer is for: {', '.join(offer_banks)}"


def check_first_transaction_eligibility(
    is_first_transaction_user: bool,
    offer_requires_first: bool
) -> Tuple[bool, str]:
    """
    Check first transaction condition.
    
    Args:
        is_first_transaction_user: Is this user's first transaction?
        offer_requires_first: Does offer require first transaction?
        
    Returns:
        Tuple of (eligible: bool, reason: str)
    """
    
    if not offer_requires_first:
        return True, "No first transaction requirement"
    
    if is_first_transaction_user:
        return True, "First transaction qualifies"
    
    return False, "Only for first transactions"


def apply_rules(
    transaction_data: Dict[str, Any],
    offer_data: Dict[str, Any],
    user_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply all business rules and calculate final result.
    
    Args:
        transaction_data: {amount: float}
        offer_data: {percentage, max_cashback, min_transaction, banks, is_first_transaction}
        user_profile: {bank, is_first_transaction, ...}
        
    Returns:
        {
            eligible: bool,
            cashback: float,
            reasons: [str],
            violations: [str]
        }
    """
    
    reasons = []
    violations = []
    
    # 1. Check amount
    amount = transaction_data.get("amount")
    if not amount or amount <= 0:
        violations.append("Invalid transaction amount")
        return {
            "eligible": False,
            "cashback": 0.0,
            "reasons": reasons,
            "violations": violations
        }
    
    # 2. Check offer validity
    percentage = offer_data.get("percentage")
    if percentage is None or percentage <= 0:
        violations.append("Invalid offer percentage")
        return {
            "eligible": False,
            "cashback": 0.0,
            "reasons": reasons,
            "violations": violations
        }
    
    # 3. Check bank eligibility
    user_bank = user_profile.get("bank")
    offer_banks = offer_data.get("banks", [])
    bank_eligible, bank_reason = check_bank_eligibility(user_bank, offer_banks)
    
    if not bank_eligible:
        violations.append(bank_reason)
    else:
        reasons.append(bank_reason)
    
    # 4. Check first transaction condition
    if offer_data.get("is_first_transaction"):
        first_txn_eligible, first_txn_reason = check_first_transaction_eligibility(
            user_profile.get("is_first_transaction", False),
            True
        )
        if not first_txn_eligible:
            violations.append(first_txn_reason)
        else:
            reasons.append(first_txn_reason)
    
    # 5. Calculate cashback
    eligible = len(violations) == 0
    
    if eligible:
        calc_eligible, cashback_amount, calc_reason = calculate_cashback(
            amount=amount,
            percentage=percentage,
            max_cashback=offer_data.get("max_cashback"),
            min_transaction=offer_data.get("min_transaction")
        )
        
        if calc_eligible:
            reasons.append(calc_reason)
            return {
                "eligible": True,
                "cashback": round(cashback_amount, 2),
                "reasons": reasons,
                "violations": []
            }
        else:
            violations.append(calc_reason)
    
    return {
        "eligible": False,
        "cashback": 0.0,
        "reasons": reasons,
        "violations": violations
    }


if __name__ == "__main__":
    # Test cases
    test_transaction = {"amount": 700}
    test_offer = {
        "percentage": 10,
        "max_cashback": 100,
        "min_transaction": 500,
        "banks": ["HDFC"],
        "is_first_transaction": True
    }
    test_user = {
        "bank": "HDFC",
        "is_first_transaction": True
    }
    
    result = apply_rules(test_transaction, test_offer, test_user)
    print(f"Test 1 - ₹700 with HDFC (first transaction):")
    print(f"  Eligible: {result['eligible']}")
    print(f"  Cashback: ₹{result['cashback']}")
    print(f"  Reasons: {result['reasons']}")
    print()
    
    # Test 2: Amount > max
    test_transaction2 = {"amount": 2000}
    result2 = apply_rules(test_transaction2, test_offer, test_user)
    print(f"Test 2 - ₹2000 with HDFC (first transaction):")
    print(f"  Eligible: {result2['eligible']}")
    print(f"  Cashback: ₹{result2['cashback']}")
    print(f"  Reasons: {result2['reasons']}")
