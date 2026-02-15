
import numpy as np
from pathlib import Path
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .document import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)



class DocumentProcessor:
    """Handles document loading and chunking"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load and chunk a document based on file type"""
        file_path = Path(file_path)
        
        # Select appropriate loader
        if file_path.suffix == '.pdf':
            loader = PyPDFLoader(str(file_path))
        elif file_path.suffix == '.txt':
            loader = TextLoader(str(file_path))
        elif file_path.suffix == '.md':
            loader = UnstructuredMarkdownLoader(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Load and split
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        
        # Convert to our Document format
        return [
            Document(
                content=chunk.page_content,
                metadata={
                    **chunk.metadata,
                    'source': str(file_path),
                    'chunk_index': idx
                }
            )
            for idx, chunk in enumerate(chunks)
        ]
