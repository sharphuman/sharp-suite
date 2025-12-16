"""
Sharp Suite - Shared UI (Minimal SaaS Edition)
===============================================
Clean, professional SaaS interface. No backgrounds, no gradients.
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
    "bespoke": "https://sharphuman.com#services",
    "blog": "https://sharphuman.com/blog",
    "demo": "https://calendly.com/sharphuman/30min",
    "consultation": "https://calendly.com/sharphuman/60min",
    "website": "https://sharphuman.com",
}

# ===========================================
# COLORS - Clean SaaS Palette
# ===========================================

# Dark mode (like Salesforce dark theme)
COLORS = {
    # Backgrounds
    "bg_main": "#1e1e1e",        # Main content area
    "bg_sidebar": "#141414",      # Darker sidebar
    "bg_header": "#141414",       # Header bar
    "bg_card": "#262626",         # Cards/containers
    "bg_input": "#2d2d2d",        # Input fields
    "bg_hover": "#333333",        # Hover states
    
    # Brand accent
    "primary": "#0176d3",         # Salesforce blue
    "primary_hover": "#014486",
    "accent": "#1b96ff",          # Lighter blue for highlights
    
    # Text
    "text_primary": "#ffffff",
    "text_secondary": "#b0b0b0",
    "text_muted": "#707070",
    
    # Borders
    "border": "#3d3d3d",
    "border_light": "#4a4a4a",
    
    # Status
    "success": "#2e844a",
    "warning": "#dd7a01",
    "error": "#c23934",
}


# ===========================================
# MASTER CSS
# ===========================================

def get_master_css():
    return f"""
<style>
/* ========== RESET & FONTS ========== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, *::before, *::after {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    box-sizing: border-box;
}}

/* ========== MAIN LAYOUT ========== */
.stApp {{
    background: {COLORS['bg_main']} !important;
}}

[data-testid="stAppViewContainer"] {{
    background: {COLORS['bg_main']} !important;
}}

[data-testid="stHeader"] {{
    background: {COLORS['bg_header']} !important;
    border-bottom: 1px solid {COLORS['border']} !important;
}}

.main .block-container {{
    background: {COLORS['bg_main']} !important;
    padding-top: 2rem !important;
    max-width: 1200px !important;
}}

/* ========== SIDEBAR ========== */
section[data-testid="stSidebar"] {{
    background: {COLORS['bg_sidebar']} !important;
    border-right: 1px solid {COLORS['border']} !important;
}}

section[data-testid="stSidebar"] > div {{
    background: {COLORS['bg_sidebar']} !important;
    padding-top: 0 !important;
}}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: 0.5rem !important;
}}

/* Hide Streamlit's default sidebar header */
section[data-testid="stSidebar"] > div > div:first-child > div:first-child {{
    display: none !important;
}}

/* ========== TYPOGRAPHY ========== */
h1 {{
    color: {COLORS['text_primary']} !important;
    font-size: 1.75rem !important;
    font-weight: 600 !important;
    margin-bottom: 0.5rem !important;
}}

h2 {{
    color: {COLORS['text_primary']} !important;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
}}

h3, h4, h5, h6 {{
    color: {COLORS['text_primary']} !important;
    font-weight: 600 !important;
}}

p, span, label, div {{
    color: {COLORS['text_secondary']} !important;
}}

a {{
    color: {COLORS['accent']} !important;
    text-decoration: none !important;
}}

a:hover {{
    text-decoration: underline !important;
}}

/* ========== INPUTS ========== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {COLORS['bg_input']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 4px !important;
    color: {COLORS['text_primary']} !important;
    padding: 0.5rem 0.75rem !important;
}}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 0 0 1px {COLORS['primary']} !important;
}}

.stSelectbox > div > div,
[data-baseweb="select"] > div {{
    background: {COLORS['bg_input']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 4px !important;
}}

[data-baseweb="select"] span {{
    color: {COLORS['text_primary']} !important;
}}

/* ========== BUTTONS ========== */
.stButton > button {{
    background: {COLORS['primary']} !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    font-size: 0.875rem !important;
    transition: background 0.15s ease !important;
}}

