import os
from pathlib import Path
from dotenv import load_dotenv


dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

USERNAME = os.environ["GPS_TRACKER_USERNAME"]
PASSWORD = os.environ["GPS_TRACKER_PASSWORD"]
SECRET_KEY = os.environ["GPS_TRACKER_KEY"]

VALID_USERNAME_PASSWORD_PAIRS = {
    USERNAME: PASSWORD
}