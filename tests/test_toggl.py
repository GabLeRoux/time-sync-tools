import pytest

from src.toggl import get_time_entries, validate_date


def test_validate_date():
    assert validate_date("2023-06-01")
    with pytest.raises(ValueError):
        validate_date("invalid_date")


def test_get_time_entries():
    entries = get_time_entries("2023-06-01", "2023-06-30")
    assert isinstance(entries, list)
    with pytest.raises(ValueError):
        get_time_entries("2023-06-30", "2023-06-01")
