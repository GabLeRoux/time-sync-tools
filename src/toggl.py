from datetime import datetime

import requests
from tqdm import tqdm

from .config import TOGGL_API_KEY, TOGGL_API_URL

headers = {
    "Authorization": f"Basic {TOGGL_API_KEY}",
    "Content-Type": "application/json",
}


def validate_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"The date must be in YYYY-MM-DD format, but got {date_str}")


def get_time_entries(start_date, end_date):
    start_date = validate_date(start_date)
    end_date = validate_date(end_date)

    if start_date > end_date:
        raise ValueError("The start date cannot be later than the end date")

    # API call to fetch time entries
    params = {
        "start_date": start_date.isoformat() + "Z",
        "end_date": end_date.isoformat() + "Z",
    }
    response = requests.get(
        f"{TOGGL_API_URL}/time_entries", headers=headers, params=params
    )

    if response.status_code == 200:
        entries = response.json()
        # Display progress bar using tqdm while processing the entries
        for entry in tqdm(entries, desc="Processing time entries"):
            pass  # Add any processing tasks if needed
        return entries
    else:
        response.raise_for_status()


def add_time_entry(description, start_time, end_time):
    data = {
        "time_entry": {
            "description": description,
            "start": start_time.isoformat() + "Z",
            "end": end_time.isoformat() + "Z",
            "duration": int((end_time - start_time).total_seconds()),
        }
    }

    print("Adding time entry...")
    with tqdm(total=1, desc="Uploading time entry to Toggl") as pbar:
        response = requests.post(
            f"{TOGGL_API_URL}/time_entries", headers=headers, json=data
        )
        pbar.update(1)  # Update progress after API call

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
