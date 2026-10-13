"""
Test script to check existing stored documents and their embeddings
"""

import sys
import os
import json
import gzip
import pickle

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.core.logging import logger

def test_existing_data():
    """Test with existing stored embeddings"""
    
    print("="*80)
    print("TESTING EXISTING DATA")
    print("="*80)
    
    # Check what documents we have
    vectors_dir = "data/vectors"
    indexes_dir = "data/indexes"
    
    print(f"\n[STEP 1] Checking stored data...")
    print(f"  Vectors directory: {vectors_dir}")
    print(f"  Indexes directory: {indexes_dir}")
    
    # List vector files
    if os.path.exists(vectors_dir):
        vector_files = os.listdir(vectors_dir)
        print(f"\n  Found {len(vector_files)} vector files:")
        for vf in vector_files:
            print(f"    - {vf}")
            # Extract doc_id
            doc_id = vf.replace('.pkl.gz', '').replace('.json', '')
            
            # Try to load vectors
            print(f"\n      Loading vectors for doc_id: {doc_id}")
            try:
                vector_path = os.path.join(vectors_dir, vf)
                if vf.endswith('.pkl.gz'):
                    with gzip.open(vector_path, 'rb') as f:
                        vectors = pickle.load(f)
                    print(f"        ✓ Loaded {len(vectors)} vectors from compressed file")
                elif vf.endswith('.json'):
                    with open(vector_path, 'r', encoding='utf-8') as f:
                        vectors = json.load(f)
                    print(f"        ✓ Loaded {len(vectors)} vectors from JSON file")
                
                if vectors:
                    sample = vectors[0]
                    print(f"        Sample vector structure:")
                    print(f"          - Keys: {list(sample.keys())}")
                    print(f"          - Embedding dimension: {len(sample.get('embedding', []))}")
                    if 'metadata' in sample:
                        print(f"          - Metadata keys: {list(sample['metadata'].keys())}")
                        print(f"          - Sample text: {sample['metadata'].get('text', '')[:100]}...")
                    
            except Exception as e:
                print(f"        ✗ Failed to load: {e}")
    else:
        print(f"  ✗ Vectors directory not found!")
        return
    
    # Now test search and retrieval
    print(f"\n[STEP 2] Testing search and retrieval...")
    
    # Initialize services
    embedding_service = EmbeddingService()
    llm_service = LLMService()
    
    # Test with first available doc_id
    if vector_files:
        doc_id = vector_files[0].replace('.pkl.gz', '').replace('.json', '')
        print(f"\n  Testing with doc_id: {doc_id}")
        
        # Test questions
        test_questions = [
            "What is this document about?",
            "What is the policy number?",
            "What are the coverage details?",
            "What is the premium amount?",
            "What is the deductible?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n  Question {i}: {question}")
            
            try:
                # Search
                search_results = embedding_service.hybrid_search(
                    query=question,
                    doc_id=doc_id,
                    top_k=5
                )
                
                print(f"    Search results: {len(search_results)} chunks")
                
                if search_results:
                    print(f"    Top result scores:")
                    for j, result in enumerate(search_results[:3], 1):
                        score = result.get('score', 0)
                        text_preview = result.get('text', '')[:80]
                        print(f"      [{j}] Score: {score:.3f} | {text_preview}...")
                    
                    # Generate answer
                    context_chunks = [result['text'] for result in search_results]
                    answer = llm_service.generate_answer(question, context_chunks)
                    
                    print(f"\n    LLM Answer:")
                    print(f"    {answer}")
                    
                    # Check if it's a "no data" response
                    no_data_phrases = [
                        "document doesn't contain",
                        "no information",
                        "not available",
                        "cannot find",
                        "doesn't provide"
                    ]
                    
                    is_no_data = any(phrase in answer.lower() for phrase in no_data_phrases)
                    
                    if is_no_data:
                        print(f"    ⚠ WARNING: This looks like a 'no data' response!")
                        print(f"    Problem: LLM might not be seeing the context properly")
                    else:
                        print(f"    ✓ Got a proper answer!")
                    
                else:
                    print(f"    ✗ NO SEARCH RESULTS - Embeddings might be broken!")
                    
            except Exception as e:
                print(f"    ✗ Error: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_existing_data()
