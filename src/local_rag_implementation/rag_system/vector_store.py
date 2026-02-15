import faiss
import numpy as np
import json
from typing import List
from .document import Document

class VectorStore:
    """FAISS-based vector storage with persistence"""
    
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.documents: List[Document] = []
    
    def add_documents(self, documents: List[Document]):
        """Add documents with embeddings to the index"""
        embeddings = np.array([doc.embedding for doc in documents]).astype('float32')
        self.index.add(embeddings)
        self.documents.extend(documents)
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[tuple[Document, float]]:
        """Search for k most similar documents"""
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(distance)))
        
        return results
    
    def save(self, index_path: str, docs_path: str):
        """Save index and documents to disk"""
        faiss.write_index(self.index, index_path)
        with open(docs_path, 'w') as f:
            json.dump([
                {
                    'content': doc.content,
                    'metadata': doc.metadata
                }
                for doc in self.documents
            ], f)
    
    def load(self, index_path: str, docs_path: str):
        """Load index and documents from disk"""
        self.index = faiss.read_index(index_path)
        with open(docs_path, 'r') as f:
            docs_data = json.load(f)
            self.documents = [
                Document(
                    content=d['content'],
                    metadata=d['metadata']
                )
                for d in docs_data
            ]