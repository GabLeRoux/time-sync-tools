from datetime import datetime

import pytz
import yaml

from jira import JIRA


class JiraAPI:
    def __init__(self, config_file="config.yaml", instance_name="default"):
        self.config = self.load_config(config_file)
        self.instance_name = instance_name

        if not self.config:
            raise ValueError("No JIRA instances configured in config file")

        if not self.config["jira_instances"]:
            raise ValueError("No JIRA instances configured in config file")

        if self.instance_name == "default":
            self.instance_name = self.config["jira_instances"][0]["name"]

        if self.instance_name not in [
            instance["name"] for instance in self.config["jira_instances"]
        ]:
            raise ValueError(f"No JIRA instance found with name {instance_name}")

        self.client = self.authenticate()

    @staticmethod
    def load_config(filename):
        with open(filename, "r") as file:
            return yaml.safe_load(file)

    def authenticate(self):
        instance_config = self.get_instance_config(self.instance_name)
        return JIRA(
            server=instance_config["base_url"],
            basic_auth=(instance_config["user_email"], instance_config["api_token"]),
        )

    def get_instance_config(self, instance_name):
        for instance in self.config["jira_instances"]:
            if instance["name"] == instance_name:
                return instance
        raise ValueError(f"No JIRA instance found with name {instance_name}")

    @staticmethod
    def parse_and_localize_datetime(datetime_str, timezone_str="America/Montreal"):
        """Parse a datetime string and localize it to a given timezone."""
        if isinstance(datetime_str, str):
            try:
                # Attempt to parse datetime string with time
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Fallback for date-only string
                dt = datetime.strptime(datetime_str, "%Y-%m-%d")
        else:
            dt = datetime_str
        # Localize datetime to specified timezone if it's naive
        if dt.tzinfo is None:
            timezone = pytz.timezone(timezone_str)
            dt = timezone.localize(dt)
        return dt

    def log_time_to_jira_task(
        self, task_id, start_datetime_str, time_spent_seconds, comment=""
    ):
        """
        Logs time to a JIRA task.
        - task_id: str - the ID of the JIRA task
        - start_datetime_str: str - the start time as string with timezone information
        - time_spent_seconds: int - the amount of time in seconds
        - comment: str - optional comment for the worklog
        """
        try:
            # Parse and localize datetime from string
            start_datetime = self.parse_and_localize_datetime(start_datetime_str)

            issue = self.client.issue(task_id)
            worklog = self.client.add_worklog(
                issue=issue.key,
                timeSpentSeconds=time_spent_seconds,
                started=start_datetime,
                comment=comment,
            )
            return {"success": True, "worklog": worklog.raw}
        except Exception as e:
            return {"error": "Failed to log time to Jira task", "details": str(e)}

    def delete_all_worklogs_for_user_on_given_day(self, date_str, dry_run=False):
        try:
            # Convert string date to datetime object
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            return {"error": "Invalid date format", "details": str(e)}

        formatted_date = date.strftime("%Y-%m-%d")
        # Get the current user's account ID using the current_user method from the JIRA client
        current_user_account_id = self.client.current_user()

        issues = self.client.search_issues(
            jql_str=f"worklogDate = {formatted_date}", expand="changelog"
        )

        results = []
        for issue in issues:
            worklogs = self.client.worklogs(issue)
            for worklog in worklogs:
                # Check if the worklog was made by the logged-in user using the account ID
                if worklog.author.accountId == current_user_account_id:
                    if worklog.started[:10] == formatted_date:
                        if not dry_run:
                            # Jira client doesn't support deleting worklogs directly, so we have to use the REST API
                            headers = {"Content-Type": "application/json"}
                            url = f"{self.client.server_url}/rest/api/2/issue/{issue.key}/worklog/{worklog.id}"
                            auth = (
                                self.client._session.auth[0],
                                self.client._session.auth[1],
                            )
                            response = self.client._session.delete(
                                url, headers=headers, auth=auth
                            )
                            if response.status_code == 204:
                                results.append(
                                    f"Deleted worklog {worklog.id} for issue {issue.key}"
                                )
                            else:
                                results.append(
                                    f"Failed to delete worklog {worklog.id} for issue {issue.key}"
                                )
                        else:
                            results.append(
                                f"Dry run mode: Would delete worklog {worklog.id} for issue {issue.key}"
                            )
        return results
