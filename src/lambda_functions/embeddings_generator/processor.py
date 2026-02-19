"""Main processing logic for embeddings generation."""

import os
from typing import Any, Dict, List

from .constants import (
    EMBEDDINGS_OUTPUT_FOLDER,
    PDF_EXTENSION,
    SUPPORTED_TEXT_EXTENSIONS,
)
from .s3_operations import S3Client
from .textract_operations import TextractClient
from .bedrock_operations import BedrockClient
from .text_chunker import TextChunker


class EmbeddingProcessor:
    """Process files and generate embeddings."""

    def __init__(self, model_id: str = None) -> None:
        """Initialize processor with required clients."""
        self.s3_client = S3Client()
        self.textract_client = TextractClient()
        self.bedrock_client = BedrockClient(model_id) if model_id else BedrockClient()
        self.text_chunker = TextChunker()

    def process_file(self, bucket: str, key: str) -> Dict[str, Any]:
        """Process a single file and generate embeddings."""
        file_extension = os.path.splitext(key)[1].lower()

        if file_extension == PDF_EXTENSION:
            text = self.textract_client.extract_text_from_pdf(bucket, key)
        elif file_extension in SUPPORTED_TEXT_EXTENSIONS:
            content = self.s3_client.read_file(bucket, key)
            text = content.decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        chunks = self.text_chunker.chunk_text(text)
        embeddings = self._generate_chunk_embeddings(chunks)

        return self._create_embedding_document(key, chunks, embeddings)

    def _generate_chunk_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for all chunks."""
        return self.bedrock_client.generate_embeddings_batch(chunks)

    def _create_embedding_document(
        self, source_key: str, chunks: List[str], embeddings: List[List[float]]
    ) -> Dict[str, Any]:
        """Create structured embedding document."""
        return {
            "source_file": source_key,
            "model": self.bedrock_client.model_id,
            "chunk_count": len(chunks),
            "embeddings": [
                {"chunk_index": i, "text": chunks[i], "embedding": embeddings[i]}
                for i in range(len(chunks))
            ],
        }

    def save_embeddings(
        self, bucket: str, source_key: str, embedding_doc: Dict[str, Any]
    ) -> str:
        """Save embeddings to S3."""
        file_name = os.path.splitext(os.path.basename(source_key))[0]
        output_key = f"{EMBEDDINGS_OUTPUT_FOLDER}/{file_name}_embeddings.json"

        self.s3_client.write_embeddings(bucket, output_key, embedding_doc)
        return output_key
