# Time-Sync-Tools

These tools provides a streamlined way to sync and manage time entries across multiple platforms, including Toggl, Wrike, Clockify, Jira and Google Sheets. This tool retrieves time entries from various platforms, processes them, and enables efficient project and task tracking across these applications. 

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
      * [Wrike](#wrike)
      * [OpenAI](#openai)
      * [Google Sheets](#google-sheets)
        * [Obtaining `credentials.json`](#obtaining-credentialsjson)
        * [Google Sheets Commands:](#google-sheets-commands)
      * [Jira](#jira)
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

* I track my time using Toggl or Clockify and use their **reporting tools** to export a **CSV file**.
* I manually import this CSV into Google Sheets (This part could be automated) with some predefined tabs.
  * These predefined tabs allow me to manage and review my time entries from Toggl or Clockify as my “source of truth.”
  * Recently, I switched from Toggl to Clockify but kept Toggl support in the project for others who may still use it. ;)
* After reviewing the data in Google Sheets, I run specific commands to sync these entries directly to Jira, Wrike, or other platforms.
* This workflow uses Google Sheets as a review step, giving me control before syncing data to other platforms.

## Getting Started

### Prerequisites

- Python 3.11+
- API keys and tokens for each service:
    - [**Toggl** API key](https://toggl.com/app/profile)
    - [**Wrike** API Token (OAuth 2.0 Authorization)](https://developers.wrike.com/oauth-20-authorization/)
    - [**Clockify** API key](https://clockify.me/developers-api)
    - [**OpenAI** API key](https://platform.openai.com/account/api-keys)
    - Google Sheets `credentials.json` for integration (see instructions below)
    - (Optional) Jira API credentials

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

Retrieve time entries for a specific date range:

```bash
python main.py toggl.get_time_entries --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD
```

Create a new time entry:

```bash
python main.py toggl.add_time_entry --description="DESCRIPTION" --start_time="YYYY-MM-DDTHH:MM:SS" --end_time="YYYY-MM-DDTHH:MM:SS"
```

#### Wrike

List all projects:

```bash
python main.py wrike.list_all_projects
```

List all folders:

```bash
python main.py wrike.list_all_folders
```

List all tasks:

```bash
python main.py wrike.get_all_tasks
```

Fetch a specific task by its ID:

```bash
python main.py wrike.get_task_by_id --task_id=YOUR_TASK_ID
```

Manage timelogs (list, create, delete) for tasks. See commands for details.

Clockify

Retrieve time entries for a date range:

```bash
python main.py clockify.get_time_entries --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD
```

Create a new time entry:

```bash
python main.py clockify.add_time_entry --description="DESCRIPTION" --start_time="YYYY-MM-DDTHH:MM:SS" --end_time="YYYY-MM-DDTHH:MM:SS"
```

#### OpenAI

Find the closest match from a list of options:

```bash
python main.py openai.find_closest_match --search_param="SEARCH_TERM" --options="option1,option2,option3"
```

Use a different model for matching:

```bash
python main.py openai.find_closest_match --search_param="SEARCH_TERM" --options="option1,option2,option3" --model="MODEL_NAME"
```

#### Google Sheets

##### Obtaining `credentials.json`

1. Go to the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project or select an existing one.
3. Navigate to the "APIs & Services > Dashboard" panel and click on “ENABLE APIS AND SERVICES”.
4. Search for "Google Sheets API" and enable it.
5. In the "Credentials" tab, click on "Create credentials" and choose "OAuth client ID".
6. If prompted, configure the consent screen, and then set the application type to "Desktop app".
7. Download the JSON file and rename it to `credentials.json`.
8. Place `credentials.json` in the root directory of your project or specify the path in your `google_sheets.py` file

##### Google Sheets Commands:

Sync Wrike tasks to Google Sheets:

```bash
python main.py google_sheets.sync_wrike_to_sheets --spreadsheet_id="YOUR_SPREADSHEET_ID"
```

Fetch data from a Google Sheet:

```bash
python main.py google_sheets.fetch_data_from_sheet --title="SHEET_TITLE" --spreadsheet_id="YOUR_SPREADSHEET_ID"
```

Create time logs from Google Sheets data in Wrike:

```bash
python main.py google_sheets.sheet_to_create_time_logs_from_data --title="SHEET_TITLE" --spreadsheet_id="YOUR_SPREADSHEET_ID" --dry_run=True
```

Replace YOUR_SPREADSHEET_ID and SHEET_TITLE with the appropriate values. Use --dry_run=True for testing without making changes.

#### Jira

Log time to a Jira task:

```bash
python main.py jira.log_time_to_task --task_id="TASK_ID" --start_datetime="YYYY-MM-DD HH:MM:SS" --time_spent_seconds=SECONDS --comment="COMMENT"
```

Delete all worklogs for a user on a specific day:

```bash
python main.py jira.delete_all_worklogs_for_user_on_given_day --date="YYYY-MM-DD" --dry_run=True
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
