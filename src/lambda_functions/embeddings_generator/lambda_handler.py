"""
AWS Lambda Handler for RAG System
Optimized for serverless deployment with cold start mitigation
"""

import json
import os
import boto3
from typing import Dict, Any
from rag_system import RAGSystem

# Global variables for Lambda container reuse
rag_system = None
s3_client = boto3.client('s3')

# Environment variables
BUCKET_NAME = os.getenv('DOCUMENT_BUCKET', 'my-rag-documents-bucket')
INDEX_KEY = os.getenv('INDEX_KEY', 'vector_store/faiss_index.bin')
DOCS_KEY = os.getenv('DOCS_KEY', 'vector_store/documents.json')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-2')


def initialize_rag_system():
    """Initialize RAG system with warm start optimization"""
    global rag_system
    
    if rag_system is None:
        print("Cold start: Initializing RAG system...")
        
        # Initialize RAG system
        rag_system = RAGSystem(
            embedding_model_name='all-MiniLM-L6-v2',
            bedrock_model_id=BEDROCK_MODEL_ID,
            aws_region=AWS_REGION
        )
        
        # Download vector store from S3
        try:
            local_index_path = '/tmp/faiss_index.bin'
            local_docs_path = '/tmp/documents.json'
            
            print(f"Downloading vector store from s3://{BUCKET_NAME}/{INDEX_KEY}")
            s3_client.download_file(BUCKET_NAME, INDEX_KEY, local_index_path)
            s3_client.download_file(BUCKET_NAME, DOCS_KEY, local_docs_path)
            
            # Load vector store
            rag_system.load(local_index_path, local_docs_path)
            print("Vector store loaded successfully")
            
        except Exception as e:
            print(f"Warning: Could not load vector store from S3: {str(e)}")
            print("RAG system initialized without pre-existing index")
    
    else:
        print("Warm start: Reusing existing RAG system")
    
    return rag_system


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for RAG inference
    
    Expected event structure:
    {
        "action": "query" | "ingest" | "health",
        "query": "user question" (for query action),
        "documents": ["s3://bucket/key1", "s3://bucket/key2"] (for ingest action),
        "k": 5 (optional, number of documents to retrieve)
    }
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse input
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        action = body.get('action', 'query')
        
        # Initialize RAG system
        rag = initialize_rag_system()
        
        # Handle different actions
        if action == 'health':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'healthy',
                    'message': 'RAG system is operational',
                    'document_count': len(rag.vector_store.documents)
                })
            }
        
        elif action == 'query':
            query = body.get('query')
            k = body.get('k', 5)
            
            if not query:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Missing required field: query'})
                }
            
            print(f"Processing query: {query}")
            result = rag.generate_response(query, k)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'query': result['query'],
                    'response': result['response'],
                    'sources': [
                        {
                            'content': doc['content'][:200] + '...',
                            'source': doc['metadata'].get('source', 'Unknown'),
                            'score': doc['similarity_score']
                        }
                        for doc in result['retrieved_documents']
                    ]
                })
            }
        
        elif action == 'ingest':
            documents = body.get('documents', [])
            
            if not documents:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Missing required field: documents'})
                }
            
            # Download documents from S3 and ingest
            local_files = []
            for s3_uri in documents:
                # Parse s3://bucket/key format
                if not s3_uri.startswith('s3://'):
                    continue
                
                parts = s3_uri[5:].split('/', 1)
                bucket = parts[0]
                key = parts[1]
                
                local_path = f"/tmp/{os.path.basename(key)}"
                s3_client.download_file(bucket, key, local_path)
                local_files.append(local_path)
            
            print(f"Ingesting {len(local_files)} documents")
            rag.ingest_documents(local_files)
            
            # Save updated vector store to S3
            local_index_path = '/tmp/faiss_index.bin'
            local_docs_path = '/tmp/documents.json'
            
            rag.save(local_index_path, local_docs_path)
            
            s3_client.upload_file(local_index_path, BUCKET_NAME, INDEX_KEY)
            s3_client.upload_file(local_docs_path, BUCKET_NAME, DOCS_KEY)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'success',
                    'message': f'Ingested {len(local_files)} documents',
                    'total_chunks': len(rag.vector_store.documents)
                })
            }
        
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f'Unknown action: {action}'})
            }
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__
            })
        }


# Local testing
if __name__ == "__main__":
    # Test health check
    health_event = {
        'action': 'health'
    }
    print("Testing health check...")
    response = lambda_handler(health_event, None)
    print(json.dumps(response, indent=2))
    
    # Test query
    query_event = {
        'action': 'query',
        'query': 'What is machine learning?',
        'k': 3
    }
    print("\nTesting query...")
    response = lambda_handler(query_event, None)
    print(json.dumps(response, indent=2))
