"""Textract API operations."""

from typing import List, Dict
import boto3

from .constants import TEXTRACT_SNS_TOPIC_ARN, TEXTRACT_ROLE_ARN, TEXTRACT_MAX_RESULTS


def start_extraction_job(bucket: str, key: str) -> str:
    """Start an async Textract text detection job and return job_id."""
    client = boto3.client("textract")
    response = client.start_document_text_detection(
        DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}},
        NotificationChannel={
            "SNSTopicArn": TEXTRACT_SNS_TOPIC_ARN,
            "RoleArn": TEXTRACT_ROLE_ARN,
        },
    )
    return response["JobId"]


def get_extraction_result(job_id: str) -> str:
    """Fetch completed Textract job result with pagination."""
    client = boto3.client("textract")
    all_blocks: List[Dict] = []
    next_token = None

    while True:
        kwargs: Dict = {"JobId": job_id, "MaxResults": TEXTRACT_MAX_RESULTS}
        if next_token:
            kwargs["NextToken"] = next_token
        response = client.get_document_text_detection(**kwargs)
        all_blocks.extend(response.get("Blocks", []))
        next_token = response.get("NextToken")
        if not next_token:
            break

    return _parse_blocks(all_blocks)


def _parse_blocks(blocks: List[Dict]) -> str:
    """Extract LINE text from Textract blocks."""
    lines = [b["Text"] for b in blocks if b["BlockType"] == "LINE"]
    return "\n".join(lines)
