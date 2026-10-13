# 🔧 AGENT NOT ANSWERING - FIX GUIDE

## **ROOT CAUSE IDENTIFIED:**

Your agent is returning generic/fallback answers because:

1. ❌ **NO API KEYS CONFIGURED** - All LLM API calls returning 401 Unauthorized
2. ❌ **NO INTERNET/NETWORK** - Cannot reach HuggingFace or external APIs  
3. ⚠️ **FALLBACK MODE ACTIVE** - System using generic responses

## **QUICK FIX - 3 STEPS:**

### **Step 1: Get FREE API Keys** (Pick ONE)

#### Option A: Groq (FASTEST & EASIEST - RECOMMENDED)
```bash
# 1. Go to: https://console.groq.com
# 2. Sign up with Google/GitHub
# 3. Go to "API Keys" → Create new key
# 4. Copy the key (starts with "gsk_...")
```

#### Option B: Google Gemini (FREE & UNLIMITED)
```bash
# 1. Go to: https://aistudio.google.com/app/apikey
# 2. Sign in with Google
# 3. Click "Create API Key"
# 4. Copy the key
```

#### Option C: OpenRouter (PAID but flexible)
```bash
# 1. Go to: https://openrouter.ai/keys
# 2. Sign up
# 3. Add credits ($5 minimum)
# 4. Create API key
```

### **Step 2: Update .env File**

Edit `.env` file and replace placeholder keys:

```bash
# Example with Groq (RECOMMENDED):
GROQ_API_KEY=gsk_YOUR_ACTUAL_KEY_HERE
GROQ_MODEL=llama-3.3-70b-versatile

# OR with Gemini:
GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_KEY_HERE
GEMINI_MODEL=gemini-2.0-flash-exp

# OR with OpenRouter:
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

### **Step 3: Test the Fix**

```bash
# Run the test script
python test_fixed_agent.py
```

## **HOW TO CHECK IF IT'S WORKING:**

### ✅ **Working Signs:**
- LLM API returns 200 OK (not 401)
- Embeddings generated successfully
- Answers are specific to document content
- Search results have scores > 0.1

### ❌ **Still Broken Signs:**
- 401 Unauthorized errors
- Generic/fallback answers
- Search scores around 0.05
- "Based on general knowledge..." responses

## **OFFLINE/NO-INTERNET FALLBACK:**

I've added local TF-IDF embeddings as fallback. But **you still need an LLM API key** for the agent to answer questions properly.

## **TESTING CHECKLIST:**

Run these commands in order:

```bash
# 1. Check your .env file has real keys
cat .env | findstr "API_KEY"

# 2. Test the fixed agent
python test_fixed_agent.py

# 3. Start the server
python -m uvicorn app.main:app --reload --port 8000

# 4. Test with curl (Windows)
curl -X POST http://localhost:8000/hackrx/run -H "Content-Type: application/json" -d "{\"documents\": \"https://example.com/doc.pdf\", \"questions\": [\"What is this about?\"]}"
```

## **COMMON ERRORS & FIXES:**

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | Invalid/missing API key | Add real API key to .env |
| `getaddrinfo failed` | No internet connection | Check your network |
| `Score: 0.054` | Zero vector embeddings | Will use TF-IDF fallback now |
| `"Based on general knowledge..."` | LLM API failing | Check API key & network |

## **RECOMMENDED SETUP (FREE):**

```bash
# .env file with Groq (BEST FREE OPTION)
GROQ_API_KEY=gsk_YOUR_KEY_FROM_CONSOLE_GROQ_COM
GROQ_MODEL=llama-3.3-70b-versatile

# Everything else can stay default
```

## **NEXT STEPS:**

1. ✅ Get a FREE Groq API key → https://console.groq.com
2. ✅ Update `.env` file with your key
3. ✅ Run `python test_fixed_agent.py` to verify
4. ✅ Start server: `python -m uvicorn app.main:app --reload`
5. ✅ Test with frontend or curl

**After fixing, the agent will provide actual document-based answers instead of generic fallbacks!**
