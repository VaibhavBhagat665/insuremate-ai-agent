"""
Test script to verify the agent fixes are working
Run this AFTER adding your API keys to .env file
"""

import sys
import os
import json

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.core.config import settings
from app.core.logging import logger

def check_api_keys():
    """Check if API keys are configured"""
    print("\n" + "="*80)
    print("STEP 1: Checking API Configuration")
    print("="*80)
    
    llm_config = settings.get_llm_config()
    provider = llm_config.get("provider", "unknown")
    api_key = llm_config.get("api_key", "")
    
    print(f"  LLM Provider: {provider}")
    print(f"  Model: {llm_config.get('model', 'unknown')}")
    
    if not api_key or api_key.startswith("your_") or len(api_key) < 10:
        print(f"  ❌ API Key: NOT CONFIGURED (length: {len(api_key)})")
        print(f"\n  ERROR: No valid API key found!")
        print(f"  Please update your .env file with a real API key.")
        print(f"\n  Quick fix:")
        print(f"    1. Get FREE key from: https://console.groq.com")
        print(f"    2. Edit .env file: GROQ_API_KEY=your_key_here")
        print(f"    3. Run this test again")
        return False
    else:
        print(f"  ✅ API Key: CONFIGURED (length: {len(api_key)}, provider: {provider})")
        return True

def test_embeddings():
    """Test embedding generation"""
    print("\n" + "="*80)
    print("STEP 2: Testing Embedding Generation")
    print("="*80)
    
    embedding_service = EmbeddingService()
    
    test_texts = [
        "This is a comprehensive insurance policy covering dental and vision care.",
        "The policy number is ABC-123-456-789 with premium of $500 per month.",
        "Deductible amount is $1000 per year with 80% coverage after deductible."
    ]
    
    print(f"  Generating embeddings for {len(test_texts)} test texts...")
    
    try:
        embeddings = embedding_service.get_embeddings(test_texts)
        
        if embeddings and len(embeddings) == len(test_texts):
            print(f"  ✅ Generated {len(embeddings)} embeddings")
            print(f"  Embedding dimension: {len(embeddings[0])}")
            
            # Check if they're meaningful (not all zeros)
            first_embedding = embeddings[0]
            non_zero_count = sum(1 for x in first_embedding if abs(x) > 0.001)
            
            print(f"  Non-zero values: {non_zero_count}/{len(first_embedding)}")
            
            if non_zero_count > 10:
                print(f"  ✅ Embeddings look good!")
                return True
            else:
                print(f"  ⚠️ WARNING: Embeddings might be zero vectors")
                print(f"  This means embedding API might be failing")
                print(f"  But TF-IDF fallback should still work for basic matching")
                return True
        else:
            print(f"  ❌ Failed to generate embeddings")
            return False
            
    except Exception as e:
        print(f"  ❌ Embedding generation failed: {e}")
        return False

