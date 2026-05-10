# 📚 DictDatabase

A full-stack dictionary application combining **FastAPI** backend with **Streamlit** frontend, powered by the **PONS Dictionary API**. Manage multiple translation profiles, search with intelligent caching, and track your translation history.

---

## ✨ Features

### 🔐 User Management
- **Secure Registration & Login** – Password hashing with bcrypt
- **Email Verification** – Unique email accounts
- **PONS API Key Storage** – Securely store your personal API key

### 🗣️ Translation Profiles
- **Create Multiple Profiles** – Different language pair configurations
- **Language Combinations** – Source, target, and result display languages
- **Profile Management** – Edit, delete, organize your translation setups
- **Quick Profile Switching** – Seamlessly switch between translation contexts

### 🔍 Smart Search
- **PONS API Integration** – Real-time dictionary lookups
- **Intelligent Caching** – Cache search results to reduce API calls
- **Search History** – Track all previous searches per profile
- **Term Suggestions** – Store and retrieve common translations

### 📊 Dashboard
- **Search Interface** – Intuitive profile-based search
- **History Viewer** – Browse past searches and results
- **Statistics** – Overview of your translations and profiles
- **Settings Management** – Configure your account and API key

### 🛡️ Security
- **Password Hashing** – Bcrypt-encrypted passwords
- **Session Management** – Secure Streamlit session handling
- **API Key Protection** – Encrypted API key storage
- **CORS Enabled** – Secure cross-origin requests

---

## 📋 Requirements

