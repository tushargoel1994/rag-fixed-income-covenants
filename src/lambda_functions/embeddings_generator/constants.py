"""Configuration constants for embeddings generator Lambda."""

# Bedrock Model Configuration
DEFAULT_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
EMBEDDING_DIMENSION = 1024
MAX_INPUT_TOKENS = 8192

# S3 Configuration
EMBEDDINGS_OUTPUT_FOLDER = "embeddings"
BATCH_SIZE = 25

# File Processing
SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".json", ".csv"}
PDF_EXTENSION = ".pdf"
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 50

# Textract Configuration
TEXTRACT_MAX_PAGES = 1000

# Lambda Configuration
PROCESSING_TIMEOUT_BUFFER = 5
