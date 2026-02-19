# Embeddings Generator Lambda

Generates vector embeddings for documents stored in S3 using AWS Bedrock.

## Functionality

Reads files from S3, extracts text (using Textract for PDFs), chunks the text,
generates embeddings using AWS Bedrock, and saves results back to S3.

## Supported Files

- PDF files (extracted via Amazon Textract)
- Text files (.txt, .md, .json, .csv)

## Configuration

- **Runtime**: Python 3.11
- **Memory**: 256 MB
- **Timeout**: 60 seconds
- **Default Model**: amazon.titan-embed-text-v2:0

## Event Structure

```json
{
  "bucket": "my-bucket",
  "key": "documents/file.pdf",
  "model_id": "amazon.titan-embed-text-v2:0"
}
```

## Output

Embeddings saved to: `s3://bucket/embeddings/{filename}_embeddings.json`

## Required IAM Permissions

- s3:GetObject
- s3:PutObject
- textract:StartDocumentTextDetection
- textract:GetDocumentTextDetection
- bedrock:InvokeModel

## Architecture

- `handler.py`: Lambda entry point
- `processor.py`: Main processing logic
- `s3_operations.py`: S3 read/write
- `textract_operations.py`: PDF text extraction
- `bedrock_operations.py`: Embedding generation
- `text_chunker.py`: Text chunking utilities
- `constants.py`: Configuration constants

## Testing

Run tests: `python -m pytest test_handler.py -v`