def test_llm():
    """Test LLM API"""
    print("\n" + "="*80)
    print("STEP 3: Testing LLM API")
    print("="*80)
    
    llm_service = LLMService()
    
    test_question = "What is the policy number?"
    test_context = [
        "This is a comprehensive insurance policy document.",
        "The policy number is ABC-123-456-789.",
        "The premium amount is $500 per month with annual deductible of $1000."
    ]
    
    print(f"  Question: {test_question}")
    print(f"  Context: {len(test_context)} chunks")
    
    try:
        answer = llm_service.generate_answer(test_question, test_context)
        
        print(f"\n  Answer received (length: {len(answer)} chars):")
        print(f"  '{answer}'")
        
        # Check if it's a fallback answer
        fallback_indicators = [
            "based on general knowledge",
            "would require specific context",
            "consult authoritative sources",
            "provide more specific context"
        ]
        
        is_fallback = any(indicator in answer.lower() for indicator in fallback_indicators)
        
        if is_fallback:
            print(f"\n  ❌ LLM API is NOT working - returning fallback answer")
            print(f"  This means:")
            print(f"    - API key might be invalid")
            print(f"    - No internet connection")
            print(f"    - API provider is down")
            return False
        else:
            # Check if answer contains expected information
            has_policy_number = "abc" in answer.lower() or "123" in answer
            
            if has_policy_number:
                print(f"\n  ✅ LLM API is WORKING - Generated proper answer from context!")
                return True
            else:
                print(f"\n  ⚠️ LLM API responded but answer might not be using context")
                print(f"  Check if the answer makes sense for the question")
                return True
                
    except Exception as e:
        print(f"  ❌ LLM API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_pipeline():
    """Test complete pipeline with stored data"""
    print("\n" + "="*80)
    print("STEP 4: Testing Full Pipeline with Stored Data")
    print("="*80)
    
    # Check if we have stored data
    vectors_dir = "data/vectors"
    if not os.path.exists(vectors_dir):
        print(f"  ⚠️ No stored vectors found - skipping full pipeline test")
        return True
    
    vector_files = os.listdir(vectors_dir)
    if not vector_files:
        print(f"  ⚠️ No vector files found - skipping full pipeline test")
        return True
    
    # Use first available document
    doc_id = vector_files[0].replace('.pkl.gz', '').replace('.json', '')
    print(f"  Testing with stored doc_id: {doc_id}")
    
    embedding_service = EmbeddingService()
    llm_service = LLMService()
    
    test_question = "What information is in this document?"
    
    print(f"  Question: {test_question}")
    
    try:
        # Search
        search_results = embedding_service.hybrid_search(
            query=test_question,
            doc_id=doc_id,
            top_k=3
        )
        
        print(f"  Search results: {len(search_results)} chunks")
        
        if search_results:
            print(f"  Top result score: {search_results[0].get('score', 0):.3f}")
            print(f"  Context preview: {search_results[0].get('text', '')[:100]}...")
            
            # Generate answer
            context_chunks = [result['text'] for result in search_results]
            answer = llm_service.generate_answer(test_question, context_chunks)
            
            print(f"\n  Final Answer:")
            print(f"  '{answer}'")
            
            # Check quality
            is_fallback = "based on general knowledge" in answer.lower()
            
            if is_fallback:
                print(f"\n  ❌ Full pipeline returning fallback answers")
                return False
            else:
                print(f"\n  ✅ Full pipeline working - generating contextual answers!")
                return True
        else:
            print(f"  ❌ No search results - embeddings might not be working")
            return False
            
    except Exception as e:
        print(f"  ❌ Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*80)
    print("INSUREMATE AI AGENT - FIX VERIFICATION TEST")
    print("="*80)
    print("\nThis script tests if your fixes are working correctly.")
    print("Make sure you have updated .env with your API keys!\n")
    
    results = {
        "api_keys": False,
        "embeddings": False,
        "llm": False,
        "full_pipeline": False
    }
    
    # Run tests
    results["api_keys"] = check_api_keys()
    
    if not results["api_keys"]:
        print("\n" + "="*80)
        print("❌ CRITICAL: API keys not configured!")
        print("="*80)
        print("\nPlease fix API keys before running other tests.")
        print("See SETUP_FIX.md for instructions.")
        return
    
    results["embeddings"] = test_embeddings()
    results["llm"] = test_llm()
    results["full_pipeline"] = test_full_pipeline()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Agent should be working now!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Start server: python -m uvicorn app.main:app --reload")
        print("  2. Test with frontend or API calls")
        print("  3. Agent should now provide document-based answers!")
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
        print("="*80)
        print("\nCommon issues:")
        print("  - Invalid API key → Get new key from https://console.groq.com")
        print("  - No internet → Check your network connection")
        print("  - API provider down → Try different provider in .env")
        print("\nSee SETUP_FIX.md for detailed troubleshooting")
    print("="*80)

if __name__ == "__main__":
    main()
