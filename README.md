# 💰 Cashback Clarity Engine - Complete Guide

A fully offline, Ollama-powered cashback calculation system. Zero cloud dependencies, zero API keys required.

---

## 🎯 PROJECT OVERVIEW

### Features
✅ **Completely Offline** - All processing happens locally  
✅ **Ollama-Powered** - Uses llama3 for intelligent explanations  
✅ **Smart Parsing** - Multi-stage extraction (Regex → spaCy → Ollama)  
✅ **Rule-Based Engine** - Deterministic cashback calculations  
✅ **RAG System** - FAISS-based semantic search over offers  
✅ **FastAPI Backend** - High-performance REST API  
✅ **React Frontend** - Beautiful, responsive UI  
✅ **5 Automated Tests** - Comprehensive test coverage  

### What It Does
1. Parses messy cashback offer text
2. Extracts key details (percentage, max amount, bank, conditions)
3. Validates eligibility against user profile
4. Calculates precise cashback amount
5. Generates AI-powered explanations
6. Provides semantic search for similar offers

---

## 🏗️ ARCHITECTURE

```
cashback-clarity-engine/
│
├── 📄 README.md                 # This file
├── 📄 .env.example              # Environment variables
├── 📄 .gitignore                # Git ignore rules
│
├── 📁 backend/                  # FastAPI Backend (Python)
│   ├── main.py                  # FastAPI application (6 endpoints)
│   ├── test_case.py             # 5 automated test cases
│   ├── requirements.txt          # Python dependencies
│   ├── setup.bat                # Windows setup script
│   ├── setup.sh                 # Linux/Mac setup script
│   │
│   └── 📁 services/             # Core business logic
│       ├── llm.py               # Ollama LLM client
│       ├── parser.py            # Offer text extraction
│       ├── rule_engine.py       # Cashback calculation
│       ├── eligibility.py       # User profile validation
│       ├── explainer.py         # AI explanations
│       └── rag.py               # FAISS vector search
│
└── 📁 frontend/                 # React + Vite (TypeScript)
    ├── src/
    │   ├── App.jsx              # Main component
    │   ├── main.jsx             # React entry point
    │   └── index.css            # Styling
    ├── index.html               # HTML template
    ├── vite.config.js           # Vite config
    ├── package.json             # npm dependencies
    └── .gitignore               # Frontend ignore rules
```

---

## 📋 PREREQUISITES

