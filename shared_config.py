"""
Sharp Suite - Shared TConfiguration
===================================
All apps import from this single source of truth.

Environment variables override these defaults.
Set once in your deployment platform, all apps use them.

REQUIRED ENV VARS (set in your hosting platform):
- SUPABASE_SERVICE_KEY  (for RLS bypass - keeps feedback, history working)
- ANTHROPIC_API_KEY     (for Claude API calls)

OPTIONAL (have defaults):
- SUPABASE_URL
- SUPABASE_ANON_KEY
- GOD_PASSWORD
"""

import os

# ===========================================
# SUPABASE CONFIGURATION
# ===========================================
SUPABASE_URL = os.environ.get(
    "SUPABASE_URL", 
    "https://qkjtprqgblnfftrotyks.supabase.co"
)

SUPABASE_ANON_KEY = os.environ.get(
    "SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
)

# SERVICE KEY - Required for RLS bypass (feedback, history, etc.)
# Get from: Supabase Dashboard → Settings → API → service_role key
SUPABASE_SERVICE_KEY = os.environ.get(
    "SUPABASE_SERVICE_KEY",
    SUPABASE_ANON_KEY  # Falls back to anon if not set (may cause permission errors)
)

# ===========================================
# ANTHROPIC (CLAUDE) CONFIGURATION
# ===========================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Model to use across all apps
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")

# ===========================================
# AUTH CONFIGURATION
# ===========================================
GOD_PASSWORD = os.environ.get("GOD_PASSWORD", "G0DHum@n101!!!")

# Session duration in hours
SESSION_DURATION_HOURS = int(os.environ.get("SESSION_DURATION_HOURS", "24"))

# ===========================================
# APP URLs (for cross-app navigation)
# ===========================================
APP_URLS = {
    "portal": os.environ.get("PORTAL_URL", "https://portal.sharphuman.com"),
    "jd": os.environ.get("JD_URL", "https://jd.sharphuman.com"),
    "screen": os.environ.get("SCREEN_URL", "https://screen.sharphuman.com"),
    "interview": os.environ.get("INTERVIEW_URL", "https://interview.sharphuman.com"),
    "outreach": os.environ.get("OUTREACH_URL", "https://outreach.sharphuman.com"),
    "content": os.environ.get("CONTENT_URL", "https://content.sharphuman.com"),
    "sales": os.environ.get("SALES_URL", "https://sales.sharphuman.com"),
    "admin": os.environ.get("ADMIN_URL", "https://admin.sharphuman.com"),
}

# ===========================================
# FEATURE FLAGS
# ===========================================
ENABLE_USAGE_LOGGING = os.environ.get("ENABLE_USAGE_LOGGING", "true").lower() == "true"
ENABLE_FEEDBACK = os.environ.get("ENABLE_FEEDBACK", "true").lower() == "true"
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"

# ===========================================
# RESEND (Email) CONFIGURATION
# ===========================================
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
FEEDBACK_EMAIL = os.environ.get("FEEDBACK_EMAIL", "feedback@sharphuman.com")

# ===========================================
# HELPER FUNCTION: Validate Config
# ===========================================
def validate_config():
    """Check if critical env vars are set. Call on app startup."""
    warnings = []
    
    if not ANTHROPIC_API_KEY:
        warnings.append("⚠️ ANTHROPIC_API_KEY not set - AI features will fail")
    
    if SUPABASE_SERVICE_KEY == SUPABASE_ANON_KEY:
        warnings.append("⚠️ SUPABASE_SERVICE_KEY not set - using anon key (may cause permission errors)")
    
    if not RESEND_API_KEY:
        warnings.append("⚠️ RESEND_API_KEY not set - feedback emails disabled")
    
    return warnings

# ===========================================
# USAGE EXAMPLE IN APP:
# ===========================================
"""
# At top of any app.py:
from shared_config import (
    SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY,
    ANTHROPIC_API_KEY, CLAUDE_MODEL, GOD_PASSWORD,
    APP_URLS, validate_config
)

# Optional: show warnings in sidebar during dev
if DEBUG_MODE:
    for warn in validate_config():
        st.sidebar.warning(warn)
"""
