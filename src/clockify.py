from datetime import datetime

import requests

from .config import CLOCKIFY_API_KEY, CLOCKIFY_API_URL

headers = {
    "X-Api-Key": CLOCKIFY_API_KEY,
    "Content-Type": "application/json",
}


def validate_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"The date must be in YYYY-MM-DD format, but got {date_str}")


def get_time_entries(workspace_id, start_date, end_date):
    start_date = validate_date(start_date)
    end_date = validate_date(end_date)

    if start_date > end_date:
        raise ValueError("The start date cannot be later than the end date")

    # API call to fetch time entries
    params = {
        "start": start_date.isoformat() + "Z",
        "end": end_date.isoformat() + "Z",
    }
    response = requests.get(
        f"{CLOCKIFY_API_URL}/workspaces/{workspace_id}/time-entries",
        headers=headers,
        params=params,
    )

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def add_time_entry(workspace_id, start_time, end_time, description):
    data = {
        "start": start_time.isoformat() + "Z",
        "end": end_time.isoformat() + "Z",
        "description": description,
        # Add more fields as per Clockify API requirements
    }

    response = requests.post(
        f"{CLOCKIFY_API_URL}/workspaces/{workspace_id}/time-entries",
        headers=headers,
        json=data,
    )

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_workspaces():
    response = requests.get(f"{CLOCKIFY_API_URL}/workspaces", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
