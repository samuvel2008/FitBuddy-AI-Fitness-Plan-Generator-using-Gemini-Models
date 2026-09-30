import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'fitbuddy.db'}")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

# The documentation used Gemini 1.5 Pro/Flash. Model names are configurable
# because Google can retire/rename models over time.
GEMINI_WORKOUT_MODEL = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-2.5-flash")
GEMINI_NUTRITION_MODEL = os.getenv("GEMINI_NUTRITION_MODEL", "gemini-2.5-flash")

ADMIN_KEY = os.getenv("ADMIN_KEY", "").strip()
APP_ENV = os.getenv("APP_ENV", "development")
