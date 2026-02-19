"""Unit tests for textract_extractor Lambda."""

import json
from unittest.mock import MagicMock, patch

from .. import text_extractor_handler
from ..dependencies import dynamodb_operations, s3_operations, sqs_operations, textract_operations

# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_sqs_event(job_id: str, status: str) -> dict:
    message = json.dumps({"JobId": job_id, "Status": status})
    body = json.dumps({"Message": message})
    return {"Records": [{"body": body}]}


SAMPLE_BLOCKS = [
    {"BlockType": "LINE", "Text": "Covenant A"},
    {"BlockType": "WORD", "Text": "ignored"},
    {"BlockType": "LINE", "Text": "Covenant B"},
]


# ── Handler: direct invoke ────────────────────────────────────────────────────

@patch.object(text_extractor_handler, 'dynamodb_operations')
@patch.object(text_extractor_handler, 'textract_operations')
def test_handler_direct_invoke_returns_job_id(mock_textract, mock_dynamo) -> None:
    """Direct invoke returns job_id and SUBMITTED status."""
    mock_textract.start_extraction_job.return_value = "job-abc"
    event = {"bucket": "my-bucket", "key": "docs/file.pdf", "callback_queue_url": "https://sqs/queue"}

    result = text_extractor_handler.handler(event, None)

    assert result == {"job_id": "job-abc", "status": "SUBMITTED"}
    mock_textract.start_extraction_job.assert_called_once_with("my-bucket", "docs/file.pdf")
    mock_dynamo.save_job.assert_called_once_with("job-abc", "my-bucket", "docs/file.pdf", "https://sqs/queue")


@patch.object(text_extractor_handler, 'dynamodb_operations')
@patch.object(text_extractor_handler, 'textract_operations')
def test_handler_direct_invoke_without_callback(mock_textract, mock_dynamo) -> None:
    """Direct invoke without callback_queue_url passes None to save_job."""
    mock_textract.start_extraction_job.return_value = "job-xyz"
    event = {"bucket": "my-bucket", "key": "docs/file.pdf"}

    result = text_extractor_handler.handler(event, None)

    assert result["job_id"] == "job-xyz"
    mock_dynamo.save_job.assert_called_once_with("job-xyz", "my-bucket", "docs/file.pdf", None)


# ── Handler: SQS trigger ──────────────────────────────────────────────────────

@patch.object(text_extractor_handler, 'sqs_operations')
@patch.object(text_extractor_handler, 's3_operations')
@patch.object(text_extractor_handler, 'dynamodb_operations')
@patch.object(text_extractor_handler, 'textract_operations')
def test_handler_sqs_succeeded_with_callback(mock_textract, mock_dynamo, mock_s3, mock_sqs) -> None:
    """SQS SUCCEEDED event saves text to S3, updates DynamoDB with S3 key, sends callback."""
    mock_textract.get_extraction_result.return_value = "Covenant A\nCovenant B"
    mock_s3.save_extracted_text.return_value = "extracted/job-1.txt"
    mock_dynamo.get_job.return_value = {"job_id": "job-1", "callback_queue_url": "https://sqs/cb"}
    event = _make_sqs_event("job-1", "SUCCEEDED")

    result = text_extractor_handler.handler(event, None)

    assert result is None
    mock_s3.save_extracted_text.assert_called_once_with("job-1", "Covenant A\nCovenant B")
    mock_dynamo.update_job_result.assert_called_once_with("job-1", "extracted/job-1.txt", "COMPLETED")
    mock_sqs.send_callback.assert_called_once_with("https://sqs/cb", "job-1", "extracted/job-1.txt")


@patch.object(text_extractor_handler, 'sqs_operations')
@patch.object(text_extractor_handler, 's3_operations')
@patch.object(text_extractor_handler, 'dynamodb_operations')
@patch.object(text_extractor_handler, 'textract_operations')
def test_handler_sqs_succeeded_without_callback(mock_textract, mock_dynamo, mock_s3, mock_sqs) -> None:
    """SQS SUCCEEDED event without callback_queue_url skips send_callback."""
    mock_textract.get_extraction_result.return_value = "Some text"
    mock_s3.save_extracted_text.return_value = "extracted/job-2.txt"
    mock_dynamo.get_job.return_value = {"job_id": "job-2"}
    event = _make_sqs_event("job-2", "SUCCEEDED")

    text_extractor_handler.handler(event, None)

    mock_s3.save_extracted_text.assert_called_once()
    mock_sqs.send_callback.assert_not_called()


@patch.object(text_extractor_handler, 'sqs_operations')
@patch.object(text_extractor_handler, 's3_operations')
@patch.object(text_extractor_handler, 'dynamodb_operations')
@patch.object(text_extractor_handler, 'textract_operations')
def test_handler_sqs_failed(mock_textract, mock_dynamo, mock_s3, mock_sqs) -> None:
    """SQS FAILED event updates DynamoDB with FAILED and no S3 key."""
    event = _make_sqs_event("job-3", "FAILED")

    text_extractor_handler.handler(event, None)

    mock_dynamo.update_job_result.assert_called_once_with("job-3", None, "FAILED")
    mock_s3.save_extracted_text.assert_not_called()
    mock_textract.get_extraction_result.assert_not_called()
    mock_sqs.send_callback.assert_not_called()


# ── Textract operations ───────────────────────────────────────────────────────

@patch.object(textract_operations, 'boto3')
def test_start_extraction_job_returns_job_id(mock_boto3) -> None:
    """start_extraction_job calls Textract with correct params and returns job_id."""
    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client
    mock_client.start_document_text_detection.return_value = {"JobId": "job-new"}

    result = textract_operations.start_extraction_job("bucket", "key/file.pdf")

    assert result == "job-new"
    mock_client.start_document_text_detection.assert_called_once()


