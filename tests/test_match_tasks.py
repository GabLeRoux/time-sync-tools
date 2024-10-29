from unittest.mock import patch

from src.match_tasks import match_toggl_entries_to_wrike_tasks

# Mock data
mock_toggl_entries = [
    {"id": "task1", "description": "Task 1 description"},
    {"id": "task2", "description": "Task 2 description"},
]

mock_wrike_task = {"id": "task1", "title": "Task 1 title"}


# Test cases
@patch("src.match_tasks.get_time_entries")
@patch("src.match_tasks.get_task_by_id")
def test_match_toggl_entries_to_wrike_tasks(mock_get_task_by_id, mock_get_time_entries):
    # Mocking the return values of the dependencies
    mock_get_time_entries.return_value = mock_toggl_entries
    mock_get_task_by_id.return_value = mock_wrike_task

    # Redirecting print output to a string
    with patch("builtins.print") as mock_print:
        match_toggl_entries_to_wrike_tasks("2023-06-01", "2023-06-18")

        # Verifying if get_time_entries was called once with the correct parameters
        mock_get_time_entries.assert_called_once_with("2023-06-01", "2023-06-18")

        # Verifying if get_task_by_id was called with the correct task IDs
        mock_get_task_by_id.assert_any_call("task1")
        mock_get_task_by_id.assert_any_call("task2")

        # Verifying if print was called with the correct format
        mock_print.assert_any_call(
            "Matched Toggl entry {'id': 'task1', 'description': 'Task 1 description'} to Wrike task {'id': 'task1', 'title': 'Task 1 title'}"
        )
        mock_print.assert_any_call(
            "Matched Toggl entry {'id': 'task2', 'description': 'Task 2 description'} to Wrike task {'id': 'task1', 'title': 'Task 1 title'}"
        )
