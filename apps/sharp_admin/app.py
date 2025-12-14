"""Sharp Admin - SaaS Management Dashboard"""
import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os

# ============================================
# CONFIGURATION
# ============================================

SUPABASE_URL = "https://qkjtprqgblnfftrotyks.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFranRwcnFnYmxuZmZ0cm90eWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzNTgzNDAsImV4cCI6MjA4MDkzNDM0MH0.pVzSq4M5i58zBGl7OPDhNL9qYBcg-bz8MVrBI5MQSkw"
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", SUPABASE_ANON_KEY)
GOD_PASSWORD = "G0DHum@n101!!!"

# ============================================
# STYLES
# ============================================

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
* { font-family: 'Nunito', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0a0f, #0f0f1a); }
h1, h2, h3 { color: white !important; }
p, span, label, .stMarkdown { color: #e5e5e5 !important; }

.metric-card {
    background: linear-gradient(135deg, #12121a, #1a1a2e);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
}
.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #6366f1;
}
.metric-label {
    font-size: 0.9rem;
    color: #9ca3af;
    margin-top: 4px;
}
.metric-change {
    font-size: 0.8rem;
    margin-top: 8px;
}
.metric-change.positive { color: #10b981; }
.metric-change.negative { color: #ef4444; }

.alert-card {
    background: rgba(0,0,0,0.3);
    border-left: 4px solid;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
}
.alert-card.critical { border-color: #ef4444; }
.alert-card.warning { border-color: #f59e0b; }
.alert-card.info { border-color: #3b82f6; }

.user-row {
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.progress-bar {
    background: rgba(99,102,241,0.2);
    border-radius: 4px;
    height: 24px;
    overflow: hidden;
}
.progress-fill {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    height: 100%;
    display: flex;
    align-items: center;
    padding-left: 8px;
    font-size: 0.75rem;
    color: white;
}

.stTextInput>div>div>input, .stSelectbox>div>div>div {
    background: #12121a !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    color: white !important;
}
.stButton>button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
}
</style>
"""

# ============================================
# SUPABASE HELPERS
# ============================================

def supabase_request(endpoint: str, method: str = "GET", data: dict = None) -> Dict[str, Any]:
    """Make a request to Supabase REST API."""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PATCH":
            r = requests.patch(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, timeout=10)
        
        if r.status_code in [200, 201]:
            return {"success": True, "data": r.json() if r.text else []}
        return {"success": False, "error": r.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# DATA FETCHING
# ============================================

def get_user_count() -> Dict[str, int]:
    """Get total and active user counts."""
    result = supabase_request("user_profiles?select=id,is_active,created_at")
    if result.get("success"):
        users = result["data"]
        total = len(users)
        active = len([u for u in users if u.get("is_active")])
        # New this month
        month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        new_mtd = len([u for u in users if u.get("created_at", "") > month_ago])
        return {"total": total, "active": active, "new_mtd": new_mtd}
    return {"total": 0, "active": 0, "new_mtd": 0}


def get_active_today() -> int:
    """Get count of users active today."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0).isoformat()
    result = supabase_request(f"usage_logs?select=user_id&created_at=gte.{today}")
    if result.get("success"):
        unique_users = set(log.get("user_id") for log in result["data"])
        return len(unique_users)
    return 0


def get_total_tokens_used() -> Dict[str, Any]:
    """Get total tokens used this month."""
    result = supabase_request("user_profiles?select=tokens_used_this_month")
    if result.get("success"):
        total = sum(u.get("tokens_used_this_month", 0) for u in result["data"])
        # Estimate cost at $0.01 per 1000 tokens (rough average)
        cost = total * 0.00001
        return {"tokens": total, "cost": cost}
    return {"tokens": 0, "cost": 0}


def get_app_usage() -> List[Dict]:
    """Get usage breakdown by app."""
    month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
    result = supabase_request(f"usage_logs?select=app&created_at=gte.{month_ago}")
    if result.get("success"):
        apps = {}
        for log in result["data"]:
            app = log.get("app", "unknown")
            apps[app] = apps.get(app, 0) + 1
        
        # Sort by usage
        sorted_apps = sorted(apps.items(), key=lambda x: x[1], reverse=True)
        total = sum(apps.values()) or 1
        
        return [{"app": app, "uses": count, "percent": (count/total)*100} for app, count in sorted_apps]
    return []


def get_pending_alerts() -> List[Dict]:
    """Get unacknowledged alerts."""
    result = supabase_request("alerts?acknowledged=eq.false&order=created_at.desc&limit=20")
    if result.get("success"):
        alerts = result["data"]
        # Get user emails
        for alert in alerts:
            user_result = supabase_request(f"user_profiles?id=eq.{alert.get('user_id')}&select=email")
            if user_result.get("success") and user_result["data"]:
                alert["user_email"] = user_result["data"][0].get("email", "Unknown")
            else:
                alert["user_email"] = "Unknown"
        return alerts
    return []


def get_users_list() -> List[Dict]:
    """Get list of all users with stats."""
    result = supabase_request("user_profiles?order=created_at.desc")
    if result.get("success"):
        users = result["data"]
        
        # Get usage stats for each user
        for user in users:
            # Get last activity
            usage_result = supabase_request(
                f"usage_logs?user_id=eq.{user['id']}&order=created_at.desc&limit=1"
            )
            if usage_result.get("success") and usage_result["data"]:
                user["last_activity"] = usage_result["data"][0].get("created_at")
            else:
                user["last_activity"] = None
            
            # Get total uses
            uses_result = supabase_request(
                f"usage_logs?user_id=eq.{user['id']}&select=id"
            )
            user["total_uses"] = len(uses_result.get("data", []))
            
            # Get active alerts count
            alerts_result = supabase_request(
                f"alerts?user_id=eq.{user['id']}&acknowledged=eq.false&select=id"
            )
            user["alert_count"] = len(alerts_result.get("data", []))
        
        return users
    return []


def get_revenue_stats() -> Dict[str, Any]:
    """Calculate revenue stats based on user plans."""
    result = supabase_request("user_profiles?select=plan,is_active")
    if result.get("success"):
        plans = {"free": 0, "pro": 0, "team": 0, "enterprise": 0, "god": 0}
        plan_prices = {"free": 0, "pro": 29, "team": 99, "enterprise": 299, "god": 0}
        
        for user in result["data"]:
            if user.get("is_active"):
                plan = user.get("plan", "free")
                plans[plan] = plans.get(plan, 0) + 1
        
        mrr = sum(plans[p] * plan_prices[p] for p in plans)
        return {"plans": plans, "mrr": mrr}
    return {"plans": {}, "mrr": 0}


def acknowledge_alert(alert_id: str) -> bool:
    """Mark an alert as acknowledged."""
    result = supabase_request(
        f"alerts?id=eq.{alert_id}",
        "PATCH",
        {"acknowledged": True, "acknowledged_at": datetime.utcnow().isoformat()}
    )
    return result.get("success", False)


def update_user_plan(user_id: str, new_plan: str) -> bool:
    """Update a user's plan."""
    plan_limits = {
        "free": {"monthly_token_limit": 5000, "seats": 1},
        "pro": {"monthly_token_limit": 50000, "seats": 1},
        "team": {"monthly_token_limit": 200000, "seats": 5},
        "enterprise": {"monthly_token_limit": 999999999, "seats": 999},
        "god": {"monthly_token_limit": 999999999, "seats": 999},
    }
    
    data = {"plan": new_plan, **plan_limits.get(new_plan, {})}
    result = supabase_request(f"user_profiles?id=eq.{user_id}", "PATCH", data)
    return result.get("success", False)


def toggle_user_active(user_id: str, is_active: bool) -> bool:
    """Enable or disable a user."""
    result = supabase_request(f"user_profiles?id=eq.{user_id}", "PATCH", {"is_active": is_active})
    return result.get("success", False)


# ============================================
# AUTH
# ============================================

def init_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "is_god" not in st.session_state:
        st.session_state.is_god = False


def render_auth():
    st.markdown(STYLES, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:60px 0 40px;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:80px;margin-bottom:20px;">
            <h1>Admin Dashboard</h1>
            <p style="color:#9ca3af;">GOD mode access required</p>
        </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("Password", type="password", key="admin_pw")
        if st.button("Access Dashboard", use_container_width=True):
            if password == GOD_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.is_god = True
                st.rerun()
            else:
                st.error("Invalid password")


# ============================================
# DASHBOARD UI
# ============================================

def render_dashboard():
    st.markdown(STYLES, unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:16px;padding:20px 0;">
            <img src="https://sharphuman.com/logo1-3.png" style="width:50px;">
            <div>
                <h1 style="margin:0;">Sharp Suite Admin</h1>
                <p style="color:#9ca3af;margin:0;">SaaS Management Dashboard</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # Metrics Row
    user_stats = get_user_count()
    active_today = get_active_today()
    token_stats = get_total_tokens_used()
    revenue_stats = get_revenue_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{user_stats['total']}</div>
            <div class="metric-label">Total Users</div>
            <div class="metric-change positive">+{user_stats['new_mtd']} this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_today}</div>
            <div class="metric-label">Active Today</div>
            <div class="metric-change">Last 24 hours</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{token_stats['tokens']:,}</div>
            <div class="metric-label">Tokens Used (MTD)</div>
            <div class="metric-change">${token_stats['cost']:.2f} estimated cost</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${revenue_stats['mrr']:,}</div>
            <div class="metric-label">MRR</div>
            <div class="metric-change positive">Monthly recurring revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🚨 Alerts", "👥 Users", "📊 App Usage", "💰 Revenue"])
    
    # ALERTS TAB
    with tab1:
        st.markdown("### Pending Alerts")
        alerts = get_pending_alerts()
        
        if not alerts:
            st.success("✅ No pending alerts!")
        else:
            for alert in alerts:
                severity = alert.get("severity", "warning")
                alert_type = alert.get("alert_type", "unknown")
                details = json.loads(alert.get("details", "{}")) if alert.get("details") else {}
                created = alert.get("created_at", "")[:16].replace("T", " ")
                
                icon = "🔴" if severity == "critical" else "⚠️" if severity == "warning" else "ℹ️"
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="alert-card {severity}">
                        <strong>{icon} {alert_type.replace('_', ' ').title()}</strong><br>
                        <span style="color:#9ca3af;">User: {alert.get('user_email', 'Unknown')}</span><br>
                        <span style="color:#6b7280;font-size:0.8rem;">{created}</span>
                        {f"<br><code>{json.dumps(details)}</code>" if details else ""}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("✓ Ack", key=f"ack_{alert['id']}"):
                        if acknowledge_alert(alert["id"]):
                            st.rerun()
    
    # USERS TAB
    with tab2:
        st.markdown("### User Management")
        
        users = get_users_list()
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            plan_filter = st.selectbox("Filter by Plan", ["All", "free", "pro", "team", "enterprise", "god"])
        with col2:
            search = st.text_input("Search email", "")
        
        # Filter users
        filtered_users = users
        if plan_filter != "All":
            filtered_users = [u for u in filtered_users if u.get("plan") == plan_filter]
        if search:
            filtered_users = [u for u in filtered_users if search.lower() in u.get("email", "").lower()]
        
        st.markdown(f"**Showing {len(filtered_users)} users**")
        
        for user in filtered_users[:50]:  # Limit to 50 for performance
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                alert_badge = "🚨" if user.get("alert_count", 0) > 0 else ""
                active_badge = "🟢" if user.get("is_active") else "🔴"
                st.markdown(f"{active_badge} **{user.get('email', 'Unknown')}** {alert_badge}")
            
            with col2:
                st.markdown(f"`{user.get('plan', 'free')}`")
            
            with col3:
                st.markdown(f"{user.get('total_uses', 0)} uses")
            
            with col4:
                tokens = user.get("tokens_used_this_month", 0)
                limit = user.get("monthly_token_limit", 5000)
                pct = min((tokens / limit) * 100, 100) if limit > 0 else 0
                st.markdown(f"{pct:.0f}% tokens")
            
            with col5:
                last = user.get("last_activity")
                if last:
                    # Parse and format
                    try:
                        dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                        diff = datetime.utcnow() - dt.replace(tzinfo=None)
                        if diff.days > 0:
                            st.markdown(f"{diff.days}d ago")
                        elif diff.seconds > 3600:
                            st.markdown(f"{diff.seconds // 3600}h ago")
                        else:
                            st.markdown(f"{diff.seconds // 60}m ago")
                    except:
                        st.markdown("—")
                else:
                    st.markdown("Never")
        
        # User Actions (expandable)
        st.markdown("---")
        with st.expander("⚙️ User Actions"):
            user_emails = [u.get("email") for u in users]
            selected_email = st.selectbox("Select User", user_emails)
            
            if selected_email:
                selected_user = next((u for u in users if u.get("email") == selected_email), None)
                if selected_user:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        new_plan = st.selectbox("Change Plan", ["free", "pro", "team", "enterprise", "god"], 
                                                index=["free", "pro", "team", "enterprise", "god"].index(selected_user.get("plan", "free")))
                        if st.button("Update Plan"):
                            if update_user_plan(selected_user["id"], new_plan):
                                st.success(f"Updated to {new_plan}")
                                st.rerun()
                    
                    with col2:
                        is_active = selected_user.get("is_active", True)
                        if st.button("Disable User" if is_active else "Enable User"):
                            if toggle_user_active(selected_user["id"], not is_active):
                                st.success("User status updated")
                                st.rerun()
    
    # APP USAGE TAB
    with tab3:
        st.markdown("### App Usage (Last 30 Days)")
        
        app_usage = get_app_usage()
        
        if not app_usage:
            st.info("No usage data yet")
        else:
            for app_stat in app_usage:
                app_name = app_stat["app"].replace("sharp_", "").title()
                uses = app_stat["uses"]
                pct = app_stat["percent"]
                
                st.markdown(f"""
                <div style="margin: 12px 0;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span>{app_name}</span>
                        <span style="color:#9ca3af;">{uses:,} uses ({pct:.0f}%)</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width:{pct}%;">{pct:.0f}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # REVENUE TAB
    with tab4:
        st.markdown("### Revenue Breakdown")
        
        plans = revenue_stats.get("plans", {})
        plan_prices = {"free": 0, "pro": 29, "team": 99, "enterprise": 299, "god": 0}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Users by Plan")
            for plan, count in plans.items():
                if count > 0:
                    st.markdown(f"**{plan.title()}**: {count} users × ${plan_prices[plan]} = **${count * plan_prices[plan]}**")
        
        with col2:
            st.markdown("#### Summary")
            total_users = sum(plans.values())
            paying_users = sum(plans[p] for p in ["pro", "team", "enterprise"])
            mrr = revenue_stats["mrr"]
            
            st.markdown(f"""
            - **Total Users**: {total_users}
            - **Paying Users**: {paying_users}
            - **Conversion Rate**: {(paying_users/total_users*100) if total_users > 0 else 0:.1f}%
            - **MRR**: ${mrr:,}
            - **ARR**: ${mrr * 12:,}
            """)
        
        st.markdown("---")
        st.markdown("#### Cost Analysis")
        token_stats = get_total_tokens_used()
        st.markdown(f"""
        - **Tokens Used (MTD)**: {token_stats['tokens']:,}
        - **Estimated API Cost**: ${token_stats['cost']:.2f}
        - **Gross Margin**: {((mrr - token_stats['cost']) / mrr * 100) if mrr > 0 else 0:.1f}%
        """)


# ============================================
# MAIN
# ============================================

st.set_page_config(page_title="Sharp Admin", page_icon="⚙️", layout="wide")
init_session()

if not st.session_state.authenticated:
    render_auth()
else:
    render_dashboard()
