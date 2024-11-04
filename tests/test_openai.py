from unittest.mock import MagicMock, patch
from src.openai import find_closest_match, OpenAIClient


def test_find_closest_match():
    mock_client = MagicMock()
    mock_client.get_ratings.return_value = {
        "option 1": 90,
        "option 2": 75,
        "option 3": 50
    }

    options = ["option 1", "option 2", "option 3"]
    prompt = "Find the closest option to this prompt"

    result = find_closest_match(search_param=prompt, options=options, client=mock_client)

    assert result == "option 1"
    mock_client.get_ratings.assert_called_once_with(prompt, options, 0.7, 50)


def test_find_closest_match_no_scores():
    mock_client = MagicMock()
    mock_client.get_ratings.return_value = {}

    options = ["option 1", "option 2", "option 3"]
    prompt = "Find the closest option to this prompt"

    result = find_closest_match(search_param=prompt, options=options, client=mock_client)

    assert result is None
    mock_client.get_ratings.assert_called_once_with(prompt, options, 0.7, 50)


def test_find_closest_match_with_empty_options():
    mock_client = MagicMock()
    mock_client.get_ratings.return_value = {}

    prompt = "Find the closest option to this prompt"
    result = find_closest_match(search_param=prompt, options=[], client=mock_client)

    assert result is None
    mock_client.get_ratings.assert_called_once_with(prompt, [], 0.7, 50)


def test_find_closest_match_exception():
    mock_client = MagicMock()
    mock_client.get_ratings.side_effect = Exception("API error")

    options = ["option 1", "option 2", "option 3"]
    prompt = "Find the closest option to this prompt"

    result = find_closest_match(search_param=prompt, options=options, client=mock_client)

    assert result is None
