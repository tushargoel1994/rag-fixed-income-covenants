"""S3 operations for reading and writing files."""

import json
from typing import Any, Dict
import boto3
from botocore.exceptions import ClientError


class S3Client:
    """Handle S3 read and write operations."""

    def __init__(self) -> None:
        """Initialize S3 client."""
        self.s3_client = boto3.client("s3")

    def read_file(self, bucket: str, key: str) -> bytes:
        """Read file content from S3."""
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            raise Exception(f"Failed to read s3://{bucket}/{key}: {str(e)}")

    def write_embeddings(
        self, bucket: str, key: str, embeddings: Dict[str, Any]
    ) -> None:
        """Write embeddings to S3 as JSON."""
        try:
            content = json.dumps(embeddings, indent=2)
            self.s3_client.put_object(
                Bucket=bucket, Key=key, Body=content.encode("utf-8")
            )
        except ClientError as e:
            raise Exception(f"Failed to write s3://{bucket}/{key}: {str(e)}")

    def check_file_exists(self, bucket: str, key: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False
