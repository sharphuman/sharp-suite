"""Sharp Content - AI Content Engine with Multi-Format TExport"""
import streamlit as st
import os
import requests
from datetime import datetime, timedelta
import secrets
import json
import re
import io
import sys

# Add parent directory for shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# ============================================
# SHARED MODULE IMPORTS
# ============================================
try:
    from shared_config import (
        SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY,
        ANTHROPIC_API_KEY, GOD_PASSWORD, APP_URLS, CLAUDE_MODEL
    )
    from shared_ui import (
        apply_global_styles,
        render_top_banner,
        render_header,
        render_sidebar,
        render_feedback_widget,
        COLORS
    )
    USING_SHARED = True
except ImportError:
    USING_SHARED = False
    SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", SUPABASE_ANON_KEY)
    GOD_PASSWORD = os.environ.get("GOD_PASSWORD", "G0DHum@n101!!!")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    APP_URLS = {
        "portal": "https://demo.sharphuman.com",
        "jd": "https://jd.sharphuman.com",
        "screen": "https://screen.sharphuman.com",
        "interview": "https://interview.sharphuman.com",
        "outreach": "https://outreach.sharphuman.com",
        "content": "https://content.sharphuman.com",
        "sales": "https://sales.sharphuman.com",
        "admin": "https://admin.sharphuman.com"
    }

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")


def create_session(user_id, email):
    token = secrets.token_urlsafe(32)
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/sessions", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"user_id": user_id, "token": token, "ip_address": "unknown", "device_hash": "content", "is_active": True, "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()}, timeout=10)
    except:
        pass
    return token


