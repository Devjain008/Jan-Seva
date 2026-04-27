import streamlit as st
import requests
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from frontend.config import TRANSLATIONS, API_BASE

def t(key):
    lang = st.session_state.get("language", "en")
    tr = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return tr.get(key, key)

STATUS_ICONS = {"pending": "⏳", "in_progress": "🔄", "resolved": "✅", "rejected": "❌"}
STATUS_COLORS = {"pending": "#d97706", "in_progress": "#2563eb", "resolved": "#16a34a", "rejected": "#dc2626"}

def show_tracking():
    lang = st.session_state.get("language", "en")
    user = st.session_state.get("user", {})
    user_id = user.get("user_id")

    if st.button(f"↩️ {t('back')}", key="back_tr"):
        st.session_state.screen = "user_dashboard"
        st.rerun()

    st.markdown(f"""
    <div class="hero">
        <h1>🔍 {t('track_complaint')}</h1>
        <p>{'अपनी शिकायत की स्थिति जानें' if lang=='hi' else 'Check status of your complaint'}</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"🔎 Track by ID", f"📋 {t('your_complaints')}"])

    with tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            comp_id = st.text_input("", placeholder="Enter Complaint ID (e.g. GR1A2B3C4D)", 
                                     key="track_id_input", label_visibility="collapsed")
        with col2:
            search = st.button("🔍 Track", use_container_width=True)
        
        auto_search = bool(comp_id and comp_id.strip())
        if (search or auto_search) and comp_id:
            try:
                resp = requests.get(f"{API_BASE}/complaints/track/{comp_id.strip()}")
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status", "pending")
                    color = STATUS_COLORS.get(status, "#6366f1")
                    icon = STATUS_ICONS.get(status, "📋")
                    
                    st.markdown(f"""
                    <div class="card" style="border-left:5px solid {color};">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;">
                            <div>
                                <div style="font-size:0.75rem;color:#888;font-weight:600;">COMPLAINT ID</div>
                                <div style="font-size:1.3rem;font-weight:800;color:{color};">#{data.get('complaint_id')}</div>
                            </div>
                            <div style="font-size:2.5rem;">{icon}</div>
                        </div>
                        <div style="margin-top:12px;">
                            <div style="font-weight:700;">{data.get('category','').title()} Issue</div>
                            <div style="font-size:0.85rem;margin-top:4px;opacity:0.75;">{data.get('description','')[:200]}</div>
                        </div>
                        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px;font-size:0.8rem;">
                            <span>📍 {data.get('location','N/A')}</span>
                            <span>🏢 {data.get('department','N/A')}</span>
                            <span>📅 {data.get('created_at','')}</span>
                        </div>
                        <div style="margin-top:10px;display:flex;gap:8px;">
                            <span class="{'badge-high' if data.get('priority')=='high' else 'badge-medium' if data.get('priority')=='medium' else 'badge-low'}">{data.get('priority','').title()}</span>
                            <span style="background:{color}20;color:{color};border:1px solid {color}60;border-radius:8px;padding:3px 10px;font-size:0.75rem;font-weight:700;">{icon} {status.replace('_',' ').title()}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Timeline
                    st.markdown(f'<div class="section-header">📅 {t("timeline")}</div>', unsafe_allow_html=True)
                    timeline = data.get("timeline", [])
                    for i, item in enumerate(timeline):
                        t_status = item.get("status", "")
                        t_color = STATUS_COLORS.get(t_status, "#6366f1")
                        t_icon = STATUS_ICONS.get(t_status, "📋")
                        st.markdown(f"""
                        <div class="timeline-item">
                            <div style="display:flex;flex-direction:column;align-items:center;">
                                <div class="timeline-dot" style="background:{t_color};"></div>
                                {f'<div class="timeline-line"></div>' if i < len(timeline)-1 else ''}
                            </div>
                            <div class="timeline-content" style="border-left:3px solid {t_color};">
                                <div class="timeline-status" style="color:{t_color};">{t_icon} {t_status.replace('_',' ').title()}</div>
                                <div class="timeline-note">{item.get('note','')}</div>
                                <div class="timeline-time">🕐 {item.get('time','')}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Official rating (after resolution)
                    if status == "resolved":
                        if data.get("rating"):
                            stars = "⭐" * int(data.get("rating", 0))
                            st.markdown(f"""
                            <div class="card" style="text-align:center;">
                                <div style="font-size:1.5rem;">{stars}</div>
                                <div style="font-weight:700;">You rated this official: {data.get("rating")}/5</div>
                                <div style="font-size:0.8rem;opacity:0.7;margin-top:6px;">{data.get("rating_comment","")}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="section-header">⭐ Rate The Official</div>', unsafe_allow_html=True)
                            rating = st.slider("Rating", min_value=1, max_value=5, value=5, key=f"rate_{comp_id}")
                            comment = st.text_area("Optional feedback comment", key=f"rate_comment_{comp_id}", height=90)
                            if st.button("Submit Rating", key=f"submit_rating_{comp_id}", use_container_width=True):
                                try:
                                    rr = requests.put(
                                        f"{API_BASE}/complaints/{comp_id}/rating",
                                        json={"user_id": user_id, "rating": rating, "comment": comment}
                                    )
                                    rd = rr.json()
                                    if rd.get("success"):
                                        st.success("Thanks! Your rating has been submitted.")
                                        st.rerun()
                                    else:
                                        st.error(rd.get("detail", "Unable to submit rating"))
                                except Exception as e:
                                    st.error(f"Error: {e}")
                    
                    # TTS status
                    speak_text = f"Your complaint {data.get('complaint_id')} is {status.replace('_',' ')}." if lang == "en" else f"आपकी शिकायत {status.replace('_',' ')} है।"
                    if st.button("🔊 Read Status Aloud"):
                        st.components.v1.html(f"""
                        <script>
                        var msg = new SpeechSynthesisUtterance("{speak_text}");
                        msg.lang = '{"hi-IN" if lang=="hi" else "en-IN"}';
                        window.speechSynthesis.speak(msg);
                        </script>
                        """, height=0)
                        st.info(f"🔊 {speak_text}")
                else:
                    st.error("Complaint not found. Check the ID.")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab2:
        if user_id:
            try:
                comps = requests.get(f"{API_BASE}/complaints/user/{user_id}").json()
                if isinstance(comps, list) and comps:
                    for c in comps:
                        status = c.get("status", "pending")
                        color = STATUS_COLORS.get(status, "#6366f1")
                        icon = STATUS_ICONS.get(status, "📋")
                        priority_class = {"high": "badge-high", "medium": "badge-medium", "low": "badge-low"}.get(c.get("priority",""), "badge-medium")
                        
                        with st.expander(f"{icon} #{c.get('complaint_id','')} — {c.get('category','').title()} ({status.replace('_',' ').title()})"):
                            st.markdown(f"""
                            <div style="font-size:0.85rem;">
                                <div>{c.get('description','')}</div>
                                <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:10px;">
                                    <span class="{priority_class}">{c.get('priority','').title()}</span>
                                    <span>📍 {c.get('location','N/A')}</span>
                                    <span>🏢 {c.get('department','N/A')}</span>
                                    <span>🕐 {c.get('created_at','')}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button(f"🔍 Full Details", key=f"detail_{c.get('complaint_id')}"):
                                st.session_state.track_id_input = c.get('complaint_id','')
                                st.rerun()
                else:
                    st.info(t("no_complaints"))
            except Exception as e:
                st.error(f"Error loading complaints: {e}")
        else:
            st.warning("Please login to view your complaints.")
