import streamlit as st
import requests
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from frontend.config import TRANSLATIONS, API_BASE

def t(key):
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

SC = {"pending":"#b45309","in_progress":"#1d4ed8","resolved":"#15803d","rejected":"#b91c1c"}
PC = {"high":"badge-high","medium":"badge-medium","low":"badge-low"}
SI = {"pending":"⏳","in_progress":"🔄","resolved":"✅","rejected":"❌"}

# ─────────────────────────────────────────────────────────────────────────────
# USER: SCHEMES LIST
# ─────────────────────────────────────────────────────────────────────────────
def show_schemes():
    lang = st.session_state.get("language","en")
    if st.button(f"↩️ {t('back')}", key="back_sch"):
        st.session_state.screen = "user_dashboard"; st.rerun()

    st.markdown(f"""<div class="hero">
        <h1>📜 {t('schemes')}</h1>
        <p>{'सरकारी योजनाओं की पूरी जानकारी' if lang=='hi' else 'Complete information on government schemes'}</p>
    </div>""", unsafe_allow_html=True)

    try:
        schemes = requests.get(f"{API_BASE}/schemes/all").json()
    except:
        st.error("Cannot load schemes."); return

    if not schemes:
        st.info("No schemes available yet."); return

    for s in schemes:
        title = (s.get("title_hi") if lang=="hi" else None) or s.get("title","")
        desc  = (s.get("description_hi") if lang=="hi" else None) or s.get("description","")
        img   = s.get("image_url","")
        cat   = s.get("category","general")

        with st.expander(f"📋 {title}  —  {cat.title()}"):
            if img:
                try:    st.image(img, width=180)
                except: pass
            st.markdown(f"""
            <div style="font-size:.9rem;line-height:1.75;margin-top:6px;">{desc}</div>
            <div style="margin-top:10px;">
                <span class="scheme-tag">📂 {cat.title()}</span>
                <span style="font-size:.72rem;opacity:.6;margin-left:10px;">📅 {s.get('created_at','')}</span>
            </div>""", unsafe_allow_html=True)

            speak = desc[:300].replace('"','').replace("'",'')
            if st.button(f"🔊 {t('read_aloud')}", key=f"tts_{s.get('id')}"):
                st.components.v1.html(f"""<script>
                var m=new SpeechSynthesisUtterance("{speak}");
                m.lang='{"hi-IN" if lang=="hi" else "en-IN"}';m.rate=0.88;
                window.speechSynthesis.speak(m);</script>""", height=0)
                st.info(f"🔊 {speak[:100]}…")


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN PANEL  (full replacement)
# ─────────────────────────────────────────────────────────────────────────────
def show_admin_panel():
    """Thin router — actual screens live in app.py; this keeps legacy compat."""
    st.session_state.screen = "admin_panel"; st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# OFFICIAL DASHBOARD  — complete rebuild
