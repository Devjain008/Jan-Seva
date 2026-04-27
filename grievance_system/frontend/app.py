import streamlit as st
import requests
import sys, os

# ── path setup ───────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from frontend.styles import get_css
from frontend.config import TRANSLATIONS, API_BASE

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Jan Seva Portal | जन सेवा पोर्टल",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="auto",
)

# ── session defaults ──────────────────────────────────────────────────────────
DEFAULTS = {
    "screen": "language",
    "language": "en",
    "dark_mode": False,
    "role": None,       # "user" | "official" | "admin"
    "user": None,
    "official": None,
    "admin": None,
    "otp_sent": False,
    "chat_history": [],
    "selected_category": "other",
    "location_text": "",
    "loc_lat": 23.2599,
    "loc_lon": 77.4126,
    "voice_captured": "",
    "viewing_dept_id": None,
    "viewing_dept_name": "",
    "viewing_dept_code": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── inject CSS ────────────────────────────────────────────────────────────────
st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)

# ── translation helper ────────────────────────────────────────────────────────
def t(key):
    lang = st.session_state.language
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# ── sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # App brand
        st.markdown("""
        <div style="text-align:center;padding:20px 0 10px 0;">
            <div style="font-size:3rem;">🏛️</div>
            <div style="font-weight:900;font-size:1.1rem;background:linear-gradient(135deg,#6366f1,#06b6d4);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">Jan Seva Portal</div>
            <div style="font-size:0.75rem;opacity:0.6;margin-top:2px;">जन सेवा पोर्टल</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Dark / Light toggle
        dark_label = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
        if st.button(dark_label, key="sb_dark", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        # Language toggle
        lang_label = "🇬🇧 Switch to English" if st.session_state.language == "hi" else "🇮🇳 हिंदी में बदलें"
        if st.button(lang_label, key="sb_lang", use_container_width=True):
            st.session_state.language = "hi" if st.session_state.language == "en" else "en"
            st.rerun()

        st.markdown("---")

        role = st.session_state.role

        # ── USER nav ──────────────────────────────────────────────────────────
        if role == "user":
            user = st.session_state.user or {}
            st.markdown(f"""
            <div style="text-align:center;padding:12px;background:{'#1a1a2e' if st.session_state.dark_mode else '#f0f4ff'};
                        border-radius:16px;margin-bottom:14px;">
                <div style="font-size:2rem;">👤</div>
                <div style="font-weight:800;font-size:0.95rem;">{user.get('name','User')}</div>
                <div style="font-size:0.72rem;opacity:0.6;">{user.get('phone','')}</div>
            </div>
            """, unsafe_allow_html=True)

            nav_items = [
                ("📢", t("file_complaint"), "file_complaint"),
                ("🔍", t("track_complaint"),"tracking"),
                ("📜", t("govt_schemes"),   "schemes"),
                ("🔔", t("notifications"),  "notifications"),
            ]
            for icon, label, screen in nav_items:
                active = "nav-active" if st.session_state.screen == screen else ""
                if st.button(f"{icon}  {label}", key=f"nav_{screen}", use_container_width=True):
                    st.session_state.screen = screen
                    st.rerun()

            st.markdown("---")
            if st.button(f"🔓 {t('logout')}", key="sb_logout_user", use_container_width=True):
                _logout()

        # ── OFFICIAL nav ──────────────────────────────────────────────────────
        elif role == "official":
            off = st.session_state.official or {}
            st.markdown(f"""
            <div style="text-align:center;padding:12px;background:{'#1a1a2e' if st.session_state.dark_mode else '#f0f4ff'};
                        border-radius:16px;margin-bottom:14px;">
                <div style="font-size:2rem;">🏢</div>
                <div style="font-weight:800;font-size:0.95rem;">{off.get('name','Official')}</div>
                <div style="font-size:0.72rem;opacity:0.6;">{off.get('department','Dept')}</div>
            </div>
            """, unsafe_allow_html=True)

            nav_items = [
                ("📊", "Dashboard",         "official_dashboard"),
                ("📢", t("all_complaints"), "official_complaints"),
                ("📜", t("govt_schemes"),   "schemes"),
            ]
            for icon, label, screen in nav_items:
                if st.button(f"{icon}  {label}", key=f"nav_{screen}", use_container_width=True):
                    st.session_state.screen = screen
                    st.rerun()

            st.markdown("---")
            if st.button(f"🔓 {t('logout')}", key="sb_logout_off", use_container_width=True):
                _logout()

        # ── ADMIN nav ─────────────────────────────────────────────────────────
        elif role == "admin":
            st.markdown("""
            <div style="text-align:center;padding:12px;background:linear-gradient(135deg,#6366f120,#8b5cf620);
                        border-radius:16px;margin-bottom:14px;">
                <div style="font-size:2rem;">👑</div>
                <div style="font-weight:800;">Admin Panel</div>
            </div>
            """, unsafe_allow_html=True)

            nav_items = [
                ("📊", "Dashboard",         "admin_panel"),
                ("🏢", "Departments",        "admin_departments"),
                ("👥", "Officials",          "admin_officials"),
                ("🗺️", "Heatmap",           "admin_heatmap"),
            ]
            for icon, label, screen in nav_items:
                if st.button(f"{icon}  {label}", key=f"nav_{screen}", use_container_width=True):
                    st.session_state.screen = screen
                    st.rerun()

            st.markdown("---")
            if st.button("🔓 Logout", key="sb_logout_adm", use_container_width=True):
                _logout()

        # ── NOT LOGGED IN ─────────────────────────────────────────────────────
        else:
            st.info("Please login to access all features.")

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center;font-size:0.68rem;opacity:0.4;padding-bottom:8px;">
            Jan Seva Portal v1.0<br>
            Powered by AI · Made in 🇮🇳
        </div>
        """, unsafe_allow_html=True)


def _logout():
    for k in ["user", "official", "admin", "role", "otp_sent", "chat_history",
              "selected_category", "location_text", "voice_captured"]:
        st.session_state[k] = None if k in ["user","official","admin"] else (
            [] if k == "chat_history" else
            False if k == "otp_sent" else
            "other" if k == "selected_category" else ""
        )
    st.session_state.role = None
    st.session_state.screen = "login_type"
    st.rerun()


