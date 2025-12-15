"""
Sharp Suite - Shared UI Components & Styles
=============================================
Central source of truth for all UI elements.
Import this in every app for consistent look & feel.

Usage in any app.py:
    from shared_ui import (
        apply_global_styles,
        render_top_banner,
        render_header,
        render_sidebar,
        render_feedback_widget,
        StatusIndicator,
        show_status
    )
"""

import streamlit as st
import time
from datetime import datetime

# Try to import from shared_config, fallback to defaults
try:
    from shared_config import APP_URLS, GOD_PASSWORD
except ImportError:
    APP_URLS = {
        "portal": "https://demo.sharphuman.com", "jd": "https://jd.sharphuman.com",
        "screen": "https://screen.sharphuman.com", "interview": "https://hire.sharphuman.com",
        "source": "https://outreach.sharphuman.com", "content": "https://content.sharphuman.com",
        "sales": "https://sales.sharphuman.com", "reach": "https://reach.sharphuman.com",
        "assistant": "https://assistant.sharphuman.com", "admin": "https://admin.sharphuman.com",
    }
    GOD_PASSWORD = "G0DHum@n101!!!"

# ===========================================
# EXTERNAL LINKS (for top banner)
# ===========================================
EXTERNAL_LINKS = {
    "website": "https://sharphuman.com",
    "website_label": "Bespoke Services",
    "blog": "https://sharphuman.com/blog",
    "calendly": "https://calendly.com/sharphuman/60min",
    "contact": "https://sharphuman.com/contact",
}

# ===========================================
# DESIGN TOKENS (Single Source of Truth)
# ===========================================

COLORS = {
    # Primary palette - Blue for app buttons
    "primary": "#3b82f6",
    "primary_light": "#60a5fa",
    "primary_dark": "#2563eb",
    "secondary": "#8b5cf6",
    
    # Pink/Magenta for highlights and top banner
    "pink": "#db2777",
    "pink_light": "#ec4899",
    "pink_dark": "#be185d",
    
    # Background - ALL dark gray like website
    "bg_dark": "#1a1a1a",
    "bg_card": "#1a1a1a",
    "bg_sidebar": "#1a1a1a",
    "bg_input": "#2a2a2a",
    "bg_hover": "#333333",
    "bg_banner": "#1a1a1a",
    
    # Text
    "text_primary": "#ffffff",
    "text_secondary": "#e5e5e5",
    "text_muted": "#9ca3af",
    "text_dim": "#6b7280",
    
    # Status colors
    "success": "#10b981",
    "warning": "#eab308",
    "error": "#ef4444",
    "info": "#3b82f6",
    
    # Borders
    "border": "rgba(255, 255, 255, 0.1)",
    "border_light": "rgba(255, 255, 255, 0.15)",
    "border_card": "rgba(255, 255, 255, 0.1)",
}

TYPOGRAPHY = {
    "font_family": "'Nunito', sans-serif",
    "font_import": "https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap",
    
    # Font sizes
    "size_xs": "11px",
    "size_sm": "13px",
    "size_base": "15px",
    "size_lg": "17px",
    "size_xl": "20px",
    "size_2xl": "24px",
    "size_3xl": "30px",
    "size_4xl": "36px",
}

SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
}

# ===========================================
# GLOBAL CSS STYLES
# ===========================================

