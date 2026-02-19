"""Set environment variables before any test module in this package is imported."""

import os

os.environ.setdefault("TEXTRACT_SNS_TOPIC_ARN", "arn:aws:sns:us-east-2:103703793592:sns-textract-jobs")
os.environ.setdefault("TEXTRACT_ROLE_ARN", "arn:aws:iam::123:role/textract-role")
os.environ.setdefault("DYNAMODB_TABLE_NAME", "tbl_textract_jobs")
os.environ.setdefault("OUTPUT_BUCKET", "tushar-1371-rag-demo-bucket")
