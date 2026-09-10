import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "postgresql://fittracker:fittracker@localhost:5432/fittracker"
)
APP_PORT: int = int(os.getenv("APP_PORT", "8080"))
APP_ENV: str = os.getenv("APP_ENV", "development")
