"""
Sharp Suite - Streamlit Community Cloud Entry Point
====================================================
Deploy to: https://share.streamlit.io

This is a simple redirect/launcher. For full testing, 
use the individual app files directly.

To test on Streamlit Community Cloud:
1. Go to share.streamlit.io
2. Connect your GitHub repo: sharphuman/sharp-suite
3. Set main file path to: apps/sharp_portal/app.py (or any app)
4. Add secrets for ANTHROPIC_API_KEY, SUPABASE_SERVICE_KEY
"""
import streamlit as st

st.set_page_config(page_title="Sharp Suite", page_icon="🏠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
.stApp { background: #1a1a1a; font-family: 'Nunito', sans-serif; }
h1, h2, h3 { color: white !important; }
p, span, label, li { color: #e5e5e5 !important; }
a { color: #60a5fa !important; }
.app-card { background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); border-radius: 12px; padding: 20px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 40px 0;">
    <img src="https://sharphuman.com/logo1-3.png" style="width:80px; margin-bottom:20px;">
    <h1 style="margin:0; font-size:2.5rem;">Sharp Suite</h1>
    <p style="color:#9ca3af; font-size:1.2rem;">Your AI Recruiting Toolkit</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 🧪 Testing on Streamlit Community Cloud")

st.markdown("""
To test individual apps on Streamlit Community Cloud:

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select repo: `sharphuman/sharp-suite`
4. Set **Main file path** to one of:
""")

apps = [
    ("Portal", "apps/sharp_portal/app.py", "Main dashboard & login"),
    ("JD Writer", "apps/sharp_jd/app.py", "AI job descriptions"),
    ("CV Screener", "apps/sharp_screen/app.py", "Resume screening"),
    ("Interview", "apps/sharp_interview/app.py", "Interview prep & eval"),
    ("Outreach", "apps/sharp_reach/app.py", "Sourcing & sequences"),
    ("Content", "apps/sharp_content/app.py", "Blog & social content"),
    ("Sales", "apps/sharp_sales/app.py", "Sales call analysis"),
]

for name, path, desc in apps:
    st.markdown(f"""
    <div class="app-card">
        <strong style="color:#60a5fa; font-size:1.1rem;">{name}</strong><br>
        <code style="background:#2a2a2a; padding:4px 8px; border-radius:4px; color:#f472b6;">{path}</code><br>
        <span style="color:#9ca3af;">{desc}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 🔑 Required Secrets")
st.markdown("""
Add these in Streamlit Cloud → App settings → Secrets:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
SUPABASE_SERVICE_KEY = "eyJ..."
SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJ..."
GOD_PASSWORD = "G0DHum@n101!!!"
```
""")

st.markdown("---")

st.markdown("## 🚀 Production URLs (Railway)")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    - [demo.sharphuman.com](https://demo.sharphuman.com) - Portal
    - [jd.sharphuman.com](https://jd.sharphuman.com) - JD Writer
    - [screen.sharphuman.com](https://screen.sharphuman.com) - CV Screener
    - [interview.sharphuman.com](https://interview.sharphuman.com) - Interview
    """)
with col2:
    st.markdown("""
    - [outreach.sharphuman.com](https://outreach.sharphuman.com) - Outreach
    - [content.sharphuman.com](https://content.sharphuman.com) - Content
    - [sales.sharphuman.com](https://sales.sharphuman.com) - Sales
    - [admin.sharphuman.com](https://admin.sharphuman.com) - Admin
    """)
