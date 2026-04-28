"""
Automated Test Cases
Tests the entire cashback calculation pipeline
"""
from services.parser import parse_offer
from services.rule_engine import apply_rules
from services.eligibility import create_test_user


def test_case_1():
    """Test Case 1: ₹700 transaction should get ₹70 cashback"""
    print("\n" + "="*60)
    print("TEST CASE 1: ₹700 transaction with ₹10% cashback (max ₹100)")
    print("="*60)
    
    # Offer: 10% cashback up to ₹100 on min ₹500 using HDFC card first transaction
    offer_text = "10% cashback up to ₹100 on min ₹500 using HDFC card first transaction"
    
    # Parse offer
    parsed = parse_offer(offer_text)
    print(f"\n✓ Parsed offer:")
    print(f"  Percentage: {parsed['percentage']}%")
    print(f"  Max cashback: ₹{parsed['max_cashback']}")
    print(f"  Min transaction: ₹{parsed['min_transaction']}")
    print(f"  Banks: {parsed['banks']}")
    print(f"  First transaction: {parsed['is_first_transaction']}")
    
    # Apply rules for ₹700
    transaction_data = {"amount": 700}
    user_profile = {
        "bank": "HDFC",
        "is_first_transaction": True
    }
    
    result = apply_rules(transaction_data, parsed, user_profile)
    
    print(f"\n✓ Calculation for ₹700:")
    print(f"  Eligible: {result['eligible']}")
    print(f"  Cashback: ₹{result['cashback']}")
    print(f"  Reasons: {result['reasons']}")
    
    # Validate
    assert result['eligible'] == True, "Should be eligible"
    assert result['cashback'] == 70.0, f"Expected ₹70, got ₹{result['cashback']}"
    print("\n✅ TEST PASSED")
    
    return True


def test_case_2():
    """Test Case 2: ₹2000 transaction should get ₹100 (capped)"""
    print("\n" + "="*60)
    print("TEST CASE 2: ₹2000 transaction should be capped at ₹100")
    print("="*60)
    
    offer_text = "10% cashback up to ₹100 on min ₹500 using HDFC card first transaction"
    
    # Parse offer
    parsed = parse_offer(offer_text)
    
    # Apply rules for ₹2000
    transaction_data = {"amount": 2000}
    user_profile = {
        "bank": "HDFC",
        "is_first_transaction": True
    }
    
    result = apply_rules(transaction_data, parsed, user_profile)
    
    print(f"\n✓ Calculation for ₹2000:")
    print(f"  Eligible: {result['eligible']}")
    print(f"  Cashback: ₹{result['cashback']}")
    print(f"  Calculation: 10% of ₹2000 = ₹200, capped at ₹100")
    print(f"  Reasons: {result['reasons']}")
    
    # Validate
    assert result['eligible'] == True, "Should be eligible"
    assert result['cashback'] == 100.0, f"Expected ₹100 (capped), got ₹{result['cashback']}"
    print("\n✅ TEST PASSED")
    
    return True


def test_case_3():
    """Test Case 3: ₹300 below minimum should be rejected"""
    print("\n" + "="*60)
    print("TEST CASE 3: ₹300 below minimum (₹500)")
    print("="*60)
    
    offer_text = "10% cashback up to ₹100 on min ₹500 using HDFC card first transaction"
    parsed = parse_offer(offer_text)
    
    # Apply rules for ₹300
    transaction_data = {"amount": 300}
    user_profile = {
        "bank": "HDFC",
        "is_first_transaction": True
    }
    
    result = apply_rules(transaction_data, parsed, user_profile)
    
    print(f"\n✓ Calculation for ₹300:")
    print(f"  Eligible: {result['eligible']}")
    print(f"  Cashback: ₹{result['cashback']}")
    print(f"  Violations: {result['violations']}")
    
    # Validate
    assert result['eligible'] == False, "Should NOT be eligible"
    assert result['cashback'] == 0.0, f"Expected ₹0, got ₹{result['cashback']}"
    print("\n✅ TEST PASSED")
    
    return True


def test_case_4():
    """Test Case 4: Wrong bank should be rejected"""
    print("\n" + "="*60)
    print("TEST CASE 4: ICICI bank but offer for HDFC")
    print("="*60)
    
    offer_text = "10% cashback up to ₹100 on min ₹500 using HDFC card only"
    parsed = parse_offer(offer_text)
    
    # Apply rules with ICICI
    transaction_data = {"amount": 700}
    user_profile = {
        "bank": "ICICI",
        "is_first_transaction": True
    }
    
    result = apply_rules(transaction_data, parsed, user_profile)
    
    print(f"\n✓ Calculation for ICICI:")
    print(f"  Eligible: {result['eligible']}")
    print(f"  Cashback: ₹{result['cashback']}")
    print(f"  Violations: {result['violations']}")
    
    # Validate
    assert result['eligible'] == False, "Should NOT be eligible"
    assert result['cashback'] == 0.0, "Should have no cashback"
    print("\n✅ TEST PASSED")
    
    return True


def test_case_5():
    """Test Case 5: First transaction requirement"""
    print("\n" + "="*60)
    print("TEST CASE 5: First transaction requirement")
    print("="*60)
    
    offer_text = "15% cashback up to ₹500 on min ₹100 for first transaction only HDFC"
    parsed = parse_offer(offer_text)
    
    # First: User not first transaction
    print("\n✓ User NOT on first transaction:")
    transaction_data = {"amount": 500}
    user_profile = {
        "bank": "HDFC",
        "is_first_transaction": False
    }
    
    result = apply_rules(transaction_data, parsed, user_profile)
    print(f"  Eligible: {result['eligible']}")
    print(f"  Violations: {result['violations']}")
    assert result['eligible'] == False, "Should NOT be eligible"
    print("  ✓ Correctly rejected")
    
    # Second: User is first transaction
    print("\n✓ User on first transaction:")
    user_profile["is_first_transaction"] = True
    result = apply_rules(transaction_data, parsed, user_profile)
    print(f"  Eligible: {result['eligible']}")
    print(f"  Cashback: ₹{result['cashback']}")
    assert result['eligible'] == True, "Should be eligible"
    print("  ✓ Correctly approved")
    
    print("\n✅ TEST PASSED")
    return True


def run_all_tests():
    """Run all test cases"""
    print("\n")
    print("╔═════════════════════════════════════════════════════╗")
    print("║  Cashback Clarity Engine - Test Suite               ║")
    print("║  Testing core functionality                         ║")
    print("╚═════════════════════════════════════════════════════╝")
    
    tests = [
        ("Cashback calculation", test_case_1),
        ("Cashback capping", test_case_2),
        ("Minimum transaction check", test_case_3),
        ("Bank eligibility check", test_case_4),
        ("First transaction check", test_case_5),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready to use.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
