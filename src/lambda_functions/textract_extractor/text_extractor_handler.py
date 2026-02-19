"""
textract_extractor Lambda handler.

Two invocation modes:
  1. Direct invoke  : {bucket, key, callback_queue_url?} → starts Textract job, returns job_id
  2. SQS trigger    : Textract SNS notification → fetches result, stores in DynamoDB,
                      sends to callback_queue_url if provided
"""

import json
from typing import Any, Dict, Optional

from .dependencies import dynamodb_operations, s3_operations, sqs_operations

from .dependencies import textract_operations
from .dependencies.constants import JOB_STATUS_COMPLETED, JOB_STATUS_FAILED


def handler(event: Dict, context: Any) -> Optional[Dict]:
    """Route event to start-extraction or result-processing."""
    if "Records" in event:
        _handle_sqs_event(event)
        return None
    return _handle_start_extraction(event)


def _handle_start_extraction(event: Dict) -> Dict:
    """Start a Textract job and persist metadata."""
    bucket: str = event["bucket"]
    key: str = event["key"]
    callback_queue_url: Optional[str] = event.get("callback_queue_url")

    job_id = textract_operations.start_extraction_job(bucket, key)
    dynamodb_operations.save_job(job_id, bucket, key, callback_queue_url)

    return {"job_id": job_id, "status": "SUBMITTED"}


def _handle_sqs_event(event: Dict) -> None:
    """Process Textract completion notifications from SQS."""
    for record in event["Records"]:
        body = json.loads(record["body"])
        message = json.loads(body["Message"])
        _process_textract_notification(message)


def _process_textract_notification(message: Dict) -> None:
    """Fetch result and notify caller on job completion."""
    job_id: str = message["JobId"]
    status: str = message["Status"]

    if status == "SUCCEEDED":
        text = textract_operations.get_extraction_result(job_id)
        output_s3_key = s3_operations.save_extracted_text(job_id, text)
        dynamodb_operations.update_job_result(job_id, output_s3_key, JOB_STATUS_COMPLETED)
        job = dynamodb_operations.get_job(job_id)
        if job.get("callback_queue_url"):
            sqs_operations.send_callback(job["callback_queue_url"], job_id, output_s3_key)
    else:
        dynamodb_operations.update_job_result(job_id, None, JOB_STATUS_FAILED)
