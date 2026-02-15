"""
RAG (Retrieval-Augmented Generation) System - Version 1
A production-ready implementation using AWS services and modern embedding models
"""

from typing import List, Dict, Any
from dotenv import load_dotenv

from .document import Document
from .bedrock_llm import BedrockLLM
from .document_processor import DocumentProcessor
from .embedding_model import EmbeddingModel
from .vector_store import VectorStore

load_dotenv()

class RAGSystem:
    """Complete RAG system orchestrating all components"""
    
    def __init__(
        self,
        embedding_model_name: str = 'all-MiniLM-L6-v2',
        bedrock_model_id: str = 'amazon.nova-2-lite-v1:0',
        aws_region: str = 'us-east-2'
    ):
        self.embedding_model = EmbeddingModel(embedding_model_name)
        self.vector_store = VectorStore(self.embedding_model.embedding_dim)
        self.document_processor = DocumentProcessor()
        self.llm = BedrockLLM(bedrock_model_id, aws_region)
    
    def ingest_documents(self, file_paths: List[str]):
        """Ingest multiple documents into the RAG system"""
        all_documents = []
        
        for file_path in file_paths:
            print(f"Processing {file_path}...")
            documents = self.document_processor.load_document(file_path)
            
            # Generate embeddings
            texts = [doc.content for doc in documents]
            embeddings = self.embedding_model.embed_batch(texts)
            
            for doc, embedding in zip(documents, embeddings):
                doc.embedding = embedding
            
            all_documents.extend(documents)
        
        # Add to vector store
        self.vector_store.add_documents(all_documents)
        print(f"Ingested {len(all_documents)} document chunks")
    

    def retrieve(self, query: str, k: int = 5) -> List[tuple[Document, float]]:
        """Retrieve relevant documents for a query"""
        query_embedding = self.embedding_model.embed_text(query)
        return self.vector_store.search(query_embedding, k)

    
    def generate_response(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Generate RAG response with retrieved context"""
        
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(query, k)
        
        # Build context from retrieved documents
        context_parts = []
        for idx, (doc, score) in enumerate(retrieved_docs, 1):
            context_parts.append(f"[Document {idx}]")
            context_parts.append(doc.content)
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        # Build prompt
        prompt = f"""You are a helpful assistant answering questions based on the provided context. Context: {context}. Question: {query}. Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to fully answer the question, acknowledge this limitation. Answer:"""
        
        # Generate response
        response = self.llm.generate(prompt)
        
        return {
            'query': query,
            'response': response,
            'retrieved_documents': [
                {
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'similarity_score': score
                }
                for doc, score in retrieved_docs
            ]
        }
    

    def save(self, index_path: str = 'faiss_index.bin', docs_path: str = 'documents.json'):
        """Save the vector store to disk"""
        self.vector_store.save(index_path, docs_path)
        print(f"Saved vector store to {index_path} and {docs_path}")
    
    
    def load(self, index_path: str = 'faiss_index.bin', docs_path: str = 'documents.json'):
        """Load the vector store from disk"""
        self.vector_store.load(index_path, docs_path)
        print(f"Loaded vector store from {index_path} and {docs_path}")


# Example usage
# if __name__ == "__main__":
    # Initialize RAG system
    # rag = RAGSystem()
    
    # print("RAG System initialized successfully!")
    # print("\nTo use:")
    # print("1. rag.ingest_documents(['file1.pdf', 'file2.txt'])")
    # print("2. result = rag.generate_response('your question here')")
    # print("3. print(result['response'])")
