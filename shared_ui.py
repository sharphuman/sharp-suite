"""
Sharp Suite - Shared UI Components (Clean Corporate Edition)
=============================================================
Simple, consistent styling that works everywhere.
"""

import streamlit as st

# ===========================================
# APP CONFIGURATION
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
# COLORS - Simple Corporate Palette
# ===========================================

COLORS = {
    # Core colors
    "bg": "#0f0f0f",           # Near black background
    "bg_secondary": "#1a1a1a", # Slightly lighter for cards
    "bg_input": "#252525",     # Input fields
    
    # Brand colors
    "pink": "#db2777",         # Primary accent (pink)
    "pink_hover": "#be185d",   # Pink hover state
    "blue": "#3b82f6",         # Secondary accent
    
    # Text
    "text": "#ffffff",         # Primary text
    "text_secondary": "#a1a1a1", # Secondary text
    "text_muted": "#6b6b6b",   # Muted text
    
    # Borders
    "border": "#2a2a2a",       # Standard border
    "border_light": "#3a3a3a", # Lighter border
}


# ===========================================
# GLOBAL CSS - Applied to ALL apps
# ===========================================

def get_global_css():
    """Returns CSS that creates consistent styling across all apps."""
    return f"""
    <style>
    /* ===== FONTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}
    
    /* ===== MAIN BACKGROUND ===== */
    .stApp, 
    [data-testid="stAppViewContainer"],
    .main .block-container {{
        background: {COLORS['bg']} !important;
    }}
    
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}
    
    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {{
        background: {COLORS['bg']} !important;
        border-right: 1px solid {COLORS['border']} !important;
    }}
    
    section[data-testid="stSidebar"] > div {{
        background: {COLORS['bg']} !important;
    }}
    
    /* Hide default sidebar nav */
    section[data-testid="stSidebar"] > div > div:first-child > div:first-child {{
        display: none !important;
    }}
    
    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['text']} !important;
        font-weight: 600 !important;
    }}
    
    p, span, label, div {{
        color: {COLORS['text_secondary']} !important;
    }}
    
    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    [data-baseweb="select"] > div {{
        background: {COLORS['bg_input']} !important;
        border: 1px solid {COLORS['border']} !important;
        color: {COLORS['text']} !important;
        border-radius: 6px !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS['pink']} !important;
        box-shadow: 0 0 0 1px {COLORS['pink']} !important;
    }}
    
    /* ===== BUTTONS ===== */
    .stButton > button {{
        background: {COLORS['pink']} !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: background 0.2s !important;
    }}
    
    .stButton > button:hover {{
        background: {COLORS['pink_hover']} !important;
    }}
    
    /* Secondary/outline buttons */
    .stButton > button[kind="secondary"] {{
        background: transparent !important;
        border: 1px solid {COLORS['border']} !important;
        color: {COLORS['text']} !important;
    }}
    
    /* Download buttons */
    .stDownloadButton > button {{
        background: {COLORS['bg_input']} !important;
        border: 1px solid {COLORS['border']} !important;
        color: {COLORS['text']} !important;
    }}
    
    /* Link buttons in sidebar */
    .stLinkButton > a {{
        background: {COLORS['bg_secondary']} !important;
        border: 1px solid {COLORS['border']} !important;
        color: {COLORS['text']} !important;
        border-radius: 6px !important;
        text-decoration: none !important;
        font-weight: 500 !important;
    }}
    
    .stLinkButton > a:hover {{
        border-color: {COLORS['pink']} !important;
        color: {COLORS['pink']} !important;
    }}
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {{
        background: transparent !important;
        gap: 0 !important;
        border-bottom: 1px solid {COLORS['border']} !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: {COLORS['text_secondary']} !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.75rem 1rem !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {COLORS['text']} !important;
        border-bottom: 2px solid {COLORS['pink']} !important;
    }}
    
    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {{
        background: {COLORS['bg_input']} !important;
        border: 1px dashed {COLORS['border']} !important;
        border-radius: 6px !important;
    }}
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {{
        background: {COLORS['bg_secondary']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 6px !important;
    }}
    
    /* ===== POPOVER (Feedback button fix) ===== */
    div[data-testid="stPopover"] > div > div > div {{
        background: {COLORS['bg_secondary']} !important;
    }}
    
    div[data-testid="stPopover"] button {{
        background: {COLORS['pink']} !important;
        border-radius: 20px !important;
    }}
    
    /* Hide "expand_more" text bug */
    div[data-testid="stPopover"] button span:last-child {{
        display: none !important;
    }}
    
    /* ===== DIVIDERS ===== */
    hr {{
        border-color: {COLORS['border']} !important;
    }}
    
    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {{
        color: {COLORS['text']} !important;
    }}
    
    /* ===== MULTISELECT TAGS ===== */
    [data-baseweb="tag"] {{
        background: {COLORS['pink']} !important;
    }}
    
    </style>
    """