@patch.object(textract_operations, 'boto3')
def test_get_extraction_result_single_page(mock_boto3) -> None:
    """get_extraction_result returns joined LINE text from single-page response."""
    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client
    mock_client.get_document_text_detection.return_value = {"Blocks": SAMPLE_BLOCKS}

    result = textract_operations.get_extraction_result("job-1")

    assert result == "Covenant A\nCovenant B"


@patch.object(textract_operations, 'boto3')
def test_get_extraction_result_multi_page(mock_boto3) -> None:
    """get_extraction_result paginates until NextToken is absent."""
    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client
    mock_client.get_document_text_detection.side_effect = [
        {"Blocks": [{"BlockType": "LINE", "Text": "Page 1"}], "NextToken": "token-1"},
        {"Blocks": [{"BlockType": "LINE", "Text": "Page 2"}]},
    ]

    result = textract_operations.get_extraction_result("job-2")

    assert result == "Page 1\nPage 2"
    assert mock_client.get_document_text_detection.call_count == 2


# ── S3 operations ─────────────────────────────────────────────────────────────

@patch.object(s3_operations, 'boto3')
def test_save_extracted_text_uploads_to_s3(mock_boto3) -> None:
    """save_extracted_text uploads text as UTF-8 and returns the S3 key."""
    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client

    result = s3_operations.save_extracted_text("job-1", "Covenant A\nCovenant B")

    assert result == "extracted/job-1.txt"
    mock_client.put_object.assert_called_once()
    call_kwargs = mock_client.put_object.call_args[1]
    assert call_kwargs["Key"] == "extracted/job-1.txt"
    assert call_kwargs["Body"] == b"Covenant A\nCovenant B"
    assert call_kwargs["ContentType"] == "text/plain"


# ── DynamoDB operations ───────────────────────────────────────────────────────

@patch.object(dynamodb_operations, 'boto3')
def test_save_job_with_callback(mock_boto3) -> None:
    """save_job includes callback_queue_url in DynamoDB item when provided."""
    mock_table = MagicMock()
    mock_boto3.resource.return_value.Table.return_value = mock_table

    dynamodb_operations.save_job("job-1", "bucket", "key.pdf", "https://sqs/queue")

    item = mock_table.put_item.call_args[1]["Item"]
    assert item["callback_queue_url"] == "https://sqs/queue"
    assert item["status"] == "SUBMITTED"


@patch.object(dynamodb_operations, 'boto3')
def test_save_job_without_callback(mock_boto3) -> None:
    """save_job omits callback_queue_url from DynamoDB item when None."""
    mock_table = MagicMock()
    mock_boto3.resource.return_value.Table.return_value = mock_table

    dynamodb_operations.save_job("job-2", "bucket", "key.pdf", None)

    item = mock_table.put_item.call_args[1]["Item"]
    assert "callback_queue_url" not in item


@patch.object(dynamodb_operations, 'boto3')
def test_get_job_returns_item(mock_boto3) -> None:
    """get_job returns the DynamoDB item for a known job_id."""
    mock_table = MagicMock()
    mock_boto3.resource.return_value.Table.return_value = mock_table
    mock_table.get_item.return_value = {"Item": {"job_id": "job-1", "status": "COMPLETED"}}

    result = dynamodb_operations.get_job("job-1")

    assert result["job_id"] == "job-1"


@patch.object(dynamodb_operations, 'boto3')
def test_get_job_returns_empty_when_not_found(mock_boto3) -> None:
    """get_job returns empty dict when job_id does not exist."""
    mock_table = MagicMock()
    mock_boto3.resource.return_value.Table.return_value = mock_table
    mock_table.get_item.return_value = {}

    result = dynamodb_operations.get_job("missing-job")

    assert result == {}


@patch.object(dynamodb_operations, 'boto3')
def test_update_job_result_with_s3_key(mock_boto3) -> None:
    """update_job_result stores output_s3_key in DynamoDB when provided."""
    mock_table = MagicMock()
    mock_boto3.resource.return_value.Table.return_value = mock_table

    dynamodb_operations.update_job_result("job-1", "extracted/job-1.txt", "COMPLETED")

    kwargs = mock_table.update_item.call_args[1]
    assert ":s3key" in kwargs["ExpressionAttributeValues"]
    assert kwargs["ExpressionAttributeValues"][":s3key"] == "extracted/job-1.txt"


@patch.object(dynamodb_operations, 'boto3')
def test_update_job_result_without_s3_key(mock_boto3) -> None:
    """update_job_result omits output_s3_key from update when None (FAILED case)."""
    mock_table = MagicMock()
    mock_boto3.resource.return_value.Table.return_value = mock_table

    dynamodb_operations.update_job_result("job-1", None, "FAILED")

    kwargs = mock_table.update_item.call_args[1]
    assert ":s3key" not in kwargs["ExpressionAttributeValues"]


# ── SQS operations ────────────────────────────────────────────────────────────

@patch.object(sqs_operations, 'boto3')
def test_send_callback_sends_s3_key(mock_boto3) -> None:
    """send_callback sends job_id, output_s3_key, and COMPLETED status to queue."""
    mock_sqs = MagicMock()
    mock_boto3.client.return_value = mock_sqs

    sqs_operations.send_callback("https://sqs/queue", "job-1", "extracted/job-1.txt")

    mock_sqs.send_message.assert_called_once()
    call_kwargs = mock_sqs.send_message.call_args[1]
    assert call_kwargs["QueueUrl"] == "https://sqs/queue"
    body = json.loads(call_kwargs["MessageBody"])
    assert body["job_id"] == "job-1"
    assert body["output_s3_key"] == "extracted/job-1.txt"
    assert body["status"] == "COMPLETED"