.stButton > button:hover {{
    background: {COLORS['primary_hover']} !important;
}}

.stDownloadButton > button {{
    background: {COLORS['bg_card']} !important;
    color: {COLORS['text_primary']} !important;
    border: 1px solid {COLORS['border']} !important;
}}

/* Sidebar link buttons */
.stLinkButton > a {{
    background: transparent !important;
    color: {COLORS['text_secondary']} !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.625rem 0.75rem !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    transition: background 0.15s ease !important;
}}

.stLinkButton > a:hover {{
    background: {COLORS['bg_hover']} !important;
    color: {COLORS['text_primary']} !important;
    text-decoration: none !important;
}}

/* ========== TABS ========== */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid {COLORS['border']} !important;
    gap: 0 !important;
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {COLORS['text_secondary']} !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.75rem 1rem !important;
    font-weight: 500 !important;
}}

.stTabs [data-baseweb="tab"]:hover {{
    color: {COLORS['text_primary']} !important;
}}

.stTabs [aria-selected="true"] {{
    color: {COLORS['primary']} !important;
    border-bottom: 2px solid {COLORS['primary']} !important;
}}

/* ========== FILE UPLOADER ========== */
[data-testid="stFileUploader"] {{
    background: {COLORS['bg_card']} !important;
    border: 1px dashed {COLORS['border']} !important;
    border-radius: 4px !important;
}}

[data-testid="stFileUploader"] label {{
    color: {COLORS['text_secondary']} !important;
}}

/* ========== EXPANDERS ========== */
.streamlit-expanderHeader {{
    background: {COLORS['bg_card']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 4px !important;
    color: {COLORS['text_primary']} !important;
}}

/* ========== METRICS ========== */
[data-testid="stMetricValue"] {{
    color: {COLORS['text_primary']} !important;
}}

[data-testid="stMetricLabel"] {{
    color: {COLORS['text_secondary']} !important;
}}

/* ========== MULTISELECT TAGS ========== */
[data-baseweb="tag"] {{
    background: {COLORS['primary']} !important;
    color: white !important;
}}

/* ========== RADIO/CHECKBOX ========== */
.stRadio > div {{
    gap: 0.5rem !important;
}}

.stRadio label, .stCheckbox label {{
    color: {COLORS['text_secondary']} !important;
}}

/* ========== DIVIDERS ========== */
hr {{
    border-color: {COLORS['border']} !important;
}}

/* ========== POPOVER FIX ========== */
div[data-testid="stPopover"] button {{
    background: {COLORS['primary']} !important;
    border-radius: 4px !important;
}}

div[data-testid="stPopover"] button span:last-child {{
    display: none !important;
}}

/* ========== SLIDERS ========== */
.stSlider [data-baseweb="slider"] div {{
    background: {COLORS['primary']} !important;
}}

</style>
"""


def apply_global_styles():
    """Apply the master CSS to the app."""
    st.markdown(get_master_css(), unsafe_allow_html=True)


# ===========================================
# HEADER BAR
# ===========================================

def render_top_banner(show_cta: bool = True, cta_text: str = "Book a Demo", cta_url: str = None):
    """Render clean top header bar."""
    st.markdown(f"""
<style>
.top-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid {COLORS['border']};
}}
.top-header-left {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}
.top-header-right {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
}}
.header-btn {{
    display: inline-flex;
    align-items: center;
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
    font-weight: 500;
    border-radius: 4px;
    text-decoration: none !important;
    transition: all 0.15s ease;
}}
.header-btn-primary {{
    background: {COLORS['primary']};
    color: white !important;
}}
.header-btn-primary:hover {{
    background: {COLORS['primary_hover']};
}}
.header-btn-outline {{
    background: transparent;
    color: {COLORS['text_secondary']} !important;
    border: 1px solid {COLORS['border']};
}}
.header-btn-outline:hover {{
    background: {COLORS['bg_hover']};
    color: {COLORS['text_primary']} !important;
}}
</style>