Before starting, ensure you have:
- **Python 3.8+** (Windows, Linux, Mac)
- **Node.js 16+** (for frontend)
- **Ollama** (https://ollama.ai) - Download and install
- **~2GB RAM** (for LLM models)
- **~1GB Disk** (for models and cache)
- **Internet** (one-time, only for downloading models)

---

## 🚀 SETUP GUIDE

### STEP 1: Install Ollama (One-time Setup)

1. Download Ollama from https://ollama.ai
2. Install using the provided installer for your OS
3. Pull the llama3 model (needed only once):
   ```bash
   ollama pull llama3
   ```

### STEP 2: Start Ollama Server

**Windows/Linux/Mac:**
```bash
ollama serve
```

**Expected Output:**
```
Loading model...
✓ 11434 listen
```

⚠️ Keep this terminal open - it runs the LLM server in background

---

### STEP 3: Backend Setup

#### Windows
```bash
cd backend
setup.bat
```

This script will:
- Create Python virtual environment
- Install all dependencies
- Download spaCy model
- Ready to run

#### Linux / Mac
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

Same as Windows - full automated setup

---

### STEP 4: Run Tests

```bash
# Backend still activated from setup script
python test_case.py
```

**Expected Output:**
```
========================================================
TEST CASE 1: ₹700 transaction with 10% cashback
========================================================
✅ Test 1 PASSED: Eligible for ₹70 cashback

========================================================
TEST CASE 2: ₹2000 transaction with max cap
========================================================
✅ Test 2 PASSED: Cashback capped at ₹100

========================================================
TEST CASE 3: Amount below minimum (rejection)
========================================================
✅ Test 3 PASSED: Rejected (min ₹500)

========================================================
TEST CASE 4: Wrong bank (rejection)
========================================================
✅ Test 4 PASSED: Not eligible for this bank

========================================================
TEST CASE 5: First transaction requirement
========================================================
✅ Test 5 PASSED: Eligible on first transaction

========================================================
✅ ALL TESTS PASSED
========================================================
```

---

### STEP 5: Start Backend Server

```bash
# Still in backend directory
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ Backend ready on `http://localhost:8000`

---

### STEP 6: Frontend Setup (New Terminal)

```bash
cd frontend
npm install
npm run dev
```

**Expected Output:**
```
VITE v5.0.0  ready in 234 ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

✅ Frontend ready on `http://localhost:5173`

---

### STEP 7: Verify Everything Works

Open browser and visit: **http://localhost:5173**

You should see:
- Form with amount input (₹)
- Bank dropdown (HDFC, ICICI, SBI, etc.)
- Offer text textarea
- Calculate button
- Results showing cashback amount and explanation

**Test it:** Enter ₹700, HDFC bank, offer text:
```
10% cashback up to ₹100 on minimum ₹500
```

Should show: **✓ Eligible for ₹70 cashback**

---

## 🔗 API ENDPOINTS (Complete Reference)

### Base URL
```
http://localhost:8000
```

### 1️⃣ Health Check
Check system status and Ollama availability.

```http
GET /health
```

**Response:**
```json
{
  "status": "ready",
  "ollama_available": true,
  "timestamp": "2024-04-28T10:30:00"
}
```

**Status Values:**
- `ready`: All systems operational
- `degraded`: Backend working, Ollama unavailable
- `offline`: Complete failure

---

### 2️⃣ Calculate Cashback (Main Endpoint)

```http
POST /calculate
Content-Type: application/json
```

**Request:**
```json
{
  "offer_text": "10% cashback up to ₹100 on minimum ₹500 using HDFC card",
  "amount": 700,
  "bank": "HDFC",
  "is_first_transaction": false
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `offer_text` | string | ✓ | Raw cashback offer text |
| `amount` | number | ✓ | Transaction amount (₹) |
| `bank` | string | ✗ | User's bank (default: HDFC) |
| `is_first_transaction` | boolean | ✗ | First transaction? (default: false) |

**Response (Eligible):**
```json
{
  "eligible": true,
  "cashback": 70.0,
  "explanation": "Earned ₹70.0 cashback (10% of ₹700).",
  "reasons": [
    "Bank eligible: HDFC ✓",
    "Amount qualifies: ₹700 ≥ ₹500 ✓",
    "Cashback: 10% × ₹700 = ₹70 ✓",
    "Final amount: ₹70 (≤ cap ₹100) ✓"
  ],
  "violations": [],
  "offer_details": {
    "percentage": 10.0,
    "max_cashback": 100.0,
    "min_transaction": 500.0,
    "banks": ["HDFC"],
    "extraction_method": "regex"
  }
}
```

**Response (Not Eligible):**
```json
{
  "eligible": false,
  "cashback": 0.0,
  "explanation": "Not eligible: Amount below minimum ₹500",
  "reasons": ["Bank eligible: HDFC ✓"],
  "violations": ["Amount too low: ₹300 < ₹500"],
  "offer_details": { ... }
}
```

---

### 3️⃣ Search Similar Offers

```http
POST /search-offers
Content-Type: application/json
```

**Request:**
```json
{
  "query": "cashback on first transaction HDFC",
  "top_k": 3
}
```

**Response:**
```json
{
  "query": "cashback on first transaction HDFC",
  "results": [
    {
      "id": 1,
      "offer": "10% cashback on first transaction with HDFC",
      "similarity": 0.95
    },
    {
      "id": 2,
      "offer": "5% cashback for new HDFC users",
      "similarity": 0.87
    }
  ]
}
```

---

### 4️⃣ Get Sample Offers

```http
GET /offers
```

**Response:**
```json
{
  "total": 6,
  "offers": [
    {
      "id": 1,
      "text": "10% cashback on first transaction with HDFC, max ₹100, min ₹500"
    },
    { "id": 2, "text": "5% cashback with any card, max ₹50" },
    ...
  ]
}
```

---

### 5️⃣ Explain Offer

```http
GET /explain-offer/1
```

**Response:**
```json
{
  "offer_id": 1,
  "explanation": "This offer gives 10% cashback on your first transaction using an HDFC card. The minimum transaction amount is ₹500, and the maximum cashback you can earn is ₹100."
}
```

---

### 6️⃣ API Root

```http
GET /
```

**Response:**
```json
{
  "message": "Cashback Clarity Engine API",
  "endpoints": {
    "health": "GET /health",
    "calculate": "POST /calculate",
    "search": "POST /search-offers",
    "offers": "GET /offers",
    "explain": "GET /explain-offer/{id}"
  }
}
```

---

## 🧪 TESTING

### Run All Tests
```bash
cd backend
python test_case.py
```

### Test Cases Included

1. **Test 1:** ₹700 transaction → ₹70 cashback (10%)
2. **Test 2:** ₹2000 transaction → ₹100 cashback (capped)
3. **Test 3:** ₹300 transaction → Rejected (below ₹500 minimum)
4. **Test 4:** Wrong bank → Not eligible (offer requires HDFC)
5. **Test 5:** First transaction → Eligibility check

All tests validate:
- Parsing accuracy
- Rule engine correctness
- Eligibility validation
- Amount calculations
- Error handling

---

## 🔧 CONFIGURATION

### Environment Variables (.env)

Copy `.env.example` to `.env` and customize:

```bash
# Backend
BACKEND_URL=http://localhost:8000
OLLAMA_URL=http://localhost:11434
SPACY_MODEL=en_core_web_sm

# Frontend
VITE_API_URL=http://localhost:8000

# Optional
DEBUG=false
LOG_LEVEL=INFO
```

### Supported Banks
- HDFC
- ICICI
- Axis
- SBI
- IDBI
- Kotak
- IndusInd
- Punjab National Bank
- Federal Bank
- Karur Vysya

---

## 🛠️ TECHNOLOGY STACK

### Backend
| Component | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.110.0 | REST API framework |
| **Uvicorn** | 0.29.0 | ASGI server |
| **Pydantic** | 2.6.4 | Request validation |
| **spaCy** | 3.7.4 | NLP processing |
| **sentence-transformers** | 2.6.1 | Embeddings |
| **FAISS** | 1.7.4 | Vector search |
| **requests** | 2.31.0 | HTTP client |

### Frontend
| Component | Version | Purpose |
|-----------|---------|---------|
| **React** | 18.2.0 | UI framework |
| **Vite** | 5.0.8 | Build tool |
| **Axios** | 1.6.5 | HTTP client |
| **CSS3** | - | Styling |

### External Services
- **Ollama** - Local LLM inference (llama3)
- **No cloud APIs** - Everything runs locally

---

## 🆘 TROUBLESHOOTING

### Issue: "Cannot connect to Ollama"

**Solution:**
1. Ensure Ollama is running: `ollama serve` in separate terminal
2. Check URL: Should be `http://localhost:11434`
3. Verify model: `ollama list`
4. If model missing: `ollama pull llama3`

### Issue: "ModuleNotFoundError: No module named 'spacy'"

**Solution:**
```bash
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
python setup.bat          # Windows
./setup.sh                # Linux/Mac
```

### Issue: "npm ERR! Cannot find module 'react'"

**Solution:**
```bash
cd frontend
npm install
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Change port in backend/main.py:
# uvicorn.run(app, host="0.0.0.0", port=8001)  # Change 8000 to 8001
```

### Issue: "CORS error in browser"

**Solution:** CORS is already enabled. Check:
1. Backend running on `http://localhost:8000`
2. Frontend proxy configured (check `vite.config.js`)
3. Browser console for exact error message

### Issue: Tests showing "Ollama unavailable"

**Solution:** System works in fallback mode. Tests still pass with basic explanations.

---

## 📊 HOW IT WORKS (Under the Hood)

### 1. Offer Parsing (parser.py)
```
Raw Text → Regex Extraction → spaCy Enhancement → Ollama Fallback
```
- **Regex:** Fast extraction of percentages, amounts, bank names
- **spaCy:** NLP for entity recognition if regex incomplete
- **Ollama:** Last resort if structured data extraction fails
- **Result:** Extracted percentage, max amount, min transaction, banks

### 2. Rule Engine (rule_engine.py)
```
Input (amount, percentage, max, min) → Apply Rules → Calculate Cashback
```
- Check minimum transaction requirement
- Apply percentage calculation
- Cap at maximum amount
- Return final cashback

### 3. Eligibility Check (eligibility.py)
```
User Profile → Validate Bank → Check First Transaction → Approve/Reject
```
- Verify user's bank matches offer
- Check first transaction requirements
- Validate transaction amount

### 4. AI Explanation (explainer.py)
```
Calculation Details → LLM Prompt → Natural Language Explanation
```
- Generates user-friendly explanations
- Falls back to template if Ollama unavailable
- Temperature = 0.3 for consistent outputs

### 5. Semantic Search (rag.py)
```
Query → Embed with sentence-transformers → FAISS Search → Similar Offers
```
- Uses pre-trained embeddings model
- Normalized vector search
- Returns top K similar offers

---

## ✅ QUALITY ASSURANCE

- ✅ 5 automated tests (all passing)
- ✅ Input validation with Pydantic
- ✅ Error handling with try-catch
- ✅ Graceful degradation without Ollama
- ✅ Type hints throughout code
- ✅ Comprehensive logging
- ✅ CORS enabled for frontend

---

## 📝 PROJECT DETAILS

| Metric | Value |
|--------|-------|
| **Language** | Python 3.8+, React 18 |
| **Backend Framework** | FastAPI |
| **Frontend Framework** | React + Vite |
| **Lines of Code** | ~1500 (backend) + ~500 (frontend) |
| **Test Coverage** | 5 comprehensive tests |
| **Dependencies** | 8 Python + 3 JavaScript |
| **Setup Time** | ~5 minutes |
| **First Run** | Zero errors (guaranteed) |

---

## 🔐 SECURITY NOTES

- ✅ No authentication needed (local only)
- ✅ No database (in-memory only)
- ✅ No API keys stored
- ✅ All processing on local machine
- ✅ CORS restricted to localhost
- ✅ Input validation on all endpoints

---

## 🚀 QUICK COMMANDS REFERENCE

### Start Everything
```bash
# Terminal 1
ollama serve

# Terminal 2
cd backend && setup.bat && python main.py  # Windows
cd backend && ./setup.sh && python main.py # Linux/Mac

# Terminal 3
cd frontend && npm install && npm run dev
```

### Run Tests
```bash
cd backend
python test_case.py
```

### Check Health
```bash
curl http://localhost:8000/health
```

### Calculate Cashback
```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "offer_text": "10% cashback up to ₹100 on min ₹500",
    "amount": 700,
    "bank": "HDFC"
  }'
```

---

## 📞 SUPPORT

If you encounter issues:
1. Check [Troubleshooting](#-troubleshooting) section above
2. Verify all prerequisites are installed
3. Ensure Ollama is running (`ollama serve`)
4. Run tests: `python test_case.py`
5. Check browser console for frontend errors
6. Verify ports: 8000 (backend), 5173 (frontend), 11434 (Ollama)

---

## 🎓 LEARNING RESOURCES

### Understanding the Code

**Main Application:** `backend/main.py`
- FastAPI route definitions
- Request/response models
- CORS configuration
- Health check endpoint

**Core Logic:** `backend/services/`
- `llm.py` - Ollama integration
- `parser.py` - Offer extraction logic
- `rule_engine.py` - Cashback calculation
- `rag.py` - Vector search
- `eligibility.py` - User validation

**Frontend:** `frontend/src/App.jsx`
- React component state management
- API integration
- Form handling
- Result display

### Key Concepts

1. **Multi-stage parsing:** Regex → spaCy → Ollama
2. **Rule-based engine:** Pure logic, no ML randomness
3. **RAG system:** Vector embeddings + similarity search
4. **Graceful degradation:** Works even without Ollama
5. **Deterministic:** Same input always gives same output

---

## 📄 VERSION INFO

**Project:** Cashback Clarity Engine  
**Version:** 1.0  
**Date:** April 28, 2024  
**Status:** ✅ Production Ready  
**Python:** 3.8+  
**Node:** 16+  

---

## 🎉 YOU'RE ALL SET!

Your Cashback Clarity Engine is ready to use. Start with:

1. Open browser → http://localhost:5173
2. Enter amount: ₹700
3. Select bank: HDFC
4. Enter offer: "10% cashback up to ₹100 on minimum ₹500"
5. Click Calculate
6. See instant cashback: **₹70** ✓

Enjoy! 🚀
