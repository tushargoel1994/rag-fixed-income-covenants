"""Lambda handler for embeddings generation."""

import json
import traceback
from typing import Any, Dict

from .processor import EmbeddingProcessor
from .constants import DEFAULT_EMBEDDING_MODEL_ID


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process S3 files and generate embeddings using AWS Bedrock.

    Expected event structure:
    {
        "bucket": "bucket-name",
        "key": "path/to/file.pdf",
        "model_id": "amazon.titan-embed-text-v2:0"  # Optional
    }
    """
    try:
        bucket = event["bucket"]
        key = event["key"]
        model_id = event.get("model_id", DEFAULT_EMBEDDING_MODEL_ID)

        processor = EmbeddingProcessor(model_id)
        embedding_doc = processor.process_file(bucket, key)
        output_key = processor.save_embeddings(bucket, key, embedding_doc)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Embeddings generated successfully",
                    "source_file": key,
                    "output_file": output_key,
                    "chunk_count": embedding_doc["chunk_count"],
                }
            ),
        }

    except Exception as e:
        error_message = f"Error processing file: {str(e)}"
        print(f"{error_message}\n{traceback.format_exc()}")

        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message}),
        }
