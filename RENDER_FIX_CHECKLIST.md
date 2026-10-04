# 🔧 Render Deployment Fix Checklist

## ✅ Confirmed Working Locally
The system works perfectly on local machine:
- LLM reads documents correctly
- Embeddings work
- Context is properly passed to LLM
- Answers are accurate

## 🔍 Issue is on Render

### Root Cause Analysis
Based on the screenshot showing generic answers on your deployed site, the issue is **environment configuration on Render**.

## 🚀 Fix Steps for Render

### Step 1: Update Environment Variables
Go to your Render dashboard → Your service → Environment

**Update these variables:**
```
GROQ_MODEL=openai/gpt-oss-120b
```

Make sure you have:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

### Step 2: Check Other Critical Variables
Ensure these are NOT set incorrectly:
```
# These should NOT be set (or set correctly)
OPENROUTER_API_KEY=(leave empty or remove)
OPENAI_API_KEY=(leave empty or remove)
GEMINI_API_KEY=(leave empty or remove)
```

### Step 3: Force Redeploy
After updating environment variables:
1. Go to "Manual Deploy" tab
2. Click "Clear build cache & deploy"
3. Wait for deployment to complete

### Step 4: Check Render Logs
After deployment, check logs for:
- ✅ `LLM service initialized with groq: openai/gpt-oss-120b`
- ❌ Any errors about API keys or models

### Step 5: Test the Endpoint
Test with curl or Postman:
```bash
curl -X POST "https://your-render-url.onrender.com/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/test.pdf",
    "questions": ["What is this document about?"]
  }'
```

## 🐛 Common Render Issues

### Issue 1: Old Environment Variables
**Problem:** Render caches old env vars even after updates
**Solution:** Use "Clear build cache & deploy"

### Issue 2: Model Name Mismatch  
**Problem:** Still using deprecated model name
**Solution:** Ensure `GROQ_MODEL=openai/gpt-oss-120b` (with the slash!)

### Issue 3: API Key Not Set
**Problem:** GROQ_API_KEY missing or wrong
**Solution:** Double-check the key in Render dashboard

### Issue 4: Wrong Base URL
**Problem:** Using old Groq endpoint
**Solution:** The code now uses correct endpoint, just redeploy

## 📊 Expected Behavior After Fix

**Before Fix (Current):**
```
Answer: "Regarding your question about whats this about, this is an interesting 
topic that encompasses various aspects. While I don't have the specific document 
context..."
```

**After Fix:**
```
Answer: "This document is about [actual content from the document]. It covers 
[specific details from the PDF]..."
```

## 🔍 Debugging on Render

### View Real-Time Logs:
1. Go to Render dashboard
2. Click on your service
3. Go to "Logs" tab
4. Look for these lines:
   - `LLM service initialized with groq: openai/gpt-oss-120b` ✅
   - `Generated answer for query` ✅
   - `All APIs failed, generating knowledge-based answer` ❌ (this means API failing)

### If Still Showing Generic Answers:
Check logs for:
```
WARNING - Primary API call failed: Client error '404 Not Found'
```
This means the model name is still wrong.

Or:
```
WARNING - Primary API call failed: Client error '401 Unauthorized'
```
This means the API key is wrong or missing.

## ✅ Verification

After fixing, test with a real document:
1. Upload the Schedule.pdf from your screenshot
2. Ask "What is this about?"
3. Should get specific answer about schedule/meetings/events in the PDF
4. NOT a generic "I don't have document context" response

## 🆘 If Still Not Working

1. Check if Render has the latest code:
   - Look at commit hash in Render dashboard
   - Should match your latest GitHub commit: `45541e6`

2. Verify the fix was deployed:
   - Check `app/core/config.py` in Render's file system
   - Should show `groq_model: Optional[str] = "openai/gpt-oss-120b"`

3. Contact me with:
   - Screenshot of Render environment variables
   - Last 50 lines of Render logs
   - Screenshot of test result

## 📝 Summary

The code works perfectly. The issue is **only on Render deployment**. Just update the `GROQ_MODEL` environment variable and redeploy with cache cleared.
