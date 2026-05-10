# frontend/pages/Settings.py
import streamlit as st
import requests
from constants import API_BASE_URL, API_KEY_MAX_LENGTH, PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH, APP_NAME, LANGUAGES, PROFILE_NAME_MAX_LENGTH
from utils import logout_user
from utils import require_login_message

st.set_page_config(page_title=f"{APP_NAME} - Settings", layout="centered")

st.title("⚙️ User Settings")

# Retrieve user info from session
if "user" not in st.session_state or not st.session_state["user"]:
    require_login_message()
    st.stop()

user = st.session_state["user"]
st.write(f"Logged in as **{user['name']} ({user['email']})**")


# --- Update API Key ---
st.subheader("🔑 Update API Key")
api_key = user.get("api_key")

if api_key:
    show_full = st.checkbox("Show full API key", value=False)
    if show_full:
        st.text_input("Current API key", api_key, type="default", disabled=True)
    else:
        st.write(f"Current API key: `{api_key[:6]}...`")
else:
    st.info("No API key set yet.")

new_api_key = st.text_input("Enter new API key", type="password", max_chars=API_KEY_MAX_LENGTH)
if st.button("Save API Key"):
    if not new_api_key.strip():
        st.error("API key cannot be empty.")
    else:
        response = requests.post(
            f"{API_BASE_URL}/users/update-api-key",
            json={"user_id": user["id"], "api_key": new_api_key.strip()},
        )
        if response.status_code == 200:
            st.success("API key updated successfully!")
            st.session_state["user"]["api_key"] = new_api_key.strip()
        else:
            st.error(response.json().get("detail", "Failed to update API key."))


st.markdown("---")


# --- Change Password ---
st.subheader("🔐 Change Password")

old_pass = st.text_input("Old password", type="password", key="old_pass")
new_pass = st.text_input("New password", type="password", key="new_pass", max_chars=PASSWORD_MAX_LENGTH)
confirm_pass = st.text_input("Confirm new password", type="password", key="confirm_pass")

if st.button("Change Password"):
    if not old_pass or not new_pass or not confirm_pass:
        st.error("Please fill in all password fields.")
    elif len(new_pass) < PASSWORD_MIN_LENGTH or len(new_pass) > PASSWORD_MAX_LENGTH:
        st.error(f"Password must be between {PASSWORD_MIN_LENGTH} and {PASSWORD_MAX_LENGTH} characters.")
    elif new_pass != confirm_pass:
        st.error("New passwords do not match.")
    else:
        response = requests.post(
            f"{API_BASE_URL}/users/change-password",
            json={
                "user_id": user["id"],
                "old_password": old_pass,
                "new_password": new_pass,
                "confirm_password": confirm_pass,
            },
        )
        if response.status_code == 200:
            st.success("Password changed successfully!")
        else:
            st.error(response.json().get("detail", "Failed to change password."))


st.markdown("---")

st.header("👤 Profile Management")

# --- Fetch profiles ---
response = requests.get(f"{API_BASE_URL}/profiles", params={"user_id": user["id"]})
if response.status_code == 200:
    profiles = response.json()
else:
    profiles = []

st.write(f"Profiles: **{len(profiles)}**")

# --- Create new profile ---
with st.expander("➕ Create New Profile", expanded=False):
    name = st.text_input("Profile name", max_chars=PROFILE_NAME_MAX_LENGTH, key="new_profile_name")
    result_lang = st.selectbox("Result language", options=list(LANGUAGES.values()), key="new_result_lang")
    source_lang = st.selectbox("Source language", options=list(LANGUAGES.values()), key="new_source_lang")
    target_lang = st.selectbox("Target language", options=list(LANGUAGES.values()), key="new_target_lang")

    if st.button("Create Profile"):
        if not name.strip():
            st.error("Profile name cannot be empty.")
        else:
            # Convert readable names to codes
            lang_codes = {v: k for k, v in LANGUAGES.items()}
            data = {
                "user_id": user["id"],
                "name": name.strip(),
                "result_lang": lang_codes[result_lang],
                "source_lang": lang_codes[source_lang],
                "target_lang": lang_codes[target_lang],
            }
            r = requests.post(f"{API_BASE_URL}/profiles", json=data)
            if r.status_code == 200:
                st.success("Profile created successfully!")
                st.rerun()
            else:
                st.error("Failed to create profile.")

# --- Existing profiles list ---
if profiles:
    st.subheader("Existing Profiles")

    # Create a reverse lookup dict for readable language names
    lang_names = LANGUAGES

    for p in profiles:
        # Convert codes (like 'en', 'de') to readable names (like 'English', 'German') + Fallback
        result_name = lang_names.get(p["result_lang"], p["result_lang"])
        source_name = lang_names.get(p["source_lang"], p["source_lang"])
        target_name = lang_names.get(p["target_lang"], p["target_lang"])

        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"**{p['name']}** — {source_name} → {target_name} ({result_name})")
        with col2:
            if st.button("🗑️", key=f"delete_{p['id']}"):
                del_res = requests.delete(
                    f"{API_BASE_URL}/profiles/{p['id']}",
                    params={"user_id": user["id"]},
                    timeout=10
                )
                if del_res.status_code == 200:
                    st.success(f"Deleted profile: {p['name']}")
                    st.rerun()
                else:
                    try:
                        st.error(del_res.json().get("detail", "Failed to delete profile."))
                    except Exception:
                        st.error("Failed to delete profile.")
else:
    st.info("No profiles found yet.")

# Navigation
if st.button("⬅️ Back to Dashboard"):
    st.switch_page("pages/Dashboard.py")


st.markdown("---")

if st.button("🚪 Logout"):
    logout_user()