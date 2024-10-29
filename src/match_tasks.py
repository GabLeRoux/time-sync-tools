from .toggl import get_time_entries
from .wrike import get_task_by_id


def match_toggl_entries_to_wrike_tasks(start_date, end_date):
    toggl_entries = get_time_entries(start_date, end_date)
    for entry in toggl_entries:
        task_id = entry["id"]
        wrike_task = get_task_by_id(task_id)
        print(f"Matched Toggl entry {entry} to Wrike task {wrike_task}")
