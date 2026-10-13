"""
Debug script to test the full pipeline and identify issues
Tests: document processing, embedding, retrieval, and LLM response
"""

import sys
import os
import json

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.core.logging import logger
import asyncio

async def test_full_pipeline():
    """Test the complete agent pipeline"""
    
    print("="*80)
    print("AGENT PIPELINE DEBUGGING TEST")
    print("="*80)
    
    # Test document URL
    test_url = "https://dka0cdhxq50w8.cloudfront.net/test_doc_123.pdf"
    test_questions = [
        "What is the policy number?",
        "What is covered under this policy?",
        "What is the premium amount?"
    ]
    
    # Step 1: Initialize services
    print("\n[STEP 1] Initializing services...")
    try:
        doc_processor = DocumentProcessor()
        embedding_service = EmbeddingService()
        llm_service = LLMService()
        print("✓ Services initialized successfully")
    except Exception as e:
        print(f"✗ FAILED to initialize services: {e}")
        return
    
    # Step 2: Process document
    print(f"\n[STEP 2] Processing document: {test_url}")
    try:
        doc_id, chunks = await doc_processor.process_document_from_url(test_url)
        print(f"✓ Document processed successfully")
        print(f"  - Document ID: {doc_id}")
        print(f"  - Number of chunks: {len(chunks)}")
        print(f"  - First chunk preview: {chunks[0]['text'][:200]}...")
        
        # Verify chunks have required fields
        if chunks:
            print(f"\n  Chunk structure verification:")
            sample_chunk = chunks[0]
            print(f"    - Has 'text' field: {'text' in sample_chunk}")
            print(f"    - Has 'doc_id' field: {'doc_id' in sample_chunk}")
            print(f"    - Has 'chunk_quality_score': {'chunk_quality_score' in sample_chunk}")
            print(f"    - Text length: {len(sample_chunk.get('text', ''))}")
    except Exception as e:
        print(f"✗ FAILED to process document: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Verify embeddings are stored
    print(f"\n[STEP 3] Verifying embeddings storage...")
    try:
        # Check if vectors are in cache
        with embedding_service.vectors_cache_lock:
            if doc_id in embedding_service.vectors_cache:
                vectors = embedding_service.vectors_cache[doc_id]
                print(f"✓ Embeddings found in cache")
                print(f"  - Number of vectors: {len(vectors)}")
                if vectors:
                    print(f"  - Vector dimension: {len(vectors[0]['embedding'])}")
                    print(f"  - Sample vector preview: {vectors[0]['embedding'][:5]}...")
            else:
                print(f"✗ WARNING: Embeddings NOT found in cache for doc_id: {doc_id}")
                # Try loading from disk
                loaded_vectors = embedding_service._load_vectors_optimized(doc_id)
                if loaded_vectors:
                    print(f"✓ Loaded {len(loaded_vectors)} vectors from disk")
                else:
                    print(f"✗ CRITICAL: No vectors found in cache or disk!")
                    return
    except Exception as e:
        print(f"✗ FAILED to verify embeddings: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Test search/retrieval
    print(f"\n[STEP 4] Testing search and retrieval...")
    for i, question in enumerate(test_questions, 1):
        print(f"\n  Question {i}: {question}")
        try:
            # Search for relevant chunks
            search_results = embedding_service.hybrid_search(
                query=question,
                doc_id=doc_id,
                top_k=5
            )
            
            print(f"    Search results: {len(search_results)} chunks found")
            
            if search_results:
                for j, result in enumerate(search_results, 1):
                    print(f"      [{j}] Score: {result.get('score', 0):.3f} | Text: {result['text'][:80]}...")
            else:
                print(f"    ✗ WARNING: NO search results found for this question!")
                print(f"       This means embeddings might not be working correctly")
                
                # Debug: Try to manually check embeddings
                print(f"\n    DEBUG: Generating query embedding...")
                query_embeddings = embedding_service.get_embeddings([question])
                if query_embeddings and query_embeddings[0]:
                    print(f"      Query embedding: {len(query_embeddings[0])} dimensions")
                    print(f"      Query embedding preview: {query_embeddings[0][:5]}")
                else:
                    print(f"      ✗ FAILED to generate query embedding!")
                    
        except Exception as e:
            print(f"    ✗ Search FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    # Step 5: Test LLM response generation
    print(f"\n[STEP 5] Testing LLM response generation...")
    for i, question in enumerate(test_questions, 1):
        print(f"\n  Question {i}: {question}")
        try:
            # Get context chunks
            search_results = embedding_service.hybrid_search(
                query=question,
                doc_id=doc_id,
                top_k=5
            )
            context_chunks = [result['text'] for result in search_results]
            
            print(f"    Context: {len(context_chunks)} chunks")
            
            # Generate answer
            answer = llm_service.generate_answer(question, context_chunks)
            
            print(f"    Answer length: {len(answer)} characters")
            print(f"    Answer: {answer}")
            
            # Check if answer is a fallback
            if "document doesn't contain" in answer.lower() or "no information" in answer.lower():
                print(f"    ⚠ WARNING: LLM returned a 'no information' response")
            else:
                print(f"    ✓ LLM generated a proper answer")
                
        except Exception as e:
            print(f"    ✗ LLM generation FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    # Step 6: Summary
    print("\n" + "="*80)
    print("DIAGNOSTIC SUMMARY")
    print("="*80)
    print("Check the output above to identify issues:")
    print("  1. Are chunks being created properly?")
    print("  2. Are embeddings being stored?")
    print("  3. Are search results being returned?")
    print("  4. Is the LLM generating proper answers?")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
