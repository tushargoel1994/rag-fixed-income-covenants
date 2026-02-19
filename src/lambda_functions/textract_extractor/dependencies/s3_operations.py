"""S3 operations for storing extracted text output."""

import boto3

from dependencies.constants import EXTRACTED_TEXT_PREFIX, OUTPUT_BUCKET


def save_extracted_text(job_id: str, text: str) -> str:
    """Save extracted text to S3 and return the S3 key."""
    key = f"{EXTRACTED_TEXT_PREFIX}{job_id}.txt"
    boto3.client("s3").put_object(
        Bucket=OUTPUT_BUCKET,
        Key=key,
        Body=text.encode("utf-8"),
        ContentType="text/plain",
    )
    return key
