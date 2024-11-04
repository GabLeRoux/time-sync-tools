import pytest
from unittest.mock import patch, MagicMock
from src.toggl import get_time_entries, validate_date


def test_validate_date():
    assert validate_date("2023-06-01")
    with pytest.raises(ValueError):
        validate_date("invalid_date")


@patch("src.toggl.requests.get")
def test_get_time_entries(mock_get):
    # Mock the response for a successful request
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "description": "Test entry 1"},
        {"id": 2, "description": "Test entry 2"}
    ]
    mock_get.return_value = mock_response

    # Call the function and check the results
    entries = get_time_entries("2023-06-01", "2023-06-30")
    assert isinstance(entries, list)
    assert len(entries) == 2
    assert entries[0]["description"] == "Test entry 1"

    # Test for invalid date range
    with pytest.raises(ValueError):
        get_time_entries("2023-06-30", "2023-06-01")