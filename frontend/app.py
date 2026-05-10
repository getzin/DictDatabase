# frontend/app.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
from constants import API_BASE_URL, APP_NAME, PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH
from utils import logout_user

st.set_page_config(page_title=APP_NAME, layout="centered")
st.title(APP_NAME)
st.markdown("<br>", unsafe_allow_html=True)

# --- Setup for toggle state ---
if "user" in st.session_state and st.session_state["user"]:
    st.success(f"Welcome back, {st.session_state['user']['name']}!")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/Dashboard.py")
    if st.button("Logout"):
        logout_user()
    st.stop()

# --- Login/Register tabs ---
if "tab_choice" not in st.session_state:
    st.session_state["tab_choice"] = "Login"

tab_choice = st.radio(
    "Choose an option:",
    ["Login", "Register new user"],
    horizontal=True,
    index=0 if st.session_state["tab_choice"] == "Login" else 1,
)

# keep session state in sync
st.session_state["tab_choice"] = tab_choice

st.markdown(
    """
    <style>

    /* layout */
    div[role="radiogroup"] {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }

    /* default tab look */
    div[role="radiogroup"] label {
        background-color: #3a3b3c;          /* dark-friendly gray */
        color: #f2f2f2;
        border: 1px solid #555;
        border-radius: 0.5rem;
        padding: 0.4rem 1.2rem;#
        cursor: default;
        text-decoration: none !important;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    /* hover */
    div[role="radiogroup"] label:hover {
        background-color: #4c4d50;
    }

    /* active / selected tab */
    div[role="radiogroup"] input:checked + div {
        color: white !important;
        border-color: #1e90ff !important;
    }

    /* light-theme fallback */
    @media (prefers-color-scheme: light) {
        div[role="radiogroup"] label {
            background-color: #f0f2f6;
            color: #111;
            border-color: #ccc;
        }
        div[role="radiogroup"] label:hover {
            background-color: #e3e6ea;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- LOGIN FORM ---
if tab_choice == "Login":
    st.subheader("🔐 Login")

    # Show registration success message if coming from register
    if st.session_state.get("registration_success"):
        st.success("Registration successful — please log in below.")
        st.session_state["registration_success"] = False

    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        submit = st.form_submit_button("Login now")
        if submit:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                response = requests.post(f"{API_BASE_URL}/users/login", json={"email": email, "password": password})
                if response.status_code == 200:
                    user_data = response.json()
                    st.session_state["user"] = user_data
                    st.success(f"Welcome, {user_data['name']}!")
                    st.switch_page("pages/Dashboard.py")
                else:
                    try:
                        detail = response.json().get("detail", "Login failed.")
                    except Exception:
                        detail = f"Login failed ({response.status_code})"
                    st.error(detail)

# --- REGISTER FORM ---
else:
    st.subheader("🆕 Register")

    with st.form("register_form"):
        email = st.text_input("Email", key="reg_email")
        name = st.text_input("Name", key="reg_name")

        # keep password fields together for smoother tabbing
        password = st.text_input(
            "Password",
            type="password",
            key="reg_pass",
            max_chars=PASSWORD_MAX_LENGTH,
        )
        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            key="reg_pass_confirm",
            max_chars=PASSWORD_MAX_LENGTH,
        )

        submit = st.form_submit_button("Register now")
        if submit:
            if not name or not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < PASSWORD_MIN_LENGTH or len(password) > PASSWORD_MAX_LENGTH:
                st.error(f"Password must be between {PASSWORD_MIN_LENGTH} and {PASSWORD_MAX_LENGTH} characters.")
            else:
                payload = {
                    "name": name,
                    "email": email,
                    "password": password,
                    "password_confirm": confirm_password,
                }
                response = requests.post(f"{API_BASE_URL}/users/register", json=payload)
                if response.status_code == 200:
                    st.session_state["tab_choice"] = "Login"
                    st.session_state["registration_success"] = True
                    st.rerun()
                else:
                    try:
                        detail = response.json().get("detail", "Registration failed.")
                    except Exception:
                        detail = f"Registration failed ({response.status_code})."
                    st.error(detail)
