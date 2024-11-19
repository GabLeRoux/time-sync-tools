# Time-Sync-Tools

[![codecov](https://codecov.io/gh/GabLeRoux/time-sync-tools/graph/badge.svg?token=VIWjPwKRvM)](https://codecov.io/gh/GabLeRoux/time-sync-tools)

These tools provide a streamlined way to sync and manage time entries across multiple platforms, including **Toggl**, **Wrike**, **Clockify**, **Jira** and **Google Sheets**. The tools retrieve time entries from various platforms, processes them, and enables efficient project and task tracking across different applications.

_This is a technical project which requires you to understand the APIs of the services you are using. Don't execute commands blindly._

<!-- TOC -->
* [Time-Sync-Tools](#time-sync-tools)
  * [The workflow](#the-workflow)
  * [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [Configuration](#configuration)
      * [Environment variables](#environment-variables)
      * [Jira configuration](#jira-configuration)
    * [Usage](#usage)
      * [Toggl](#toggl)
        * [Retrieve time entries for a specific date range](#retrieve-time-entries-for-a-specific-date-range)
        * [Create a new time entry](#create-a-new-time-entry)
      * [Wrike](#wrike)
        * [List all projects](#list-all-projects)
        * [List all folders](#list-all-folders)
        * [List all tasks](#list-all-tasks)
        * [Fetch a specific task by its ID](#fetch-a-specific-task-by-its-id)
      * [Clockify](#clockify)
        * [Retrieve time entries for a date range](#retrieve-time-entries-for-a-date-range)
        * [Create a new time entry](#create-a-new-time-entry-1)
      * [OpenAI](#openai)
        * [Find the closest match from a list of options](#find-the-closest-match-from-a-list-of-options)
        * [Use a different model for matching](#use-a-different-model-for-matching)
      * [Google Sheets](#google-sheets)
        * [Obtaining `credentials.json`](#obtaining-credentialsjson)
        * [Google Sheets Commands](#google-sheets-commands)
          * [Sync Data from Google Sheets to Jira](#sync-data-from-google-sheets-to-jira)
          * [Fetch Data from a Google Sheet](#fetch-data-from-a-google-sheet)
          * [Sync Wrike Tasks to Google Sheets](#sync-wrike-tasks-to-google-sheets)
          * [Sync Data from Google Sheets to Wrike](#sync-data-from-google-sheets-to-wrike)
      * [Jira](#jira)
        * [Log time to a Jira task](#log-time-to-a-jira-task)
        * [Delete all worklogs for a user on a specific day](#delete-all-worklogs-for-a-user-on-a-specific-day)
  * [Development](#development)
    * [Managing dependencies](#managing-dependencies)
    * [Using local environment with uv](#using-local-environment-with-uv)
    * [Run Tests](#run-tests)
    * [Format Code](#format-code)
    * [Contributing](#contributing)
    * [Support](#support)
  * [License](#license)
<!-- TOC -->

## The workflow

Here's how I use this project.

1. I track my time using **Toggl** or **Clockify** and use their **reporting tools** to export a **CSV file**.
2. I _manually_ import this CSV into **Google Sheets** (This part could be automated) with some predefined tabs.
    * These predefined Google Sheet tabs allow me to manage and review my time entries from Toggl or Clockify as my “source of truth.”
    * I recently switched from Toggl to Clockify but kept Toggl support in the project for others who may want to use it. ;)
3. After reviewing the data in Google Sheets, I run a `sync` command that reads data from Google Sheets and import them directly in **Jira**, **Wrike**, or other platforms.

This workflow uses Google Sheets as a review step, giving me control before syncing data to other platforms.

## Getting Started

### Prerequisites

- Python 3.11+
- API keys and tokens for each service:
    - [**Toggl** API key](https://toggl.com/app/profile)
    - [**Wrike** API Token (OAuth 2.0 Authorization)](https://developers.wrike.com/oauth-20-authorization/)
    - [**Clockify** API key](https://clockify.me/developers-api)
    - [**OpenAI** API key](https://platform.openai.com/account/api-keys) (Optional)
    - **Google Sheets** `credentials.json` for integration (see instructions below)
    - [**Jira** API credentials](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) (Optional) 

### Installation

To install Time-Sync-Tools, follow these steps:

```bash
# Clone the repository
git clone https://github.com/GabLeRoux/time-sync-tools.git
# Navigate into the project directory
cd time-sync-tools
# Install dependencies
pip install -r requirements.txt
```

### Configuration

#### Environment variables

Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

Update the `.env` file with your specific API keys for Toggl, Wrike, Clockify, OpenAI, etc.

#### Jira configuration

This project uses a yaml configuration file located at `config.yaml` to store Jira configuration details. 

```bash
cp config.yaml.example config.yaml
```

Then update the `config.yaml` file with your Jira configuration details. You can have multiple jira configurations.

### Usage

#### Toggl

##### Retrieve time entries for a specific date range

```bash
python main.py toggl get_time_entries --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD
```

##### Create a new time entry

```bash
python main.py toggl add_time_entry --description="DESCRIPTION" --start_time="YYYY-MM-DDTHH:MM:SS" --end_time="YYYY-MM-DDTHH:MM:SS"
```

#### Wrike

##### List all projects

```bash
python main.py wrike list_all_projects
```

##### List all folders

```bash
python main.py wrike list_all_folders
```

##### List all tasks

```bash
python main.py wrike get_all_tasks
```

##### Fetch a specific task by its ID

```bash
python main.py wrike get_task_by_id --task_id=YOUR_TASK_ID
```

Manage timelogs (list, create, delete) for tasks. See commands for details.

#### Clockify

##### Retrieve time entries for a date range

```bash
python main.py clockify get_time_entries --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD
```

##### Create a new time entry

```bash
python main.py clockify add_time_entry --description="DESCRIPTION" --start_time="YYYY-MM-DDTHH:MM:SS" --end_time="YYYY-MM-DDTHH:MM:SS"
```

#### OpenAI

##### Find the closest match from a list of options

```bash
python main.py openai find_closest_match --search_param="SEARCH_TERM" --options="option1,option2,option3"
```

##### Use a different model for matching

```bash
python main.py openai find_closest_match --search_param="SEARCH_TERM" --options="option1,option2,option3" --model="MODEL_NAME"
```

#### Google Sheets

##### Obtaining `credentials.json`

1. Go to the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project or select an existing one.
3. Navigate to the **APIs & Services > Dashboard** panel and click on **ENABLE APIS AND SERVICES**.
4. Search for **Google Sheets API** and enable it.
5. In the **Credentials** tab, click on **Create credentials** and choose **OAuth client ID**.
6. If prompted, configure the consent screen, then set the application type to **Desktop app**.
7. Download the JSON file and rename it to `credentials.json`.
8. Place `credentials.json` in the root directory of your project or specify the path in your `google_sheets.py` file.

##### Google Sheets Commands

###### Sync Data from Google Sheets to Jira

Synchronizes time logs from Google Sheets to Jira. Use the Jira project key as the client name.

```bash
python main.py google_sheets sync --client="jira_project_key_from_config"
```

Replace `jira_project_key_from_config` with your configured Jira project key.

###### Fetch Data from a Google Sheet

Retrieves data from the specified sheet title within a Google Sheets document.

```bash
python main.py google_sheets fetch_data_from_sheet --title="SHEET_TITLE" --spreadsheet_id="YOUR_SPREADSHEET_ID"
```

Replace `SHEET_TITLE` and `YOUR_SPREADSHEET_ID` with your specific values.

###### Sync Wrike Tasks to Google Sheets

Syncs task data from Wrike to Google Sheets by creating or updating a specific sheet.

```bash
python main.py google_sheets sync_wrike_to_sheets --spreadsheet_id="YOUR_SPREADSHEET_ID"
```

Replace `YOUR_SPREADSHEET_ID` with your Google Sheet ID.

###### Sync Data from Google Sheets to Wrike

Transfers data from Google Sheets to Wrike, creating time logs based on the provided data. Use `--dry_run=True` for testing without making changes in Wrike.

```bash
python main.py google_sheets sync_sheet_to_wrike --title="SHEET_TITLE" --spreadsheet_id="YOUR_SPREADSHEET_ID" --dry_run=True
```

Replace `YOUR_SPREADSHEET_ID` and `SHEET_TITLE` with the appropriate values in each command. Use `--dry_run=True` for testing mode to validate data without making changes in the target platform.


#### Jira

##### Log time to a Jira task

```bash
python main.py jira log_time_to_task --task_id="TASK_ID" --start_datetime="YYYY-MM-DD HH:MM:SS" --time_spent_seconds=SECONDS --comment="COMMENT"
```

##### Delete all worklogs for a user on a specific day

> ⚠️ **Warning**: This operation permanently deletes worklogs. Always use --dry_run=True first to verify the affected entries.

```bash
python main.py jira delete_all_worklogs_for_user_on_given_day --date="YYYY-MM-DD" --dry_run=True
```

## Development

### Managing dependencies

This project uses [`uv`](https://github.com/astral-sh/uv) to manage dependencies and development tasks.

### Using local environment with uv

```bash
# install uv (see https://docs.astral.sh/uv/getting-started/installation/)
curl -LsSf https://astral.sh/uv/install.sh | sh
# create a virtual environment
uv venv --python=3.11
# activate the virtual environment
source venv/bin/activate
# compile the requirements
uv pip compile requirements.in -o requirements.txt
# install the requirements
uv pip sync requirements.txt
```

### Run Tests

```bash
pytest
```

### Format Code

```bash
uv tool run ruff check --select I --fix .
uv tool run ruff format
```

### Contributing

Contributions are welcome!

* Create an issue to discuss it first
* Fork the repository
* Create a branch for new features or bug fixes
* Write tests for your changes
* Run the tests to ensure they pass
* Submit a pull request for review

### Support

Don't expect support. This is a personal project. You can still open issues if you want, but I might not have time to help you.

## License

[MIT](./LICENSE.md) © [Gabriel Le Breton](https://gableroux.com)