# ── screen router ─────────────────────────────────────────────────────────────
def route():
    screen = st.session_state.screen
    role   = st.session_state.role

    # ── public screens ────────────────────────────────────────────────────────
    if screen == "language":
        from frontend.pages.login import show_language_select
        show_language_select()

    elif screen == "login_type":
        from frontend.pages.login import show_login_type
        show_login_type()

    elif screen == "user_login":
        from frontend.pages.login import show_user_login
        show_user_login()

    elif screen == "official_login":
        from frontend.pages.login import show_official_login
        show_official_login()

    elif screen == "admin_login":
        from frontend.pages.login import show_admin_login
        show_admin_login()

    # ── user screens ──────────────────────────────────────────────────────────
    elif screen == "user_dashboard" and role == "user":
        from frontend.pages.dashboard import show_user_dashboard
        show_user_dashboard()

    elif screen == "file_complaint" and role == "user":
        from frontend.pages.complaint import show_file_complaint
        show_file_complaint()

    elif screen == "tracking":
        from frontend.pages.tracking import show_tracking
        show_tracking()

    elif screen == "schemes":
        from frontend.pages.schemes_admin import show_schemes
        show_schemes()

    elif screen == "assistant" and role == "user":
        from frontend.pages.assistant import show_assistant
        show_assistant()

    elif screen == "notifications" and role == "user":
        show_notifications()

    # ── official screens ──────────────────────────────────────────────────────
    elif screen == "official_dashboard" and role == "official":
        from frontend.pages.dashboard import show_official_dashboard
        show_official_dashboard()

    elif screen == "official_complaints" and role == "official":
        _official_complaints_screen()

    # ── admin screens ─────────────────────────────────────────────────────────
    elif screen == "admin_panel" and role == "admin":
        _admin_stats_screen()

    elif screen == "admin_departments" and role == "admin":
        _admin_departments_screen()

    elif screen == "admin_officials" and role == "admin":
        _admin_officials_screen()

    elif screen == "admin_complaints" and role == "admin":
        _admin_complaints_screen()

    elif screen == "admin_schemes" and role == "admin":
        _admin_schemes_screen()

    elif screen == "admin_heatmap" and role == "admin":
        _admin_heatmap_screen()

    # ── fallback ──────────────────────────────────────────────────────────────
    else:
        st.session_state.screen = "language" if not role else (
            "user_dashboard" if role == "user" else
            "official_dashboard" if role == "official" else "admin_panel"
        )
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# NOTIFICATIONS SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def show_notifications():
    lang = st.session_state.language
    user = st.session_state.user or {}
    user_id = user.get("user_id")

    _back("user_dashboard")

    st.markdown(f"""
    <div class="hero">
        <h1>🔔 {t('notifications')}</h1>
        <p>{'आपकी सूचनाएं एवं अपडेट' if lang=='hi' else 'Your updates and alerts'}</p>
    </div>
    """, unsafe_allow_html=True)

    if not user_id:
        st.warning("Login required.")
        return

    try:
        notifs = requests.get(f"{API_BASE}/schemes/user/notifications/{user_id}").json()
    except Exception as e:
        st.error(f"Cannot load notifications: {e}")
        return

    if not notifs:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;opacity:0.5;">
            <div style="font-size:4rem;">🔕</div>
            <div style="margin-top:12px;font-size:1rem;font-weight:600;">No notifications yet</div>
        </div>
        """, unsafe_allow_html=True)
        return

    unread = [n for n in notifs if not n.get("is_read")]
    read   = [n for n in notifs if  n.get("is_read")]

    if unread:
        st.markdown(f'<div class="section-header">🔴 Unread ({len(unread)})</div>', unsafe_allow_html=True)
        for n in unread:
            _render_notif(n, user_id, unread=True)

    if read:
        st.markdown(f'<div class="section-header">✅ Read ({len(read)})</div>', unsafe_allow_html=True)
        for n in read:
            _render_notif(n, user_id, unread=False)


def _render_notif(n, user_id, unread=True):
    icon = "📢" if n.get("type") == "complaint" else "📜"
    dot_color = "#6366f1" if unread else "#9ca3af"
    st.markdown(f"""
    <div class="notif-card">
        <div style="width:10px;height:10px;border-radius:50%;background:{dot_color};flex-shrink:0;margin-top:6px;"></div>
        <div style="flex:1;">
            <div style="font-weight:700;font-size:0.9rem;">{icon} {n.get('title','')}</div>
            <div style="font-size:0.82rem;opacity:0.75;margin-top:2px;">{n.get('message','')}</div>
            <div style="font-size:0.7rem;opacity:0.5;margin-top:5px;">🕐 {n.get('time','')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if unread:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("✅ Mark read", key=f"notif_{n.get('id')}", use_container_width=True):
                try:
                    requests.put(f"{API_BASE}/schemes/notifications/{n.get('id')}/read")
                    st.rerun()
                except: pass


# ══════════════════════════════════════════════════════════════════════════════
# OFFICIAL — COMPLAINTS (extended, standalone)
# ══════════════════════════════════════════════════════════════════════════════
def _official_complaints_screen():
    official = st.session_state.official or {}
    dept_id  = official.get("department_id")
    official_id = official.get("official_id")

    _back("official_dashboard")
    st.markdown(f"""
    <div class="hero">
        <h1>📋 {t('all_complaints')}</h1>
        <p>{official.get('department','Department')} — Complaints Manager</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        comps = requests.get(f"{API_BASE}/complaints/department/{dept_id}").json()
        comps = comps if isinstance(comps, list) else []
    except:
        comps = []

    # Filter + search bar
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        f_status = st.selectbox("Status", ["all","pending","in_progress","resolved","rejected"], key="off2_st")
    with col2:
        f_priority = st.selectbox("Priority", ["all","high","medium","low"], key="off2_pr")
    with col3:
        search_q = st.text_input("Search", placeholder="keyword…", key="off2_q", label_visibility="collapsed")

    filtered = comps
    if f_status   != "all": filtered = [c for c in filtered if c.get("status")   == f_status]
    if f_priority != "all": filtered = [c for c in filtered if c.get("priority") == f_priority]
    if search_q:
        q = search_q.lower()
        filtered = [c for c in filtered if q in c.get("description","").lower()
                                        or q in c.get("location","").lower()
                                        or q in c.get("user_name","").lower()]

    st.markdown(f"**{len(filtered)} complaints found**")

    STATUS_COLORS = {"pending":"#d97706","in_progress":"#2563eb","resolved":"#16a34a","rejected":"#dc2626"}
    for c in filtered:
        p   = c.get("priority","medium")
        s   = c.get("status","pending")
        sc  = STATUS_COLORS.get(s,"#888")
        pcl = {"high":"badge-high","medium":"badge-medium","low":"badge-low"}.get(p,"badge-medium")

        with st.expander(f"#{c.get('complaint_id','')}  ·  {c.get('category','').title()}  ·  {c.get('user_name','')}"):
            st.markdown(f"""
            <div style="border-left:4px solid {sc};padding-left:12px;">
                <div style="font-size:0.85rem;line-height:1.65;">{c.get('description','')}</div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;">
                    <span class="{pcl}">{p.title()} Priority</span>
                    <span style="color:{sc};font-weight:700;font-size:0.8rem;">{s.replace('_',' ').title()}</span>
                </div>
                <div style="font-size:0.77rem;opacity:0.6;margin-top:6px;">
                    📍 {c.get('location','N/A')} &nbsp;·&nbsp; 👤 {c.get('user_name','')} &nbsp;·&nbsp;
                    📞 {c.get('user_phone','')} &nbsp;·&nbsp; 🕐 {c.get('created_at','')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            note = st.text_input("Add note (optional)", key=f"note_{c.get('complaint_id')}", label_visibility="collapsed",
                                 placeholder="Add a resolution note…")
            cols = st.columns(3)
            cid  = c.get("complaint_id","")
            with cols[0]:
                if st.button("🔄 In Progress", key=f"ip_{cid}", use_container_width=True):
                    _update_status(cid, "in_progress", note or "Being processed.", official_id=official_id)
            with cols[1]:
                if st.button("✅ Resolve", key=f"res_{cid}", use_container_width=True):
                    _update_status(cid, "resolved", note or "Resolved by department.", official_id=official_id)
            with cols[2]:
                if st.button("❌ Reject", key=f"rej_{cid}", use_container_width=True):
                    _update_status(cid, "rejected", note or "Rejected.", official_id=official_id)


def _update_status(complaint_id, status, note):
    try:
        r = requests.put(f"{API_BASE}/complaints/{complaint_id}/status",
                         json={"status": status, "note": note})
        if r.json().get("success"):
            st.success(f"Status updated → {status.replace('_',' ').title()}")
            st.rerun()
        else:
            st.error("Update failed.")
    except Exception as e:
        st.error(str(e))



# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — STATS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def _admin_stats_screen():
    st.markdown("""<div class="hero">
        <h1>👑 Admin Dashboard</h1>
        <p>System overview, analytics & real-time activity</p>
    </div>""", unsafe_allow_html=True)

    try: s = requests.get(f"{API_BASE}/admin/stats").json()
    except: s = {}
    try: lb = requests.get(f"{API_BASE}/admin/leaderboard").json()
    except: lb = {}

    # ── KPI cards (aligned with backend stat names) ─────────────────────────
    metrics = [
        ("👤 Users",          s.get("total_users", 0),         "#D97706"),
        ("🏢 Departments",    s.get("total_departments", 0),   "#1D4ED8"),
        ("👥 Officials",      s.get("total_officials", 0),     "#059669"),
        ("✅ Approved",       s.get("approved_officials", 0),  "#15803D"),
        ("📋 Complaints",     s.get("total_complaints", 0),    "#B45309"),
        ("⏳ Pending",        s.get("pending", 0),             "#B91C1C"),
        ("🔄 In Progress",    s.get("in_progress", 0),         "#2563EB"),
        ("✅ Resolved",       s.get("resolved", 0),            "#16A34A"),
    ]

    # Render in fixed 4-column grid row-by-row
    for row_start in range(0, len(metrics), 4):
        row = metrics[row_start:row_start + 4]
        cols = st.columns(4)
        for col, (label, val, color) in zip(cols, row):
            col.markdown(f"""<div class="stat-card" style="margin-bottom:12px;">
                <div class="stat-number" style="color:{color}">{val}</div>
                <div class="stat-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    # ── resolution rate ───────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Resolution Rate</div>', unsafe_allow_html=True)
    total = s.get("total_complaints", 1) or 1
    res   = s.get("resolved", 0)
    pct   = int(s.get("resolution_rate", round((res / total) * 100, 1)))
    st.progress(pct/100, text=f"Resolution Rate: {pct}%  ({res}/{total} complaints resolved)")

    # ── complaints by category ────────────────────────────────────────────────
    try:
        comps = requests.get(f"{API_BASE}/complaints/all").json()
        if isinstance(comps,list) and comps:
            cats = {}
            for c in comps:
                cat = c.get("category","other")
                cats[cat] = cats.get(cat,0)+1

            st.markdown('<div class="section-header">📂 Complaints by Category</div>', unsafe_allow_html=True)
            max_v = max(cats.values()) if cats else 1
            for cat,cnt in sorted(cats.items(), key=lambda x:-x[1]):
                fill = int(cnt/max_v*100)
                st.markdown(f"""<div style="margin:6px 0;">
                    <div style="display:flex;justify-content:space-between;font-size:.82rem;margin-bottom:3px;">
                        <span style="font-weight:700;text-transform:capitalize;">{cat}</span>
                        <span style="opacity:.7;">{cnt}</span>
                    </div>
                    <div style="height:10px;background:#EDE7D5;border-radius:5px;overflow:hidden;">
                        <div style="height:100%;width:{fill}%;background:linear-gradient(90deg,#D97706,#059669);border-radius:5px;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # ── recent activity feed ──────────────────────────────────────────
            st.markdown('<div class="section-header">🕐 Recent Activity</div>', unsafe_allow_html=True)
            SC2 = {"pending":"#b45309","in_progress":"#1d4ed8","resolved":"#15803d","rejected":"#b91c1c"}
            for c in comps[:10]:
                sc = SC2.get(c.get("status","pending"),"#888")
                st.markdown(f"""<div style="display:flex;gap:12px;align-items:center;padding:9px 0;border-bottom:1px solid #EDE7D540;">
                    <div style="width:9px;height:9px;border-radius:50%;background:{sc};flex-shrink:0;"></div>
                    <div style="flex:1;font-size:.82rem;">
                        <strong>#{c.get('complaint_id','')}</strong> — {c.get('category','').title()}
                        <span style="opacity:.6;font-size:.75rem;"> · {c.get('user_name','')} · {c.get('created_at','')}</span>
                    </div>
                    <div style="font-size:.75rem;color:{sc};font-weight:700;">{c.get('status','').replace('_',' ').title()}</div>
                </div>""", unsafe_allow_html=True)
    except: pass

    if isinstance(lb, dict):
        st.markdown('<div class="section-header">🏆 Overall Leaderboard</div>', unsafe_allow_html=True)
        st.caption(f"Minimum resolved complaints required: {lb.get('min_resolved_threshold', 5)}")
        for row in lb.get("overall", [])[:10]:
            st.markdown(
                f"**#{row.get('rank')}** {row.get('name')} | {row.get('department')} | "
                f"⭐ {row.get('avg_rating', 0):.2f} | Resolved: {row.get('total_resolved', 0)}"
            )

        st.markdown('<div class="section-header">🏢 Department-wise Leaderboard</div>', unsafe_allow_html=True)
        for dept_board in lb.get("department_wise", {}).values():
            if not dept_board:
                continue
            st.markdown(f"**{dept_board[0].get('department','Department')}**")
            for row in dept_board[:5]:
                st.markdown(
                    f"#{row.get('rank')} {row.get('name')} | ⭐ {row.get('avg_rating', 0):.2f} | "
                    f"Resolved: {row.get('total_resolved', 0)}"
                )

        st.markdown('<div class="section-header">📈 Department Performance</div>', unsafe_allow_html=True)
        for d in lb.get("department_performance", []):
            handled = d.get("total_assigned", 0)
            resolved = d.get("total_resolved", 0)
            pct = int((resolved / max(handled, 1)) * 100)
            st.markdown(
                f"**{d.get('department')}** · Officials: {d.get('officials')} · "
                f"Avg Rating: ⭐ {d.get('avg_rating', 0):.2f} · Resolved: {resolved}/{handled}"
            )
            st.progress(pct / 100)


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — DEPARTMENTS  (create + list with drill-down)
# ══════════════════════════════════════════════════════════════════════════════
CAT_COLORS = {"water":"#0369a1","electricity":"#d97706","road":"#7c3aed","waste":"#059669",
              "drainage":"#0284c7","health":"#dc2626","other":"#6b7280"}

def _admin_departments_screen():
    st.markdown("""<div class="hero">
        <h1>🏢 Departments</h1>
        <p>Create departments · manage officials · view complaints per department</p>
    </div>""", unsafe_allow_html=True)

    # ── drill-down into a single dept ─────────────────────────────────────────
    if st.session_state.get("viewing_dept_id"):
        _dept_detail_screen()
        return

    # ── CREATE FORM ───────────────────────────────────────────────────────────
    with st.expander("➕ Create New Department", expanded=False):
        with st.form("dept_form_main"):
            c1,c2 = st.columns(2)
            with c1:
                name     = st.text_input("Department Name (English) *")
                category = st.selectbox("Category",["water","electricity","road","waste","drainage","health","other"])
            with c2:
                name_hi  = st.text_input("विभाग का नाम (हिंदी)")
                location = st.text_input("City / Location","Bhopal")
            if st.form_submit_button("➕ Create Department", use_container_width=True):
                if name:
                    try:
                        r = requests.post(f"{API_BASE}/admin/departments",
                                          json={"name":name,"name_hi":name_hi,"category":category,"location":location})
                        d = r.json()
                        if d.get("success"):
                            st.success(f"✅ Created!  Department Code: **{d.get('dept_id')}** — share with officials.")
                            st.rerun()
                        else: st.error(d.get("detail","Error"))
                    except Exception as e: st.error(str(e))
                else: st.warning("Department name is required.")

    # ── DEPT LIST ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 All Departments</div>', unsafe_allow_html=True)
    try: depts = requests.get(f"{API_BASE}/admin/departments").json()
    except: depts=[]

    if not depts:
        st.info("No departments yet. Create one above."); return

    for d in depts:
        cc  = CAT_COLORS.get(d.get("category","other"),"#888")
        tot = d.get("total_complaints",0)
        pen = d.get("pending_complaints",0)
        res = d.get("resolved_complaints",0)
        aof = d.get("approved_officials",0)
        tof = d.get("total_officials",0)

        with st.expander(f"🏢 {d.get('name','')}  ·  Code: {d.get('dept_id','')}  ·  {tot} complaints"):
            st.markdown(f"""
            <div style="border-left:4px solid {cc};padding-left:12px;">
                <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
                    <div>
                        <div style="font-weight:800;font-size:1.05rem;">{d.get('name','')}</div>
                        <div style="font-size:.82rem;opacity:.65;">{d.get('name_hi','')}</div>
                        <div style="font-size:.75rem;margin-top:4px;opacity:.6;">
                            📂 {d.get('category','').title()} &nbsp;·&nbsp; 📍 {d.get('location','')}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:monospace;font-size:1.1rem;font-weight:800;color:{cc};">{d.get('dept_id','')}</div>
                        <div style="font-size:.7rem;opacity:.5;">Department Code</div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;text-align:center;">
                    <div style="background:#fffbeb;border-radius:10px;padding:8px 4px;">
                        <div style="font-weight:800;color:#b45309;">{tot}</div><div style="font-size:.65rem;font-weight:700;opacity:.7;">TOTAL</div>
                    </div>
                    <div style="background:#fef2f2;border-radius:10px;padding:8px 4px;">
                        <div style="font-weight:800;color:#b91c1c;">{pen}</div><div style="font-size:.65rem;font-weight:700;opacity:.7;">PENDING</div>
                    </div>
                    <div style="background:#f0fdf4;border-radius:10px;padding:8px 4px;">
                        <div style="font-weight:800;color:#15803d;">{res}</div><div style="font-size:.65rem;font-weight:700;opacity:.7;">RESOLVED</div>
                    </div>
                    <div style="background:#eff6ff;border-radius:10px;padding:8px 4px;">
                        <div style="font-weight:800;color:#1d4ed8;">{aof}/{tof}</div><div style="font-size:.65rem;font-weight:700;opacity:.7;">OFFICIALS</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            if st.button(f"🔍 Open Department Details", key=f"open_dept_{d.get('id')}", use_container_width=True):
                st.session_state.viewing_dept_id   = d.get("id")
                st.session_state.viewing_dept_name = d.get("name","")
                st.session_state.viewing_dept_code = d.get("dept_id","")
                st.rerun()


def _dept_detail_screen():
    """Full drill-down: officials (approve/reject) + complaints for a dept."""
    dept_id   = st.session_state.viewing_dept_id
    dept_name = st.session_state.get("viewing_dept_name","Department")
    dept_code = st.session_state.get("viewing_dept_code","")

    if st.button("← Back to Departments", key="back_dept_detail"):
        st.session_state.viewing_dept_id = None
        st.rerun()

    st.markdown(f"""<div class="hero">
        <h1>🏢 {dept_name}</h1>
        <p>Code: <strong>{dept_code}</strong> — Officials & Complaints</p>
    </div>""", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👥 Officials", "📢 Complaints"])

    # ── Officials tab ─────────────────────────────────────────────────────────
    with tab1:
        try: officials = requests.get(f"{API_BASE}/admin/departments/{dept_id}/officials").json()
        except: officials=[]

        approved  = [o for o in officials if o.get("is_approved")]
        pending   = [o for o in officials if not o.get("is_approved")]

        if pending:
            st.markdown(f'<div class="section-header">⏳ Pending Approval ({len(pending)})</div>', unsafe_allow_html=True)
            for o in pending:
                c1,c2,c3 = st.columns([5,1,1])
                with c1:
                    st.markdown(f"""<div class="card" style="border-left:4px solid #d97706;margin:4px 0;">
                        <div style="font-weight:800;">{o.get('name','')}</div>
                        <div style="font-size:.8rem;opacity:.7;">📧 {o.get('email','')} &nbsp;·&nbsp; Joined: {o.get('joined','')}</div>
                    </div>""", unsafe_allow_html=True)
                with c2:
                    if st.button("✅", key=f"dapv_{o.get('id')}", use_container_width=True, help="Approve"):
                        try:
                            requests.put(f"{API_BASE}/admin/officials/{o.get('id')}/approve")
                            st.success("Approved!"); st.rerun()
                        except Exception as e: st.error(str(e))
                with c3:
                    if st.button("❌", key=f"drej_{o.get('id')}", use_container_width=True, help="Reject"):
                        try:
                            requests.put(f"{API_BASE}/admin/officials/{o.get('id')}/reject")
                            st.warning("Rejected & removed."); st.rerun()
                        except Exception as e: st.error(str(e))
        else:
            st.info("No pending officials for this department.")

        if approved:
            st.markdown(f'<div class="section-header">✅ Approved Officials ({len(approved)})</div>', unsafe_allow_html=True)
            for o in approved:
                c1,c2 = st.columns([5,1])
                with c1:
                    st.markdown(f"""<div class="card" style="border-left:4px solid #15803d;margin:4px 0;">
                        <div style="font-weight:800;">{o.get('name','')}</div>
                        <div style="font-size:.8rem;opacity:.7;">📧 {o.get('email','')} &nbsp;·&nbsp; Joined: {o.get('joined','')}</div>
                    </div>""", unsafe_allow_html=True)
                with c2:
                    if st.button("🗑️", key=f"drem_{o.get('id')}", use_container_width=True, help="Remove"):
                        try:
                            requests.put(f"{API_BASE}/admin/officials/{o.get('id')}/reject")
                            st.warning("Official removed."); st.rerun()
                        except Exception as e: st.error(str(e))

    # ── Complaints tab ────────────────────────────────────────────────────────
    with tab2:
        try: comps = requests.get(f"{API_BASE}/admin/departments/{dept_id}/complaints").json()
        except: comps=[]

        if not comps:
            st.info("No complaints for this department yet."); return

        f1,f2 = st.columns(2)
        with f1: f_st=st.selectbox("Status",["all","pending","in_progress","resolved","rejected"],key="dct_st")
        with f2: f_pr=st.selectbox("Priority",["all","high","medium","low"],key="dct_pr")

        filtered=comps
        if f_st!="all": filtered=[c for c in filtered if c.get("status")==f_st]
        if f_pr!="all": filtered=[c for c in filtered if c.get("priority")==f_pr]

        st.markdown(f"**{len(filtered)} complaint{'s' if len(filtered)!=1 else ''}**")

        SC3={"pending":"#b45309","in_progress":"#1d4ed8","resolved":"#15803d","rejected":"#b91c1c"}
        SI3={"pending":"⏳","in_progress":"🔄","resolved":"✅","rejected":"❌"}
        for c in filtered:
            s = c.get("status","pending"); p=c.get("priority","medium")
            sc=SC3.get(s,"#888"); si=SI3.get(s,"📋")
            pcl={"high":"badge-high","medium":"badge-medium","low":"badge-low"}.get(p,"badge-medium")
            cid=c.get("complaint_id","")

            with st.expander(f"{si} #{cid}  ·  {c.get('category','').title()}  ·  👤 {c.get('user_name','')}"):
                st.markdown(f"""<div style="border-left:4px solid {sc};padding-left:12px;">
                    <div style="font-size:.87rem;line-height:1.65;">{c.get('description','')}</div>
                    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;">
                        <span class="{pcl}">{p.title()}</span>
                        <span style="color:{sc};font-weight:700;font-size:.78rem;">{s.replace('_',' ').title()}</span>
                    </div>
                    <div style="font-size:.75rem;opacity:.6;margin-top:5px;">
                        📍 {c.get('location','N/A')} &nbsp;·&nbsp;
                        📞 {c.get('user_phone','')} &nbsp;·&nbsp;
                        🕐 {c.get('created_at','')}
                    </div>
                </div>""", unsafe_allow_html=True)

                note=st.text_input("Note",key=f"adm_dnote_{cid}",placeholder="Resolution note…",label_visibility="collapsed")
                b1,b2,b3=st.columns(3)
                with b1:
                    if st.button("🔄 In Progress",key=f"adm_dip_{cid}",use_container_width=True):
                        _update_status(cid,"in_progress",note or "Being processed.")
                with b2:
                    if st.button("✅ Resolve",key=f"adm_dres_{cid}",use_container_width=True):
                        _update_status(cid,"resolved",note or "Resolved by admin.")
                with b3:
                    if st.button("❌ Reject",key=f"adm_drej_{cid}",use_container_width=True):
                        _update_status(cid,"rejected",note or "Rejected.")


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — OFFICIALS (global view: approve/reject across all depts)
# ══════════════════════════════════════════════════════════════════════════════
def _admin_officials_screen():
    st.markdown("""<div class="hero">
        <h1>👥 Officials</h1>
        <p>Approve, reject and manage officials across all departments</p>
    </div>""", unsafe_allow_html=True)

    try:
        pending  = requests.get(f"{API_BASE}/admin/officials/pending").json()
        all_offs = requests.get(f"{API_BASE}/admin/officials/all").json()
    except: pending=[]; all_offs=[]

    approved = [o for o in all_offs if o.get("is_approved")]

    # ── pending ───────────────────────────────────────────────────────────────
    if pending:
        st.markdown(f'<div class="section-header">⏳ Awaiting Approval ({len(pending)})</div>', unsafe_allow_html=True)
        for o in pending:
            c1,c2,c3 = st.columns([5,1,1])
            with c1:
                st.markdown(f"""<div class="card" style="border-left:4px solid #d97706;">
                    <div style="font-weight:800;font-size:.95rem;">{o.get('name','')}</div>
                    <div style="font-size:.8rem;opacity:.7;margin-top:3px;">
                        📧 {o.get('email','')} &nbsp;·&nbsp;
                        🏢 {o.get('department','Unknown')} &nbsp;·&nbsp;
                        Code: <strong>{o.get('dept_code','')}</strong> &nbsp;·&nbsp;
                        📅 {o.get('joined','')}
                    </div>
                </div>""", unsafe_allow_html=True)
            with c2:
                if st.button("✅ Approve", key=f"apv_{o.get('id')}", use_container_width=True):
                    try:
                        requests.put(f"{API_BASE}/admin/officials/{o.get('id')}/approve")
                        st.success(f"✅ {o.get('name','')} approved!"); st.rerun()
                    except Exception as e: st.error(str(e))
            with c3:
                if st.button("❌ Reject", key=f"rej_{o.get('id')}", use_container_width=True):
                    try:
                        requests.put(f"{API_BASE}/admin/officials/{o.get('id')}/reject")
                        st.warning("Rejected & removed."); st.rerun()
                    except Exception as e: st.error(str(e))
    else:
        st.success("🎉 No pending approvals at this time.")

    # ── approved officials ────────────────────────────────────────────────────
    if approved:
        st.markdown(f'<div class="section-header">✅ Approved Officials ({len(approved)})</div>', unsafe_allow_html=True)
        for o in approved:
            c1,c2 = st.columns([6,1])
            with c1:
                st.markdown(f"""<div class="card" style="border-left:4px solid #15803d;">
                    <div style="font-weight:800;">{o.get('name','')}</div>
                    <div style="font-size:.8rem;opacity:.7;margin-top:3px;">
                        📧 {o.get('email','')} &nbsp;·&nbsp;
                        🏢 {o.get('department','Unknown')} &nbsp;·&nbsp;
                        Code: <strong>{o.get('dept_code','')}</strong> &nbsp;·&nbsp;
                        📅 {o.get('joined','')}
                    </div>
                </div>""", unsafe_allow_html=True)
            with c2:
                if st.button("🗑️ Remove", key=f"rem_{o.get('id')}", use_container_width=True):
                    try:
                        requests.put(f"{API_BASE}/admin/officials/{o.get('id')}/reject")
                        st.warning("Official removed."); st.rerun()
                    except Exception as e: st.error(str(e))

    st.markdown("""<div class="card" style="text-align:center;margin-top:16px;">
        <div style="font-size:.85rem;opacity:.7;">
            💡 Share the <strong>Department Code</strong> with officials at signup —
            they appear here for your approval automatically.
        </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — ALL COMPLAINTS
# ══════════════════════════════════════════════════════════════════════════════
def _admin_complaints_screen():
    st.markdown("""<div class="hero">
        <h1>📢 All Complaints</h1>
        <p>System-wide complaint management & status control</p>
    </div>""", unsafe_allow_html=True)

    try: comps = requests.get(f"{API_BASE}/complaints/all").json()
    except: comps=[]
    comps = comps if isinstance(comps,list) else []

    # ── summary mini-stats ────────────────────────────────────────────────────
    total  = len(comps)
    pen    = len([c for c in comps if c.get("status")=="pending"])
    inp    = len([c for c in comps if c.get("status")=="in_progress"])
    res    = len([c for c in comps if c.get("status")=="resolved"])
    hi     = len([c for c in comps if c.get("priority")=="high"])

    cols=st.columns(5)
    for col,lab,val,color in [
        (cols[0],"Total",    total,"#D97706"),
        (cols[1],"Pending",  pen,  "#b91c1c"),
        (cols[2],"In Prog",  inp,  "#1d4ed8"),
        (cols[3],"Resolved", res,  "#15803d"),
        (cols[4],"High Pri", hi,   "#b91c1c"),
    ]:
        col.markdown(f"""<div class="stat-card">
            <div class="stat-number" style="color:{color}">{val}</div>
            <div class="stat-label">{lab}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── filters ───────────────────────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    with c1: f_st = st.selectbox("Status",["all","pending","in_progress","resolved","rejected"],key="admc_st2")
    with c2: f_pr = st.selectbox("Priority",["all","high","medium","low"],key="admc_pr2")
    with c3:
        depts_resp = requests.get(f"{API_BASE}/admin/departments").json() if True else []
        dept_names = ["all"] + [d.get("name","") for d in (depts_resp if isinstance(depts_resp,list) else [])]
        f_dept = st.selectbox("Department",dept_names,key="admc_dept2")
    with c4: srch = st.text_input("Search",placeholder="keyword…",key="admc_q2",label_visibility="collapsed")

    filtered=comps
    if f_st!="all":   filtered=[c for c in filtered if c.get("status")==f_st]
    if f_pr!="all":   filtered=[c for c in filtered if c.get("priority")==f_pr]
    if f_dept!="all": filtered=[c for c in filtered if c.get("department","")==f_dept]
    if srch:
        q=srch.lower()
        filtered=[c for c in filtered if q in c.get("description","").lower()
                  or q in c.get("user_name","").lower()
                  or q in c.get("location","").lower()
                  or q in c.get("complaint_id","").lower()]

    st.markdown(f"**Showing {len(filtered)} of {total} complaints**")

    SC4={"pending":"#b45309","in_progress":"#1d4ed8","resolved":"#15803d","rejected":"#b91c1c"}
    SI4={"pending":"⏳","in_progress":"🔄","resolved":"✅","rejected":"❌"}
    for c in filtered[:50]:
        s=c.get("status","pending"); p=c.get("priority","medium")
        sc=SC4.get(s,"#888"); si=SI4.get(s,"📋")
        pcl={"high":"badge-high","medium":"badge-medium","low":"badge-low"}.get(p,"badge-medium")
        cid=c.get("complaint_id","")

        with st.expander(f"{si} #{cid}  ·  {c.get('category','').title()}  ·  {c.get('department','N/A')}  ·  👤 {c.get('user_name','')}"):
            st.markdown(f"""<div style="border-left:4px solid {sc};padding-left:12px;">
                <div style="font-size:.87rem;line-height:1.65;">{c.get('description','')}</div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;">
                    <span class="{pcl}">{p.title()} Priority</span>
                    <span style="color:{sc};font-weight:700;font-size:.8rem;">{s.replace('_',' ').title()}</span>
                    <span style="font-size:.78rem;opacity:.65;">🏢 {c.get('department','N/A')}</span>
                </div>
                <div style="font-size:.75rem;opacity:.6;margin-top:5px;">
                    📍 {c.get('location','N/A')} &nbsp;·&nbsp; 👤 {c.get('user_name','')} &nbsp;·&nbsp; 🕐 {c.get('created_at','')}
                </div>
            </div>""", unsafe_allow_html=True)

            note=st.text_input("Note",key=f"adm_note2_{cid}",placeholder="Resolution note…",label_visibility="collapsed")
            b1,b2,b3=st.columns(3)
            with b1:
                if st.button("🔄 In Progress",key=f"adm2_ip_{cid}",use_container_width=True):
                    _update_status(cid,"in_progress",note or "Being processed by admin.")
            with b2:
                if st.button("✅ Resolve",key=f"adm2_res_{cid}",use_container_width=True):
                    _update_status(cid,"resolved",note or "Resolved by admin.")
            with b3:
                if st.button("❌ Reject",key=f"adm2_rej_{cid}",use_container_width=True):
                    _update_status(cid,"rejected",note or "Rejected by admin.")


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — SCHEMES MANAGER  (with image upload)
# ══════════════════════════════════════════════════════════════════════════════
def _admin_schemes_screen():
    lang = st.session_state.get("language","en")

    st.markdown("""<div class="hero">
        <h1>📜 Schemes Manager</h1>
        <p>Create government schemes with image · bilingual · notify all users</p>
    </div>""", unsafe_allow_html=True)

    # ── CREATE FORM ───────────────────────────────────────────────────────────
    with st.expander("➕ Create New Scheme", expanded=True):
        with st.form("adm_scheme_form2", clear_on_submit=True):
            c1,c2 = st.columns(2)
            with c1:
                title    = st.text_input("Scheme Title (English) *")
                desc     = st.text_area("Description (English) *", height=120)
                cat      = st.selectbox("Category",
                    ["housing","water","energy","health","education","agriculture","general"])
            with c2:
                title_hi = st.text_input("योजना का शीर्षक (हिंदी)")
                desc_hi  = st.text_area("विवरण (हिंदी)", height=120)
                img_file = st.file_uploader("📷 Upload Scheme Image",
                                            type=["jpg","jpeg","png","webp"],
                                            help="Upload a photo for this scheme")
                img_url  = st.text_input("— OR paste image URL —",
                                         placeholder="https://example.com/image.jpg")

            submitted = st.form_submit_button("🚀 Create Scheme & Notify All Users", use_container_width=True)
            if submitted:
                if not title or not desc:
                    st.warning("Title and description (English) are required.")
                else:
                    try:
                        if img_file:
                            # multipart upload
                            files   = {"image": (img_file.name, img_file.getvalue(), img_file.type)}
                            payload = {
                                "title": title, "title_hi": title_hi,
                                "description": desc, "description_hi": desc_hi,
                                "category": cat,
                            }
                            r = requests.post(f"{API_BASE}/schemes/create-with-image",
                                              data=payload, files=files)
                        else:
                            r = requests.post(f"{API_BASE}/schemes/create", json={
                                "title": title, "title_hi": title_hi,
                                "description": desc, "description_hi": desc_hi,
                                "image_url": img_url, "category": cat,
                            })
                        d = r.json()
                        if d.get("success"):
                            st.success("✅ Scheme created! All registered users have been notified.")
                            st.rerun()
                        else:
                            st.error(f"Error: {d.get('detail','Unknown error')}")
                    except Exception as e:
                        st.error(f"Server error: {e}")

    # ── SCHEME LIST ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 All Schemes</div>', unsafe_allow_html=True)

    try: schemes = requests.get(f"{API_BASE}/schemes/all").json()
    except: schemes=[]

    if not schemes:
        st.info("No schemes yet. Create one above."); return

    for sch in schemes:
        title_show = (sch.get("title_hi") if lang=="hi" else None) or sch.get("title","")
        desc_show  = (sch.get("description_hi") if lang=="hi" else None) or sch.get("description","")
        img        = sch.get("image_url","")
        cat        = sch.get("category","general")
        date       = sch.get("created_at","")

        with st.expander(f"📋 {sch.get('title','')}  ·  {cat.title()}  ·  {date}"):
            col_img, col_body = st.columns([1,3]) if img else (None, st.columns(1)[0])
            if img and col_img:
                with col_img:
                    try: st.image(img, use_container_width=True)
                    except: st.markdown(f"🖼️ [Image]({img})")
                with col_body:
                    _scheme_body_block(title_show, desc_show, cat, date, sch.get("id"), lang)
            else:
                _scheme_body_block(title_show, desc_show, cat, date, sch.get("id"), lang)

            # Delete button
            st.markdown("---")
            if st.button(f"🗑️ Delete Scheme", key=f"del_sch_{sch.get('id')}"):
                try:
                    requests.delete(f"{API_BASE}/schemes/{sch.get('id')}")
                    st.warning("Scheme deleted."); st.rerun()
                except Exception as e: st.error(str(e))


def _scheme_body_block(title, desc, cat, date, scheme_id, lang):
    st.markdown(f"""
    <div style="font-weight:800;font-size:.97rem;margin-bottom:6px;">{title}</div>
    <div style="font-size:.85rem;line-height:1.72;opacity:.88;">{desc}</div>
    <div style="margin-top:8px;">
        <span class="scheme-tag">📂 {cat.title()}</span>
        <span style="font-size:.72rem;opacity:.55;margin-left:10px;">📅 {date}</span>
    </div>""", unsafe_allow_html=True)
    if st.button("🔊 Read Aloud", key=f"tts_adm_{scheme_id}"):
        speak = desc[:300].replace('"','').replace("'",'')
        st.components.v1.html(f"""<script>
        var m=new SpeechSynthesisUtterance("{speak}");
        m.lang='{"hi-IN" if lang=="hi" else "en-IN"}'; m.rate=0.88;
        window.speechSynthesis.speak(m);</script>""", height=0)
        st.info(f"🔊 {speak[:120]}…")


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
def _admin_heatmap_screen():
    st.markdown("""<div class="hero">
        <h1>🗺️ Complaint Heatmap</h1>
        <p>Geographic distribution — colour-coded by priority</p>
    </div>""", unsafe_allow_html=True)

    try: comps = requests.get(f"{API_BASE}/complaints/all").json()
    except: comps=[]
    comps = comps if isinstance(comps,list) else []

    geotagged = [(c.get("latitude"),c.get("longitude"),
                  c.get("priority","medium"),c.get("category","other"),
                  c.get("complaint_id",""),c.get("status","pending"))
                 for c in comps if c.get("latitude") and c.get("longitude")]

    cols=st.columns(3)
    for col,lab,val,color in [
        (cols[0],"Total Complaints",len(comps),"#D97706"),
        (cols[1],"High Priority",   len([c for c in comps if c.get("priority")=="high"]),"#b91c1c"),
        (cols[2],"Geotagged",       len(geotagged),"#15803d"),
    ]:
        col.markdown(f"""<div class="stat-card">
            <div class="stat-number" style="color:{color}">{val}</div>
            <div class="stat-label">{lab}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">📍 Live Map</div>', unsafe_allow_html=True)

    markers_js = ""
    for lat,lon,priority,category,cid,status in geotagged:
        color  = {"high":"#dc2626","medium":"#d97706","low":"#16a34a"}.get(priority,"#6366f1")
        radius = {"high":14,"medium":10,"low":8}.get(priority,10)
        popup  = f"#{cid} | {category.title()} | {priority.title()} | {status.replace('_',' ').title()}"
        markers_js += f"""L.circleMarker([{lat},{lon}],{{radius:{radius},fillColor:'{color}',
            color:'white',weight:2,opacity:1,fillOpacity:.85}}).addTo(map).bindPopup('{popup}');\n"""

    st.components.v1.html(f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <div id="hmap" style="height:480px;border-radius:18px;overflow:hidden;border:2px solid #EDE7D5;"></div>
    <script>
    var map=L.map('hmap').setView([23.2599,77.4126],11);
    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{maxZoom:19}}).addTo(map);
    L.marker([23.2599,77.4126]).addTo(map).bindPopup('Bhopal HQ').openPopup();
    {markers_js}
    </script>""", height=500)

    st.markdown("""<div class="heatmap-legend" style="margin-top:12px;">
        <div class="legend-item"><div class="legend-dot" style="background:#dc2626"></div> High Priority</div>
        <div class="legend-item"><div class="legend-dot" style="background:#d97706"></div> Medium Priority</div>
        <div class="legend-item"><div class="legend-dot" style="background:#16a34a"></div> Low Priority</div>
    </div>""", unsafe_allow_html=True)
    if not geotagged:
        st.info("📍 File complaints with location data to see them on the map.")


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _update_status(complaint_id, status, note, official_id=None):
    try:
        payload = {"status":status,"note":note}
        if official_id:
            payload["official_id"] = official_id
        r = requests.put(f"{API_BASE}/complaints/{complaint_id}/status",
                         json=payload)
        if r.json().get("success"):
            st.success(f"✅ {status.replace('_',' ').title()}")
            st.rerun()
        else: st.error("Update failed.")
    except Exception as e: st.error(str(e))

def _back(target_screen):
    if st.button(f"← {t('back')}", key=f"back_{target_screen}_{st.session_state.screen}"):
        st.session_state.screen = target_screen
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
render_sidebar()
route()
