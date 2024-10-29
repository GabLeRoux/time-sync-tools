import fire

from src import clockify, google_sheets, jira, openai, toggl, wrike

if __name__ == "__main__":
    fire.Fire(
        {
            "toggl": toggl,
            "wrike": wrike,
            "jira": jira.JiraAPI(),
            "openai": openai,
            "google_sheets": google_sheets,
            "clockify": clockify,
        }
    )
