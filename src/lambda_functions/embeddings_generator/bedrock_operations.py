"""AWS Bedrock operations for generating embeddings."""

import json
from typing import List
import boto3
from botocore.exceptions import ClientError

from .constants import DEFAULT_EMBEDDING_MODEL_ID


class BedrockClient:
    """Handle embedding generation using AWS Bedrock."""

    def __init__(self, model_id: str = DEFAULT_EMBEDDING_MODEL_ID) -> None:
        """Initialize Bedrock runtime client."""
        self.bedrock_runtime = boto3.client("bedrock-runtime")
        self.model_id = model_id

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for given text."""
        try:
            body = json.dumps({"inputText": text})
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id, body=body
            )

            response_body = json.loads(response["body"].read())
            return response_body["embedding"]
        except ClientError as e:
            raise Exception(f"Bedrock embedding generation failed: {str(e)}")

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return [self.generate_embedding(text) for text in texts]

    def set_model(self, model_id: str) -> None:
        """Change the embedding model."""
        self.model_id = model_id