def supabase_sign_in(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            user = data.get("user", {})
            return {"success": True, "user": user, "session_token": create_session(user.get("id"), email)}
        return {"success": False, "message": data.get("error_description") or "Invalid"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def supabase_sign_up(email, password):
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/signup", headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}, json={"email": email, "password": password}, timeout=10)
        data = r.json()
        return {"success": True, "message": "Check email!"} if r.status_code == 200 and data.get("user") else {"success": False, "message": data.get("error_description") or "Failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def validate_session_token(token):
    if not token:
        return None
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/sessions?token=eq.{token}&is_active=eq.true", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
        if r.status_code == 200 and r.json():
            session = r.json()[0]
            expires = datetime.fromisoformat(session["expires_at"].replace("Z", "+00:00"))
            if expires.replace(tzinfo=None) > datetime.utcnow():
                ur = requests.get(f"{SUPABASE_URL}/rest/v1/user_profiles?id=eq.{session['user_id']}", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
                if ur.status_code == 200 and ur.json():
                    p = ur.json()[0]
                    return {"user_id": session["user_id"], "email": p.get("email"), "plan": p.get("plan", "free"), "token": token}
    except:
        pass
    return None


def log_usage(user_id, session_id, app, action, tokens_used=0):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/usage_logs", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"user_id": user_id, "session_id": session_id, "app": app, "action": action, "tokens_used": tokens_used}, timeout=5)
    except:
        pass


def submit_feedback(app, feedback_type, message):
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/user_feedback", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}, json={"user_id": st.session_state.user.get("id") if st.session_state.user else None, "app": app, "feedback_type": feedback_type, "rating": 4, "message": message, "email": get_user_email()}, timeout=10)
        return r.status_code in [200, 201]
    except:
        return False


def init_session():
    for k, v in [('authenticated', False), ('user', None), ('is_god', False), ('session_token', ''), ('user_plan', 'free'), ('working_on', None), ('blog_result', None), ('research_data', ''), ('content_result', None)]:
        if k not in st.session_state:
            st.session_state[k] = v


def check_url_auth():
    if st.session_state.authenticated:
        return
    # Support both 'token' and 'auth' params for backwards compatibility
    token = st.query_params.get("token") or st.query_params.get("auth")
    if token:
        user_info = validate_session_token(token)
        if user_info:
            st.session_state.authenticated = True
            st.session_state.user = {"email": user_info["email"], "id": user_info["user_id"]}
            st.session_state.session_token = token
            st.session_state.user_plan = user_info.get("plan", "free")
            st.session_state.is_god = user_info.get("plan") == "god"


def get_user_email():
    return st.session_state.user.get("email", "User") if st.session_state.user else ("GOD" if st.session_state.is_god else "User")


def build_app_url(app_name):
    base = APP_URLS.get(app_name, f"https://{app_name}.sharphuman.com")
    token = st.session_state.get("session_token", "")
    return f"{base}?token={token}" if base and token else base


def call_claude(prompt, max_tokens=4000, action="content"):
    api_key = ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "Error: ANTHROPIC_API_KEY not set", 0
    try:
        model = CLAUDE_MODEL if USING_SHARED else "claude-sonnet-4-20250514"
        r = requests.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}, json={"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}, timeout=180)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"]
            if st.session_state.user:
                log_usage(st.session_state.user.get("id"), st.session_state.get("session_token"), "content", action, (len(prompt)+len(text))//4)
            return text, (len(prompt)+len(text))//4
        return f"Error: {r.status_code}", 0
    except Exception as e:
        return f"Error: {e}", 0


def research_topic(topic):
    if not PERPLEXITY_API_KEY:
        return "Research requires PERPLEXITY_API_KEY"
    try:
        r = requests.post("https://api.perplexity.ai/chat/completions", headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"}, json={"model": "sonar-pro", "messages": [{"role": "system", "content": "You are an expert researcher. Provide comprehensive, factual information."}, {"role": "user", "content": f"Research this topic in depth: {topic}"}]}, timeout=60)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Research error: {r.status_code}"
    except Exception as e:
        return f"Research error: {e}"


def generate_blog(topic, research, audience, tone, keywords, word_count):
    prompt = f"""Write a professional, SEO-optimized blog post.

TOPIC: {topic}
TARGET AUDIENCE: {audience or "General professional audience"}
TONE: {tone}
TARGET WORD COUNT: {word_count}
KEYWORDS TO INCLUDE: {keywords or "None specified"}
{f"RESEARCH/CONTEXT:{chr(10)}{research[:3000]}" if research else ""}

REQUIREMENTS:
1. Compelling headline with emotional hook
2. Meta description (155 chars max)
3. Introduction that hooks the reader
4. 3-5 main sections with H2 headers
5. Practical takeaways or action items
6. Strong conclusion with CTA
7. Naturally incorporate keywords for SEO

OUTPUT FORMAT (use this exact structure):
---
HEADLINE: [Your headline here]
META_DESCRIPTION: [Your meta description here]
TAGS: [tag1, tag2, tag3]
---

[Full blog post content in HTML format with <h2>, <p>, <ul>, <li> tags]

---
SOCIAL_SNIPPET: [A short, shareable quote from the article]
---"""
    return call_claude(prompt, max_tokens=6000, action="blog_generate")


def generate_social_from_blog(title, content):
    prompt = f"""Convert this blog content into platform-optimized social posts.

TITLE: {title}
CONTENT:
{content[:5000]}

OUTPUT FORMAT (JSON):
```json
{{
    "linkedin": {{
        "post": "Professional LinkedIn post (150-200 words with line breaks)",
        "hashtags": ["#tag1", "#tag2"]
    }},
    "twitter": {{
        "thread": ["Tweet 1 (280 chars max)", "Tweet 2", "Tweet 3"],
        "single": "Single tweet version (280 chars)"
    }},
    "facebook": {{
        "post": "Engaging Facebook post (100-150 words)",
        "caption": "Short caption for image post"
    }},
    "instagram": {{
        "caption": "Instagram caption with emojis (150-200 words)",
        "hashtags": ["#tag1", "#tag2", "#tag3"]
    }}
}}
```"""
    return call_claude(prompt, max_tokens=3000, action="social_generate")


def convert_to_wordpress(html_content, title, meta_desc, tags):
    return f"""<!-- WordPress Post -->
<!-- Title: {title} -->
<!-- Meta Description: {meta_desc} -->
<!-- Tags: {', '.join(tags) if tags else ''} -->

{html_content}

<!-- End WordPress Post -->"""


def convert_to_markdown(html_content, title):
    md = html_content
    md = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', md)
    md = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', md)
    md = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', md)
    md = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', md)
    md = re.sub(r'<strong>(.*?)</strong>', r'**\1**', md)
    md = re.sub(r'<em>(.*?)</em>', r'*\1*', md)
    md = re.sub(r'<ul[^>]*>', '', md)
    md = re.sub(r'</ul>', '\n', md)
    md = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', md)
    md = re.sub(r'<[^>]+>', '', md)
    return f"# {title}\n\n{md}"


# ============================================
# STREAMLIT APP
# ============================================
st.set_page_config(page_title="Sharp Content", page_icon="✍️", layout="wide")
init_session()
check_url_auth()

# CSS with shared styling
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
*, *::before, *::after { font-family: 'Nunito', sans-serif !important; }
.stApp, [data-testid="stAppViewContainer"] { background: #1a1a1a !important; }
[data-testid="stHeader"] { background: transparent !important; }
section[data-testid="stSidebar"] { background: #1a1a1a !important; border-right: 1px solid rgba(255,255,255,0.1); }
section[data-testid="stSidebar"] > div { background: #1a1a1a !important; }
section[data-testid="stSidebar"] * { color: #e5e5e5 !important; }
section[data-testid="stSidebar"] > div > div:first-child > div:first-child { display: none !important; }
h1,h2,h3,h4,h5,h6 { color: #fff !important; }
p,span,label,div,li { color: #e5e5e5; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div, [data-baseweb="select"] > div { background: #2a2a2a !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #fff !important; border-radius: 8px !important; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stDownloadButton > button { background: #2a2a2a !important; border: 1px solid rgba(255,255,255,0.1) !important; }
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 8px; border-bottom: 1px solid rgba(99,102,241,0.2); }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #9ca3af !important; border: none !important; }
.stTabs [aria-selected="true"] { color: #fff !important; border-bottom: 2px solid #6366f1 !important; }
[data-testid="stFileUploader"] { background: #2a2a2a !important; border: 1px dashed rgba(255,255,255,0.2) !important; border-radius: 8px !important; }
.user-card { background: rgba(99,102,241,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
.output-box { background: #2a2a2a; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 24px; margin: 16px 0; }
.export-card { background: #2a2a2a; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; text-align: center; }
/* Status badge with spinning logo */
.status-badge { position: fixed; top: 70px; right: 20px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 12px 24px 12px 50px; border-radius: 25px; font-weight: 600; z-index: 9999; box-shadow: 0 4px 15px rgba(99,102,241,0.4); }
.status-badge::before { content: ''; position: absolute; left: 12px; top: 50%; transform: translateY(-50%); width: 28px; height: 28px; background: url('https://assets.sharphuman.com/logo_spinner_small.gif') center/contain no-repeat; }
div[data-testid="stPopover"] button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 25px !important; }
</style>""", unsafe_allow_html=True)

# Auth screen
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:60px 0 30px;"><img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;"><h1 style="margin:0;">Sharp Content</h1><p style="color:#9ca3af;">AI Content Engine</p></div>""", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Log In", "Sign Up"])
        with t1:
            email, pwd = st.text_input("Email", key="l_email"), st.text_input("Password", type="password", key="l_pwd")
            if st.button("Log In", use_container_width=True):
                if pwd == GOD_PASSWORD:
                    st.session_state.authenticated, st.session_state.is_god, st.session_state.user = True, True, {"email": "GOD", "id": "god"}
                    st.session_state.session_token = secrets.token_urlsafe(32)
                    st.rerun()
                elif email and pwd:
                    r = supabase_sign_in(email, pwd)
                    if r["success"]:
                        st.session_state.authenticated, st.session_state.user, st.session_state.session_token = True, r["user"], r.get("session_token")
                        st.rerun()
                    else:
                        st.error(r["message"])
        with t2:
            s_email, s_pwd, s_conf = st.text_input("Email", key="s_email"), st.text_input("Password", type="password", key="s_pwd"), st.text_input("Confirm", type="password", key="s_conf")
            if st.button("Create Account", use_container_width=True):
                if s_pwd != s_conf:
                    st.error("Passwords don't match")
                elif len(s_pwd) < 6:
                    st.warning("6+ characters")
                elif s_email and s_pwd:
                    r = supabase_sign_up(s_email, s_pwd)
                    st.success(r["message"]) if r["success"] else st.error(r["message"])
    st.stop()

# Show working status
if st.session_state.working_on:
    st.markdown(f'<div class="status-badge">{st.session_state.working_on}</div>', unsafe_allow_html=True)

# Use shared_ui sidebar and top banner
if USING_SHARED:
    render_top_banner(show_cta=True, cta_text="Book a Demo")
    render_sidebar(
        current_app="content",
        user_email=get_user_email(),
        user_plan=st.session_state.get('user_plan', 'free'),
        session_token=st.session_state.get('session_token', '')
    )
else:
    # Fallback sidebar
    with st.sidebar:
        st.markdown(f"""<div class="user-card"><p style="color:#9ca3af;margin:0;font-size:12px;">Logged in as</p><p style="color:#fff;margin:4px 0;font-weight:600;">{get_user_email()}</p><p style="color:#6366f1;margin:0;font-size:12px;text-transform:uppercase;">{st.session_state.get('user_plan','free')} plan</p></div>""", unsafe_allow_html=True)
        st.markdown("**Apps**")
        for key, label in [("portal", "🏠 Portal"), ("jd", "📝 JD Writer"), ("screen", "🔍 CV Screener"), ("interview", "🎯 Interview"), ("outreach", "🚀 Outreach"), ("content", "✍️ Content"), ("sales", "💰 Sales")]:
            if key == "content":
                st.markdown(f"<div style='background:#db2777;padding:10px 16px;border-radius:8px;text-align:center;margin:4px 0;color:white;font-weight:600;'>{label} ◀</div>", unsafe_allow_html=True)
            else:
                st.link_button(label, build_app_url(key), use_container_width=True)
        if st.session_state.get("is_god"):
            st.markdown("---")
            st.link_button("⚙️ Admin", build_app_url("admin"), use_container_width=True)
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# Header
st.markdown("""<div style="display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid rgba(99,102,241,0.2);margin-bottom:20px;"><img src="https://sharphuman.com/logo1-3.png" style="width:50px;"><div><h1 style="margin:0;font-size:28px;">Sharp Content</h1><p style="color:#9ca3af;margin:0;">AI-Powered Content Engine</p></div></div>""", unsafe_allow_html=True)

# Main tabs
tab_blog, tab_social, tab_email, tab_video, tab_refine, tab_repurpose = st.tabs(["📝 Blog Writer", "📱 Social Media", "📧 Email", "🎬 Video Script", "✨ Refine", "♻️ Repurpose"])

with tab_blog:
    st.markdown("### 📝 AI Blog Writer")
    st.caption("Generate SEO-optimized blog posts with research, then export to social media")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        topic = st.text_input("Blog Topic", placeholder="e.g., The Future of Remote Work in Tech")
        audience = st.text_input("Target Audience", placeholder="e.g., HR managers, Tech recruiters")
    with col2:
        tone = st.selectbox("Tone", ["Professional", "Conversational", "Authoritative", "Friendly", "Technical"])
        word_count = st.select_slider("Word Count", options=[500, 800, 1000, 1500, 2000], value=1000)
    
    keywords = st.text_input("SEO Keywords (comma-separated)", placeholder="remote work, hybrid teams, productivity")
    
    c1, c2 = st.columns(2)
    with c1:
        do_research = st.checkbox("🔍 Research topic first (uses Perplexity)", value=False)
    with c2:
        if do_research and st.button("🔬 Research Now", use_container_width=True):
            if topic:
                st.session_state.working_on = "Researching..."
                st.session_state.research_data = research_topic(topic)
                st.session_state.working_on = None
                st.rerun()
    
    if st.session_state.research_data:
        with st.expander("📚 Research Results", expanded=False):
            st.markdown(st.session_state.research_data)
    
    if st.button("📝 Generate Blog Post", type="primary", use_container_width=True):
        if topic:
            st.session_state.working_on = "Writing blog..."
            result, tokens = generate_blog(topic, st.session_state.research_data, audience, tone, keywords, word_count)
            st.session_state.working_on = None
            if not str(result).startswith("Error"):
                st.session_state.blog_result = result
                st.rerun()
            else:
                st.error(result)
    
    if st.session_state.blog_result:
        result = st.session_state.blog_result
        
        # Parse result
        headline_match = re.search(r'HEADLINE:\s*(.+?)(?:\n|META)', result, re.DOTALL)
        meta_match = re.search(r'META_DESCRIPTION:\s*(.+?)(?:\n|TAGS|---)', result, re.DOTALL)
        tags_match = re.search(r'TAGS:\s*\[?([^\]]+)\]?', result)
        social_match = re.search(r'SOCIAL_SNIPPET:\s*(.+?)(?:---|$)', result, re.DOTALL)
        
        headline = headline_match.group(1).strip() if headline_match else "Blog Post"
        meta_desc = meta_match.group(1).strip() if meta_match else ""
        tags = [t.strip() for t in tags_match.group(1).split(',')] if tags_match else []
        social_snippet = social_match.group(1).strip() if social_match else ""
        
        # Extract main content
        content_match = re.search(r'---\s*\n(.*?)\n---\s*\nSOCIAL', result, re.DOTALL)
        if not content_match:
            content_match = re.search(r'TAGS:.*?\n\s*(.*?)(?:\n---\s*SOCIAL|$)', result, re.DOTALL)
        main_content = content_match.group(1).strip() if content_match else result
        
        st.markdown(f"### 📰 {headline}")
        if meta_desc:
            st.caption(f"*{meta_desc}*")
        if tags:
            st.markdown(" ".join([f"`{t}`" for t in tags[:5]]))
        
        st.markdown('<div class="output-box">', unsafe_allow_html=True)
        st.markdown(main_content, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export options
        st.markdown("---")
        st.markdown("#### 📤 Export Options")
        
        safe_title = re.sub(r'[^\w\s-]', '', headline)[:30].strip().replace(' ', '_')
        
        ec1, ec2, ec3, ec4 = st.columns(4)
        with ec1:
            st.download_button("📄 HTML", main_content, f"{safe_title}.html", "text/html", use_container_width=True)
        with ec2:
            md = convert_to_markdown(main_content, headline)
            st.download_button("📝 Markdown", md, f"{safe_title}.md", use_container_width=True)
        with ec3:
            wp = convert_to_wordpress(main_content, headline, meta_desc, tags)
            st.download_button("🔷 WordPress", wp, f"{safe_title}_wp.html", use_container_width=True)
        with ec4:
            st.download_button("📋 Raw", result, f"{safe_title}_full.txt", use_container_width=True)
        
        # Social media conversion
        st.markdown("---")
        st.markdown("#### 📱 Convert to Social Media")
        if st.button("🚀 Generate Social Posts", use_container_width=True):
            st.session_state.working_on = "Creating social posts..."
            social_result, _ = generate_social_from_blog(headline, main_content)
            st.session_state.working_on = None
            try:
                m = re.search(r'```json\s*(.*?)\s*```', social_result, re.DOTALL)
                social = json.loads(m.group(1) if m else social_result)
                
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.markdown("#### 💼 LinkedIn")
                    li = social.get('linkedin', {})
                    li_text = li.get('post', '') if isinstance(li, dict) else li
                    st.text_area("LinkedIn Post", li_text, height=150, key="li_out")
                    st.download_button("📥 LinkedIn", li_text, f"{safe_title}_linkedin.txt", use_container_width=True)
                    
                    st.markdown("#### 📘 Facebook")
                    fb = social.get('facebook', {})
                    fb_text = fb.get('post', '') if isinstance(fb, dict) else fb
                    st.text_area("Facebook Post", fb_text, height=150, key="fb_out")
                    st.download_button("📥 Facebook", fb_text, f"{safe_title}_facebook.txt", use_container_width=True)
                
                with sc2:
                    st.markdown("#### 🐦 Twitter/X")
                    tw = social.get('twitter', {})
                    thread = tw.get('thread', []) if isinstance(tw, dict) else []
                    tw_text = "\n\n---\n\n".join(thread) if thread else tw.get('single', '')
                    st.text_area("Twitter Thread", tw_text, height=150, key="tw_out")
                    st.download_button("📥 Twitter", tw_text, f"{safe_title}_twitter.txt", use_container_width=True)
                    
                    st.markdown("#### 📸 Instagram")
                    ig = social.get('instagram', {})
                    ig_text = ig.get('caption', '') if isinstance(ig, dict) else ig
                    st.text_area("Instagram Caption", ig_text, height=150, key="ig_out")
                    st.download_button("📥 Instagram", ig_text, f"{safe_title}_instagram.txt", use_container_width=True)
            except Exception as e:
                st.error(f"Parse error: {e}")
                st.text(social_result)

with tab_social:
    st.markdown("### 📱 Quick Social Post Generator")
    stopic = st.text_input("Topic", key="social_topic", placeholder="What do you want to post about?")
    platform = st.selectbox("Platform", ["All Platforms", "LinkedIn", "Twitter/X", "Facebook", "Instagram"])
    style = st.selectbox("Style", ["Professional", "Casual", "Engaging", "Inspirational", "Humorous"])
    if st.button("📱 Generate Posts", type="primary", use_container_width=True, key="social_gen"):
        if stopic:
            st.session_state.working_on = "Creating posts..."
            result, _ = call_claude(f"Create {platform} posts about '{stopic}'. Style: {style}. Include emojis, hashtags, compelling hooks, and CTAs. For Twitter, keep under 280 chars per tweet.", action="social_quick")
            st.session_state.working_on = None
            if not str(result).startswith("Error"):
                st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
            else:
                st.error(result)

with tab_email:
    st.markdown("### 📧 Email Generator")
    etype = st.selectbox("Type", ["Newsletter", "Cold Outreach", "Follow-up", "Nurture Sequence", "Event Invite", "Product Announcement"])
    etopic = st.text_input("Topic/Purpose", key="email_topic", placeholder="What's the email about?")
    eaudience = st.text_input("Audience", key="email_audience", placeholder="Who is receiving this?")
    if st.button("📧 Generate Email", type="primary", use_container_width=True, key="email_gen"):
        if etopic:
            st.session_state.working_on = "Writing email..."
            result, _ = call_claude(f"Write a {etype} email about '{etopic}' for {eaudience or 'general audience'}. Include: subject line, preview text, greeting, body with clear sections, CTA, and sign-off. Make it professional and action-oriented.", action="email_gen")
            st.session_state.working_on = None
            if not str(result).startswith("Error"):
                st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
                st.download_button("📥 Download", result, "email.txt", use_container_width=True)
            else:
                st.error(result)

with tab_video:
    st.markdown("### 🎬 Video Script Generator")
    vtopic = st.text_input("Video Topic", key="video_topic", placeholder="What's the video about?")
    vformat = st.selectbox("Format", ["YouTube Long-form", "YouTube Short", "TikTok/Reel", "Podcast Outline", "Webinar Script", "Course Module"])
    vduration = st.selectbox("Duration", ["30 seconds", "1 minute", "3-5 minutes", "10+ minutes", "30+ minutes"])
    if st.button("🎬 Generate Script", type="primary", use_container_width=True, key="video_gen"):
        if vtopic:
            st.session_state.working_on = "Writing script..."
            result, _ = call_claude(f"Create a {vformat} script about '{vtopic}'. Duration: {vduration}. Include: hook, intro, main content with timestamps, key points, transitions, CTA, and outro. Add [B-ROLL], [GRAPHIC], [CUT] notes for editing.", action="video_gen")
            st.session_state.working_on = None
            if not str(result).startswith("Error"):
                st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
                st.download_button("📥 Download Script", result, "video_script.txt", use_container_width=True)
            else:
                st.error(result)

with tab_refine:
    st.markdown("### ✨ Content Refiner")
    content = st.text_area("Paste content to refine", height=200, key="refine_content")
    goal = st.selectbox("Refinement Goal", ["Improve clarity & flow", "Make more concise", "Expand & add detail", "Fix grammar & spelling", "Change tone to professional", "Change tone to casual", "Optimize for SEO", "Make more engaging"])
    if st.button("✨ Refine Content", type="primary", use_container_width=True, key="refine_btn"):
        if content:
            st.session_state.working_on = "Refining..."
            result, _ = call_claude(f"Refine this content. Goal: {goal}.\n\nORIGINAL:\n{content}\n\nProvide the refined version and briefly explain what you changed.", action="refine")
            st.session_state.working_on = None
            if not str(result).startswith("Error"):
                st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
            else:
                st.error(result)

with tab_repurpose:
    st.markdown("### ♻️ Content Repurposer")
    original = st.text_area("Paste original content", height=200, key="repurpose_content")
    formats = st.multiselect("Repurpose to", ["LinkedIn Post", "Twitter Thread", "Email Newsletter", "Blog Summary", "Video Script", "Podcast Talking Points", "Infographic Outline", "Slide Deck Outline"])
    if st.button("♻️ Repurpose", type="primary", use_container_width=True, key="repurpose_btn"):
        if original and formats:
            st.session_state.working_on = "Repurposing..."
            result, _ = call_claude(f"Repurpose this content into these formats: {', '.join(formats)}.\n\nORIGINAL:\n{original}\n\nProvide each format clearly labeled and optimized for that platform/purpose.", action="repurpose")
            st.session_state.working_on = None
            if not str(result).startswith("Error"):
                st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
            else:
                st.error(result)

# Feedback widget
st.markdown('<div style="height:60px;"></div>', unsafe_allow_html=True)
_, _, _, fb = st.columns([4, 1, 1, 1])
with fb:
    with st.popover("💬 Feedback"):
        st.markdown("**Send Feedback**")
        ft = st.segmented_control("Type", ["🐛 Bug", "✨ Feature", "💬 General"], default="💬 General", label_visibility="collapsed")
        fm = st.text_area("Message", height=100, placeholder="...", label_visibility="collapsed", key="fb_msg")
        if st.button("Send", type="primary", use_container_width=True, key="fb_send"):
            if fm:
                if submit_feedback("content", ft.split()[1].lower() if ft else "general", fm):
                    st.success("Thanks! 🙏")
                else:
                    st.error("Failed")
