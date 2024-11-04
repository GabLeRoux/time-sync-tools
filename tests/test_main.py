import subprocess

import pytest


@pytest.mark.parametrize(
    "command, expected_output",
    [
        (
            ["python", "-m", "main", "toggl"],
            "main.py toggl",
        ),
        (
            ["python", "-m", "main", "wrike"],
            "main.py wrike",
        ),
        (
            ["python", "-m", "main", "openai"],
            "main.py openai",
        ),
        (
            ["python", "-m", "main", "clockify"],
            "main.py clockify",
        ),
        (
            ["python", "-m", "main", "google_sheets"],
            "main.py google_sheets",
        ),
        (
            ["python", "-m", "main", "jira"],
            "main.py jira",
        ),
    ],
)
def test_fire_cli(command, expected_output):
    try:
        output = subprocess.check_output(command, text=True)
        assert expected_output in output
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Command '{' '.join(command)}' failed with error: {str(e)}")
