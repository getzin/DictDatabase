# constants.py
from datetime import timedelta
import re

# ========================
# App
# ========================
APP_NAME = "PONS Dictionary Client"
DEBUG_MODE = True

# ========================
# API
# ========================
API_BASE_URL = "http://127.0.0.1:8000"


# ========================
# Database
# ========================
SQLALCHEMY_DATABASE_URL = "sqlite:///./langDict.db"

# ========================
# CORS
# ========================
ALLOW_CORS_ORIGINS = ["http://localhost:8501", "http://127.0.0.1:8501"]

# ========================
# Users / Auth
# ========================
EMAIL_MAX_LENGTH = 255
USERNAME_MAX_LENGTH = 30
USERNAME_ALLOWED_CHARS_REGEX = re.compile(r"^[A-Za-z0-9_\-\. ]+$")  # letters, digits, underscore, hyphen, dot, space

# Password (bcrypt-safe)
PASSWORD_MIN_LENGTH = 3   # testing
PASSWORD_MAX_LENGTH = 72
PASSWORD_ALLOWED_CHARS_REGEX = re.compile(
    r"^[A-Za-z0-9!@#$%^&*()_\-+=\[{\]};:'\",<.>/?\\|`~]+$"
)
# Note: length is validated separately with PASSWORD_MIN_LENGTH / PASSWORD_MAX_LENGTH

# API key
API_KEY_MAX_LENGTH = 64  # based on example

# ========================
# Profiles & Search
# ========================
PROFILE_NAME_MAX_LENGTH = 30
SEARCH_TERM_MAX_LENGTH = 50
LANG_CODE_MAX_LENGTH = 2

# Cache validity for search results
CACHE_VALID_FOR = timedelta(minutes=1)  # dev/testing
# Alternatives:
# CACHE_VALID_FOR = timedelta(hours=1)
# CACHE_VALID_FOR = timedelta(days=1)
# CACHE_VALID_FOR = timedelta(weeks=1)
# CACHE_VALID_FOR = timedelta(days=30)   # ~1 month
# CACHE_VALID_FOR = timedelta(days=365)  # ~1 year

# History cap (we will enforce this on insert)
MAX_HISTORY_ENTRIES_PER_PROFILE = 1000

# ========================
# Languages (codes -> names)
# ========================
LANGUAGES = {
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "it": "Italian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ru": "Russian",
    "sl": "Slovenian",
    "tr": "Turkish",
    "zh": "Chinese",
}

# Defaults (codes)
DEFAULT_RESULT_LANG = "en"
DEFAULT_SOURCE_LANG = "en"
DEFAULT_TARGET_LANG = "de"
