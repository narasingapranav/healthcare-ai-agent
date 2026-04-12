from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

load_dotenv(BASE_DIR / ".env")


def _reload_env() -> None:
	load_dotenv(BASE_DIR / ".env", override=True)


def get_mongodb_uri() -> str:
	_reload_env()
	return os.getenv("MONGODB_URI", "mongodb://localhost:27017")


def get_mongodb_db_name() -> str:
	_reload_env()
	return os.getenv("MONGODB_DB_NAME", "healthcare_agent")


def get_use_llm() -> bool:
	_reload_env()
	return os.getenv("USE_LLM", "false").lower() == "true"


def get_llm_provider() -> str:
	_reload_env()
	return os.getenv("LLM_PROVIDER", "groq").lower()


def get_openai_api_key() -> str:
	_reload_env()
	return os.getenv("OPENAI_API_KEY", "")


def get_groq_api_key() -> str:
	_reload_env()
	return os.getenv("GROQ_API_KEY", "")


def get_google_api_key() -> str:
	_reload_env()
	return os.getenv("GOOGLE_API_KEY", "")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "healthcare_agent")

# Optional Indian health platform API settings.
ONE_MG_API_URL = os.getenv("ONE_MG_API_URL", "")
ONE_MG_API_KEY = os.getenv("ONE_MG_API_KEY", "")
PRACTO_API_URL = os.getenv("PRACTO_API_URL", "")
PRACTO_API_KEY = os.getenv("PRACTO_API_KEY", "")
AYURVEDA_API_URL = os.getenv("AYURVEDA_API_URL", "")
AYURVEDA_API_KEY = os.getenv("AYURVEDA_API_KEY", "")

USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY", "")
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY", "")
SERP_API_KEY = os.getenv("SERP_API_KEY", "")