<div class="top-header">
    <div class="top-header-left">
        <a href="{EXTERNAL_LINKS['bespoke']}" target="_blank" class="header-btn header-btn-primary">Services</a>
        <a href="{EXTERNAL_LINKS['blog']}" target="_blank" class="header-btn header-btn-outline">Blog</a>
    </div>
    <div class="top-header-right">
        <a href="{EXTERNAL_LINKS['demo']}" target="_blank" class="header-btn header-btn-outline">Book Demo</a>
        <a href="{EXTERNAL_LINKS['website']}" target="_blank" class="header-btn header-btn-primary">sharphuman.com</a>
    </div>
</div>
""", unsafe_allow_html=True)


# ===========================================
# SIDEBAR
# ===========================================

def render_sidebar(
    current_app: str,
    user_email: str = "User",
    user_plan: str = "free",
    session_token: str = ""
):
    """Render clean sidebar navigation."""
    
    with st.sidebar:
        # Logo/Brand
        st.markdown(f"""
<div style="
    padding: 1.25rem 1rem;
    border-bottom: 1px solid {COLORS['border']};
    margin-bottom: 1rem;
">
    <div style="
        display: flex;
        align-items: center;
        gap: 0.75rem;
    ">
        <div style="
            width: 32px;
            height: 32px;
            background: {COLORS['primary']};
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 14px;
        ">S</div>
        <span style="
            color: {COLORS['text_primary']};
            font-weight: 600;
            font-size: 1rem;
        ">Sharp Suite</span>
    </div>
</div>
""", unsafe_allow_html=True)
        
        # User info
        plan_display = user_plan.upper()
        st.markdown(f"""
<div style="
    padding: 0.75rem 1rem;
    background: {COLORS['bg_card']};
    border-radius: 6px;
    margin: 0 0.5rem 1rem;
">
    <div style="color: {COLORS['text_primary']}; font-size: 0.875rem; font-weight: 500;">{user_email}</div>
    <div style="color: {COLORS['text_muted']}; font-size: 0.75rem; margin-top: 0.25rem;">{plan_display} Plan</div>
</div>
""", unsafe_allow_html=True)
        
        # Navigation
        for app_key, icon, label in APP_LABELS:
            url = f"{APP_URLS.get(app_key, '')}?token={session_token}" if session_token else APP_URLS.get(app_key, "")
            
            if app_key == current_app:
                # Active state
                st.markdown(f"""
<div style="
    background: {COLORS['primary']};
    color: white;
    padding: 0.625rem 1rem;
    border-radius: 4px;
    margin: 0.25rem 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
">
    <span>{icon}</span>
    <span>{label}</span>
</div>
""", unsafe_allow_html=True)
            else:
                st.link_button(f"{icon} {label}", url, use_container_width=True)
        
        # Spacer
        st.markdown("<div style='flex: 1; min-height: 2rem;'></div>", unsafe_allow_html=True)
        
        # Logout
        st.markdown(f"<hr style='margin: 1rem 0.5rem; border-color: {COLORS['border']};'>", unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ===========================================
# APP HEADER
# ===========================================

def render_app_header(title: str, subtitle: str = ""):
    """Render clean app title header."""
    st.markdown(f"""
<div style="margin-bottom: 1.5rem;">
    <h1 style="
        color: {COLORS['text_primary']};
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0 0 0.25rem 0;
    ">{title}</h1>
    <p style="
        color: {COLORS['text_muted']};
        font-size: 0.875rem;
        margin: 0;
    ">{subtitle}</p>
</div>
""", unsafe_allow_html=True)


# ===========================================
# UTILITIES
# ===========================================

def render_feedback_widget(app_name: str = "app"):
    """Render feedback button."""
    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
    with col4:
        with st.popover("💬 Feedback"):
            st.markdown("**Send Feedback**")
            fb_type = st.radio("Type", ["Bug", "Feature", "Other"], horizontal=True)
            fb_msg = st.text_area("Message", placeholder="Your feedback...")
            if st.button("Submit", type="primary", use_container_width=True):
                if fb_msg:
                    st.success("Thanks for your feedback!")


def inject_ga4(measurement_id: str = ""):
    """Inject Google Analytics (if configured)."""
    pass  # Placeholder


# For backwards compatibility
def render_header(*args, **kwargs):
    """Deprecated - use render_app_header instead."""
    pass
