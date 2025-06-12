import os
import time
import yaml
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# Add startup assertions to ensure critical credentials are set
if not API_ID:
    raise ValueError("Missing required environment variable: API_ID")
if not API_HASH:
    raise ValueError("Missing required environment variable: API_HASH")

SESSION_STRING = os.getenv("SESSION_STRING")
DATABASE_URL = os.getenv("DATABASE_URL")
CHANNEL_CONFIG_PATH = os.getenv("CHANNEL_CONFIG_PATH", "channels.yml")
CHANNEL_CONFIG_POLL = int(os.getenv("CHANNEL_CONFIG_POLL", 30))

_channels_cache = {
    "data": None,
    "last_loaded": 0,
}

def get_channels():
    """
    Loads the channel list from the configured YAML file.
    Caches the result for CHANNEL_CONFIG_POLL seconds to avoid frequent file reads.
    """
    now = time.time()
    if now - _channels_cache["last_loaded"] > CHANNEL_CONFIG_POLL:
        try:
            with open(CHANNEL_CONFIG_PATH, "r") as f:
                data = yaml.safe_load(f)
                _channels_cache["data"] = data.get("channels", [])
                _channels_cache["last_loaded"] = now
        except (yaml.YAMLError, FileNotFoundError) as e:
            print(f"Error loading channel config: {e}. Using cached or empty list.")
            # Reset timer so we don't spam errors, but still use old data if available
            _channels_cache["last_loaded"] = now

    return _channels_cache["data"] or [] 