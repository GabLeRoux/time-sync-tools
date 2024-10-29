from unittest.mock import MagicMock, patch

from src.openai import find_closest_match


@patch("openai.Completion.create")
def test_find_closest_match(mock_create):
    mock_create.return_value = MagicMock(choices=[MagicMock(text="option 1")])

    options = ["option 1", "option 2", "option 3"]
    prompt = "Find the closest option to this prompt"

    result = find_closest_match(model="GPT-4", prompt=prompt, options=options)

    assert result == "option 1"
    mock_create.assert_called_once_with(
        engine="GPT-4",
        prompt=prompt,
        max_tokens=1,
        n=1,
        stop=None,
        temperature=0.7,
        choices=options,
    )


@patch("openai.Completion.create")
def test_find_closest_match_no_choices(mock_create):
    mock_create.return_value = MagicMock(choices=[])

    options = ["option 1", "option 2", "option 3"]
    prompt = "Find the closest option to this prompt"

    result = find_closest_match(model="GPT-4", prompt=prompt, options=options)

    assert result is None
    mock_create.assert_called_once_with(
        engine="GPT-4",
        prompt=prompt,
        max_tokens=1,
        n=1,
        stop=None,
        temperature=0.7,
        choices=options,
    )


@patch("openai.Completion.create")
def test_find_closest_match_exception(mock_create):
    mock_create.side_effect = Exception("Error while using OpenAI API")

    options = ["option 1", "option 2", "option 3"]
    prompt = "Find the closest option to this prompt"

    result = find_closest_match(model="GPT-4", prompt=prompt, options=options)

    assert result is None
    mock_create.assert_called_once_with(
        engine="GPT-4",
        prompt=prompt,
        max_tokens=1,
        n=1,
        stop=None,
        temperature=0.7,
        choices=options,
    )


@patch("openai.Completion.create")
def test_find_closest_match_with_options_none(mock_create=None):
    mock_create.return_value = MagicMock(choices=[])
    prompt = "example"
    result = find_closest_match(prompt=prompt)
    assert result is None
    mock_create.assert_called_once_with(
        engine="GPT-4",
        prompt=prompt,
        max_tokens=1,
        n=1,
        stop=None,
        temperature=0.7,
        choices=[],
    )
