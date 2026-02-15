
# RAG Implementation - Version 1

A production-ready Retrieval-Augmented Generation (RAG) system built with Python, AWS Bedrock, and FAISS for building GenAI applications.

## 🎯 Features

- **Document Processing**: PDF, TXT, and Markdown support with intelligent chunking
- **Vector Embeddings**: Sentence Transformers for semantic search
- **Vector Storage**: FAISS for fast similarity search
- **LLM Integration**: AWS Bedrock (Claude 3 Sonnet)
- **Serverless Ready**: Lambda handler for AWS deployment
- **Production Optimized**: Cold start mitigation, S3 integration, error handling

## 🏗️ Architecture

```
┌─────────────┐
│   Documents │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Document        │
│ Processing      │
│ - Load          │
│ - Chunk         │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Embedding       │
│ Generation      │
│ (Sentence-BERT) │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Vector Store    │
│ (FAISS Index)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│ Query           │──────>│ Retrieval    │
└─────────────────┘      └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ Context +    │
                         │ Prompt       │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ LLM          │
                         │ (Bedrock)    │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ Response     │
                         └──────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- AWS Account with Bedrock access
- AWS CLI configured
- 2GB+ RAM (for embedding models)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Clone or download the repository
cd rag-implementation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure AWS

```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

### 3. Enable Bedrock Model Access

1. Go to AWS Console → Amazon Bedrock
2. Click "Model access" in the left sidebar
3. Click "Enable specific models"
4. Select "Claude 3 Sonnet"
5. Submit request (usually instant approval)

### 4. Run Example

```bash
python example_usage.py
```

This will:
- Create sample documents about ML, AWS, and RAG
- Generate embeddings and build vector index
- Demonstrate retrieval capabilities
- Show example RAG responses

## 💻 Basic Usage

### Initialize RAG System

```python
from rag_system import RAGSystem

# Initialize
rag = RAGSystem(
    embedding_model_name='all-MiniLM-L6-v2',
    bedrock_model_id='anthropic.claude-3-sonnet-20240229-v1:0',
    aws_region='us-east-1'
)
```

### Ingest Documents

```python
# Ingest documents from files
rag.ingest_documents([
    'path/to/document1.pdf',
    'path/to/document2.txt',
    'path/to/document3.md'
])

# Save vector store
rag.save('faiss_index.bin', 'documents.json')
```

### Query the System

```python
# Generate RAG response
result = rag.generate_response(
    query="What is machine learning?",
    k=5  # Number of documents to retrieve
)

print(result['response'])

# Access retrieved documents
for doc in result['retrieved_documents']:
    print(f"Source: {doc['metadata']['source']}")
    print(f"Score: {doc['similarity_score']}")
    print(f"Content: {doc['content'][:200]}...\n")
```

### Retrieval Only

```python
# Just retrieve relevant documents without LLM
results = rag.retrieve("What is deep learning?", k=3)

for doc, score in results:
    print(f"Similarity: {score:.4f}")
    print(f"Content: {doc.content[:200]}...\n")
```

## 🔧 Configuration Options

### Embedding Models

Choose based on your requirements:

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| all-MiniLM-L6-v2 | 80MB | ⚡⚡⚡ | ⭐⭐ | General purpose, fast |
| all-mpnet-base-v2 | 420MB | ⚡⚡ | ⭐⭐⭐ | Better quality |
| instructor-large | 1.3GB | ⚡ | ⭐⭐⭐⭐ | Best quality, slower |

```python
rag = RAGSystem(embedding_model_name='all-mpnet-base-v2')
```

### Document Chunking

Adjust based on document type:

```python
from rag_system import DocumentProcessor

processor = DocumentProcessor(
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=200     # Overlap between chunks
)

# Technical documentation
processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)

# Narrative content
processor = DocumentProcessor(chunk_size=1500, chunk_overlap=300)
```

### Retrieval Parameters

```python
# Retrieve more documents for comprehensive answers
result = rag.generate_response(query, k=10)

# Fewer documents for focused answers
result = rag.generate_response(query, k=3)
```

## ☁️ AWS Deployment

### Lambda Deployment

1. **Create S3 bucket for documents:**
```bash
aws s3 mb s3://my-rag-documents-bucket
```

