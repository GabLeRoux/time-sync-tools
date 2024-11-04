import csv
import re
from datetime import datetime

import requests
from diskcache import Cache
from halo import Halo

from .config import WRIKE_ACCESS_TOKEN, WRIKE_API_URL

# Setup diskcache
CACHE_DIR = "disk_cache_directory"
cache = Cache(CACHE_DIR)


def _validate_task_id(task_id):
    if not re.match("^[a-zA-Z0-9]+$", task_id):
        raise ValueError("Invalid task ID format")
    return task_id


def _validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")
    return date_str


def _get_headers():
    return {"Authorization": f"Bearer {WRIKE_ACCESS_TOKEN}"}


def _handle_api_response(response):
    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"Error: Unable to process API request. HTTP Status code: {response.status_code}"
        )
        print(f"Response body: {response.text}")
        print(f"Request URL: {response.url}")
        print(f"Request headers: {response.request.headers}")
        print(f"Request body: {response.request.body}")
        return None


def fetch_data(func, *args, **kwargs):
    key = (func.__name__, args, frozenset(kwargs.items()))

    if key in cache:
        return cache[key]

    result = func(*args, **kwargs)
    cache[key] = result
    return result


def get_connected_user_id():
    return fetch_data(_get_connected_user_id_internal)


def _get_connected_user_id_internal():
    response = requests.get(f"{WRIKE_API_URL}/contacts?me=true", headers=_get_headers())
    data = _handle_api_response(response)

    if data and "data" in data and len(data["data"]) > 0:
        return data["data"][0]["id"]
    else:
        return None


# Similar pattern applies for all other functions:
# Separate the core logic into an "internal" function,
# and have the publicly-exposed function call `fetch_data`.


# For brevity, I'll demonstrate just one more:
def get_all_tasks(folder_or_project_id=None, page_size=1000, tsv=False):
    data = fetch_data(_get_all_tasks_internal, folder_or_project_id, page_size)
    if tsv:
        return "\n".join([f"{row[0]}\t{row[1]}" for row in data])
    else:
        return data


def _get_all_tasks_internal(folder_or_project_id=None, page_size=1000):
    tasks = []
    next_page_token = None

    while True:
        params = {"pageSize": page_size, "descendants": True, "subTasks": True}
        if next_page_token:
            params["nextPageToken"] = next_page_token

        url = f"{WRIKE_API_URL}/tasks"
        if folder_or_project_id:
            url = f"{WRIKE_API_URL}/folders/{folder_or_project_id}/tasks"

        response = requests.get(url, headers=_get_headers(), params=params)
        data = _handle_api_response(response)

        if data and "data" in data:
            for task in data["data"]:
                task_id = task.get("id")
                task_name = task.get("title")
                tasks.append((task_id, task_name))

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

    return tasks


def _print_to_console_as_csv(data):
    print("Task ID,Task Name")
    for row in data:
        print(f"{row[0]},{row[1]}")


def get_all_tasks_as_csv(folder_or_project_id=None, page_size=1000):
    data = get_all_tasks(folder_or_project_id, page_size)
    _print_to_console_as_csv(data)


def list_all_projects():
    return fetch_data(_list_all_projects_internal)


def _list_all_projects_internal():
    response = requests.get(
        f"{WRIKE_API_URL}/folders", headers=_get_headers(), params={"type": "Project"}
    )
    data = _handle_api_response(response)
    return (
        [(project["id"], project["title"]) for project in data["data"]]
        if data
        else None
    )


def list_all_folders():
    return fetch_data(_list_all_folders_internal)


def _list_all_folders_internal():
    response = requests.get(f"{WRIKE_API_URL}/folders", headers=_get_headers())
    data = _handle_api_response(response)
    return (
        [(folder["id"], folder["title"]) for folder in data["data"]] if data else None
    )


def get_task_by_id(task_id):
    return fetch_data(_get_task_by_id_internal, task_id)


def _get_task_by_id_internal(task_id):
    task_id = _validate_task_id(task_id)

    spinner = Halo(text="Fetching task from Wrike...", spinner="dots")
    spinner.start()

    response = requests.get(f"{WRIKE_API_URL}/tasks/{task_id}", headers=_get_headers())

    spinner.stop()
    return _handle_api_response(response)


def create_timelog(task_id, hours, tracked_date, comment=""):
    return fetch_data(_create_timelog_internal, task_id, hours, tracked_date, comment)


def _create_timelog_internal(task_id, hours, tracked_date, comment=""):
    task_id = _validate_task_id(str(task_id))
    tracked_date = _validate_date(tracked_date)

    data = {"hours": hours, "trackedDate": tracked_date, "comment": comment}
    response = requests.post(
        f"{WRIKE_API_URL}/tasks/{task_id}/timelogs", headers=_get_headers(), data=data
    )

    return _handle_api_response(response)


