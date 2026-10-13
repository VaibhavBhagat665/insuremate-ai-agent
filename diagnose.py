"""
Quick diagnostic script - shows current status in 5 seconds
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def diagnose():
    print("\n" + "="*70)
    print("INSUREMATE AI AGENT - QUICK DIAGNOSTIC")
    print("="*70)
    
    # Check API keys
    print("\nAPI Configuration:")
    print("-" * 70)
    
    llm_config = settings.get_llm_config()
    provider = llm_config.get("provider", "unknown")
    api_key = llm_config.get("api_key", "")
    model = llm_config.get("model", "unknown")
    
    print(f"  Provider: {provider}")
    print(f"  Model: {model}")
    
    if not api_key or api_key.startswith("your_") or len(api_key) < 10:
        print(f"  API Key: [FAIL] NOT CONFIGURED")
        print(f"           Length: {len(api_key)} (should be > 20)")
        print(f"\n  WARNING: No valid API key found!")
        print(f"           This is why the agent returns generic answers.")
    else:
        masked_key = api_key[:8] + "..." + api_key[-4:]
        print(f"  API Key: [PASS] CONFIGURED")
        print(f"           {masked_key} (length: {len(api_key)})")
    
    # Check stored data
    print("\nStored Vector Data:")
    print("-" * 70)
    
    vectors_dir = "data/vectors"
    if os.path.exists(vectors_dir):
        vector_files = os.listdir(vectors_dir)
        print(f"  Vector files: {len(vector_files)} documents stored")
        for vf in vector_files[:5]:  # Show first 5
            doc_id = vf.replace('.pkl.gz', '').replace('.json', '')
            print(f"    - {doc_id}")
        if len(vector_files) > 5:
            print(f"    ... and {len(vector_files) - 5} more")
    else:
        print(f"  Vector files: [FAIL] No data directory found")
    
    # Network check
    print("\nNetwork Connectivity:")
    print("-" * 70)
    
    import requests
    
    endpoints_to_check = [
        ("HuggingFace API", "https://api-inference.huggingface.co"),
        ("Groq API", "https://api.groq.com"),
        ("OpenRouter API", "https://openrouter.ai"),
    ]
    
    for name, url in endpoints_to_check:
        try:
            response = requests.get(url, timeout=3)
            print(f"  {name}: [PASS] Reachable (status: {response.status_code})")
        except Exception as e:
            error_type = type(e).__name__
            print(f"  {name}: [FAIL] Unreachable ({error_type})")
    
    # Summary
    print("\n" + "="*70)
    print("DIAGNOSIS SUMMARY:")
    print("="*70)
    
    has_api_key = api_key and not api_key.startswith("your_") and len(api_key) >= 10
    
    if not has_api_key:
        print("\nCRITICAL ISSUE FOUND:")
        print("   Your .env file has no valid API keys configured.")
        print("\nFIX:")
        print("   1. Get FREE key from: https://console.groq.com")
        print("   2. Edit .env: GROQ_API_KEY=your_key_here")
        print("   3. Run: python test_fixed_agent.py")
        print("\n   Without API keys, agent will only give generic answers!")
    else:
        print("\nAPI Key is configured - agent should work!")
        print("\nNext steps:")
        print("   1. Run full test: python test_fixed_agent.py")
        print("   2. Start server: python -m uvicorn app.main:app --reload")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    diagnose()
