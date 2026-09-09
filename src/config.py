import os

from dotenv import load_dotenv

load_dotenv()

MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME: str = os.getenv("DB_NAME", "fittracker")
APP_PORT: int = int(os.getenv("APP_PORT", "8080"))
