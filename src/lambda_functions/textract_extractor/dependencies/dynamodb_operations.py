"""DynamoDB operations for tracking Textract jobs."""

from datetime import datetime
from typing import Dict, Optional
import boto3

from dependencies.constants import DYNAMODB_TABLE_NAME, JOB_STATUS_SUBMITTED


def save_job(
    job_id: str, bucket: str, key: str, callback_queue_url: Optional[str]
) -> None:
    """Persist a new Textract job record."""
    table = boto3.resource("dynamodb").Table(DYNAMODB_TABLE_NAME)
    created_at = datetime.now().isoformat()
    item: Dict = {
        "job_id": job_id,
        "bucket": bucket,
        "key": key,
        "status": JOB_STATUS_SUBMITTED,
        "created_at": created_at,
    }
    if callback_queue_url:
        item["callback_queue_url"] = callback_queue_url
    table.put_item(Item=item)


def get_job(job_id: str) -> Dict:
    """Retrieve a Textract job record by job_id."""
    table = boto3.resource("dynamodb").Table(DYNAMODB_TABLE_NAME)
    response = table.get_item(Key={"job_id": job_id})
    return response.get("Item", {})


def update_job_result(job_id: str, output_s3_key: Optional[str], status: str) -> None:
    """Update job status and output S3 key on completion or failure."""
    table = boto3.resource("dynamodb").Table(DYNAMODB_TABLE_NAME)
    update_expr = "SET #s = :status"
    expr_names = {"#s": "status"}
    expr_values = {":status": status}

    if output_s3_key is not None:
        update_expr += ", output_s3_key = :s3key"
        expr_values[":s3key"] = output_s3_key

    table.update_item(
        Key={"job_id": job_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
    )
