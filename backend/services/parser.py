"""
Offer Parser Service
Extracts structured information from cashback offer text
Uses regex first, then LangChain/Ollama for complex parsing
"""
import re
import json
from typing import Dict, Any, Optional
from .llm import call_ollama


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Extract first JSON object from model output safely."""
    if not text:
        return None

    text = text.strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        data = json.loads(text[start:end + 1])
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def extract_percentage(text: str) -> Optional[float]:
    """Extract percentage value using regex"""
    pattern = r'(\d+(?:\.\d+)?)\s*%'
    match = re.search(pattern, text)
    if match:
        return float(match.group(1))
    return None


def extract_max_cashback(text: str) -> Optional[float]:
    """Extract max cashback amount (handles ₹ and rupees)"""
    # Pattern for ₹ symbol or "rupees"/"Rs"
    patterns = [
        r'(?:up\s+to|max|maximum)\s+[₹Rr][s]?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'[₹Rr]s?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s+(?:cashback|max)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            return float(amount_str)
    return None


def extract_min_transaction(text: str) -> Optional[float]:
    """Extract minimum transaction amount"""
    patterns = [
        r'(?:min|minimum|on)\s+(?:transaction|spend|order|purchase)?\s*[₹Rr]s?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'[₹Rr]s?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s+(?:transaction|spend|min)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            return float(amount_str)
    return None


def extract_bank_names(text: str) -> list:
    """Extract bank names"""
    banks = ['HDFC', 'ICICI', 'SBI', 'Axis', 'Kotak', 'IDBI', 'PNB', 'BOB', 'RBL', 'IndusInd']
    found_banks = []
    
    for bank in banks:
        if bank.lower() in text.lower():
            found_banks.append(bank)
    
    return list(set(found_banks))  # Remove duplicates


def extract_merchant(text: str) -> Optional[str]:
    """Extract merchant/category information"""
    # Look for specific merchant patterns
    merchants = ['amazon', 'flipkart', 'swiggy', 'zomato', 'uber', 'airbnb', 'ola', 'makemytrip']
    
    for merchant in merchants:
        if merchant.lower() in text.lower():
            return merchant.capitalize()
    
    return None


def has_first_transaction_condition(text: str) -> bool:
    """Check if offer is for first transaction"""
    patterns = [
        r'first\s+(?:transaction|purchase|order|time)',
        r'on\s+first',
        r'inaugural',
        r'new\s+users?',
    ]
    
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def parse_offer(offer_text: str) -> Dict[str, Any]:
    """
    Parse cashback offer text and extract structured information.
    
    Primary method: Regex
    Secondary method: LangChain/Ollama (if regex incomplete)
    
    Returns:
        Dict with keys: percentage, max_cashback, min_transaction, banks, merchant, is_first_transaction
    """
    
    if not offer_text or not offer_text.strip():
        return {
            "percentage": None,
            "max_cashback": None,
            "min_transaction": None,
            "banks": [],
            "merchant": None,
            "is_first_transaction": False,
            "raw_text": offer_text,
            "extraction_method": "none"
        }
    
    # Step 1: Regex extraction (primary)
    result = {
        "percentage": extract_percentage(offer_text),
        "max_cashback": extract_max_cashback(offer_text),
        "min_transaction": extract_min_transaction(offer_text),
        "banks": extract_bank_names(offer_text),
        "merchant": extract_merchant(offer_text),
        "is_first_transaction": has_first_transaction_condition(offer_text),
        "raw_text": offer_text,
        "extraction_method": "regex"
    }
    
    # Step 2: LLM enhancement (secondary) if regex incomplete
    if result["percentage"] is None or not result["banks"]:
        try:
            prompt = (
                "Extract cashback offer details from the text below and return ONLY a valid JSON object "
                "with keys: percentage, max_cashback, min_transaction, banks, merchant, is_first_transaction.\n\n"
                f"Text: {offer_text}"
            )
            response = call_ollama(prompt)
            parsed = _extract_json_object(response or "")

            if parsed:
                # Merge with existing results, preferring LLM results for missing fields
                if parsed.get("percentage") and result["percentage"] is None:
                    result["percentage"] = parsed["percentage"]
                if parsed.get("max_cashback") and result["max_cashback"] is None:
                    result["max_cashback"] = parsed["max_cashback"]
                if parsed.get("min_transaction") and result["min_transaction"] is None:
                    result["min_transaction"] = parsed["min_transaction"]
                if parsed.get("banks") and not result["banks"]:
                    result["banks"] = parsed["banks"]
                if parsed.get("merchant") and result["merchant"] is None:
                    result["merchant"] = parsed["merchant"]
                result["extraction_method"] = "llm"
        except Exception as e:
            print(f"LLM extraction failed: {e}")
            # Keep regex results as fallback

    return result


def format_offer_for_display(parsed: Dict[str, Any]) -> str:
    """Format parsed offer into readable string"""
    parts = []
    
    if parsed.get("percentage"):
        parts.append(f"{parsed['percentage']}% cashback")
    
    if parsed.get("max_cashback"):
        parts.append(f"up to ₹{parsed['max_cashback']}")
    
    if parsed.get("min_transaction"):
        parts.append(f"on ₹{parsed['min_transaction']}+ spend")
    
    if parsed.get("banks"):
        parts.append(f"with {', '.join(parsed['banks'])}")
    
    if parsed.get("is_first_transaction"):
        parts.append("(first transaction)")
    
    return " ".join(parts) if parts else "No details extracted"


if __name__ == "__main__":
    # Test parsing
    test_offers = [
        "10% cashback up to ₹100 on min ₹500 using HDFC card first transaction",
        "₹500 cashback on min ₹5000 spend with SBI credit card",
        "5% back on Amazon purchases for new users",
    ]
    
    for offer in test_offers:
        parsed = parse_offer(offer)
        print(f"\nOffer: {offer}")
        print(f"Parsed: {parsed}")
        print(f"Display: {format_offer_for_display(parsed)}")
