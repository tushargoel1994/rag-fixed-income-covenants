"""Text chunking utilities for processing large documents."""

from typing import List

from .constants import CHUNK_SIZE, CHUNK_OVERLAP


class TextChunker:
    """Chunk text into smaller pieces for embedding generation."""

    def __init__(
        self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
    ) -> None:
        """Initialize text chunker."""
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk.strip())

            start = end - self.overlap

        return chunks
