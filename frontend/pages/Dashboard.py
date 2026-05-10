# frontend/pages/Dashboard.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
from constants import (
    APP_NAME, API_BASE_URL,
    PROFILE_NAME_MAX_LENGTH, LANGUAGES,
    DEFAULT_RESULT_LANG, DEFAULT_SOURCE_LANG, DEFAULT_TARGET_LANG,
)
from utils import logout_user, require_login_message, render_pons_result
import json

st.set_page_config(page_title=f"{APP_NAME} - Dashboard", layout="centered")

# --- Session check (require login) ---
if "user" not in st.session_state or not st.session_state["user"]:
    require_login_message()
    st.stop()
user = st.session_state["user"]

# --- Header (title + logout) ---
col1, col2 = st.columns([6, 1])
with col1:
    st.title(f"👋 Welcome, {user['name']}!")
with col2:
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()

# ----------------------------
# API helpers
# ----------------------------
def api_list_profiles(user_id: int):
    try:
        r = requests.get(f"{API_BASE_URL}/profiles", params={"user_id": user_id}, timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except Exception:
        return []

def api_create_profile(user_id: int, name: str, result_lang: str, source_lang: str, target_lang: str):
    payload = {
        "user_id": user_id,
        "name": name,
        "result_lang": result_lang,
        "source_lang": source_lang,
        "target_lang": target_lang,
    }
    try:
        r = requests.post(f"{API_BASE_URL}/profiles", json=payload, timeout=15)
        return r
    except Exception:
        return None

def api_delete_profile(profile_id: int, user_id: int):
    try:
        r = requests.delete(f"{API_BASE_URL}/profiles/{profile_id}", params={"user_id": user_id}, timeout=10)
        return r
    except Exception:
        return None

# Fetch current profiles from backend
profiles = api_list_profiles(user["id"])

# ----------------------------
# Onboarding overlay
# ----------------------------
missing_api_key = not user.get("api_key")
missing_profiles = len(profiles) == 0

if missing_api_key or missing_profiles:
    with st.expander("⚙️ Let's finish your setup", expanded=True):
        st.write("Before you can start using the dictionary, please complete the steps below:")

        # Step 1: API Key setup
        if missing_api_key:
            st.subheader("🔑 Add your API Key")
            st.info("You need an API key to use the PONS Dictionary API.")
            new_api_key = st.text_input("Enter your API key", type="password")
            if st.button("Save API key"):
                if not new_api_key.strip():
                    st.error("API key cannot be empty.")
                else:
                    resp = requests.post(
                        f"{API_BASE_URL}/users/update-api-key",
                        json={"user_id": user["id"], "api_key": new_api_key.strip()},
                        timeout=15,
                    )
                    if resp is not None and resp.status_code == 200:
                        st.success("API key saved successfully!")
                        st.session_state["user"]["api_key"] = new_api_key.strip()
                        st.rerun()
                    else:
                        try:
                            detail = resp.json().get("detail", "Failed to update API key.")
                        except Exception:
                            detail = "Failed to update API key."
                        st.error(detail)

        # Step 2: Create first profile
        if missing_profiles:
            st.subheader("👤 Create your first profile")
            st.info("Profiles store your language preferences and history.")

            name = st.text_input("Profile name", max_chars=PROFILE_NAME_MAX_LENGTH)
            lang_codes = list(LANGUAGES.keys())
            d_code = st.selectbox(
                "Result language",
                options=lang_codes,
                index=max(0, lang_codes.index(DEFAULT_RESULT_LANG)) if DEFAULT_RESULT_LANG in lang_codes else 0,
                format_func=lambda c: f"{c} — {LANGUAGES[c]}",
                key="disp_lang_select",
            )
            s_code = st.selectbox(
                "Source language",
                options=lang_codes,
                index=max(0, lang_codes.index(DEFAULT_SOURCE_LANG)) if DEFAULT_SOURCE_LANG in lang_codes else 0,
                format_func=lambda c: f"{c} — {LANGUAGES[c]}",
                key="src_lang_select",
            )
            t_code = st.selectbox(
                "Target language",
                options=lang_codes,
                index=max(0, lang_codes.index(DEFAULT_TARGET_LANG)) if DEFAULT_TARGET_LANG in lang_codes else 0,
                format_func=lambda c: f"{c} — {LANGUAGES[c]}",
                key="tgt_lang_select",
            )

            if st.button("Create Profile"):
                clean_name = (name or "").strip()
                if not clean_name:
                    st.error("Profile name cannot be empty.")
                else:
                    resp = api_create_profile(user["id"], clean_name, d_code, s_code, t_code)
                    if resp is not None and resp.status_code == 200:
                        st.success(f"Profile '{clean_name}' created successfully!")
                        st.rerun()
                    else:
                        try:
                            detail = resp.json().get("detail", "Failed to create profile.")
                        except Exception:
                            detail = "Failed to create profile."
                        st.error(detail)

    st.stop()  # Block normal dashboard until setup complete

# ----------------------------
# Main Dashboard (after setup)
# ----------------------------
st.subheader("🧭 Dashboard")
st.write("Everything looks good! You're ready to use the PONS Dictionary Client.")

# --- Profile selector ---
if profiles:
    st.subheader("🧭 Active Profile")
    profile_labels = [
        f"{p['name']} ({p['source_lang']} → {p['target_lang']}, {p['result_lang']})"
        for p in profiles
    ]
    selected_profile = st.selectbox("Select a profile", profile_labels)
    profile = profiles[profile_labels.index(selected_profile)]
    st.session_state["active_profile"] = profile
    st.success(f"Active profile: **{selected_profile}**")
else:
    st.warning("No profiles found. Please create one in Settings.")
    st.stop()

st.markdown("---")

# =====================================================
# 🔍 SEARCH + HISTORY SECTION
# =====================================================
st.subheader("📜 Search History")

# --- Fetch history ---
def fetch_history(pid: int):
    r = requests.get(f"{API_BASE_URL}/search/history/{pid}")
    return r.json() if r.status_code == 200 else []

history = fetch_history(profile["id"])

# --- Delete one history item helper ---
def delete_history_item(term):
    res = requests.delete(f"{API_BASE_URL}/search/history/{profile['id']}/{term}")
    if res.status_code == 200:
        st.success(f"Deleted '{term}' from history.")
        st.rerun()
    else:
        st.error(f"Failed to delete '{term}'.")

# --- Clear entire history ---
def clear_history():
    res = requests.delete(f"{API_BASE_URL}/search/history/{profile['id']}")
    if res.status_code == 200:
        st.success("History cleared successfully.")
        st.rerun()
    else:
        st.error("Failed to clear history.")

# --- Show history items ---
if history:
    cols = st.columns([8, 2])
    with cols[0]:
        st.markdown("##### Previous searches:")
    with cols[1]:
        confirm_clear = st.checkbox("⚠️ Confirm clear all", key="confirm_clear")
        if st.button("🗑️ Clear History", disabled=not confirm_clear):
            clear_history()

    for h in history:
        term = h["term"]
        col1, col2 = st.columns([10, 1])
        with col1:
            if st.button(term, key=f"hist_{h['id']}"):
                st.session_state["pending_term"] = term
                st.rerun()
        with col2:
            if st.button("❌", key=f"del_{h['id']}"):
                delete_history_item(term)
else:
    st.info("No search history yet.")

st.markdown("---")
st.subheader("🔎 New Search")

# --- Perform search helper ---
def perform_search(term):
    with st.spinner("Searching..."):
        term = term.strip()
        if not term:
            st.warning("Please enter a search term.")
            return

        cached_entry = next((h for h in history if h["term"].lower() == term.lower()), None)
        if cached_entry and "json_response" in cached_entry:
            try:
                st.session_state["search_result"] = json.loads(cached_entry["json_response"])
            except Exception:
                st.session_state["search_result"] = cached_entry["json_response"]
            st.info("Loaded from local history cache ✅")
            return

        params = {"profile_id": profile["id"], "user_id": user["id"], "term": term}
        r = requests.get(f"{API_BASE_URL}/search", params=params)
        if r.status_code == 200:
            data = r.json()
            st.session_state["search_result"] = data
            st.success("Search completed!")
            st.rerun()
        else:
            try:
                detail = r.json().get("detail", "")
            except Exception:
                detail = ""
            if r.status_code == 403:
                st.error("❌ Invalid API key. Please check your key in Settings.")
            elif r.status_code == 404:
                st.warning("⚠️ No dictionary available for that language pair.")
            else:
                st.error(f"Search failed ({r.status_code}) {detail}")

# --- Auto-fill search field + trigger search from history click ---
if "pending_term" in st.session_state:
    preset_term = st.session_state.pop("pending_term")
    st.session_state["search_term"] = preset_term
    perform_search(preset_term)
    preset_term = st.session_state["search_term"]  # keep field populated
else:
    preset_term = st.session_state.get("search_term", "")

# --- Input triggers search on Enter ---
search_term = st.text_input(
    "Enter a term to look up",
    value=preset_term,
    key="search_term",
    on_change=lambda: perform_search(st.session_state["search_term"]),
)

# --- Manual trigger button ---
if st.button("Search"):
    perform_search(search_term)

# --- Show result if available ---
if "search_result" in st.session_state:
    data = st.session_state["search_result"]
    if isinstance(data, dict) and "data" in data:
        render_pons_result(data["data"])
    else:
        render_pons_result(data)
    with st.expander("🧾 Raw API Response (click to expand)", expanded=False):
        st.json(data)

st.markdown("---")

# Navigation
left, right = st.columns(2)
with left:
    if st.button("⚙️ Go to Settings"):
        st.switch_page("pages/Settings.py")
with right:
    if st.button("🚪 Logout"):
        logout_user()
