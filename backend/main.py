"""
FastAPI Backend
Main application with API routes and error handling
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import traceback

# Import services
from services.llm import is_ollama_available, call_ollama
from services.parser import parse_offer
from services.rule_engine import apply_rules
from services.eligibility import create_test_user
from services.explainer import generate_explanation, explain_offer
from services.rag import initialize_rag_with_offers, search_similar_offers

# Initialize FastAPI app
app = FastAPI(
    title="Cashback Clarity Engine",
    description="Offline, Ollama-powered cashback calculation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for validation
class OfferRequest(BaseModel):
    """Cashback offer details"""
    offer_text: str = Field(..., min_length=1, description="Raw offer text")
    amount: float = Field(..., gt=0, description="Transaction amount")
    bank: Optional[str] = Field("HDFC", description="User's bank")
    is_first_transaction: bool = Field(False, description="Is first transaction?")


class OfferResponse(BaseModel):
    """Response with calculation results"""
    eligible: bool
    cashback: float
    offer_details: dict
    explanation: str
    reasons: List[str]
    violations: List[str]


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    ollama_available: bool
    timestamp: str


class OfferSearchRequest(BaseModel):
    """Search request for similar offers"""
    query: str = Field(..., min_length=1)
    top_k: int = Field(3, ge=1, le=10)


class OfferSearchResponse(BaseModel):
    """Search results"""
    query: str
    results: List[dict]
    count: int


# Sample offers for RAG
SAMPLE_OFFERS = [
    {
        "id": 1,
        "text": "10% cashback up to ₹100 on min ₹500 using HDFC card first transaction"
    },
    {
        "id": 2,
        "text": "5% cashback on Amazon purchases with ICICI credit card no minimum"
    },
    {
        "id": 3,
        "text": "₹500 flat cashback on ₹5000 or more spend with SBI debit card"
    },
    {
        "id": 4,
        "text": "3% cashback on all online transactions with Axis bank up to ₹200"
    },
    {
        "id": 5,
        "text": "15% cashback on first order up to ₹500 on Zomato with Kotak credit card"
    },
    {
        "id": 6,
        "text": "2% flat cashback on all purchases with RBL bank minimum 100"
    },
]

# Initialize RAG on startup
try:
    initialize_rag_with_offers(SAMPLE_OFFERS)
    print("✓ RAG system initialized with sample offers")
except Exception as e:
    print(f"⚠ RAG initialization warning: {e}")


@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    """Check system health and Ollama availability"""
    from datetime import datetime
    
    ollama_ok = is_ollama_available()
    status = "ready" if ollama_ok else "degraded"
    
    return HealthCheckResponse(
        status=status,
        ollama_available=ollama_ok,
        timestamp=datetime.now().isoformat()
    )


@app.post("/calculate", response_model=OfferResponse)
def calculate_cashback(request: OfferRequest):
    """
    Calculate cashback eligibility and amount.
    
    POST body:
    {
        "offer_text": "10% cashback up to ₹100 on min ₹500 using HDFC card",
        "amount": 700,
        "bank": "HDFC",
        "is_first_transaction": true
    }
    
    Returns:
    {
        "eligible": true,
        "cashback": 70.0,
        "offer_details": {...},
        "explanation": "...",
        "reasons": [...],
        "violations": [...]
    }
    """
    try:
        # 1. Parse offer
        parsed_offer = parse_offer(request.offer_text)
        
        # Handle edge cases
        if not parsed_offer.get("percentage"):
            return OfferResponse(
                eligible=False,
                cashback=0.0,
                offer_details=parsed_offer,
                explanation="Could not extract percentage from offer text",
                reasons=[],
                violations=["No percentage found in offer"]
            )
        
        # 2. Prepare transaction data
        transaction_data = {"amount": request.amount}
        
        # 3. Prepare user profile
        user_profile = {
            "bank": request.bank,
            "is_first_transaction": request.is_first_transaction
        }
        
        # 4. Apply rules
        result = apply_rules(transaction_data, parsed_offer, user_profile)
        
        # 5. Generate explanation
        explanation = generate_explanation(
            amount=request.amount,
            cashback=result["cashback"],
            is_eligible=result["eligible"],
            offer_details=parsed_offer,
            reasons=result["reasons"],
            violations=result["violations"]
        )
        
        # 6. Return response
        return OfferResponse(
            eligible=result["eligible"],
            cashback=result["cashback"],
            offer_details=parsed_offer,
            explanation=explanation,
            reasons=result["reasons"],
            violations=result["violations"]
        )
    
    except Exception as e:
        print(f"ERROR in /calculate: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@app.post("/search-offers", response_model=OfferSearchResponse)
def search_offers(request: OfferSearchRequest):
    """
    Search for similar cashback offers using RAG.
    
    POST body:
    {
        "query": "cashback on first transaction HDFC",
        "top_k": 3
    }
    """
    try:
        results = search_similar_offers(request.query, top_k=request.top_k)
        
        return OfferSearchResponse(
            query=request.query,
            results=results,
            count=len(results)
        )
    
    except Exception as e:
        print(f"ERROR in /search-offers: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.get("/offers", response_model=dict)
def get_sample_offers():
    """Get list of sample offers in database"""
    return {
        "total": len(SAMPLE_OFFERS),
        "offers": SAMPLE_OFFERS
    }


@app.get("/explain-offer/{offer_id}")
def get_offer_explanation(offer_id: int, bank: str = "HDFC"):
    """Get explanation for a specific offer"""
    try:
        # Find offer
        offer = next((o for o in SAMPLE_OFFERS if o["id"] == offer_id), None)
        
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        
        # Parse
        parsed = parse_offer(offer["text"])
        
        # Generate explanation
        explanation = explain_offer(parsed, bank)
        
        return {
            "offer_id": offer_id,
            "offer_text": offer["text"],
            "explanation": explanation,
            "parsed": parsed
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in /explain-offer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/")
def root():
    """API root - provides information"""
    return {
        "app": "Cashback Clarity Engine",
        "version": "1.0.0",
        "description": "Offline, Ollama-powered cashback calculation",
        "endpoints": {
            "GET /health": "Check system health",
            "POST /calculate": "Calculate cashback",
            "POST /search-offers": "Search similar offers",
            "GET /offers": "Get sample offers",
            "GET /explain-offer/{id}": "Get offer explanation",
        },
        "ollama": {
            "required": True,
            "start_command": "ollama serve",
            "model": "llama3"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════╗
    ║  Cashback Clarity Engine - Backend Server  ║
    ║     Starting on http://localhost:8000      ║
    ╚════════════════════════════════════════════╝
    """)
    
    print("Checking Ollama...")
    if is_ollama_available():
        print("✓ Ollama is running")
    else:
        print("⚠ Ollama not available. Some features will degrade gracefully.")
        print("   Start Ollama with: ollama serve")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