def get_global_css():
    """Returns the global CSS that should be applied to all apps."""
    return f"""
    <style>
    /* ========== FONT IMPORT ========== */
    @import url('{TYPOGRAPHY["font_import"]}');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    
    /* ========== GLOBAL RESET ========== */
    *, *::before, *::after {{
        font-family: {TYPOGRAPHY["font_family"]} !important;
    }}
    
    /* ========== BACKGROUND - Unified dark like website ========== */
    .stApp, [data-testid="stAppViewContainer"], .main {{
        background: {COLORS["bg_dark"]} !important;
    }}
    
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}
    
    /* ========== SIDEBAR - With subtle border ========== */
    section[data-testid="stSidebar"] {{
        background: {COLORS["bg_dark"]} !important;
        border-right: 1px solid {COLORS["border_card"]} !important;
    }}
    
    section[data-testid="stSidebar"] > div {{
        background: {COLORS["bg_dark"]} !important;
    }}
    
    /* Hide default sidebar collapse button */
    section[data-testid="stSidebar"] > div > div:first-child > div:first-child {{
        display: none !important;
    }}
    
    /* ========== CARDS & CONTAINERS ========== */
    .input-card, [data-testid="stExpander"] {{
        background: {COLORS["bg_card"]} !important;
        border: 1px solid {COLORS["border_card"]} !important;
        border-radius: 12px !important;
    }}
    
    /* ========== TYPOGRAPHY ========== */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS["text_primary"]} !important;
        font-weight: 700 !important;
    }}
    
    h1 {{ font-size: {TYPOGRAPHY["size_3xl"]} !important; }}
    h2 {{ font-size: {TYPOGRAPHY["size_2xl"]} !important; }}
    h3 {{ font-size: {TYPOGRAPHY["size_xl"]} !important; }}
    
    p, span, label, div {{
        font-size: {TYPOGRAPHY["size_base"]} !important;
    }}
    
    p, label {{
        color: {COLORS["text_secondary"]} !important;
    }}
    
    /* ========== FORM INPUTS ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiselect > div > div > div {{
        background: {COLORS["bg_card"]} !important;
        border: 1px solid {COLORS["border_card"]} !important;
        border-radius: 8px !important;
        color: {COLORS["text_primary"]} !important;
        font-size: {TYPOGRAPHY["size_base"]} !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS["primary"]} !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }}
    
    /* Select dropdowns */
    [data-baseweb="select"] > div {{
        background: {COLORS["bg_card"]} !important;
        border-color: {COLORS["border_card"]} !important;
    }}
    
    /* Tags in multiselect - pink like website */
    [data-baseweb="tag"] {{
        background: {COLORS["pink"]} !important;
        color: white !important;
    }}
    
    /* File uploader */
    [data-testid="stFileUploader"] {{
        background: {COLORS["bg_card"]} !important;
        border: 1px dashed {COLORS["border_card"]} !important;
        border-radius: 8px !important;
    }}
    
    /* ========== BUTTONS ========== */
    .stButton > button {{
        background: {COLORS["primary"]} !important;
        color: {COLORS["text_primary"]} !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: {TYPOGRAPHY["size_base"]} !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button:hover {{
        background: {COLORS["primary_dark"]} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
    }}
    
    .stButton > button:disabled {{
        background: {COLORS["bg_input"]} !important;
        color: {COLORS["text_muted"]} !important;
        opacity: 0.6 !important;
    }}
    
    /* Download buttons - subtle style */
    .stDownloadButton > button {{
        background: {COLORS["bg_input"]} !important;
        border: 1px solid {COLORS["border_light"]} !important;
        color: {COLORS["text_secondary"]} !important;
        border-radius: 6px !important;
    }}
    
    .stDownloadButton > button:hover {{
        border-color: {COLORS["primary"]} !important;
        color: {COLORS["primary"]} !important;
    }}
    
    /* Secondary/Link buttons */
    .stLinkButton > a {{
        background: {COLORS["bg_input"]} !important;
        border: 1px solid {COLORS["border"]} !important;
        color: {COLORS["text_secondary"]} !important;
        border-radius: 6px !important;
        font-size: {TYPOGRAPHY["size_base"]} !important;
    }}
    
    .stLinkButton > a:hover {{
        border-color: {COLORS["primary"]} !important;
        color: {COLORS["primary"]} !important;
        background: {COLORS["bg_hover"]} !important;
    }}
    
    /* ========== TABS ========== */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORS["bg_card"]};
        border-radius: 12px;
        padding: 6px;
        gap: 4px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: {COLORS["text_muted"]} !important;
        border-radius: 8px !important;
        font-size: {TYPOGRAPHY["size_base"]} !important;
        font-weight: 500 !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%) !important;
        color: {COLORS["text_primary"]} !important;
    }}
    
    /* ========== SIDEBAR ========== */
    section[data-testid="stSidebar"] {{
        background: {COLORS["bg_card"]} !important;
        border-right: 1px solid {COLORS["border"]} !important;
    }}
    
    section[data-testid="stSidebar"] .stButton > button {{
        background: {COLORS["bg_hover"]} !important;
        border: 1px solid {COLORS["border"]} !important;
    }}
    
    section[data-testid="stSidebar"] .stButton > button:hover {{
        border-color: {COLORS["primary"]} !important;
    }}
    
    /* ========== CARDS & CONTAINERS ========== */
    .output-box, .card {{
        background: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        padding: {SPACING["lg"]};
        margin: {SPACING["md"]} 0;
    }}
    
    .input-section {{
        background: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        padding: {SPACING["lg"]};
        margin-bottom: {SPACING["md"]};
    }}
    
    /* ========== STATUS INDICATOR ========== */
    .status-container {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        border: 1px solid {COLORS["border"]};
        border-left: 4px solid {COLORS["primary"]};
        border-radius: 12px;
        padding: {SPACING["lg"]};
        margin: {SPACING["md"]} 0;
    }}
    
    .status-step {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0;
        color: {COLORS["text_muted"]};
        font-size: {TYPOGRAPHY["size_base"]};
    }}
    
    .status-step.active {{
        color: {COLORS["primary"]};
        font-weight: 600;
    }}
    
    .status-step.complete {{
        color: {COLORS["success"]};
    }}
    
    .status-spinner {{
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid {COLORS["border"]};
        border-top-color: {COLORS["primary"]};
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }}
    
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}
    
    /* ========== EXPANDER (with Material Icons fix) ========== */
    .streamlit-expanderHeader {{
        background: {COLORS["bg_card"]} !important;
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 10px !important;
        font-size: {TYPOGRAPHY["size_base"]} !important;
        padding: 12px 16px !important;
    }}
    
    .streamlit-expanderHeader:hover {{
        border-color: {COLORS["primary"]} !important;
    }}
    
    /* Hide broken Material Icon text (keyboard_arrow_down, etc.) */
    [data-testid="stExpander"] details > summary > span:first-child {{
        font-size: 0 !important;
        width: 20px !important;
        height: 20px !important;
    }}
    
    [data-testid="stExpander"] details > summary > span:first-child::before {{
        content: "▶" !important;
        font-size: 12px !important;
        color: {COLORS["text_muted"]} !important;
    }}
    
    [data-testid="stExpander"] details[open] > summary > span:first-child::before {{
        content: "▼" !important;
    }}
    
    /* Custom details/summary (recommended alternative to st.expander) */
    details.sharp-accordion {{
        background: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        margin: 8px 0;
    }}
    
    details.sharp-accordion summary {{
        padding: 14px 18px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        list-style: none;
        color: {COLORS["text_primary"]};
    }}
    
    details.sharp-accordion summary::-webkit-details-marker {{
        display: none;
    }}
    
    details.sharp-accordion > div {{
        padding: 0 18px 18px;
        border-top: 1px solid {COLORS["border"]};
    }}
    
    /* ========== DOWNLOAD BUTTONS ========== */
    .stDownloadButton > button {{
        background: {COLORS["bg_card"]} !important;
        border: 1px solid {COLORS["border"]} !important;
        color: {COLORS["text_secondary"]} !important;
    }}
    
    .stDownloadButton > button:hover {{
        border-color: {COLORS["primary"]} !important;
        color: {COLORS["primary"]} !important;
    }}
    
    /* ========== CHECKBOX & RADIO ========== */
    .stCheckbox, .stRadio {{
        font-size: {TYPOGRAPHY["size_base"]} !important;
    }}
    
    /* ========== SLIDER ========== */
    .stSlider {{
        padding-top: 16px !important;
    }}
    
    /* ========== ALERTS ========== */
    .stAlert {{
        border-radius: 10px !important;
        font-size: {TYPOGRAPHY["size_base"]} !important;
    }}
    
    /* ========== POPOVER (Feedback) ========== */
    [data-testid="stPopover"] {{
        background: {COLORS["bg_card"]} !important;
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 12px !important;
    }}
    
    /* Hide broken Material Icon text on popover button (expand_more, etc.) */
    [data-testid="stPopover"] > button > div > span:last-child {{
        font-size: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }}
    
    /* Aggressive fix: hide any text containing icon names */
    [data-testid="stPopover"] button span {{
        font-size: 0 !important;
        visibility: hidden !important;
    }}
    
    /* But show the label text */
    [data-testid="stPopover"] button p,
    [data-testid="stPopover"] button div[data-testid="stMarkdownContainer"] {{
        font-size: 14px !important;
        visibility: visible !important;
    }}
    
    /* Also fix any stray icon text in buttons */
    button span.material-icons,
    button span[class*="icon"] {{
        font-size: 0 !important;
    }}
    
    /* Hide keyboard_arrow, expand_more, expand_less text anywhere */
    *:not(script):not(style) {{
        font-family: 'Nunito', sans-serif !important;
    }}
    
    /* Force Material Icons font where needed but hide text fallback */
    .material-icons {{
        font-family: 'Material Icons' !important;
        font-size: 24px !important;
    }}
    
    /* ========== METRICS ========== */
    [data-testid="stMetricValue"] {{
        font-size: {TYPOGRAPHY["size_2xl"]} !important;
        font-weight: 700 !important;
    }}
    
    /* ========== FILE UPLOADER ========== */
    .stFileUploader {{
        background: {COLORS["bg_card"]} !important;
        border: 1px dashed {COLORS["border_light"]} !important;
        border-radius: 10px !important;
    }}
    
    /* ========== TOP BANNER ========== */
    .top-banner {{
        background: #1a1a1a;
        border-bottom: 1px solid {COLORS["border"]};
        padding: 12px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -1rem -1rem 1rem -1rem;
        flex-wrap: wrap;
        gap: 12px;
    }}
    
    .top-banner-links {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    
    /* Pink filled buttons - matching website exactly */
    .top-banner-btn-pink {{
        background: #db2777;
        color: white !important;
        text-decoration: none !important;
        font-size: 14px;
        font-weight: 600;
        padding: 10px 24px;
        border-radius: 6px;
        transition: all 0.2s;
        display: inline-block;
        border: none;
    }}
    
    .top-banner-btn-pink:hover {{
        background: #be185d;
        transform: translateY(-1px);
        text-decoration: none !important;
        box-shadow: 0 4px 12px rgba(219, 39, 119, 0.3);
    }}
    
    /* Outline button - white/light border like website */
    .top-banner-btn-outline {{
        background: transparent;
        color: white !important;
        text-decoration: none !important;
        font-size: 14px;
        font-weight: 600;
        padding: 10px 24px;
        border-radius: 6px;
        border: 2px solid #60a5fa;
        transition: all 0.2s;
        display: inline-block;
    }}
    
    .top-banner-btn-outline:hover {{
        background: rgba(96, 165, 250, 0.1);
        transform: translateY(-1px);
        text-decoration: none !important;
    }}
    
    /* Website link on right */
    .top-banner-website {{
        color: #60a5fa;
        text-decoration: none !important;
        font-size: 14px;
        font-weight: 500;
        transition: color 0.2s;
    }}
    
    .top-banner-website:hover {{
        color: #93c5fd;
        text-decoration: none !important;
    }}
    
    .top-banner-cta {{
        background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["secondary"]});
        color: white !important;
        padding: 8px 20px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none;
        transition: transform 0.2s, box-shadow 0.2s;
        border: none;
    }}
    
    .top-banner-cta:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        color: white;
    }}
    
    /* ========== HIDE STREAMLIT BRANDING ========== */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    </style>
    """