# ═════════════════════════════════════════════════════════════════════════════
def show_official_dashboard():
    official = st.session_state.get("official", {})
    dept_id  = official.get("department_id")
    name     = official.get("name","Official")
    dept_name= official.get("department","Department")

    st.markdown(f"""<div class="hero">
        <h1>🏢 {name}</h1>
        <p>{dept_name} — Official Portal</p>
    </div>""", unsafe_allow_html=True)

    # ── stats ─────────────────────────────────────────────────────────────────
    try:
        comps = requests.get(f"{API_BASE}/complaints/department/{dept_id}").json()
        comps = comps if isinstance(comps,list) else []
    except: comps=[]

    total   = len(comps)
    pending = len([c for c in comps if c.get("status")=="pending"])
    inprog  = len([c for c in comps if c.get("status")=="in_progress"])
    res     = len([c for c in comps if c.get("status")=="resolved"])

    cols=st.columns(4)
    for col,label,val,color in [
        (cols[0],"Total",    total, "#D97706"),
        (cols[1],"Pending",  pending,"#b45309"),
        (cols[2],"In Progress",inprog,"#1d4ed8"),
        (cols[3],"Resolved", res,   "#15803d"),
    ]:
        col.markdown(f"""<div class="stat-card">
            <div class="stat-number" style="color:{color}">{val}</div>
            <div class="stat-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 Complaints", "📜 Schemes"])

    # ── TAB 1: complaints ─────────────────────────────────────────────────────
    with tab1:
        c1,c2,c3 = st.columns([2,2,2])
        with c1: f_st = st.selectbox("Status",["all","pending","in_progress","resolved","rejected"],key="off_st")
        with c2: f_pr = st.selectbox("Priority",["all","high","medium","low"],key="off_pr")
        with c3: srch = st.text_input("Search",placeholder="keyword…",key="off_srch",label_visibility="collapsed")

        filtered = comps
        if f_st!="all": filtered=[c for c in filtered if c.get("status")==f_st]
        if f_pr!="all": filtered=[c for c in filtered if c.get("priority")==f_pr]
        if srch:
            q=srch.lower()
            filtered=[c for c in filtered if q in c.get("description","").lower()
                      or q in c.get("location","").lower()
                      or q in c.get("user_name","").lower()]

        st.markdown(f"**{len(filtered)} complaint{'s' if len(filtered)!=1 else ''} found**")

        for c in filtered:
            s  = c.get("status","pending")
            p  = c.get("priority","medium")
            sc = SC.get(s,"#888")
            si = SI.get(s,"📋")
            pcl= PC.get(p,"badge-medium")
            cid= c.get("complaint_id","")

            with st.expander(f"{si} #{cid}  ·  {c.get('category','').title()}  ·  👤 {c.get('user_name','')}  ·  {c.get('created_at','')}"):
                st.markdown(f"""
                <div style="border-left:4px solid {sc};padding-left:12px;margin-bottom:10px;">
                    <div style="font-size:.88rem;line-height:1.65;color:var(--text,#1C1507);">{c.get('description','')}</div>
                    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;">
                        <span class="{pcl}">{p.title()} Priority</span>
                        <span style="color:{sc};font-weight:700;font-size:.8rem;">{s.replace('_',' ').title()}</span>
                    </div>
                    <div style="font-size:.76rem;opacity:.65;margin-top:6px;">
                        📍 {c.get('location','N/A')} &nbsp;·&nbsp;
                        📞 {c.get('user_phone','')} &nbsp;·&nbsp;
                        🕐 {c.get('created_at','')}
                    </div>
                </div>""", unsafe_allow_html=True)

                note = st.text_input("Resolution note (optional)",
                                     key=f"off_note_{cid}",
                                     placeholder="Add a note…",
                                     label_visibility="collapsed")
                b1,b2,b3 = st.columns(3)
                with b1:
                    if st.button("🔄 In Progress", key=f"off_ip_{cid}", use_container_width=True):
                        _update(cid,"in_progress", note or "Being processed by the department.")
                with b2:
                    if st.button("✅ Resolve", key=f"off_res_{cid}", use_container_width=True):
                        _update(cid,"resolved", note or "Resolved by department official.")
                with b3:
                    if st.button("❌ Reject", key=f"off_rej_{cid}", use_container_width=True):
                        _update(cid,"rejected", note or "Rejected by department.")

    # ── TAB 2: schemes view ───────────────────────────────────────────────────
    with tab2:
        try:
            schemes = requests.get(f"{API_BASE}/schemes/all").json()
        except: schemes=[]
        if not schemes:
            st.info("No schemes yet."); return
        for s in schemes:
            with st.expander(f"📋 {s.get('title','')}  —  {s.get('category','').title()}"):
                img = s.get("image_url","")
                if img:
                    try: st.image(img, width=140)
                    except: pass
                st.markdown(f"""
                <div style="font-size:.88rem;line-height:1.7;">{s.get('description','')}</div>
                <div style="font-size:.72rem;opacity:.6;margin-top:6px;">📅 {s.get('created_at','')}</div>
                """, unsafe_allow_html=True)


def _update(complaint_id, status, note):
    try:
        r = requests.put(f"{API_BASE}/complaints/{complaint_id}/status",
                         json={"status":status,"note":note})
        if r.json().get("success"):
            st.success(f"✅ Updated → {status.replace('_',' ').title()}")
            st.rerun()
        else:
            st.error("Update failed.")
    except Exception as e:
        st.error(str(e))
