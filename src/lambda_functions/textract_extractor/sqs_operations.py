"""SQS callback operations for notifying callers of completed extraction."""

import json
import boto3


def send_callback(queue_url: str, job_id: str, output_s3_key: str) -> None:
    """Send extraction result S3 key to the caller's SQS callback queue."""
    sqs = boto3.client("sqs")
    message = {
        "job_id": job_id,
        "output_s3_key": output_s3_key,
        "status": "COMPLETED",
    }
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