def apply_global_styles():
    """Apply global styles to the current app. Call this early in your app."""
    st.markdown(get_global_css(), unsafe_allow_html=True)

# ===========================================
# AUTH STYLES (for login page)
# ===========================================

def get_auth_css():
    """Additional styles for auth/login pages."""
    return f"""
    <style>
    .auth-container {{
        max-width: 400px;
        margin: 0 auto;
        padding: {SPACING["xl"]} {SPACING["lg"]};
    }}
    
    .auth-header {{
        text-align: center;
        padding: {SPACING["xl"]} 0 {SPACING["lg"]};
    }}
    
    .auth-logo {{
        width: 80px;
        margin-bottom: {SPACING["md"]};
    }}
    
    .auth-title {{
        color: {COLORS["text_primary"]};
        font-size: {TYPOGRAPHY["size_3xl"]};
        font-weight: 700;
        margin: 0 0 {SPACING["sm"]};
    }}
    
    .auth-subtitle {{
        color: {COLORS["text_muted"]};
        font-size: {TYPOGRAPHY["size_base"]};
    }}
    
    .auth-divider {{
        text-align: center;
        color: {COLORS["text_dim"]};
        margin: {SPACING["md"]} 0;
    }}
    </style>
    """

def apply_auth_styles():
    """Apply auth-specific styles."""
    st.markdown(get_auth_css(), unsafe_allow_html=True)

