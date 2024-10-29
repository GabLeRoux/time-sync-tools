from unittest.mock import patch

import pytest

from src.wrike import _validate_task_id, get_task_by_id


def test_validate_task_id():
    assert _validate_task_id("abc123") == "abc123"
    with pytest.raises(ValueError):
        _validate_task_id("!invalid_id!")


class MockResponse:
    @staticmethod
    def json():
        return {"id": "abc123", "title": "Sample Task"}


@patch("requests.get")
def test_get_task_by_id(mock_get):
    # Mocking a successful API response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json = MockResponse.json

    task = get_task_by_id("abc123")
    assert isinstance(task, dict)
    assert task["id"] == "abc123"

    # Mocking an unsuccessful API response
    mock_get.return_value.status_code = 400
    mock_get.return_value.json = MockResponse.json

    task = get_task_by_id("abc123")
    assert task is None