def create_timelogs_from_csv(file_path, dry_run=False):
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        create_time_logs_from_data(reader, dry_run)


def create_time_logs_from_data(data, dry_run=False):
    timelogs = []
    for row in data:
        date, hours, comment, task_key = row
        if dry_run:
            print(
                f"Dry Run - create_timelog(task_id={task_key}, hours={hours}, date={date}, comment={comment})"
            )
        else:
            timelog = create_timelog(
                task_id=task_key, hours=hours, tracked_date=date, comment=comment
            )
            print(timelog)
            timelogs.append(timelog)
    return timelogs


def delete_timelog(timelog_id):
    response = requests.delete(
        f"{WRIKE_API_URL}/timelogs/{timelog_id}", headers=_get_headers()
    )
    return _handle_api_response(response)


def get_specific_timelog_from_id(timelog_id):
    return fetch_data(_get_specific_timelog_from_id_internal, timelog_id)


def _get_specific_timelog_from_id_internal(timelog_id):
    response = requests.get(
        f"{WRIKE_API_URL}/timelogs/{timelog_id}", headers=_get_headers()
    )
    return _handle_api_response(response)


def list_timelogs(task_id):
    return fetch_data(_list_timelogs_internal, task_id)


def _list_timelogs_internal(task_id):
    task_id = _validate_task_id(str(task_id))
    response = requests.get(
        f"{WRIKE_API_URL}/tasks/{task_id}/timelogs", headers=_get_headers()
    )
    return _handle_api_response(response)


def get_all_timelogs(
    created_date_range=None, tracked_date_range=None, for_current_user=True, tsv=False
):
    """
    Get all timelog records. Can optionally filter by created_date_range and tracked_date_range.

    :param created_date_range: Optional tuple with start and end dates for creation date filtering.
    :param tracked_date_range: Optional tuple with start and end dates for tracking date filtering.
    :param for_current_user: Boolean, if set to True will only fetch timelogs created by current user.
    :return: List of timelog records.
    """
    data = fetch_data(
        _get_all_timelogs_internal,
        created_date_range,
        tracked_date_range,
        for_current_user,
    )
    if tsv:
        rows = []
        for row in data:
            rows.append(
                f"{row['id']}\t{row['hours']}\t{row['createdDate']}\t{row['trackedDate']}\t{row['comment']}"
            )
        return "\n".join(rows)
    return data


def _get_all_timelogs_internal(
    created_date_range, tracked_date_range, for_current_user
):
    params = {}

    if created_date_range:
        start_date, end_date = created_date_range
        params["createdDate"] = {
            "start": start_date.isoformat() + "Z",
            "end": end_date.isoformat() + "Z",
        }

    if tracked_date_range:
        start_date, end_date = tracked_date_range
        params["trackedDate"] = {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
        }

    if for_current_user:
        params["me"] = True

    response = requests.get(
        f"{WRIKE_API_URL}/timelogs", headers=_get_headers(), params=params
    )
    data = _handle_api_response(response)
    return data.get("data", []) if data else []


def get_all_timelogs_with_task_data(
    created_date_range=None, tracked_date_range=None, for_current_user=True
):
    """
    Get all timelog records and their associated task data. Can optionally filter by created_date_range and tracked_date_range.

    :param created_date_range: Optional tuple with start and end dates for creation date filtering.
    :param tracked_date_range: Optional tuple with start and end dates for tracking date filtering.
    :param for_current_user: Boolean, if set to True will only fetch timelogs created by current user.
    :return: List of timelog records with their associated task data.
    """
    timelogs = fetch_data(
        _get_all_timelogs_internal,
        created_date_range,
        tracked_date_range,
        for_current_user,
    )

    # Iterate through the timelogs and fetch task data
    enriched_timelogs = []
    for timelog in timelogs:
        task_id = timelog.get("taskId")
        task_data_response = fetch_data(_get_task_by_id_internal, task_id)

        # Extract task data
        task_data = (
            task_data_response["data"][0]
            if task_data_response
            and "data" in task_data_response
            and len(task_data_response["data"]) > 0
            else None
        )

        # Combine timelog and task data
        enriched_timelog = {
            "hours": timelog.get("hours"),
            "createdDate": timelog.get("createdDate"),
            "updatedDate": timelog.get("updatedDate"),
            "trackedDate": timelog.get("trackedDate"),
            "comment": timelog.get("comment"),
            "permalink": task_data.get("permalink") if task_data else None,
            "task_name": task_data.get("title") if task_data else "Unknown Task Name",
        }
        enriched_timelogs.append(enriched_timelog)

    return enriched_timelogs


def delete_cache():
    cache.clear()
