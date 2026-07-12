from pathlib import Path
import os

from dotenv import load_dotenv

try:
    import streamlit as st
    _HAS_STREAMLIT = True
except ImportError:
    _HAS_STREAMLIT = False

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

load_dotenv(BASE_DIR / ".env")


def _get_setting(key: str, default: str = "") -> str:
    """Read a setting from environment first, then Streamlit secrets, then default."""
    value = os.getenv(key)
    if value:
        return value
    if _HAS_STREAMLIT:
        try:
            return st.secrets.get(key, default)
        except Exception:
            return default
    return default


def _reload_env() -> None:
    load_dotenv(BASE_DIR / ".env", override=True)


def get_mongodb_uri() -> str:
    _reload_env()
    return _get_setting("MONGODB_URI", "mongodb://localhost:27017")


def get_mongodb_db_name() -> str:
    _reload_env()
    return _get_setting("MONGODB_DB_NAME", "healthcare_agent")


def get_use_llm() -> bool:
    _reload_env()
    return _get_setting("USE_LLM", "false").lower() == "true"


def get_llm_provider() -> str:
    _reload_env()
    return _get_setting("LLM_PROVIDER", "groq").lower()


def get_openai_api_key() -> str:
    _reload_env()
    return _get_setting("OPENAI_API_KEY", "")


def get_groq_api_key() -> str:
    _reload_env()
    return _get_setting("GROQ_API_KEY", "")


def get_google_api_key() -> str:
    _reload_env()
    return _get_setting("GOOGLE_API_KEY", "")


MONGODB_URI = _get_setting("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = _get_setting("MONGODB_DB_NAME", "healthcare_agent")

# Optional Indian health platform API settings.
ONE_MG_API_URL = _get_setting("ONE_MG_API_URL", "")
ONE_MG_API_KEY = _get_setting("ONE_MG_API_KEY", "")
PRACTO_API_URL = _get_setting("PRACTO_API_URL", "")
PRACTO_API_KEY = _get_setting("PRACTO_API_KEY", "")
AYURVEDA_API_URL = _get_setting("AYURVEDA_API_URL", "")
AYURVEDA_API_KEY = _get_setting("AYURVEDA_API_KEY", "")

USE_LLM = _get_setting("USE_LLM", "false").lower() == "true"
LLM_PROVIDER = _get_setting("LLM_PROVIDER", "groq").lower()
OPENAI_API_KEY = _get_setting("OPENAI_API_KEY", "")
GROQ_API_KEY = _get_setting("GROQ_API_KEY", "")

GOOGLE_API_KEY = _get_setting("GOOGLE_API_KEY", "")
WEATHERSTACK_API_KEY = _get_setting("WEATHERSTACK_API_KEY", "")
EXCHANGERATE_API_KEY = _get_setting("EXCHANGERATE_API_KEY", "")
SERP_API_KEY = _get_setting("SERP_API_KEY", "")