# ===========================================
# TOP BANNER COMPONENT
# ===========================================

def render_top_banner(show_cta: bool = True, cta_text: str = "Let's Talk", cta_url: str = None):
    """
    Render top banner with links to website, blog, calendly, and optional CTA.
    Call this at the very top of your app, right after apply_global_styles().
    
    Args:
        show_cta: Whether to show the CTA button
        cta_text: Text for the CTA button
        cta_url: URL for CTA (defaults to calendly link)
    """
    cta_link = cta_url or EXTERNAL_LINKS["calendly"]
    
    st.markdown(f"""
    <div class="top-banner">
        <div class="top-banner-links">
            <a href="{EXTERNAL_LINKS["website"]}" target="_blank" class="top-banner-btn-pink">
                Bespoke Services
            </a>
            <a href="{EXTERNAL_LINKS["blog"]}" target="_blank" class="top-banner-btn-pink">
                Blog
            </a>
            <a href="{cta_link}" target="_blank" class="top-banner-btn-outline">
                {cta_text}
            </a>
        </div>
        <a href="{EXTERNAL_LINKS["website"]}" target="_blank" class="top-banner-website">
            sharphuman.com
        </a>
    </div>
    """, unsafe_allow_html=True)

def render_promo_banner(
    message: str = "Need bespoke implementation or custom features?",
    cta_text: str = "Let's Chat",
    cta_url: str = None,
    dismissible: bool = True
):
    """
    Render a promotional banner below the top banner.
    Good for announcements, feature promos, or bespoke implementation offers.
    
    Args:
        message: The promo message
        cta_text: CTA button text
        cta_url: URL for CTA (defaults to calendly)
        dismissible: Whether user can dismiss the banner
    """
    cta_link = cta_url or EXTERNAL_LINKS["calendly"]
    
    # Check if dismissed in session state
    if dismissible and st.session_state.get('promo_dismissed', False):
        return
    
    col1, col2, col3 = st.columns([6, 2, 1])
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 10px;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 20px;">💡</span>
            <span style="color: {COLORS["text_secondary"]}; font-size: 14px;">{message}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.link_button(f"✨ {cta_text}", cta_link, use_container_width=True)
    
    with col3:
        if dismissible:
            if st.button("✕", key="dismiss_promo", help="Dismiss"):
                st.session_state.promo_dismissed = True
                st.rerun()

