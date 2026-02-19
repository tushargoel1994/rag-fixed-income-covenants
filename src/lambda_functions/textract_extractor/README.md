# textract_extractor

Async PDF text extraction service using Amazon Textract. Accepts any S3 PDF and returns extracted text via DynamoDB and an optional SQS callback.

## Invocation Modes

### 1. Direct Invoke (start extraction)
Any service or Lambda invokes this function with:
```json
{
  "bucket": "my-bucket",
  "key": "documents/file.pdf",
  "callback_queue_url": "https://sqs.region.amazonaws.com/account/queue"
}
```
Returns:
```json
{ "job_id": "abc123", "status": "SUBMITTED" }
```
`callback_queue_url` is optional. If provided, extracted text is sent to that queue on completion.

### 2. SQS Trigger (result processing)
Triggered automatically when Textract publishes job completion to SNS → SQS.
Fetches result, stores in DynamoDB, and sends to `callback_queue_url` if set.

## Result Retrieval

- **Polling**: Query DynamoDB table with `job_id` to check `status` and `extracted_text`
- **Event-driven**: Provide `callback_queue_url` at invocation; result is pushed when ready

## Environment Variables

| Variable | Description |
|---|---|
| `TEXTRACT_SNS_TOPIC_ARN` | SNS topic ARN for Textract completion notifications |
| `TEXTRACT_ROLE_ARN` | IAM role ARN allowing Textract to publish to SNS |
| `DYNAMODB_TABLE_NAME` | DynamoDB table for job tracking (PK: `job_id`) |

## Infrastructure Required
- SNS topic subscribed to SQS queue
- SQS queue as Lambda trigger
- DynamoDB table with `job_id` as partition key
