"""
Sharp Suite - Shared UI (ServiceNow Style)
==========================================
Single source of truth for ALL styling.
No app should have its own CSS.
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

# ===========================================
# DESIGN TOKENS (ServiceNow Dark Theme)
# ===========================================

COLORS = {
    # Backgrounds - ServiceNow dark mode
    "bg_page": "#1c1c1c",
    "bg_sidebar": "#161616", 
    "bg_card": "#232323",
    "bg_input": "#2a2a2a",
    "bg_hover": "#333333",
    
    # Primary - ServiceNow green/teal
    "primary": "#62d84e",
    "primary_dark": "#4aa83a",
    
    # Secondary - Blue for links
    "secondary": "#78b4e8",
    
    # Text
    "text_white": "#ffffff",
    "text_light": "#d4d4d4",
    "text_muted": "#8c8c8c",
    "text_dark": "#666666",
    
    # Borders
    "border": "#404040",
    "border_light": "#4a4a4a",
    
    # Status
    "success": "#62d84e",
    "warning": "#f5c518",
    "error": "#ff6b6b",
    "info": "#78b4e8",
}

SPACING = {
    "xs": "0.25rem",
    "sm": "0.5rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem",
}

# ===========================================
# COMPLETE CSS RESET + STYLING
# ===========================================

def apply_global_styles():
    """Apply complete styling. This is the ONLY CSS source."""
    
    css = f"""
<style>
/* ============================================
   COMPLETE CSS RESET FOR SHARP SUITE
   ============================================ */

/* Google Font */
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap');

/* Universal Reset */
*, *::before, *::after {{
    font-family: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, sans-serif !important;
    box-sizing: border-box !important;
}}

/* ============================================
   PAGE LAYOUT
   ============================================ */

/* Main app container */
.stApp {{
    background: {COLORS['bg_page']} !important;
}}

[data-testid="stAppViewContainer"] {{
    background: {COLORS['bg_page']} !important;
}}

/* Top header bar */
[data-testid="stHeader"] {{
    background: {COLORS['bg_sidebar']} !important;
    border-bottom: 1px solid {COLORS['border']} !important;
    height: 48px !important;
}}

/* Main content area */
.main .block-container {{
    background: {COLORS['bg_page']} !important;
    padding: {SPACING['lg']} {SPACING['xl']} !important;
    max-width: 1400px !important;
}}

/* ============================================
   SIDEBAR
   ============================================ */

section[data-testid="stSidebar"] {{
    background: {COLORS['bg_sidebar']} !important;
    width: 240px !important;
}}

section[data-testid="stSidebar"] > div {{
    background: {COLORS['bg_sidebar']} !important;
    padding: 0 !important;
}}

section[data-testid="stSidebar"] > div > div:first-child > div:first-child {{
    display: none !important;
}}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: 2px !important;
}}

/* ============================================
   TYPOGRAPHY
   ============================================ */

h1 {{
    color: {COLORS['text_white']} !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    margin: 0 0 {SPACING['sm']} 0 !important;
    line-height: 1.3 !important;
}}

h2 {{
    color: {COLORS['text_white']} !important;
    font-size: 1.125rem !important;
    font-weight: 600 !important;
    margin: {SPACING['md']} 0 {SPACING['sm']} 0 !important;
}}

h3, h4, h5, h6 {{
    color: {COLORS['text_white']} !important;
    font-weight: 600 !important;
}}

p {{
    color: {COLORS['text_light']} !important;
    font-size: 0.875rem !important;
    line-height: 1.5 !important;
}}

span, label, div {{
    color: {COLORS['text_light']} !important;
}}

a {{
    color: {COLORS['secondary']} !important;
    text-decoration: none !important;
}}

a:hover {{
    text-decoration: underline !important;
}}

/* ============================================
   FORM INPUTS
   ============================================ */

