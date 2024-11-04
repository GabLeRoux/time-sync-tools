import subprocess

import pytest


@pytest.mark.parametrize(
    "command, expected_output",
    [
        (
            ["python", "-m", "main", "toggl"],
            "Toggl functions available",
        ),  # Add expected output or part of it
        (
            ["python", "-m", "main", "wrike"],
            "Wrike functions available",
        ),  # Add expected output or part of it
        (
            ["python", "-m", "main", "openai"],
            "OpenAI functions available",
        ),  # Add expected output or part of it
    ],
)
def test_fire_cli(command, expected_output):
    try:
        output = subprocess.check_output(command, text=True)
        assert expected_output in output
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Command '{' '.join(command)}' failed with error: {str(e)}")