# ===========================================
# HEADER COMPONENT
# ===========================================

def render_header(app_name: str, app_subtitle: str, app_icon: str = "🚀"):
    """
    Render consistent app header.
    
    Args:
        app_name: Name of the app (e.g., "Sharp Screen")
        app_subtitle: Short description (e.g., "CV Screening & Analysis")
        app_icon: Emoji or icon (optional, defaults to 🚀)
    """
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 24px 0;
        border-bottom: 1px solid {COLORS["border"]};
        margin-bottom: 32px;
    ">
        <img src="https://sharphuman.com/logo1-3.png" style="width: 50px;">
        <div>
            <h1 style="margin: 0; font-size: {TYPOGRAPHY["size_3xl"]};">{app_name}</h1>
            <p style="color: {COLORS["text_muted"]}; margin: 4px 0 0; font-size: {TYPOGRAPHY["size_base"]};">{app_subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===========================================
# SIDEBAR COMPONENT
# ===========================================

APP_LABELS = [
    ("portal", "🏠", "Portal"),
    ("jd", "📝", "JD Writer"),
    ("screen", "🔍", "CV Screener"),
    ("interview", "🎯", "Interview"),
    ("source", "🎣", "Sourcing"),
    ("content", "✍️", "Content"),
    ("sales", "💰", "Sales"),
    ("reach", "🚀", "Reach"),
    ("assistant", "🤖", "Assistant"),
]

def render_sidebar(
    current_app: str, 
    user_email: str = "User", 
    user_plan: str = "free", 
    session_token: str = "",
    show_external_links: bool = True
):
    """
    Render consistent sidebar with navigation.
    
    Args:
        current_app: Key of current app (e.g., "screen")
        user_email: User's email to display
        user_plan: User's plan level
        session_token: Auth token for cross-app navigation
        show_external_links: Whether to show website/blog/calendly links
    """
    with st.sidebar:
        # Logo at top
        st.markdown(f"""
        <div style="text-align: center; padding: 12px 0 20px; border-bottom: 1px solid {COLORS['border']}; margin-bottom: 16px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width: 45px; margin-bottom: 8px;">
            <p style="color: {COLORS['text_primary']}; font-weight: 700; font-size: 16px; margin: 0;">Sharp Suite</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User card
        st.markdown(f"""
        <div style="
            padding: 14px 16px;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            margin-bottom: 20px;
        ">
            <p style="color: {COLORS["text_muted"]}; margin: 0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">Account</p>
            <p style="color: {COLORS["text_primary"]}; margin: 6px 0 4px; font-weight: 600; font-size: 14px;">{user_email}</p>
            <span style="
                display: inline-block;
                background: {'{}'.format(COLORS['pink']) if user_plan == 'god' else 'rgba(219, 39, 119, 0.2)'};
                color: {'white' if user_plan == 'god' else COLORS['pink']};
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            ">{user_plan}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # App Navigation
        st.markdown(f"<p style='color: {COLORS['text_muted']}; font-size: 11px; margin: 0 0 8px 4px; text-transform: uppercase; letter-spacing: 0.5px;'>🧭 Navigation</p>", unsafe_allow_html=True)
        
        for app_key, icon, label in APP_LABELS:
            url = f"{APP_URLS.get(app_key, '')}?auth={session_token}" if session_token else APP_URLS.get(app_key, "")
            
            if app_key == current_app:
                # Current app - highlighted in pink
                st.markdown(f"""
                <div style="
                    background: {COLORS['pink']};
                    padding: 10px 16px;
                    border-radius: 8px;
                    margin: 4px 0;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                ">
                    <span style="font-size: 16px;">{icon}</span>
                    <span style="color: white; font-weight: 600; font-size: 14px;">{label}</span>
                    <span style="color: rgba(255,255,255,0.7); margin-left: auto; font-size: 12px;">◀</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.link_button(f"{icon} {label}", url, use_container_width=True)
        
        # Admin link (for god users)
        if user_plan == "god":
            st.markdown("---")
            admin_url = f"{APP_URLS.get('admin', '')}?auth={session_token}" if session_token else APP_URLS.get('admin', "")
            st.link_button("⚙️ Admin Dashboard", admin_url, use_container_width=True)
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ===========================================
# FEEDBACK WIDGET
# ===========================================

def render_feedback_widget(app_name: str, submit_callback=None):
    """
    Render feedback widget in bottom-right corner.
    
    Args:
        app_name: Name of current app for logging
        submit_callback: Function to call when feedback submitted. 
                        Should accept (app, type, message) params.
    """
    # Add spacer to push feedback to bottom
    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
    
    # Position in bottom right
    _, _, _, col = st.columns([4, 1, 1, 1])
    with col:
        with st.popover("💬 Feedback"):
            st.markdown(f"**Send Feedback**")
            fb_type = st.segmented_control(
                "Type", 
                ["🐛 Bug", "✨ Feature", "💬 General"], 
                default="💬 General",
                label_visibility="collapsed",
                key=f"fb_type_{app_name}"
            )
            fb_message = st.text_area(
                "Message", 
                height=100, 
                placeholder="Your feedback helps us improve...",
                label_visibility="collapsed",
                key=f"fb_msg_{app_name}"
            )
            if st.button("Send", type="primary", use_container_width=True, key=f"fb_send_{app_name}"):
                if fb_message and submit_callback:
                    type_map = {"🐛 Bug": "bug", "✨ Feature": "feature", "💬 General": "general"}
                    fb_type_clean = type_map.get(fb_type, "general")
                    if submit_callback(app_name, fb_type_clean, fb_message):
                        st.success("Thanks for your feedback! 🙏")
                    else:
                        st.error("Failed to submit. Try again?")
                elif fb_message:
                    st.info("Feedback logged!")
                else:
                    st.warning("Please enter a message")

# ===========================================
# STATUS INDICATOR COMPONENT
# ===========================================

class StatusIndicator:
    """
    Show users what the AI is currently doing.
    
    Usage:
        status = StatusIndicator()
        status.start()
        status.update("🔍 Analyzing resume...", 1, 4)
        status.update("📊 Scoring skills...", 2, 4)
        status.update("✍️ Writing summary...", 3, 4)
        status.update("✅ Complete!", 4, 4)
        status.finish()
    """
    
    # Pre-defined step sequences for common operations
    PRESETS = {
        "screening": [
            ("🔍", "Reading and parsing documents..."),
            ("📊", "Analyzing skills and experience..."),
            ("⚖️", "Scoring against job requirements..."),
            ("📝", "Generating detailed evaluation..."),
            ("✨", "Polishing for clarity..."),
        ],
        "interview": [
            ("🎧", "Processing interview content..."),
            ("🔍", "Identifying key responses..."),
            ("📊", "Evaluating against criteria..."),
            ("🎯", "Scoring competencies..."),
            ("📝", "Writing recommendations..."),
        ],
        "jd": [
            ("📖", "Understanding role requirements..."),
            ("🎯", "Tailoring for target audience..."),
            ("✍️", "Crafting compelling copy..."),
            ("🔍", "Optimizing for search..."),
            ("✨", "Final polish..."),
        ],
        "sales": [
            ("🎧", "Transcribing call audio..."),
            ("🔍", "Identifying key moments..."),
            ("📊", "Scoring against framework..."),
            ("💡", "Finding coaching opportunities..."),
            ("📝", "Writing recommendations..."),
        ],
        "content": [
            ("🔍", "Researching topic..."),
            ("📖", "Structuring outline..."),
            ("✍️", "Writing content..."),
            ("🎯", "Optimizing for platform..."),
            ("✨", "Final review..."),
        ],
        "general": [
            ("🔍", "Analyzing input..."),
            ("🧠", "Processing with AI..."),
            ("✍️", "Generating output..."),
            ("✨", "Finalizing..."),
        ],
    }
    
    def __init__(self, preset: str = "general", placeholder=None):
        """
        Initialize status indicator.
        
        Args:
            preset: One of the predefined step sequences
            placeholder: Optional st.empty() to use
        """
        self.steps = self.PRESETS.get(preset, self.PRESETS["general"])
        self.placeholder = placeholder or st.empty()
        self.current_step = 0
        self.total_steps = len(self.steps)
        self.start_time = None
    
    def start(self):
        """Start the status indicator."""
        self.start_time = time.time()
        self.current_step = 0
        self._render()
    
    def update(self, step_index: int = None, custom_message: str = None):
        """
        Update to a specific step or custom message.
        
        Args:
            step_index: Step number (1-indexed) to show
            custom_message: Override message for current step
        """
        if step_index is not None:
            self.current_step = min(step_index, self.total_steps)
        else:
            self.current_step = min(self.current_step + 1, self.total_steps)
        self._render(custom_message)
    
    def next(self):
        """Move to the next step."""
        self.update()
    
    def finish(self, message: str = "✅ Complete!"):
        """Finish and show completion message."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.placeholder.markdown(f"""
        <div class="status-container">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 24px;">✅</span>
                <div>
                    <p style="margin: 0; color: {COLORS["success"]}; font-weight: 600; font-size: {TYPOGRAPHY["size_lg"]};">
                        {message}
                    </p>
                    <p style="margin: 4px 0 0; color: {COLORS["text_muted"]}; font-size: {TYPOGRAPHY["size_sm"]};">
                        Completed in {elapsed:.1f}s
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def clear(self):
        """Clear the status indicator."""
        self.placeholder.empty()
    
    def _render(self, custom_message: str = None):
        """Render the current status."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        steps_html = ""
        for i, (icon, label) in enumerate(self.steps):
            step_num = i + 1
            if step_num < self.current_step:
                # Completed
                steps_html += f"""
                <div class="status-step complete">
                    <span style="color: {COLORS["success"]};">✓</span>
                    <span>{label}</span>
                </div>
                """
            elif step_num == self.current_step:
                # Active
                display_label = custom_message if custom_message else label
                steps_html += f"""
                <div class="status-step active">
                    <div class="status-spinner"></div>
                    <span>{icon} {display_label}</span>
                </div>
                """
            else:
                # Pending
                steps_html += f"""
                <div class="status-step">
                    <span style="color: {COLORS["text_dim"]};">○</span>
                    <span>{label}</span>
                </div>
                """
        
        self.placeholder.markdown(f"""
        <div class="status-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <p style="margin: 0; color: {COLORS["text_primary"]}; font-weight: 600; font-size: {TYPOGRAPHY["size_lg"]};">
                    Working on it...
                </p>
                <span style="color: {COLORS["text_muted"]}; font-size: {TYPOGRAPHY["size_sm"]};">
                    {elapsed:.1f}s
                </span>
            </div>
            {steps_html}
        </div>
        """, unsafe_allow_html=True)


def show_status(preset: str = "general"):
    """
    Quick helper to create and start a status indicator.
    
    Usage:
        with show_status("screening") as status:
            result = do_screening()
            status.next()
            result = do_scoring()
            status.next()
    
    Returns:
        StatusIndicator instance
    """
    status = StatusIndicator(preset=preset)
    status.start()
    return status

# ===========================================
# CARD COMPONENTS
# ===========================================

def render_metric_card(label: str, value: str, color: str = None, icon: str = ""):
    """Render a metric card."""
    card_color = color or COLORS["primary"]
    st.markdown(f"""
    <div style="
        background: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    ">
        <p style="color: {COLORS["text_muted"]}; margin: 0; font-size: {TYPOGRAPHY["size_xs"]}; text-transform: uppercase;">
            {icon} {label}
        </p>
        <p style="color: {card_color}; font-size: {TYPOGRAPHY["size_3xl"]}; font-weight: 700; margin: 8px 0 0;">
            {value}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_info_card(title: str, content: str, icon: str = "ℹ️"):
    """Render an info card."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        border: 1px solid {COLORS["border"]};
        border-left: 4px solid {COLORS["primary"]};
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
    ">
        <p style="color: {COLORS["text_primary"]}; font-weight: 600; margin: 0 0 8px; font-size: {TYPOGRAPHY["size_lg"]};">
            {icon} {title}
        </p>
        <p style="color: {COLORS["text_secondary"]}; margin: 0; font-size: {TYPOGRAPHY["size_base"]};">
            {content}
        </p>
    </div>
    """, unsafe_allow_html=True)

# ===========================================
# AUTH COMPONENTS
# ===========================================

def render_auth_header(app_name: str, app_subtitle: str):
    """Render auth page header."""
    st.markdown(f"""
    <div class="auth-header">
        <img src="https://sharphuman.com/logo1-3.png" class="auth-logo">
        <h1 class="auth-title">{app_name}</h1>
        <p class="auth-subtitle">{app_subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

# ===========================================
# UTILITY FUNCTIONS
# ===========================================

def get_score_color(score: float, max_score: float = 100) -> str:
    """Get color based on score percentage."""
    pct = (score / max_score) * 100 if max_score > 0 else 0
    if pct >= 75:
        return COLORS["success"]
    elif pct >= 50:
        return COLORS["warning"]
    else:
        return COLORS["error"]

def format_timestamp(dt: datetime = None) -> str:
    """Format timestamp for display."""
    dt = dt or datetime.now()
    return dt.strftime("%B %d, %Y at %I:%M %p")