/* Text inputs */
.stTextInput > div > div > input {{
    background: {COLORS['bg_input']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 3px !important;
    color: {COLORS['text_white']} !important;
    font-size: 0.875rem !important;
    padding: 8px 12px !important;
    height: 36px !important;
}}

.stTextInput > div > div > input:focus {{
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 0 0 1px {COLORS['primary']} !important;
}}

.stTextInput > div > div > input::placeholder {{
    color: {COLORS['text_muted']} !important;
}}

/* Text areas */
.stTextArea > div > div > textarea {{
    background: {COLORS['bg_input']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 3px !important;
    color: {COLORS['text_white']} !important;
    font-size: 0.875rem !important;
    padding: 8px 12px !important;
}}

.stTextArea > div > div > textarea:focus {{
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 0 0 1px {COLORS['primary']} !important;
}}

/* Select boxes */
.stSelectbox > div > div,
[data-baseweb="select"] > div {{
    background: {COLORS['bg_input']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 3px !important;
}}

[data-baseweb="select"] span {{
    color: {COLORS['text_white']} !important;
    font-size: 0.875rem !important;
}}

/* Labels */
.stTextInput label,
.stTextArea label,
.stSelectbox label {{
    color: {COLORS['text_light']} !important;
    font-size: 0.8125rem !important;
    font-weight: 600 !important;
    margin-bottom: 4px !important;
}}

/* ============================================
   BUTTONS
   ============================================ */

/* Primary buttons */
.stButton > button {{
    background: {COLORS['primary']} !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 3px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 8px 16px !important;
    height: 36px !important;
    transition: background 0.15s !important;
}}

.stButton > button:hover {{
    background: {COLORS['primary_dark']} !important;
}}

/* Download buttons */
.stDownloadButton > button {{
    background: {COLORS['bg_card']} !important;
    color: {COLORS['text_white']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 3px !important;
    font-size: 0.875rem !important;
}}

/* Link buttons (sidebar nav) */
.stLinkButton > a {{
    background: transparent !important;
    color: {COLORS['text_light']} !important;
    border: none !important;
    border-radius: 3px !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
    padding: 10px 16px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    transition: background 0.1s !important;
}}

.stLinkButton > a:hover {{
    background: {COLORS['bg_hover']} !important;
    color: {COLORS['text_white']} !important;
    text-decoration: none !important;
}}

/* ============================================
   TABS
   ============================================ */

.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid {COLORS['border']} !important;
    gap: 0 !important;
    padding: 0 !important;
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {COLORS['text_muted']} !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    padding: 12px 16px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}}

.stTabs [data-baseweb="tab"]:hover {{
    color: {COLORS['text_white']} !important;
}}

.stTabs [aria-selected="true"] {{
    color: {COLORS['text_white']} !important;
    border-bottom-color: {COLORS['primary']} !important;
}}

/* ============================================
   FILE UPLOADER
   ============================================ */

[data-testid="stFileUploader"] {{
    background: {COLORS['bg_card']} !important;
    border: 1px dashed {COLORS['border']} !important;
    border-radius: 3px !important;
    padding: 16px !important;
}}

[data-testid="stFileUploader"] label {{
    color: {COLORS['text_light']} !important;
}}

[data-testid="stFileUploader"] button {{
    background: {COLORS['bg_input']} !important;
    border: 1px solid {COLORS['border']} !important;
    color: {COLORS['text_white']} !important;
}}

/* ============================================
   RADIO & CHECKBOX
   ============================================ */

.stRadio > div {{
    gap: 8px !important;
}}

.stRadio label,
.stCheckbox label {{
    color: {COLORS['text_light']} !important;
    font-size: 0.875rem !important;
}}

/* ============================================
   MULTISELECT TAGS
   ============================================ */

[data-baseweb="tag"] {{
    background: {COLORS['primary']} !important;
    color: #000000 !important;
    border-radius: 3px !important;
    font-size: 0.8125rem !important;
}}

/* ============================================
   SLIDERS
   ============================================ */

.stSlider [data-baseweb="slider"] {{
    margin-top: 8px !important;
}}

.stSlider [data-baseweb="slider"] div[role="slider"] {{
    background: {COLORS['primary']} !important;
}}

/* ============================================
   EXPANDERS
   ============================================ */

.streamlit-expanderHeader {{
    background: {COLORS['bg_card']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 3px !important;
    color: {COLORS['text_white']} !important;
    font-size: 0.875rem !important;
}}

/* ============================================
   METRICS
   ============================================ */

[data-testid="stMetricValue"] {{
    color: {COLORS['text_white']} !important;
    font-size: 1.5rem !important;
}}

[data-testid="stMetricLabel"] {{
    color: {COLORS['text_muted']} !important;
}}

/* ============================================
   DIVIDERS
   ============================================ */

hr {{
    border: none !important;
    border-top: 1px solid {COLORS['border']} !important;
    margin: {SPACING['md']} 0 !important;
}}

/* ============================================
   POPOVER (Feedback button fix)
   ============================================ */

div[data-testid="stPopover"] button {{
    background: {COLORS['primary']} !important;
    color: #000000 !important;
    border-radius: 3px !important;
}}

div[data-testid="stPopover"] button span:last-child {{
    display: none !important;
}}

/* ============================================
   DATAFRAMES / TABLES
   ============================================ */

.stDataFrame {{
    border: 1px solid {COLORS['border']} !important;
    border-radius: 3px !important;
}}

/* ============================================
   ALERTS / INFO BOXES
   ============================================ */

.stAlert {{
    background: {COLORS['bg_card']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 3px !important;
}}

</style>
"""
    st.markdown(css, unsafe_allow_html=True)


# ===========================================
# TOP HEADER BAR
# ===========================================

def render_top_banner(show_cta: bool = True, cta_text: str = "Book Demo", cta_url: str = None):
    """Render top navigation bar."""
    
    st.markdown(f"""
<style>
.sharp-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    margin-bottom: 24px;
    border-bottom: 1px solid {COLORS['border']};
}}
.sharp-header-nav {{
    display: flex;
    gap: 8px;
}}
.sharp-header-btn {{
    display: inline-block;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 3px;
    text-decoration: none !important;
    transition: all 0.15s;
}}
.sharp-header-btn-primary {{
    background: {COLORS['primary']};
    color: #000 !important;
}}
.sharp-header-btn-primary:hover {{
    background: {COLORS['primary_dark']};
}}
.sharp-header-btn-ghost {{
    background: transparent;
    color: {COLORS['text_light']} !important;
    border: 1px solid {COLORS['border']};
}}
.sharp-header-btn-ghost:hover {{
    background: {COLORS['bg_hover']};
    color: {COLORS['text_white']} !important;
}}
</style>

<div class="sharp-header">
    <div class="sharp-header-nav">
        <a href="{EXTERNAL_LINKS['services']}" target="_blank" class="sharp-header-btn sharp-header-btn-primary">Services</a>
        <a href="{EXTERNAL_LINKS['blog']}" target="_blank" class="sharp-header-btn sharp-header-btn-ghost">Blog</a>
    </div>
    <div class="sharp-header-nav">
        <a href="{EXTERNAL_LINKS['demo']}" target="_blank" class="sharp-header-btn sharp-header-btn-ghost">Book Demo</a>
        <a href="{EXTERNAL_LINKS['website']}" target="_blank" class="sharp-header-btn sharp-header-btn-primary">sharphuman.com</a>
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
    """Render sidebar navigation."""
    
    with st.sidebar:
        # Brand header
        st.markdown(f"""
<div style="padding: 16px; border-bottom: 1px solid {COLORS['border']};">
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="
            width: 28px; height: 28px;
            background: {COLORS['primary']};
            border-radius: 4px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 13px; color: #000;
        ">S</div>
        <span style="color: {COLORS['text_white']}; font-weight: 600; font-size: 15px;">Sharp Suite</span>
    </div>
</div>
""", unsafe_allow_html=True)
        
        # User info
        st.markdown(f"""
<div style="padding: 12px 16px; background: {COLORS['bg_card']}; margin: 12px 8px; border-radius: 4px;">
    <div style="color: {COLORS['text_white']}; font-size: 13px; font-weight: 500;">{user_email}</div>
    <div style="color: {COLORS['text_muted']}; font-size: 11px; margin-top: 2px;">{user_plan.upper()} Plan</div>
</div>
""", unsafe_allow_html=True)
        
        # Navigation
        st.markdown(f"<div style='padding: 0 8px; margin-bottom: 8px;'><span style='color: {COLORS['text_muted']}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;'>Navigation</span></div>", unsafe_allow_html=True)
        
        for app_key, icon, label in APP_LABELS:
            url = f"{APP_URLS.get(app_key, '')}?token={session_token}" if session_token else APP_URLS.get(app_key, "")
            
            if app_key == current_app:
                st.markdown(f"""
<div style="
    background: {COLORS['primary']};
    color: #000;
    padding: 10px 16px;
    margin: 2px 8px;
    border-radius: 3px;
    font-size: 14px;
    font-weight: 500;
">{icon} {label}</div>
""", unsafe_allow_html=True)
            else:
                st.link_button(f"{icon} {label}", url, use_container_width=True)
        
        # Logout
        st.markdown(f"<hr style='margin: 16px 8px; border-color: {COLORS['border']};'>", unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ===========================================
# APP HEADER
# ===========================================

def render_app_header(title: str, subtitle: str = ""):
    """Simple app title."""
    subtitle_html = f"<p style='color: {COLORS['text_muted']}; font-size: 14px; margin: 0;'>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
<div style="margin-bottom: 24px;">
    <h1 style="color: {COLORS['text_white']}; font-size: 24px; font-weight: 600; margin: 0 0 4px 0;">{title}</h1>
    {subtitle_html}
</div>
""", unsafe_allow_html=True)


# ===========================================
# UTILITIES
# ===========================================

def render_feedback_widget(app_name: str = ""):
    """Feedback button."""
    col1, col2, col3, col4 = st.columns([6, 1, 1, 1])
    with col4:
        with st.popover("💬"):
            st.markdown("**Feedback**")
            fb_msg = st.text_area("Message", placeholder="Your feedback...", label_visibility="collapsed")
            if st.button("Send", use_container_width=True):
                if fb_msg:
                    st.success("Thanks!")


def inject_ga4(measurement_id: str = ""):
    """GA placeholder."""
    pass


def render_header(*args, **kwargs):
    """Deprecated."""
    pass
