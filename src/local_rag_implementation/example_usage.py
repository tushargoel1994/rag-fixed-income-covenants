"""
Example RAG Usage Script
Demonstrates how to use the RAG system with sample documents
"""

from rag_system import RAGSystem
import os
from pathlib import Path


def get_sample_documents():
    """Create sample documents for testing"""
    sample_dir = Path('data')
    print (sample_dir)
    sample_dir.mkdir(exist_ok=True)
    
    return [
        str(sample_dir / 'ml_concepts.txt'),
        # str(sample_dir / 'aws_services.txt'),
        # str(sample_dir / 'rag_agentic_ai.txt')
    ]


def example_usage_task():
    """Main execution function"""
    print("=" * 70)
    print("RAG System Example - Version 1")
    print("=" * 70)
    
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    print (f'Access Key: {access_key}')
    
    # Check for AWS credentials
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        print("⚠️  AWS credentials not found in environment variables")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to use Bedrock")
        print("   For this demo, we'll proceed with document ingestion only\n")
    
    # Get sample documents
    print("Get sample documents...")
    file_paths = get_sample_documents()
    print(f"Get {len(file_paths)} sample documents\n")
    
    # Initialize RAG system
    print("🚀 Initializing RAG system...")
    rag = RAGSystem(
        embedding_model_name='all-MiniLM-L6-v2',
        bedrock_model_id='amazon.nova-2-lite-v1:0',
        aws_region='us-east-2'
    )
    print("RAG system initialized \n")
    
    # Ingest documents
    print("📚 Ingesting documents into vector store...")
    rag.ingest_documents(file_paths)
    print()
    
    # Save the index
    print("💾 Saving vector store...")
    rag.save('faiss_index.bin', 'documents.json')
    print()
    
    # Example queries
    queries = [
        "What is RAG and how does it work?",
        "What AWS services are available for machine learning?",
        "Explain the difference between supervised and unsupervised learning",
        "What are the key characteristics of Agentic AI?"
    ]
    
    print("🔍 Testing retrieval (top 3 documents per query):\n\n")
    
    for query in queries:
        print(f"Query: {query}")
        results = rag.retrieve(query, k=3)
        
        for idx, (doc, score) in enumerate(results, 1):
            print(f"[{idx}] Similarity Score: {score:.4f}")
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Preview: {doc.content[:150]}...")
            print ('\n')
        
        print("\n" + "-" * 70 + "\n")
    
    # Try generating a response if AWS credentials are available
    if os.getenv('AWS_ACCESS_KEY_ID'):
        print("🤖 Generating RAG response with Bedrock...\n")
        test_query = "What is RAG and why is it useful for AI applications?"
        result = rag.generate_response(test_query, k=3)
        
        print(f"Query: {test_query}\n\n")
        print(f"Response:{result['response']}\n\n")
        print(f"Retrieved {len(result['retrieved_documents'])} documents\n")
    
    print("\n" + "=" * 70)
    print("✅ RAG System Demo Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Add your own documents to ingest")
    print("2. Experiment with different embedding models")
    print("3. Tune chunk sizes and retrieval parameters")
    print("4. Deploy to AWS Lambda for serverless RAG")
    print("5. Add ChromaDB or Pinecone for production vector storage")

if __name__ == "__main__":
    example_usage_task()
    # create_sample_documents()