2. **Upload vector store:**
```bash
aws s3 cp faiss_index.bin s3://my-rag-documents-bucket/vector_store/
aws s3 cp documents.json s3://my-rag-documents-bucket/vector_store/
```

3. **Create Lambda layer for dependencies:**
```bash
mkdir python
pip install -r requirements.txt -t python/
zip -r rag-layer.zip python/
aws lambda publish-layer-version \
    --layer-name rag-dependencies \
    --zip-file fileb://rag-layer.zip \
    --compatible-runtimes python3.9
```

4. **Deploy Lambda function:**
```bash
zip -r function.zip lambda_handler.py rag_system.py
aws lambda create-function \
    --function-name rag-inference \
    --runtime python3.9 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
    --handler lambda_handler.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 900 \
    --memory-size 3008 \
    --environment Variables={DOCUMENT_BUCKET=my-rag-documents-bucket}
```

5. **Test Lambda function:**
```bash
aws lambda invoke \
    --function-name rag-inference \
    --payload '{"action":"query","query":"What is RAG?","k":3}' \
    response.json
cat response.json
```

See [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md) for detailed deployment guide.

## 📊 Performance Optimization

### 1. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_retrieve(query: str):
    return rag.retrieve(query, k=5)
```

### 2. Batch Processing

```python
# Process multiple queries efficiently
queries = ["query1", "query2", "query3"]
embeddings = rag.embedding_model.embed_batch(queries)
```

### 3. Async Processing

```python
import asyncio

async def process_query(query):
    return rag.generate_response(query)

# Process multiple queries concurrently
results = await asyncio.gather(*[
    process_query(q) for q in queries
])
```

## 🧪 Testing

Run tests:
```bash
python -m pytest tests/
```

Run example with different configurations:
```bash
# Use different embedding model
python example_usage.py --embedding-model all-mpnet-base-v2

# Use different number of chunks
python example_usage.py --chunk-size 500 --chunk-overlap 100
```

## 📈 Monitoring

### CloudWatch Metrics

The Lambda handler automatically logs:
- Invocation count
- Duration
- Errors
- Document count
- Query performance

### Custom Metrics

```python
import time

start = time.time()
result = rag.generate_response(query)
latency = time.time() - start

print(f"Query latency: {latency:.2f}s")
print(f"Retrieved documents: {len(result['retrieved_documents'])}")
```

## 🔒 Security Best Practices

1. **Use IAM Roles**: Don't hardcode AWS credentials
2. **Enable S3 Encryption**: Encrypt documents at rest
3. **VPC Deployment**: Deploy Lambda in VPC for private resources
4. **API Gateway Auth**: Add authentication (API keys, Cognito)
5. **Secrets Manager**: Store sensitive configuration

## 🐛 Troubleshooting

### Common Issues

**Issue: "Bedrock Access Denied"**
```
Solution: Enable model access in AWS Bedrock console
Verify IAM permissions include bedrock:InvokeModel
```

**Issue: "Lambda timeout"**
```
Solution: Increase Lambda timeout (max 15 minutes)
Use smaller embedding model
Pre-warm Lambda with scheduled events
```

**Issue: "Out of memory"**
```
Solution: Increase Lambda memory allocation
Use FAISS quantization for large indices
Consider external vector database (Pinecone, Weaviate)
```

## 🛣️ Roadmap

- [ ] Add evaluation metrics (RAGAS)
- [ ] Implement query caching with Redis
- [ ] Multi-modal RAG (images, tables)
- [ ] Add reranking capabilities
- [ ] Hybrid search (keyword + semantic)
- [ ] Agentic AI features (tool calling, planning)
- [ ] Streaming responses
- [ ] Support for more LLM providers

## 📚 Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [LangChain Documentation](https://python.langchain.com/)
- [FAISS Documentation](https://faiss.ai/)
- [Sentence Transformers](https://www.sbert.net/)
- [RAG Best Practices](https://www.anthropic.com/research/retrieval-augmented-generation)

## 📝 License

MIT License - feel free to use for personal or commercial projects

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## ⭐ Next Steps

1. Try the example script: `python example_usage.py`
2. Add your own documents
3. Experiment with different models and parameters
4. Deploy to AWS Lambda for production use
5. Explore agentic AI patterns for advanced use cases

---

**Built with ❤️ for GenAI and Agentic AI development**
