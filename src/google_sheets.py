import datetime
import logging
import os
import pickle
import sys

import pytz
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from src.config import DEFAULT_GOOGLE_SHEET_ID
from src.jira import JiraAPI
from src.wrike import create_time_logs_from_data, get_all_tasks

# Create a logger for the 'google_sheets' module
logger = logging.getLogger("google_sheets")
logger.setLevel(logging.INFO)  # Set the logging level to INFO

# Directory for log files
log_dir = "logs/google_sheets"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # Create the directory if it doesn't exist

# Log file name with date and time
log_file = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"

# Create a file handler to write logs to a file
file_handler = logging.FileHandler(os.path.join(log_dir, log_file))
file_handler.setLevel(logging.INFO)  # Set the logging level for the file handler

# Create a formatter and set it for the file handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def login_to_google_sheets():
    creds = None
    token_pickle_file = "token.pickle"
    # Check if the token.pickle file exists and is valid for current scopes
    if os.path.exists(token_pickle_file):
        with open(token_pickle_file, "rb") as token:
            creds = pickle.load(token)
        if set(creds.scopes) != set(SCOPES):  # Scopes comparison
            logger.info("Scopes have changed, re-authenticate needed.")
            creds = None

    # Refresh or obtain new credentials if necessary
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as e:
                logger.error(f"Error refreshing token: {e}")
                creds = None  # Force re-authentication

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_pickle_file, "wb") as token:
            pickle.dump(creds, token)

    if not creds:
        logger.error("Authentication has failed")
        sys.exit(1)

    service = build("sheets", "v4", credentials=creds)
    return service


def check_or_create_sheet(service, spreadsheet_id, title):
    # Get metadata to check for the existing sheets
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get("sheets", "")

    # Determine if the sheet exists
    sheet_exists = any(sheet["properties"]["title"] == title for sheet in sheets)

    # If the sheet does not exist, create it
    if not sheet_exists:
        batch_update_spreadsheet_request_body = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": title,
                        }
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=batch_update_spreadsheet_request_body
        ).execute()
        logger.info(f"Sheet '{title}' created.")
    else:
        logger.warning(f"Sheet '{title}' already exists. No new sheet was created.")

    # Return a boolean indicating if the sheet had to be created (True if it was created, False otherwise)
    return not sheet_exists


def update_sheet_with_data(service, spreadsheet_id, title, data):
    # Prepare the data for insertion into the sheet
    value_range_body = {"values": data}

    # Insert data into the sheet
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{title}!A1",
        valueInputOption="USER_ENTERED",
        body=value_range_body,
    ).execute()


def sync_wrike_to_sheets(spreadsheet_id=DEFAULT_GOOGLE_SHEET_ID):
    # Log in to Google Sheets API
    service = login_to_google_sheets()

    # Get current date to title the new sheet
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    sheet_title = f"Wrike Tasks {today}"

    # Get folder or project IDs from environment variable
    folder_ids = os.getenv("WRIKE_FOLDER_IDS", "").split(",")

    # Fetch Wrike data for each folder or project ID
    wrike_data = []
    for folder_id in folder_ids:
        folder_data = get_all_tasks(folder_or_project_id=folder_id.strip())
        wrike_data.extend(folder_data)

    # Check or create the Google Sheet
    check_or_create_sheet(service, spreadsheet_id, sheet_title)

    # Update the Google Sheet with the combined Wrike data
    update_sheet_with_data(service, spreadsheet_id, sheet_title, wrike_data)

    print(f"Sync completed. Data added to the sheet: {sheet_title}")


def fetch_data_from_sheet(title, spreadsheet_id=DEFAULT_GOOGLE_SHEET_ID):
    service = login_to_google_sheets()

    # Assumes you want to fetch all rows and columns
    range_name = f"{title}!A:Z"

    try:
        # Use the Sheets API to fetch the data
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            logger.warning(f"No data found in sheet: {title}")
            return None
        else:
            logger.info(
                f"Data fetched from sheet '{title}' in spreadsheet '{spreadsheet_id}'"
            )
            return values

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


def sync_sheet_to_wrike(title=None, spreadsheet_id=DEFAULT_GOOGLE_SHEET_ID, dry_run=False):
    if title is None:
        title = f"wrike sync {datetime.datetime.now().strftime('%Y-%m-%d')}"
    data = fetch_data_from_sheet(title, spreadsheet_id)
    if not data:
        logger.info(f"No data found in sheet: {title}")
        return
    data = data[1:]  # skip the first row

    # Log the number of rows to be processed
    logger.info(f"Processing {len(data)} rows from sheet '{title}'")

    timelogs = create_time_logs_from_data(data=data, dry_run=dry_run)
    for timelog in timelogs:
        logger.info(f"Created time log: {timelog}")


def sync(client):
    jira_instance_name = client
    sheet_name = f"Jira Sync {jira_instance_name}"
    sync_sheet_to_jira(sheet_name, jira_instance_name)


def sync_sheet_to_jira(
    sheet_name: str,
    jira_instance_name: str,
    spreadsheet_id: str = DEFAULT_GOOGLE_SHEET_ID,
    dry_run: bool = False,
):
    logger.info("Starting sync from Google Sheets to Jira.")
    montreal_tz = pytz.timezone("America/Montreal")

    try:
        service: Resource = login_to_google_sheets()
        range_name: str = f"{sheet_name}!A:E"
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            logger.warning("No data found in the specified Google Sheet.")
            return

        jira_api: JiraAPI = JiraAPI(instance_name=jira_instance_name)

        for index, row in enumerate(values[1:], start=2):  # Skip header row
            if len(row) < 4:
                logger.error(
                    f"Row {index} is missing some values. Expected at least 4, got {len(row)}."
                )
                continue

            start_date, start_time, time_spent, task = row[:4]
            comment = (
                row[4] if len(row) > 4 else ""
            )  # Check if comment is provided; otherwise, set to empty string

            task_id: str = task.split(" ")[0]
            datetime_str: str = f"{start_date} {start_time}"

            # 10/24/2024	4:15 PM
            format_1 = "%m/%d/%Y %I:%M %p"
            # 2024-10-24 16:15:00
            format_2 = "%Y-%m-%d %H:%M:%S"
            try:
                start_datetime: datetime.datetime = datetime.datetime.strptime(
                    datetime_str, format_1
                )
                montreal_dt: datetime.datetime = montreal_tz.localize(start_datetime)
            except ValueError as e:
                try:
                    start_datetime: datetime.datetime = datetime.datetime.strptime(
                        datetime_str, format_2
                    )
                    montreal_dt: datetime.datetime = montreal_tz.localize(
                        start_datetime
                    )
                except ValueError as e:
                    logger.error(
                        f"Error parsing date and time for row {index}: {str(e)}"
                    )
                    continue

            time_spent_seconds: int = int(float(time_spent) * 3600)

            if not dry_run:
                response: dict = jira_api.log_time_to_jira_task(
                    task_id, montreal_dt, time_spent_seconds, comment
                )
                logger.info(f"Logged time for task {task_id}: {response}")
            else:
                logger.info(
                    f"Dry run mode: Would log time for task {task_id} at {montreal_dt} for {time_spent_seconds} seconds."
                )

        logger.info("Sync from Google Sheets to Jira completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred while syncing data to Jira: {str(e)}")
