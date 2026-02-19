"""Amazon Textract operations for PDF text extraction."""

from typing import Dict, List
import boto3
from botocore.exceptions import ClientError

from .constants import TEXTRACT_MAX_PAGES


class TextractClient:
    """Handle PDF text extraction using Amazon Textract."""

    def __init__(self) -> None:
        """Initialize Textract client."""
        self.textract_client = boto3.client("textract")

    def extract_text_from_pdf(self, bucket: str, key: str) -> str:
        """Extract text and tables from PDF using Textract."""
        try:
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}}
            )
            job_id = response["JobId"]
            return self._get_detection_results(job_id)
        except ClientError as e:
            raise Exception(f"Textract extraction failed: {str(e)}")

    def _get_detection_results(self, job_id: str) -> str:
        """Poll and retrieve Textract job results."""
        while True:
            response = self.textract_client.get_document_text_detection(
                JobId=job_id, MaxResults=TEXTRACT_MAX_PAGES
            )
            status = response["JobStatus"]

            if status == "SUCCEEDED":
                return self._parse_blocks(response["Blocks"])
            elif status == "FAILED":
                raise Exception("Textract job failed")
            

    def _parse_blocks(self, blocks: List[Dict]) -> str:
        """Parse Textract blocks to extract text."""
        text_lines = [
            block["Text"] for block in blocks if block["BlockType"] == "LINE"
        ]
        return "\n".join(text_lines)
