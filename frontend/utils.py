# frontend/utils.py
import streamlit as st
import re

def logout_user():
    """Unified logout logic for all frontend pages."""
    name = st.session_state.get("user", {}).get("name", "User")

    # Clear session data
    st.session_state.clear()

    # Show goodbye message
    st.success(f"Goodbye, {name}!")

    # Force back to login
    st.session_state["tab_choice"] = "Login"

    # Rerun app.py so it actually shows login screen
    st.switch_page("app.py")

def require_login_message():
    st.warning("Please log in first.")
    if st.button("🔐 Go to Login / Register page"):
        # Use JS redirect to same tab (Streamlit-safe)
        st.markdown(
            """
            <meta http-equiv="refresh" content="0; url='/'" />
            """,
            unsafe_allow_html=True
        )

# ===============================================
# PONS RESULT RENDERER (Enhanced)
# ===============================================

def _clean_html(raw_html: str) -> str:
    """Remove basic HTML tags and replace <br> with line breaks."""
    if not raw_html:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", raw_html)
    text = re.sub(r"<.*?>", "", text)
    return text.strip()


def render_pons_result(json_data):
    """Pretty renderer for PONS API results with grouping, examples, and notes."""
    if not json_data or not isinstance(json_data, list):
        st.info("No results found.")
        return

    for entry in json_data:
        lang = entry.get("lang", "")
        hits = entry.get("hits", [])
        if not hits:
            continue

        for hit in hits:
            for rom_entry in hit.get("roms", []):
                headword = _clean_html(rom_entry.get("headword", ""))
                st.markdown(f"## 🟢 {headword} ({lang})")

                arabs = rom_entry.get("arabs", [])
                for arab in arabs:
                    header = _clean_html(arab.get("header", ""))  # usually part of speech
                    if header:
                        st.markdown(f"### ✳️ {header}")

                    translations = arab.get("translations", [])
                    if translations:
                        for t in translations:
                            src = _clean_html(t.get("source", ""))
                            tgt = _clean_html(t.get("target", ""))
                            if src and tgt:
                                st.markdown(f"• **{src}** → _{tgt}_")

                    # Grammar or attribute notes (often small hints like "pl", "f", "adj")
                    attrs = arab.get("attrs", [])
                    if attrs:
                        st.markdown(
                            f"<small>📘 {'; '.join(_clean_html(a) for a in attrs)}</small>",
                            unsafe_allow_html=True,
                        )

                    # Example sentences (if provided)
                    examples = arab.get("examples", [])
                    if examples:
                        st.markdown("**Examples:**")
                        for ex in examples:
                            src_ex = _clean_html(ex.get("source", ""))
                            tgt_ex = _clean_html(ex.get("target", ""))
                            if src_ex and tgt_ex:
                                st.markdown(
                                    f"<small>💬 {src_ex} → _{tgt_ex}_</small>",
                                    unsafe_allow_html=True,
                                )

                    st.markdown("---")