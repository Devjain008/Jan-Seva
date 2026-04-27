import streamlit as st
import requests
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from frontend.config import TRANSLATIONS, API_BASE

def t(key):
    lang = st.session_state.get("language", "en")
    tr = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return tr.get(key, key)

def get_greeting():
    hour = datetime.now().hour
    lang = st.session_state.get("language", "en")
    if hour < 12:
        return t("greeting_morning")
    elif hour < 17:
        return t("greeting_afternoon")
    else:
        return t("greeting_evening")

def show_user_dashboard():
    user = st.session_state.get("user", {})
    lang = st.session_state.get("language", "en")
    name = user.get("name", "User")
    user_id = user.get("user_id")
    greeting = get_greeting()

    # Hero
    st.markdown(f"""
    <div class="hero">
        <h1>{greeting}, {name} 👋</h1>
        <p>{'आपकी सेवा में तत्पर हैं' if lang=='hi' else 'We are here to serve you'}</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    try:
        stats = requests.get(f"{API_BASE}/complaints/stats").json()
        user_comps = requests.get(f"{API_BASE}/complaints/user/{user_id}").json()
        user_total = len(user_comps) if isinstance(user_comps, list) else 0
        user_resolved = len([c for c in (user_comps if isinstance(user_comps, list) else []) if c.get("status") == "resolved"])
        user_pending = len([c for c in (user_comps if isinstance(user_comps, list) else []) if c.get("status") == "pending"])
    except:
        user_total, user_resolved, user_pending = 0, 0, 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-number" style="color:#6366f1">{user_total}</div>
            <div class="stat-label">{t('total')}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-number" style="color:#d97706">{user_pending}</div>
            <div class="stat-label">{t('pending')}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-number" style="color:#16a34a">{user_resolved}</div>
            <div class="stat-label">{t('resolved')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="action-card">
            <div class="action-icon">📢</div>
            <div class="action-label">{t('file_complaint')}</div>
        </div>""", unsafe_allow_html=True)
        if st.button(t("file_complaint"), key="dash_file", use_container_width=True):
            st.session_state.screen = "file_complaint"
            st.rerun()
    
    with col2:
        st.markdown(f"""<div class="action-card">
            <div class="action-icon">🔍</div>
            <div class="action-label">{t('track_complaint')}</div>
        </div>""", unsafe_allow_html=True)
        if st.button(t("track_complaint"), key="dash_track", use_container_width=True):
            st.session_state.screen = "tracking"
            st.rerun()
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""<div class="action-card">
            <div class="action-icon">📜</div>
            <div class="action-label">{t('govt_schemes')}</div>
        </div>""", unsafe_allow_html=True)
        if st.button(t("govt_schemes"), key="dash_schemes", use_container_width=True):
            st.session_state.screen = "schemes"
            st.rerun()
    
    with col4:
        st.markdown(f"""<div class="action-card">
            <div class="action-icon">🤖</div>
            <div class="action-label">{t('ai_assistant')}</div>
        </div>""", unsafe_allow_html=True)
        if st.button(t("ai_assistant"), key="dash_ai", use_container_width=True):
            st.session_state.screen = "assistant"
            st.rerun()

    # Recent complaints
    if user_total > 0:
        st.markdown(f'<div class="section-header">📋 {t("your_complaints")}</div>', unsafe_allow_html=True)
        try:
            comps = requests.get(f"{API_BASE}/complaints/user/{user_id}").json()
            if isinstance(comps, list):
                for c in comps[:3]:
                    status_class = {"pending": "status-pending", "in_progress": "status-inprogress", "resolved": "status-resolved"}.get(c.get("status",""), "status-pending")
                    priority_class = {"high": "badge-high", "medium": "badge-medium", "low": "badge-low"}.get(c.get("priority",""), "badge-medium")
                    st.markdown(f"""
                    <div class="complaint-item">
                        <div class="complaint-id">#{c.get('complaint_id','')}</div>
                        <div class="complaint-title">{c.get('category','').title()} — {c.get('description','')}</div>
                        <div class="complaint-meta">
                            <span class="{status_class}">{c.get('status','').replace('_',' ').title()}</span>
                            <span class="{priority_class}">{c.get('priority','').title()}</span>
                            <span>📍 {c.get('location','N/A')}</span>
                            <span>🕐 {c.get('created_at','')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except:
            pass

    # Notifications
    try:
        notifs = requests.get(f"{API_BASE}/schemes/user/notifications/{user_id}").json()
        if isinstance(notifs, list) and notifs:
            unread = [n for n in notifs if not n.get("is_read")]
            if unread:
                st.markdown(f'<div class="section-header">🔔 {t("notifications")} ({len(unread)})</div>', unsafe_allow_html=True)
                for n in unread[:3]:
                    st.markdown(f"""
                    <div class="notif-card">
                        <div class="notif-dot"></div>
                        <div>
                            <div class="notif-title">{n.get('title','')}</div>
                            <div class="notif-msg">{n.get('message','')}</div>
                            <div class="notif-time">🕐 {n.get('time','')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    except:
        pass

def show_official_dashboard():
    official = st.session_state.get("official", {})
    dept_id = official.get("department_id")
    name = official.get("name", "Official")
    official_id = official.get("official_id")

    st.markdown(f"""
    <div class="hero">
        <h1>🏢 {name}</h1>
        <p>{official.get('department', 'Department')} — Official Portal</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        comps = requests.get(f"{API_BASE}/complaints/department/{dept_id}").json()
        if not isinstance(comps, list):
            comps = []
    except:
        comps = []

    try:
        perf = requests.get(f"{API_BASE}/admin/officials/{official_id}/performance").json() if official_id else {}
    except:
        perf = {}
    try:
        lb = requests.get(f"{API_BASE}/admin/leaderboard").json()
    except:
        lb = {}

    total = len(comps)
    pending = len([c for c in comps if c.get("status") == "pending"])
    inprog = len([c for c in comps if c.get("status") == "in_progress"])
    resolved = len([c for c in comps if c.get("status") == "resolved"])

    col1, col2, col3, col4 = st.columns(4)
    for col, label, val, color in [(col1, t("total"), total, "#6366f1"), (col2, t("pending"), pending, "#d97706"), (col3, t("in_progress"), inprog, "#2563eb"), (col4, t("resolved"), resolved, "#16a34a")]:
        with col:
            col.markdown(f"""<div class="stat-card">
                <div class="stat-number" style="color:{color}">{val}</div>
                <div class="stat-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">📋 Complaints</div>', unsafe_allow_html=True)
    if perf:
        stars = "⭐" * int(round(perf.get("avg_rating", 0)))
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Average Rating", f"{perf.get('avg_rating', 0):.2f}")
        c2.metric("Assigned", perf.get("total_assigned", 0))
        c3.metric("Resolved", perf.get("total_resolved", 0))
        c4.metric("Success Rate", f"{perf.get('success_rate', 0):.1f}%")
        st.caption(f"Rating Stars: {stars or 'No ratings yet'}")
        if not perf.get("eligible_for_ranking"):
            st.info(f"Need at least {perf.get('min_resolved_threshold', 5)} resolved complaints to enter leaderboard.")
        elif perf.get("rank_in_department"):
            st.success(f"Department Rank: #{perf.get('rank_in_department')}")

    dept_board = []
    if isinstance(lb, dict):
        dept_board = lb.get("department_wise", {}).get(str(dept_id), [])
    if dept_board:
        st.markdown("### Department Leaderboard")
        for row in dept_board[:10]:
            st.markdown(
                f"**#{row.get('rank')}** {row.get('name')} | {row.get('department')} | "
                f"⭐ {row.get('avg_rating', 0):.2f} | Resolved: {row.get('total_resolved', 0)}"
            )

    filter_status = st.selectbox("Filter by status", ["all", "pending", "in_progress", "resolved"], key="off_filter")
    
    filtered = comps if filter_status == "all" else [c for c in comps if c.get("status") == filter_status]
    
    for c in filtered:
        priority_class = {"high": "badge-high", "medium": "badge-medium", "low": "badge-low"}.get(c.get("priority",""), "badge-medium")
        status_class = {"pending": "status-pending", "in_progress": "status-inprogress", "resolved": "status-resolved"}.get(c.get("status",""), "")
        
        with st.expander(f"#{c.get('complaint_id','')} — {c.get('category','').title()} | {c.get('user_name','')} | {c.get('created_at','')}"):
            st.markdown(f"""
            <div class="official-complaint {c.get('priority','')}">
                <div style="display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap;">
                    <span class="{priority_class}">{c.get('priority','').title()} Priority</span>
                    <span class="{status_class}">{c.get('status','').replace('_',' ').title()}</span>
                    <span>📍 {c.get('location','N/A')}</span>
                </div>
                <div style="font-size:0.9rem;">{c.get('description','')}</div>
                <div style="font-size:0.78rem;margin-top:6px;opacity:0.7;">
                    👤 {c.get('user_name','')} · 📞 {c.get('user_phone','')} · 🕐 {c.get('created_at','')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 In Progress", key=f"inprog_{c.get('complaint_id')}"):
                    try:
                        requests.put(f"{API_BASE}/complaints/{c.get('complaint_id')}/status", 
                                   json={"status": "in_progress", "note": "Being processed by the department.", "official_id": official_id})
                        st.success("Updated!")
                        st.rerun()
                    except: st.error("Error")
            with col2:
                if st.button("✅ Resolve", key=f"resolve_{c.get('complaint_id')}"):
                    try:
                        requests.put(f"{API_BASE}/complaints/{c.get('complaint_id')}/status",
                                   json={"status": "resolved", "note": "Complaint resolved by department.", "official_id": official_id})
                        st.success("Resolved!")
                        st.rerun()
                    except: st.error("Error")
            with col3:
                if st.button("❌ Reject", key=f"reject_{c.get('complaint_id')}"):
                    try:
                        requests.put(f"{API_BASE}/complaints/{c.get('complaint_id')}/status",
                                   json={"status": "rejected", "note": "Complaint rejected.", "official_id": official_id})
                        st.warning("Rejected")
                        st.rerun()
                    except: st.error("Error")
