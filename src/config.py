import os

import yaml
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Clockify
CLOCKIFY_API_KEY = os.environ.get("CLOCKIFY_API_KEY")
CLOCKIFY_API_URL = os.environ.get("CLOCKIFY_API_URL", "https://api.clockify.me/api/v1")

# Google Sheets
DEFAULT_GOOGLE_SHEET_ID = os.environ.get("DEFAULT_GOOGLE_SHEET_ID")

# OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Toggl
TOGGL_API_KEY = os.environ.get("TOGGL_API_KEY")
TOGGL_API_URL = os.environ.get("TOGGL_API_URL", "https://api.track.toggl.com/api/v8")

# Wrike
WRIKE_ACCESS_TOKEN = os.environ.get("WRIKE_ACCESS_TOKEN")
WRIKE_API_URL = os.environ.get("WRIKE_API_URL", "https://www.wrike.com/api/v4")
WRIKE_USER_ID = os.environ.get("WRIKE_USER_ID")
WRIKE_DISK_CACHE_DIR = os.getenv("WRIKE_DISK_CACHE_DIR", "disk_cache_directory")

def load_yaml_config(filename="config.yaml"):
    with open(filename, "r") as file:
        return yaml.safe_load(file)


def get_jira_config(instance_name):
    instances = config["jira_instances"]
    for instance in instances:
        if instance["name"] == instance_name:
            return instance
    raise ValueError(f"No JIRA instance found with name {instance_name}")


config = load_yaml_config()
