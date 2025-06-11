import os
import yaml
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
DATABASE_URL = os.getenv("DATABASE_URL")

def get_channel_list():
    """Loads channel list from channels.yml"""
    with open("channels.yml", "r") as f:
        try:
            data = yaml.safe_load(f)
            return data["channels"]
        except yaml.YAMLError as exc:
            print(exc)
            return []

CHANNELS = get_channel_list() 