def apply_global_styles():
    """Apply consistent global CSS to the app."""
    st.markdown(get_global_css(), unsafe_allow_html=True)


# ===========================================
# TOP BANNER - Consistent button style
# ===========================================

def render_top_banner(show_cta: bool = True, cta_text: str = "Book a Demo", cta_url: str = None):
    """Render consistent top banner with styled buttons."""
    st.markdown(f"""
    <style>
    .top-banner {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid {COLORS['border']};
    }}
    .top-banner-left {{
        display: flex;
        gap: 10px;
    }}
    .top-banner-right {{
        display: flex;
        gap: 10px;
    }}
    .btn {{
        display: inline-block;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        text-decoration: none;
        transition: all 0.2s;
    }}
    .btn-pink {{
        background: {COLORS['pink']};
        color: white !important;
    }}
    .btn-pink:hover {{
        background: {COLORS['pink_hover']};
    }}
    .btn-outline {{
        background: transparent;
        border: 1px solid {COLORS['border']};
        color: {COLORS['text']} !important;
    }}
    .btn-outline:hover {{
        border-color: {COLORS['pink']};
        color: {COLORS['pink']} !important;
    }}
    .btn-outline-pink {{
        background: transparent;
        border: 1px solid {COLORS['pink']};
        color: {COLORS['pink']} !important;
    }}
    .btn-outline-pink:hover {{
        background: {COLORS['pink']};
        color: white !important;
    }}
    </style>
    
    <div class="top-banner">
        <div class="top-banner-left">
            <a href="{EXTERNAL_LINKS['bespoke']}" target="_blank" class="btn btn-pink">Bespoke Services</a>
            <a href="{EXTERNAL_LINKS['blog']}" target="_blank" class="btn btn-pink">Blog</a>
            <a href="{EXTERNAL_LINKS['demo']}" target="_blank" class="btn btn-outline">Book a Demo</a>
        </div>
        <div class="top-banner-right">
            <a href="{EXTERNAL_LINKS['consultation']}" target="_blank" class="btn btn-outline-pink">Book a Free AI Consultation</a>
            <a href="{EXTERNAL_LINKS['website']}" target="_blank" class="btn btn-pink">sharphuman.com</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ===========================================
# SIDEBAR - Consistent navigation
# ===========================================

def render_sidebar(
    current_app: str,
    user_email: str = "User",
    user_plan: str = "free",
    session_token: str = ""
):
    """Render consistent sidebar with navigation."""
    
    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="text-align: center; padding: 16px 0; border-bottom: 1px solid {COLORS['border']}; margin-bottom: 16px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width: 40px; margin-bottom: 8px;">
            <div style="color: {COLORS['text']}; font-weight: 600; font-size: 15px;">Sharp Suite</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Account info
        plan_bg = COLORS['pink'] if user_plan == 'god' else COLORS['bg_input']
        plan_color = 'white' if user_plan == 'god' else COLORS['pink']
        
        st.markdown(f"""
        <div style="padding: 12px; background: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border']}; border-radius: 8px; margin-bottom: 16px;">
            <div style="color: {COLORS['text_muted']}; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">Account</div>
            <div style="color: {COLORS['text']}; font-weight: 500; font-size: 13px; margin-bottom: 6px;">{user_email}</div>
            <span style="background: {plan_bg}; color: {plan_color}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase;">{user_plan}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation label
        st.markdown(f"""
        <div style="color: {COLORS['text_muted']}; font-size: 11px; text-transform: uppercase; margin: 0 0 8px 4px;">
            🧭 Navigation
        </div>
        """, unsafe_allow_html=True)
        
        # App buttons
        for app_key, icon, label in APP_LABELS:
            url = f"{APP_URLS.get(app_key, '')}?token={session_token}" if session_token else APP_URLS.get(app_key, "")
            
            if app_key == current_app:
                # Current app - pink highlight
                st.markdown(f"""
                <div style="
                    background: {COLORS['pink']};
                    padding: 10px 14px;
                    border-radius: 6px;
                    margin: 4px 0;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                ">
                    <span style="color: white; font-weight: 500;">{icon} {label}</span>
                    <span style="color: rgba(255,255,255,0.7);">◀</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.link_button(f"{icon} {label}", url, use_container_width=True)
        
        # Admin link for god users
        if user_plan == "god":
            st.markdown("---")
            admin_url = f"{APP_URLS.get('admin', '')}?token={session_token}" if session_token else APP_URLS.get('admin', "")
            st.link_button("⚙️ Admin Dashboard", admin_url, use_container_width=True)
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ===========================================
# APP HEADER - Consistent title styling
# ===========================================

def render_app_header(title: str, subtitle: str, icon_url: str = "https://sharphuman.com/logo1-3.png"):
    """Render consistent app header."""
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 16px; padding: 16px 0; border-bottom: 1px solid {COLORS['border']}; margin-bottom: 24px;">
        <img src="{icon_url}" style="width: 48px; height: 48px;">
        <div>
            <h1 style="margin: 0; font-size: 24px; color: {COLORS['text']};">{title}</h1>
            <p style="margin: 0; color: {COLORS['text_secondary']}; font-size: 14px;">{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ===========================================
# FEEDBACK WIDGET
# ===========================================

def render_feedback_widget(app_name: str):
    """Render feedback button (fixes the expand_more bug)."""
    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
    with col4:
        with st.popover("💬 Feedback"):
            st.markdown("**Send Feedback**")
            fb_type = st.radio("Type", ["🐛 Bug", "✨ Feature", "💬 General"], horizontal=True, label_visibility="collapsed")
            fb_msg = st.text_area("Message", height=100, placeholder="Your feedback...", label_visibility="collapsed")
            if st.button("Send", type="primary", use_container_width=True):
                if fb_msg:
                    # TODO: Connect to feedback submission
                    st.success("Thanks! 🙏")


# ===========================================
# STATUS INDICATOR (Loading spinner)
# ===========================================

def show_loading(message: str = "Working..."):
    """Show loading status with spinner."""
    st.markdown(f"""
    <div style="
        position: fixed;
        top: 70px;
        right: 20px;
        background: {COLORS['pink']};
        color: white;
        padding: 10px 20px;
        border-radius: 20px;
        font-weight: 500;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 10px;
    ">
        <div style="
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
        {message}
    </div>
    <style>
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)


# ===========================================
# GOOGLE ANALYTICS
# ===========================================

def inject_ga4(measurement_id: str = "G-XXXXXXXXXX"):
    """Inject Google Analytics 4 tracking."""
    if measurement_id and measurement_id != "G-XXXXXXXXXX":
        st.markdown(f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());
            gtag('config', '{measurement_id}');
        </script>
        """, unsafe_allow_html=True)
