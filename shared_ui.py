"""
Sharp Suite - Shared UI (MINIMAL - No Custom CSS)
==================================================
Pure Streamlit defaults. No styling overrides.
"""

import streamlit as st

# ===========================================
# CONFIGURATION
# ===========================================

APP_URLS = {
    "portal": "https://demo.sharphuman.com",
    "jd": "https://jd.sharphuman.com",
    "screen": "https://screen.sharphuman.com",
    "interview": "https://interview.sharphuman.com",
    "outreach": "https://outreach.sharphuman.com",
    "content": "https://content.sharphuman.com",
    "sales": "https://sales.sharphuman.com",
    "admin": "https://admin.sharphuman.com",
}

APP_LABELS = [
    ("portal", "🏠", "Portal"),
    ("jd", "📝", "JD Writer"),
    ("screen", "🔍", "CV Screener"),
    ("interview", "🎯", "Interview"),
    ("outreach", "🚀", "Outreach"),
    ("content", "✍️", "Content"),
    ("sales", "💰", "Sales"),
]

EXTERNAL_LINKS = {
    "services": "https://sharphuman.com#services",
    "blog": "https://sharphuman.com/blog",
    "demo": "https://calendly.com/sharphuman/30min",
    "website": "https://sharphuman.com",
}

# Colors for reference (not used for styling)
COLORS = {
    "primary": "#ff4b4b",  # Streamlit default red
    "success": "#21c354",
    "warning": "#faca2b", 
    "error": "#ff4b4b",
}


def apply_global_styles():
    """No-op - using Streamlit defaults."""
    pass


def render_top_banner(show_cta: bool = True, cta_text: str = "Book Demo", cta_url: str = None):
    """Simple text links for navigation."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.link_button("🔧 Services", EXTERNAL_LINKS["services"])
    with col2:
        st.link_button("📝 Blog", EXTERNAL_LINKS["blog"])
    with col3:
        st.link_button("📅 Book Demo", EXTERNAL_LINKS["demo"])
    with col4:
        st.link_button("🌐 sharphuman.com", EXTERNAL_LINKS["website"])
    st.divider()


def render_sidebar(
    current_app: str,
    user_email: str = "User",
    user_plan: str = "free",
    session_token: str = ""
):
    """Simple sidebar with Streamlit components only."""
    
    with st.sidebar:
        st.title("Sharp Suite")
        
        st.divider()
        
        # User info
        st.caption("ACCOUNT")
        st.write(f"**{user_email}**")
        st.write(f"Plan: {user_plan.upper()}")
        
        st.divider()
        
        # Navigation
        st.caption("NAVIGATION")
        
        for app_key, icon, label in APP_LABELS:
            url = f"{APP_URLS.get(app_key, '')}?token={session_token}" if session_token else APP_URLS.get(app_key, "")
            
            if app_key == current_app:
                st.success(f"{icon} **{label}** ◀")
            else:
                st.link_button(f"{icon} {label}", url, use_container_width=True)
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def render_app_header(title: str, subtitle: str = ""):
    """Simple header using Streamlit components."""
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def render_feedback_widget(app_name: str = ""):
    """Simple feedback using expander."""
    with st.expander("💬 Feedback"):
        msg = st.text_area("Your feedback", label_visibility="collapsed")
        if st.button("Send Feedback"):
            if msg:
                st.success("Thanks!")


def inject_ga4(measurement_id: str = ""):
    """Placeholder."""
    pass


def render_header(*args, **kwargs):
    """Deprecated - use render_app_header."""
    pass