- **Python 3.8+**
- **PONS API Key** (free account from [PONS](https://www.pons.com))
- See `requirements.txt` for Python dependencies

---

## 🚀 Quick Start

### 1. Installation

```bash
cd DictDatabase
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `constants.py` to set your configuration (optional):
- Database URL: `SQLALCHEMY_DATABASE_URL`
- CORS origins: `ALLOW_CORS_ORIGINS`
- API base URL: `API_BASE_URL`

### 3. Run the Application

**One Command – Starts Both Backend & Frontend:**
```bash
python run.py
```

Or manually start components separately:

**Backend (FastAPI):**
```bash
uvicorn backend.main:app --reload
```
API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

**Frontend (Streamlit):**
```bash
streamlit run frontend/app.py
```
Web app will open at `http://localhost:8501`

---

## 📁 Project Structure

```
DictDatabase/
├── constants.py                  # Configuration & constants
├── requirements.txt              # Python dependencies
├── run.py                        # Launcher script (starts both services)
│
├── backend/                      # FastAPI backend
│   ├── __init__.py
│   ├── main.py                  # FastAPI app setup
│   ├── database.py              # Database connection setup
│   ├── models.py                # SQLAlchemy data models
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── crud.py                  # Database CRUD operations
│   ├── security.py              # Password hashing utilities
│   │
│   └── routes/                  # API route handlers
│       ├── __init__.py
│       ├── user_routes.py       # Authentication endpoints
│       ├── profile_routes.py    # Profile management endpoints
│       └── search_routes.py     # Search & history endpoints
│
└── frontend/                     # Streamlit frontend
    ├── __init__.py
    ├── app.py                   # Main login/register page
    ├── utils.py                 # Frontend utilities
    │
    └── pages/                   # Multi-page app pages
        ├── Dashboard.py         # Main search interface
        └── Settings.py          # Account & profile settings
```

---

## 🗄️ Database Schema

### Users Table
```sql
users (id, email, name, password, api_key)
```

### Profiles Table
```sql
profiles (id, name, result_lang, source_lang, target_lang, created_at, user_id)
```

### History Table
```sql
history (id, profile_id, term, source_lang, target_lang, json_response)
```

---

## 🔧 API Reference

### Base URL
```
http://localhost:8000
```

### Authentication Endpoints

#### Register User
```http
POST /users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}

Response:
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}
```

#### Login
```http
POST /users/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response:
{
  "user": {...},
  "message": "Login successful"
}
```

#### Update API Key
```http
PUT /users/{user_id}/api-key
Content-Type: application/json

{
  "api_key": "your_pons_api_key"
}
```

### Profile Endpoints

#### List User Profiles
```http
GET /profiles?user_id=1
```

#### Create Profile
```http
POST /profiles
Content-Type: application/json

{
  "user_id": 1,
  "name": "German to English",
  "source_lang": "de",
  "target_lang": "en",
  "result_lang": "en"
}
```

#### Update Profile
```http
PUT /profiles/{profile_id}
Content-Type: application/json

{
  "name": "German → English",
  "source_lang": "de",
  "target_lang": "en"
}
```

#### Delete Profile
```http
DELETE /profiles/{profile_id}?user_id=1
```

### Search Endpoints

#### Perform Search
```http
GET /search?profile_id=1&user_id=1&term=hello
```

Response:
```json
{
  "cached": false,
  "data": {
    "lang": "de",
    "hits": [...]
  }
}
```

#### Get Profile History
```http
GET /profiles/{profile_id}/history
```

---

## 🌍 Supported Languages

The PONS API supports numerous language combinations. Common pairs:

| Code | Language |
|------|----------|
| de | German |
| en | English |
| es | Spanish |
| fr | French |
| it | Italian |
| pl | Polish |
| pt | Portuguese |
| ru | Russian |
| el | Greek |
| tr | Turkish |
| zh | Chinese |

---

## 🔑 Getting Your PONS API Key

1. Visit [PONS.com](https://www.pons.com)
2. Create a free account or log in
3. Navigate to API settings
4. Generate an API key
5. Copy the key and paste it in the app's Settings page

---

## 📝 Configuration Guide

### constants.py Settings

| Setting | Default | Purpose |
|---------|---------|---------|
| `APP_NAME` | "PONS Dictionary Client" | Application display name |
| `DEBUG_MODE` | True | Enable debug logging |
| `API_BASE_URL` | "http://127.0.0.1:8000" | Backend API URL |
| `SQLALCHEMY_DATABASE_URL` | "sqlite:///./langDict.db" | Database connection |
| `ALLOW_CORS_ORIGINS` | ["localhost:8501", "127.0.0.1:8501"] | Allowed frontend origins |
| `PASSWORD_MIN_LENGTH` | 3 | Minimum password length |
| `PASSWORD_MAX_LENGTH` | 72 | Maximum password length (bcrypt limit) |

### Password Requirements

- **Length**: 3-72 characters (configurable)
- **Allowed Characters**: Letters, digits, and special chars: `!@#$%^&*()_-+=[{]};:\'",<.>/?\\|`~`

### Username Requirements

- **Length**: Max 30 characters
- **Allowed Characters**: Letters, digits, underscore, hyphen, dot, space

---

## 🔒 Security Features

### Password Security
- **Bcrypt Hashing** – Industry-standard password hashing
- **Salt Generation** – Unique salt per password
- **Constant-Time Comparison** – Prevents timing attacks

### API Key Security
- **Server-Side Storage** – Keys stored in database, never exposed to frontend
- **HTTPS Ready** – Configure for production SSL/TLS
- **User Isolation** – Each user can only access their own keys

### Session Management
- **Streamlit Sessions** – Browser session isolation
- **User Verification** – Required for sensitive operations
- **CORS Protection** – Restrict cross-origin requests

---

## 🛠️ Development

### Adding a New Route

1. Create a router in `backend/routes/`:
```python
# backend/routes/new_routes.py
from fastapi import APIRouter

router = APIRouter(prefix="/new", tags=["New"])

@router.get("/")
def get_data():
    return {"data": "example"}
```

2. Import in `backend/routes/__init__.py`:
```python
from .new_routes import router
```

3. Register in `backend/main.py`:
```python
for r in routers:
    app.include_router(r)
```

### Adding a New Frontend Page

1. Create in `frontend/pages/`:
```python
# frontend/pages/NewPage.py
import streamlit as st

st.title("New Page")
st.write("Content here...")
```

2. Streamlit automatically adds it to the sidebar navigation

### Database Migrations

To modify the database schema:

1. Update `backend/models.py`
2. Clear the database: `rm langDict.db`
3. Restart app (models will be recreated)

For production, implement alembic migrations.

---

## 🐛 Troubleshooting

### "Connection Refused" on Backend
- Ensure FastAPI is running: `uvicorn backend.main:app --reload`
- Check if port 8000 is available
- Verify `API_BASE_URL` in constants.py

### "Email already registered"
- Use a different email for new account
- Reset database if needed: `rm langDict.db`

### "Invalid or missing API key"
- Verify your PONS API key is correct
- Check API key in Settings page
- Ensure key has not expired
- Confirm key has proper permissions

### "Profile not found"
- Ensure you're using correct profile_id
- Verify profile belongs to logged-in user
- Create a new profile if deleted

### CORS Errors
- Add your frontend URL to `ALLOW_CORS_ORIGINS` in constants.py
- For local development, default settings should work

### Streamlit Cache Issues
- Clear Streamlit cache: `streamlit cache clear`
- Or delete `.streamlit/` folder
- Restart Streamlit app

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.121.0 | Web framework (API) |
| uvicorn | 0.38.0 | ASGI server |
| sqlalchemy | 2.0.44 | ORM database |
| pydantic | 2.12.4 | Data validation |
| passlib | 1.7.4 | Password hashing |
| streamlit | 1.51.0 | Web framework (UI) |
| requests | 2.32.5 | HTTP client |

---

## 🎯 Workflow Example

### 1. Register Account
```
1. Open http://localhost:8501
2. Click "Register new user"
3. Enter email, username, password
4. Click "Register"
```

### 2. Add PONS API Key
```
1. Click Dashboard
2. Go to Settings page
3. Paste your PONS API key
4. Click "Save API Key"
```

### 3. Create Translation Profile
```
1. In Settings, click "Create New Profile"
2. Name: "German to English"
3. Source Language: German
4. Target Language: English
5. Result Language: English
6. Click "Create"
```

### 4. Perform Search
```
1. In Dashboard, select your profile
2. Type a word (e.g., "Katze")
3. Click "Search"
4. View results with translation history
```

### 5. Browse History
```
1. In Dashboard, click "View History"
2. See all previous searches
3. Click on past searches to view full results
```

---

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🔍 Search Caching Strategy

The application implements intelligent caching:

1. **User searches a term** → Check local cache first
2. **If cached** → Return immediately (no API call)
3. **If not cached** → Call PONS API
4. **Store result** → Save in history for future use
5. **Return to user** → Display results

This reduces API calls and improves performance.

---

## 📄 License

This project is a personal application for educational purposes.

---

## 🤝 Contributing

Areas for enhancement:
- Dark mode support
- Advanced search filters
- Pronunciation audio
- Offline dictionary support
- Export search history
- Multiple dictionary providers
- Word frequency analysis
- Spaced repetition for learning

---

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PONS API Documentation](https://en.pons.com/open_dict/public_api)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Happy translating! 📚✨**
