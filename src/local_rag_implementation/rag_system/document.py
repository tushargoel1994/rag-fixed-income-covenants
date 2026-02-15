
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Document:
    """Represents a document chunk with metadata"""
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None