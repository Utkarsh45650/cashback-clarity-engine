"""
Eligibility Service
Simulates user profile and validates eligibility
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class UserProfile:
    """User eligibility profile"""
    user_id: str
    bank: str
    is_first_transaction: bool = False
    registered_date: Optional[str] = None
    transaction_count: int = 0
    total_spent: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_test_user() -> UserProfile:
    """Create a test user for development/testing"""
    return UserProfile(
        user_id="test_user_001",
        bank="HDFC",
        is_first_transaction=True,
        registered_date=datetime.now().isoformat(),
        transaction_count=0,
        total_spent=0.0
    )


def create_user(
    user_id: str,
    bank: str,
    is_first_transaction: bool = False,
    transaction_count: int = 0,
    total_spent: float = 0.0
) -> UserProfile:
    """
    Create a user profile.
    
    Args:
        user_id: Unique identifier
        bank: User's bank (HDFC, ICICI, SBI, etc.)
        is_first_transaction: Is this first transaction?
        transaction_count: Number of transactions
        total_spent: Total spending amount
        
    Returns:
        UserProfile instance
    """
    return UserProfile(
        user_id=user_id,
        bank=bank,
        is_first_transaction=is_first_transaction,
        registered_date=datetime.now().isoformat(),
        transaction_count=transaction_count,
        total_spent=total_spent
    )


def validate_user_bank(bank: str) -> bool:
    """Validate if bank is supported"""
    supported_banks = ['HDFC', 'ICICI', 'SBI', 'Axis', 'Kotak', 'IDBI', 'PNB', 'BOB', 'RBL', 'IndusInd']
    return bank.upper() in supported_banks


def get_user_eligibility_summary(user: UserProfile) -> Dict[str, Any]:
    """Get eligibility summary for a user"""
    return {
        "user_id": user.user_id,
        "bank": user.bank,
        "is_new_user": user.is_first_transaction,
        "transaction_history": user.transaction_count,
        "total_lifetime_value": user.total_spent,
        "eligible_for_first_txn_offers": user.is_first_transaction,
        "registered_date": user.registered_date
    }


if __name__ == "__main__":
    # Test user creation
    test_user = create_test_user()
    print(f"Test User Created:")
    print(f"  ID: {test_user.user_id}")
    print(f"  Bank: {test_user.bank}")
    print(f"  First Transaction: {test_user.is_first_transaction}")
    print()
    
    # Create another user
    user2 = create_user(
        user_id="user_002",
        bank="ICICI",
        is_first_transaction=False,
        transaction_count=5,
        total_spent=25000
    )
    print(f"User 2 Created:")
    summary = get_user_eligibility_summary(user2)
    for key, value in summary.items():
        print(f"  {key}: {value}")
