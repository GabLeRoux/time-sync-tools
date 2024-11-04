import os
from unittest.mock import patch, MagicMock
import pytest
from src.wrike import _validate_task_id, get_task_by_id, delete_cache

# Set a temporary cache directory for testing
os.environ["WRIKE_DISK_CACHE_DIR"] = "/tmp/test_disk_cache"

def test_validate_task_id():
    assert _validate_task_id("abc123") == "abc123"
    with pytest.raises(ValueError):
        _validate_task_id("!invalid_id!")


class MockResponse:
    @staticmethod
    def json():
        return {"id": "abc123", "title": "Sample Task"}


@patch("src.wrike.requests.get")
def test_get_task_by_id(mock_get):
    # Ensure cache is clear at the start of the test
    delete_cache()

    # Mocking a successful API response
    successful_response = MagicMock()
    successful_response.status_code = 200
    successful_response.json = MockResponse.json
    mock_get.return_value = successful_response

    task = get_task_by_id("abc123")
    assert isinstance(task, dict)
    assert task["id"] == "abc123"

    # Clear cache to ensure a fresh call for the unsuccessful response
    delete_cache()

    # Mocking an unsuccessful API response
    unsuccessful_response = MagicMock()
    unsuccessful_response.status_code = 400
    unsuccessful_response.json = lambda: {"error": "Bad Request"}
    mock_get.return_value = unsuccessful_response

    task = get_task_by_id("abc123")
    assert task is None

    # Clean up the cache at the end of the test
    delete_cache()