"""
Quick test script to debug the document reading issue
"""
import os
os.environ['GROQ_API_KEY'] = 'your_groq_key_here'  # Replace with your actual key

from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService

# Test 1: Check if LLM service is working
print("=" * 60)
print("TEST 1: LLM Service Connection")
print("=" * 60)

try:
    llm = LLMService()
    print(f"✓ LLM Service initialized")
    print(f"  Provider: {llm.provider}")
    print(f"  Model: {llm.model}")
    print(f"  API Key: {llm.api_key[:20]}...")
    
    # Test with document context
    test_context = ["The sky is blue. Grass is green. Water is wet."]
    test_question = "What color is the sky?"
    
    print(f"\n📝 Testing with context...")
    print(f"  Question: {test_question}")
    print(f"  Context: {test_context[0]}")
    
    answer = llm.generate_answer(test_question, test_context)
    print(f"\n✓ Answer: {answer}")
    
    # Check if answer actually uses the context
    if "blue" in answer.lower():
        print("✓ LLM is reading the context correctly!")
    else:
        print("✗ LLM is NOT using the provided context")
        print("  This means the problem is with document chunking/retrieval")
    
except Exception as e:
    print(f"✗ LLM Test Failed: {e}")

# Test 2: Check embedding service
print("\n" + "=" * 60)
print("TEST 2: Embedding Service")
print("=" * 60)

try:
    embed = EmbeddingService()
    print("✓ Embedding Service initialized")
    
    # Test embeddings
    test_texts = ["The sky is blue", "Grass is green"]
    embeddings = embed.get_embeddings(test_texts)
    
    print(f"✓ Generated {len(embeddings)} embeddings")
    print(f"  Embedding dimension: {len(embeddings[0]) if embeddings else 0}")
    
except Exception as e:
    print(f"✗ Embedding Test Failed: {e}")

# Test 3: Full document flow simulation
print("\n" + "=" * 60)
print("TEST 3: Document Processing Flow")
print("=" * 60)

try:
    # Simulate storing a document
    doc_id = "test_doc_123"
    test_chunks = [
        {'text': 'The sky is blue and beautiful.', 'chunk_id': 0},
        {'text': 'Grass is green in the summer.', 'chunk_id': 1},
        {'text': 'Water is wet and refreshing.', 'chunk_id': 2}
    ]
    
    print(f"📄 Storing test document with {len(test_chunks)} chunks...")
    success = embed.store_document_vectors(doc_id, test_chunks)
    
    if success:
        print("✓ Document stored successfully")
        
        # Test search
        query = "What color is the sky?"
        print(f"\n🔍 Searching for: '{query}'")
        results = embed.hybrid_search(query, doc_id, top_k=3)
        
        print(f"✓ Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"    Text: {result['text'][:60]}...")
            print(f"    Score: {result['score']:.4f}")
        
        if results:
            # Test LLM with retrieved context
            context_chunks = [r['text'] for r in results]
            answer = llm.generate_answer(query, context_chunks)
            print(f"\n✓ Final Answer: {answer}")
            
            if "blue" in answer.lower():
                print("\n✅ SYSTEM IS WORKING CORRECTLY!")
            else:
                print("\n⚠️  System retrieved chunks but LLM didn't use them properly")
        else:
            print("\n✗ No results found - this is the problem!")
            print("  The search is returning empty results")
    else:
        print("✗ Failed to store document")
        
except Exception as e:
    print(f"✗ Document Flow Test Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
