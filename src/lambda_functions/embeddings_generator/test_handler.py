"""Unit tests for embeddings generator Lambda."""

from . import handler
import json
from unittest.mock import MagicMock, patch

@patch.object(handler, 'EmbeddingProcessor')
def test_lambda_handler_success(mock_processor_class) -> None:
    """Test successful embedding generation."""
    event = {
        "bucket": "test-bucket", 
        "key": "documents/test.pdf"
    }
    mock_instance = MagicMock()
    mock_processor_class.return_value = mock_instance
    mock_instance.process_file.return_value = {
            "source_file": "documents/test.pdf",
            "chunk_count": 5,
        }
    mock_instance.save_embeddings.return_value = "embeddings/test_embeddings.json"

    response = handler.lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])

    assert body["message"] == "Embeddings generated successfully"
    assert body["chunk_count"] == 5
    assert body["source_file"] == "documents/test.pdf"
    assert body["output_file"] == "embeddings/test_embeddings.json"
    mock_instance.process_file.assert_called_once_with("test-bucket", "documents/test.pdf")


@patch.object(handler, 'EmbeddingProcessor')
def test_lambda_handler_with_custom_model(mock_processor_class) -> None:
    """Test embedding generation with custom model."""
    event = {
        "bucket": "test-bucket",
        "key": "documents/test.txt",
        "model_id": "custom-model-id",
    }
    mock_instance = MagicMock()
    mock_processor_class.return_value = mock_instance
    mock_instance.process_file.return_value = {
            "source_file": "documents/test.txt",
            "chunk_count": 3,
        }
    mock_instance.save_embeddings.return_value = "embeddings/test_embeddings.json"
    response = handler.lambda_handler(event, None)
    mock_processor_class.assert_called_once_with("custom-model-id")
    assert response["statusCode"] == 200

    # with patch("handler.EmbeddingProcessor") as mock_processor:
        


# def test_lambda_handler_error() -> None:
#     """Test error handling."""
#     event = {"bucket": "test-bucket", "key": "documents/test.pdf"}

#     with patch("handler.EmbeddingProcessor") as mock_processor:
#         mock_processor.side_effect = Exception("Test error")

#         response = lambda_handler(event, None)

#         assert response["statusCode"] == 500
#         body = json.loads(response["body"])
#         assert "error" in body
