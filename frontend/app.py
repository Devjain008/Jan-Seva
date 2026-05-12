from __future__ import annotations
import streamlit as st
import requests as _req
import sys, os
from datetime import datetime
import html
from urllib.parse import unquote
import os
import time
import requests as _req
import re
import secrets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from frontend.styles import get_css
from frontend.config import TRANSLATIONS, API_BASE

st.set_page_config(
    page_title="Jan Seva Portal",
    page_icon="🏛️",
    layout="wide",                    
    initial_sidebar_state="expanded",
)

def _apply_layout(page_type: str = "user") -> None:
  
 
    LAYOUTS = {
        # ── AUTH: narrow centered card like Stripe / Clerk ──────────────────
        "auth": """
            .main .block-container {
                max-width      : 480px  !important;
                padding-left   : 1.25rem !important;
                padding-right  : 1.25rem !important;
                padding-top    : 2.5rem  !important;
                padding-bottom : 4rem    !important;
                margin         : 0 auto  !important;
                width          : 100%    !important;
            }
        """,
 
        # ── USER: comfortable reading width for complaint cards ──────────────
        "user": """
            .main .block-container {
                max-width      : 900px   !important;
                padding-left   : 2rem    !important;
                padding-right  : 2rem    !important;
                padding-top    : 1.75rem !important;
                padding-bottom : 4rem    !important;
                margin         : 0 auto  !important;
                width          : 100%    !important;
            }
        """,
 
        # ── ADMIN: wide for tables, heatmaps, analytics ─────────────────────
        "admin": """
            .main .block-container {
                max-width      : 1180px  !important;
                padding-left   : 2.5rem  !important;
                padding-right  : 2.5rem  !important;
                padding-top    : 1.75rem !important;
                padding-bottom : 4rem    !important;
                margin         : 0 auto  !important;
                width          : 100%    !important;
            }
        """,
    }
 
    # fallback to user layout
    css = LAYOUTS.get(page_type, LAYOUTS["user"])
 
    # responsive overrides applied to ALL layout types
    responsive = """
        @media (max-width: 1024px) {
            .main .block-container {
                padding-left   : 1.5rem  !important;
                padding-right  : 1.5rem  !important;
            }
        }
        @media (max-width: 768px) {
            .main .block-container {
                max-width      : 100%    !important;
                padding-left   : 1.25rem !important;
                padding-right  : 1.25rem !important;
                padding-top    : 1.25rem !important;
                padding-bottom : 3rem    !important;
            }
        }
        @media (max-width: 480px) {
            .main .block-container {
                padding-left   : 1rem    !important;
                padding-right  : 1rem    !important;
                padding-top    : 1rem    !important;
                padding-bottom : 2.5rem  !important;
            }
        }
    """
 
    st.markdown(
        f"<style>{css}{responsive}</style>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# API HELPER
# ─────────────────────────────────────────────

def api(method, endpoint, **kwargs):
    url = f"{API_BASE}{endpoint}"
    try:
        response = _req.request(
            method=method.upper(),
            url=url,
            timeout=30,
            **kwargs
        )
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return {"success": True}
    except _req.exceptions.HTTPError:

        try:
            return response.json()
        except Exception:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}"
            }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

# In app.py, after st.set_page_config
st.markdown("""
<script>
window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'voice_transcript') {
        // Optional: show a floating notification
        let toast = document.getElementById('voice_toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'voice_toast';
            toast.style.cssText = 'position:fixed; bottom:20px; right:20px; background:#059669; color:white; padding:8px 16px; border-radius:30px; font-size:0.8rem; z-index:9999; opacity:0; transition:opacity 0.2s;';
            document.body.appendChild(toast);
        }
        toast.innerText = '✓ Voice captured! Page is refreshing...';
        toast.style.opacity = '1';
        setTimeout(() => { toast.style.opacity = '0'; }, 1500);
    }
});
</script>
""", unsafe_allow_html=True)

# Offline mode JavaScript


if "offline_complaints" not in st.session_state:
    st.session_state.offline_complaints = []

# ── session defaults ──────────────────────────────────────────────────────────
DEFS = {
    "screen": "language", "language": "en", "dark_mode": False,
    "role": None, "user": None, "official": None, "admin": None,
    "otp_sent": False, "chat_history": [],
    "selected_cat": "other", "location_text": "Bhopal, MP",
    "loc_lat": 23.2599, "loc_lon": 77.4126, "voice_text": "",
    "viewing_dept_id": None, "viewing_dept_name": "", "viewing_dept_code": "",
}
for k, v in DEFS.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)

# ── helpers ───────────────────────────────────────────────────────────────────
def t(key):
    return TRANSLATIONS.get(st.session_state.language, TRANSLATIONS["en"]).get(key, key)



def speak_text(text, lang="en"):
    """Generate JavaScript to speak the given text aloud."""
    # Escape double quotes and newlines
    safe_text = text.replace('"', '\\"').replace('\n', ' ')
    lang_code = "hi-IN" if lang == "hi" else "en-IN"
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{safe_text}");
    msg.lang = '{lang_code}';
    msg.rate = 0.9;
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0)

def submit_offline_complaints():
    if not st.session_state.offline_complaints:
        return
    # Try a cheap API call to check connectivity
    try:
        _req.get(f"{API_BASE}/schemes/all", timeout=3)
        online = True
    except:
        online = False
    
    if online:
        submitted = []
        for comp in st.session_state.offline_complaints:
            resp = api("post", "/complaints/create", json=comp)
            if resp.get("success"):
                submitted.append(comp)
        # Remove submitted ones
        for comp in submitted:
            st.session_state.offline_complaints.remove(comp)
        if submitted:
            st.success(f"✅ {len(submitted)} offline complaint(s) submitted successfully!")
            st.rerun()
            
def logout():
    for k, v in DEFS.items():
        st.session_state[k] = v
    st.rerun()

SC   = {"pending": "#b45309", "in_progress": "#1d4ed8", "resolved": "#15803d",
        "rejected": "#b91c1c", "closed": "#6b7280"}
SI   = {"pending": "⏳", "in_progress": "🔄", "resolved": "✅", "rejected": "❌", "closed": "🔒"}
PC   = {"high": "badge-high", "medium": "badge-medium", "low": "badge-low"}
STAR = ["", "⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]

def stars_html(avg, count=0):
    """Returns a safe HTML string for a star rating."""
    avg = float(avg or 0)
    full  = int(avg)
    half  = 1 if (avg - full) >= 0.5 else 0
    empty = 5 - full - half
    bar   = "★" * full + ("⯨" if half else "") + "☆" * empty
    ct    = f" ({count} rating{'s' if count != 1 else ''})" if count else ""
    return (
        f'<span style="color:#f59e0b;font-size:1rem;letter-spacing:1px;">{bar}</span>'
        f'<span style="font-size:.78rem;opacity:.7;"> {avg:.1f}{ct}</span>'
    )

def render_sidebar():
    import streamlit as st

    role = st.session_state.get("role")
    dark = st.session_state.get("dark_mode", False)
    current_screen = st.session_state.get("screen", "")

    if not role:
        return

    # ─────────────────────────────────────────────────────
    # COLORS — NagarSeva inspired (warm orange + neutrals)
    # ─────────────────────────────────────────────────────
    if dark:
        BG = "#0F1115"
        CARD = "#1A1D24"
        BORDER = "rgba(255,255,255,0.08)"
        TEXT = "#F5F5F4"
        SUB = "#A8A29E"
        HOVER_BG = "rgba(249,115,22,0.10)"
        ACTIVE_BG = "rgba(249,115,22,0.18)"
        ACTIVE_TEXT = "#FB923C"
        DANGER_BG = "rgba(220,38,38,0.12)"
        DANGER_TEXT = "#F87171"
    else:
        # Warm light palette inspired by reference
        BG = "#FFFFFF"
        CARD = "#FFF7ED"           # warm cream like reference
        BORDER = "#F1E9DD"
        TEXT = "#1C1917"           # near-black, fully visible
        SUB = "#78716C"
        HOVER_BG = "#FFF1E0"
        ACTIVE_BG = "#FFEDD5"
        ACTIVE_TEXT = "#EA580C"
        DANGER_BG = "#FEF2F2"
        DANGER_TEXT = "#DC2626"

    ACCENT = "#F97316"             # NagarSeva orange
    ACCENT_2 = "#FB923C"
    GRADIENT = f"linear-gradient(135deg, {ACCENT} 0%, {ACCENT_2} 100%)"

    # ─────────────────────────────────────────────────────
    # CSS — Stronger specificity to survive Streamlit reruns
    # ─────────────────────────────────────────────────────
    st.markdown(f"""
    <style>

    /* ===== Sidebar container ===== */
    section[data-testid="stSidebar"] {{
        width: 280px !important;
        min-width: 280px !important;
        background: {BG} !important;
        border-right: 1px solid {BORDER} !important;
        box-shadow: none !important;
    }}
    
        /* Fixed sidebar width across all screen sizes */
    section[data-testid="stSidebar"] {{
        min-width : 260px !important;
        max-width : 260px !important;
        width     : 260px !important;
    }}
    button[data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[kind="headerNoPadding"] {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: #FFFFFF !important;
        border: 1px solid #F1E9DD !important;
        border-radius: 10px !important;
        color: #F97316 !important;
        width: 40px !important;
        height: 40px !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 999999 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    button[data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg,
    button[kind="headerNoPadding"] svg {{
        color: #F97316 !important;
        fill: #F97316 !important;
        width: 20px !important;
        height: 20px !important;
    }}

    button[data-testid="stSidebarCollapsedControl"]:hover {{
        background: #FFEDD5 !important;
        border-color: #F97316 !important;
    }}

    

    /* Hide default Streamlit chrome */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{
        display: none;
    }}
    section[data-testid="stSidebar"] hr {{
        display: none;
    }}

    /* Force sidebar visible after login */
    section[data-testid="stSidebar"][aria-expanded="true"] {{
        transform: none !important;
        visibility: visible !important;
        opacity: 1 !important;
    }}

    .sb-wrap {{
        padding: 0.25rem 0.85rem 1.5rem;
    }}

    /* ===== Brand card ===== */
    .sb-brand {{
        background: {GRADIENT};
        border-radius: 16px;
        padding: 1rem 1.1rem;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(249,115,22,0.10),
                    0 8px 20px rgba(249,115,22,0.22);
        position: relative;
        overflow: hidden;
    }}

    .sb-brand::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(120% 80% at 100% 0%,
                    rgba(255,255,255,0.22), transparent 60%);
        pointer-events: none;
    }}

    .sb-brand-row {{
        display: flex;
        align-items: center;
        gap: 10px;
        position: relative;
        z-index: 1;
    }}

    .sb-brand-logo {{
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: rgba(255,255,255,0.20);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        border: 1px solid rgba(255,255,255,0.25);
    }}

    .sb-brand-text {{
        line-height: 1.1;
    }}

    .sb-brand-title {{
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: -0.01em;
    }}

    .sb-brand-title span {{
        opacity: 0.92;
        font-weight: 600;
    }}

    .sb-brand-sub {{
        font-size: 0.7rem;
        opacity: 0.92;
        margin-top: 0.2rem;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }}

    /* ===== User card ===== */
    .sb-user {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 0.7rem 0.8rem;
        margin-bottom: 1rem;
        transition: all 0.15s ease;
    }}

    .sb-user:hover {{
        border-color: {ACCENT};
        box-shadow: 0 2px 8px rgba(249,115,22,0.08);
    }}

    .sb-user-top {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .sb-avatar {{
        width: 38px;
        height: 38px;
        min-width: 38px;
        border-radius: 10px;
        background: {GRADIENT};
        display: flex;
        align-items: center;
        justify-content: center;
        color: white !important;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
        box-shadow: 0 2px 6px rgba(249,115,22,0.28);
    }}

    .sb-user-info {{
        min-width: 0;
        flex: 1;
    }}

    .sb-user-name {{
        color: {TEXT} !important;
        font-size: 0.88rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .sb-user-role {{
        color: {SUB} !important;
        font-size: 0.7rem;
        margin-top: 2px;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }}

    .sb-user-role::before {{
        content: "";
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 0 2px rgba(16,185,129,0.15);
    }}

    /* ===== Section labels ===== */
    .sb-section {{
        margin-top: 1rem;
        margin-bottom: 0.4rem;
        padding-left: 0.7rem;
        color: {SUB} !important;
        font-size: 0.66rem;
        font-weight: 700;
        letter-spacing: 0.10em;
        text-transform: uppercase;
    }}

    /* ===== Navigation buttons (STRONG specificity) ===== */
    section[data-testid="stSidebar"] div.stButton {{
        margin-bottom: 3px;
    }}

    section[data-testid="stSidebar"] div.stButton > button {{
        width: 100% !important;
        border-radius: 10px !important;
        height: 40px !important;
        min-height: 40px !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        background-color: transparent !important;
        color: {TEXT} !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        text-align: left !important;
        padding: 0 12px !important;
        letter-spacing: -0.005em !important;
        transition: background-color 0.15s ease, color 0.15s ease, transform 0.1s ease !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }}

    section[data-testid="stSidebar"] div.stButton > button p,
    section[data-testid="stSidebar"] div.stButton > button div,
    section[data-testid="stSidebar"] div.stButton > button span {{
        color: {TEXT} !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        margin: 0 !important;
    }}

    section[data-testid="stSidebar"] div.stButton > button:hover {{
        background: {HOVER_BG} !important;
        background-color: {HOVER_BG} !important;
        color: {ACTIVE_TEXT} !important;
        border-color: transparent !important;
        transform: translateX(2px) !important;
        box-shadow: none !important;
    }}

    section[data-testid="stSidebar"] div.stButton > button:hover p,
    section[data-testid="stSidebar"] div.stButton > button:hover div,
    section[data-testid="stSidebar"] div.stButton > button:hover span {{
        color: {ACTIVE_TEXT} !important;
    }}

    section[data-testid="stSidebar"] div.stButton > button:focus {{
        background: {HOVER_BG} !important;
        color: {TEXT} !important;
        box-shadow: none !important;
        outline: none !important;
    }}

    section[data-testid="stSidebar"] div.stButton > button:active {{
        background: {ACTIVE_BG} !important;
        color: {ACTIVE_TEXT} !important;
        transform: translateX(2px) !important;
    }}

    /* ===== Active nav item ===== */
    section[data-testid="stSidebar"] .nav-active div.stButton > button {{
        background: {ACTIVE_BG} !important;
        background-color: {ACTIVE_BG} !important;
        color: {ACTIVE_TEXT} !important;
        font-weight: 600 !important;
        border-left: 3px solid {ACCENT} !important;
        padding-left: 9px !important;
    }}

    section[data-testid="stSidebar"] .nav-active div.stButton > button p,
    section[data-testid="stSidebar"] .nav-active div.stButton > button div,
    section[data-testid="stSidebar"] .nav-active div.stButton > button span {{
        color: {ACTIVE_TEXT} !important;
        font-weight: 600 !important;
    }}

    /* ===== Logout button — danger style ===== */
    section[data-testid="stSidebar"] .nav-logout div.stButton > button:hover {{
        background: {DANGER_BG} !important;
        background-color: {DANGER_BG} !important;
        color: {DANGER_TEXT} !important;
    }}

    section[data-testid="stSidebar"] .nav-logout div.stButton > button:hover p,
    section[data-testid="stSidebar"] .nav-logout div.stButton > button:hover div,
    section[data-testid="stSidebar"] .nav-logout div.stButton > button:hover span {{
        color: {DANGER_TEXT} !important;
    }}

    /* ===== Footer ===== */
    .sb-footer {{
        margin-top: 1.25rem;
        padding: 0.8rem 0.9rem;
        border-radius: 12px;
        background: {CARD};
        border: 1px solid {BORDER};
        color: {SUB} !important;
        font-size: 0.7rem;
        text-align: center;
        line-height: 1.55;
        font-weight: 500;
    }}

    .sb-footer strong {{
        color: {ACTIVE_TEXT} !important;
        font-weight: 700;
    }}

    .sb-footer-dot {{
        display: inline-block;
        width: 6px;
        height: 6px;
        background: #10B981;
        border-radius: 50%;
        margin-right: 5px;
        vertical-align: middle;
        box-shadow: 0 0 0 2px rgba(16,185,129,0.15);
    }}

    /* ===== Scrollbar ===== */
    section[data-testid="stSidebar"] ::-webkit-scrollbar {{
        width: 6px;
    }}
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{
        background: {BORDER};
        border-radius: 3px;
    }}
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {{
        background: {ACCENT_2};
    }}

    /* ===== Responsive ===== */
    @media (max-width: 992px) {{
        section[data-testid="stSidebar"] {{
            width: 264px !important;
            min-width: 264px !important;
        }}
    }}

    @media (max-width: 768px) {{
        section[data-testid="stSidebar"] {{
            width: 85% !important;
            min-width: 260px !important;
            max-width: 320px !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.10) !important;
        }}

        .sb-wrap {{
            padding: 0.25rem 0.7rem 1.25rem;
        }}

        section[data-testid="stSidebar"] div.stButton > button {{
            height: 44px !important;
            min-height: 44px !important;
            font-size: 0.92rem !important;
        }}
    }}

    @media (max-width: 480px) {{
        .sb-brand-title {{
            font-size: 1rem;
        }}
        .sb-user-name {{
            font-size: 0.85rem;
        }}
    }}

    </style>
    """, unsafe_allow_html=True)

    role = st.session_state.role
    dark = st.session_state.dark_mode
    lang = st.session_state.language

    # ── Helper to get translation ──
    def _(key): return t(key)

    # ── Fetch unread notifications count for badge (dynamic) ──
    unread_count = 0
    if role == "user":
        uid = (st.session_state.user or {}).get("user_id")
        if uid:
            notifs = api("get", f"/schemes/user/notifications/{uid}")
            if isinstance(notifs, list):
                unread_count = len([n for n in notifs if not n.get("is_read")])

    with st.sidebar:
        # ── Brand / Logo ────────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;padding:20px 0 12px;">
            <div style="font-size:2.8rem;">🏛️</div>
            <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;font-weight:600;color:#d97706;">
                Jan Seva Portal
            </div>
            <div style="font-size:.7rem;opacity:.6;">जन सेवा पोर्टल</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ================================================================
        # USER PROFILE CARD (dynamic)
        # ================================================================
        if role == "user":
            u = st.session_state.user or {}
            name = u.get('name', 'Citizen')
            phone = u.get('phone', '')
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 16px; padding: 12px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: linear-gradient(135deg, #667eea, #764ba2); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">👤</div>
                    <div>
                        <div style="font-weight: 700; font-size: 1rem;">{name}</div>
                        <div style="font-size: 0.7rem; opacity: 0.7;">📞 {phone}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif role == "official":
            o = st.session_state.official or {}
            name = o.get('name', 'Official')
            dept = o.get('department', 'Department')
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 16px; padding: 12px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: linear-gradient(135deg, #667eea, #764ba2); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">🏢</div>
                    <div>
                        <div style="font-weight: 700; font-size: 1rem;">{name}</div>
                        <div style="font-size: 0.7rem; opacity: 0.7;">{dept}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif role == "admin":
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border-radius: 16px; padding: 12px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: linear-gradient(135deg, #667eea, #764ba2); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">👑</div>
                    <div>
                        <div style="font-weight: 700; font-size: 1rem;">System Admin</div>
                        <div style="font-size: 0.7rem; opacity: 0.7;">Administrator</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ================================================================
        # NAVIGATION MENU (collapsible groups)
        # ================================================================
        # We'll use Streamlit's native expander components for groups

        # --- MAIN MENU (always visible) ---
        st.markdown("#### 🧭 Navigation")

        if role == "user":
            # User menu items with icons, labels, screen names
            user_items = [
                ("🏠", _("dashboard"), "user_dashboard"),
                ("📢", _("file_complaint"), "file_complaint"),
                ("🔍", _("track_complaint"), "tracking"),
                ("📜", _("govt_schemes"), "schemes"),
                ("🤖", _("ai_assistant"), "assistant"),
                ("🔔", _("notifications"), "notifications"),  # Notifications will be handled separately for badge
            ]
            for icon, label, screen in user_items:
                active = (st.session_state.screen == screen)
                btn_label = f"{icon}  {label}"
                if active:
                    st.markdown(f'<div class="sidebar-active" style="background: linear-gradient(90deg, #667eea20, transparent); border-left: 3px solid #667eea;">', unsafe_allow_html=True)
                if st.button(btn_label, key=f"sb_{screen}", use_container_width=True):
                    st.session_state.screen = screen
                    st.rerun()
                if active:
                    st.markdown('</div>', unsafe_allow_html=True)

            # # Notifications with badge (dynamic)
            # notif_label = f"🔔 {_('notifications')}"
            # if unread_count > 0:
            #     notif_label = f"🔔 {_('notifications')} <span style='background:#EF4444; color:white; border-radius:20px; padding:0 8px; margin-left:6px; font-size:0.7rem;'>{unread_count}</span>"
            # active = (st.session_state.screen == "notifications")
            # if active:
            #     st.markdown(f'<div class="sidebar-active" style="background: linear-gradient(90deg, #667eea20, transparent); border-left: 3px solid #667eea;">', unsafe_allow_html=True)
            # if st.button(notif_label, key="sb_notifications", use_container_width=True):
            #     st.session_state.screen = "notifications"
            #     st.rerun()
            # if active:
            #     st.markdown('</div>', unsafe_allow_html=True)

        elif role == "official":
            off_items = [
                ("📊", _("dashboard"), "official_dashboard"),
                ("📋", _("complaints"), "official_complaints"),
                ("🏆", _("leaderboard"), "official_leaderboard"),
                ("📜", _("govt_schemes"), "schemes"),
            ]
            for icon, label, screen in off_items:
                active = (st.session_state.screen == screen)
                btn_label = f"{icon}  {label}"
                if active:
                    st.markdown(f'<div class="sidebar-active" style="background: linear-gradient(90deg, #667eea20, transparent); border-left: 3px solid #667eea;">', unsafe_allow_html=True)
                if st.button(btn_label, key=f"sb_{screen}", use_container_width=True):
                    st.session_state.screen = screen
                    st.rerun()
                if active:
                    st.markdown('</div>', unsafe_allow_html=True)

        elif role == "admin":
            # Admin menu with categories (use st.expander for groups)
            with st.expander("📊 Overview", expanded=False):
                admin_items = [
                    ("📊", _("dashboard"), "admin_dashboard"),
                    ("🏢", _("departments"), "admin_departments"),
                    ("👥", _("officials"), "admin_officials"),
                    ("📢", _("all_complaints"), "admin_complaints"),
                ]
                for icon, label, screen in admin_items:
                    active = (st.session_state.screen == screen)
                    btn_label = f"{icon}  {label}"
                    if active:
                        st.markdown(f'<div class="sidebar-active" style="background: linear-gradient(90deg, #667eea20, transparent); border-left: 3px solid #667eea;">', unsafe_allow_html=True)
                    if st.button(btn_label, key=f"sb_{screen}", use_container_width=True):
                        st.session_state.screen = screen
                        st.rerun()
                    if active:
                        st.markdown('</div>', unsafe_allow_html=True)
            with st.expander("🏆 Performance", expanded=False):
                perf_items = [
                    ("🏆", _("leaderboard"), "admin_leaderboard"),
                    ("🔮", "Predictive AI", "predictive_analytics"),
                    ("⏱️", "SLA Tracking", "sla_management"),
                ]
                for icon, label, screen in perf_items:
                    active = (st.session_state.screen == screen)
                    btn_label = f"{icon}  {label}"
                    if active:
                        st.markdown(f'<div class="sidebar-active" style="background: linear-gradient(90deg, #667eea20, transparent); border-left: 3px solid #667eea;">', unsafe_allow_html=True)
                    if st.button(btn_label, key=f"sb_{screen}", use_container_width=True):
                        st.session_state.screen = screen
                        st.rerun()
                    if active:
                        st.markdown('</div>', unsafe_allow_html=True)
            with st.expander("🏙️ City Analytics", expanded=False):
                if st.button("🏆 City Health Score", key="sb_city_health", use_container_width=True):
                    st.session_state.screen = "city_health_score"
                    st.rerun()
            with st.expander("📡 Live Monitoring", expanded=False):
                if st.button("📈 Live Dashboard", key="sb_live_dashboard", use_container_width=True):
                    st.session_state.screen = "live_dashboard"
                    st.rerun()
            with st.expander("📜 Content", expanded=False):
                content_items = [
                    ("📜", _("schemes"), "admin_schemes"),
                    ("🗺️", "Heatmap", "admin_heatmap"),
                ]
                for icon, label, screen in content_items:
                    active = (st.session_state.screen == screen)
                    btn_label = f"{icon}  {label}"
                    if active:
                        st.markdown(f'<div class="sidebar-active" style="background: linear-gradient(90deg, #667eea20, transparent); border-left: 3px solid #667eea;">', unsafe_allow_html=True)
                    if st.button(btn_label, key=f"sb_{screen}", use_container_width=True):
                        st.session_state.screen = screen
                        st.rerun()
                    if active:
                        st.markdown('</div>', unsafe_allow_html=True)

        # ================================================================
        # LOGGED OUT SIDEBAR
        # ================================================================
        else:
            st.info("👋 Please login to access the portal")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👤 Citizen", key="login_citizen", use_container_width=True):
                    st.session_state.screen = "user_login"
                    st.rerun()
            with col2:
                if st.button("🏢 Official", key="login_official", use_container_width=True):
                    st.session_state.screen = "official_login"
                    st.rerun()
            if st.button("👑 Admin", key="login_admin", use_container_width=True):
                st.session_state.screen = "admin_login"
                st.rerun()

        st.markdown("---")

        # ── Theme & Language Toggles (at bottom) ─────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            dark_label = "🌙 Dark" if not dark else "☀️ Light"
            if st.button(dark_label, key="sb_dark", use_container_width=True):
                st.session_state.dark_mode = not dark
                st.rerun()
        with col2:
            lang_label = "🇮🇳 HI" if st.session_state.language == "en" else "🇬🇧 EN"
            if st.button(lang_label, key="sb_lang", use_container_width=True):
                st.session_state.language = "hi" if st.session_state.language == "en" else "en"
                st.rerun()

        # Logout button (only when logged in)
        if role:
            if st.button("🔓 Logout", key="sb_logout", use_container_width=True):
                logout()

        # Footer
        st.markdown("""<div style="text-align:center;font-size:.66rem;opacity:.35;padding:12px 0 4px;">
            Jan Seva Portal v2.0<br>Made in 🇮🇳
        </div>""", unsafe_allow_html=True)
# def _sb_nav(items):
#     for icon, label, scr in items:
#         active = st.session_state.screen == scr
#         if active:
#             st.markdown('<div class="sidebar-active">', unsafe_allow_html=True)
#         if st.button(f"{icon}  {label}", key=f"sb_{scr}", use_container_width=True):
#             st.session_state.screen = scr
#             st.rerun()
#         if active:
#             st.markdown('</div>', unsafe_allow_html=True)
# ═════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═════════════════════════════════════════════════════════════════════════════
def route():
    s    = st.session_state.screen
    role = st.session_state.role

    # public
    if   s == "language":       pg_language()
    elif s == "login_type":     pg_login_type()
    elif s == "user_login":     pg_user_login()
    elif s == "official_login": pg_official_login()
    elif s == "admin_login":    pg_admin_login()
    elif s == "public_transparency":
        pg_public_transparency()

    # user
    elif s == "user_dashboard" and role == "user":  pg_user_dashboard()
    elif s == "file_complaint" and role == "user":  pg_file_complaint()
    elif s == "tracking":                           pg_tracking()
    elif s == "notifications"  and role == "user":  pg_notifications()
    elif s == "schemes":                            pg_schemes()
    elif s == "assistant"      and role == "user":  pg_assistant()

    # official
    elif s in ("official_dashboard", "official_complaints") and role == "official":
        pg_official_dashboard()
    elif s == "official_leaderboard" and role == "official":
        pg_official_leaderboard()

    # admin
    elif s == "admin_dashboard"   and role == "admin": pg_admin_dashboard()
    elif s == "admin_departments" and role == "admin": pg_admin_departments()
    elif s == "admin_officials"   and role == "admin": pg_admin_officials()
    elif s == "admin_complaints"  and role == "admin": pg_admin_complaints()
    elif s == "admin_leaderboard" and role == "admin": pg_admin_leaderboard()
    elif s == "admin_schemes"     and role == "admin": pg_admin_schemes()
    elif s == "admin_heatmap"     and role == "admin": pg_admin_heatmap()
    elif s == "predictive_analytics" and role == "admin": pg_predictive_analytics()
    elif s == "sla_management" and role == "admin": pg_sla_management()
    elif s == "city_health_score" and role == "admin":
        pg_city_health_score()
    elif s == "live_dashboard" and role == "admin":
        pg_live_dashboard()

    else:
        st.session_state.screen = (
            "user_dashboard"     if role == "user"     else
            "official_dashboard" if role == "official" else
            "admin_dashboard"    if role == "admin"    else "language"
        )
        st.rerun()




def analyze_sentiment(rating, comment=""):
    """Return 'positive', 'neutral', or 'negative' based on rating and comment."""
    comment = (comment or "").lower()
    # keyword lists (bilingual)
    positive_keywords = ["good", "excellent", "satisfied", "great", "thankful", "helpful", "quick", "resolve",
                         "अच्छा", "उत्कृष्ट", "संतुष्ट", "बहुत अच्छा", "धन्यवाद", "शानदार"]
    negative_keywords = ["bad", "poor", "unhappy", "dissatisfied", "waste", "useless", "slow", "ignored",
                         "खराब", "बेकार", "असंतुष्ट", "निराश", "धीमा", "अनदेखा"]
    if rating >= 4:
        return "positive"
    elif rating <= 2:
        return "negative"
    elif rating == 3:
        # Use comment to break tie
        if any(kw in comment for kw in positive_keywords):
            return "positive"
        elif any(kw in comment for kw in negative_keywords):
            return "negative"
        return "neutral"
    return "neutral"
# ═════════════════════════════════════════════════════════════════════════════
# PUBLIC SCREENS
# ═════════════════════════════════════════════════════════════════════════════
def pg_language():
    _apply_layout("auth")          
    
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 50%, #10B981 100%);
        border-radius: 24px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 80%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .hero-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.9);
        position: relative;
        z-index: 1;
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem 1.2rem;
        border-radius: 50px;
        font-size: 0.75rem;
        margin-top: 1rem;
        position: relative;
        z-index: 1;
        color: white;
    }
    
    .section-header {
        text-align: center;
        margin: 2rem 0 1rem 0;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .section-subtitle {
        font-size: 0.9rem;
        color: #6B7280;
    }
    
    .lang-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .lang-card {
        background: white;
        border-radius: 24px;
        padding: 1.8rem;
        text-align: center;
        transition: all 0.3s ease;
        border: 2px solid #E5E7EB;
        cursor: pointer;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .lang-card:hover {
        transform: translateY(-4px);
        border-color: #0EA5E9;
        box-shadow: 0 16px 30px -10px rgba(14, 165, 233, 0.25);
    }
    
    .lang-flag {
        font-size: 3rem;
        margin-bottom: 0.75rem;
    }
    
    .lang-name {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.25rem;
    }
    
    .lang-native {
        font-size: 0.85rem;
        color: #6B7280;
    }
    
    .guide-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .guide-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        border: 1px solid #E5E7EB;
        position: relative;
        overflow: hidden;
    }
    
    .guide-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #0EA5E9, #06B6D4);
    }
    
    .guide-card:hover {
        transform: translateX(5px);
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
    }
    
    .guide-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
    }
    
    .guide-number {
        display: inline-block;
        background: #0EA5E9;
        color: white;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        margin-bottom: 0.5rem;
    }
    
    .guide-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    
    .guide-desc {
        font-size: 0.8rem;
        color: #6B7280;
        line-height: 1.5;
    }
    
    .scheme-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .scheme-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 16px;
        padding: 1rem;
        transition: all 0.3s ease;
        border: 1px solid #bbf7d0;
    }
    
    .scheme-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -5px rgba(34,197,94,0.2);
    }
    
    .scheme-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    .scheme-name {
        font-size: 0.9rem;
        font-weight: 700;
        color: #166534;
    }
    
    .scheme-desc {
        font-size: 0.7rem;
        color: #4B5563;
        margin-top: 0.25rem;
        line-height: 1.4;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
        text-align: center;
    }
    
    .feature-item {
        background: #F9FAFB;
        border-radius: 16px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transform: translateY(-3px);
    }
    
    .feature-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-text {
        font-size: 0.8rem;
        font-weight: 600;
        color: #374151;
    }
    
    .feature-sub {
        font-size: 0.65rem;
        color: #9CA3AF;
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #E5E7EB;
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0EA5E9;
    }
    
    .stat-label {
        font-size: 0.7rem;
        color: #6B7280;
    }
    
    .testimonial-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .testimonial-card {
        background: #FFFBEB;
        border-radius: 16px;
        padding: 1rem;
        border-left: 4px solid #F59E0B;
    }
    
    .testimonial-text {
        font-size: 0.8rem;
        color: #374151;
        line-height: 1.5;
        font-style: italic;
    }
    
    .testimonial-author {
        font-size: 0.7rem;
        color: #9CA3AF;
        margin-top: 0.5rem;
    }
    
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid #E5E7EB;
        font-size: 0.7rem;
        color: #9CA3AF;
    }
    
    .help-box {
        background: #F3F4F6;
        border-radius: 20px;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-up {
        animation: fadeInUp 0.6s ease forwards;
    }
    
    @media (max-width: 768px) {
        .stat-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .hero-title {
            font-size: 1.6rem;
        }
        .section-title {
            font-size: 1.3rem;
        }
    }
    </style>
    
    <div class="main-container">
        <div class="hero-section fade-up">
            <div class="hero-icon">🏛️</div>
            <div class="hero-title">Jan Seva Portal</div>
            <div class="hero-subtitle">AI-Powered Citizen Grievance Management System</div>
            <div class="hero-badge">🇮🇳 Digital India | Smart Governance</div>
        </div>
        
        
    """, unsafe_allow_html=True)
    
    # ============================================================
    # LANGUAGE SELECTION
    # ============================================================
    st.markdown('<div class="section-header"><div class="section-title">🌐 Choose Your Language</div><div class="section-subtitle">अपनी भाषा चुनें | Select your preferred language</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="lang-card">
            <div class="lang-flag">🇬🇧</div>
            <div class="lang-name">English</div>
            <div class="lang-native">International Language</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🌐 Continue in English", key="lang_en", use_container_width=True):
            st.session_state.language = "en"
            st.session_state.screen = "login_type"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="lang-card">
            <div class="lang-flag">🇮🇳</div>
            <div class="lang-name">हिंदी</div>
            <div class="lang-native">भारत की राष्ट्रीय भाषा</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🇮🇳 हिंदी में जारी रखें", key="lang_hi", use_container_width=True):
            st.session_state.language = "hi"
            st.session_state.screen = "login_type"
            st.rerun()
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📊 View Public Transparency Portal", use_container_width=True):
            st.session_state.screen = "public_transparency"
            st.rerun()

    # ============================================================
    # HOW IT WORKS - USER GUIDE
    # ============================================================
    st.markdown('<div class="section-header"><div class="section-title">📚 How It Works</div><div class="section-subtitle">Simple 3-step process to get your issues resolved</div></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="guide-grid">
        <div class="guide-card">
            <div class="guide-number">STEP 01</div>
            <div class="guide-icon">📝</div>
            <div class="guide-title">File a Complaint</div>
            <div class="guide-desc">Describe your issue in text or voice, add location and photos. Our AI automatically categorizes and assigns it to the right department.</div>
        </div>
        
       
    """, unsafe_allow_html=True)
    
    # ============================================================
    # GOVERNMENT SCHEMES
    # ============================================================
   
    
    # ============================================================
    # KEY FEATURES
    # ============================================================
    st.markdown('<div class="section-header"><div class="section-title">✨ Key Features</div><div class="section-subtitle">What makes our platform special</div></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <div class="feature-text">AI-Powered</div>
            <div class="feature-sub">Smart categorization</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🎤</div>
            <div class="feature-text">Voice Input</div>
            <div class="feature-sub">Speak your complaint</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📍</div>
            <div class="feature-text">GPS Location</div>
            <div class="feature-sub">Auto-detect address</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🔔</div>
            <div class="feature-text">Real-time Alerts</div>
            <div class="feature-sub">Instant notifications</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">⏱️</div>
            <div class="feature-text">SLA Tracking</div>
            <div class="feature-sub">Time-bound resolution</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📊</div>
            <div class="feature-text">Analytics</div>
            <div class="feature-sub">Data-driven insights</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🌙</div>
            <div class="feature-text">Dark Mode</div>
            <div class="feature-sub">Eye-friendly interface</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🔒</div>
            <div class="feature-text">Secure & Private</div>
            <div class="feature-sub">Data encryption</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================
    # CONTACT & SUPPORT
    # ============================================================
    st.markdown("""
    <div class="help-box">
        <div style="font-size: 1rem; font-weight: 600; color: #1F2937;">📞 Need Help?</div>
        <div style="font-size: 0.8rem; color: #6B7280; margin-top: 0.5rem;">
            Toll-Free Helpline: <strong>1800-XXX-XXXX</strong> | Email: <strong>support@janseva.gov.in</strong>
        </div>
        <div style="font-size: 0.7rem; color: #9CA3AF; margin-top: 0.5rem;">
            Working Hours: Monday - Saturday, 9:00 AM to 6:00 PM
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================
    # FOOTER
    # ============================================================
    st.markdown("""
    <div class="footer">
        © 2024 Jan Seva Portal | An Initiative by Government of India | Version 2.0<br>
        Empowering Citizens | Ensuring Accountability | Enhancing Governance
    </div>
    """, unsafe_allow_html=True)
    
    # Voice Greeting
    st.components.v1.html("""
    <script>
    setTimeout(function() {
        var msg = new SpeechSynthesisUtterance("Welcome to Jan Seva Portal. Citizen Grievance Management System. Please select your language to continue.");
        msg.lang = 'en-IN';
        msg.rate = 0.85;
        window.speechSynthesis.speak(msg);
    }, 500);
    </script>
    """, height=0)

 
import streamlit as st
 
def t(key: str, fallback: str = "") -> str:
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, fallback or key)
 
 
# ═══════════════════════════════════════════════════════════════════════════════
#  Extra login-specific translations not in config (extend here cleanly)
# ═══════════════════════════════════════════════════════════════════════════════
 
_LOGIN_EXTRA = {
    "en": {
        # Role selection
        "choose_role":          "Choose your role",
        "choose_role_sub":      "Select how you'd like to access the Jan Seva Portal",
        "citizen_desc":         "File complaints, track status & access government schemes",
        "official_desc":        "Manage & resolve complaints for your department",
        "admin_desc":           "System management, analytics & oversight",
        "continue_citizen":     "Continue as Citizen",
        "continue_official":    "Continue as Official",
        "continue_admin":       "Continue as Admin",
        "change_language":      "← Change Language",
        "secure_trusted":       "Secure · Trusted · Government of India",
        "govt_india":           "Government of India Initiative",
        "secure_badge":         "● Secure",
        # Citizen login
        "welcome_back":         "Welcome back",
        "citizen_hero_sub":     "File complaints · track status · access schemes",
        "sign_in":              "Sign In",
        "create_account":       "Create Account",
        "phone_verification":   "Phone Verification",
        "otp_hint":             "We'll send a one-time password to verify your number.",
        "mobile_number":        "Mobile number",
        "mobile_placeholder":   "Enter your 10-digit number",
        "send_otp_arrow":       "Send OTP →",
        "otp_sent_to":          "OTP sent to",
        "demo_otp_label":       "Demo OTP",
        "enter_otp":            "Enter OTP",
        "otp_placeholder":      "6-digit code",
        "verify_sign_in":       "Verify & Sign In →",
        "resend_otp":           "🔄 Resend OTP",
        "change_number":        "← Change number",
        "full_name":            "Full name *",
        "full_name_ph":         "Your full name",
        "phone_star":           "Phone number *",
        "phone_ph":             "10-digit number",
        "address_star":         "Address *",
        "address_ph":           "Your complete address",
        "create_account_arrow": "Create Account →",
        "back_role":            "← Back to role selection",
        "terms":                "By continuing you agree to our Terms of Service",
        "already_registered":   "Phone already registered — please sign in.",
        "reg_failed":           "Registration failed.",
        "otp_sent_success":     "New OTP sent!",
        "enter_phone_err":      "Please enter your phone number.",
        "invalid_phone_err":    "Enter a valid 10-digit number (digits only).",
        "enter_otp_err":        "Please enter the OTP.",
        "invalid_otp_err":      "Invalid OTP. Please try again.",
        "enter_name_err":       "Please enter your full name.",
        "invalid_phone2_err":   "Enter a valid 10-digit phone number.",
        "enter_address_err":    "Please enter your address.",
        "account_created":      "✅ Account created! Switch to Sign In to continue.",
        # Official login
        "official_hero":        "Official Portal",
        "official_hero_sub":    "Department management & complaint resolution",
        "official_creds":       "Official credentials",
        "email_placeholder":    "official@department.gov.in",
        "password_ph":          "Your password",
        "sign_in_arrow":        "Sign In →",
        "request_access":       "Request Access",
        "forgot_password":      "Forgot password?",
        "reset_password":       "Reset Password",
        "reg_email":            "Registered email address",
        "send_reset_otp":       "Send Reset OTP →",
        "verify_otp_arrow":     "Verify OTP →",
        "resend":               "Resend",
        "new_password":         "New password",
        "confirm_password":     "Confirm new password",
        "reset_arrow":          "Reset Password →",
        "back_sign_in":         "← Back to sign in",
        "your_details":         "Your details",
        "phone_verify":         "Phone verification",
        "full_name_req":        "Full name *",
        "email_req":            "Email address *",
        "phone_req":            "Phone (10 digits) *",
        "pass_req":             "Password (min 6 chars) *",
        "dept_code_req":        "Department code *",
        "dept_code_help":       "Get this from your department admin",
        "continue_arrow":       "Continue →",
        "submit_request":       "Submit Request →",
        "edit_details":         "← Edit details",
        "otp_sent_demo":        "OTP sent to {masked} — use demo code 123456",
        "demo_otp_sent":        "Demo OTP sent — use **123456**",
        "otp_resent":           "Demo OTP resent — still 123456.",
        "phone_verified":       "Phone verified — ready to submit!",
        "verify_first":         "Verify your OTP above before submitting.",
        "email_verified":       "Email verified — set your new password",
        "request_submitted":    "✅ Request submitted! Awaiting admin approval.",
        "already_registered2":  "Email already registered — try signing in.",
        "enter_email_err":      "Please enter your email.",
        "invalid_email_err":    "Enter a valid email address.",
        "enter_both_err":       "Please enter both email and password.",
        "missing_fields":       "Missing: ",
        "phone_10_err":         "Phone must be exactly 10 digits.",
        "pass_6_err":           "Password must be at least 6 characters.",
        "fill_both_err":        "Please fill both fields.",
        "pass_mismatch_err":    "Passwords do not match.",
        "reset_success":        "✅ Password reset! Please sign in.",
        "reset_failed":         "Reset failed: ",
        "invalid_otp_123":      "Invalid OTP — use 123456.",
        "code_sent_to":         "Code sent to {email} — use 123456",
        # Admin login
        "admin_hero":           "Admin Panel",
        "admin_hero_sub":       "System administration · analytics · oversight",
        "admin_creds":          "Administrator credentials",
        "username_label":       "Username",
        "username_ph":          "Enter your username",
        "password_label":       "Password",
        "password_ph2":         "Enter your password",
        "sign_in_admin":        "Sign In to Admin Panel →",
        "default_creds":        "Default credentials",
        "default_creds_val":    "Username: admin  ·  Password: admin123",
        "enter_username_err":   "Please enter your username.",
        "enter_password_err":   "Please enter your password.",
        "invalid_creds_err":    "Invalid username or password.",
        # Step labels
        "step_details":         "Details",
        "step_verify":          "Verify",
    },
    "hi": {
        # Role selection
        "choose_role":          "अपनी भूमिका चुनें",
        "choose_role_sub":      "जन सेवा पोर्टल तक पहुंचने का तरीका चुनें",
        "citizen_desc":         "शिकायत दर्ज करें, स्थिति ट्रैक करें और सरकारी योजनाओं तक पहुंचें",
        "official_desc":        "अपने विभाग की शिकायतें प्रबंधित करें और हल करें",
        "admin_desc":           "सिस्टम प्रबंधन, विश्लेषण और निगरानी",
        "continue_citizen":     "नागरिक के रूप में जारी रखें",
        "continue_official":    "अधिकारी के रूप में जारी रखें",
        "continue_admin":       "एडमिन के रूप में जारी रखें",
        "change_language":      "← भाषा बदलें",
        "secure_trusted":       "सुरक्षित · विश्वसनीय · भारत सरकार",
        "govt_india":           "भारत सरकार की पहल",
        "secure_badge":         "● सुरक्षित",
        # Citizen login
        "welcome_back":         "वापस स्वागत है",
        "citizen_hero_sub":     "शिकायत दर्ज · स्थिति ट्रैक · योजनाएं देखें",
        "sign_in":              "साइन इन",
        "create_account":       "खाता बनाएं",
        "phone_verification":   "फ़ोन सत्यापन",
        "otp_hint":             "हम आपके नंबर को सत्यापित करने के लिए OTP भेजेंगे।",
        "mobile_number":        "मोबाइल नंबर",
        "mobile_placeholder":   "10 अंकों का नंबर दर्ज करें",
        "send_otp_arrow":       "OTP भेजें →",
        "otp_sent_to":          "OTP भेजा गया",
        "demo_otp_label":       "डेमो OTP",
        "enter_otp":            "OTP दर्ज करें",
        "otp_placeholder":      "6 अंकों का कोड",
        "verify_sign_in":       "सत्यापित करें और साइन इन करें →",
        "resend_otp":           "🔄 OTP दोबारा भेजें",
        "change_number":        "← नंबर बदलें",
        "full_name":            "पूरा नाम *",
        "full_name_ph":         "आपका पूरा नाम",
        "phone_star":           "फ़ोन नंबर *",
        "phone_ph":             "10 अंकों का नंबर",
        "address_star":         "पता *",
        "address_ph":           "आपका पूरा पता",
        "create_account_arrow": "खाता बनाएं →",
        "back_role":            "← भूमिका चयन पर वापस",
        "terms":                "जारी रखने पर आप हमारी सेवा शर्तों से सहमत होते हैं",
        "already_registered":   "फ़ोन पहले से पंजीकृत है — कृपया साइन इन करें।",
        "reg_failed":           "पंजीकरण विफल।",
        "otp_sent_success":     "नया OTP भेजा गया!",
        "enter_phone_err":      "कृपया अपना फ़ोन नंबर दर्ज करें।",
        "invalid_phone_err":    "10 अंकों का मान्य नंबर दर्ज करें (केवल अंक)।",
        "enter_otp_err":        "कृपया OTP दर्ज करें।",
        "invalid_otp_err":      "अमान्य OTP। कृपया पुनः प्रयास करें।",
        "enter_name_err":       "कृपया अपना पूरा नाम दर्ज करें।",
        "invalid_phone2_err":   "10 अंकों का मान्य फ़ोन नंबर दर्ज करें।",
        "enter_address_err":    "कृपया अपना पता दर्ज करें।",
        "account_created":      "✅ खाता बनाया गया! साइन इन पर जाएं।",
        # Official login
        "official_hero":        "अधिकारी पोर्टल",
        "official_hero_sub":    "विभाग प्रबंधन और शिकायत समाधान",
        "official_creds":       "अधिकारी प्रमाण पत्र",
        "email_placeholder":    "official@department.gov.in",
        "password_ph":          "आपका पासवर्ड",
        "sign_in_arrow":        "साइन इन करें →",
        "request_access":       "एक्सेस अनुरोध",
        "forgot_password":      "पासवर्ड भूल गए?",
        "reset_password":       "पासवर्ड रीसेट करें",
        "reg_email":            "पंजीकृत ईमेल पता",
        "send_reset_otp":       "रीसेट OTP भेजें →",
        "verify_otp_arrow":     "OTP सत्यापित करें →",
        "resend":               "दोबारा भेजें",
        "new_password":         "नया पासवर्ड",
        "confirm_password":     "पासवर्ड की पुष्टि करें",
        "reset_arrow":          "पासवर्ड रीसेट करें →",
        "back_sign_in":         "← साइन इन पर वापस",
        "your_details":         "आपकी जानकारी",
        "phone_verify":         "फ़ोन सत्यापन",
        "full_name_req":        "पूरा नाम *",
        "email_req":            "ईमेल पता *",
        "phone_req":            "फ़ोन (10 अंक) *",
        "pass_req":             "पासवर्ड (न्यूनतम 6 अक्षर) *",
        "dept_code_req":        "विभाग कोड *",
        "dept_code_help":       "अपने विभाग एडमिन से प्राप्त करें",
        "continue_arrow":       "आगे बढ़ें →",
        "submit_request":       "अनुरोध जमा करें →",
        "edit_details":         "← जानकारी संपादित करें",
        "otp_sent_demo":        "OTP भेजा {masked} पर — डेमो कोड 123456 उपयोग करें",
        "demo_otp_sent":        "डेमो OTP भेजा — **123456** उपयोग करें",
        "otp_resent":           "डेमो OTP दोबारा भेजा — अभी भी 123456।",
        "phone_verified":       "फ़ोन सत्यापित — जमा करने के लिए तैयार!",
        "verify_first":         "जमा करने से पहले OTP सत्यापित करें।",
        "email_verified":       "ईमेल सत्यापित — नया पासवर्ड सेट करें",
        "request_submitted":    "✅ अनुरोध जमा हुआ! एडमिन की स्वीकृति की प्रतीक्षा।",
        "already_registered2":  "ईमेल पहले से पंजीकृत — साइन इन करें।",
        "enter_email_err":      "कृपया अपना ईमेल दर्ज करें।",
        "invalid_email_err":    "मान्य ईमेल पता दर्ज करें।",
        "enter_both_err":       "कृपया ईमेल और पासवर्ड दोनों दर्ज करें।",
        "missing_fields":       "अनुपस्थित: ",
        "phone_10_err":         "फ़ोन नंबर ठीक 10 अंकों का होना चाहिए।",
        "pass_6_err":           "पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।",
        "fill_both_err":        "कृपया दोनों फ़ील्ड भरें।",
        "pass_mismatch_err":    "पासवर्ड मेल नहीं खाते।",
        "reset_success":        "✅ पासवर्ड रीसेट हुआ! कृपया साइन इन करें।",
        "reset_failed":         "रीसेट विफल: ",
        "invalid_otp_123":      "अमान्य OTP — 123456 उपयोग करें।",
        "code_sent_to":         "कोड {email} पर भेजा — 123456 उपयोग करें",
        # Admin login
        "admin_hero":           "एडमिन पैनल",
        "admin_hero_sub":       "सिस्टम प्रशासन · विश्लेषण · निगरानी",
        "admin_creds":          "प्रशासक प्रमाण पत्र",
        "username_label":       "उपयोगकर्ता नाम",
        "username_ph":          "अपना उपयोगकर्ता नाम दर्ज करें",
        "password_label":       "पासवर्ड",
        "password_ph2":         "अपना पासवर्ड दर्ज करें",
        "sign_in_admin":        "एडमिन पैनल में साइन इन →",
        "default_creds":        "डिफ़ॉल्ट प्रमाण पत्र",
        "default_creds_val":    "उपयोगकर्ता नाम: admin  ·  पासवर्ड: admin123",
        "enter_username_err":   "कृपया उपयोगकर्ता नाम दर्ज करें।",
        "enter_password_err":   "कृपया पासवर्ड दर्ज करें।",
        "invalid_creds_err":    "अमान्य उपयोगकर्ता नाम या पासवर्ड।",
        # Step labels
        "step_details":         "जानकारी",
        "step_verify":          "सत्यापन",
    }
}
 
 
def tx(key: str, fallback: str = "") -> str:
    """Translate from login-specific dictionary first, fall back to config TRANSLATIONS."""
    lang = st.session_state.get("language", "en")
    val = _LOGIN_EXTRA.get(lang, _LOGIN_EXTRA["en"]).get(key)
    if val:
        return val
    # fall back to config.py TRANSLATIONS
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, fallback or key)
 
# ─────────────────────────────────────────────────────────────────────────────
#  Shared base CSS  (inject once via get_css() in your real app)
# ─────────────────────────────────────────────────────────────────────────────
 
def _base_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=Sora:wght@600;700&display=swap');
 
/* ── Reset & base ─────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}
.stApp {
    background: #F5F3EF !important;
}
.block-container {
    padding-top: 0 !important;
    max-width: 860px !important;
}
 
/* ── Hide Streamlit chrome ────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
 
/* ── Streamlit button override ────────────────────────────────────── */


 
/* ── Inputs ───────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    font-family: 'DM Sans', sans-serif !important;
    background: #FAFAFA !important;
    border: 1.5px solid #E5E7EB !important;
    border-radius: 10px !important;
    color: #111827 !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.10) !important;
    background: #fff !important;
}
.stTextInput label, .stTextArea label {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: #374151 !important;
    font-family: 'DM Sans', sans-serif !important;
}
 
/* ── Tabs ─────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #F3F4F6 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border-bottom: none !important;
}


.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
 
/* ── Form submit button ───────────────────────────────────────────── */
.stFormSubmitButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    padding: 11px 18px !important;
    color: #fff !important;
    border: none !important;
    width: 100% !important;
}
 
/* ── Alerts ───────────────────────────────────────────────────────── */
.stAlert {
    border-radius: 10px !important;
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
    border-left-width: 3px !important;
}
 
/* ── Spinner ──────────────────────────────────────────────────────── */
.stSpinner > div { border-color: #6366F1 transparent transparent !important; }
</style>
"""
 
 
def _login_css(accent: str = "#6366F1", accent2: str = "#8B5CF6") -> str:
    """Per-page accent colours injected on top of base."""
    return f"""
<style>
/* Primary CTA button (accent coloured) */
div[data-testid="stForm"] .stFormSubmitButton > button,
.primary-btn .stButton > button {{
    background: linear-gradient(135deg, {accent}, {accent2}) !important;
    border: none !important;
    color: #fff !important;
    box-shadow: 0 2px 10px {accent}44 !important;
}}
div[data-testid="stForm"] .stFormSubmitButton > button:hover,
.primary-btn .stButton > button:hover {{
    filter: brightness(1.08) !important;
}}
 
/* Ghost back button */
.ghost-btn .stButton > button {{
    background: transparent !important;
    border: 1.5px solid #E5E7EB !important;
    color: #6B7280 !important;
    font-size: 12.5px !important;
}}
.ghost-btn .stButton > button:hover {{
    background: #F9FAFB !important;
    color: #374151 !important;
}}
</style>
"""
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  HTML building blocks
# ─────────────────────────────────────────────────────────────────────────────
 
def _topbar() -> str:
    return """
<div style="
    background:#1A1A1A;
    padding:10px 28px;
    border-radius:0 0 16px 16px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:32px;
">
    <div style="display:flex;align-items:center;gap:12px;">
        <div style="
            width:38px;height:38px;
            background:#E8660A;
            border-radius:9px;
            display:flex;align-items:center;justify-content:center;
            font-size:20px;
        ">🏛️</div>
        <div>
            <div style="font-family:'Sora',sans-serif;font-weight:700;font-size:15px;color:#fff;letter-spacing:-0.3px;">
                Jan Seva Portal
            </div>
            <div style="font-size:11px;color:rgba(255,255,255,0.4);font-weight:300;">
                Government of India Initiative
            </div>
        </div>
    </div>
    <div style="
        background:rgba(232,102,10,0.15);
        border:1px solid rgba(232,102,10,0.35);
        color:#E8660A;
        font-size:11px;font-weight:500;
        padding:4px 12px;border-radius:20px;
        letter-spacing:0.5px;
    ">● SECURE</div>
</div>
"""
 
 
def _hero(icon: str, title: str, subtitle: str, gradient: str) -> str:
    return f"""
<div style="
    background:{gradient};
    border-radius:20px;
    padding:36px 28px 30px;
    text-align:center;
    margin-bottom:20px;
    position:relative;
    overflow:hidden;
">
    <div style="
        position:absolute;top:-40px;right:-40px;
        width:150px;height:150px;
        background:rgba(255,255,255,0.04);
        border-radius:50%;
    "></div>
    <div style="font-size:2.6rem;margin-bottom:14px;filter:drop-shadow(0 4px 12px rgba(0,0,0,0.25));">{icon}</div>
    <div style="font-family:'Sora',sans-serif;font-size:22px;font-weight:700;color:#fff;letter-spacing:-0.4px;margin-bottom:6px;">
        {title}
    </div>
    <div style="font-size:13px;color:rgba(255,255,255,0.6);font-weight:300;">{subtitle}</div>
</div>
"""
 
 
def _card_open(label: str = "") -> str:
    label_html = f'<div style="font-size: 23.5px;font-weight: 490;color: rgb(44 65 100);letter-spacing: 3.1px;text-transform: uppercase;margin-bottom: -5px;">{label}</div>' if label else ""
    return f"""
<div style="
    background:#fff;
    border:1.5px solid #E5E7EB;
    border-radius:16px;
    padding:12px;
    margin-bottom:13px;
">
{label_html}
"""
 
 
def _card_close() -> str:
    return "</div>"
 
 
def _role_tile(css_class: str, icon: str, title: str, desc: str, gradient: str) -> str:
    return f"""
<div style="
    background:#fff;
    border:1.5px solid #E5E7EB;
    border-radius:16px;
    padding:28px 18px 22px;
    text-align:center;
    position:relative;
    overflow:hidden;
    transition:all 0.2s ease;
">
    <div style="
        position:absolute;top:0;left:0;right:0;
        height:3px;
        background:{gradient};
        border-radius:16px 16px 0 0;
    "></div>
    <div style="font-size:2rem;margin-bottom:12px;">{icon}</div>
    <div style="font-family:'Sora',sans-serif;font-size:14px;font-weight:700;color:#111827;margin-bottom:6px;">
        {title}
    </div>
    <div style="font-size:12px;color:#6B7280;line-height:1.55;margin-bottom:18px;font-weight:300;">
        {desc}
    </div>
</div>
"""
 
 
def _otp_badge(phone: str, otp: str) -> str:
    return f"""
<div style="
    background:#F8FAFC;
    border:1px solid #E5E7EB;
    border-radius:12px;
    padding:14px 16px;
    margin-bottom:16px;
    display:flex;
    align-items:center;
    gap:10px;
">
    <span style="font-size:1.1rem;">📱</span>
    <div>
        <div style="font-size:11px;color:#9CA3AF;font-weight:400;margin-bottom:2px;">OTP sent to</div>
        <div style="font-size:13.5px;color:#111827;font-weight:500;">+91 {phone}</div>
    </div>
    <div style="
        margin-left:auto;
        background:linear-gradient(135deg,#F0FDF4,#DCFCE7);
        border:1px solid #BBF7D0;
        border-radius:8px;
        padding:6px 12px;
        text-align:center;
    ">
        <div style="font-size:10px;color:#6B7280;font-weight:400;">Demo OTP</div>
        <div style="font-size:18px;font-weight:700;color:#16A34A;letter-spacing:3px;">{otp}</div>
    </div>
</div>
"""
 
 
def _step_indicator(step: int) -> str:
    s1_cls = "active" if step == 1 else "done"
    s2_cls = "active" if step == 2 else "idle"
    s1_txt = "1" if step == 1 else "✓"
 
    def dot(cls, txt):
        if cls == "active":
            bg, color, border = "#6366F1", "#fff", "#6366F1"
        elif cls == "done":
            bg, color, border = "#ECFDF5", "#16A34A", "#16A34A"
        else:
            bg, color, border = "#F3F4F6", "#9CA3AF", "#E5E7EB"
        return f"""
        <div style="
            width:30px;height:30px;
            border-radius:50%;
            background:{bg};
            border:2px solid {border};
            color:{color};
            font-size:12px;font-weight:600;
            display:flex;align-items:center;justify-content:center;
        ">{txt}</div>"""
 
    def lbl(cls, text):
        color = "#111827" if cls in ("active", "done") else "#9CA3AF"
        return f'<div style="font-size:11px;color:{color};font-weight:{"500" if cls=="active" else "400"};margin-top:4px;">{text}</div>'
 
    return f"""
<div style="display:flex;align-items:center;justify-content:center;gap:0;margin-bottom:24px;">
    <div style="text-align:center;">
        {dot(s1_cls, s1_txt)}
        {lbl(s1_cls, "Details")}
    </div>
    <div style="flex:1;max-width:80px;height:2px;background:{'#6366F1' if step==2 else '#E5E7EB'};margin:0 12px;margin-bottom:18px;border-radius:2px;"></div>
    <div style="text-align:center;">
        {dot(s2_cls, "2")}
        {lbl(s2_cls, "Verify")}
    </div>
</div>
"""
 
 
def _info_box(text: str, icon: str = "ℹ️") -> str:
    return f"""
<div style="
    background:#EFF6FF;border:1px solid #BFDBFE;
    border-radius:10px;padding:12px 14px;
    font-size:13px;color:#1D4ED8;
    margin-bottom:14px;display:flex;align-items:center;gap:8px;
">
    <span>{icon}</span><span>{text}</span>
</div>
"""
 
 
def _warn_box(text: str) -> str:
    return f"""
<div style="
    background:#FFFBEB;border:1px solid #FDE68A;
    border-radius:10px;padding:12px 14px;
    font-size:13px;color:#92400E;
    margin-bottom:14px;display:flex;align-items:center;gap:8px;
">
    <span>⚠️</span><span>{text}</span>
</div>
"""
 
 
def _verified_box(text: str) -> str:
    return f"""
<div style="
    background:#F0FDF4;border:1px solid #BBF7D0;
    border-radius:10px;padding:12px 14px;
    font-size:13px;color:#16A34A;font-weight:500;
    margin-bottom:14px;display:flex;align-items:center;gap:8px;
">
    <span>✅</span><span>{text}</span>
</div>
"""
 
 
def _divider() -> str:
    return '<div style="height:14px;"></div>'
 
 
def _footer(text: str = "Secure · Trusted · Government of India") -> str:
    return f"""
<div style="
    text-align:center;
    font-size:11.5px;
    color:#9CA3AF;
    font-weight:300;
    letter-spacing:0.5px;
    margin-top:8px;
    padding-bottom:24px;
">
    {text}
</div>
"""
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  Primary accent button helper
#  Wraps a st.button in a <div class="primary-btn"> so CSS can colour it
# ─────────────────────────────────────────────────────────────────────────────
 
def _primary_btn(label: str, key: str, accent: str = "#6366F1", accent2: str = "#8B5CF6") -> bool:
    st.markdown(f"""
    <style>
    div[data-testid="stButton"][id="{key}"] > button,
    #btn_{key} .stButton > button {{
        background: linear-gradient(135deg, {accent}, {accent2}) !important;
        border: none !important;
        color: #fff !important;
        box-shadow: 0 2px 10px {accent}44 !important;
        width: 100% !important;
        padding: 11px 16px !important;
        font-size: 14px !important;
    }}
    </style>
    <div id="btn_{key}">
    """, unsafe_allow_html=True)
    clicked = st.button(label, key=key, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    return clicked
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  pg_login_type  — Role selection screen
# ─────────────────────────────────────────────────────────────────────────────
 
def pg_login_type():
    st.markdown(_base_css(), unsafe_allow_html=True)
 
    # Role-specific CTA colours
    st.markdown("""
    <style>
    .btn-citizen  .stButton > button { background: linear-gradient(135deg,#6366F1,#8B5CF6) !important; border:none!important; color:#fff!important; font-size:13.5px!important; }
    .btn-official .stButton > button { background: linear-gradient(135deg,#0EA5E9,#6366F1) !important; border:none!important; color:#fff!important; font-size:13.5px!important; }
    .btn-admin    .stButton > button { background: linear-gradient(135deg,#E8660A,#EF4444) !important; border:none!important; color:#fff!important; font-size:13.5px!important; }
    </style>
    """, unsafe_allow_html=True)
 
    st.markdown(_topbar(), unsafe_allow_html=True)
 
    # Page header
    st.markdown("""
    <div style="text-align:center;margin-bottom:32px;">
        <div style="font-family:'Sora',sans-serif;font-size:26px;font-weight:700;color:#111827;letter-spacing:-0.5px;margin-bottom:8px;">
            Choose your role
        </div>
        <div style="font-size:14px;color:#6B7280;font-weight:300;">
            Select how you'd like to access the Jan Seva Portal
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    r1, r2, r3 = st.columns(3, gap="medium")
 
    with r1:
        st.markdown(_role_tile(
            "citizen", "👤", "Citizen",
            "File complaints, track status, access government schemes",
            "linear-gradient(90deg,#6366F1,#8B5CF6)"
        ), unsafe_allow_html=True)
        st.markdown('<div class="btn-citizen">', unsafe_allow_html=True)
        if st.button("Continue as Citizen", key="citizen_role_btn", use_container_width=True):
            st.session_state.screen = "user_login"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
 
    with r2:
        st.markdown(_role_tile(
            "official", "🏢", "Official",
            "Manage & resolve complaints for your department",
            "linear-gradient(90deg,#0EA5E9,#6366F1)"
        ), unsafe_allow_html=True)
        st.markdown('<div class="btn-official">', unsafe_allow_html=True)
        if st.button("Continue as Official", key="official_role_btn", use_container_width=True):
            st.session_state.screen = "official_login"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
 
    with r3:
        st.markdown(_role_tile(
            "admin", "👑", "Admin",
            "System management, analytics & oversight",
            "linear-gradient(90deg,#E8660A,#EF4444)"
        ), unsafe_allow_html=True)
        st.markdown('<div class="btn-admin">', unsafe_allow_html=True)
        if st.button("Continue as Admin", key="admin_role_btn", use_container_width=True):
            st.session_state.screen = "admin_login"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
 
    st.markdown("<br>", unsafe_allow_html=True)
    _, bc, _ = st.columns([1, 2, 1])
    with bc:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Change Language", key="lt_lang", use_container_width=True):
            st.session_state.screen = "language"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
 
    st.markdown(_footer(), unsafe_allow_html=True)
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  pg_user_login  — Citizen OTP login
# ─────────────────────────────────────────────────────────────────────────────
 
def pg_user_login():
    st.markdown(_base_css(), unsafe_allow_html=True)
    st.markdown(_login_css(accent="#6366F1", accent2="#8B5CF6"), unsafe_allow_html=True)
 
    # Additional: colour the primary CTA inside form
    st.markdown("""
    <style>
    .primary-btn .stButton > button {
        background: linear-gradient(135deg,#6366F1,#8B5CF6) !important;
        border: none !important; color: #fff !important;
        box-shadow: 0 2px 10px rgba(99,102,241,0.30) !important;
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)
 
    for k, v in [("otp_sent", False), ("login_phone", ""), ("demo_otp", "")]:
        if k not in st.session_state:
            st.session_state[k] = v
 
    st.markdown(_topbar(), unsafe_allow_html=True)
    st.markdown(_hero(
        "👤", "Welcome back",
        "File complaints · track status · access schemes",
        "linear-gradient(135deg,#1e1b4b 0%,#4338CA 50%,#0c4a6e 100%)"
    ), unsafe_allow_html=True)
 
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
 
    # ── SIGN IN ──────────────────────────────────────────────────────────────
    with tab1:
        st.markdown(_card_open("Phone Verification"), unsafe_allow_html=True)
 
        if not st.session_state.otp_sent:
            phone = st.text_input("Mobile number", placeholder="Enter your 10-digit number", key="login_phone_input")
            st.markdown('<p style="font-size:11.5px;color:#9CA3AF;margin-top:-6px;font-weight:300;">We\'ll send a one-time password to verify your number.</p>', unsafe_allow_html=True)
            st.markdown(_divider(), unsafe_allow_html=True)
 
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Send OTP →", key="send_otp_btn", use_container_width=True):
                p = phone.strip()
                if not p:
                    st.error("Please enter your phone number.")
                elif len(p) != 10 or not p.isdigit():
                    st.error("Enter a valid 10-digit number (digits only).")
                else:
                    with st.spinner("Sending OTP…"):
                        resp = api("post", "/auth/user/send-otp", json={"phone": p})
                    if resp.get("success"):
                        st.session_state.otp_sent    = True
                        st.session_state.login_phone = p
                        st.session_state.demo_otp    = resp.get("otp", "123456")
                        st.rerun()
                    else:
                        st.error(resp.get("detail", "Failed to send OTP. Try again."))
            st.markdown("</div>", unsafe_allow_html=True)
 
        else:
            st.markdown(_otp_badge(st.session_state.login_phone, st.session_state.demo_otp), unsafe_allow_html=True)
            otp = st.text_input("Enter OTP", placeholder="6-digit code", key="temp_otp", type="password")
            st.markdown(_divider(), unsafe_allow_html=True)
 
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Verify & Sign In →", key="verify_otp_btn", use_container_width=True):
                if not otp:
                    st.error("Please enter the OTP.")
                else:
                    with st.spinner("Verifying…"):
                        resp = api("post", "/auth/user/verify-otp",
                                   json={"phone": st.session_state.login_phone, "otp": otp})
                    if resp.get("success"):
                        st.session_state.user     = resp
                        st.session_state.role     = "user"
                        st.session_state.otp_sent = False
                        st.session_state.demo_otp = ""
                        st.session_state.screen   = "user_dashboard"
                        st.rerun()
                    else:
                        st.error(resp.get("detail", "Invalid OTP. Please try again."))
            st.markdown("</div>", unsafe_allow_html=True)
 
            st.markdown(_divider(), unsafe_allow_html=True)
            ra, rb = st.columns(2)
            with ra:
                if st.button("🔄 Resend OTP", key="resend_otp_btn", use_container_width=True):
                    with st.spinner("Resending…"):
                        resp = api("post", "/auth/user/send-otp", json={"phone": st.session_state.login_phone})
                    if resp.get("success"):
                        st.session_state.demo_otp = resp.get("otp", "123456")
                        st.success("New OTP sent!")
                        st.rerun()
                    else:
                        st.error("Failed to resend OTP.")
            with rb:
                st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
                if st.button("← Change number", key="cancel_otp_btn", use_container_width=True):
                    st.session_state.otp_sent = False
                    st.session_state.demo_otp = ""
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
 
        st.markdown(_card_close(), unsafe_allow_html=True)
 
    # ── CREATE ACCOUNT ───────────────────────────────────────────────────────
    with tab2:
        st.markdown(_card_open("Create your account"), unsafe_allow_html=True)
        with st.form(key="register_form", clear_on_submit=True):
            r_name    = st.text_input("Full name *",    placeholder="Your full name",        key="reg_name")
            r_phone   = st.text_input("Phone number *", placeholder="10-digit number",       key="reg_phone")
            r_address = st.text_area("Address *",       placeholder="Your complete address", key="reg_address", height=85)
            submitted = st.form_submit_button("Create Account →", use_container_width=True)
 
        if submitted:
            if not r_name:
                st.error("Please enter your full name.")
            elif not r_phone or len(r_phone.strip()) != 10 or not r_phone.strip().isdigit():
                st.error("Enter a valid 10-digit phone number.")
            elif not r_address:
                st.error("Please enter your address.")
            else:
                with st.spinner("Creating account…"):
                    resp = api("post", "/auth/user/signup", json={
                        "name":     r_name,
                        "phone":    r_phone.strip(),
                        "address":  r_address,
                        "language": st.session_state.get("language", "en"),
                    })
                if resp.get("success"):
                    st.success("✅ Account created! Switch to Sign In to continue.")
                    st.balloons()
                else:
                    em = resp.get("detail", "Registration failed.")
                    st.error(
                        "❌ Phone already registered — please sign in."
                        if "already" in em.lower() else f"❌ {em}"
                    )
        st.markdown(_card_close(), unsafe_allow_html=True)
 
    st.markdown(_divider(), unsafe_allow_html=True)
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("← Back to role selection", key="back_to_role", use_container_width=True):
        st.session_state.otp_sent = False
        st.session_state.demo_otp = ""
        st.session_state.screen   = "login_type"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(_footer("By continuing you agree to our Terms of Service"), unsafe_allow_html=True)
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  pg_official_login  — Official login + request access
# ─────────────────────────────────────────────────────────────────────────────
 
def pg_official_login():
    st.markdown(_base_css(), unsafe_allow_html=True)
    st.markdown(_login_css(accent="#0EA5E9", accent2="#6366F1"), unsafe_allow_html=True)
    st.markdown("""
    <style>
    .primary-btn .stButton > button {
        background: linear-gradient(135deg,#0EA5E9,#6366F1) !important;
        border:none!important; color:#fff!important;
        box-shadow: 0 2px 10px rgba(14,165,233,0.30) !important;
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)
 
    for k, v in [
        ("off_active_tab", "login"), ("off_step", 1), ("off_data", {}),
        ("off_otp_verified", False), ("forgot_step", 1), ("forgot_email", ""),
        ("forgot_otp_verified", False), ("show_forgot", False),
    ]:
        if k not in st.session_state:
            st.session_state[k] = v
 
    st.markdown(_topbar(), unsafe_allow_html=True)
    st.markdown(_hero(
        "🏢", "Official Portal",
        "Department management & complaint resolution",
        "linear-gradient(135deg,#0c1a3a 0%,#0369a1 50%,#1e1b4b 100%)"
    ), unsafe_allow_html=True)
 
    # Custom pill tabs
    st.markdown("""
    <style>
    .pill-tab-active .stButton > button {
        background: #0EA5E9 !important; color: #fff !important;
        border: none !important; font-weight: 500 !important;
        box-shadow: 0 2px 8px rgba(14,165,233,0.30) !important;
    }
    .pill-tab-idle .stButton > button {
        background: #F3F4F6 !important; color: #6B7280 !important;
        border: 1.5px solid #E5E7EB !important; font-weight: 400 !important;
    }
    </style>
    """, unsafe_allow_html=True)
 
    tc1, tc2 = st.columns(2, gap="small")
    with tc1:
        cls = "pill-tab-active" if st.session_state.off_active_tab == "login" else "pill-tab-idle"
        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
        if st.button("Sign In", key="tab_login_btn", use_container_width=True):
            st.session_state.off_active_tab = "login"
            st.session_state.show_forgot    = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with tc2:
        cls = "pill-tab-active" if st.session_state.off_active_tab == "request" else "pill-tab-idle"
        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
        if st.button("Request Access", key="tab_request_btn", use_container_width=True):
            st.session_state.off_active_tab = "request"
            st.session_state.show_forgot    = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
 
    st.markdown(_divider(), unsafe_allow_html=True)
 
    # ── SIGN IN / FORGOT ─────────────────────────────────────────────────────
    if st.session_state.off_active_tab == "login":
 
        if not st.session_state.show_forgot:
            st.markdown(_card_open("Official credentials"), unsafe_allow_html=True)
            with st.form(key="official_login_form", clear_on_submit=False):
                email    = st.text_input("Email address", placeholder="official@department.gov.in", key="official_email")
                password = st.text_input("Password",      placeholder="Your password", key="official_password", type="password")
                submitted = st.form_submit_button("Sign In →", use_container_width=True)
 
            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    with st.spinner("Signing in…"):
                        resp = api("post", "/auth/official/login", json={"email": email, "password": password})
                    if resp.get("success"):
                        st.session_state.official = resp
                        st.session_state.role     = "official"
                        st.session_state.screen   = "official_dashboard"
                        st.rerun()
                    else:
                        st.error(resp.get("detail", "Invalid email or password."))
 
            st.markdown(_divider(), unsafe_allow_html=True)
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Forgot password?", key="forgot_pwd_btn", use_container_width=True):
                st.session_state.show_forgot         = True
                st.session_state.forgot_step         = 1
                st.session_state.forgot_otp_verified = False
                st.session_state.forgot_email        = ""
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(_card_close(), unsafe_allow_html=True)
 
        else:
            # ── FORGOT PASSWORD ──────────────────────────────────────────────
            st.markdown(_card_open("Reset password"), unsafe_allow_html=True)
            step = st.session_state.forgot_step
 
            if step == 1:
                fe = st.text_input("Registered email address", key="forgot_email_input")
                st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                if st.button("Send Reset OTP →", key="send_reset_otp", use_container_width=True):
                    if not fe:
                        st.error("Please enter your email.")
                    elif "@" not in fe or "." not in fe.split("@")[-1]:
                        st.error("Enter a valid email address.")
                    else:
                        st.session_state.forgot_email = fe
                        st.session_state.forgot_step  = 2
                        st.success("Demo OTP sent — use **123456**")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
 
            elif step == 2:
                st.markdown(_info_box(f"Code sent to <strong>{st.session_state.forgot_email}</strong> — use <strong>123456</strong>", "📧"), unsafe_allow_html=True)
                otp = st.text_input("Enter OTP", type="password", placeholder="123456", key="reset_otp")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                    if st.button("Verify OTP →", use_container_width=True, key="verify_reset"):
                        if otp == "123456":
                            st.session_state.forgot_otp_verified = True
                            st.session_state.forgot_step         = 3
                            st.rerun()
                        else:
                            st.error("Invalid OTP — use 123456.")
                    st.markdown("</div>", unsafe_allow_html=True)
                with c2:
                    if st.button("Resend", use_container_width=True, key="resend_reset"):
                        st.info("OTP resent (still 123456).")
 
            else:
                st.markdown(_verified_box("Email verified — set your new password"), unsafe_allow_html=True)
                new_pwd     = st.text_input("New password",         type="password", key="new_pwd")
                confirm_pwd = st.text_input("Confirm new password", type="password", key="confirm_pwd")
                st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                if st.button("Reset Password →", use_container_width=True, key="do_reset"):
                    if not new_pwd or not confirm_pwd:
                        st.error("Please fill both fields.")
                    elif len(new_pwd) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif new_pwd != confirm_pwd:
                        st.error("Passwords do not match.")
                    else:
                        with st.spinner("Updating…"):
                            resp = api("post", "/auth/official/reset-password",
                                       json={"email": st.session_state.forgot_email, "new_password": new_pwd})
                        if resp.get("success"):
                            st.success("✅ Password reset! Please sign in.")
                            for key in ["show_forgot", "forgot_step", "forgot_email", "forgot_otp_verified"]:
                                st.session_state.pop(key, None)
                            st.rerun()
                        else:
                            st.error(f"Reset failed: {resp.get('detail','Unknown error')}")
                st.markdown("</div>", unsafe_allow_html=True)
 
            st.markdown(_divider(), unsafe_allow_html=True)
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("← Back to sign in", use_container_width=True, key="back_from_forgot"):
                for key in ["show_forgot", "forgot_step", "forgot_email", "forgot_otp_verified"]:
                    st.session_state.pop(key, None)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(_card_close(), unsafe_allow_html=True)
 
    # ── REQUEST ACCESS ────────────────────────────────────────────────────────
    else:
        st.markdown(_card_open(), unsafe_allow_html=True)
        step = st.session_state.off_step
        st.markdown(_step_indicator(step), unsafe_allow_html=True)
 
        if step == 1:
            st.markdown('<p style="font-size:10.5px;font-weight:600;color:#9CA3AF;letter-spacing:1.1px;text-transform:uppercase;margin-bottom:16px;">Your details</p>', unsafe_allow_html=True)
            d  = st.session_state.off_data
            nm = st.text_input("Full name *",               value=d.get("name", ""),      key="off_name")
            em = st.text_input("Email address *",           value=d.get("email", ""),     key="off_email")
            ph = st.text_input("Phone (10 digits) *",       value=d.get("phone", ""),     key="off_phone")
            pw = st.text_input("Password (min 6 chars) *",  value=d.get("password", ""),  key="off_pass",  type="password")
            dc = st.text_input("Department code *",         value=d.get("dept_code", ""), key="off_dept",
                               help="Get this from your department admin")
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Continue →", use_container_width=True, key="off_send_otp"):
                errs = [f for f, v in [("Name", nm), ("Email", em), ("Phone", ph), ("Password", pw), ("Dept Code", dc)] if not v]
                if errs:
                    st.error("Missing: " + ", ".join(errs))
                elif len(ph) != 10 or not ph.isdigit():
                    st.error("Phone must be exactly 10 digits.")
                elif len(pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    st.session_state.off_data = {"name": nm, "email": em, "phone": ph, "password": pw, "dept_code": dc}
                    st.session_state.off_step = 2
                    st.session_state.off_otp_verified = False
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
 
        else:
            masked = "×" * 6 + st.session_state.off_data.get("phone", "")[-4:]
            st.markdown(_info_box(f"OTP sent to <strong>{masked}</strong> — use demo code <strong>123456</strong>", "📱"), unsafe_allow_html=True)
 
            otp = st.text_input("OTP", type="password", placeholder="6-digit code",
                                key="off_otp_input", max_chars=6, label_visibility="collapsed")
 
            if st.session_state.off_otp_verified:
                st.markdown(_verified_box("Phone verified — ready to submit!"), unsafe_allow_html=True)
 
            oc1, oc2 = st.columns(2)
            with oc1:
                st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                if st.button("Verify OTP →", use_container_width=True, key="off_verify_otp"):
                    if otp and otp.strip() == "123456":
                        st.session_state.off_otp_verified = True
                        st.rerun()
                    else:
                        st.error("Invalid OTP — use 123456.")
                st.markdown("</div>", unsafe_allow_html=True)
            with oc2:
                if st.button("Resend", use_container_width=True, key="off_resend_otp"):
                    st.info("Demo OTP resent — still 123456.")
 
            st.markdown(_divider(), unsafe_allow_html=True)
 
            if st.session_state.off_otp_verified:
                st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                if st.button("Submit Request →", use_container_width=True, key="off_submit_request"):
                    with st.spinner("Submitting…"):
                        resp = api("post", "/auth/official/signup", json=st.session_state.off_data)
                    if resp.get("success"):
                        st.success("✅ Request submitted! Awaiting admin approval.")
                        for k in ("off_step", "off_data", "off_otp_verified"):
                            st.session_state.pop(k, None)
                        st.session_state.off_active_tab = "login"
                        st.balloons()
                        st.rerun()
                    else:
                        em2 = resp.get("detail", "Unknown error")
                        st.error("❌ Email already registered — try signing in." if "already" in em2.lower() else f"❌ {em2}")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(_warn_box("Verify your OTP above before submitting."), unsafe_allow_html=True)
 
            st.markdown(_divider(), unsafe_allow_html=True)
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("← Edit details", use_container_width=True, key="off_back_step1"):
                st.session_state.off_step         = 1
                st.session_state.off_otp_verified = False
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
 
        st.markdown(_card_close(), unsafe_allow_html=True)
 
    st.markdown(_divider(), unsafe_allow_html=True)
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("← Back to role selection", key="official_back", use_container_width=True):
        for k in ("off_step", "off_data", "off_otp_verified", "off_active_tab",
                  "show_forgot", "forgot_step", "forgot_email", "forgot_otp_verified"):
            st.session_state.pop(k, None)
        st.session_state.screen = "login_type"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(_footer(), unsafe_allow_html=True)
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  pg_admin_login  — Admin login
# ─────────────────────────────────────────────────────────────────────────────
 
def pg_admin_login():
    st.markdown(_base_css(), unsafe_allow_html=True)
    st.markdown(_login_css(accent="#E8660A", accent2="#EF4444"), unsafe_allow_html=True)
 
    st.markdown(_topbar(), unsafe_allow_html=True)
    st.markdown(_hero(
        "👑", "Admin Panel",
        "System administration · analytics · oversight",
        "linear-gradient(135deg,#3b1a00 0%,#78350f 50%,#1c1917 100%)"
    ), unsafe_allow_html=True)
 
    st.markdown(_card_open("Administrator credentials"), unsafe_allow_html=True)
 
    with st.form(key="admin_login_form", clear_on_submit=False):
        username  = st.text_input("Username", placeholder="Enter your username",  key="admin_username")
        password  = st.text_input("Password", placeholder="Enter your password",  key="admin_password", type="password")
        submitted = st.form_submit_button("Sign In to Admin Panel →", use_container_width=True)
 
    if submitted:
        if not username:
            st.error("Please enter your username.")
        elif not password:
            st.error("Please enter your password.")
        else:
            with st.spinner("Authenticating…"):
                resp = api("post", "/auth/admin/login", json={"username": username, "password": password})
            if resp.get("success"):
                st.session_state.admin  = resp
                st.session_state.role   = "admin"
                st.session_state.screen = "admin_dashboard"
                st.rerun()
            else:
                st.error(resp.get("detail", "Invalid username or password."))
 
    st.markdown("""
    <div style="
        background:#FFF7ED;
        border:1px solid #FED7AA;
        border-radius:10px;
        padding:14px 16px;
        margin-top:16px;
        font-size:13px;
        color:#92400E;
    ">
        <div style="font-weight:600;margin-bottom:4px;">Default credentials</div>
        <div style="font-weight:300;">Username: <strong>admin</strong> &nbsp;·&nbsp; Password: <strong>admin123</strong></div>
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown(_card_close(), unsafe_allow_html=True)
 
    st.markdown(_divider(), unsafe_allow_html=True)
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("← Back to role selection", key="admin_back", use_container_width=True):
        st.session_state.screen = "login_type"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(_footer(), unsafe_allow_html=True)

def api(method, path, **kwargs):

# ═════════════════════════════════════════════════════════════════════════════
# USER DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════

def _inline_voice_html(lang_code: str = "en-IN") -> str:
    """
    Self-contained voice recorder iframe.
    Posts result to parent via postMessage → parent writes it to query param
    → Streamlit reads it on next rerun via st.query_params.
    This lives in its OWN iframe scope so category button clicks, reruns, or
    any other Streamlit interaction CANNOT kill the recognizer.
    """
    tap_lbl      = "Tap to speak"                        if "en" in lang_code else "बोलने के लिए दबाएं"
    listen_lbl   = "🎙️ Listening…"                       if "en" in lang_code else "🎙️ सुन रहा हूँ…"
    done_lbl     = "✅ Done — click Use Text below"       if "en" in lang_code else "✅ हो गया!"
    nothing_lbl  = "❌ Nothing heard. Try again."         if "en" in lang_code else "❌ कुछ नहीं सुना।"
    use_lbl      = "✅  Use This Text"                    if "en" in lang_code else "✅  इस टेक्स्ट का उपयोग करें"
    live_lbl     = "Live Transcript"                     if "en" in lang_code else "लाइव ट्रांसक्रिप्ट"
 
    return f"""
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Segoe UI',sans-serif;background:transparent;}}
.vc{{background:linear-gradient(135deg,rgba(99,102,241,.09),rgba(139,92,246,.06));
    border:1px solid rgba(99,102,241,.20);border-radius:18px;padding:22px 18px;text-align:center;}}
.vc-hdr{{font-size:.62rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;
    color:#818CF8;margin-bottom:14px;display:flex;align-items:center;justify-content:center;gap:8px;}}
.vc-hdr::before,.vc-hdr::after{{content:'';flex:1;height:1px;background:rgba(99,102,241,.2);}}
#vbtn{{background:linear-gradient(135deg,#EC4899,#8B5CF6);color:#fff;border:none;
    border-radius:50%;width:66px;height:66px;font-size:1.75rem;cursor:pointer;
    display:inline-flex;align-items:center;justify-content:center;
    box-shadow:0 6px 22px rgba(139,92,246,.45);transition:all .18s;}}
#vbtn:hover{{transform:scale(1.08);}}
.wf{{display:none;align-items:center;justify-content:center;gap:4px;height:32px;margin:10px auto 0;width:140px;}}
.wb{{width:4px;background:#818CF8;border-radius:99px;animation:wv 1.1s ease-in-out infinite;}}
.wb:nth-child(1){{height:10px;animation-delay:0s;}}
.wb:nth-child(2){{height:18px;animation-delay:.1s;}}
.wb:nth-child(3){{height:28px;animation-delay:.2s;}}
.wb:nth-child(4){{height:20px;animation-delay:.3s;}}
.wb:nth-child(5){{height:32px;animation-delay:.4s;}}
.wb:nth-child(6){{height:22px;animation-delay:.5s;}}
.wb:nth-child(7){{height:14px;animation-delay:.6s;}}
@keyframes wv{{0%,100%{{transform:scaleY(.4);opacity:.5;}}50%{{transform:scaleY(1);opacity:1;}}}}
#vstatus{{font-size:.75rem;color:#8892AA;margin:10px 0 4px;font-weight:500;}}
.vt{{display:none;background:rgba(255,255,255,.05);border:1px solid rgba(99,102,241,.2);
    border-radius:12px;padding:12px 14px;margin-top:10px;text-align:left;}}
.vtlbl{{font-size:.60rem;font-weight:800;text-transform:uppercase;letter-spacing:.10em;
    color:#818CF8;margin-bottom:6px;display:flex;align-items:center;gap:6px;}}
.vdot{{width:7px;height:7px;border-radius:50%;background:#EC4899;
    animation:dp .9s infinite;flex-shrink:0;display:none;}}
@keyframes dp{{0%,100%{{opacity:1;transform:scale(1);}}50%{{opacity:.3;transform:scale(.6);}}}}
#vi{{color:rgba(240,242,255,.35);font-style:italic;font-size:.80rem;min-height:16px;line-height:1.55;}}
#vf{{font-weight:600;color:#F0F2FF;font-size:.84rem;line-height:1.6;margin-top:4px;}}
#vub{{display:none;margin-top:10px;width:100%;
    background:linear-gradient(135deg,#6366F1,#818CF8);color:#fff;border:none;
    border-radius:10px;padding:10px;font-size:.80rem;font-weight:800;cursor:pointer;
    box-shadow:0 4px 16px rgba(99,102,241,.38);transition:all .15s;
    font-family:'Segoe UI',sans-serif;}}
#vub:hover{{transform:translateY(-2px);box-shadow:0 8px 26px rgba(99,102,241,.50);}}
@keyframes mp{{0%{{box-shadow:0 0 0 0 rgba(236,72,153,.65);}}
    70%{{box-shadow:0 0 0 20px rgba(236,72,153,0);}}100%{{box-shadow:0 0 0 0 rgba(236,72,153,0);}}}}
.rec{{animation:mp 1.1s ease-in-out infinite!important;}}
</style>
<div class="vc">
<div class="vc-hdr">🎤 Voice Input</div>
<button id="vbtn" onclick="toggleV()">🎤</button>
<div class="wf" id="wf">
    <div class="wb"></div><div class="wb"></div><div class="wb"></div>
    <div class="wb"></div><div class="wb"></div><div class="wb"></div><div class="wb"></div>
</div>
<div id="vstatus">{tap_lbl}</div>
<div class="vt" id="vt">
    <div class="vtlbl"><span class="vdot" id="vdot"></span>📝 {live_lbl}</div>
    <div id="vi"></div>
    <div id="vf"></div>
    <button id="vub" onclick="sendUp()">{use_lbl}</button>
</div>
</div>
<script>
var cap='', rec=null, running=false;
function toggleV(){{ running?stopV():startV(); }}
function startV(){{
    var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    if(!SR){{ setSt('❌ Browser does not support speech recognition','#EF4444'); return; }}
    cap='';
    document.getElementById('vf').textContent='';
    document.getElementById('vi').textContent='';
    document.getElementById('vub').style.display='none';
    rec=new SR(); rec.lang='{lang_code}'; rec.continuous=true; rec.interimResults=true;
    rec.onresult=function(e){{
        var it='',ft='';
        for(var i=0;i<e.results.length;i++){{
            if(e.results[i].isFinal) ft+=e.results[i][0].transcript+' ';
            else it+=e.results[i][0].transcript;
        }}
        document.getElementById('vi').textContent=it;
        document.getElementById('vf').textContent=ft;
        cap=(ft+it).trim();
    }};
    rec.onerror=function(e){{ setSt('❌ '+e.error,'#EF4444'); setIdle(); }};
    rec.onend=function(){{
        /* KEY FIX: auto-restart to keep continuous across silence gaps */
        if(running){{ try{{rec.start();}}catch(e){{setIdle();}} return; }}
        setIdle();
        if(cap){{ document.getElementById('vub').style.display='block'; setSt('{done_lbl}','#10B981'); }}
        else{{ document.getElementById('vt').style.display='none'; setSt('{nothing_lbl}','#EF4444'); }}
    }};
    try{{ rec.start(); }}catch(e){{ setSt('❌ Could not start mic','#EF4444'); return; }}
    running=true;
    var btn=document.getElementById('vbtn');
    btn.textContent='⏹️'; btn.classList.add('rec');
    document.getElementById('wf').style.display='flex';
    document.getElementById('vt').style.display='block';
    document.getElementById('vdot').style.display='inline-block';
    setSt('{listen_lbl}','#F59E0B');
}}
function stopV(){{ running=false; if(rec)try{{rec.stop();}}catch(e){{}} }}
function setIdle(){{
    running=false;
    var btn=document.getElementById('vbtn');
    btn.textContent='🎤'; btn.classList.remove('rec');
    document.getElementById('wf').style.display='none';
    document.getElementById('vdot').style.display='none';
}}
function setSt(t,c){{ var e=document.getElementById('vstatus'); e.textContent=t; e.style.color=c||''; }}
/* Send captured text to parent via postMessage.
   Parent listens → writes to URL query param → Streamlit reads it on rerun.
   This keeps voice completely isolated from Streamlit reruns. */
function sendUp(){{
    if(!cap) return;
    window.parent.postMessage({{type:'VOICE_RESULT',text:cap}},'*');
    setSt('✅ Sent to description!','#10B981');
    document.getElementById('vub').style.display='none';
}}
</script>
"""
# ── Module-level imports (never re-imported on rerun) ──────────────────────
import html as _html
import re
from datetime import datetime
from functools import lru_cache

# ── Pre-compiled regex (compiled once, reused on every call) ───────────────
_CLEAN_RE  = re.compile(r"silkr\.flask=\('[^']+'\)|silkr|[\"\']", re.I)
_SPACE_RE  = re.compile(r"\s+")

PAGE_SIZE  = 10   # complaints visible per page


# ═══════════════════════════════════════════════════════════════════════════
# CSS  ── injected once per session, never again
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def _voice_html(lang_code: str) -> str:
    """
    Full self-contained voice recorder iframe (proper HTML document).
    Features:
     - Live interim transcript shown while speaking
     - Final transcript highlighted in green
     - Waveform animation while recording
     - ✅ Use This Text  →  postMessage to parent bridge
     - 🔄 Record Again  →  resets state, starts fresh (no page reload)
    Bridge (separate iframe below) catches postMessage and writes URL param → 1 rerun.
    """
    path = os.path.join(os.path.dirname(__file__), "components", "voice_component.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().replace("%LANG%", lang_code)
 
    is_hi = "hi" in lang_code
    tap   = "बोलने के लिए दबाएं"     if is_hi else "Tap mic to speak"
    lst   = "🎙️ सुन रहा हूँ…"        if is_hi else "🎙️ Listening…"
    dn    = "✅ हो गया! नीचे दबाएं"  if is_hi else "✅ Done! Use text below"
    nth   = "❌ कुछ नहीं सुना"        if is_hi else "❌ Nothing heard. Try again"
    use   = "✅ इस टेक्स्ट का उपयोग करें" if is_hi else "✅  Use This Text"
    again = "🔄 दोबारा बोलें"         if is_hi else "🔄  Record Again"
    lv    = "लाइव ट्रांसक्रिप्ट"      if is_hi else "Live Transcript"
    lv_ph = "आप जो बोलेंगे वह यहाँ दिखेगा…" if is_hi else "What you speak will appear here…"
 
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'DM Sans','Segoe UI',system-ui,sans-serif;background:transparent;}}
 
/* ── outer card ── */
.vc{{
    background:linear-gradient(135deg,rgba(99,102,241,.07),rgba(139,92,246,.04));
    border:1.5px solid rgba(99,102,241,.18);
    border-radius:20px;padding:18px 16px 14px;text-align:center;
}}
.vc-hdr{{
    font-size:.58rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;
    color:#818CF8;margin-bottom:14px;
    display:flex;align-items:center;justify-content:center;gap:8px;
}}
.vc-hdr::before,.vc-hdr::after{{content:'';flex:1;height:1px;background:rgba(99,102,241,.20);}}
 
/* ── mic button ── */
#vbtn{{
    background:linear-gradient(135deg,#EC4899,#8B5CF6);color:#fff;border:none;
    border-radius:50%;width:68px;height:68px;font-size:1.75rem;cursor:pointer;
    display:inline-flex;align-items:center;justify-content:center;
    box-shadow:0 6px 24px rgba(139,92,246,.50);transition:all .18s;
}}
#vbtn:hover{{transform:scale(1.08);box-shadow:0 10px 32px rgba(139,92,246,.60);}}
@keyframes mp{{0%{{box-shadow:0 0 0 0 rgba(236,72,153,.70);}}
    70%{{box-shadow:0 0 0 22px rgba(236,72,153,0);}}100%{{box-shadow:0 0 0 0 rgba(236,72,153,0);}}}}
.rec{{animation:mp 1.1s ease-in-out infinite!important;}}
 
/* ── waveform ── */
.wf{{
    display:none;align-items:center;justify-content:center;
    gap:3px;height:28px;margin:10px auto 0;
}}
.wb{{width:3px;background:#818CF8;border-radius:99px;animation:wv 1.1s ease-in-out infinite;}}
.wb:nth-child(1){{height:8px;animation-delay:0s;}}
.wb:nth-child(2){{height:14px;animation-delay:.10s;}}
.wb:nth-child(3){{height:24px;animation-delay:.20s;}}
.wb:nth-child(4){{height:17px;animation-delay:.30s;}}
.wb:nth-child(5){{height:28px;animation-delay:.40s;}}
.wb:nth-child(6){{height:17px;animation-delay:.50s;}}
.wb:nth-child(7){{height:9px;animation-delay:.60s;}}
@keyframes wv{{0%,100%{{transform:scaleY(.3);opacity:.4;}}50%{{transform:scaleY(1);opacity:1;}}}}
 
/* ── status line ── */
#vstatus{{font-size:.74rem;color:#8892AA;margin:10px 0 0;font-weight:500;min-height:18px;}}
 
/* ── transcript box ── */
.vt{{
    display:none;
    background:rgba(255,255,255,.06);
    border:1px solid rgba(99,102,241,.20);
    border-radius:14px;padding:12px 14px;margin-top:10px;text-align:left;
}}
.vtlbl{{
    font-size:.56rem;font-weight:800;text-transform:uppercase;letter-spacing:.10em;
    color:#818CF8;margin-bottom:7px;display:flex;align-items:center;gap:6px;
}}
.vdot{{
    width:7px;height:7px;border-radius:50%;background:#EC4899;
    animation:dp .9s infinite;flex-shrink:0;display:none;
}}
@keyframes dp{{0%,100%{{opacity:1;transform:scale(1);}}50%{{opacity:.3;transform:scale(.55);}}}}
 
/* interim text — grey italic (what's being processed) */
#vi{{
    color:rgba(180,190,255,.50);font-style:italic;
    font-size:.78rem;min-height:16px;line-height:1.6;
    word-break:break-word;
}}
/* final text — bright bold (confirmed words) */
#vf{{
    font-weight:700;color:#A5B4FC;
    font-size:.85rem;line-height:1.65;margin-top:5px;
    word-break:break-word;
    min-height:18px;
}}
/* placeholder shown before any speech */
.vph{{
    font-size:.76rem;color:rgba(180,190,255,.30);
    font-style:italic;padding:4px 0;
}}
 
/* ── action buttons row ── */
.vactions{{
    display:none;flex-direction:column;gap:7px;margin-top:12px;
}}
#vub{{
    width:100%;background:linear-gradient(135deg,#6366F1,#818CF8);color:#fff;
    border:none;border-radius:10px;padding:10px 0;
    font-size:.78rem;font-weight:800;cursor:pointer;
    box-shadow:0 4px 16px rgba(99,102,241,.40);
    transition:all .15s;font-family:'DM Sans','Segoe UI',sans-serif;
    letter-spacing:.01em;
}}
#vub:hover{{transform:translateY(-2px);box-shadow:0 8px 28px rgba(99,102,241,.55);}}
#vagain{{
    width:100%;background:rgba(99,102,241,.12);color:#818CF8;
    border:1.5px solid rgba(99,102,241,.28);
    border-radius:10px;padding:8px 0;
    font-size:.76rem;font-weight:700;cursor:pointer;
    transition:all .15s;font-family:'DM Sans','Segoe UI',sans-serif;
}}
#vagain:hover{{background:rgba(99,102,241,.22);transform:translateY(-1px);}}
</style></head>
<body>
<div class="vc">
  <div class="vc-hdr">🎤 Voice Input</div>
  <button id="vbtn" onclick="toggleV()">🎤</button>
  <div class="wf" id="wf">
    <div class="wb"></div><div class="wb"></div><div class="wb"></div>
    <div class="wb"></div><div class="wb"></div><div class="wb"></div><div class="wb"></div>
  </div>
  <div id="vstatus">{tap}</div>
  <div class="vt" id="vt">
    <div class="vtlbl">
      <span class="vdot" id="vdot"></span>📝 {lv}
    </div>
    <div id="vi"><span class="vph">{lv_ph}</span></div>
    <div id="vf"></div>
  </div>
  <div class="vactions" id="vactions">
    <button id="vub"    onclick="sendUp()">{use}</button>
    <button id="vagain" onclick="doAgain()">{again}</button>
  </div>
</div>
 
<script>
var cap='', rec=null, running=false;
 
function toggleV(){{ running ? stopV() : startV(); }}
 
function startV(){{
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!SR){{ setSt('❌ Use Chrome or Edge for voice input','#EF4444'); return; }}
 
    // reset display
    cap = '';
    setEl('vi', '<span class="vph">{lv_ph}</span>');
    setEl('vf', '');
    show('vactions', 'none');
    show('vt', 'block');
 
    rec = new SR();
    rec.lang           = '{lang_code}';
    rec.continuous     = true;
    rec.interimResults = true;
 
    rec.onresult = function(e){{
        var interim='', finalT='';
        for(var i=0; i<e.results.length; i++){{
            if(e.results[i].isFinal) finalT += e.results[i][0].transcript + ' ';
            else interim += e.results[i][0].transcript;
        }}
        // Update live transcript — interim grey, final bright
        document.getElementById('vi').textContent = interim;
        document.getElementById('vf').textContent = finalT.trim();
        cap = (finalT + interim).trim();
    }};
 
    rec.onerror = function(e){{
        setSt('❌ ' + e.error, '#EF4444');
        setIdle();
    }};
 
    rec.onend = function(){{
        // keep continuous recording across silence gaps
        if(running){{ try{{ rec.start(); }}catch(ex){{ setIdle(); }} return; }}
        setIdle();
        if(cap){{
            document.getElementById('vdot').style.display = 'none';
            show('vactions', 'flex');
            setSt('{dn}', '#10B981');
        }} else {{
            show('vt', 'none');
            setSt('{nth}', '#EF4444');
        }}
    }};
 
    try{{ rec.start(); }}
    catch(e){{ setSt('❌ Could not start microphone', '#EF4444'); return; }}
 
    running = true;
    var btn = document.getElementById('vbtn');
    btn.textContent = '⏹️';
    btn.classList.add('rec');
    show('wf', 'flex');
    document.getElementById('vdot').style.display = 'inline-block';
    setSt('{lst}', '#F59E0B');
}}
 
function stopV(){{
    running = false;
    if(rec) try{{ rec.stop(); }}catch(e){{}}
}}
 
function setIdle(){{
    running = false;
    var btn = document.getElementById('vbtn');
    btn.textContent = '🎤';
    btn.classList.remove('rec');
    show('wf', 'none');
    document.getElementById('vdot').style.display = 'none';
}}
 
function doAgain(){{
    // reset everything and start fresh recording
    cap = '';
    setEl('vi', '<span class="vph">{lv_ph}</span>');
    setEl('vf', '');
    show('vactions', 'none');
    show('vt', 'none');
    setSt('{tap}', '#8892AA');
    startV();
}}
 
function sendUp(){{
    if(!cap) return;
    window.parent.postMessage({{type:'VOICE_RESULT', text:cap}}, '*');
    setSt('✅ Sent to form!', '#10B981');
    show('vactions', 'none');
}}
 
// helpers
function setEl(id, html){{ document.getElementById(id).innerHTML = html; }}
function show(id, val){{ document.getElementById(id).style.display = val; }}
function setSt(t, c){{ var e=document.getElementById('vstatus'); e.textContent=t; e.style.color=c||''; }}
</script>
</body></html>"""

 
@st.cache_data(show_spinner=False)
def _bridge_html() -> str:
    """
    Zero-height postMessage bridge — must be a full HTML document.
    Listens for VOICE_RESULT from voice iframe, writes to URL param → 1 rerun.
    Guard flag prevents duplicate writes.
    """
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body><script>
(function(){
  if(window._voiceBridgeInstalled) return;
  window._voiceBridgeInstalled = true;
  window.addEventListener('message', function(ev){
    if(!ev.data || ev.data.type !== 'VOICE_RESULT') return;
    var text = (ev.data.text || '').trim();
    if(!text) return;
    var u = new URL(window.parent.location.href);
    u.searchParams.set('voice_text', encodeURIComponent(text));
    window.parent.history.pushState({}, '', u);
    window.parent.dispatchEvent(new PopStateEvent('popstate', {state:{}}));
  });
})();
</script></body></html>"""


@st.cache_data(show_spinner=False)
def _gps_html(label: str) -> str:
    return f"""<style>
#gpsbtn{{background:linear-gradient(135deg,#06b6d4,#6366F1);color:#fff;border:none;
    border-radius:13px;width:100%;height:49px;font-size:.78rem;font-weight:700;
    cursor:pointer;font-family:sans-serif;box-shadow:0 4px 14px rgba(6,182,212,.30);transition:transform .18s;}}
#gpsbtn:hover{{transform:translateY(-2px);}}
#gpsst{{font-size:.62rem;text-align:center;margin-top:5px;color:#64748B;font-family:sans-serif;min-height:14px;}}
</style>
<button id="gpsbtn" onclick="doGPS()">📍 GPS</button>
<div id="gpsst">{label}</div>
<script>
function doGPS(){{
  var s=document.getElementById('gpsst');s.textContent='⏳ Fetching…';s.style.color='#d97706';
  if(!navigator.geolocation){{s.textContent='❌ Not supported';s.style.color='#dc2626';return;}}
  navigator.geolocation.getCurrentPosition(
    function(p){{s.textContent='✅ Got it!';s.style.color='#10b981';
      var u=new URL(window.parent.location.href);
      u.searchParams.set('gps_lat',p.coords.latitude);u.searchParams.set('gps_lon',p.coords.longitude);
      window.parent.history.pushState({{}},'',u);
      window.parent.dispatchEvent(new PopStateEvent('popstate',{{state:{{}}}}));}},
    function(e){{s.textContent='❌ '+e.message;s.style.color='#dc2626';}},
    {{timeout:10000,enableHighAccuracy:true}});
}}
</script>"""
 
 
def _map_html(lat: float, lon: float, dark: bool) -> str:
    bc = "#1E2A3D" if dark else "#E2E8F4"
    return (
        "<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/>"
        "<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>"
        f"<div id='cmap' style='height:218px;border-radius:16px;overflow:hidden;"
        f"border:1.5px solid {bc};box-shadow:0 4px 18px rgba(15,23,42,.08);margin-top:8px;'></div>"
        "<script>(function(){"
        "if(window._cmapI){window._cmapI.remove();}"
        f"var m=L.map('cmap',{{zoomControl:true,attributionControl:false}}).setView([{lat},{lon}],15);"
        "window._cmapI=m;"
        "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',"
        "{maxZoom:19,subdomains:['a','b','c']}).addTo(m);"
        "var ic=L.divIcon({className:'',"
        "html:'<div style=\"position:relative;width:32px;height:40px;\">"
        "<div style=\"width:32px;height:32px;background:linear-gradient(135deg,#6366F1,#8B5CF6);"
        "border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:2.5px solid #fff;"
        "box-shadow:0 3px 14px rgba(99,102,241,.50);\"></div>"
        "<div style=\"position:absolute;top:6px;left:6px;font-size:13px;transform:rotate(45deg);\">📍</div>"
        "</div>',"
        "iconSize:[32,40],iconAnchor:[16,40]});"
        f"L.marker([{lat},{lon}],{{icon:ic}}).addTo(m).bindPopup('<b>📍 Your Location</b>').openPopup();"
        "})();</script>"
    )

def _dashboard_render_hero(user: dict, comps: list, lang: str) -> None:
    hour       = datetime.now().hour
    greet_map  = [(12,"Good Morning","सुप्रभात","☀️"),
                  (17,"Good Afternoon","नमस्कार","👋"),
                  (24,"Good Evening","शुभ संध्या","🌙")]
    greet, emoji = next(
        ((_t(lang, g, h), e) for lim, g, h, e in greet_map if hour < lim),
        (_t(lang,"Good Evening","शुभ संध्या"), "🌙")
    )
    user_name = user.get("name", "User").split()[0]
    initials  = "".join(p[0].upper() for p in user.get("name", "U U").split()[:2])
    total     = len(comps)
    active    = sum(1 for c in comps if c.get("status") in ("pending", "in_progress"))
    resolved  = sum(1 for c in comps if c.get("status") in ("resolved", "closed"))
    pending   = sum(1 for c in comps if c.get("status") == "pending")

    st.markdown(
        f'<div class="prem-hero">'
        f'<div class="prem-hero-avatar">{initials}</div>'
        f'<div class="prem-hero-title">{emoji} {greet}, {_html.escape(user_name)}!</div>'
        f'<div class="prem-hero-sub">{_t(lang,"Welcome to your complaint dashboard","आपकी सेवा में तत्पर हैं")}</div>'
        f'<div class="prem-hero-stats">'
        f'<div class="prem-hstat h-blue"><div class="prem-hstat-num">{total}</div>'
        f'<div class="prem-hstat-lbl">📋 {_t(lang,"Total","कुल")}</div></div>'
        f'<div class="prem-hstat h-amber"><div class="prem-hstat-num">{active}</div>'
        f'<div class="prem-hstat-lbl">🔄 {_t(lang,"Active","सक्रिय")}</div></div>'
        f'<div class="prem-hstat h-green"><div class="prem-hstat-num">{resolved}</div>'
        f'<div class="prem-hstat-lbl">✅ {_t(lang,"Resolved","समाधान")}</div></div>'
        f'<div class="prem-hstat h-red"><div class="prem-hstat-num">{pending}</div>'
        f'<div class="prem-hstat-lbl">⏳ {_t(lang,"Pending","लंबित")}</div></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

def _inject_css_once(dark: bool) -> None:
    """Inject dashboard CSS into the Streamlit page exactly once per session."""
    flag = f"_dash_css_{dark}"
    if st.session_state.get(flag):
        return

    _CARD = "#10161F" if dark else "#FFFFFF"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"

    # Semantic badge classes replace per-card inline style strings
    st.markdown(f"""
<style>
/* ── Quick-action overlay ── */
.qa-wrap{{position:relative;}}
.qa-wrap .stButton{{position:absolute;inset:0;opacity:0;z-index:2;}}
.qa-wrap .stButton>button{{width:100%!important;height:100%!important;
  min-height:100%!important;background:transparent!important;
  border:none!important;box-shadow:none!important;}}

/* ── Filter chip strip ── */
.dash-chips{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:4px;padding:4px 0;}}
.dash-chip{{padding:7px 16px;border-radius:30px;font-size:.76rem;font-weight:700;
  border:1.5px solid {_BOR};background:{_CARD};color:{_SUB};
  white-space:nowrap;pointer-events:none;transition:all .18s;}}
.dash-chip.active{{background:linear-gradient(135deg,#6366F1,#8B5CF6);
  color:#fff;border-color:transparent;
  box-shadow:0 4px 14px rgba(99,102,241,.30);}}

/* ── Notification inline bar ── */
.notif-inline{{background:{"#1C1408" if dark else "#FFFBEB"};
  border:1.5px solid {"#78350F" if dark else "#FDE68A"};
  border-radius:14px;padding:12px 16px;
  display:flex;align-items:center;gap:10px;margin:12px 0;}}
.ni-dot{{width:9px;height:9px;border-radius:50%;background:#F59E0B;flex-shrink:0;
  box-shadow:0 0 0 3px rgba(245,158,11,.20);}}
.ni-text{{font-size:.80rem;color:{"#FCD34D" if dark else "#B45309"};
  font-weight:600;flex:1;}}
.ni-badge{{background:#F59E0B;color:#fff;border-radius:20px;
  padding:2px 10px;font-size:.66rem;font-weight:800;flex-shrink:0;}}

/* ── Feedback card ── */
.fb-card{{background:{_CARD};
  border:1.5px solid {"#14532D" if dark else "#BBF7D0"};
  border-radius:18px;padding:18px 20px;margin:8px 0;
  box-shadow:0 0 0 4px {"#0A2218" if dark else "#F0FDF4"};}}
.fb-head{{display:flex;align-items:center;gap:12px;margin-bottom:10px;}}
.fb-icon{{width:42px;height:42px;border-radius:13px;
  background:{"#0A2218" if dark else "#DCFCE7"};
  border:1px solid {"#14532D" if dark else "#BBF7D0"};
  display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;}}
.fb-title{{font-weight:800;font-size:.92rem;color:{_TXT};}}
.fb-sub{{font-size:.74rem;color:{_SUB};margin-top:2px;}}
.fb-desc{{font-size:.80rem;color:{_SUB};line-height:1.65;}}

/* ── Rating card ── */
.rt-card{{background:{_CARD};
  border:1.5px solid {"#1E3A5F" if dark else "#BFDBFE"};
  border-radius:18px;padding:18px 20px;margin:8px 0;
  box-shadow:0 0 0 4px {"#080F1C" if dark else "#EFF6FF"};}}
.rt-head{{display:flex;align-items:center;gap:12px;margin-bottom:10px;}}
.rt-icon{{width:42px;height:42px;border-radius:13px;
  background:{"#080F1C" if dark else "#EFF6FF"};
  border:1px solid {"#1E3A5F" if dark else "#BFDBFE"};
  display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;}}
.rt-title{{font-weight:800;font-size:.92rem;color:{_TXT};}}
.rt-sub{{font-size:.74rem;color:{_SUB};margin-top:2px;}}
.rt-desc{{font-size:.80rem;color:{_SUB};line-height:1.6;margin-bottom:12px;}}
.rt-display{{display:flex;align-items:center;gap:12px;margin:10px 0;}}
.rt-stars-large{{font-size:1.5rem;color:#F59E0B;letter-spacing:2px;}}
.rt-lbl{{font-size:.74rem;color:{_SUB};font-weight:600;}}

/* ── Complaint card (inside expander) ── */
.cc-badges{{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:8px;}}
.cc-cid{{font-family:'Courier New',monospace;font-size:.70rem;font-weight:700;
  background:rgba(99,102,241,.10);color:#6366F1;
  padding:3px 10px;border-radius:8px;display:inline-block;}}
.cc-badge{{border-radius:20px;padding:3px 12px;font-size:.68rem;font-weight:700;display:inline-block;}}
/* Status variants */
.st-pending    {{background:#FFFBEB;color:#B45309;}}
.st-in_progress{{background:#EFF6FF;color:#1D4ED8;}}
.st-resolved   {{background:#F0FDF4;color:#15803D;}}
.st-closed     {{background:#F1F5F9;color:#475569;}}
.st-rejected   {{background:#FFF1F2;color:#BE123C;}}
/* Priority variants */
.pr-high  {{background:#FFF1F2;color:#BE123C;}}
.pr-medium{{background:#FFFBEB;color:#B45309;}}
.pr-low   {{background:#F0FDF4;color:#15803D;}}
/* Emergency */
.badge-emg{{background:#DC2626;color:#fff;
  border-radius:20px;padding:3px 10px;font-size:.67rem;font-weight:700;}}

.cc-title{{font-size:.92rem;font-weight:800;color:{_TXT};margin:6px 0 4px;}}
.cc-desc {{font-size:.80rem;color:{_SUB};line-height:1.65;margin-bottom:8px;}}
.cc-meta {{font-size:.71rem;color:{_SUB};
  display:flex;gap:14px;flex-wrap:wrap;
  padding-top:10px;border-top:1px solid {_BOR};}}

/* ── Tip bar ── */
.tip-bar{{background:{_CARD};border:1px solid {_BOR};
  border-radius:16px;padding:14px 18px;
  display:flex;align-items:center;gap:12px;margin-top:20px;
  box-shadow:0 2px 10px rgba(15,23,42,.05);}}
.tip-text{{font-size:.80rem;color:{_SUB};flex:1;line-height:1.55;}}
.tip-text strong{{color:{_TXT};font-weight:700;}}

/* ── Priority border helpers ── */
.bl-high   {{border-left:4px solid #EF4444;padding:0 0 0 14px;margin-bottom:4px;}}
.bl-medium {{border-left:4px solid #F59E0B;padding:0 0 0 14px;margin-bottom:4px;}}
.bl-low    {{border-left:4px solid #22C55E;padding:0 0 0 14px;margin-bottom:4px;}}
.bl-emg    {{border-left:4px solid #DC2626;padding:0 0 0 14px;margin-bottom:4px;}}
.bl-default{{border-left:4px solid #6366F1;padding:0 0 0 14px;margin-bottom:4px;}}

/* ── NOTIFICATION CLEAR BUTTON ── */
.fc-clear-btn .stButton>button{{
    background:linear-gradient(135deg,#6366F1,#8B5CF6)!important;
    color:#fff!important;
    border:none!important;
    border-radius:12px!important;
    padding:8px 16px!important;
    font-size:.78rem!important;
    font-weight:700!important;
    box-shadow:0 4px 14px rgba(99,102,241,.28)!important;
    transition:all .18s ease!important;
}}

.fc-clear-btn .stButton>button:hover{{
    transform:translateY(-2px)!important;
    box-shadow:0 8px 24px rgba(99,102,241,.42)!important;
    filter:brightness(1.05)!important;
}}

.fc-clear-btn .stButton>button:active{{
    transform:scale(.98)!important;
}}
/* ── Page selector ── */
.page-row{{display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:8px;margin:12px 0 8px;}}
.page-info{{background:rgba(99,102,241,.09);color:#6366F1;
  border:1.5px solid rgba(99,102,241,.20);border-radius:20px;
  padding:5px 16px;font-size:.78rem;font-weight:800;}}

/* ── Hide filter buttons ── */
.dash-filter-btns .stButton>button{{opacity:0!important;height:0!important;
  padding:0!important;margin:0!important;min-height:0!important;overflow:hidden!important;}}
</style>
""", unsafe_allow_html=True)
    st.session_state[flag] = True


# ═══════════════════════════════════════════════════════════════════════════
# DATA FETCHERS  ── all cached with TTL to eliminate duplicate requests
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=30, show_spinner=False)
def _fetch_complaints(uid: int) -> list:
    """Single cached complaints fetch. TTL=30 s — fresh enough for dashboard."""
    import requests as _req
    try:
        r = _req.get(f"https://bfo-backend.onrender.com/complaints/user/{uid}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_notifications(uid: int) -> list:
    """Cached notifications. Reused for both the banner and bottom section."""
    import requests as _req
    try:
        r = _req.get(f"https://bfo-backend.onrender.com/schemes/user/notifications/{uid}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


@st.cache_data(ttl=120, show_spinner=False)
def _fetch_officials_map() -> dict:
    """Fetch all officials once, return id→name dict for O(1) lookup."""
    import requests as _req
    try:
        r = _req.get("https://bfo-backend.onrender.com/admin/officials/all", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return {o.get("id"): o.get("name", "") for o in data}
    except Exception:
        pass
    return {}


def _api_post(endpoint: str, json_body: dict) -> dict:
    """Lightweight POST helper; invalidates complaint cache on success."""
    import requests as _req
    try:
        r = _req.post(f"https://bfo-backend.onrender.com{endpoint}", json=json_body, timeout=10)
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}: {r.text[:100]}"}
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def _api_put(endpoint: str, json_body: dict) -> dict:
    import requests as _req
    try:
        r = _req.put(f"https://bfo-backend.onrender.com{endpoint}", json=json_body, timeout=10)
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}: {r.text[:100]}"}
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _clean(text: str) -> str:
    """Sanitise complaint description text. Uses pre-compiled regexes."""
    if not text:
        return ""
    text = _CLEAN_RE.sub("", text)
    return _SPACE_RE.sub(" ", text).strip()


def _t(lang: str, en: str, hi: str) -> str:
    return en if lang == "en" else hi


# ── Pre-computed lookup tables (built once at module level) ─────────────────
_STATUS_META = {
    "pending":     ("⏳", "Pending",     "st-pending"),
    "in_progress": ("🔄", "In Progress", "st-in_progress"),
    "resolved":    ("✅", "Resolved",    "st-resolved"),
    "closed":      ("🔒", "Closed",      "st-closed"),
    "rejected":    ("❌", "Rejected",    "st-rejected"),
}
_PRIORITY_META = {
    "high":   ("🔴", "High",   "pr-high",   "bl-high"),
    "medium": ("🟡", "Medium", "pr-medium", "bl-medium"),
    "low":    ("🟢", "Low",    "pr-low",    "bl-low"),
}


# ═══════════════════════════════════════════════════════════════════════════
# RENDER HELPERS  ── modular, single-responsibility
# ═══════════════════════════════════════════════════════════════════════════

def _render_hero(user: dict, comps: list, lang: str) -> None:
    hour       = datetime.now().hour
    greet_map  = [(12,"Good Morning","सुप्रभात","☀️"),
                  (17,"Good Afternoon","नमस्कार","👋"),
                  (24,"Good Evening","शुभ संध्या","🌙")]
    greet, emoji = next(
        ((_t(lang, g, h), e) for lim, g, h, e in greet_map if hour < lim),
        (_t(lang,"Good Evening","शुभ संध्या"), "🌙")
    )
    user_name = user.get("name", "User").split()[0]
    initials  = "".join(p[0].upper() for p in user.get("name", "U U").split()[:2])
    total     = len(comps)
    active    = sum(1 for c in comps if c.get("status") in ("pending", "in_progress"))
    resolved  = sum(1 for c in comps if c.get("status") in ("resolved", "closed"))
    pending   = sum(1 for c in comps if c.get("status") == "pending")

    st.markdown(
        f'<div class="prem-hero">'
        f'<div class="prem-hero-avatar">{initials}</div>'
        f'<div class="prem-hero-title">{emoji} {greet}, {_html.escape(user_name)}!</div>'
        f'<div class="prem-hero-sub">{_t(lang,"Welcome to your complaint dashboard","आपकी सेवा में तत्पर हैं")}</div>'
        f'<div class="prem-hero-stats">'
        f'<div class="prem-hstat h-blue"><div class="prem-hstat-num">{total}</div>'
        f'<div class="prem-hstat-lbl">📋 {_t(lang,"Total","कुल")}</div></div>'
        f'<div class="prem-hstat h-amber"><div class="prem-hstat-num">{active}</div>'
        f'<div class="prem-hstat-lbl">🔄 {_t(lang,"Active","सक्रिय")}</div></div>'
        f'<div class="prem-hstat h-green"><div class="prem-hstat-num">{resolved}</div>'
        f'<div class="prem-hstat-lbl">✅ {_t(lang,"Resolved","समाधान")}</div></div>'
        f'<div class="prem-hstat h-red"><div class="prem-hstat-num">{pending}</div>'
        f'<div class="prem-hstat-lbl">⏳ {_t(lang,"Pending","लंबित")}</div></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def _render_quick_actions(lang: str) -> None:
    st.markdown(
        f'<div class="prem-section-header">⚡ {_t(lang,"Quick Actions","त्वरित कार्य")}</div>',
        unsafe_allow_html=True,
    )
    actions = [
        ("📢", _t(lang,"File Complaint","शिकायत दर्ज"),    "file_complaint",
         "linear-gradient(135deg,rgba(239,68,68,.12),rgba(220,38,38,.06))",  "#EF4444"),
        ("🔍", _t(lang,"Track Status","ट्रैक करें"),      "tracking",
         "linear-gradient(135deg,rgba(99,102,241,.12),rgba(139,92,246,.06))", "#6366F1"),
        ("📜", _t(lang,"Govt Schemes","सरकारी योजनाएं"), "schemes",
         "linear-gradient(135deg,rgba(5,150,105,.12),rgba(16,185,129,.06))",  "#059669"),
        ("🤖", _t(lang,"AI Assistant","एआई सहायक"),      "assistant",
         "linear-gradient(135deg,rgba(6,182,212,.12),rgba(14,165,233,.06))",  "#06B6D4"),
    ]
    qa_cols = st.columns(4)
    for col, (icon, label, screen, bg, color) in zip(qa_cols, actions):
        with col:
            st.markdown(
                f'<div class="prem-action-card" style="'
                f'background:{bg};border:1.5px solid {color}22;">'
                f'<div class="prem-action-icon" style="'
                f'background:{color}18;border:1.5px solid {color}30;font-size:1.5rem;">{icon}</div>'
                f'<div class="prem-action-label" style="color:{color};font-weight:800;">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(label, key=f"qa_{screen}", use_container_width=True):
                st.session_state.screen = screen
                st.rerun()


def _render_notification_banner(notifs: list, lang: str) -> None:
    """Render top notification banner — uses already-fetched notifs list."""
    unread = [n for n in notifs if not n.get("is_read")]
    if not unread:
        return
    first = unread[0]
    st.markdown(
        f'<div class="notif-inline">'
        f'<div class="ni-dot"></div>'
        f'<div class="ni-text">🔔 {_html.escape(first.get("title",""))} — '
        f'{_html.escape(first.get("message","")[:65])}…</div>'
        f'<span class="ni-badge">{len(unread)} {_t(lang,"new","नई")}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_feedback_section(comps: list, lang: str) -> None:
    """Feedback confirmation cards — no extra API calls."""
    need_feedback = [c for c in comps if c.get("status") == "resolved" and not c.get("feedback")]
    if not need_feedback:
        return

    st.markdown(
        f'<div class="prem-section-header">✅ {_t(lang,"Confirm Resolution","समाधान की पुष्टि करें")}</div>',
        unsafe_allow_html=True,
    )
    for fb_comp in need_feedback:
        fb_cid      = fb_comp.get("complaint_id")
        fb_deadline = fb_comp.get("feedback_deadline", _t(lang,"within 2 days","2 दिनों के भीतर"))
        cleaned     = _clean(fb_comp.get("description", ""))

        st.markdown(
            f'<div class="fb-card">'
            f'<div class="fb-head">'
            f'<div class="fb-icon">✅</div>'
            f'<div>'
            f'<div class="fb-title">{_t(lang,"Complaint Resolved — Please Confirm!","शिकायत समाधान हुई — पुष्टि करें!")}</div>'
            f'<div class="fb-sub">#{fb_cid}</div>'
            f'</div></div>'
            f'<div class="fb-desc">{_html.escape(cleaned[:120])}…'
            f'<br><small>⏰ {_t(lang,"Respond by","उत्तर दें:")} {_html.escape(str(fb_deadline))}</small>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button(_t(lang,"👍 Yes, Satisfied!","👍 हाँ, संतुष्ट हूँ!"), key=f"fb_ok_{fb_cid}"):
                resp = _api_put(f"/complaints/{fb_cid}/feedback", {"feedback": "satisfied"})
                if resp.get("success"):
                    st.session_state[f"pending_rating_{fb_cid}"] = True
                    _fetch_complaints.clear()          # invalidate cache
                    st.toast("Feedback submitted")
                    st.rerun()
                else:
                    st.error(f"Error: {resp.get('error','Unknown')}")
        with col2:
            if st.button(_t(lang,"❌ Not Resolved — Reopen","❌ समाधान नहीं — पुनः खोलें"), key=f"fb_no_{fb_cid}"):
                resp = _api_put(f"/complaints/{fb_cid}/feedback", {"feedback": "not_satisfied"})
                if resp.get("success"):
                    _fetch_complaints.clear()
                    st.toast("Complaint reopened")
                    st.rerun()
                else:
                    st.error(f"Error: {resp.get('error','Unknown')}")


def _render_rating_section(comps: list, lang: str) -> None:
    """Rating cards. Officials fetched once via _fetch_officials_map()."""
    need_rating = [c for c in comps if c.get("feedback") == "satisfied" and not c.get("rating")]
    # also include any that have a pending_rating_ flag in session_state
    pending_ids = {
        k.replace("pending_rating_","")
        for k in st.session_state
        if k.startswith("pending_rating_")
    }
    existing_ids = {c.get("complaint_id") for c in need_rating}
    for cid in pending_ids - existing_ids:
        match = next((c for c in comps if str(c.get("complaint_id")) == cid), None)
        if match:
            need_rating.append(match)

    if not need_rating:
        return

    # Single fetch for all officials — O(1) lookup inside the loop
    officials_map = _fetch_officials_map()

    st.markdown(
        f'<div class="prem-section-header">⭐ {_t(lang,"Rate the Service","सेवा को रेट करें")}</div>',
        unsafe_allow_html=True,
    )
    STAR_LABELS = {
        1: _t(lang,"Very Poor","बहुत खराब"),
        2: _t(lang,"Poor","खराब"),
        3: _t(lang,"Average","औसत"),
        4: _t(lang,"Good","अच्छा"),
        5: _t(lang,"Excellent","उत्कृष्ट"),
    }

    for rt_comp in need_rating:
        rt_cid      = rt_comp.get("complaint_id")
        rt_off_id   = rt_comp.get("official_id")
        rt_off_name = (
            rt_comp.get("official_name")
            or officials_map.get(rt_off_id)
            or _t(lang,"the department","विभाग")
        )
        star_key    = f"_star_val_{rt_cid}"
        comment_key = f"_comment_val_{rt_cid}"
        cur_star    = st.session_state.get(star_key, 0)
        star_disp   = "★" * cur_star if cur_star > 0 else "☆☆☆☆☆"
        cleaned     = _clean(rt_comp.get("description",""))

        st.markdown(
            f'<div class="rt-card">'
            f'<div class="rt-head"><div class="rt-icon">⭐</div><div>'
            f'<div class="rt-title">{_t(lang,"Rate the Service","सेवा को रेट करें")}</div>'
            f'<div class="rt-sub">{_t(lang,"Resolved by","समाधानकर्ता")}: '
            f'<strong>{_html.escape(str(rt_off_name))}</strong> · #{rt_cid}</div>'
            f'</div></div>'
            f'<div class="rt-desc">{_html.escape(cleaned[:100])}…</div>'
            f'<div class="rt-display">'
            f'<div class="rt-stars-large">{star_disp}</div>'
            f'<div class="rt-lbl">{_t(lang,"Select your rating below","नीचे रेटिंग चुनें")}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        star_cols = st.columns(5)
        for val in range(1, 6):
            with star_cols[val - 1]:
                icon = "★" if cur_star == val else "☆"
                if st.button(f"{icon} {STAR_LABELS[val]}", key=f"star_{rt_cid}_{val}"):
                    st.session_state[star_key] = val
                    st.rerun()

        comment = st.text_area(
            _t(lang,"Additional feedback (optional)","अतिरिक्त प्रतिक्रिया (वैकल्पिक)"),
            key=comment_key, height=85,
        )

        if cur_star == 0:
            st.info(_t(lang,
                "⭐ Please select a star rating above before submitting.",
                "⭐ सबमिट करने से पहले ऊपर एक स्टार रेटिंग चुनें।"))
        else:
            sub_key = f"rate_sub_{rt_cid}"
            if st.button(f"{'⭐'*cur_star} {_t(lang,'Submit Rating','रेटिंग सबमिट करें')}",
                         key=sub_key):
                payload = {
                    "stars":       cur_star,
                    "comment":     comment or None,
                    "user_id":     st.session_state.user.get("user_id"),
                    "official_id": rt_off_id if rt_off_id else 1,
                }
                resp = _api_post(f"/complaints/{rt_cid}/rate", payload)
                if resp.get("success"):
                    for k in (star_key, comment_key, f"pending_rating_{rt_cid}"):
                        st.session_state.pop(k, None)
                    _fetch_complaints.clear()
                    st.success(_t(lang,"✅ Rating submitted! Thank you.","✅ रेटिंग सबमिट हो गई! धन्यवाद।"))
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"Error: {resp.get('detail', resp.get('error','Unknown'))}")

        st.markdown(
            f'<div style="height:1px;background:linear-gradient(90deg,'
            f'transparent,rgba(99,102,241,.15),transparent);margin:16px 0 24px;"></div>',
            unsafe_allow_html=True,
        )


def _render_single_complaint_card(
        c: dict,
        lang: str,
        skip_ids: set,
        idx: int
    ) -> bool:
    """
    Render one complaint expander.
    Returns False if the card was skipped (in skip_ids), True otherwise.
    All badge/border CSS now comes from pre-defined classes — zero per-card
    Python string work for colors.
    """
    cid = c.get("complaint_id", "N/A")
    if cid in skip_ids:
        return False

    status       = c.get("status", "pending")
    priority     = c.get("priority", "medium")
    category     = c.get("category", "other").title()
    desc         = _clean(c.get("description", ""))
    loc          = c.get("location", "—")
    date         = c.get("created_at", "—")
    is_emergency = c.get("is_emergency", False)
    sla          = c.get("sla_deadline")
    overdue      = c.get("is_overdue", False)
    img_path     = c.get("image_path")

    s_icon, s_lbl, s_cls = _STATUS_META.get(status, ("", "", ""))
    p_icon, p_lbl, p_cls, bl_cls = _PRIORITY_META.get(priority, ("", "", "pr-medium", "bl-default"))
    if is_emergency:
        bl_cls = "bl-emg"

    emg_html  = '<span class="cc-badge badge-emg">🚨 EMERGENCY</span>' if is_emergency else ""
    exp_title = (
        ("🚨 " if is_emergency else "")
        + f"{idx}. #{cid}  ·  {category}  ·  {s_icon} {s_lbl}"
    )
    st.markdown(
        f"""
        <div style="
            font-size:0.82rem;
            font-weight:800;
            color:#6366F1;
            margin:10px 0 6px 4px;
        ">
            Complaint #{idx}
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander(exp_title, expanded=False):
        if st.button(f"🔊 {_t(lang,'Listen','सुनें')}", key=f"voice_{cid}"):
            try:
                speak_text(f"Complaint {cid}: {desc}", lang)
            except NameError:
                pass

        st.markdown(
            f'<div class="{bl_cls}">'
            f'<div class="cc-badges">'
            f'<span class="cc-cid">#{cid}</span>'
            f'<span class="cc-badge {s_cls}">{s_icon} {s_lbl}</span>'
            f'<span class="cc-badge {p_cls}">{p_icon} {p_lbl}</span>'
            f'{emg_html}'
            f'</div>'
            f'<div class="cc-title">{_html.escape(category)}</div>'
            f'<div class="cc-desc">{_html.escape(desc[:180])}{"…" if len(desc)>180 else ""}</div>'
            f'<div class="cc-meta">'
            f'<span>📍 {_html.escape(str(loc))}</span>'
            f'<span>📅 {_html.escape(str(date))}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        # Lazy image render — only fetched/decoded when expander is open
        # ── Complaint Image Preview ─────────────────────────

        # ── Complaint Evidence Image ─────────────────────────

        if img_path:

            st.markdown("""
            <style>

            .evidence-wrap{
                margin-top:14px;
                margin-bottom:10px;
            }

            .evidence-title{
                font-size:.80rem;
                font-weight:800;
                color:#6366F1;
                margin-bottom:8px;
                display:flex;
                align-items:center;
                gap:8px;
            }

            .evidence-box{
                background:linear-gradient(
                    135deg,
                    rgba(99,102,241,.08),
                    rgba(139,92,246,.04)
                );
                border:1.5px solid rgba(99,102,241,.18);
                border-radius:18px;
                padding:14px;
            }

            .img-btn .stButton>button{
                width:100%;
                border:none!important;
                border-radius:14px!important;
                background:linear-gradient(135deg,#6366F1,#8B5CF6)!important;
                color:white!important;
                font-weight:700!important;
                padding:12px 18px!important;
                font-size:.84rem!important;
                box-shadow:0 8px 24px rgba(99,102,241,.28)!important;
                transition:all .18s ease!important;
            }

            .img-btn .stButton>button:hover{
                transform:translateY(-2px)!important;
                box-shadow:0 12px 30px rgba(99,102,241,.38)!important;
            }

            </style>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="evidence-wrap">

                <div class="evidence-title">
                    🖼️ Complaint Evidence
                </div>

                <div class="evidence-box">
            """, unsafe_allow_html=True)

            st.markdown('<div class="img-btn">', unsafe_allow_html=True)

            show_img = st.button(
                "👁️ View Uploaded Image",
                key=f"show_img_{cid}",
                use_container_width=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

            if show_img:

                st.image(
                    f"https://bfo-backend.onrender.com{img_path}",
                    caption="Uploaded Complaint Evidence",
                    use_container_width=True
                )

            st.markdown("</div></div>", unsafe_allow_html=True)

        if sla:
            if overdue:
                st.error(f"⏰ OVERDUE! Expected by: {sla}")
            else:
                st.info(f"⏱️ Expected by: {sla}")

    return True


def _render_complaint_list(comps: list, lang: str, skip_ids: set) -> None:
    if not comps:
        st.markdown(
            f'<div class="prem-empty-state" style="margin-top:12px;">'
            f'<span class="prem-empty-icon">📭</span>'
            f'<div class="prem-empty-title">'
            f'{_t(lang,"You have not filed any complaints yet.","आपने अभी तक कोई शिकायत दर्ज नहीं की है।")}'
            f'</div><div class="prem-empty-sub">'
            f'{_t(lang,"Use Quick Actions above to file your first complaint.","पहली शिकायत दर्ज करने के लिए ऊपर Quick Actions का उपयोग करें।")}'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<div class="prem-section-header">📋 {_t(lang,"Your Complaints","आपकी शिकायतें")}</div>',
        unsafe_allow_html=True,
    )

    # ── Filter chips (visual display only) ────────────────────────────────
    filters = [
        ("all",         "All",         "📋"),
        ("pending",     "Pending",     "⏳"),
        ("in_progress", "In Progress", "🔄"),
        ("resolved",    "Resolved",    "✅"),
        ("closed",      "Closed",      "🔒"),
    ]
    active_filter = st.session_state.get("dash_filter", "all")
    

    # ── Filter buttons (hidden but functional) ─────────────────────────────
    st.markdown('<div class="dash-filter-btns">', unsafe_allow_html=True)
    with st.container():
        fcols = st.columns(len(filters))
        for fcol, (fval, flbl, ficon) in zip(fcols, filters):
            with fcol:
                if st.button(f"{ficon} {flbl}", key=f"flt_{fval}", use_container_width=True):
                    st.session_state.dash_filter = fval
                    # Reset to page 1 on filter change — no full rerun needed
                    st.session_state["dash_page"] = 0
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Filter data ────────────────────────────────────────────────────────
    filtered = comps if active_filter == "all" else [
        c for c in comps if c.get("status") == active_filter
    ]
    # Exclude feedback/rating cards already shown above
    filtered = [c for c in filtered if c.get("complaint_id") not in skip_ids]

    # ── Pagination ─────────────────────────────────────────────────────────
    total_pages = max(1, (len(filtered) + PAGE_SIZE - 1) // PAGE_SIZE)
    page        = st.session_state.get("dash_page", 0)
    page        = max(0, min(page, total_pages - 1))   # clamp
    page_slice  = filtered[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]

    st.markdown(
        f'<div class="page-row">'
        f'<span class="page-info">'
        f'{_t(lang,"Showing","दिखा रहे हैं")} '
        f'<strong>{len(page_slice)}</strong> / <strong>{len(filtered)}</strong> '
        f'{_t(lang,"complaints","शिकायतें")}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Render only the current page ──���────────────────────────────────────
    shown = 0

    start_no = page * PAGE_SIZE + 1

    for idx, c in enumerate(page_slice, start=start_no):

        if _render_single_complaint_card(
            c,
            lang,
            skip_ids,
            idx
        ):
            shown += 1

    if shown == 0:
        st.markdown(
            f'<div class="prem-empty-state" style="margin-top:12px;">'
            f'<span class="prem-empty-icon">🔍</span>'
            f'<div class="prem-empty-title">'
            f'{_t(lang,"No complaints match the current filter.","वर्तमान फ़िल्टर से मेल खाती कोई शिकायत नहीं।")}'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    # ── Page navigation ────────────────────────────────────────────────────
    if total_pages > 1:
        nav_cols = st.columns([1, 3, 1])
        with nav_cols[0]:
            if page > 0:
                if st.button("← Prev", key="page_prev", use_container_width=True):
                    st.session_state["dash_page"] = page - 1
                    st.rerun()
        with nav_cols[1]:
            st.markdown(
                f'<div style="text-align:center;font-size:.78rem;'
                f'color:rgba(99,102,241,.80);font-weight:700;padding:8px 0;">'
                f'Page {page+1} / {total_pages}</div>',
                unsafe_allow_html=True,
            )
        with nav_cols[2]:
            if page < total_pages - 1:
                if st.button("Next →", key="page_next", use_container_width=True):
                    st.session_state["dash_page"] = page + 1
                    st.rerun()


def _render_notifications_footer(notifs: list, lang: str) -> None:
    """Bottom notifications section — reuses already-fetched notifs."""
    unread = [n for n in notifs if not n.get("is_read")]
    if not unread:
        return

    st.markdown(
        f'<div class="prem-section-header">🔔 {_t(lang,"Notifications","सूचनाएं")} '
        f'<span style="background:#6366F1;color:#fff;border-radius:20px;'
        f'padding:2px 10px;font-size:.68rem;font-weight:800;">'
        f'{len(unread)} {_t(lang,"new","नई")}</span></div>',
        unsafe_allow_html=True,
    )
    for n in unread[:3]:
        st.markdown(
            f'<div class="prem-notif-card">'
            f'<div class="prem-notif-dot"></div>'
            f'<div>'
            f'<div class="prem-notif-title">🔔 {_clean(_html.unescape(str(n.get("title",""))))}</div>'
            f'<div class="prem-notif-msg">{_clean(_html.unescape(str(n.get("message",""))))}</div>'
            f'<div class="prem-notif-time">{_clean(_html.unescape(str(n.get("time",""))))}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    if st.button(_t(lang,"View All Notifications →","सभी सूचनाएं देखें →"), key="va_notifs_dash"):
        st.session_state.screen = "notifications"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def pg_user_dashboard() -> None:
    _apply_layout("user") 
    try:
        submit_offline_complaints()
    except NameError:
        pass

    user = st.session_state.user or {}
    uid  = user.get("user_id")
    lang = st.session_state.language
    dark = st.session_state.get("dark_mode", False)

    # ── 1. CSS injected once per session ───────────────────────────────────
    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)
    _inject_css_once(dark)

    # ── 2. All data fetched via cached functions (single network trip each) ─
    comps  = _fetch_complaints(uid)
    notifs = _fetch_notifications(uid)

    # ── 3. Session-state defaults ───────────────────────────────────────────
    st.session_state.setdefault("dash_filter", "all")
    st.session_state.setdefault("dash_page",   0)

    # ── 4. Build skip-set: IDs shown in feedback/rating sections ───────────
    skip_ids = {
        c.get("complaint_id")
        for c in comps
        if (c.get("status") == "resolved" and not c.get("feedback"))
        or (c.get("feedback") == "satisfied"  and not c.get("rating"))
    }

    # ── 5. Render sections ─────────────────────────────────────────────────
    
    _dashboard_render_hero(user, comps, lang)
    _render_quick_actions(lang)
    _render_notification_banner(notifs, lang)
    _render_feedback_section(comps, lang)
    _render_rating_section(comps, lang)
    _render_complaint_list(comps, lang, skip_ids)
    _render_notifications_footer(notifs, lang)

    # ── 6. Tip bar ─────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="tip-bar">'
        f'<span style="font-size:1.1rem;">💡</span>'
        f'<div class="tip-text"><strong>{_t(lang,"Pro Tip:","सुझाव:")}</strong> '
        f'{_t(lang,"Track your complaint in real-time and get instant notifications on every update.","अपनी शिकायत को रियल-टाइम में ट्रैक करें और हर अपडेट पर तुरंत सूचना पाएं।")}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── 7. Manual refresh (the ONLY justified rerun) ───────────────────────
    if st.button(_t(lang,"🔄 Refresh Dashboard","🔄 डैशबोर्ड रिफ्रेश करें"),
                 key="refresh_dash", use_container_width=True):
        _fetch_complaints.clear()
        _fetch_notifications.clear()
        st.rerun()

def _feedback_confirm_card(c, uid, idx=0):
    cid = c.get("complaint_id", "")
    complaint_db_id = c.get("id", idx)
    dl = c.get("feedback_deadline", "within 2 days")
    unique_key = f"{complaint_db_id}_{idx}_{cid[:8]}"

    st.markdown(f"""
    <div style="background:#fffbeb; border-left:4px solid #f59e0b; border-radius:12px; padding:1rem; margin:1rem 0;">
        <div style="font-size:1.5rem;">✅</div>
        <div style="font-weight:800; font-size:1rem; color:#b45309;">Complaint Resolved — Please Confirm!</div>
        <div><strong>#{cid}</strong> · {c.get('category', '').title()}<br><span style="opacity:0.8;">{c.get('description', '')[:90]}…</span></div>
        <div style="font-size:0.75rem; color:#b45309;">⏰ Respond by {dl} · After 2 days auto-closes.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Yes, I'm Satisfied!", key=f"fb_ok_{unique_key}", use_container_width=True):
            resp = api("put", f"/complaints/{cid}/feedback", json={"feedback": "satisfied"})
            if resp.get("success"):
                st.success("✅ Thank you! Now please rate the service.")
                st.rerun()
            else:
                st.error(resp.get("error", "Error submitting feedback"))
    with col2:
        if st.button("❌ Not Resolved — Reopen", key=f"fb_no_{unique_key}", use_container_width=True):
            resp = api("put", f"/complaints/{cid}/feedback", json={"feedback": "not_satisfied"})
            if resp.get("success"):
                st.warning("Complaint reopened for re-investigation.")
                st.rerun()
            else:
                st.error(resp.get("error", "Error submitting feedback"))
def render_timeline(complaint):
    steps = [
        {"key": "submitted", "label": "Submitted", "icon": "📝"},
        {"key": "assigned",  "label": "Assigned",  "icon": "👤"},
        {"key": "in_progress","label": "In Progress","icon": "⚙️"},
        {"key": "resolved",  "label": "Resolved",  "icon": "✅"},
        {"key": "closed",    "label": "Closed",    "icon": "🔒"}
    ]

    # Map your complaint status to the step keys
    status_to_step = {
        "pending":     "submitted",
        "assigned":    "assigned",
        "in_progress": "in_progress",
        "resolved":    "resolved",
        "closed":      "closed",
        "rejected":    None
    }
    current = complaint.get("status", "pending")
    current_step_key = status_to_step.get(current, "submitted")

    # Fetch timeline events if they exist
    timeline_events = complaint.get("timeline", [])
    event_times = {}
    for ev in timeline_events:
        ev_status = ev.get("status", "")
        # Try to map timeline status to step key
        mapped = status_to_step.get(ev_status)
        if mapped:
            event_times[mapped] = ev.get("time", "")
        elif ev_status in [s["key"] for s in steps]:
            event_times[ev_status] = ev.get("time", "")

    # Determine which step is current
    try:
        current_index = [s["key"] for s in steps].index(current_step_key)
    except ValueError:
        current_index = 0

    # Build HTML (responsive horizontal layout)
    html = '<div style="margin: 1rem 0; overflow-x: auto;">'
    html += '<div style="display: flex; align-items: stretch; justify-content: space-between; min-width: 500px;">'

    for i, step in enumerate(steps):
        is_completed = i < current_index
        is_current = i == current_index

        if is_current:
            color = "#3b82f6"      # blue for current
            bg_color = "#eff6ff"
            border_color = "#3b82f6"
        elif is_completed:
            color = "#10b981"      # green for completed
            bg_color = "#f0fdf4"
            border_color = "#10b981"
        else:
            color = "#9ca3af"      # gray for pending
            bg_color = "#f9fafb"
            border_color = "#e5e7eb"

        # Format timestamp if present
        ts = event_times.get(step["key"], "")
        if ts:
            try:
                from datetime import datetime
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                ts = dt.strftime("%d %b, %I:%M %p")
            except:
                pass

        html += f"""
        <div style="flex: 1; text-align: center; min-width: 100px;">
            <div style="
                width: 44px; height: 44px; 
                background: {bg_color};
                border: 2px solid {border_color};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 8px auto;
                color: {color};
                font-size: 1.3rem;">
                {step['icon']}
            </div>
            <div style="font-size: 0.75rem; font-weight: 600; color: {color};">{step['label']}</div>
            <div style="font-size: 0.65rem; color: #6b7280; margin-top: 4px;">{ts}</div>
        </div>
        """

        # Arrow icon between steps (except after last)
        if i < len(steps) - 1:
            arrow_color = "#3b82f6" if i < current_index else "#e5e7eb"
            html += f'<div style="color: {arrow_color}; font-size: 1.2rem; align-self: center;">→</div>'

    html += '</div></div>'
    return html

def _rating_card(c, uid, idx=0):
    cid = c.get("complaint_id", "")
    complaint_db_id = c.get("id", idx)
    off_id = c.get("official_id")
    unique_key = f"{complaint_db_id}_{idx}_{cid[:8]}"

    # Get department name or fallback
    off_name = "the department"
    if off_id:
        off_list = api("get", "/admin/officials/all")
        if isinstance(off_list, list):
            match = next((o for o in off_list if o.get("id") == off_id), None)
            if match:
                off_name = match.get("name", off_name)
    else:
        # No official assigned – use department name
        dept_id = c.get("department_id")
        if dept_id:
            depts = api("get", "/admin/departments")
            if isinstance(depts, list):
                dept = next((d for d in depts if d.get("id") == dept_id), None)
                if dept:
                    off_name = dept.get("name", off_name)

    st.markdown(f"""
    <div style="background:#f0fdf4; border-left:4px solid #10b981; border-radius:12px; padding:1rem; margin:1rem 0;">
        <div style="font-weight:800; font-size:1rem;">⭐ Rate the Service</div>
        <div>How satisfied were you with <strong>{off_name}</strong>'s resolution of <strong>#{cid}</strong>?</div>
        <div style="font-size:0.8rem;">{c.get('description', '')[:80]}…</div>
    </div>
    """, unsafe_allow_html=True)

    stars = st.select_slider(
        "Your rating",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: f"{'⭐' * x} ({x}/5)",
        value=5,
        key=f"star_{unique_key}"
    )
    st.markdown(f'<div style="text-align:center;font-size:2rem;">{"⭐" * stars}</div>', unsafe_allow_html=True)

    label_map = {
        1: "😞 Very Unsatisfied",
        2: "😕 Unsatisfied",
        3: "😐 Neutral",
        4: "😊 Satisfied",
        5: "🤩 Very Satisfied!"
    }
    st.markdown(f'<div style="text-align:center;font-weight:700;color:#d97706;">{label_map[stars]}</div>', unsafe_allow_html=True)

    comment = st.text_area(
        "Additional feedback (optional)",
        key=f"cmt_{unique_key}",
        placeholder=f"Tell us about your experience with {off_name}…",
        height=80,
        label_visibility="collapsed"
    )

    if st.button(f"Submit {stars}⭐ Rating", key=f"rate_{unique_key}", use_container_width=True):
        # If no official_id, we can still submit rating with official_id = 1 (admin) or None (backend handles)
        payload = {
            "stars": stars,
            "comment": comment or None,
            "user_id": uid,
            "official_id": off_id if off_id else 1  # fallback to admin official (ID 1)
        }
        resp = api("post", f"/complaints/{cid}/rate", json=payload)
        if resp.get("success"):
            st.success(f"✅ Rating submitted! Thank you for your feedback.")
            st.balloons()
            st.rerun()
        else:
            st.error(resp.get("detail", resp.get("error", "Error submitting rating")))

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CSS
# ─────────────────────────────────────────────────────────────────────────────


# ────────────��────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# VERSION-SAFE HELPERS
# st.image(use_container_width=) was added in Streamlit 1.16.
# Older installs (common on Windows with pip-cached packages) only have
# use_column_width=. This wrapper tries the new arg first, falls back silently.
# ─────────────────────────────────────────────────────────────────────────────

def _st_image(src, caption: str = "") -> None:
    """Display an image filling its container, compatible with all Streamlit versions."""
    kwargs: dict = {"caption": caption} if caption else {}
    try:
        st.image(src, use_container_width=True, **kwargs)
    except TypeError:
        # Streamlit < 1.16 — use the old parameter name
        try:
            st.image(src, use_column_width=True, **kwargs)
        except TypeError:
            # Ultimate fallback — no width control
            st.image(src, **kwargs)
 
# ─────────────────────────────────────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────────────────────────────────────
_FC_DEFAULTS: dict[str, Any] = {
    "category":        "other",
    "description":     "",
    # Merged text shown in the text input widget
    "location_name":   "Bhopal, Madhya Pradesh",
    # Structured location fields — populated by GPS geocode
    "loc_area":        "",   # neighbourhood / suburb / village
    "loc_city":        "",   # city / town
    "loc_district":    "",   # district / county
    "loc_state":       "",   # state
    "loc_pincode":     "",   # postcode
    "lat":             23.2599,
    "lon":             77.4126,
    "is_emergency":    False,
    "voice_text":      "",
    "voice_reset_key": 0,
    # bridge_key tracks how many times bridge must be fresh
    "bridge_key":      0,
    "voice_applied":   False,
    "image_name":      "",
    "phase":           "idle",
    "submit_token":    "",
    "error_msg":       "",
    "success_data":    {},
    "_map_lat":        23.2599,
    "_map_lon":        77.4126,
    "_gps_ingested":   False,
    "_voice_ingested": False,
    "_img_bytes":      None,
    "_img_name":       "",
}
 
 
def _init_fc() -> None:
    if "fc" not in st.session_state:
        st.session_state.fc = dict(_FC_DEFAULTS)
    else:
        for k, v in _FC_DEFAULTS.items():
            if k not in st.session_state.fc:
                st.session_state.fc[k] = v
 
 
def fc() -> dict[str, Any]:
    return st.session_state.fc  # type: ignore[return-value]
 
 
def fc_set(**kw: Any) -> None:
    st.session_state.fc.update(kw)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# REVERSE GEOCODE  (FIX 2 — now includes pincode)
# ─────────────────────────────────────────────────────────────────────────────
 
@st.cache_data(ttl=300, show_spinner=False)
def _reverse_geocode(lat: float, lon: float) -> dict:
    """
    Returns a structured dict with all location fields.
    Keys: area, city, district, state, pincode, display (merged string)
    Never raises — always returns a valid dict.
    """
    empty = {
        "area": "", "city": "", "district": "",
        "state": "", "pincode": "",
        "display": f"{lat:.5f}, {lon:.5f}",
    }
    try:
        import requests as _req
        r = _req.get(
            "https://nominatim.openstreetmap.org/reverse"
            f"?format=jsonv2&lat={lat}&lon={lon}&zoom=18&addressdetails=1",
            headers={"User-Agent": "JanSevaPortal/1.0"},
            timeout=6,
        )
        if not r.ok:
            return empty
        addr = r.json().get("address", {})
 
        area     = (addr.get("neighbourhood") or addr.get("suburb")
                    or addr.get("village")    or addr.get("hamlet")
                    or addr.get("residential") or "")
        city     = addr.get("city") or addr.get("town") or ""
        district = addr.get("county") or addr.get("district") or addr.get("state_district") or ""
        state    = addr.get("state", "")
        pincode  = addr.get("postcode", "")
 
        # Build display string: all non-empty parts joined
        parts = [p for p in [area, city, district, state] if p]
        base  = ", ".join(parts) if parts else f"{lat:.5f}, {lon:.5f}"
        display = f"{base} — {pincode}" if pincode else base
 
        return {
            "area": area, "city": city, "district": district,
            "state": state, "pincode": pincode, "display": display,
        }
    except Exception:
        return empty
 
 
# ─────────────────────────────────────────────────────────────────────────────
# QUERY PARAM INGESTION
# FIX 1 & 3: Delete widget keys before rerun so widgets re-seed from fc()
# FIX 3: Reset _voice_ingested on clear so next voice param is accepted
# ─────────────────────────────────────────────────────────────────────────────
 
def _ingest_query_params() -> bool:
    params = st.query_params
 
    # ── Voice text ───────────────────────────────────────────────────────────
    if "voice_text" in params and not fc()["_voice_ingested"]:
        text = unquote(params["voice_text"])
        fc_set(
            voice_text      = text,
            description     = text,
            voice_applied   = True,
            _voice_ingested = True,
        )
        st.query_params.clear()
        # Delete widget key so textarea re-seeds from fc()["description"]
        st.session_state.pop("_fc_desc", None)
        return True
 
    # ── GPS location ─────────────────────────────────────────────────────────
    if "gps_lat" in params and not fc()["_gps_ingested"]:
        try:
            lat  = float(params["gps_lat"])
            lon  = float(params["gps_lon"])
 
            # JS iframe sends pre-built structured fields via URL params
            # Fall back to Python geocode only if JS fields are absent
            js_area     = unquote(params.get("gps_area",     ""))
            js_city     = unquote(params.get("gps_city",     ""))
            js_district = unquote(params.get("gps_district", ""))
            js_state    = unquote(params.get("gps_state",    ""))
            js_pincode  = unquote(params.get("gps_pincode",  ""))
            js_display  = unquote(params.get("gps_name",     ""))
 
            if js_display:
                # JS already did the geocoding — use its structured fields
                geo = {
                    "area":     js_area,
                    "city":     js_city,
                    "district": js_district,
                    "state":    js_state,
                    "pincode":  js_pincode,
                    "display":  js_display,
                }
            else:
                # Fallback: Python-side geocode
                geo = _reverse_geocode(lat, lon)
 
            fc_set(
                lat           = lat,
                lon           = lon,
                location_name = geo["display"],
                loc_area      = geo["area"],
                loc_city      = geo["city"],
                loc_district  = geo["district"],
                loc_state     = geo["state"],
                loc_pincode   = geo["pincode"],
                _map_lat      = lat,
                _map_lon      = lon,
                _gps_ingested = True,
            )
            st.query_params.clear()
            # Delete widget key so text input re-seeds from fc()
            st.session_state.pop("_fc_location", None)
            return True
        except (ValueError, KeyError, TypeError):
            pass
 
    return False
 
 
# ─────────────────────────────────────────────────────────────────────────────
# CSS (unchanged from v4 — all classes preserved)
# ─────────────────────────────────────────────────────────────────────────────
 
def _inject_page_css(dark: bool) -> None:
    CARD  = "#0D1220" if dark else "#FFFFFF"
    BG    = "#070B14" if dark else "#F4F7FD"
    BOR   = "#1E2A3D" if dark else "#E2E8F4"
    TXT   = "#EFF2FF" if dark else "#0B1428"
    SUB   = "#7C8FAC" if dark else "#64748B"
    INP   = "#0F1828" if dark else "#F0F4FB"
    A1    = "#6366F1"
    A2    = "#8B5CF6"
    GRN   = "#10B981"
    GRN_BG  = "#071A10" if dark else "#F0FDF4"
    GRN_BD  = "#166534" if dark else "#86EFAC"
    GRN_T   = "#4ADE80" if dark else "#166534"
    AMB_BG  = "#1A1000" if dark else "#FFFBEB"
    AMB_BD  = "#92400E" if dark else "#FDE68A"
    AMB_T   = "#FCD34D" if dark else "#92400E"
    RED_BG  = "#1A0505" if dark else "#FEF2F2"
    RED_BD  = "#991B1B" if dark else "#FECACA"
    RED_T   = "#FCA5A5" if dark else "#BE123C"
 
    css = f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=DM+Mono:wght@400;500&display=swap');
 
html,body,.stApp{{background:{BG}!important;color:{TXT};font-family:'DM Sans',system-ui,sans-serif;}}
.main .block-container{{max-width:860px!important;margin:0 auto!important;padding:1.5rem 1.75rem 4rem!important;}}
#MainMenu,footer,header,.stDeployButton{{display:none!important;}}
.stApp::before{{content:'';position:fixed;top:0;left:0;right:0;height:2px;z-index:9999;pointer-events:none;
    background:linear-gradient(90deg,{A1},{A2},#22D3EE,{A1});background-size:200% 100%;
    animation:fc-stripe 6s ease infinite;}}
@keyframes fc-stripe{{0%,100%{{background-position:0 50%;}}50%{{background-position:100% 50%;}}}}
@keyframes fc-fade-up{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
 
.fc-hero{{background:linear-gradient(135deg,#1a1757 0%,#2e2b85 45%,#0d3461 100%);
    border-radius:24px;padding:30px 28px 24px;margin-bottom:20px;
    position:relative;overflow:hidden;box-shadow:0 20px 56px rgba(0,0,0,0.30);
    animation:fc-fade-up .30s ease both;}}
.fc-hero::before{{content:'';position:absolute;top:-80px;right:-80px;width:280px;height:280px;
    border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,0.07) 0%,transparent 70%);}}
.fc-hero-eyebrow{{font-size:.60rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;
    color:rgba(255,255,255,0.55);margin-bottom:8px;display:flex;align-items:center;gap:7px;}}
.fc-hero-dot{{width:6px;height:6px;background:#10B981;border-radius:50%;
    box-shadow:0 0 0 3px rgba(16,185,129,0.28);animation:fc-dot 2s ease infinite;}}
@keyframes fc-dot{{0%,100%{{box-shadow:0 0 0 3px rgba(16,185,129,.28);}}50%{{box-shadow:0 0 0 7px rgba(16,185,129,.08);}}}}
.fc-hero-title{{font-family:'Bricolage Grotesque',sans-serif;font-size:1.70rem;font-weight:800;
    color:#fff;letter-spacing:-0.03em;line-height:1.2;margin-bottom:7px;}}
.fc-hero-sub{{font-size:0.82rem;color:rgba(255,255,255,0.62);font-weight:500;line-height:1.6;}}
.fc-hero-chips{{display:flex;gap:8px;flex-wrap:wrap;margin-top:15px;}}
.fc-chip{{background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.16);
    border-radius:20px;padding:4px 13px;font-size:.65rem;font-weight:700;color:#fff;
    display:inline-flex;align-items:center;gap:5px;}}
 
.fc-steps{{display:flex;align-items:flex-start;background:{CARD};border:1px solid {BOR};
    border-radius:18px;padding:14px 18px;margin-bottom:22px;box-shadow:0 2px 10px rgba(0,0,0,0.07);}}
.fc-step-col{{flex:1;text-align:center;}}
.fc-step-circle{{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;
    justify-content:center;font-size:.88rem;margin:0 auto 5px;transition:all .22s;}}
.fc-step-circle.done{{background:{A1};color:#fff;box-shadow:0 3px 12px rgba(99,102,241,.35);}}
.fc-step-circle.idle{{background:{BOR};color:{SUB};}}
.fc-step-lbl{{font-size:.54rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;}}
.fc-step-lbl.done{{color:{A1};}} .fc-step-lbl.idle{{color:{SUB};}}
.fc-step-bar{{flex:0 0 20px;height:2px;border-radius:2px;margin-top:16px;transition:background .22s;}}
.fc-step-bar.done{{background:{A1};}} .fc-step-bar.idle{{background:{BOR};}}
 
.fc-sec{{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.10em;
    color:{SUB};margin:24px 0 11px;display:flex;align-items:center;gap:9px;}}
.fc-sec::before{{content:'';width:3px;height:13px;
    background:linear-gradient(180deg,{A1},{A2});border-radius:99px;flex-shrink:0;}}
.fc-sec::after{{content:'';flex:1;height:1px;background:linear-gradient(to right,{BOR},transparent);}}
 
.fc-voice-wrap{{background:{"rgba(99,102,241,0.05)" if dark else "#F7F5FF"};
    border:1.5px solid {"rgba(99,102,241,0.16)" if dark else "#DDD6FE"};border-radius:20px;overflow:hidden;}}
.fc-voice-captured{{background:{GRN_BG};border:1.5px solid {GRN_BD};border-left:4px solid {GRN};
    border-radius:14px;padding:12px 15px;margin:8px 0;animation:fc-fade-up .2s ease both;}}
.fc-voice-captured-lbl{{font-size:.58rem;font-weight:700;text-transform:uppercase;
    letter-spacing:.08em;color:{GRN_T};margin-bottom:5px;}}
.fc-voice-captured-txt{{font-size:.80rem;color:{TXT};line-height:1.6;word-break:break-word;
    font-style:italic;margin-bottom:10px;}}
 
/* ── CATEGORY ── */
.fc-cat-cell .stButton>button{{
    background:{CARD}!important;border:1.5px solid {BOR}!important;
    border-radius:15px!important;padding:14px 6px 11px!important;
    text-align:center!important;width:100%!important;min-height:72px!important;
    display:flex!important;flex-direction:column!important;align-items:center!important;
    justify-content:center!important;gap:5px!important;font-size:.70rem!important;
    font-weight:700!important;color:{TXT}!important;line-height:1.25!important;
    transition:all .18s ease!important;box-shadow:none!important;}}
.fc-cat-cell .stButton>button:hover{{
    border-color:{A1}!important;transform:translateY(-2px)!important;
    box-shadow:0 6px 18px rgba(99,102,241,0.14)!important;
    background:{"rgba(99,102,241,0.07)" if dark else "#F5F3FF"}!important;}}
.fc-cat-active .stButton>button{{
    background:{"rgba(99,102,241,0.14)" if dark else "#EEF2FF"}!important;
    border:2px solid {A1}!important;box-shadow:0 0 0 4px rgba(99,102,241,0.13)!important;
    color:{"#818CF8" if dark else "#3730A3"}!important;}}
 
/* ── GPS LOCATION PILL ── */
.fc-gps-pill{{background:{GRN_BG};border:1.5px solid {GRN_BD};border-left:4px solid {GRN};
    border-radius:12px;padding:10px 14px;margin-bottom:10px;
    display:flex;align-items:flex-start;gap:10px;animation:fc-fade-up .2s ease both;}}
.fc-gps-pill-icon{{font-size:1.1rem;flex-shrink:0;margin-top:1px;}}
.fc-gps-pill-body{{flex:1;}}
.fc-gps-pill-lbl{{font-size:.56rem;font-weight:700;text-transform:uppercase;
    letter-spacing:.08em;color:{GRN_T};margin-bottom:3px;}}
.fc-gps-pill-name{{font-size:.82rem;font-weight:600;color:{TXT};line-height:1.45;}}
.fc-gps-pill-coords{{font-size:.62rem;color:{SUB};margin-top:3px;font-family:'DM Mono',monospace;}}
 
/* ── EMERGENCY ── */
.fc-emg{{background:{"rgba(239,68,68,0.07)" if dark else "#FFF1F2"};
    border:1.5px solid {"rgba(239,68,68,0.18)" if dark else "#FECDD3"};
    border-radius:18px;padding:16px 18px;margin:16px 0 6px;}}
.fc-emg-title{{font-size:.62rem;font-weight:800;text-transform:uppercase;
    letter-spacing:.10em;color:#EF4444;margin-bottom:10px;}}
.fc-emg-warn{{background:rgba(239,68,68,0.10);border:1px solid rgba(239,68,68,0.18);
    border-radius:10px;padding:8px 12px;font-size:.76rem;color:#EF4444;font-weight:600;margin-top:8px;}}
 
.fc-ai{{background:{CARD};border:1.5px solid {"rgba(99,102,241,0.18)" if dark else "#C7D2FE"};
    border-left:4px solid {A1};border-radius:18px;padding:15px 18px;margin-top:12px;
    animation:fc-fade-up .22s ease both;}}
.fc-ai-head{{display:flex;align-items:center;gap:10px;margin-bottom:10px;}}
.fc-ai-icon{{width:28px;height:28px;background:linear-gradient(135deg,{A1},{A2});
    border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.82rem;}}
.fc-ai-lbl{{font-size:.60rem;font-weight:800;text-transform:uppercase;letter-spacing:.10em;color:{A1};}}
.fc-ai-pills{{display:flex;gap:8px;flex-wrap:wrap;}}
.fc-ai-pill{{border-radius:10px;padding:6px 11px;display:flex;align-items:center;
    gap:5px;font-size:.76rem;font-weight:700;border:1.5px solid;}}
.fc-ai-hint{{font-size:.65rem;color:{SUB};margin-top:8px;font-style:italic;}}
 
.fc-photo-wrap{{background:{"rgba(99,102,241,0.04)" if dark else "#F9FAFB"};
    border:2px dashed {"rgba(99,102,241,0.20)" if dark else "#C7D2FE"};
    border-radius:18px;padding:16px 18px;}}
.fc-photo-head{{display:flex;align-items:center;gap:12px;margin-bottom:12px;}}
.fc-photo-icon{{width:44px;height:44px;background:linear-gradient(135deg,{A1},{A2});
    border-radius:13px;display:flex;align-items:center;justify-content:center;
    font-size:1.3rem;flex-shrink:0;box-shadow:0 4px 12px rgba(99,102,241,.28);}}
.fc-photo-title{{font-size:.82rem;font-weight:800;color:{"#818CF8" if dark else "#3730A3"};}}
.fc-photo-sub{{font-size:.64rem;color:{SUB};margin-top:2px;}}
 
.fc-checklist{{background:{CARD};border:1px solid {BOR};border-radius:14px;
    padding:12px 16px;margin:12px 0 14px;}}
.fc-checklist-title{{font-size:.60rem;font-weight:700;text-transform:uppercase;
    letter-spacing:.09em;color:{SUB};margin-bottom:9px;}}
.fc-checks{{display:flex;gap:7px;flex-wrap:wrap;}}
.fc-check{{background:{"rgba(255,255,255,0.04)" if dark else "#F8FAFF"};
    border:1px solid {BOR};border-radius:9px;padding:5px 11px;font-size:.72rem;
    font-weight:600;color:{SUB};display:inline-flex;align-items:center;gap:5px;}}
.fc-check.ok{{background:{GRN_BG};border-color:{GRN_BD};color:{GRN_T};}}
 
.fc-tip{{background:{CARD};border:1px solid {BOR};border-radius:13px;
    padding:11px 16px;display:flex;align-items:flex-start;gap:10px;
    margin:10px 0 16px;font-size:.75rem;color:{SUB};line-height:1.55;}}
.fc-tip strong{{color:{TXT};}}
 
.fc-err{{background:{RED_BG};border:1.5px solid {RED_BD};border-radius:13px;
    padding:11px 16px;margin-top:8px;color:{RED_T};font-weight:600;font-size:.80rem;}}
 
.fc-success{{background:linear-gradient(135deg,#064e3b 0%,#059669 55%,#047857 100%);
    border-radius:24px;padding:40px 28px;text-align:center;color:#fff;
    box-shadow:0 20px 56px rgba(16,185,129,0.38);margin-top:12px;animation:fc-fade-up .30s ease both;}}
.fc-success-ring{{width:72px;height:72px;background:rgba(255,255,255,0.18);border-radius:50%;
    display:inline-flex;align-items:center;justify-content:center;font-size:2.1rem;
    margin-bottom:14px;box-shadow:0 0 0 10px rgba(255,255,255,0.08);}}
.fc-success-title{{font-family:'Bricolage Grotesque',sans-serif;font-size:1.35rem;
    font-weight:800;margin-bottom:4px;letter-spacing:-0.02em;}}
.fc-success-sub{{font-size:.86rem;opacity:.82;margin-bottom:18px;font-weight:500;}}
.fc-success-id{{background:rgba(255,255,255,0.16);border:2px solid rgba(255,255,255,0.30);
    border-radius:13px;padding:11px 22px;display:inline-block;
    font-family:'DM Mono',monospace;font-size:1.55rem;font-weight:800;
    letter-spacing:4px;margin-bottom:16px;}}
.fc-success-chips{{display:flex;justify-content:center;gap:9px;flex-wrap:wrap;margin-bottom:12px;}}
.fc-success-chip{{background:rgba(255,255,255,0.14);border-radius:9px;padding:6px 13px;font-size:.72rem;font-weight:600;}}
.fc-success-note{{font-size:.70rem;opacity:.65;line-height:1.85;}}
 
.fc-offline{{background:{AMB_BG};border:1.5px solid {AMB_BD};border-radius:18px;padding:18px;margin-top:10px;}}
.fc-offline-head{{display:flex;align-items:center;gap:12px;margin-bottom:9px;}}
.fc-offline-icon{{width:44px;height:44px;background:{"rgba(245,158,11,0.18)" if dark else "#FDE68A"};
    border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;}}
.fc-offline-title{{font-weight:800;color:{AMB_T};font-size:.90rem;}}
.fc-offline-sub{{font-size:.70rem;color:{AMB_T};opacity:.78;margin-top:2px;}}
.fc-offline-body{{background:rgba(255,255,255,0.08);border-radius:10px;
    padding:10px 12px;font-size:.74rem;color:{AMB_T};line-height:1.65;}}
 
/* Streamlit native overrides */
.stTextInput>div>div>input,.stTextArea>div>div>textarea{{
    background:{INP}!important;border:1.5px solid {BOR}!important;
    border-radius:13px!important;color:{TXT}!important;
    font-size:.875rem!important;padding:10px 14px!important;
    transition:border-color .15s,box-shadow .15s!important;font-family:'DM Sans',sans-serif!important;}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{{
    border-color:{A1}!important;box-shadow:0 0 0 3px rgba(99,102,241,0.12)!important;
    background:{CARD}!important;outline:none!important;}}
.stTextInput>div>div>input::placeholder,.stTextArea>div>div>textarea::placeholder{{
    color:{SUB}!important;opacity:.60!important;}}
.stTextInput label,.stTextArea label,.stFileUploader label{{
    color:{SUB}!important;font-size:.64rem!important;font-weight:600!important;
    text-transform:uppercase!important;letter-spacing:.08em!important;}}
.stCheckbox label{{text-transform:none!important;font-size:.85rem!important;
    letter-spacing:0!important;color:{TXT}!important;font-weight:500!important;}}
.stFileUploader>div{{background:{INP}!important;
    border:1.5px dashed {"rgba(99,102,241,0.22)" if dark else "#C7D2FE"}!important;
    border-radius:14px!important;padding:14px!important;}}
 
.fc-submit-col .stButton>button{{
    background:linear-gradient(135deg,{A1},{A2})!important;color:#fff!important;
    border:none!important;border-radius:18px!important;padding:14px 28px!important;
    font-size:.95rem!important;font-weight:700!important;letter-spacing:-.01em!important;
    box-shadow:0 6px 22px rgba(99,102,241,0.38)!important;
    transition:transform .18s,box-shadow .18s,filter .15s!important;}}
.fc-submit-col .stButton>button:hover{{transform:translateY(-2px)!important;
    box-shadow:0 10px 32px rgba(99,102,241,0.50)!important;filter:brightness(1.06)!important;}}
.fc-submit-col .stButton>button:active{{transform:translateY(0) scale(.985)!important;filter:brightness(.96)!important;}}
 
@media(max-width:640px){{
    .fc-hero{{padding:22px 16px 18px;border-radius:18px;}}
    .fc-hero-title{{font-size:1.35rem;}}
    .fc-cat-cell{{}}
    .main .block-container{{padding:1rem .75rem 3rem!important;}}
    .fc-steps{{padding:10px 10px;}}
}}
</style>"""
    st.markdown(css, unsafe_allow_html=True)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# VOICE IFRAME  (unchanged from v4 — record-again works inside iframe)
# ─────────────────────────────────────────────────────────────────────────────
 
@st.cache_data(show_spinner=False)
def _voice_iframe_html(lang_code: str) -> str:
    ext_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "components", "voice_component.html",
    )
    if os.path.exists(ext_path):
        with open(ext_path, "r", encoding="utf-8") as f:
            return f.read().replace("%LANG%", lang_code)
 
    is_hi = "hi" in lang_code
    tap   = "बोलने के लिए दबाएं" if is_hi else "Tap to speak"
    lst   = "🎙️ सुन रहा हूँ…"    if is_hi else "🎙️ Listening…"
    dn    = "✅ हो गया!"            if is_hi else "✅ Done"
    nth   = "❌ कुछ नहीं सुना"     if is_hi else "❌ Nothing heard"
    use   = "✅ उपयोग करें"        if is_hi else "✅ Use This Text"
    again = "🔄 दोबारा रिकॉर्ड करें" if is_hi else "🔄 Record Again"
    live  = "लाइव ट्रांसक्रिप्ट"   if is_hi else "Live Transcript"
 
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'DM Sans','Segoe UI',system-ui,sans-serif;background:transparent;}}
.vc{{padding:18px 16px 14px;text-align:center;}}
.vc-hdr{{font-size:.58rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;
  color:#818CF8;margin-bottom:14px;display:flex;align-items:center;justify-content:center;gap:8px;}}
.vc-hdr::before,.vc-hdr::after{{content:'';flex:1;height:1px;background:rgba(99,102,241,.20);}}
#vbtn{{background:linear-gradient(135deg,#EC4899,#8B5CF6);color:#fff;border:none;
  border-radius:50%;width:64px;height:64px;font-size:1.65rem;cursor:pointer;
  display:inline-flex;align-items:center;justify-content:center;
  box-shadow:0 6px 22px rgba(139,92,246,.45);transition:all .18s;}}
#vbtn:hover{{transform:scale(1.08);}}
.wf{{display:none;align-items:center;justify-content:center;gap:3px;height:26px;margin:8px auto 0;}}
.wb{{width:3px;background:#818CF8;border-radius:99px;animation:wv 1.1s ease-in-out infinite;}}
.wb:nth-child(1){{height:8px;}} .wb:nth-child(2){{height:14px;animation-delay:.10s;}}
.wb:nth-child(3){{height:22px;animation-delay:.20s;}} .wb:nth-child(4){{height:16px;animation-delay:.30s;}}
.wb:nth-child(5){{height:26px;animation-delay:.40s;}} .wb:nth-child(6){{height:16px;animation-delay:.50s;}}
.wb:nth-child(7){{height:9px;animation-delay:.60s;}}
@keyframes wv{{0%,100%{{transform:scaleY(.4);opacity:.5;}}50%{{transform:scaleY(1);opacity:1;}}}}
#vstatus{{font-size:.73rem;color:#8892AA;margin:10px 0 4px;font-weight:500;min-height:18px;}}
.vt{{display:none;background:rgba(99,102,241,.06);border:1px solid rgba(99,102,241,.18);
  border-radius:12px;padding:11px 13px;margin-top:10px;text-align:left;}}
.vtlbl{{font-size:.56rem;font-weight:800;text-transform:uppercase;letter-spacing:.10em;
  color:#818CF8;margin-bottom:5px;display:flex;align-items:center;gap:5px;}}
.vdot{{width:6px;height:6px;border-radius:50%;background:#EC4899;animation:dp .9s infinite;flex-shrink:0;display:none;}}
@keyframes dp{{0%,100%{{opacity:1;transform:scale(1);}}50%{{opacity:.3;transform:scale(.6);}}}}
#vi{{color:rgba(200,210,255,.40);font-style:italic;font-size:.78rem;min-height:14px;line-height:1.55;}}
#vf{{font-weight:600;color:#EFF2FF;font-size:.82rem;line-height:1.6;margin-top:4px;word-break:break-word;}}
.vactions{{display:none;margin-top:10px;gap:8px;}}
#vub{{flex:1;background:linear-gradient(135deg,#6366F1,#818CF8);color:#fff;border:none;
  border-radius:9px;padding:9px 0;font-size:.76rem;font-weight:800;cursor:pointer;
  box-shadow:0 4px 14px rgba(99,102,241,.38);transition:all .15s;font-family:'DM Sans',sans-serif;}}
#vub:hover{{transform:translateY(-2px);}}
#vagain{{flex:1;background:rgba(99,102,241,.12);color:#818CF8;
  border:1.5px solid rgba(99,102,241,.25);border-radius:9px;padding:9px 0;
  font-size:.76rem;font-weight:700;cursor:pointer;transition:all .15s;font-family:'DM Sans',sans-serif;}}
#vagain:hover{{background:rgba(99,102,241,.22);transform:translateY(-2px);}}
@keyframes mp{{0%{{box-shadow:0 0 0 0 rgba(236,72,153,.65);}}
  70%{{box-shadow:0 0 0 18px rgba(236,72,153,0);}}100%{{box-shadow:0 0 0 0 rgba(236,72,153,0);}}}}
.rec{{animation:mp 1.1s ease-in-out infinite!important;background:linear-gradient(135deg,#EF4444,#F87171)!important;}}
</style></head>
<body><div class="vc">
<div class="vc-hdr">🎤 Voice Input</div>
<button id="vbtn" onclick="toggleV()">🎤</button>
<div class="wf" id="wf">
  <div class="wb"></div><div class="wb"></div><div class="wb"></div>
  <div class="wb"></div><div class="wb"></div><div class="wb"></div><div class="wb"></div>
</div>
<div id="vstatus">{tap}</div>
<div class="vt" id="vt">
  <div class="vtlbl"><span class="vdot" id="vdot"></span>📝 {live}</div>
  <div id="vi"></div><div id="vf"></div>
</div>
<div class="vactions" id="vactions">
  <button id="vagain" onclick="doAgain()">{again}</button>
  <button id="vub"    onclick="sendUp()">{use}</button>
</div>
</div>
<script>
var cap='',rec=null,running=false;
function toggleV(){{running?stopV():startV();}}
function startV(){{
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){{setSt('❌ Browser not supported','#EF4444');return;}}
  cap='';
  document.getElementById('vi').textContent='';
  document.getElementById('vf').textContent='';
  document.getElementById('vactions').style.display='none';
  document.getElementById('vt').style.display='block';
  rec=new SR();rec.lang='{lang_code}';rec.continuous=true;rec.interimResults=true;
  rec.onresult=function(e){{
    var interim='',final_='';
    for(var i=0;i<e.results.length;i++){{
      if(e.results[i].isFinal)final_+=e.results[i][0].transcript+' ';
      else interim+=e.results[i][0].transcript;
    }}
    document.getElementById('vi').textContent=interim;
    document.getElementById('vf').textContent=final_;
    cap=(final_+interim).trim();
  }};
  rec.onerror=function(e){{setSt('❌ '+e.error,'#EF4444');setIdle();}};
  rec.onend=function(){{
    if(running){{try{{rec.start();}}catch(e){{setIdle();}}return;}}
    setIdle();
    if(cap){{document.getElementById('vdot').style.display='none';
      document.getElementById('vactions').style.display='flex';setSt('{dn}','#10B981');}}
    else{{document.getElementById('vt').style.display='none';setSt('{nth}','#EF4444');}}
  }};
  try{{rec.start();}}catch(e){{setSt('❌ Could not start mic','#EF4444');return;}}
  running=true;
  var btn=document.getElementById('vbtn');
  btn.textContent='⏹️';btn.classList.add('rec');
  document.getElementById('wf').style.display='flex';
  document.getElementById('vdot').style.display='inline-block';
  setSt('{lst}','#F59E0B');
}}
function stopV(){{running=false;if(rec)try{{rec.stop();}}catch(e){{}}}}
function setIdle(){{
  running=false;
  var btn=document.getElementById('vbtn');
  btn.textContent='🎤';btn.classList.remove('rec');
  document.getElementById('wf').style.display='none';
  document.getElementById('vdot').style.display='none';
}}
function setSt(t,c){{var e=document.getElementById('vstatus');e.textContent=t;if(c)e.style.color=c;}}
function doAgain(){{
  cap='';
  document.getElementById('vi').textContent='';
  document.getElementById('vf').textContent='';
  document.getElementById('vactions').style.display='none';
  document.getElementById('vt').style.display='none';
  setSt('{tap}','#8892AA');
  startV();
}}
function sendUp(){{
  if(!cap)return;
  window.parent.postMessage({{type:'VOICE_RESULT',text:cap}},'*');
  setSt('✅ Sent to form!','#10B981');
  document.getElementById('vactions').style.display='none';
}}
</script></body></html>"""
 
 
@st.cache_data(show_spinner=False)
def _bridge_iframe_html() -> str:
    """
    postMessage bridge.
    ROOT CAUSE FIX: The old 'window._voiceBridgeInstalled' guard persisted
    across reruns in the parent frame. After Clear & Re-record, the bridge
    was already 'installed' so it ignored the new voice message.
 
    FIX: Replace the guard with a timestamp-based debounce (500ms).
    The listener is re-added on every bridge render (which is fine — it
    replaces itself). Multiple fires within 500ms are collapsed to one.
    This means Clear & Re-record always works regardless of how many times
    the user records.
    """
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head><body>
<script>
(function(){
  // Remove any previous listener to avoid duplicates from rerenders
  if(window._voiceBridgeFn) {
    window.removeEventListener('message', window._voiceBridgeFn);
  }
  var lastSent = 0;
  window._voiceBridgeFn = function(ev) {
    if(!ev.data || ev.data.type !== 'VOICE_RESULT') return;
    var text = (ev.data.text || '').trim();
    if(!text) return;
    // Debounce: ignore duplicate fires within 500ms
    var now = Date.now();
    if(now - lastSent < 500) return;
    lastSent = now;
    var u = new URL(window.parent.location.href);
    u.searchParams.set('voice_text', encodeURIComponent(text));
    window.parent.history.pushState({}, '', u);
    window.parent.dispatchEvent(new PopStateEvent('popstate', {state:{}}));
  };
  window.addEventListener('message', window._voiceBridgeFn);
})();
</script></body></html>"""
 
 
# ─────────────────────────────────────────────────────────────────────────────
# GPS IFRAME  (FIX 4 — does reverse geocode in JS, sends name + coords)
# ─────────────────────────────────────────────────────────────────────────────
 
@st.cache_data(show_spinner=False)
def _gps_iframe_html(label: str) -> str:
    """
    GPS button that:
    1. Gets browser coordinates
    2. Reverse-geocodes via Nominatim IN JS (no extra Python call)
    3. Sends ALL structured fields as separate URL params:
       gps_lat, gps_lon, gps_name (display), gps_area, gps_city,
       gps_district, gps_state, gps_pincode
    Python reads each field individually so the map card can show
    structured rows instead of one merged string.
    """
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'DM Sans',sans-serif;background:transparent;}}
#gpsbtn{{background:linear-gradient(135deg,#06b6d4,#6366F1);color:#fff;border:none;
  border-radius:13px;width:100%;height:49px;font-size:.78rem;font-weight:700;
  cursor:pointer;box-shadow:0 4px 14px rgba(6,182,212,.28);
  transition:transform .18s,box-shadow .18s;}}
#gpsbtn:hover{{transform:translateY(-2px);box-shadow:0 7px 22px rgba(6,182,212,.42);}}
#gpsbtn:disabled{{opacity:.55;cursor:not-allowed;transform:none;}}
#gpsst{{font-size:.60rem;text-align:center;margin-top:6px;color:#64748B;
  min-height:34px;line-height:1.45;word-break:break-word;padding:0 2px;}}
</style></head><body>
<button id="gpsbtn" onclick="doGPS()">📍 GPS</button>
<div id="gpsst">{label}</div>
<script>
function doGPS(){{
  var btn = document.getElementById('gpsbtn');
  var s   = document.getElementById('gpsst');
  btn.disabled = true;
  s.textContent = '⏳ Getting location…';
  s.style.color = '#d97706';
 
  if(!navigator.geolocation){{
    s.textContent = '❌ Geolocation not supported';
    s.style.color = '#dc2626';
    btn.disabled = false;
    return;
  }}
 
  navigator.geolocation.getCurrentPosition(
    function(pos){{
      var lat = pos.coords.latitude;
      var lon = pos.coords.longitude;
      s.textContent = '📍 Fetching area name…';
      s.style.color = '#10b981';
 
      fetch(
        'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=' + lat +
        '&lon=' + lon + '&zoom=18&addressdetails=1',
        {{ headers: {{'User-Agent': 'JanSevaPortal/1.0'}} }}
      )
      .then(function(r){{ return r.ok ? r.json() : null; }})
      .then(function(data){{
        var area='', city='', district='', state='', pin='';
        if(data && data.address){{
          var a = data.address;
          area     = a.neighbourhood || a.suburb || a.village || a.hamlet || a.residential || '';
          city     = a.city || a.town || '';
          district = a.county || a.district || a.state_district || '';
          state    = a.state || '';
          pin      = a.postcode || '';
        }}
        // Build display string
        var parts = [area, city, district, state].filter(function(p){{ return p && p.trim(); }});
        var base  = parts.length ? parts.join(', ') : (lat.toFixed(5) + ', ' + lon.toFixed(5));
        var disp  = pin ? base + ' — ' + pin : base;
 
        s.textContent = '✅ ' + disp;
        s.style.color = '#10b981';
 
        // Send all fields to parent
        var u = new URL(window.parent.location.href);
        u.searchParams.set('gps_lat',      lat);
        u.searchParams.set('gps_lon',      lon);
        u.searchParams.set('gps_name',     encodeURIComponent(disp));
        u.searchParams.set('gps_area',     encodeURIComponent(area));
        u.searchParams.set('gps_city',     encodeURIComponent(city));
        u.searchParams.set('gps_district', encodeURIComponent(district));
        u.searchParams.set('gps_state',    encodeURIComponent(state));
        u.searchParams.set('gps_pincode',  encodeURIComponent(pin));
        window.parent.history.pushState({{}}, '', u);
        window.parent.dispatchEvent(new PopStateEvent('popstate', {{state:{{}}}}));
        btn.disabled = false;
      }})
      .catch(function(){{
        // Geocode failed — send raw coords only
        var disp = lat.toFixed(5) + ', ' + lon.toFixed(5);
        s.textContent = '✅ Location detected';
        s.style.color = '#10b981';
        var u = new URL(window.parent.location.href);
        u.searchParams.set('gps_lat',  lat);
        u.searchParams.set('gps_lon',  lon);
        u.searchParams.set('gps_name', encodeURIComponent(disp));
        window.parent.history.pushState({{}}, '', u);
        window.parent.dispatchEvent(new PopStateEvent('popstate', {{state:{{}}}}));
        btn.disabled = false;
      }});
    }},
    function(err){{
      s.textContent = '❌ ' + err.message;
      s.style.color = '#dc2626';
      btn.disabled = false;
    }},
    {{ timeout: 12000, enableHighAccuracy: true }}
  );
}}
</script></body></html>"""
 
 
def _map_html(lat: float, lon: float, dark: bool,
              area: str = "", city: str = "", district: str = "",
              state: str = "", pincode: str = "", display: str = "") -> str:
    """
    Leaflet map with a rich popup showing all location fields:
    Area / Neighbourhood, City, District, State, PIN Code.
    Falls back to raw display string if structured fields are empty.
    """
    bc = "#1E2A3D" if dark else "#E2E8F4"
 
    # Build popup HTML rows — only non-empty fields shown
    rows = []
    if area:     rows.append(f"<tr><td style='color:#94A3B8;padding:2px 8px 2px 0;font-size:11px;'>Area</td><td style='font-weight:600;font-size:12px;'>{area}</td></tr>")
    if city:     rows.append(f"<tr><td style='color:#94A3B8;padding:2px 8px 2px 0;font-size:11px;'>City / Town</td><td style='font-weight:600;font-size:12px;'>{city}</td></tr>")
    if district: rows.append(f"<tr><td style='color:#94A3B8;padding:2px 8px 2px 0;font-size:11px;'>District</td><td style='font-weight:600;font-size:12px;'>{district}</td></tr>")
    if state:    rows.append(f"<tr><td style='color:#94A3B8;padding:2px 8px 2px 0;font-size:11px;'>State</td><td style='font-weight:600;font-size:12px;'>{state}</td></tr>")
    if pincode:  rows.append(f"<tr><td style='color:#94A3B8;padding:2px 8px 2px 0;font-size:11px;'>PIN Code</td><td style='font-weight:600;font-size:12px;letter-spacing:.04em;'>{pincode}</td></tr>")
 
    if rows:
        popup_inner = (
            "<div style='font-family:sans-serif;min-width:170px;'>"
            "<div style='font-size:13px;font-weight:700;margin-bottom:6px;color:#1E293B;'>"
            "📍 Your Location</div>"
            "<table style='border-collapse:collapse;'>" + "".join(rows) + "</table>"
            "</div>"
        )
    else:
        # No structured data — show plain display string or coords
        label = display or f"{lat:.5f}, {lon:.5f}"
        # Escape single quotes for JS string safety
        label = label.replace("'", "\\'").replace('"', '\\"')
        popup_inner = (
            "<div style='font-family:sans-serif;'>"
            "<b style='font-size:13px;'>📍 Your Location</b>"
            f"<div style='font-size:12px;color:#475569;margin-top:4px;'>{label}</div>"
            "</div>"
        )
 
    # Escape the popup HTML for embedding in a JS string
    popup_js = popup_inner.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "")
 
    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/>"
        f"<style>"
        f"body{{margin:0;padding:0;}}"
        f"#cmap{{height:230px;border-radius:16px;overflow:hidden;"
        f"border:1.5px solid {bc};box-shadow:0 4px 18px rgba(15,23,42,.08);}}"
        f".leaflet-popup-content-wrapper{{border-radius:12px!important;"
        f"box-shadow:0 8px 28px rgba(0,0,0,.15)!important;padding:4px!important;}}"
        f".leaflet-popup-content{{margin:10px 14px!important;}}"
        f"</style>"
        f"</head><body><div id='cmap'></div>"
        f"<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>"
        f"<script>(function(){{"
        f"var m=L.map('cmap',{{zoomControl:true,attributionControl:false}}).setView([{lat},{lon}],16);"
        f"L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',"
        f"{{maxZoom:19,subdomains:['a','b','c']}}).addTo(m);"
        # Custom pin marker
        f"var ic=L.divIcon({{className:'',"
        f"html:'<div style=\"position:relative;width:36px;height:44px;\">"
        f"<div style=\"width:36px;height:36px;"
        f"background:linear-gradient(135deg,#6366F1,#8B5CF6);"
        f"border-radius:50% 50% 50% 0;transform:rotate(-45deg);"
        f"border:3px solid #fff;box-shadow:0 4px 16px rgba(99,102,241,.55);\"></div>"
        f"<div style=\"position:absolute;top:5px;left:50%;transform:translateX(-50%);"
        f"font-size:14px;\">📍</div></div>',"
        f"iconSize:[36,44],iconAnchor:[18,44],popupAnchor:[0,-44]}});"
        f"L.marker([{lat},{lon}],{{icon:ic}}).addTo(m)"
        f".bindPopup('{popup_js}',{{maxWidth:280}}).openPopup();"
        f"}})();</script></body></html>"
    )
 
 
# ─────────────────────────────────────────────────────────────────────────────
# RENDER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
 
def _render_hero(lang: str) -> None:
    title  = "File a Complaint"  if lang == "en" else "शिकायत दर्ज करें"
    sub    = ("Speak or type — AI routes it to the right department instantly."
               if lang == "en" else "बोलें या टाइप करें — AI तुरंत सही विभाग को भेजेगा।")
    v_lbl  = "Voice"      if lang == "en" else "आवाज़"
    e_lbl  = "Emergency"  if lang == "en" else "आपातकाल"
    ai_lbl = "AI-Powered" if lang == "en" else "AI सहायता"
    st.markdown(
        "<div class='fc-hero'>"
        "<div class='fc-hero-eyebrow'><span class='fc-hero-dot'></span>" + ai_lbl + "</div>"
        "<div class='fc-hero-title'>📢 " + title + "</div>"
        "<div class='fc-hero-sub'>" + sub + "</div>"
        "<div class='fc-hero-chips'>"
        "<span class='fc-chip'>🎤 " + v_lbl + "</span>"
        "<span class='fc-chip'>📍 GPS</span>"
        "<span class='fc-chip'>🤖 AI</span>"
        "<span class='fc-chip'>🚨 " + e_lbl + "</span>"
        "</div></div>",
        unsafe_allow_html=True,
    )
 
 
def _render_steps(lang: str, step: int) -> None:
    labels = (["Voice","Category","Location","Photo","Submit"]
              if lang == "en" else ["आवाज़","श्रेणी","स्थान","फोटो","जमा"])
    icons  = ["🎤","📂","📍","📷","🚀"]
    html   = "<div class='fc-steps'>"
    for i, (ic, lb) in enumerate(zip(icons, labels)):
        cls = "done" if i <= step else "idle"
        html += (
            "<div class='fc-step-col'>"
            "<div class='fc-step-circle " + cls + "'>" + ic + "</div>"
            "<div class='fc-step-lbl " + cls + "'>" + lb + "</div>"
            "</div>"
        )
        if i < 4:
            html += "<div class='fc-step-bar " + ("done" if i < step else "idle") + "'></div>"
    st.markdown(html + "</div>", unsafe_allow_html=True)
 
 
def _render_sec(icon: str, label: str) -> None:
    st.markdown("<div class='fc-sec'>" + icon + " " + label + "</div>", unsafe_allow_html=True)
 
def _render_voice(lang: str):
    """
    Voice section — iframe recorder + bridge + Streamlit-side result display.
 
    FLOW:
      1. User clicks mic in iframe → speaks → clicks "Use This Text"
         → postMessage → bridge writes to URL param → _ingest_query_params()
         picks it up on next rerun → fc["voice_text"] = captured text
         → fc["description"] = same text → desc textarea pre-filled
      2. "Clear & Re-record" button resets fc voice state → st.rerun()
         so the iframe shows clean initial state again.
    """
    import html as _html_mod
 
    lang_code = "hi-IN" if lang == "hi" else "en-IN"
    lbl = "Voice Input" if lang == "en" else "आवाज़ इनपुट"
    _render_sec("🎤", lbl)
 
    # ── iframe (stable — cached, never remounts unless lang changes) ──────
    st.markdown("<div class='fc-voice-wrap'>", unsafe_allow_html=True)
    st.components.v1.html(_voice_html(lang_code), height=260)
    st.markdown("</div>", unsafe_allow_html=True)
 
    # ── bridge (zero-height, catches postMessage from iframe) ─────────────
    st.components.v1.html(_bridge_html(), height=0)
 
    # ── Streamlit-side: show captured text + action buttons ───────────────
    vt = fc()["voice_text"]
    if vt:
        dark  = st.session_state.get("dark_mode", False)
        _GRN_BG = "rgba(16,185,129,0.08)" if dark else "#F0FDF4"
        _GRN_BD = "rgba(16,185,129,0.22)" if dark else "#A7F3D0"
        _GRN_T  = "#4ADE80" if dark else "#166534"
        _TXT    = "#EFF2FF" if dark else "#0B1428"
        _A1     = "#6366F1"

        cap_lbl   = "Voice Captured — you can edit this text below" if lang == "en" else "आवाज़ कैप्चर — नीचे संपादित कर सकते हैं"
        
        clear_note = (                                           # ← inside if vt:
            "🎙️ If the complaint is wrong, speak again"
            if lang == "en"
            else "🎙️ अगर शिकायत गलत है तो फिर से बोलें"
        )
        clear_lbl = (
            "Update"
            if lang == "en"
            else "अपडेट करें"
        )
        edit_note = "✅ This text has been filled in the description below — edit freely." if lang == "en" else "✅ यह टेक्स्ट नीचे विवरण में भरा गया है — स्वतंत्र रूप से संपादित करें।"

        # pill showing full captured text
        safe_vt = _html_mod.escape(vt)
        pill_html = (
            "<div style='background:" + _GRN_BG + ";border:1.5px solid " + _GRN_BD + ";"
            "border-left:4px solid #10B981;border-radius:14px;padding:13px 16px;margin:8px 0;'>"
            "<div style='font-size:.58rem;font-weight:700;text-transform:uppercase;"
            "letter-spacing:.08em;color:" + _GRN_T + ";margin-bottom:6px;"
            "display:flex;align-items:center;gap:6px;'>"
            "🎤 " + cap_lbl +
            "</div>"
            "<div style='font-size:.83rem;color:" + _TXT + ";line-height:1.65;"
            "word-break:break-word;'>" + safe_vt + "</div>"
            "</div>"
        )
        st.markdown(pill_html, unsafe_allow_html=True)

        # action row
        ca, cb = st.columns([1, 3])
        with ca:
            st.caption(clear_note)                               # ← inside if vt: → with ca:
            if st.button(clear_lbl, key="fc_voice_clear", use_container_width=True):
                fc_set(
                    voice_text      = "",
                    description     = "",
                    voice_applied   = False,
                    _voice_ingested = False,
                )
                if "_fc_desc" in st.session_state:
                    del st.session_state["_fc_desc"]
                st.rerun()
        with cb:
            st.markdown(
                "<div style='font-size:.74rem;color:" + _GRN_T + ";"
                "padding:6px 4px;line-height:1.5;'>" + edit_note + "</div>",
                unsafe_allow_html=True,
            )

        if "_fc_desc" not in st.session_state or st.session_state.get("_fc_desc") == "":
            st.session_state["_fc_desc"] = vt
 
 
 
def _render_category(lang: str) -> None:

    # ───��─────────────────────────────────────────
    # FETCH DYNAMIC CATEGORIES
    # ─────────────────────────────────────────────

    try:

        resp = api("get", "/categories")

        dynamic_categories = resp.get(
            "categories",
            []
        )

    except Exception:

        dynamic_categories = []

    # ─────────────────────────────────────────────
    # FALLBACK DEFAULTS
    # ─────────────────────────────────────────────

    if not dynamic_categories:

        dynamic_categories = [

            "water",
            "electricity",
            "road",
            "waste",
            "drainage",
            "health",
            "other",
        ]

    # Remove duplicates
    dynamic_categories = sorted(
        list(set(dynamic_categories))
    )

    # ─────────────────────────────────────────────
    # AUTO CATEGORY LABEL + ICON
    # ─────────────────────────────────────────────

    def get_category_display(category):

        category = str(category).lower().strip()

        AUTO_MAP = {

            "water": (
                "💧",
                "Water" if lang == "en" else "पानी"
            ),

            "electricity": (
                "⚡",
                "Electricity" if lang == "en" else "बिजली"
            ),

            "road": (
                "🛣️",
                "Road" if lang == "en" else "सड़क"
            ),

            "waste": (
                "🗑️",
                "Waste" if lang == "en" else "कचरा"
            ),

            "drainage": (
                "🌊",
                "Drainage" if lang == "en" else "नाला"
            ),

            "health": (
                "🏥",
                "Health" if lang == "en" else "स्वास्थ्य"
            ),

            "cyber": (
                "💻",
                "Cyber Crime"
                if lang == "en"
                else "साइबर अपराध"
            ),

            "internet": (
                "🌐",
                "Internet"
                if lang == "en"
                else "इंटरनेट"
            ),

            "telecom": (
                "📡",
                "Telecom"
                if lang == "en"
                else "टेलीकॉम"
            ),

            "transport": (
                "🚌",
                "Transport"
                if lang == "en"
                else "परिवहन"
            ),

            "police": (
                "🚓",
                "Police"
                if lang == "en"
                else "पुलिस"
            ),

            "fire": (
                "🔥",
                "Fire Service"
                if lang == "en"
                else "फायर सेवा"
            ),

            "tourism": (
                "✈️",
                "Tourism"
                if lang == "en"
                else "पर्यटन"
            ),

            "bank": (
                "🏦",
                "Banking"
                if lang == "en"
                else "बैंकिंग"
            ),

            "finance": (
                "💰",
                "Finance"
                if lang == "en"
                else "वित्त"
            ),

            "education": (
                "🎓",
                "Education"
                if lang == "en"
                else "शिक्षा"
            ),

            "housing": (
                "🏠",
                "Housing"
                if lang == "en"
                else "आवास"
            ),
        }

        for key, value in AUTO_MAP.items():

            if key in category:

                return value

        return (

            "📌",

            category.replace(
                "_",
                " "
            ).title()
        )

    # ─────────────────────────────────────────────
    # SECTION TITLE
    # ─────────────────────────────────────────────

    _render_sec(

        "📂",

        "Select Category"
        if lang == "en"
        else "श्रेणी चुनें"
    )

    # ─────────────────────────────────────────────
    # ACTIVE CATEGORY
    # ─────────────────────────────────────────────

    active = fc()["category"]

    # ─────────────────────────────────────────────
    # GRID SYSTEM
    # ─────────────────────────────────────────────

    col_count = 4

    padded = dynamic_categories + [

        None

    ] * ((-len(dynamic_categories)) % col_count)

    rows = [

        padded[i:i + col_count]

        for i in range(
            0,
            len(padded),
            col_count
        )
    ]

    # ─────────────────────────────────────────────
    # RENDER CATEGORY BUTTONS
    # ─────────────────────────────────────────────

    for row in rows:

        cols = st.columns(
            col_count,
            gap="small"
        )

        for col, category in zip(cols, row):

            if category is None:

                continue

            icon, label = get_category_display(
                category
            )

            cls = (

                "fc-cat-cell fc-cat-active"

                if category == active

                else "fc-cat-cell"
            )

            with col:

                st.markdown(

                    f"<div class='{cls}'>",

                    unsafe_allow_html=True
                )

                def _make_select(cat_key: str):

                    def _select():

                        fc_set(
                            category=cat_key
                        )

                    return _select

                safe_category = re.sub(

                    r"[^a-zA-Z0-9_]",

                    "_",

                    str(category).lower()
                )

                btn_text = f"{icon}  {label}"

                clicked = st.button(

                    btn_text,

                    key=f"fc_cat_{safe_category}",

                    use_container_width=True,
                )

                if clicked:

                    fc_set(
                        category=category
                    )

                    st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )
 
 
def _render_emergency(lang: str) -> None:
    mode_lbl = "Emergency Mode" if lang == "en" else "आपातकालीन मोड"
    chk_lbl  = ("⚠️ This is an emergency (fire, accident, water leakage, etc.)"
                 if lang == "en" else "⚠️ यह आपातकालीन है (आग, दुर्घटना, पानी का रिसाव आदि)")
    warn_txt = ("Emergency complaints receive highest priority and immediate alerts."
                if lang == "en" else "आपातकालीन शिकायतें तुरंत उच्चतम प्राथमिकता पर भेजी जाती हैं।")
 
    def _on_emg(): fc_set(is_emergency=st.session_state["_fc_emergency"])
 
    st.markdown("<div class='fc-emg'><div class='fc-emg-title'>🚨 " + mode_lbl + "</div>",
                unsafe_allow_html=True)
    st.checkbox(chk_lbl, value=fc()["is_emergency"], key="_fc_emergency", on_change=_on_emg)
    if fc()["is_emergency"]:
        st.markdown("<div class='fc-emg-warn'>🚨 " + warn_txt + "</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
 
 
def _render_description(lang: str):
    ph = ("Describe the issue — what happened, where, how severe…"
          if lang == "en" else "समस्या विस्तार से बताएं — क्या हुआ, कहाँ, कितना गंभीर…")
    lbl = "Describe Your Issue" if lang == "en" else "समस्या का विवरण"
    _render_sec("📝", lbl)
 
    def _on_desc():
        fc_set(description=st.session_state["_fc_desc"], voice_applied=False)
 
    default_val = fc()["description"] or fc()["voice_text"]
    st.text_area("", value=default_val, placeholder=ph, key="_fc_desc",
                 height=118, label_visibility="collapsed", on_change=_on_desc)
 
    if fc()["voice_applied"] and fc()["voice_text"]:
        note = "🎤 Voice text applied — edit freely above." if lang=="en" else "🎤 आवाज़ टेक्स्ट लागू — ऊपर संपादित करें।"
        st.markdown(
            "<div style='background:rgba(16,185,129,0.07);border-left:3px solid #10B981;"
            "border-radius:0 10px 10px 0;padding:7px 13px;font-size:.73rem;"
            "color:#059669;margin-top:4px;'>" + note + "</div>",
            unsafe_allow_html=True,
        )
 
 
def _render_ai_preview(lang: str, desc: str, is_emg: bool) -> None:
    if not desc.strip():
        return
 
    def _local(text: str, sel: str) -> tuple[str, str]:

        tl = str(text).lower().strip()

        # ─────────────────────────────────────────
        # DYNAMIC CATEGORY DETECTION
        # ─────────────────────────────────────────

        CATEGORY_KEYWORDS = {

            "water": [
                "water", "पानी", "tap",
                "leak", "pipeline", "jal"
            ],

            "electricity": [
                "electricity", "बिजली",
                "power", "light",
                "transformer", "wire"
            ],

            "road": [
                "road", "सड़क",
                "pothole", "street",
                "bridge", "traffic"
            ],

            "waste": [
                "garbage", "कचरा",
                "waste", "dump",
                "dirty", "cleaning"
            ],

            "drainage": [
                "drain", "नाला",
                "sewer", "flood",
                "drainage"
            ],

            "health": [
                "hospital", "स्वास्थ्य",
                "clinic", "doctor",
                "ambulance"
            ],

            # ─────────────────────────
            # NEW DYNAMIC CATEGORIES
            # ─────────────────────────

            "cybercrime": [
                "cyber", "hack",
                "fraud", "otp",
                "scam", "online fraud"
            ],

            "internet": [
                "internet", "wifi",
                "network", "broadband"
            ],

            "telecom": [
                "telecom", "tower",
                "signal", "mobile network"
            ],

            "transport": [
                "transport", "bus",
                "metro", "auto",
                "train"
            ],

            "police": [
                "police", "crime",
                "theft", "attack",
                "violence"
            ],

            "fire": [
                "fire", "आग",
                "smoke", "burn"
            ],
        }

        # Default category
        cat = sel if sel != "other" else "other"

        # Detect category
        for category, keywords in CATEGORY_KEYWORDS.items():

            if any(word in tl for word in keywords):

                cat = category

                break

        # ─────────────────────────────────────────
        # PRIORITY DETECTION
        # ─────────────────────────────────────────

        urgent_words = [

            "urgent",
            "emergency",
            "critical",
            "fire",
            "injury",
            "collapse",

            "आग",
            "खतरा",
            "तुरंत",
            "आपातकाल"
        ]

        priority = (

            "high"

            if any(word in tl for word in urgent_words)
            or is_emg

            else "medium"
        )

        return cat, priority
 
    try:
        from backend.routers.complaints import ai_classify  # type: ignore[import]
        ai_cat, ai_pri = ai_classify(desc, fc()["category"])
    except Exception:
        ai_cat, ai_pri = _local(desc, fc()["category"])
 
    PRI = {
        "high":   ("#FEF2F2","#BE123C","#FECACA","🔴"),
        "medium": ("#FFFBEB","#B45309","#FDE68A","🟡"),
        "low":    ("#F0FDF4","#166534","#A7F3D0","🟢"),
    }
    pb, pt, pbd, pi = PRI.get(ai_pri, PRI["medium"])
    cat_lbl = "Category" if lang == "en" else "श्रेणी"
    pri_lbl = "Priority"  if lang == "en" else "प्राथमिकता"
    hint    = "Auto-detected — adjust category above if needed." if lang == "en" else "स्वतः पहचाना — ऊपर बदल सकते हैं।"
 
    st.markdown(
        "<div class='fc-ai'>"
        "<div class='fc-ai-head'><div class='fc-ai-icon'>🤖</div>"
        "<span class='fc-ai-lbl'>AI Classification Preview</span></div>"
        "<div class='fc-ai-pills'>"
        "<div class='fc-ai-pill' style='background:rgba(99,102,241,0.09);"
        "border-color:rgba(99,102,241,0.22);color:#3730A3;'>"
        "<span style='font-size:.60rem;opacity:.7;'>" + cat_lbl + "</span> 📂 " + ai_cat.title() + "</div>"
        "<div class='fc-ai-pill' style='background:" + pb + ";border-color:" + pbd + ";color:" + pt + ";'>"
        "<span style='font-size:.60rem;opacity:.7;'>" + pri_lbl + "</span> " + pi + " " + ai_pri.title() + "</div>"
        "</div>"
        "<div class='fc-ai-hint'>✨ " + hint + "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
 
 
def _render_location(lang: str, dark: bool) -> None:
    _render_sec("📍", "Location" if lang == "en" else "स्थान")

    col_gps, col_loc = st.columns([1, 3])
    with col_gps:
        auto_lbl = "Auto-detect" if lang == "en" else "स्थान पता करें"
        st.components.v1.html(_gps_iframe_html(auto_lbl), height=88)

    with col_loc:
        def _on_loc():
            fc_set(
                location_name = st.session_state.get("_fc_location", ""),
                _gps_ingested = False,
                loc_area="", loc_city="", loc_district="",
                loc_state="", loc_pincode="",
            )

        st.text_input(
            "",
            value            = fc()["location_name"],
            placeholder      = ("Enter your location"
                                 if lang == "en" else "अपना स्थान दर्ज करें"),
            key              = "_fc_location",
            label_visibility = "collapsed",
            on_change        = _on_loc,
        )

    # ── Map only — card removed ───────────────────────────────────────────────
    state = fc()
    lat, lon = state["lat"], state["lon"]
    if lat != state["_map_lat"] or lon != state["_map_lon"]:
        fc_set(_map_lat=lat, _map_lon=lon)

    st.components.v1.html(
        _map_html(
            lat      = state["_map_lat"],
            lon      = state["_map_lon"],
            dark     = dark,
            area     = state.get("loc_area", ""),
            city     = state.get("loc_city", ""),
            district = state.get("loc_district", ""),
            state    = state.get("loc_state", ""),
            pincode  = state.get("loc_pincode", ""),
            display  = state["location_name"],
        ),
        height=252,
    )
 
 
def _render_photo(lang: str):
    lbl      = "Attach a Photo" if lang == "en" else "फोटो संलग्न करें"
    opt_lbl  = "Optional"       if lang == "en" else "वैकल्पिक"
    note     = "Photos help resolve complaints 3× faster" if lang == "en" else "फोटो से 3 गुना तेज़ समाधान"
    hint     = "JPG · PNG · WEBP · Max 5 MB"

    sec_html = (
        "<div class='fc-sec'>📷 " + lbl +
        " &nbsp;<span style='font-size:.54rem;background:rgba(99,102,241,0.12);"
        "color:#6366F1;border-radius:6px;padding:2px 7px;font-weight:700;'>"
        + opt_lbl + "</span></div>"
    )
    st.markdown(sec_html, unsafe_allow_html=True)
    st.markdown(
        "<div class='fc-photo-wrap'>"
        "<div class='fc-photo-head'>"
        "<div class='fc-photo-icon'>📷</div>"
        "<div><div class='fc-photo-title'>" + note + "</div>"
        "<div class='fc-photo-sub'>" + hint + "</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "",
        type             = ["jpg", "jpeg", "png", "webp"],
        key              = "_fc_image",
        label_visibility = "collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded:
        fc_set(image_name=uploaded.name)
        ready_lbl = "Photo Ready" if lang == "en" else "फोटो तैयार"
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown(
                "<div style='background:rgba(16,185,129,0.07);border:1.5px solid #86EFAC;"
                "border-radius:13px;padding:10px;text-align:center;margin-top:8px;'>"
                "<div style='font-size:.58rem;font-weight:700;text-transform:uppercase;"
                "letter-spacing:.07em;color:#166534;margin-bottom:7px;'>✅ " + ready_lbl + "</div>",
                unsafe_allow_html=True,
            )
            st.image(uploaded, use_container_width=True)
            st.markdown(
                "<div style='font-size:.63rem;color:#6B7280;margin-top:4px;'>"
                + uploaded.name + "</div></div>",
                unsafe_allow_html=True,
            )
    else:
        fc_set(image_name="")

    return uploaded
 
 
def _render_checklist(lang: str, desc_ok: bool, loc_ok: bool, photo_ok: bool) -> None:
    title = "Ready to Submit?" if lang == "en" else "जमा करने के लिए तैयार?"
    d_lbl = "Description"      if lang == "en" else "विवरण"
    l_lbl = "Location"         if lang == "en" else "स्थान"
    p_lbl = "Photo (optional)" if lang == "en" else "फोटो (वैकल्पिक)"
 
    def chk(ok: bool, lbl: str) -> str:
        return "<div class='fc-check" + (" ok" if ok else "") + "'>" + ("✅" if ok else "⬜") + " " + lbl + "</div>"
 
    st.markdown(
        "<div class='fc-checklist'><div class='fc-checklist-title'>" + title + "</div>"
        "<div class='fc-checks'>" + chk(desc_ok,d_lbl) + chk(loc_ok,l_lbl) + chk(photo_ok,p_lbl) + "</div></div>",
        unsafe_allow_html=True,
    )
 
 
def _render_tip(lang: str) -> None:
    tip = "Add landmarks & a photo for fastest resolution." if lang == "en" else "लैंडमार्क और फोटो जोड़ें।"
    lbl = "Tip:" if lang == "en" else "सुझाव:"
    st.markdown(
        "<div class='fc-tip'>💡 <span><strong>" + lbl + "</strong> " + tip + "</span></div>",
        unsafe_allow_html=True,
    )
 
 
def _render_submit(lang: str, uid, uploaded_file) -> bool:
    state = fc()
    if state["phase"] == "error":
        st.markdown("<div class='fc-err'>⚠️ " + state["error_msg"] + "</div>", unsafe_allow_html=True)

    lbl = "🚀  Submit Complaint" if lang == "en" else "🚀  शिकायत जमा करें"
    
    # Prevent double submission
    already_submitting = state["phase"] == "submitting"
    
    st.markdown("<div class='fc-submit-col'>", unsafe_allow_html=True)
    clicked = st.button(
        lbl,
        use_container_width=True,
        key="fc_sub",
        disabled=already_submitting,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Show spinner while submitting
    if already_submitting:
        st.markdown(
            "<div style='text-align:center;padding:10px;font-size:.85rem;"
            "color:#6366F1;font-weight:600;'>⏳ Submitting your complaint…</div>",
            unsafe_allow_html=True,
        )
        return False

    if not clicked:
        return False

    # Guard: ignore if token already set (prevents double fire on rerun)
    if state.get("submit_token"):
        return False

    desc = (st.session_state.get("_fc_desc") or state["description"] or state["voice_text"] or "").strip()
    loc  = (st.session_state.get("_fc_location") or state["location_name"] or "").strip()
    
    err = ""
    if not desc:
        err = "Please describe the issue." if lang == "en" else "कृपया समस्या का विवरण दें।"
    elif not loc:
        err = "Please enter a location."   if lang == "en" else "कृपया स्थान दर्ज करें।"
    elif not uid:
        err = "Please log in first."       if lang == "en" else "पहले लॉगिन करें।"
    if err:
        st.markdown("<div class='fc-err'>❗ " + err + "</div>", unsafe_allow_html=True)
        return False

    img_bytes, img_name = None, ""
    if uploaded_file is not None:
        try:
            img_bytes = uploaded_file.getvalue()
            img_name  = uploaded_file.name
        except Exception:
            pass

    fc_set(
        phase         = "submitting",
        description   = desc,
        location_name = loc,
        is_emergency  = st.session_state.get("_fc_emergency", state["is_emergency"]),
        category      = state["category"],
        submit_token  = secrets.token_hex(8),
        _img_bytes    = img_bytes,
        _img_name     = img_name,
    )
    return True
 
 
# ─────────────────────────────────────────────────────────────────────────────
# SUBMISSION
# ─────────────────────────────────────────────────────────────────────────────
 
def _run_submission(uid, lang: str) -> None:
    state = fc()
    with st.spinner("Submitting…" if lang == "en" else "जमा हो रहा है…"):
        try:
            img_bytes = state.get("_img_bytes")
            img_name  = state.get("_img_name", "image.jpg")
            if img_bytes:
                resp = api("post", "/complaints/create-with-image",  # type: ignore[name-defined]
                           data={
                               "user_id":     str(uid), "category": state["category"],
                               "description": state["description"], "location": state["location_name"],
                               "latitude":    str(state["lat"]), "longitude": str(state["lon"]),
                               "is_emergency":str(state["is_emergency"]),
                           },
                           files={"image": (img_name, img_bytes, "image/jpeg")})
            else:
                resp = api("post", "/complaints/create",             # type: ignore[name-defined]
                           json={
                               "user_id":     uid, "category": state["category"],
                               "description": state["description"], "location": state["location_name"],
                               "latitude":    state["lat"], "longitude": state["lon"],
                               "is_emergency":state["is_emergency"],
                           })
        except Exception as ex:
            resp = {"error": str(ex)}
 
    fc_set(_img_bytes=None, _img_name="")
 
    if resp.get("success"):
        fc_set(phase="success", success_data={
            "cid":          resp.get("complaint_id", "—"),
            "category":     state["category"],
            "assigned_to":  resp.get("assigned_official_name", "Concerned Department"),
            "is_emergency": state["is_emergency"],
        })
    elif "connect" in str(resp.get("error","")).lower():
        st.session_state.setdefault("offline_complaints", []).append({
            "user_id":     uid,         "category":    state["category"],
            "description": state["description"], "location": state["location_name"],
            "latitude":    state["lat"],"longitude":   state["lon"],
            "is_emergency":state["is_emergency"],
        })
        fc_set(phase="offline")
    else:
        fc_set(phase="idle", error_msg=resp.get("error", resp.get("detail","Unknown error. Try again.")))
 
    st.rerun()

def build_sla(comp):

    try:
        created = comp.get("created_at")
        status = str(comp.get("status", "")).lower()

        if not created:
            return ""

        # Parse datetime
        if isinstance(created, str):
            created_dt = datetime.fromisoformat(
                created.replace("Z", "")
            )
        else:
            created_dt = created

        now = datetime.now()

        days = (now - created_dt).days

        # SLA limit
        sla_limit = 7

        overdue = days > sla_limit and status not in [
            "resolved",
            "closed"
        ]

        cls = "prem-sla-bar overdue" if overdue else "prem-sla-bar"

        if overdue:
            text = f"⚠️ Overdue by {days - sla_limit} day(s)"
        else:
            remaining = max(0, sla_limit - days)
            text = f"⏳ {remaining} day(s) remaining"

        return f'''
        <div class="{cls}">
            <strong>SLA Status:</strong>
            {text}
        </div>
        '''

    except Exception as e:
        return ""
# ─────────────────────────────────────────────────────────────────────────────
# OUTCOME SCREENS
# ─────────────────────────────────────────────────────────────────────────────
 
def _render_success(lang: str) -> None:
    sd  = fc()["success_data"]
    cid = sd.get("cid","—")
    asg = sd.get("assigned_to","Concerned Department")
    emg = sd.get("is_emergency", False)
    title = "Submitted Successfully!" if lang=="en" else "सफलतापूर्वक जमा हुई!"
    sub   = "Your complaint has been received." if lang=="en" else "शिकायत दर्ज हो गई।"
    note  = "Use the ID to track from the dashboard." if lang=="en" else "इस ID से डैशबोर्ड पर ट्रैक करें।"
    back  = "← Back to Dashboard" if lang=="en" else "← डैशबोर्ड पर वापस"
    emg_html = ("<div class='fc-success-chip' style='background:rgba(220,38,38,.40);'>🚨 Emergency</div>"
                if emg else "")
    st.markdown(
        "<div class='fc-success'>"
        "<div class='fc-success-ring'>✅</div>"
        "<div class='fc-success-title'>" + title + "</div>"
        "<div class='fc-success-sub'>" + sub + "</div>"
        "<div class='fc-success-id'>" + cid + "</div>"
        "<div class='fc-success-chips'>"
        "<div class='fc-success-chip'>👤 " + str(asg or "Assign to the official") + "</div>"
        "<div class='fc-success-chip'>📂 " + sd.get("category","").title() + "</div>"
        + emg_html + "</div>"
        "<div class='fc-success-note'>" + note + "</div></div>",
        unsafe_allow_html=True,
    )
    st.balloons()
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if st.button(back, key="success_back_btn", use_container_width=True):
            st.session_state.fc = dict(_FC_DEFAULTS)
            st.session_state.screen = "user_dashboard"
            st.rerun()
 
 
def _render_offline(lang: str) -> None:
    title = "Saved Offline" if lang=="en" else "ऑफलाइन सहेजा गया"
    sub   = "Will submit when internet restores" if lang=="en" else "इंटरनेट मिलते ही जमा होगा"
    body  = ("Saved locally. Will submit automatically on reconnect."
             if lang=="en" else "सहेज ली गई। इंटरनेट मिलते ही जमा होगी।")
    back  = "← Back to Dashboard" if lang=="en" else "← डैशबोर्ड पर वापस"
    st.markdown(
        "<div class='fc-offline'>"
        "<div class='fc-offline-head'><div class='fc-offline-icon'>📶</div>"
        "<div><div class='fc-offline-title'>" + title + "</div>"
        "<div class='fc-offline-sub'>" + sub + "</div></div></div>"
        "<div class='fc-offline-body'>✅ " + body + "</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if st.button(back, key="offline_back_btn", use_container_width=True):
            fc_set(phase="idle")
            st.session_state.screen = "user_dashboard"
            st.rerun()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY
# ─────────────────────────────────────────────────────────────────────────────
 
def pg_file_complaint() -> None:
    _apply_layout("user")  
    submit_offline_complaints()   # type: ignore[name-defined]
 
    lang = st.session_state.language
    uid  = (st.session_state.user or {}).get("user_id")
    dark = st.session_state.get("dark_mode", False)
 
    _init_fc()
    _inject_page_css(dark)
 
    if _ingest_query_params():
        st.rerun()
        return
 
    phase = fc()["phase"]
    if phase == "success":   _render_success(lang);  return
    if phase == "offline":   _render_offline(lang);  return
    if phase == "submitting":_run_submission(uid, lang); return
 
    s    = fc()
    step = 0
    if s["description"] or s["voice_text"]:                      step = 1
    if s["category"] != "other":                                 step = 2
    if s["location_name"] not in ("","Bhopal, Madhya Pradesh"):  step = 3
    if s["image_name"]:                                          step = 4
 
    _render_hero(lang)
    _render_steps(lang, step)
    _render_voice(lang)
    _render_description(lang)
    _render_category(lang)
    _render_emergency(lang)

 
    desc_now = (st.session_state.get("_fc_desc") or s["description"] or s["voice_text"] or "").strip()
    is_emg   = st.session_state.get("_fc_emergency", s["is_emergency"])
    _render_ai_preview(lang, desc_now, is_emg)
 
    _render_location(lang, dark)
    uploaded = _render_photo(lang)
 
    desc_ok  = bool(desc_now)
    loc_ok   = bool((st.session_state.get("_fc_location") or s["location_name"] or "").strip())
    photo_ok = uploaded is not None
    _render_checklist(lang, desc_ok, loc_ok, photo_ok)
    _render_tip(lang)
 
    if _render_submit(lang, uid, uploaded):
        st.rerun()
 

# ═════════════════════════════════════════════════════════════════════════════
# TRACKING
# ═════════════════════════════════════════════════════════════════════════════
def pg_tracking():
    _apply_layout("user")  
    lang = st.session_state.language
    uid  = (st.session_state.user or {}).get("user_id")

    def t(en, hi):
        return en if lang == "en" else hi

    dark  = st.session_state.get("dark_mode", False)
    _CARD = "#10161F" if dark else "#FFFFFF"
    _BG2  = "#080C14" if dark else "#F4F6FB"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
    _A1   = "#6366F1"
    _A2   = "#8B5CF6"

    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)

    # ── PREMIUM CSS ────────────────────────────────────────────────────────────
    css = (
        "<style>"

        ".trk-search-wrap .stTextInput>div>div>input{"
        "border-radius:30px!important;padding:12px 20px!important;"
        "font-size:.88rem!important;border:1.5px solid " + _BOR + "!important;"
        "background:" + _CARD + "!important;"
        "transition:border-color .18s,box-shadow .18s!important;}"
        ".trk-search-wrap .stTextInput>div>div>input:focus{"
        "border-color:#6366F1!important;"
        "box-shadow:0 0 0 3px rgba(99,102,241,.12)!important;}"

        ".trk-chips{display:flex;gap:8px;flex-wrap:wrap;padding:4px 0;margin-bottom:2px;}"
        ".trk-chip{padding:7px 16px;border-radius:30px;font-size:.76rem;font-weight:700;"
        "border:1.5px solid " + _BOR + ";background:" + _CARD + ";color:" + _SUB + ";"
        "white-space:nowrap;pointer-events:none;transition:all .18s;}"
        ".trk-chip.on{background:linear-gradient(135deg,#6366F1,#8B5CF6);"
        "color:#fff;border-color:transparent;"
        "box-shadow:0 4px 12px rgba(99,102,241,.28);}"

        "div[data-testid='stRadio']>div>label>div:first-child{display:none!important;}"
        "div[data-testid='stRadio']>div{gap:4px!important;}"
        "div[data-testid='stRadio']>div>label{"
        "height:0!important;overflow:hidden!important;"
        "opacity:0!important;padding:0!important;margin:0!important;"
        "min-height:0!important;pointer-events:auto!important;}"

        ".trk-flabel{font-size:.70rem;font-weight:700;text-transform:uppercase;"
        "letter-spacing:.09em;color:" + _SUB + ";margin:18px 0 8px;"
        "display:flex;align-items:center;gap:8px;}"
        ".trk-flabel::before{content:'';width:3px;height:14px;"
        "background:linear-gradient(180deg,#6366F1,#8B5CF6);"
        "border-radius:99px;flex-shrink:0;}"
        ".trk-flabel::after{content:'';flex:1;height:1px;"
        "background:linear-gradient(to right," + _BOR + ",transparent);}"

        ".trk-count{font-size:.75rem;color:" + _SUB + ";font-weight:600;"
        "text-align:right;margin:8px 0 12px;}"

        ".trk-card{background:" + _CARD + ";border:1px solid " + _BOR + ";"
        "border-left:4px solid;border-radius:18px;"
        "padding:18px 20px;margin-bottom:4px;"
        "box-shadow:0 2px 10px rgba(15,23,42,.06);"
        "transition:transform .20s,box-shadow .20s;}"
        ".trk-card:hover{transform:translateX(4px);"
        "box-shadow:0 8px 28px rgba(99,102,241,.10);}"
        ".trk-cid{font-family:'Courier New',monospace;font-size:.70rem;font-weight:700;"
        "background:rgba(99,102,241,.10);color:#6366F1;"
        "padding:3px 10px;border-radius:8px;display:inline-block;margin-bottom:8px;}"
        ".trk-badge{border-radius:20px;padding:3px 12px;font-size:.68rem;"
        "font-weight:700;display:inline-block;margin-right:5px;}"
        ".trk-title{font-size:.92rem;font-weight:800;color:" + _TXT + ";"
        "margin:8px 0 4px;}"
        ".trk-desc{font-size:.80rem;color:" + _SUB + ";line-height:1.65;"
        "margin-bottom:10px;}"
        ".trk-meta{display:flex;gap:14px;flex-wrap:wrap;font-size:.71rem;color:" + _SUB + ";"
        "padding-top:10px;border-top:1px solid " + _BOR + ";}"

        ".tl-wrap{margin-top:14px;padding:14px 16px;"
        "background:" + _BG2 + ";border-radius:14px;"
        "border:1px solid " + _BOR + ";}"
        ".tl-row{display:flex;gap:12px;align-items:flex-start;}"
        ".tl-col{display:flex;flex-direction:column;align-items:center;}"
        ".tl-dot{width:24px;height:24px;border-radius:50%;"
        "display:flex;align-items:center;justify-content:center;"
        "font-size:.60rem;font-weight:800;flex-shrink:0;transition:all .18s;}"
        ".tl-dot.done{background:linear-gradient(135deg,#6366F1,#8B5CF6);"
        "color:#fff;box-shadow:0 0 0 4px rgba(99,102,241,.15);}"
        ".tl-dot.active{background:linear-gradient(135deg,#8B5CF6,#EC4899);"
        "color:#fff;box-shadow:0 0 0 4px rgba(139,92,246,.20);"
        "animation:prem-pulse-ring 2s infinite;}"
        ".tl-dot.idle{background:" + _BOR + ";color:" + _SUB + ";"
        "border:2px solid " + _BOR + ";}"
        ".tl-line{width:2px;min-height:16px;border-radius:2px;margin:2px 0;flex:1;}"
        ".tl-line.done{background:linear-gradient(to bottom,#6366F1," + _BOR + ");}"
        ".tl-line.idle{background:" + _BOR + ";}"
        ".tl-info{padding:2px 0 16px;}"
        ".tl-lbl{font-size:.78rem;font-weight:600;color:" + _TXT + ";}"

        ".sla-ok{background:" + ("#080F1C" if dark else "#EFF6FF") + ";"
        "border:1.5px solid " + ("#1E3A5F" if dark else "#BFDBFE") + ";"
        "border-radius:12px;padding:10px 16px;font-size:.76rem;"
        "color:" + ("#60A5FA" if dark else "#1D4ED8") + ";"
        "margin-top:12px;display:flex;gap:8px;align-items:center;"
        "font-weight:600;}"
        ".sla-late{background:" + ("#1C0808" if dark else "#FFF1F2") + ";"
        "border:1.5px solid " + ("#7F1D1D" if dark else "#FECDD3") + ";"
        "border-radius:12px;padding:10px 16px;font-size:.76rem;"
        "color:" + ("#F87171" if dark else "#BE123C") + ";"
        "margin-top:12px;display:flex;gap:8px;align-items:center;"
        "font-weight:600;}"

        ".trk-empty{text-align:center;padding:3rem 2rem;"
        "background:" + _CARD + ";border-radius:22px;"
        "border:1.5px dashed " + _BOR + ";margin:1rem 0;}"
        ".trk-empty-icon{font-size:3.2rem;opacity:.55;display:block;margin-bottom:14px;}"
        ".trk-empty-title{font-size:.98rem;font-weight:700;color:" + _TXT + ";margin-bottom:8px;}"
        ".trk-empty-sub{font-size:.79rem;color:" + _SUB + ";line-height:1.6;}"

        "@media(max-width:600px){"
        ".trk-meta{flex-direction:column;gap:4px;}"
        ".trk-chips{gap:5px;}"
        ".trk-chip{padding:5px 11px;font-size:.68rem;}}"
        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)

    # ── SHARED LOOKUPS ─────────────────────────────────────────────────────────
    STATUS_D = {
        "pending":     ("⏳", t("Pending",     "लंबित"),       "#FFFBEB", "#B45309"),
        "in_progress": ("🔄", t("In Progress", "प्रगति"),      "#EFF6FF", "#1D4ED8"),
        "resolved":    ("✅", t("Resolved",    "समाधान"),      "#F0FDF4", "#15803D"),
        "closed":      ("🔒", t("Closed",      "बंद"),          "#F1F5F9", "#475569"),
        "rejected":    ("❌", t("Rejected",    "अस्वीकृत"),    "#FFF1F2", "#BE123C"),
    }
    PRIORITY_D = {
        "high":   ("🔴", t("High",   "उच्च"),   "#FFF1F2", "#BE123C", "#EF4444"),
        "medium": ("🟡", t("Medium", "मध्यम"),  "#FFFBEB", "#B45309", "#F59E0B"),
        "low":    ("🟢", t("Low",    "निम्न"),  "#F0FDF4", "#15803D", "#22C55E"),
    }

    # ── BUILD TIMELINE ────────────────────────────────────────────────────────
    def build_tl(status: str) -> str:
        steps = [
            t("Submitted",  "सबमिट"),
            t("In Review",  "समीक्षा"),
            t("In Progress","प्रगति"),
            t("Resolved",   "समाधान"),
        ]
        status_map = {
            "pending":     0,
            "review":      1,
            "in_progress": 2,
            "resolved":    3,
            "closed":      3,
        }
        current = status_map.get(str(status).lower(), 0)

        html = "<div class='prem-timeline'>"
        for i, label in enumerate(steps):
            if i < current:
                cls  = "done"
                icon = "✓"
            elif i == current:
                cls  = "active"
                icon = "●"
            else:
                cls  = "idle"
                icon = "○"

            html += (
                "<div class='prem-tl-item'>"
                "<div class='prem-tl-dot " + cls + "'>" + icon + "</div>"
                "<div class='prem-tl-info'>"
                "<div class='prem-tl-label'>" + label + "</div>"
                "</div></div>"
            )
            if i < len(steps) - 1:
                html += "<div class='prem-tl-line " + cls + "'></div>"

        html += "</div>"
        return html

    # ── BUILD SLA ─────────────────────────────────────────────────────────────
    # FIX: build_sla was accidentally removed when build_tl was rewritten.
    # Restored here — render_card references it.
    def build_sla(comp: dict) -> str:
        sla = comp.get("sla_deadline")
        if not sla:
            return ""
        if comp.get("is_overdue"):
            return (
                "<div class='sla-late'>⏰&nbsp;<span><strong>"
                + t("OVERDUE!", "समय सीमा समाप्त!") + "</strong> "
                + t("Expected by", "अपेक्षित") + ": " + str(sla) + "</span></div>"
            )
        return (
            "<div class='sla-ok'>⏱&nbsp;<span>"
            + t("Expected by", "अपेक्षित")
            + ": <strong>" + str(sla) + "</strong></span></div>"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # render_card — FIX: idx parameter added
    #
    # ROOT CAUSE of StreamlitDuplicateElementKey:
    #   Streamlit renders ALL tab contents in a single pass.
    #   Tab 1 called render_card(found) and Tab 2's loop also called
    #   render_card(same_complaint) — both produced key="trk_v_GR4B5Q2G3J".
    #   Streamlit sees two widgets with the same key → crash.
    #
    # FIX:
    #   Every widget key inside render_card now includes BOTH the cid AND
    #   the `idx` (loop counter / call-site discriminator).
    #   Tab 1 always passes idx=0 (only one card rendered there).
    #   Tab 2 passes the enumerate() index.
    #   Even if the same complaint appears in both tabs, the keys differ:
    #     Tab1: "trk_v_GR4B5Q2G3J_t1"
    #     Tab2: "trk_v_GR4B5Q2G3J_0", "trk_v_GR4B5Q2G3J_1", ...
    # ─────────────────────────────────────────────────────────────────────────
    def render_card(comp: dict, expanded: bool = False, idx: int = 0,
                    id_prefix: str = "t2") -> None:
        """
        Parameters
        ----------
        comp      : complaint dict
        expanded  : whether expander starts open
        idx       : position in the calling loop (0-based).
                    Used to guarantee unique widget keys.
        id_prefix : extra namespace — "t1" for Tab-1 search result,
                    "t2" for Tab-2 list items.  Prevents key collision
                    when the same complaint appears in both tabs.
        """
        cid      = comp.get("complaint_id") or comp.get("id") or "N/A"
        status   = comp.get("status",   "pending")
        priority = comp.get("priority", "medium")
        cat      = comp.get("category", "other").title()
        desc     = comp.get("description", "")
        loc      = comp.get("location",  "—")
        date     = comp.get("created_at", "—")
        emg      = comp.get("is_emergency", False)

        si, sl, sb, sf       = STATUS_D.get(status,   ("", "", _BOR, _SUB))
        pi, pl, pb, pf, bcol = PRIORITY_D.get(priority, ("", "", _BOR, _SUB, _A1))
        if emg:
            bcol = "#DC2626"

        exp_lbl  = ("🚨 " if emg else "") + "#" + str(cid) + "  ·  " + cat + "  ·  " + si + " " + sl
        emg_html = (
            '<span class="trk-badge" style="background:#DC2626;color:#fff;">🚨 EMERGENCY</span>'
            if emg else ""
        )

        # Unique key base — combines prefix + cid + loop index
        # Safe against: None cid, duplicate cids, same card in two tabs
        _k = f"{id_prefix}_{str(cid)}_{idx}"

        with st.expander(exp_lbl, expanded=expanded):

            # ── Listen / voice button ──────────────────────────────────────
            if st.button("🔊 " + t("Listen", "सुनें"), key="trk_v_" + _k):
                speak_text("Complaint " + str(cid) + ": " + desc, lang)

            # ── Card HTML ─────────────────────────────────────────────────
            st.markdown(
                "<div class='trk-card' style='border-left-color:" + bcol + ";'>"

                "<div style='display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:10px;'>"
                "<span class='trk-cid'>#" + str(cid) + "</span>"
                "<span class='trk-badge' style='background:" + sb + ";color:" + sf + ";'>" + si + " " + sl + "</span>"
                "<span class='trk-badge' style='background:" + pb + ";color:" + pf + ";'>" + pi + " " + pl + "</span>"
                + emg_html +
                "</div>"

                "<div class='trk-title'>" + cat + "</div>"
                "<div class='trk-desc'>" + html.escape(desc[:200]) + ("…" if len(desc) > 200 else "") + "</div>"

                "<div class='trk-meta'>"
                "<span>📍 " + html.escape(str(loc)) + "</span>"
                "<span>📅 " + str(date) + "</span>"
                "</div>"
                "</div>"

                "<div class='trk-flabel' style='margin-top:16px;'>"
                + t("Progress Timeline", "प्रगति टाइमलाइन") + "</div>"
                + build_tl(status)
                + build_sla(comp),

                unsafe_allow_html=True,
            )

    # ════════════════════════════════════════════════════════
    # HERO
    # ════════════════════════════════════════════════════════
    st.markdown(
        "<div class='prem-hero' style='padding:28px 28px 24px;margin-bottom:0;'>"
        "<div class='prem-hero-avatar'>🔍</div>"
        "<div class='prem-hero-title'>" + t("Track Complaint", "शिकायत ट्रैक करें") + "</div>"
        "<p class='prem-hero-sub'>" + t("Check real-time status of your complaints", "अपनी शिकायत की स्थिति जानें") + "</p>"
        "<div class='prem-hero-stats'>"
        "<div class='prem-hstat h-blue'><div class='prem-hstat-num'>🔎</div><div class='prem-hstat-lbl'>" + t("Track by ID", "ID से ट्रैक") + "</div></div>"
        "<div class='prem-hstat h-amber'><div class='prem-hstat-num'>📋</div><div class='prem-hstat-lbl'>" + t("My Complaints", "मेरी शिकायतें") + "</div></div>"
        "<div class='prem-hstat h-green'><div class='prem-hstat-num'>⏱</div><div class='prem-hstat-lbl'>" + t("Live Status", "लाइव स्थिति") + "</div></div>"
        "<div class='prem-hstat h-red'><div class='prem-hstat-num'>🚨</div><div class='prem-hstat-lbl'>" + t("Emergency", "आपातकाल") + "</div></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs([
        "🔎 " + t("Track by ID",   "ID से ट्रैक करें"),
        "📋 " + t("My Complaints", "मेरी शिकायतें"),
    ])

    # ════════════════════════════════════════════════════════
    # TAB 1 — Track by ID
    # ════════════════════════════════════════════════════════
    with tab1:
        st.markdown(
            "<div class='prem-section-header'>🔎 " + t("Enter Complaint ID", "शिकायत ID दर्ज करें") + "</div>",
            unsafe_allow_html=True,
        )

        sc1, sc2 = st.columns([4, 1])
        with sc1:
            st.markdown('<div class="trk-search-wrap">', unsafe_allow_html=True)
            search_id = st.text_input(
                "tid",
                label_visibility="collapsed",
                placeholder=t("Enter Complaint ID  e.g. CMP-0041", "शिकायत ID दर्ज करें जैसे CMP-0041"),
                key="trk_search_id",
            )
            st.markdown("</div>", unsafe_allow_html=True)
        with sc2:
            search_btn = st.button(t("🔍 Track", "🔍 ट्रैक"), key="trk_btn", use_container_width=True)

        if search_btn:
            sid = search_id.strip()
            if not sid:
                st.warning(t("Please enter a complaint ID.", "कृपया शिकायत ID दर्ज करें।"))
            elif not uid:
                st.warning(t("Please login to track complaints.", "लॉगिन करें।"))
            else:
                raw = api("get", "/complaints/user/" + str(uid))
                if isinstance(raw, list):
                    found = next(
                        (c for c in raw
                         if c.get("complaint_id", "").strip().lower() == sid.lower()),
                        None,
                    )
                    if found:
                        st.success(t("✅ Complaint found!", "✅ शिकायत मिली!"))
                        # FIX: id_prefix="t1" ensures Tab-1 keys never clash with Tab-2 keys
                        render_card(found, expanded=True, idx=0, id_prefix="t1")
                    else:
                        st.markdown(
                            "<div class='trk-empty'>"
                            "<span class='trk-empty-icon'>❌</span>"
                            "<div class='trk-empty-title'>"
                            + t("Complaint not found", "शिकायत नहीं मिली") +
                            "</div>"
                            "<div class='trk-empty-sub'>"
                            + t("Check the ID and ensure you are logged into the correct account.",
                                "ID जाँचें या सुनिश्चित करें सही खाते में हैं।") +
                            "</div></div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.error(t("Unable to fetch. Please try again.", "डेटा प्राप्त नहीं हुआ। पुनः प्रयास करें।"))

    # ════════════════════════════════════════════════════════
    # TAB 2 — My Complaints
    # ════════════════════════════════════════════════════════
    with tab2:
        if not uid:
            st.markdown(
                "<div class='trk-empty'>"
                "<span class='trk-empty-icon'>🔒</span>"
                "<div class='trk-empty-title'>" + t("Login Required", "लॉगिन आवश्यक") + "</div>"
                "<div class='trk-empty-sub'>" + t("Please login to view your complaints.", "लॉगिन करें।") + "</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            return

        all_comps = api("get", "/complaints/user/" + str(uid))
        all_comps = all_comps if isinstance(all_comps, list) else []

        if not all_comps:
            st.markdown(
                "<div class='trk-empty'>"
                "<span class='trk-empty-icon'>📭</span>"
                "<div class='trk-empty-title'>" + t("No complaints yet", "कोई शिकायत नहीं") + "</div>"
                "<div class='trk-empty-sub'>" + t("File your first complaint to get started.", "पहली शिकायत दर्ज करें।") + "</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            ec1, ec2, ec3 = st.columns([1, 2, 1])
            with ec2:
                if st.button(
                    t("📢 File First Complaint", "📢 पहली शिकायत दर्ज करें"),
                    key="trk_file_first",
                    use_container_width=True,
                ):
                    st.session_state.screen = "file_complaint"
                    st.rerun()
            return

        # ── Filter state defaults ──────────────────────────────────────────
        for k, v in [("trk_sf", "all"), ("trk_pf", "all"), ("trk_q", "")]:
            if k not in st.session_state:
                st.session_state[k] = v

        # ── Search bar ────────────────────────────────────────────────────
        st.markdown(
            "<div class='prem-section-header'>🔍 " + t("Filter & Search", "खोजें और फ़िल्टर") + "</div>",
            unsafe_allow_html=True,
        )
        st.markdown('<div class="trk-search-wrap">', unsafe_allow_html=True)
        srch = st.text_input(
            "tsrch",
            label_visibility="collapsed",
            placeholder="🔍 " + t("Search by ID, category, location…", "ID, श्रेणी, स्थान से खोजें…"),
            value=st.session_state.trk_q,
            key="trk_search_q",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        if srch != st.session_state.trk_q:
            st.session_state.trk_q = srch
            st.rerun()

        # ── Status filter ─────────────────────────────────────────────────
        SF = [
            ("all",         t("All",         "सभी"),          "📋"),
            ("pending",     t("Pending",      "लंबित"),        "⏳"),
            ("in_progress", t("In Progress",  "प्रगति"),       "🔄"),
            ("resolved",    t("Resolved",     "समाधान"),       "✅"),
            ("closed",      t("Closed",       "बंद"),           "🔒"),
            ("rejected",    t("Rejected",     "अस्वीकृत"),     "❌"),
        ]
        st.markdown("<div class='trk-flabel'>" + t("Status", "स्थिति") + "</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='trk-chips'>"
            + "".join(
                "<span class='trk-chip" + (" on" if st.session_state.trk_sf == v else "") + "'>"
                + ic + " " + lb + "</span>"
                for v, lb, ic in SF
            )
            + "</div>",
            unsafe_allow_html=True,
        )
        sf_choice = st.radio(
            "sf_radio",
            label_visibility="collapsed",
            options=[v for v, lb, ic in SF],
            format_func=lambda v: next(ic + " " + lb for fv, lb, ic in SF if fv == v),
            index=next(i for i, (v, lb, ic) in enumerate(SF) if v == st.session_state.trk_sf),
            horizontal=True,
            key="trk_sf_radio",
        )
        if sf_choice != st.session_state.trk_sf:
            st.session_state.trk_sf = sf_choice
            st.rerun()

        # ── Priority filter ───────────────────────────────────────────────
        PF = [
            ("all",    t("All",    "सभी"),     "🔘"),
            ("high",   t("High",   "उच्च"),    "🔴"),
            ("medium", t("Medium", "मध्यम"),   "🟡"),
            ("low",    t("Low",    "निम्न"),   "🟢"),
        ]
        st.markdown("<div class='trk-flabel'>" + t("Priority", "प्राथमिकता") + "</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='trk-chips'>"
            + "".join(
                "<span class='trk-chip" + (" on" if st.session_state.trk_pf == v else "") + "'>"
                + ic + " " + lb + "</span>"
                for v, lb, ic in PF
            )
            + "</div>",
            unsafe_allow_html=True,
        )
        pf_choice = st.radio(
            "pf_radio",
            label_visibility="collapsed",
            options=[v for v, lb, ic in PF],
            format_func=lambda v: next(ic + " " + lb for fv, lb, ic in PF if fv == v),
            index=next(i for i, (v, lb, ic) in enumerate(PF) if v == st.session_state.trk_pf),
            horizontal=True,
            key="trk_pf_radio",
        )
        if pf_choice != st.session_state.trk_pf:
            st.session_state.trk_pf = pf_choice
            st.rerun()

        # ── Apply filters ─────────────────────────────────────────────────
        filtered = all_comps
        if st.session_state.trk_sf != "all":
            filtered = [c for c in filtered if c.get("status", "") == st.session_state.trk_sf]
        if st.session_state.trk_pf != "all":
            filtered = [c for c in filtered if c.get("priority", "") == st.session_state.trk_pf]
        if st.session_state.trk_q:
            term = st.session_state.trk_q.strip().lower()
            filtered = [
                c for c in filtered
                if term in c.get("complaint_id", "").lower()
                or term in c.get("category",     "").lower()
                or term in c.get("location",     "").lower()
                or term in c.get("description",  "").lower()
            ]

        # ── Results summary ───────────────────────────────────────────────
        st.markdown(
            "<div style='display:flex;align-items:center;justify-content:space-between;"
            "flex-wrap:wrap;gap:8px;margin:14px 0 8px;'>"
            "<span style='background:rgba(99,102,241,.09);color:#6366F1;"
            "border:1.5px solid rgba(99,102,241,.20);border-radius:20px;"
            "padding:5px 16px;font-size:.78rem;font-weight:800;'>"
            + t("Showing", "दिखा रहे हैं") + " <strong>" + str(len(filtered)) + "</strong> "
            + t("of", "में से") + " <strong>" + str(len(all_comps)) + "</strong> "
            + t("complaints", "शिकायतें") + "</span>"
            "<span style='font-size:.72rem;color:#94A3B8;font-weight:600;'>"
            + str(len(all_comps) - len(filtered)) + " " + t("hidden", "छिपे") + "</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        any_active = (
            st.session_state.trk_sf != "all"
            or st.session_state.trk_pf != "all"
            or st.session_state.trk_q
        )
        if any_active:
            cl1, cl2, cl3 = st.columns([1, 2, 1])
            with cl2:
                if st.button(
                    t("✕ Clear All Filters", "✕ सभी फ़िल्टर साफ़ करें"),
                    key="trk_clear",
                    use_container_width=True,
                ):
                    st.session_state.trk_sf = "all"
                    st.session_state.trk_pf = "all"
                    st.session_state.trk_q  = ""
                    st.rerun()

        if not filtered:
            st.markdown(
                "<div class='trk-empty'>"
                "<span class='trk-empty-icon'>🔍</span>"
                "<div class='trk-empty-title'>"
                + t("No complaints match your filters", "कोई शिकायत मेल नहीं खाती") +
                "</div>"
                "<div class='trk-empty-sub'>"
                + t("Try adjusting the filters above.", "ऊपर फ़िल्टर बदलें।") +
                "</div></div>",
                unsafe_allow_html=True,
            )
            return

        # ── Render cards
        # FIX: enumerate() provides `idx` for each card.
        # id_prefix="t2" namespaces Tab-2 keys away from Tab-1.
        # Even if Tab-1 searched for and rendered complaint #3,
        # Tab-2 keys are "t2_CMP-0003_2" vs Tab-1's "t1_CMP-0003_0" → no clash.
        for idx, comp in enumerate(filtered):
            render_card(comp, expanded=False, idx=idx, id_prefix="t2")

    # ════════════════════════════════════════════════════════
    # BACK
    # ════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    bc1, bc2, bc3 = st.columns([1, 2, 1])
    with bc2:
        if st.button(
            t("← Back to Dashboard", "← डैशबोर्ड पर वापस"),
            key="trk_back",
            use_container_width=True,
        ):
            st.session_state.screen = "user_dashboard"
            st.rerun()
def _display_complaint_card(complaint, uid, lang):
    """Display a compact complaint card with expandable details"""
    complaint_id = complaint.get("complaint_id", "N/A")
    status = complaint.get("status", "pending")
    priority = complaint.get("priority", "medium")
    category = complaint.get("category", "other").title()
    created_at = complaint.get("created_at", "Unknown")
    
    # Status badge
    status_config = {
        "pending": ("⏳ Pending", "#FEF3C7", "#D97706"),
        "in_progress": ("🔄 In Progress", "#DBEAFE", "#2563EB"),
        "resolved": ("✅ Resolved", "#D1FAE5", "#059669"),
        "closed": ("🔒 Closed", "#F3F4F6", "#6B7280"),
        "rejected": ("❌ Rejected", "#FEE2E2", "#DC2626")
    }
    status_text, status_bg, status_color = status_config.get(status, ("📋 Pending", "#FEF3C7", "#D97706"))
    
    # Priority badge
    priority_config = {
        "high": ("🔴 High", "#FEE2E2", "#DC2626"),
        "medium": ("🟠 Medium", "#FEF3C7", "#D97706"),
        "low": ("🟢 Low", "#D1FAE5", "#059669")
    }
    priority_text, priority_bg, priority_color = priority_config.get(priority, ("⚪ Normal", "#F3F4F6", "#6B7280"))
    
    with st.expander(f"#{complaint_id} - {category} - {status_text}", expanded=False):
        st.markdown(f"""
        <div style="padding: 10px; background: #f8fafc; border-radius: 12px; margin-bottom: 10px;">
            <p style="margin-bottom: 8px;"><strong>Description:</strong> {complaint.get('description', '')}</p>
            <div style="display: flex; gap: 16px; flex-wrap: wrap; font-size: 0.8rem; color: #475569;">
                <span>📍 {complaint.get('location', 'N/A')}</span>
                <span>📅 {created_at}</span>
                <span>🏢 {complaint.get('department', 'N/A')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # SLA info
        if complaint.get("sla_deadline"):
            if complaint.get("is_overdue"):
                st.error(f"⏰ OVERDUE! Expected by: {complaint.get('sla_deadline')}")
            else:
                st.info(f"⏱️ Expected resolution by: {complaint.get('sla_deadline')}")
        
        # Action buttons based on status
        if status == "resolved" and not complaint.get("feedback"):
            _display_feedback_section(complaint, uid)
        elif complaint.get("feedback") == "satisfied" and not complaint.get("rating") and complaint.get("official_id"):
            _display_rating_section(complaint, uid)


def _display_complaint_detail(complaint, uid, lang):
    """Display full complaint details with timeline"""
    complaint_id = complaint.get("complaint_id", "N/A")
    status = complaint.get("status", "pending")
    priority = complaint.get("priority", "medium")
    
    status_config = {
        "pending": ("⏳ Pending", "#FEF3C7", "#D97706"),
        "in_progress": ("🔄 In Progress", "#DBEAFE", "#2563EB"),
        "resolved": ("✅ Resolved", "#D1FAE5", "#059669"),
        "closed": ("🔒 Closed", "#F3F4F6", "#6B7280"),
        "rejected": ("❌ Rejected", "#FEE2E2", "#DC2626")
    }
    status_text, status_bg, status_color = status_config.get(status, ("📋 Pending", "#FEF3C7", "#D97706"))
    
    priority_config = {
        "high": ("🔴 High", "#DC2626"),
        "medium": ("🟠 Medium", "#D97706"),
        "low": ("🟢 Low", "#059669")
    }
    priority_text, priority_color = priority_config.get(priority, ("⚪ Normal", "#6B7280"))
    
    st.markdown(f"""
    <div style="background: white; border-radius: 16px; padding: 20px; margin: 16px 0; border: 1px solid #E5E7EB;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
            <div>
                <span style="font-family: monospace; font-size: 1.2rem; font-weight: 700;">#{complaint_id}</span>
                <span style="margin-left: 12px; background: {status_bg}; color: {status_color}; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">{status_text}</span>
                <span style="margin-left: 8px; color: {priority_color}; font-weight: 600;">{priority_text}</span>
            </div>
            <div style="font-size: 0.8rem; color: #6B7280;">📅 {complaint.get('created_at', 'Unknown')}</div>
        </div>
        <div style="margin-bottom: 16px;">
            <div style="font-weight: 600; margin-bottom: 8px;">Category: {complaint.get('category', 'Other').title()}</div>
            <div style="background: #F8FAFC; padding: 12px; border-radius: 12px;">
                <div style="font-weight: 600; margin-bottom: 4px;">Description:</div>
                <p style="margin: 0;">{complaint.get('description', '')}</p>
            </div>
        </div>
        <div style="display: flex; gap: 16px; flex-wrap: wrap; font-size: 0.85rem; color: #475569; margin-bottom: 16px;">
            <span>📍 <strong>Location:</strong> {complaint.get('location', 'N/A')}</span>
            <span>🏢 <strong>Department:</strong> {complaint.get('department', 'N/A')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # SLA info
    if complaint.get("sla_deadline"):
        if complaint.get("is_overdue"):
            st.error(f"⏰ OVERDUE! Expected by: {complaint.get('sla_deadline')}")
        else:
            st.info(f"⏱️ Expected resolution by: {complaint.get('sla_deadline')}")
    
    # Timeline
    timeline = complaint.get("timeline", [])
    if timeline:
        st.markdown("### 📅 Timeline")
        for item in timeline:
            st.markdown(f"""
            <div style="display: flex; gap: 12px; margin-bottom: 12px;">
                <div style="width: 8px; height: 8px; background: #D97706; border-radius: 50%; margin-top: 6px;"></div>
                <div style="flex: 1;">
                    <div style="font-weight: 600;">{item.get('status', '').replace('_', ' ').title()}</div>
                    <div style="font-size: 0.85rem;">{item.get('note', '')}</div>
                    <div style="font-size: 0.7rem; opacity: 0.6;">{item.get('time', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No timeline updates yet.")
    
    # Feedback/Rating section if needed
    if status == "resolved" and not complaint.get("feedback"):
        _display_feedback_section(complaint, uid)
    elif complaint.get("feedback") == "satisfied" and not complaint.get("rating") and complaint.get("official_id"):
        _display_rating_section(complaint, uid)


def _display_feedback_section(complaint, uid):
    """Display feedback confirmation for resolved complaint"""
    cid = complaint.get("complaint_id", "")
    deadline = complaint.get("feedback_deadline", "within 2 days")
    unique_key = f"track_fb_{cid}_{uid}"
    
    st.markdown(f"""
    <div style="background: #FFFBEB; border-left: 4px solid #F59E0B; border-radius: 12px; padding: 16px; margin: 12px 0;">
        <div style="font-size: 1.2rem; margin-bottom: 8px;">✅</div>
        <div style="font-weight: 700; font-size: 1rem;">Complaint Resolved – Please Confirm!</div>
        <div style="margin: 8px 0;">Was your issue resolved to your satisfaction?</div>
        <div style="font-size: 0.75rem; color: #B45309;">⏰ Respond by {deadline} (auto‑closes after 2 days)</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Yes, Satisfied", key=f"fb_yes_{unique_key}", use_container_width=True):
            resp = api("put", f"/complaints/{cid}/feedback", json={"feedback": "satisfied"})
            if resp.get("success"):
                st.success("Thank you! Now please rate the service.")
                st.rerun()
            else:
                st.error("Error submitting feedback")
    with col2:
        if st.button("❌ Not Satisfied", key=f"fb_no_{unique_key}", use_container_width=True):
            resp = api("put", f"/complaints/{cid}/feedback", json={"feedback": "not_satisfied"})
            if resp.get("success"):
                st.warning("Complaint reopened for re-investigation.")
                st.rerun()
            else:
                st.error("Error submitting feedback")


def _display_rating_section(complaint, uid):
    """Display rating section for satisfied complaint"""
    cid = complaint.get("complaint_id", "")
    off_id = complaint.get("official_id")
    unique_key = f"track_rate_{cid}_{uid}"
    
    # Try to get official name
    off_name = "the official"
    if off_id:
        off_list = api("get", "/admin/officials/all")
        if isinstance(off_list, list):
            match = next((o for o in off_list if o.get("id") == off_id), None)
            if match:
                off_name = match.get("name", off_name)
    
    st.markdown(f"""
    <div style="background: #F0FDF4; border-left: 4px solid #10B981; border-radius: 12px; padding: 16px; margin: 12px 0;">
        <div style="font-weight: 700; font-size: 1rem;">⭐ Rate your experience</div>
        <div>How satisfied were you with <strong>{off_name}</strong>'s resolution?</div>
    </div>
    """, unsafe_allow_html=True)
    
    stars = st.select_slider(
        "Your rating",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: f"{'⭐' * x} ({x}/5)",
        value=5,
        key=f"stars_{unique_key}"
    )
    
    comment = st.text_area(
        "Additional feedback (optional)",
        key=f"comment_{unique_key}",
        placeholder="Tell us about your experience...",
        height=80,
        label_visibility="collapsed"
    )
    
    if st.button(f"Submit {stars}⭐ Rating", key=f"submit_rate_{unique_key}", use_container_width=True):
        resp = api("post", f"/complaints/{cid}/rate", json={
            "stars": stars,
            "comment": comment or None,
            "user_id": uid,
            "official_id": off_id,
        })
        if resp.get("success"):
            st.success("✅ Rating submitted! Thank you for your feedback.")
            st.balloons()
            st.rerun()
        else:
            st.error(resp.get("detail", resp.get("error", "Error submitting rating")))


def _show_detail(d, uid, lang):
    s = d.get("status", "pending")
    sc = SC.get(s, "#888")
    si = SI.get(s, "📋")
    p = d.get("priority", "medium")
    pcl = PC.get(p, "badge-medium")
    rat = d.get("rating")

    st.markdown(f"""<div class="card" style="border-left:5px solid {sc};">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">
            <div>
                <div style="font-size:.72rem;font-weight:700;opacity:.6;">COMPLAINT ID</div>
                <div style="font-size:1.3rem;font-weight:800;color:{sc};">
                    #{d.get('complaint_id','')}</div>
            </div>
            <div style="font-size:2.5rem;">{si}</div>
        </div>
        <div style="margin-top:10px;font-size:.88rem;line-height:1.65;">
            {d.get('description','')[:200]}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;">
            <span class="{pcl}">{p.title()}</span>
            <span style="color:{sc};font-weight:700;font-size:.8rem;">
                {si} {s.replace('_',' ').title()}</span>
            {"<span>" + stars_html(rat['stars']) + "</span>" if rat else ""}
        </div>
        <div style="font-size:.76rem;opacity:.6;margin-top:8px;">
            📍 {d.get('location','N/A')} · 🏢 {d.get('department','N/A')} ·
            📅 {d.get('created_at','')}</div>
    </div>""", unsafe_allow_html=True)

    # timeline
    st.markdown(f'<div class="section-header">📅 {t("timeline")}</div>', unsafe_allow_html=True)
    st.markdown(render_timeline(d), unsafe_allow_html=True)

    # --- Voice Output Button (improved) ---
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔊 Read Status Aloud", key="tr_tts", use_container_width=True):
            status_text = f"Complaint {d.get('complaint_id')} is {s.replace('_',' ')}. "
            desc = d.get('description', '')
            msg = status_text + desc[:200]
            speak_text(msg, lang)

    if s == "resolved" and not d.get("feedback"):
        _feedback_confirm_card(d, uid)
    elif d.get("feedback") == "satisfied" and not rat and d.get("official_id"):
        _rating_card(d, uid)


# ═════════════════════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═════════════════════════════════════════════════════════════════════════════
def pg_notifications():
    _apply_layout("user")  
    import re
    import html as _html
    from datetime import datetime, timedelta

    lang = st.session_state.language
    uid  = (st.session_state.user or {}).get("user_id")

    def t(en, hi):
        return hi if lang == "hi" else en

    dark  = st.session_state.get("dark_mode", False)
    _CARD = "#0D1220" if dark else "#FFFFFF"
    _BOR  = "#1C2540" if dark else "#E8EDF7"
    _TXT  = "#EFF2FF" if dark else "#0B1428"
    _SUB  = "#7C8FAC" if dark else "#5A6A85"
    _A1   = "#6366F1"
    _A2   = "#8B5CF6"
    _UNR  = "rgba(99,102,241,0.10)" if dark else "rgba(99,102,241,0.06)"
    _GRN  = "#4ADE80" if dark else "#166534"
    _GRN_BG = "rgba(74,222,128,0.10)" if dark else "#F0FDF4"
    _GRN_BD = "rgba(74,222,128,0.25)" if dark else "#86EFAC"
    _RED_BG = "rgba(239,68,68,0.10)" if dark else "#FEF2F2"
    _RED_BD = "rgba(239,68,68,0.25)" if dark else "#FECACA"
    _RED    = "#FCA5A5" if dark else "#991B1B"

    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)
    st.markdown(f"""
<style>
/* ── notification card ── */
.nc{{
    background:{_CARD};border:1.5px solid {_BOR};border-radius:18px;
    padding:18px 20px;margin:8px 0;position:relative;
    transition:transform .18s,box-shadow .18s,border-color .18s;
    font-family:'DM Sans','Noto Sans Devanagari',system-ui,sans-serif;
}}
.nc:hover{{transform:translateX(5px);box-shadow:0 8px 28px rgba(99,102,241,.13);border-color:{_A1}55;}}
.nc.unread{{border-left:4px solid {_A1};background:{_UNR};}}
.nc.dimmed{{opacity:.72;}}
.nc-inner{{display:flex;gap:14px;align-items:flex-start;}}
.nc-icon{{font-size:1.75rem;min-width:44px;text-align:center;flex-shrink:0;margin-top:2px;}}
.nc-body{{flex:1;min-width:0;}}
.nc-title{{font-size:.90rem;font-weight:700;color:{_TXT};margin-bottom:4px;
    display:flex;align-items:center;gap:8px;flex-wrap:wrap;letter-spacing:-.01em;}}
.nc-new{{background:linear-gradient(135deg,{_A1},{_A2});color:#fff;
    font-size:.58rem;font-weight:700;padding:2px 8px;border-radius:99px;
    letter-spacing:.04em;text-transform:uppercase;
    box-shadow:0 2px 8px rgba(99,102,241,.35);flex-shrink:0;}}
.nc-msg{{font-size:.81rem;color:{_SUB};line-height:1.65;margin-bottom:7px;}}
.nc-time{{font-size:.67rem;color:{_SUB};font-family:'DM Mono','Courier New',monospace;}}
.nc-dot{{position:absolute;top:18px;right:18px;width:9px;height:9px;border-radius:50%;
    background:{_A1};box-shadow:0 0 0 3px rgba(99,102,241,.22);}}

/* ── section group label ── */
.ng-label{{font-size:.67rem;font-weight:700;text-transform:uppercase;letter-spacing:.10em;
    color:{_SUB};margin:22px 0 10px;display:flex;align-items:center;gap:10px;}}
.ng-label::before{{content:'';width:3px;height:13px;
    background:linear-gradient(180deg,{_A1},{_A2});border-radius:99px;flex-shrink:0;}}
.ng-label::after{{content:'';flex:1;height:1px;
    background:linear-gradient(to right,{_BOR},transparent);}}

/* ── stat cards ── */
.notif-stat-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:6px;}}
.notif-stat{{background:{_CARD};border:1px solid {_BOR};border-radius:16px;
    padding:16px 12px;text-align:center;position:relative;overflow:hidden;
    box-shadow:0 2px 8px rgba(15,23,42,0.06);}}
.notif-stat::before{{content:'';position:absolute;top:0;left:0;right:0;
    height:3px;border-radius:16px 16px 0 0;}}
.notif-stat.all::before{{background:linear-gradient(90deg,{_A1},{_A2});}}
.notif-stat.unread::before{{background:linear-gradient(90deg,#EF4444,#DC2626);}}
.notif-stat.read::before{{background:linear-gradient(90deg,#10B981,#059669);}}
.notif-stat-num{{font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:2rem;font-weight:800;line-height:1.1;margin-bottom:4px;}}
.notif-stat-lbl{{font-size:.65rem;font-weight:700;text-transform:uppercase;
    letter-spacing:.07em;color:{_SUB};}}

/* ── action buttons override ── */
div[data-testid="stButton"].notif-read-btn>button{{
    background:{"rgba(99,102,241,0.12)" if dark else "#EEF2FF"}!important;
    color:{_A1}!important;border:1.5px solid rgba(99,102,241,0.25)!important;
    box-shadow:none!important;font-size:.72rem!important;padding:5px 10px!important;
    border-radius:9px!important;
}}
div[data-testid="stButton"].notif-read-btn>button:hover{{
    background:rgba(99,102,241,0.20)!important;transform:none!important;
}}
div[data-testid="stButton"].notif-del-btn>button{{
    background:{"rgba(239,68,68,0.08)" if dark else "#FFF1F2"}!important;
    color:{"#FCA5A5" if dark else "#BE123C"}!important;
    border:1.5px solid {"rgba(239,68,68,0.22)" if dark else "#FECDD3"}!important;
    box-shadow:none!important;font-size:.72rem!important;padding:5px 10px!important;
    border-radius:9px!important;
}}
div[data-testid="stButton"].notif-del-btn>button:hover{{
    background:{"rgba(239,68,68,0.18)" if dark else "#FFE4E6"}!important;
    transform:none!important;
}}

/* ── tip bar ── */
.notif-tip{{background:{_CARD};border:1px solid {_BOR};border-radius:13px;
    padding:12px 16px;display:flex;align-items:center;gap:10px;
    margin:14px 0;font-size:.76rem;color:{_SUB};line-height:1.55;}}
.notif-tip strong{{color:{_TXT};}}

/* ── empty state ── */
.notif-empty{{text-align:center;padding:3rem 2rem;background:{_CARD};
    border-radius:22px;border:1.5px dashed {_BOR};}}
.notif-empty-icon{{font-size:3rem;opacity:.5;display:block;margin-bottom:12px;}}
.notif-empty-title{{font-size:.95rem;font-weight:700;color:{_TXT};margin-bottom:6px;}}
.notif-empty-sub{{font-size:.78rem;color:{_SUB};line-height:1.6;}}

@media(max-width:600px){{
    .notif-stat-grid{{grid-template-columns:repeat(3,1fr);gap:8px;}}
    .notif-stat-num{{font-size:1.6rem;}}
    .nc{{padding:14px 15px;border-radius:14px;}}
    .nc-icon{{font-size:1.4rem;min-width:36px;}}
}}
</style>
""", unsafe_allow_html=True)

    # ── HERO ─────────────────────────────────────────────────────────────────
    hero_title = t("Notifications", "सूचनाएं")
    hero_sub   = t(
        "Stay updated with your complaints &amp; government schemes",
        "अपनी शिकायतों और सरकारी योजनाओं की ताजा जानकारी पाएं"
    )
    st.markdown(
        "<div class='prem-hero'>"
        "<div class='prem-hero-title'>🔔 " + hero_title + "</div>"
        "<div class='prem-hero-sub'>" + hero_sub + "</div>"
        "<div class='prem-hero-stats'>"
        "<div class='prem-hstat h-blue'><div class='prem-hstat-num'>🔔</div>"
        "<div class='prem-hstat-lbl'>" + t("All","सभी") + "</div></div>"
        "<div class='prem-hstat h-amber'><div class='prem-hstat-num'>🔴</div>"
        "<div class='prem-hstat-lbl'>" + t("Unread","अपठित") + "</div></div>"
        "<div class='prem-hstat h-green'><div class='prem-hstat-num'>✅</div>"
        "<div class='prem-hstat-lbl'>" + t("Read","पढ़ा") + "</div></div>"
        "<div class='prem-hstat'><div class='prem-hstat-num'>📜</div>"
        "<div class='prem-hstat-lbl'>" + t("Schemes","योजनाएं") + "</div></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    # ── login guard ───────────────────────────────────────────────────────────
    if not uid:
        st.warning(t("Please login to view notifications.",
                      "कृपया सूचनाएं देखने के लिए लॉगिन करें।"))
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button(t("← Back to Dashboard", "← डैशबोर्ड पर वापस"),
                         use_container_width=True, key="notif_back_nologin"):
                st.session_state.screen = "user_dashboard"
                st.rerun()
        return

    # ── fetch ─────────────────────────────────────────────────────────────────
    notifs_raw = api("get", f"/schemes/user/notifications/{uid}")
    notifs     = notifs_raw if isinstance(notifs_raw, list) else []

    # ── empty state ───────────────────────────────────────────────────────────
    if not notifs:
        st.markdown(
            "<div class='notif-empty'>"
            "<span class='notif-empty-icon'>🔕</span>"
            "<div class='notif-empty-title'>" + t("No notifications yet","अभी तक कोई सूचना नहीं") + "</div>"
            "<div class='notif-empty-sub'>"
            + t("When your complaint status changes or new schemes launch, you will see them here.",
                "जब आपकी शिकायत की स्थिति बदलती है या नई योजनाएं लॉन्च होती हैं, तो वे यहां दिखेंगी।")
            + "</div></div>",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button(t("← Back to Dashboard", "← डैशबोर्ड पर वापस"),
                         use_container_width=True, key="notif_back_empty"):
                st.session_state.screen = "user_dashboard"
                st.rerun()
        return

    unread = [n for n in notifs if not n.get("is_read")]
    read   = [n for n in notifs if n.get("is_read")]

    # ── STAT CARDS ────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='notif-stat-grid'>"
        "<div class='notif-stat all'>"
        "<div class='notif-stat-num' style='color:" + _A1 + ";'>" + str(len(notifs)) + "</div>"
        "<div class='notif-stat-lbl'>🔔 " + t("Total","कुल") + "</div>"
        "</div>"
        "<div class='notif-stat unread'>"
        "<div class='notif-stat-num' style='color:#EF4444;'>" + str(len(unread)) + "</div>"
        "<div class='notif-stat-lbl'>🔴 " + t("Unread","अपठित") + "</div>"
        "</div>"
        "<div class='notif-stat read'>"
        "<div class='notif-stat-num' style='color:#10B981;'>" + str(len(read)) + "</div>"
        "<div class='notif-stat-lbl'>✅ " + t("Read","पढ़ा") + "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── ACTION BUTTONS ────────────────────────────────────────────────────────
    st.markdown(
        "<div class='prem-section-header'>⚡ " + t("Actions","कार्रवाई") + "</div>",
        unsafe_allow_html=True,
    )
    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        if unread and st.button(
            t("✅ Mark all read", "✅ सभी पढ़े मार्क करें"),
            use_container_width=True, key="notif_mark_all",
        ):
            resp = api("put", f"/schemes/notifications/mark-all-read/{uid}")
            if resp.get("success"):
                st.success(t("All marked as read!", "सभी पढ़े गए!"))
                st.rerun()
    with ac2:
        if st.button(
            t("🗑 Clear all", "🗑 सभी हटाएं"),
            use_container_width=True, key="notif_clear_all",
        ):
            resp = api("delete", f"/schemes/notifications/clear-all/{uid}")
            if resp.get("success"):
                st.success(t("All cleared!", "सभी हटा दी गईं!"))
                st.rerun()
    with ac3:
        if st.button(t("🔄 Refresh", "🔄 रिफ्रेश"),
                     use_container_width=True, key="notif_refresh"):
            st.rerun()

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def _fmt_time(time_str):
        if not time_str:
            return "—"
        for fmt in ["%d %b %Y, %I:%M %p", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
            try:
                dt    = datetime.strptime(str(time_str).strip(), fmt)
                delta = datetime.now() - dt
                if delta.days == 0:
                    return t("Today","आज") + " " + dt.strftime("%I:%M %p")
                elif delta.days == 1:
                    return t("Yesterday","कल") + " " + dt.strftime("%I:%M %p")
                elif delta.days < 7:
                    return dt.strftime("%A, %I:%M %p")
                return dt.strftime("%d %b %Y, %I:%M %p")
            except ValueError:
                continue
        return str(time_str)

    def _get_icon(title: str) -> str:
        tl = title.lower()
        if any(w in tl for w in ("complaint","शिकायत")): return "📢"
        if any(w in tl for w in ("scheme","योजना")):     return "📜"
        if any(w in tl for w in ("rating","रेटिंग")):    return "⭐"
        if any(w in tl for w in ("resolved","समाधान")):  return "✅"
        if any(w in tl for w in ("rejected","अस्वीकृत")):return "❌"
        if any(w in tl for w in ("progress","प्रगति")):  return "🔄"
        if any(w in tl for w in ("update","अपडेट")):     return "🔄"
        return "🔔"

    def _clean(text: str) -> str:
        """Strip HTML tags and normalize whitespace, then HTML-escape for safe display."""
        if not text:
            return ""
        # unescape any existing HTML entities first
        text = _html.unescape(str(text))
        # remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        # normalize whitespace
        return " ".join(text.split()).strip()

    # ── RENDER ONE NOTIFICATION ───────────────────────────────────────────────
    def render_notif(n, show_read_btn=False, dimmed=False):
        nid      = n.get("id", "")
        is_unrd  = not n.get("is_read")
        raw_title   = _clean(n.get("title", ""))
        raw_message = _clean(n.get("message", ""))
        display_t   = _fmt_time(n.get("time", ""))
        icon        = _get_icon(raw_title)

        # safe — both inputs are already stripped of HTML tags
        safe_title   = _html.escape(raw_title)
        safe_message = _html.escape(raw_message)
        safe_time    = _html.escape(display_t)

        unrd_cls = "unread" if is_unrd else ""
        dim_cls  = "dimmed" if dimmed else ""
        new_badge = "<span class='nc-new'>NEW</span>" if is_unrd else ""
        dot_html  = "<div class='nc-dot'></div>" if is_unrd else ""

        # Single complete HTML block — all values pre-escaped
        card_html = (
            "<div class='nc " + unrd_cls + " " + dim_cls + "'>"
            + dot_html +
            "<div class='nc-inner'>"
            "<div class='nc-icon'>" + icon + "</div>"
            "<div class='nc-body'>"
            "<div class='nc-title'>" + safe_title + " " + new_badge + "</div>"
            "<div class='nc-msg'>" + safe_message + "</div>"
            "<div class='nc-time'>🕐 " + safe_time + "</div>"
            "</div></div></div>"
        )
        st.markdown(card_html, unsafe_allow_html=True)

        # Action buttons — native Streamlit, outside any HTML block
        if show_read_btn or True:

            st.markdown(
                "<div class='notif-actions'>",
                unsafe_allow_html=True
            )

            btn_cols = st.columns(
                [1.2, 1.2, 5],
                gap="small"
            )

            btn_index = 0

            # READ BUTTON
            if show_read_btn and is_unrd:

                with btn_cols[btn_index]:

                    st.markdown(
                        "<div class='notif-read-btn'>",
                        unsafe_allow_html=True
                    )

                    if st.button(
                        t("✓ Read","✓ पढ़ा"),
                        key=f"notif_read_{nid}",
                        use_container_width=True
                    ):

                        resp = api(
                            "put",
                            f"/schemes/notifications/{nid}/read"
                        )

                        if resp.get("success"):

                            st.rerun()

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

                btn_index += 1

            # CLEAR BUTTON
            with btn_cols[btn_index]:

                st.markdown(
                    "<div class='notif-del-btn'>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "🗑 Clear",
                    key=f"notif_del_{nid}",
                    use_container_width=True,
                    help=t("Delete","हटाएं")
                ):

                    resp = api(
                        "delete",
                        f"/schemes/notifications/{nid}"
                    )

                    if resp.get("success"):

                        st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

        st.markdown(
            "<div style='height:4px'></div>",
            unsafe_allow_html=True
        )

    # ── UNREAD SECTION ────────────────────────────────────────────────────────
    if unread:
        st.markdown(
            "<div class='ng-label'>🔴 " + t("Unread","अपठित")
            + " (" + str(len(unread)) + ")</div>",
            unsafe_allow_html=True,
        )
        for n in unread:
            render_notif(n, show_read_btn=True, dimmed=False)

    # ── READ SECTION — grouped by date ────────────────────────────────────────
    if read:
        today     = datetime.now().date()
        yesterday = today - timedelta(days=1)
        week_ago  = today - timedelta(days=7)

        g_today   = t("Today","आज")
        g_yest    = t("Yesterday","कल")
        g_week    = t("This Week","इस सप्ताह")
        g_older   = t("Older","पुराना")

        groups = {g_today: [], g_yest: [], g_week: [], g_older: []}

        for n in read:
            placed = False
            for fmt in ["%d %b %Y, %I:%M %p","%Y-%m-%dT%H:%M:%S","%Y-%m-%d %H:%M:%S"]:
                try:
                    dt   = datetime.strptime(str(n.get("time","")).strip(), fmt)
                    date = dt.date()
                    if date == today:
                        groups[g_today].append(n)
                    elif date == yesterday:
                        groups[g_yest].append(n)
                    elif date > week_ago:
                        groups[g_week].append(n)
                    else:
                        groups[g_older].append(n)
                    placed = True
                    break
                except ValueError:
                    continue
            if not placed:
                groups[g_older].append(n)

        for group_name, items in groups.items():
            if not items:
                continue
            st.markdown(
                "<div class='ng-label'>✅ "
                + _html.escape(group_name)
                + " (" + str(len(items)) + ")</div>",
                unsafe_allow_html=True,
            )
            for n in items:
                render_notif(n, show_read_btn=False, dimmed=True)

    # ── TIP BAR ───────────────────────────────────────────────────────────────
    tip_txt = t(
        "Notifications are sent when your complaint status changes, feedback is requested, or new schemes are announced.",
        "सूचनाएं तब भेजी जाती हैं जब शिकायत की स्थिति बदलती है, प्रतिक्रिया मांगी जाती है, या नई योजनाएं आती हैं।"
    )
    st.markdown(
        "<div class='notif-tip'>💡 <span><strong>" + t("Tip:","सुझाव:") + "</strong> " + tip_txt + "</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    bc1, bc2, bc3 = st.columns([1, 2, 1])
    with bc2:
        if st.button(t("← Back to Dashboard","← डैशबोर्ड पर वापस"),
                     use_container_width=True, key="notif_back"):
            st.session_state.screen = "user_dashboard"
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# SCHEMES
# ═════════════════════════════════════════════════════════════════════════════
def pg_schemes():
    _apply_layout("user")  
    lang = st.session_state.language
    user = st.session_state.user or {}

    def t(en, hi):
        return en if lang == "en" else hi

    dark  = st.session_state.get("dark_mode", False)
    _CARD = "#10161F" if dark else "#FFFFFF"
    _BG2  = "#080C14" if dark else "#F4F6FB"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
    _G1   = "#059669"
    _G2   = "#10B981"

    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)

    # ── PREMIUM CSS + JS DROPDOWN FIX ────────────────────────────────────────
    css = (
        "<style>"

        # Hero
        ".sch-hero{background:linear-gradient(135deg,#059669 0%,#10B981 50%,#06B6D4 100%);"
        "border-radius:22px;padding:28px 28px 24px;color:#fff;margin-bottom:24px;"
        "position:relative;overflow:hidden;box-shadow:0 16px 48px rgba(5,150,105,.28);}"
        ".sch-hero::before{content:'';position:absolute;top:-60px;right:-60px;"
        "width:240px;height:240px;border-radius:50%;background:rgba(255,255,255,.07);pointer-events:none;}"
        ".sch-hero::after{content:'';position:absolute;bottom:-80px;left:20%;"
        "width:200px;height:200px;border-radius:50%;background:rgba(255,255,255,.04);pointer-events:none;}"
        ".sch-hero-title{font-family:'Sora',sans-serif;font-size:1.75rem;font-weight:800;"
        "color:#fff;margin-bottom:6px;position:relative;z-index:1;text-shadow:0 2px 12px rgba(0,0,0,.15);}"
        ".sch-hero-sub{font-size:.87rem;color:rgba(255,255,255,.88);position:relative;z-index:1;font-weight:500;}"
        ".sch-hero-stats{display:grid;grid-template-columns:repeat(3,1fr);"
        "gap:10px;margin-top:20px;position:relative;z-index:1;}"
        ".sch-hstat{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.20);"
        "border-radius:14px;padding:12px 10px;text-align:center;backdrop-filter:blur(10px);transition:background .18s;}"
        ".sch-hstat:hover{background:rgba(255,255,255,.22);}"
        ".sch-hstat-num{font-family:'Sora',sans-serif;font-size:1.7rem;font-weight:800;"
        "color:#fff;line-height:1;margin-bottom:4px;}"
        ".sch-hstat-lbl{font-size:.62rem;font-weight:700;text-transform:uppercase;"
        "letter-spacing:.08em;color:rgba(255,255,255,.70);}"

        # Search
        ".sch-search-wrap .stTextInput>div>div>input{"
        "border-radius:30px!important;padding:12px 20px!important;font-size:.88rem!important;"
        "border:1.5px solid #E2E8F4!important;background:#fff!important;"
        "box-shadow:0 2px 12px rgba(5,150,105,.07)!important;"
        "transition:border-color .18s,box-shadow .18s!important;}"
        ".sch-search-wrap .stTextInput>div>div>input:focus{"
        "border-color:#10B981!important;box-shadow:0 0 0 3px rgba(16,185,129,.14)!important;}"

        # Filter chips
        ".sch-chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px;padding:4px 0;}"
        ".sch-chip{padding:7px 16px;border-radius:30px;font-size:.76rem;font-weight:700;"
        "border:1.5px solid " + _BOR + ";background:" + _CARD + ";color:" + _SUB + ";"
        "white-space:nowrap;pointer-events:none;transition:all .18s;}"
        ".sch-chip.active{background:linear-gradient(135deg,#059669,#10B981);"
        "color:#fff;border-color:transparent;box-shadow:0 4px 14px rgba(16,185,129,.32);}"

        # Hide invisible filter buttons
        ".sch-filter-btns .stButton>button{"
        "opacity:0!important;height:0!important;padding:0!important;"
        "margin:0!important;min-height:0!important;overflow:hidden!important;}"

        # Scheme card
        ".sch-card{background:" + _CARD + ";border:1px solid " + _BOR + ";"
        "border-left:4px solid #10B981;border-radius:18px;"
        "padding:18px 20px;margin-bottom:8px;"
        "display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap;"
        "box-shadow:0 2px 10px rgba(15,23,42,.06);"
        "transition:transform .20s ease,box-shadow .20s,border-left-color .20s;"
        "position:relative;overflow:hidden;}"
        ".sch-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;"
        "background:linear-gradient(90deg,#059669,#10B981,#06B6D4);"
        "transform:scaleX(0);transition:transform .22s ease;"
        "transform-origin:left;border-radius:0 0 18px 18px;}"
        ".sch-card:hover{transform:translateY(-3px);"
        "box-shadow:0 12px 32px rgba(16,185,129,.14);border-left-color:#059669;}"
        ".sch-card:hover::after{transform:scaleX(1);}"
        ".sch-card-icon{width:48px;height:48px;border-radius:14px;flex-shrink:0;"
        "background:linear-gradient(135deg,rgba(16,185,129,.12),rgba(6,182,212,.08));"
        "border:1.5px solid rgba(16,185,129,.20);"
        "display:flex;align-items:center;justify-content:center;font-size:1.4rem;margin-top:2px;}"
        ".sch-card-body{flex:1;min-width:180px;}"
        ".sch-card-title{font-weight:800;font-size:.95rem;color:" + _TXT + ";margin-bottom:6px;line-height:1.4;}"
        ".sch-card-cat{font-size:.67rem;font-weight:800;background:#ECFDF5;color:#059669;"
        "padding:3px 10px;border-radius:20px;border:1px solid #BBF7D0;"
        "display:inline-block;margin-bottom:8px;text-transform:uppercase;letter-spacing:.04em;}"
        ".sch-card-desc{font-size:.81rem;color:" + _SUB + ";line-height:1.65;}"
        ".sch-card-meta{font-size:.70rem;color:#94A3B8;margin-top:10px;"
        "display:flex;gap:14px;flex-wrap:wrap;align-items:center;"
        "padding-top:10px;border-top:1px solid " + _BOR + ";}"

        # Detail panel
        ".sch-detail{background:" + _BG2 + ";border:1.5px solid #BBF7D0;"
        "border-radius:16px;padding:20px 22px;margin:2px 0 12px;"
        "animation:prem-fade-up .28s ease both;}"
        ".sch-detail-title{font-family:'Sora',sans-serif;font-size:1rem;font-weight:800;"
        "color:" + _TXT + ";margin-bottom:14px;display:flex;align-items:center;gap:10px;}"
        ".sch-detail-field{font-size:.82rem;color:" + _SUB + ";margin-bottom:10px;line-height:1.7;}"
        ".sch-detail-field strong{color:" + _TXT + ";font-weight:700;}"
        ".sch-detail-badge{display:inline-flex;align-items:center;gap:6px;"
        "background:" + _CARD + ";border:1px solid #BBF7D0;border-radius:10px;"
        "padding:6px 14px;font-size:.75rem;font-weight:700;color:#059669;margin:4px 6px 4px 0;}"

        # Empty
        ".sch-empty{text-align:center;padding:3.5rem 2rem;background:" + _CARD + ";"
        "border-radius:22px;border:1.5px dashed " + _BOR + ";margin:1rem 0;}"
        ".sch-empty-icon{font-size:3.2rem;opacity:.55;display:block;margin-bottom:14px;}"
        ".sch-empty-title{font-size:.98rem;font-weight:700;color:" + _TXT + ";margin-bottom:8px;}"
        ".sch-empty-sub{font-size:.79rem;color:" + _SUB + ";line-height:1.6;}"

        # Responsive
        "@media(max-width:600px){"
        ".sch-card{padding:14px;gap:10px;}"
        ".sch-hero{padding:22px 18px 18px;border-radius:18px;}"
        ".sch-hero-title{font-size:1.4rem;}"
        ".sch-hero-stats{grid-template-columns:repeat(3,1fr);}"
        ".sch-chips{gap:6px;}"
        ".sch-chip{padding:6px 12px;font-size:.70rem;}}"
        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)

    # JS nuclear dropdown fix
    st.markdown(
        "<script>(function(){"
        "var r=["
        "\"[data-baseweb='popover']{background:#FFFFFF!important;border-radius:16px!important;border:1.5px solid #E2E8F4!important;box-shadow:0 12px 40px rgba(15,23,42,.14)!important;overflow:hidden!important;}\","
        "\"[data-baseweb='popover'] *{background-color:#FFFFFF!important;color:#0F172A!important;}\","
        "\"[data-baseweb='menu']{background:#FFFFFF!important;padding:6px!important;}\","
        "\"[data-baseweb='menu'] *{background-color:#FFFFFF!important;color:#0F172A!important;}\","
        "\"[data-baseweb='option']{background:#FFFFFF!important;color:#0F172A!important;border-radius:10px!important;padding:9px 14px!important;margin:2px 0!important;font-size:.85rem!important;cursor:pointer!important;}\","
        "\"[data-baseweb='option']:hover{background:#F0FDF4!important;color:#059669!important;}\","
        "\"[aria-selected='true'][data-baseweb='option']{background:rgba(16,185,129,.10)!important;color:#059669!important;font-weight:700!important;}\","
        "\"[role='listbox']{background:#FFFFFF!important;padding:6px!important;}\","
        "\"[role='listbox'] *{background-color:#FFFFFF!important;color:#0F172A!important;}\","
        "\"[role='option']{background:#FFFFFF!important;color:#0F172A!important;border-radius:10px!important;padding:9px 14px!important;}\","
        "\"[role='option']:hover{background:#F0FDF4!important;color:#059669!important;}\","
        "\"body > div[data-portal='true']{background:#FFFFFF!important;}\","
        "\"body > div[data-portal='true'] *{background-color:#FFFFFF!important;color:#0F172A!important;}\""
        "];"
        "function inject(){try{var sh=null;"
        "for(var i=0;i<document.styleSheets.length;i++){try{if(document.styleSheets[i].cssRules!==null){sh=document.styleSheets[i];break;}}catch(e){}}"
        "if(!sh){var s=document.createElement('style');document.head.appendChild(s);sh=s.sheet;}"
        "r.forEach(function(x){try{sh.insertRule(x,sh.cssRules.length);}catch(e){}});}catch(e){}}"
        "inject();[300,800,1500].forEach(function(d){setTimeout(inject,d);});"
        "new MutationObserver(function(ms){ms.forEach(function(m){m.addedNodes.forEach(function(n){"
        "if(n.nodeType===1&&(n.dataset&&n.dataset.portal==='true'||n.querySelector&&n.querySelector('[data-baseweb=\"popover\"]')))inject();"
        "});});}).observe(document.body,{childList:true,subtree:false});"
        "})();</script>",
        unsafe_allow_html=True
    )

    # ════════════════════════════════════════════════════════
    # FETCH
    # ════════════════════════════════════════════════════════
    schemes = api("get", "/schemes/all")
    schemes = schemes if isinstance(schemes, list) else []

    total_schemes = len(schemes)
    categories    = sorted({s.get("category", "general") for s in schemes})
    total_cats    = len(categories)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="sch-hero">'
        '<div class="sch-hero-title">📜 ' + t('Government Schemes', 'सरकारी योजनाएं') + '</div>'
        '<div class="sch-hero-sub">'
        + t('Welfare schemes and benefits for citizens',
            'नागरिकों के लिए कल्याणकारी योजनाएं और लाभ') +
        '</div>'
        '<div class="sch-hero-stats">'
        '<div class="sch-hstat"><div class="sch-hstat-num">' + str(total_schemes) + '</div>'
        '<div class="sch-hstat-lbl">' + t('Total Schemes', 'कुल योजनाएं') + '</div></div>'
        '<div class="sch-hstat"><div class="sch-hstat-num">' + str(total_cats) + '</div>'
        '<div class="sch-hstat-lbl">' + t('Categories', 'श्रेणियां') + '</div></div>'
        '<div class="sch-hstat"><div class="sch-hstat-num">🔔</div>'
        '<div class="sch-hstat-lbl">' + t('Subscribe', 'सदस्यता') + '</div></div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    if not schemes:
        st.markdown(
            '<div class="sch-empty"><span class="sch-empty-icon">📭</span>'
            '<div class="sch-empty-title">' + t('No schemes available yet', 'अभी कोई योजना उपलब्ध नहीं') + '</div>'
            '<div class="sch-empty-sub">' + t('Check back later.', 'बाद में देखें।') + '</div></div>',
            unsafe_allow_html=True
        )
        ec1, ec2, ec3 = st.columns([1, 2, 1])
        with ec2:
            if st.button(t("← Back to Dashboard", "← डैशबोर्ड पर वापस"),
                         key="sch_back_empty", use_container_width=True):
                st.session_state.screen = "user_dashboard"
                st.rerun()
        return

    # ════════════════════════════════════════════════════════
    # FILTER STATE
    # ════════════════════════════════════════════════════════
    if "sch_cat_filter" not in st.session_state:
        st.session_state.sch_cat_filter = "all"
    if "sch_search"     not in st.session_state:
        st.session_state.sch_search     = ""
    if "sch_open"       not in st.session_state:
        st.session_state.sch_open       = set()

    categories = sorted({s.get("category", "general") for s in schemes})

    # ════════════════════════════════════════════════════════
    # SEARCH BAR
    # ════════════════════════════════════════════════════════
    st.markdown(
        '<div class="prem-section-header">🔍 '
        + t('Search & Filter', 'खोजें और फ़िल्टर करें') + '</div>',
        unsafe_allow_html=True
    )
    with st.container():
        st.markdown('<div class="sch-search-wrap">', unsafe_allow_html=True)
        search_val = st.text_input(
            label="search",
            label_visibility="collapsed",
            placeholder="🔍 " + t("Search schemes by name or keyword…",
                                   "नाम या कीवर्ड से योजनाएं खोजें…"),
            value=st.session_state.sch_search,
            key="sch_search_input",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    if search_val != st.session_state.sch_search:
        st.session_state.sch_search = search_val
        st.rerun()

    # ════════════════════════════════════════════════════════
    # CATEGORY CHIPS
    # ════════════════════════════════════════════════════════
    CHIP_ICONS = {
        "health": "🏥", "education": "🎓", "agriculture": "🌾", "housing": "🏠",
        "finance": "💰", "women": "👩", "youth": "👦", "elderly": "👴",
        "disability": "♿", "employment": "💼", "general": "📋",
    }
    all_filters = [("all", t("All", "सभी"), "📋")] + [
        (cat, cat.title(), CHIP_ICONS.get(cat.lower(), "🏷")) for cat in categories
    ]

    chips_html = '<div class="sch-chips">'
    for fval, flbl, ficon in all_filters:
        act = "active" if st.session_state.sch_cat_filter == fval else ""
        chips_html += '<div class="sch-chip ' + act + '">' + ficon + ' ' + flbl + '</div>'
    chips_html += "</div>"
    st.markdown(chips_html, unsafe_allow_html=True)

    # Invisible click-target buttons
    st.markdown('<div class="sch-filter-btns">', unsafe_allow_html=True)
    chip_cols = st.columns(len(all_filters))
    for ccol, (fval, flbl, ficon) in zip(chip_cols, all_filters):
        with ccol:
            if st.button(f"{ficon} {flbl}", key=f"sch_flt_{fval}",
                         use_container_width=True):
                st.session_state.sch_cat_filter = fval
                st.session_state.sch_open = set()
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # APPLY FILTERS
    # ════════════════════════════════════════════════════════
    filtered = schemes
    if st.session_state.sch_cat_filter != "all":
        filtered = [s for s in filtered
                    if s.get("category", "") == st.session_state.sch_cat_filter]

    if st.session_state.sch_search:
        term = st.session_state.sch_search.strip().lower()
        filtered = [s for s in filtered
                    if term in s.get("title", "").lower()
                    or term in s.get("description", "").lower()
                    or term in s.get("title_hi", "").lower()
                    or term in s.get("description_hi", "").lower()]

    # result count
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'flex-wrap:wrap;gap:8px;margin:12px 0 8px;">'
        '<span style="background:#ECFDF5;color:#059669;border:1.5px solid #BBF7D0;'
        'border-radius:20px;padding:5px 16px;font-size:.78rem;font-weight:800;">'
        + t("Showing", "दिखा रहे हैं") + " <strong>" + str(len(filtered)) + "</strong> "
        + t("scheme(s)", "योजनाएं") + "</span>"
        '<span style="font-size:.72rem;color:#94A3B8;font-weight:600;">'
        + str(total_schemes - len(filtered)) + " "
        + t("hidden by filter", "फ़िल्टर से छिपे") + "</span></div>",
        unsafe_allow_html=True
    )

    # ════════════════════════════════════════════════════════
    # EMPTY FILTERED STATE
    # ════════════════════════════════════════════════════════
    if not filtered:
        st.markdown(
            '<div class="sch-empty"><span class="sch-empty-icon">🔍</span>'
            '<div class="sch-empty-title">'
            + t('No matching schemes found', 'कोई मिलती योजना नहीं मिली') +
            '</div><div class="sch-empty-sub">'
            + t('Try a different search or filter.', 'अलग खोज या फ़िल्टर आज़माएं।') +
            '</div></div>',
            unsafe_allow_html=True
        )
        cc1, cc2, cc3 = st.columns([1, 2, 1])
        with cc2:
            if st.button(t("Clear Filters", "फ़िल्टर साफ़ करें"),
                         key="sch_clear", use_container_width=True):
                st.session_state.sch_cat_filter = "all"
                st.session_state.sch_search     = ""
                st.session_state.sch_open       = set()
                st.rerun()
        return

    # ════════════════════════════════════════════════════════
    # SCHEME CARDS
    # ════════════════════════════════════════════════════════
    CATEGORY_ICONS = {
        "health":      "🏥", "education": "🎓", "agriculture": "🌾",
        "housing":     "🏠", "finance":   "💰", "women":       "👩",
        "youth":       "👦", "elderly":   "👴", "disability":  "♿",
        "employment":  "💼", "general":   "📋",
    }

    for scheme in filtered:
        sid     = scheme.get("id", "")
        s_title = (scheme.get("title_hi") if lang == "hi" and scheme.get("title_hi")
                   else scheme.get("title", "Untitled"))
        s_desc  = (scheme.get("description_hi") if lang == "hi" and scheme.get("description_hi")
                   else scheme.get("description", ""))
        s_cat   = scheme.get("category", "general")
        s_icon  = CATEGORY_ICONS.get(s_cat.lower(), "📋")
        s_date  = scheme.get("created_at", "—")
        s_by    = scheme.get("uploaded_by", t("Government", "सरकार"))
        s_short = s_desc[:110] + "…" if len(s_desc) > 110 else s_desc
        is_open = sid in st.session_state.sch_open

        st.markdown(
            '<div class="sch-card">'
            '<div class="sch-card-icon">' + s_icon + '</div>'
            '<div class="sch-card-body">'
            '<div class="sch-card-title">' + html.escape(s_title) + '</div>'
            '<span class="sch-card-cat">' + html.escape(s_cat.title()) + '</span>'
            '<div class="sch-card-desc">' + html.escape(s_short) + '</div>'
            '<div class="sch-card-meta">'
            '<span>📅 ' + str(s_date) + '</span>'
            '<span>🏛 ' + html.escape(str(s_by)) + '</span>'
            '</div></div></div>',
            unsafe_allow_html=True
        )

        # action row — unchanged
        ac1, ac2, ac3, ac4 = st.columns([2, 1, 1, 1])
        with ac2:
            if st.button("🔊 " + t("Listen", "सुनें"),
                         key=f"sch_voice_{sid}", use_container_width=True):
                speak_text(s_desc, lang)
        with ac3:
            detail_lbl = (t("▲ Hide", "▲ छुपाएं") if is_open
                          else t("📖 Details", "📖 विवरण"))
            if st.button(detail_lbl, key=f"sch_det_{sid}", use_container_width=True):
                if is_open:
                    st.session_state.sch_open.discard(sid)
                else:
                    st.session_state.sch_open.add(sid)
                st.rerun()
        with ac4:
            if st.button("🔔 " + t("Notify", "सूचित करें"),
                         key=f"sch_notif_{sid}", use_container_width=True):
                resp = api("post", f"/schemes/{sid}/subscribe",
                           json={"user_id": user.get("user_id")})
                if resp.get("success"):
                    st.success(t("✅ You'll be notified about this scheme.",
                                 "✅ इस योजना के बारे में आपको सूचित किया जाएगा।"))
                else:
                    st.info(t("Already subscribed or unavailable.",
                              "पहले से सदस्यता है या उपलब्ध नहीं।"))

        # expandable detail panel — unchanged logic
        if is_open:
            s_img = scheme.get("image_url", "")
            st.markdown('<div class="sch-detail">', unsafe_allow_html=True)

            st.markdown(
                '<div class="sch-detail-title">'
                '<div style="width:34px;height:34px;border-radius:10px;'
                'background:linear-gradient(135deg,#059669,#10B981);'
                'display:flex;align-items:center;justify-content:center;'
                'font-size:.9rem;box-shadow:0 4px 10px rgba(5,150,105,.28);">📜</div>'
                + html.escape(s_title) + '</div>',
                unsafe_allow_html=True
            )

            if s_img:
                try:
                    img_url = (f"https://bfo-backend.onrender.com{s_img}"
                               if s_img.startswith("/") else s_img)
                    di1, di2 = st.columns([1, 2])
                    with di1:
                        st.image(img_url, use_container_width=True)
                    with di2:
                        st.markdown(
                            '<div class="sch-detail-field"><strong>'
                            + t("Description", "विवरण") + ':</strong><br>'
                            + html.escape(s_desc) + '</div>',
                            unsafe_allow_html=True
                        )
                except Exception:
                    st.markdown(
                        '<div class="sch-detail-field"><strong>'
                        + t("Description", "विवरण") + ':</strong><br>'
                        + html.escape(s_desc) + '</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    '<div class="sch-detail-field"><strong>'
                    + t("Description", "विवरण") + ':</strong><br>'
                    + html.escape(s_desc) + '</div>',
                    unsafe_allow_html=True
                )

            s_desc_hi = scheme.get("description_hi", "")
            if s_desc_hi and lang == "en":
                st.markdown(
                    '<div class="sch-detail-field"><strong>हिंदी विवरण:</strong><br>'
                    + html.escape(s_desc_hi) + '</div>',
                    unsafe_allow_html=True
                )

            st.markdown(
                '<div style="display:flex;flex-wrap:wrap;margin-top:6px;">'
                '<span class="sch-detail-badge">📂 ' + html.escape(s_cat.title()) + '</span>'
                '<span class="sch-detail-badge">📅 ' + str(s_date) + '</span>'
                '<span class="sch-detail-badge">🏛 ' + html.escape(str(s_by)) + '</span>'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

        # gradient divider
        st.markdown(
            '<div style="height:1px;background:linear-gradient(90deg,'
            'transparent,' + _BOR + ',transparent);margin:6px 0 10px;"></div>',
            unsafe_allow_html=True
        )

    # ════════════════════════════════════════════════════════
    # BACK BUTTON
    # ════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    bc1, bc2, bc3 = st.columns([1, 2, 1])
    with bc2:
        if st.button(t("← Back to Dashboard", "← डैशबोर्ड पर वापस"),
                     key="sch_back", use_container_width=True):
            st.session_state.screen = "user_dashboard"
            st.rerun()
# ═════════════════════════════════════════════════════════════════════════════
# AI ASSISTANT
# ═════════════════════════════════════════════════════════════════════════════
def pg_assistant():
    _apply_layout("user")  
    lang = st.session_state.get("language", "en")
    from frontend.pages.assistant import get_bot_response

    def _(en, hi):
        return en if lang == "en" else hi

    # ---------- Modern UI CSS ----------
    st.markdown("""
    <style>
    /* Chat container */
    .stChatMessage {
        background: transparent !important;
    }
    /* User message bubble */
    div[data-testid="stChatMessageUser"] div[data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border-radius: 20px 20px 4px 20px !important;
        box-shadow: 0 4px 12px rgba(99,102,241,0.2) !important;
    }
    /* Assistant message bubble */
    div[data-testid="stChatMessageAssistant"] div[data-testid="stChatMessageContent"] {
        background: rgba(255,255,255,0.08) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #1e293b !important;
        border-radius: 20px 20px 20px 4px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    /* Quick reply chips */
    .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        justify-content: center;
        margin: 1.5rem 0;
    }
    .chip {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 40px;
        padding: 0.5rem 1.2rem;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.2s ease;
        cursor: pointer;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .chip:hover {
        background: #6366f1;
        border-color: #6366f1;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99,102,241,0.3);
    }
    /* Hero header */
    .assistant-hero {
        background: linear-gradient(135deg, #10b981, #059669);
        border-radius: 28px;
        padding: 1.8rem;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 35px -10px rgba(0,0,0,0.15);
    }
    .assistant-hero::after {
        content: '✨';
        position: absolute;
        bottom: 10px;
        right: 20px;
        font-size: 3rem;
        opacity: 0.2;
        transform: rotate(15deg);
    }
    .hero-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 0.95rem;
        color: rgba(255,255,255,0.9);
    }
    /* Mic button row */
    .mic-row {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        height: 100%;
    }
    .mic-btn {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border: none;
        border-radius: 50%;
        width: 48px;
        height: 48px;
        font-size: 1.3rem;
        color: white;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 4px 12px rgba(99,102,241,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .mic-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 20px rgba(99,102,241,0.5);
    }
    .mic-btn.recording {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        animation: pulseMic 1.2s infinite;
    }
    @keyframes pulseMic {
        0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.6); }
        70% { box-shadow: 0 0 0 12px rgba(239,68,68,0); }
        100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
    }
    /* Chat input styling */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important;
        border: 1px solid #e2e8f0 !important;
        background: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------- Hero Header ----------
    st.markdown(f"""
    <div class="assistant-hero">
        <div class="hero-title">🤖 {_('AI Assistant', 'एआई सहायक')}</div>
        <div class="hero-sub">{_('Ask me anything about complaints, schemes, or the portal', 'शिकायतों, योजनाओं या पोर्टल के बारे में कुछ भी पूछें')}</div>
    </div>
    """, unsafe_allow_html=True)

    # ---------- Initialize chat history ----------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({"role": "assistant", "content": get_bot_response("hello", lang)})

    # ---------- Display messages ----------
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ---------- Quick reply chips ----------
    quick_items = [
        ("📢 " + _("How to file a complaint?", "शिकायत कैसे दर्ज करें?"), "file complaint"),
        ("🔍 " + _("Track my complaint", "मेरी शिकायत ट्रैक करें"), "track complaint"),
        ("📜 " + _("Government schemes", "सरकारी योजनाएं"), "schemes"),
        ("⏱️ " + _("What is SLA?", "SLA क्या है?"), "sla"),
        ("⭐ " + _("How to rate an official?", "अधिकारी को कैसे रेट करें?"), "rating"),
        ("🏢 " + _("Department contacts", "विभाग संपर्क"), "departments"),
    ]
    st.markdown('<div class="chips">', unsafe_allow_html=True)
    cols = st.columns(min(3, len(quick_items)))
    for i, (label, intent) in enumerate(quick_items):
        with cols[i % 3]:
            if st.button(label, key=f"chip_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": label})
                with st.chat_message("user"):
                    st.markdown(label)
                response = get_bot_response(intent, lang)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Chat input + Microphone (fully functional) ----------
    col_input, col_mic = st.columns([6, 1])
    with col_input:
        user_input = st.chat_input(_("Type your message...", "अपना संदेश लिखें..."))
    with col_mic:
        mic_html = f"""
        <div class="mic-row">
            <button id="modernMicBtn" class="mic-btn">🎤</button>
        </div>
        <script>
        (function() {{
            const micBtn = document.getElementById('modernMicBtn');
            if (!micBtn) return;
            let recognition = null;

            function findChatInput() {{
                return window.parent.document.querySelector('div[data-testid="stChatInput"] textarea') ||
                       window.parent.document.querySelector('input[data-testid="stChatInput"]');
            }}

            function findSendButton() {{
                const btns = window.parent.document.querySelectorAll('button');
                for (let btn of btns) {{
                    const aria = btn.getAttribute('aria-label') || '';
                    if (aria === 'Send' || btn.innerText.includes('Send')) return btn;
                }}
                return null;
            }}

            function insertAndSend(text) {{
                const input = findChatInput();
                if (!input) return;
                input.value = text;
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                setTimeout(() => {{
                    const sendBtn = findSendButton();
                    if (sendBtn) sendBtn.click();
                }}, 200);
            }}

            micBtn.onclick = () => {{
                if (recognition) {{
                    recognition.stop();
                    recognition = null;
                    micBtn.classList.remove('recording');
                    micBtn.style.background = 'linear-gradient(135deg, #6366f1, #8b5cf6)';
                    return;
                }}
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {{
                    alert('Voice not supported. Please use Chrome/Edge.');
                    return;
                }}
                recognition = new SpeechRecognition();
                recognition.lang = '{'hi-IN' if lang == 'hi' else 'en-IN'}';
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.onstart = () => {{
                    micBtn.classList.add('recording');
                    micBtn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
                }};
                recognition.onresult = (e) => {{
                    const text = e.results[0][0].transcript;
                    insertAndSend(text);
                }};
                recognition.onend = () => {{
                    micBtn.classList.remove('recording');
                    micBtn.style.background = 'linear-gradient(135deg, #6366f1, #8b5cf6)';
                    recognition = null;
                }};
                recognition.start();
            }};
        }})();
        </script>
        """
        st.components.v1.html(mic_html, height=70)

    # ---------- Process typed input ----------
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        response = get_bot_response(user_input, lang)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
        st.rerun()

    # ---------- Utility buttons ----------
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(_("🗑️ Clear Chat", "🗑️ चैट साफ़ करें"), use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.chat_history.append({"role": "assistant", "content": get_bot_response("hello", lang)})
            st.rerun()
        if st.button(_("← Back to Dashboard", "← डैशबोर्ड पर वापस"), use_container_width=True):
            st.session_state.screen = "user_dashboard"
            st.rerun()

def pg_official_dashboard():
    
    _apply_layout("admin")  
    # ------------------- GET OFFICIAL DATA -------------------
    off = st.session_state.get("official", {})
    if not off:
        st.error("⚠️ Session missing. Please login again.")
        if st.button("Go to Login", use_container_width=True):
            for key in ["official", "role"]:
                st.session_state.pop(key, None)
            st.session_state.screen = "login_type"
            st.rerun()
        return

    dept_id = off.get("department_id")
    off_id = off.get("official_id")
    name = off.get("name", "Official")
    dept_name = off.get("department", "Department")
    email = off.get("email", "")

    if not dept_id or dept_id == "None":
        st.warning("⚠️ No department assigned. Contact admin.")
        with st.expander("📋 My Profile"):
            st.write(f"**Name:** {name}\n**Email:** {email}\n**Status:** Approved")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
        return

    # ------------------- FETCH COMPLAINTS -------------------
    # Assume dept_id is defined earlier (e.g., from session state or function param)
    comps = []

    try:

        with st.spinner("Loading complaints..."):

            resp = api(

                "get",

                f"/complaints/department/{dept_id}?status_filter=all"
            )

            if isinstance(resp, list):

                comps = resp

            else:

                st.warning(
                    f"Unexpected API response format: {type(resp)}"
                )

    except Exception as e:

        st.warning(
            f"Could not load complaints: {e}"
        )

    # ─────────────────────────────────────────────
    # DISPLAY COMPLAINTS
    # ─────────────────────────────────────────────

    if comps:

        for complaint in comps:

            is_emergency = complaint.get(
                "is_emergency",
                False
            )

            expander_label = (

                f"{complaint.get('id', '')}  ·  "

                f"{complaint.get('category', '').title()}  ·  "

                f"{complaint.get('department', complaint.get('user_name', ''))}"
            )

            if is_emergency:

                expander_label = (

                    f"🚨 {expander_label} - EMERGENCY"
                )

                border_color = "#dc2626"

            else:

                border_color = "#e5e7eb"

            # ─────────────────────────────────────────────
            # COMPLAINT CARD
            # ─────────────────────────────────────────────

            with st.expander(
                expander_label,
                expanded=False
            ):

                st.markdown(

                    f"""
                    <div style="
                        border:1px solid {border_color};
                        border-radius:16px;
                        padding:16px;
                        margin-bottom:12px;
                        background:var(--c-card);
                    ">
                    """,

                    unsafe_allow_html=True
                )

                # Complaint text
                st.write(

                    complaint.get(
                        "text",
                        "No complaint text"
                    )
                )

                # Status
                st.markdown(

                    f"""
                    <b>Status:</b>
                    {complaint.get('status', 'pending')}
                    """,

                    unsafe_allow_html=True
                )

                # Priority
                st.markdown(

                    f"""
                    <b>Priority:</b>
                    {complaint.get('priority', 'medium')}
                    """,

                    unsafe_allow_html=True
                )

                # ─────────────────────────────────────────────
                # IMAGE PREVIEW
                # ─────────────────────────────────────────────

                if complaint.get("image_path"):

                    img_url = (

                        f"{API_BASE}"

                        f"{complaint['image_path']}"
                    )

                    st.image(

                        img_url,

                        width=300,

                        caption="Attached Image"
                    )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

    else:

        st.info("No complaints found.")

    # ─────────────────────────────────────────────
    # STATISTICS
    # ─────────────────────────────────────────────

    total = len(comps)

    pending = sum(
        1
        for c in comps
        if c.get("status") == "pending"
    )

    in_progress = sum(
        1
        for c in comps
        if c.get("status") == "in_progress"
    )

    resolved = sum(
        1
        for c in comps
        if c.get("status") in (
            "resolved",
            "closed"
        )
    )

    resolution_rate = round(

        resolved / max(total, 1) * 100,

        1
    )

    resolution_rate = min(
        resolution_rate,
        100
    )
    # ------------------- STATISTICS -------------------
    total = len(comps)
    pending = sum(1 for c in comps if c.get("status") == "pending")
    in_progress = sum(1 for c in comps if c.get("status") == "in_progress")
    resolved = sum(1 for c in comps if c.get("status") in ("resolved", "closed"))
    resolution_rate = round(resolved / max(total, 1) * 100, 1)
    resolution_rate = min(resolution_rate, 100)   # ✅ Cap at 100%

    # ------------------- MODERN CSS -------------------
    st.markdown("""
    <style>
    /* ----- MODERN OFFICIAL DASHBOARD CSS ----- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Section */
    .hero-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 28px;
        padding: 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2);
    }
    .hero-card::after {
        content: '';
        position: absolute;
        top: -30%;
        right: -10%;
        width: 60%;
        height: 160%;
        background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
        transform: rotate(15deg);
    }
    .hero-avatar {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        width: 70px;
        height: 70px;
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .hero-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        line-height: 1.2;
    }
    .hero-dept {
        background: rgba(59,130,246,0.3);
        display: inline-block;
        padding: 4px 12px;
        border-radius: 40px;
        font-size: 0.8rem;
        color: #93c5fd;
        margin-top: 8px;
    }
    .hero-email {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    .hero-badge {
        background: rgba(16,185,129,0.2);
        padding: 6px 14px;
        border-radius: 40px;
        font-size: 0.8rem;
        color: #34d399;
        font-weight: 500;
    }
    
    /* Stats Cards */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .stat-card {
        background: white;
        border-radius: 24px;
        padding: 1.25rem;
        transition: all 0.2s;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -12px rgba(0,0,0,0.15);
        border-color: #cbd5e1;
    }
    .stat-number {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .stat-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-top: 6px;
    }
    
    /* Resolution Progress */
    .progress-container {
        background: white;
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    .progress-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .progress-bar-bg {
        height: 10px;
        background: #e2e8f0;
        border-radius: 20px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #10b981);
        border-radius: 20px;
        transition: width 0.4s;
    }
    
    /* Filter Bar */
    .filter-bar {
        background: white;
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        align-items: flex-end;
    }
    .filter-item {
        flex: 1;
        min-width: 150px;
    }
    
    /* Complaint Cards */
    .complaint-card {
        background: white;
        border-radius: 20px;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        transition: all 0.2s;
        overflow: hidden;
    }
    .complaint-card:hover {
        transform: translateX(5px);
        border-color: #3b82f6;
        box-shadow: 0 8px 20px -12px rgba(0,0,0,0.2);
    }
    .complaint-priority-high { border-left: 4px solid #ef4444; }
    .complaint-priority-medium { border-left: 4px solid #f59e0b; }
    .complaint-priority-low { border-left: 4px solid #10b981; }
    
    .complaint-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .badge-status {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 12px;
        border-radius: 40px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    .badge-pending { background: #fef3c7; color: #92400e; }
    .badge-in_progress { background: #dbeafe; color: #1e40af; }
    .badge-resolved { background: #d1fae5; color: #065f46; }
    .badge-closed { background: #f3f4f6; color: #374151; }
    .badge-rejected { background: #fee2e2; color: #991b1b; }
    
    .badge-priority {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 12px;
        border-radius: 40px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    .badge-priority-high { background: #fee2e2; color: #991b1b; }
    .badge-priority-medium { background: #fef3c7; color: #92400e; }
    .badge-priority-low { background: #d1fae5; color: #065f46; }
    
    .complaint-desc-box {
        background: #f8fafc;
        padding: 14px;
        border-radius: 16px;
        margin: 12px 0;
        border: 1px solid #e2e8f0;
        color: #0f172a;
        font-size: 0.9rem;
        line-height: 1.5;
        white-space: pre-wrap;
        word-wrap: break-word;
        max-height: 200px;
        overflow-y: auto;
    }
    
    .complaint-meta {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        font-size: 0.8rem;
        color: #475569;
        margin-bottom: 1rem;
    }
    
    .action-buttons {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-top: 0.5rem;
    }
    
    .btn-custom {
        border: none;
        padding: 6px 14px;
        border-radius: 40px;
        font-weight: 600;
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-primary { background: #3b82f6; color: white; }
    .btn-success { background: #10b981; color: white; }
    .btn-danger { background: #ef4444; color: white; }
    .btn-warning { background: #f59e0b; color: white; }
    .btn-secondary { background: #64748b; color: white; }
    .btn-custom:hover { transform: translateY(-2px); filter: brightness(1.05); }
    
    .empty-state {
        text-align: center;
        padding: 3rem;
        background: #f8fafc;
        border-radius: 28px;
        border: 1px solid #e2e8f0;
    }
    
    .tips-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 100%);
        border-radius: 20px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid #ccf0e6;
    }
    
    @media (max-width: 768px) {
        .stat-grid { grid-template-columns: repeat(2, 1fr); gap: 1rem; }
        .hero-name { font-size: 1.3rem; }
        .hero-card { padding: 1.25rem; }
        .hero-avatar { width: 50px; height: 50px; font-size: 1.5rem; }
    }
    </style>
    """, unsafe_allow_html=True)

    # ------------------- HERO SECTION -------------------
    st.markdown(f"""
    <div class="hero-card">
        <div style="display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;">
            <div class="hero-avatar">🏢</div>
            <div style="flex:1;">
                <div class="hero-name">{html.escape(str(name))}</div>
                <div class="hero-dept">{html.escape(str(dept_name))}</div>
                <div class="hero-email">{html.escape(str(email))}</div>
            </div>
            <div class="hero-badge">
                ⚡ Active · {datetime.now().strftime('%d %b %Y')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ------------------- STATISTICS CARDS -------------------
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card"><div class="stat-number" style="color:#3b82f6">{total}</div><div class="stat-label">📋 Total Complaints</div></div>
        <div class="stat-card"><div class="stat-number" style="color:#f59e0b">{pending}</div><div class="stat-label">⏳ Pending</div></div>
        <div class="stat-card"><div class="stat-number" style="color:#06b6d4">{in_progress}</div><div class="stat-label">🔄 In Progress</div></div>
        <div class="stat-card"><div class="stat-number" style="color:#10b981">{resolved}</div><div class="stat-label">✅ Resolved</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ------------------- RESOLUTION RATE -------------------
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-header">
            <span>📊 Resolution Rate</span>
            <span style="font-weight:800; color:#10b981;">{resolution_rate}%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-fill" style="width:{resolution_rate}%"></div>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:0.5rem; font-size:0.7rem; color:#475569;">
            <span>✅ {resolved} resolved</span>
            <span>📋 {total - resolved} remaining</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ------------------- FILTER BAR -------------------
    with st.container():
        col1, col2, col3, col4 = st.columns([2,2,2,1])
        with col1:
            status_filter = st.selectbox("📌 Status", ["All","Pending","In Progress","Resolved","Rejected"], key="off_status", label_visibility="collapsed")
        with col2:
            priority_filter = st.selectbox("⚡ Priority", ["All","High","Medium","Low"], key="off_priority", label_visibility="collapsed")
        with col3:
            search_term = st.text_input("🔍 Search", placeholder="ID, citizen, location...", key="off_search", label_visibility="collapsed")
        with col4:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

    # Apply filters
    filtered = comps[:]
    if status_filter != "All":
        filtered = [c for c in filtered if c.get("status","").replace("_"," ").title() == status_filter]
    if priority_filter != "All":
        filtered = [c for c in filtered if c.get("priority","").title() == priority_filter]
    if search_term:
        sl = search_term.lower()
        filtered = [c for c in filtered if sl in c.get("complaint_id","").lower() or sl in c.get("user_name","").lower() or sl in c.get("location","").lower() or sl in c.get("description","").lower()]

    st.markdown(f'<div style="display:flex; justify-content:space-between; margin:1rem 0 0.75rem;"><span style="font-weight:600;">📋 Complaints</span><span style="background:#f1f5f9; padding:2px 12px; border-radius:30px; font-size:0.75rem;">{len(filtered)} of {total}</span></div>', unsafe_allow_html=True)

    # ------------------- COMPLAINT CARDS -------------------
    if filtered:
        for idx, c in enumerate(filtered, start=1):
            # Extract data
            complaint_id = c.get("complaint_id", "N/A")
            category = c.get("category", "other").title()
            status = c.get("status", "pending")
            priority = c.get("priority", "medium")
            description = c.get("description", "")
            safe_desc = html.escape(description).replace('\n', '<br>')
            user_name = c.get("user_name", "Unknown")
            phone = c.get("user_phone", "N/A")
            location = c.get("location", "N/A")
            created = c.get("created_at", "")
            
            # Status badge
            status_map = {
                "pending": ("⏳ Pending", "badge-pending"),
                "in_progress": ("🔄 In Progress", "badge-in_progress"),
                "resolved": ("✅ Resolved", "badge-resolved"),
                "closed": ("🔒 Closed", "badge-closed"),
                "rejected": ("❌ Rejected", "badge-rejected")
            }
            status_text, status_class = status_map.get(status, ("📋 " + status, "badge-pending"))
            
            # Priority badge
            priority_map = {
                "high": ("🔴 High", "badge-priority-high"),
                "medium": ("🟠 Medium", "badge-priority-medium"),
                "low": ("🟢 Low", "badge-priority-low")
            }
            priority_text, priority_class = priority_map.get(priority, ("⚪ Normal", "badge-priority-medium"))
            
            # Card priority class for left border
            border_class = f"complaint-priority-{priority}"
            
            # Preview for expander
            preview = description[:60] + "..." if len(description) > 60 else description
            safe_preview = html.escape(preview)
            st.markdown(
                f"""
                <div style="
                    font-size:14px;
                    font-weight:700;
                    color:#3b82f6;
                    margin:10px 0 6px 4px;
                ">
                    Complaint #{idx}
                </div>
                """,
                unsafe_allow_html=True
            )
            with st.expander(
                f"{idx}. #{complaint_id} - {category} - {safe_preview}",
                expanded=False
            ):
                st.markdown(f"""
                <div class="complaint-card {border_class}" style="padding: 1rem; margin-top: 0.5rem;">
                    <div class="complaint-header">
                        <div>
                            <span class="badge-status {status_class}">{status_text}</span>
                            <span class="badge-priority {priority_class}" style="margin-left: 8px;">{priority_text}</span>
                        </div>
                        <div class="complaint-meta" style="margin:0; font-size:0.7rem;">
                            📅 {created}
                        </div>
                    </div>
                    <div class="complaint-desc-box">
                        {safe_desc}
                    </div>
                    <div class="complaint-meta">
                        <span>👤 {html.escape(user_name)}</span>
                        <span>📞 {html.escape(phone)}</span>
                        <span>📍 {html.escape(location)}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show citizen feedback if any
                if c.get("feedback") == "satisfied":
                    st.success("👍 Citizen satisfied with resolution")
                elif c.get("feedback") == "not_satisfied":
                    st.warning("⚠️ Citizen not satisfied – complaint reopened")
                
                # Action buttons based on status
                st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
                
                if status == "pending":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔄 Start Processing", key=f"start_{complaint_id}_{idx}", use_container_width=True):
                            resp = api("put", f"/complaints/{complaint_id}/status", json={"status":"in_progress","note":"Started","official_id":off_id})
                            if resp.get("success"): st.success("Started!"); st.rerun()
                    with col2:
                        if st.button("✅ Resolve Directly", key=f"resolve_{complaint_id}_{idx}", use_container_width=True):
                            resp = api("put", f"/complaints/{complaint_id}/status", json={"status":"resolved","note":"Resolved","official_id":off_id})
                            if resp.get("success"): st.success("Resolved!"); st.balloons(); st.rerun()
                    with col3:
                        if st.button("❌ Reject", key=f"reject_{complaint_id}_{idx}", use_container_width=True):
                            resp = api("put", f"/complaints/{complaint_id}/status", json={"status":"rejected","note":"Rejected","official_id":off_id})
                            if resp.get("success"): st.warning("Rejected"); st.rerun()
                
                elif status == "in_progress":
                    note = st.text_area("📝 Resolution note", key=f"note_{complaint_id}_{idx}", placeholder="Describe how issue was fixed...", height=80)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Mark Resolved", key=f"resolve_final_{complaint_id}_{idx}", use_container_width=True):
                            resp = api("put", f"/complaints/{complaint_id}/status", json={"status":"resolved","note":note or "Resolved","official_id":off_id})
                            if resp.get("success"): st.success("Resolved!"); st.balloons(); st.rerun()
                    with col2:
                        if st.button("📝 Update Note", key=f"update_note_{complaint_id}_{idx}", use_container_width=True):
                            if note:
                                resp = api("put", f"/complaints/{complaint_id}/status", json={"status":"in_progress","note":note,"official_id":off_id})
                                if resp.get("success"): st.success("Note updated"); st.rerun()
                elif status == "resolved":
                    st.info("✅ This complaint is resolved. It will be closed after citizen feedback.")
                elif status == "rejected":
                    st.warning("❌ This complaint was rejected.")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        if comps:
            st.markdown("""
            <div class="empty-state">
                <div style="font-size:3rem;">🔍</div>
                <h3>No matching complaints</h3>
                <p>Try adjusting your filters.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div style="font-size:3rem;">📭</div>
                <h3>No complaints yet</h3>
                <p>Complaints assigned to your department will appear here.</p>
            </div>
            """, unsafe_allow_html=True)

    # ------------------- TIPS SECTION -------------------

def pg_live_dashboard():
    _apply_layout("admin")  
    dark  = st.session_state.get("dark_mode", False)
    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)

    _CARD = "#10161F" if dark else "#FFFFFF"
    _BG2  = "#080C14" if dark else "#F4F6FB"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
    _A1   = "#6366F1"
    _A2   = "#8B5CF6"

    st.markdown(f"""
<style>
/* ── hero ── */
.live-hero{{
    background:linear-gradient(135deg,#0C4A6E 0%,#0369A1 50%,#1e1b4b 100%);
    border-radius:22px;padding:1.75rem 2rem;margin-bottom:1.75rem;
    position:relative;overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,0.25);
}}
.live-hero::before{{content:'';position:absolute;top:-60px;right:-60px;
    width:220px;height:220px;border-radius:50%;
    background:radial-gradient(circle,rgba(255,255,255,0.08) 0%,transparent 70%);
    pointer-events:none;}}
.live-hero-title{{font-family:'Sora',sans-serif;font-size:1.75rem;font-weight:800;
    color:#fff;margin-bottom:5px;position:relative;z-index:1;}}
.live-hero-sub{{font-size:0.86rem;color:rgba(255,255,255,0.65);
    position:relative;z-index:1;font-weight:500;}}
.live-hero-badge{{
    display:inline-flex;align-items:center;gap:6px;
    background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);
    border-radius:20px;padding:4px 12px;
    font-size:0.72rem;font-weight:700;color:#fff;
    margin-top:10px;position:relative;z-index:1;
}}
.live-dot{{
    width:8px;height:8px;border-radius:50%;
    background:#4ADE80;
    box-shadow:0 0 0 0 rgba(74,222,128,0.6);
    animation:live-pulse 1.8s infinite;
    flex-shrink:0;
}}
@keyframes live-pulse{{
    0%{{box-shadow:0 0 0 0 rgba(74,222,128,0.6);}}
    70%{{box-shadow:0 0 0 8px rgba(74,222,128,0);}}
    100%{{box-shadow:0 0 0 0 rgba(74,222,128,0);}}
}}

/* ── section header ── */
.live-sec{{font-size:0.70rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.10em;color:{_SUB};margin:22px 0 12px;
    display:flex;align-items:center;gap:10px;}}
.live-sec::before{{content:'';width:4px;height:16px;
    background:linear-gradient(180deg,#0EA5E9,{_A1});border-radius:3px;flex-shrink:0;}}
.live-sec::after{{content:'';flex:1;height:1px;
    background:linear-gradient(to right,{_BOR},transparent);}}

/* ── update time ── */
.live-update{{
    font-size:0.72rem;color:{_SUB};font-weight:600;
    text-align:right;margin-bottom:14px;
    display:flex;align-items:center;justify-content:flex-end;gap:6px;
}}

/* ── stat cards ── */
.live-stat{{
    background:{_CARD};border:1px solid {_BOR};border-radius:18px;
    padding:20px 14px 16px;text-align:center;position:relative;overflow:hidden;
    box-shadow:0 2px 8px rgba(15,23,42,0.06);
    transition:transform 0.20s,box-shadow 0.20s;
}}
.live-stat::before{{content:'';position:absolute;top:0;left:0;right:0;
    height:4px;border-radius:18px 18px 0 0;}}
.live-stat:hover{{transform:translateY(-3px);
    box-shadow:0 10px 28px rgba(99,102,241,0.12);}}
.live-stat-num{{font-family:'Sora',sans-serif;font-size:2.2rem;font-weight:800;
    line-height:1.1;margin-bottom:5px;}}
.live-stat-lbl{{font-size:0.68rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.08em;color:{_SUB};}}

/* ── activity card ── */
.live-act-card{{
    background:{_CARD};border:1px solid {_BOR};
    border-left:4px solid #10B981;border-radius:14px;
    padding:13px 16px;margin-bottom:8px;
    box-shadow:0 2px 6px rgba(15,23,42,0.05);
    transition:transform 0.18s;
}}
.live-act-card:hover{{transform:translateX(4px);}}
.live-act-id{{font-size:0.72rem;font-weight:700;color:#10B981;
    font-family:'Courier New',monospace;
    background:rgba(16,185,129,0.12);padding:2px 8px;border-radius:6px;
    display:inline-block;margin-bottom:5px;}}
.live-act-desc{{font-size:0.79rem;color:{_SUB};line-height:1.5;margin-bottom:5px;}}
.live-act-time{{font-size:0.68rem;color:{_SUB};}}

/* ── empty ── */
.live-empty{{
    text-align:center;padding:2.5rem 2rem;
    background:{_CARD};border-radius:18px;border:1.5px dashed {_BOR};
}}
.live-empty-icon{{font-size:2.5rem;opacity:0.5;display:block;margin-bottom:10px;}}
.live-empty-txt{{font-size:0.85rem;color:{_SUB};}}

/* ── countdown bar ── */
.live-cd-wrap{{
    background:{_BOR};border-radius:10px;height:6px;
    overflow:hidden;margin-top:6px;
}}
.live-cd-fill{{
    height:100%;border-radius:10px;
    background:linear-gradient(90deg,#0EA5E9,{_A1});
    animation:live-countdown 30s linear forwards;
}}
@keyframes live-countdown{{from{{width:100%;}}to{{width:0%;}}}}

@media(max-width:600px){{
    .live-hero{{padding:1.4rem 1rem;border-radius:18px;}}
    .live-hero-title{{font-size:1.4rem;}}
}}
</style>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # SESSION-SAFE AUTO-REFRESH
    # Uses st.session_state counter + st.rerun() via a
    # JS postMessage so the Streamlit session is preserved.
    # Falls back to a "Refresh Now" button if JS is blocked.
    # ════════════════════════════════════════════════════════
    REFRESH_SECS = 30   # longer interval — 5s was too aggressive

    # inject JS that calls Streamlit's internal rerun trigger
    # by clicking a hidden button after the interval
    st.markdown(
        f"""
<script>
(function(){{
    var delay = {REFRESH_SECS * 1000};
    setTimeout(function(){{
        // find the hidden refresh trigger button and click it
        var btns = window.parent.document.querySelectorAll('button');
        for(var i=0;i<btns.length;i++){{
            if(btns[i].innerText.includes('__live_refresh__')){{
                btns[i].click(); break;
            }}
        }}
    }}, delay);
}})();
</script>
""",
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════
    # HERO
    # ════════════════════════════════════════════════════════
    now_str = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
    st.markdown(
        "<div class='live-hero'>"
        "<div class='live-hero-title'>📡 Live Dashboard</div>"
        "<div class='live-hero-sub'>"
        "Real-time complaint monitoring — auto-refreshes every 30 seconds"
        "</div>"
        "<div class='live-hero-badge'>"
        "<span class='live-dot'></span>"
        f"LIVE &nbsp;·&nbsp; Last updated: {now_str}"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════
    # FETCH STATS
    # ════════════════════════════════════════════════════════
    stats = api("get", "/admin/stats")
    if "error" in stats:
        st.error(f"Error fetching stats: {stats['error']}")
        return

    # ════════════════════════════════════════════════════════
    # STAT CARDS
    # ════════════════════════════════════════════════════════
    st.markdown("<div class='live-sec'>📊 Live Metrics</div>", unsafe_allow_html=True)

    LIVE_METRICS = [
        (stats.get("total_complaints",0), "📋 Total",       "#6366F1",
         "linear-gradient(90deg,#6366F1,#8B5CF6)"),
        (stats.get("pending",0),          "⏳ Pending",      "#F59E0B",
         "linear-gradient(90deg,#F59E0B,#D97706)"),
        (stats.get("in_progress",0),      "🔄 In Progress",  "#0EA5E9",
         "linear-gradient(90deg,#0EA5E9,#0369A1)"),
        (stats.get("resolved",0),         "✅ Resolved",     "#10B981",
         "linear-gradient(90deg,#10B981,#059669)"),
    ]

    m_cols = st.columns(4)
    for col, (val, lbl, clr, grad) in zip(m_cols, LIVE_METRICS):
        with col:
            st.markdown(
                f"<div class='live-stat'>"
                f"<div style='position:absolute;top:0;left:0;right:0;height:4px;"
                f"background:{grad};border-radius:18px 18px 0 0;'></div>"
                f"<div class='live-stat-num' style='color:{clr};'>{val}</div>"
                f"<div class='live-stat-lbl'>{lbl}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # resolution rate bar
    pct = max(0, min(100, stats.get("resolution_rate", 0)))
    bar_clr = "#22C55E" if pct>=70 else "#F59E0B" if pct>=40 else "#EF4444"
    st.markdown(
        f"<div style='background:{_CARD};border:1px solid {_BOR};"
        f"border-radius:14px;padding:14px 18px;margin-top:12px;'>"
        f"<div style='display:flex;justify-content:space-between;"
        f"font-size:0.78rem;font-weight:700;color:{_TXT};margin-bottom:7px;'>"
        f"<span>Overall Resolution Rate</span>"
        f"<span style='color:{bar_clr};'>{pct}%</span></div>"
        f"<div style='background:{_BOR};border-radius:10px;height:8px;overflow:hidden;'>"
        f"<div style='width:{pct}%;height:100%;border-radius:10px;"
        f"background:linear-gradient(90deg,{bar_clr},{bar_clr}CC);'></div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════
    # RECENT ACTIVITY (last 30 min resolved)
    # ════════════════════════════════════════════════════════
    st.markdown("<div class='live-sec'>📡 Recent Resolution Activity (last 30 min)</div>",
                unsafe_allow_html=True)

    all_complaints = api("get", "/complaints/all")
    recent_resolved = []

    if isinstance(all_complaints, list):
        now_ts = datetime.now()
        DATE_FMTS = [
            "%d %b %Y, %I:%M %p",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M",
        ]
        for c in all_complaints:
            if c.get("status") not in ("resolved","closed"):
                continue
            raw = c.get("updated_at") or c.get("created_at","")
            if not raw:
                continue
            parsed = None
            for fmt in DATE_FMTS:
                try:
                    parsed = datetime.strptime(str(raw).strip(), fmt)
                    break
                except ValueError:
                    continue
            if parsed and (now_ts - parsed).total_seconds() < 1800:
                recent_resolved.append({**c, "_parsed_dt": parsed})

        recent_resolved.sort(key=lambda x: x["_parsed_dt"], reverse=True)

    if recent_resolved:
        for c in recent_resolved[:10]:
            cid   = c.get("complaint_id","—")
            desc  = c.get("description","")[:110]
            when  = c.get("updated_at") or c.get("created_at","Recently")
            cat   = c.get("category","").title()
            st.markdown(
                f"<div class='live-act-card'>"
                f"<span class='live-act-id'>#{cid}</span>"
                f"{'  <span style=\"font-size:0.68rem;color:' + _SUB + ';margin-left:6px;\">' + cat + '</span>' if cat else ''}"
                f"<div class='live-act-desc'>{desc}{'…' if len(c.get('description',''))>110 else ''}</div>"
                f"<div class='live-act-time'>✅ Resolved · {when}</div>"
                f"</div> \n",unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<div class='live-empty'>"
            "<span class='live-empty-icon'>🕐</span>"
            "<div class='live-empty-txt'>"
            "No complaints resolved in the last 30 minutes.<br>"
            "The list will update automatically."
            "</div></div>",
            unsafe_allow_html=True,
        )

    # ════════════════════════════════════════════════════════
    # COUNTDOWN + REFRESH BUTTON
    # ════════════════════════════════════════════════════════
    st.markdown(
        f"<div style='font-size:0.72rem;color:{_SUB};margin-top:18px;margin-bottom:4px;'>"
        f"🔄 Auto-refreshes in {REFRESH_SECS}s</div>"
        f"<div class='live-cd-wrap'><div class='live-cd-fill'></div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    rc1, rc2, rc3 = st.columns([1, 2, 1])
    with rc2:
        # This button is the session-safe refresh trigger.
        # The JS above looks for text '__live_refresh__' to auto-click it.
        # We label it normally for display; add hidden marker via help text.
        # if st.button(
        #     "🔄 Refresh Now",
        #     key="live_refresh_btn",
        #     use_container_width=True,
        #     help="__live_refresh__",   # JS searches button text; help is read by JS too
        # ):
            st.rerun()

def pg_official_leaderboard():
    _apply_layout("admin")  

    off       = st.session_state.get("official", {})
    dept_id   = off.get("department_id")
    dept_name = str(off.get("department") or "Your Department")
    off_id    = off.get("official_id")

    # ── FIX 1: _bar_grad defined HERE — top of function, available everywhere ──
    def _bar_grad(pct):
        if pct < 40:  return "linear-gradient(90deg,#EF4444,#F97316)"
        if pct < 70:  return "linear-gradient(90deg,#F59E0B,#EAB308)"
        return "linear-gradient(90deg,#6366F1,#10B981)"

    def _bar_color(pct):
        """Solid color for bar fills (no gradient string splitting needed)."""
        if pct < 40:  return "#EF4444"
        if pct < 70:  return "#F59E0B"
        return "#6366F1"

    # ── PREMIUM CSS ───────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    /* ── Leaderboard row ── */
    .lb-row {
        display:flex; align-items:center; gap:16px;
        background:#FFFFFF;
        border:1.5px solid #E2E8F4;
        border-radius:18px; padding:16px 20px;
        margin:8px 0; position:relative; overflow:hidden;
        transition:transform .18s ease, box-shadow .18s ease, border-color .18s;
    }
    .lb-row::before {
        content:''; position:absolute;
        top:0; left:0; bottom:0; width:4px;
        background:linear-gradient(180deg,#6366F1,#818CF8);
        border-radius:4px 0 0 4px;
    }
    .lb-row:hover {
        transform:translateX(6px);
        box-shadow:0 8px 28px rgba(99,102,241,.13);
        border-color:#6366F1;
    }
    .lb-row.me {
        border:2px solid #6366F1 !important;
        background:linear-gradient(135deg,#f5f3ff 0%,#fff 100%) !important;
        box-shadow:0 4px 20px rgba(99,102,241,.14);
    }
    .lb-row.me::before { width:5px; background:linear-gradient(180deg,#4F46E5,#6366F1); }
    .lb-row.gold::before   { background:linear-gradient(180deg,#FFD700,#F59E0B); }
    .lb-row.silver::before { background:linear-gradient(180deg,#C0C0C0,#94A3B8); }
    .lb-row.bronze::before { background:linear-gradient(180deg,#CD7F32,#B45309); }
    .lb-row.ineligible     { opacity:.55; }

    .lb-medal {
        font-size:2rem; min-width:52px; text-align:center;
        font-weight:800; letter-spacing:-.03em; flex-shrink:0;
        color:#6366F1;
    }
    .lb-body  { flex:1; min-width:0; }
    .lb-name  {
        font-size:.93rem; font-weight:700;
        color:#0F172A; letter-spacing:-.01em;
        display:flex; align-items:center; gap:8px; flex-wrap:wrap;
        margin-bottom:4px;
    }
    .lb-you {
        background:#EEF2FF; color:#4F46E5;
        font-size:.62rem; font-weight:700;
        padding:2px 9px; border-radius:99px;
        letter-spacing:.04em; text-transform:uppercase;
        border:1px solid #C7D2FE;
    }
    .lb-unranked {
        background:#FEF9C3; color:#854D0E;
        font-size:.62rem; font-weight:700;
        padding:2px 9px; border-radius:99px;
        border:1px solid #FDE68A;
    }
    .lb-stats {
        display:flex; gap:18px; flex-wrap:wrap; margin-top:8px;
    }
    .lb-stat { text-align:center; min-width:52px; }
    .lb-stat-val {
        font-size:.92rem; font-weight:700;
        color:#0F172A; letter-spacing:-.02em;
    }
    .lb-stat-lbl {
        font-size:.60rem; color:#64748B;
        text-transform:uppercase; letter-spacing:.06em;
    }
    .lb-bar-wrap {
        background:#E2E8F4; border-radius:99px;
        height:7px; margin-top:10px; overflow:hidden;
    }
    .lb-bar-fill { height:100%; border-radius:99px; transition:width .4s ease; }

    /* ── Podium ── */
    .pod-grid   { display:grid; gap:14px; margin:12px 0 20px; }
    .pod-grid-1 { grid-template-columns:1fr; }
    .pod-grid-2 { grid-template-columns:repeat(2,1fr); }
    .pod-grid-3 { grid-template-columns:repeat(3,1fr); }
    .pod-card {
        background:#fff; border:1.5px solid #E2E8F4;
        border-radius:20px; padding:24px 16px 20px;
        text-align:center; position:relative; overflow:hidden;
        transition:transform .2s ease, box-shadow .2s ease;
        box-shadow:0 2px 10px rgba(15,23,42,.06);
    }
    .pod-card::after {
        content:''; position:absolute;
        bottom:0; left:0; right:0; height:3px;
        background:linear-gradient(90deg,#6366F1,#818CF8);
        transform:scaleX(0); transform-origin:left;
        transition:transform .22s ease;
    }
    .pod-card:hover { transform:translateY(-6px); box-shadow:0 16px 40px rgba(99,102,241,.16); }
    .pod-card:hover::after { transform:scaleX(1); }
    .pod-card.me {
        border:2px solid #6366F1 !important;
        background:linear-gradient(160deg,#f5f3ff 0%,#fff 100%) !important;
        box-shadow:0 4px 20px rgba(99,102,241,.18) !important;
    }
    .pod-you-badge {
        position:absolute; top:10px; right:10px;
        background:#6366F1; color:#fff;
        font-size:.58rem; font-weight:700;
        padding:2px 8px; border-radius:99px;
        letter-spacing:.04em; text-transform:uppercase;
    }
    .pod-rank-badge {
        width:38px; height:38px; border-radius:50%;
        background:linear-gradient(135deg,#6366F1,#818CF8);
        color:#fff; font-weight:800; font-size:.82rem;
        display:inline-flex; align-items:center; justify-content:center;
        margin-bottom:10px; box-shadow:0 4px 14px rgba(99,102,241,.35);
    }
    .pod-medal  { font-size:2.4rem; display:block; margin-bottom:6px; }
    .pod-name   { font-size:.95rem; font-weight:800; color:#0F172A; margin-bottom:4px; }
    .pod-dept   { font-size:.70rem; color:#64748B; margin-bottom:8px; }
    .pod-stars  { font-size:.88rem; color:#F59E0B; margin-bottom:8px; }
    .pod-stats  { font-size:.74rem; color:#64748B; }
    .pod-bar-wrap { background:#E2E8F4; border-radius:99px; height:5px; margin-top:12px; overflow:hidden; }
    .pod-bar-fill { height:100%; border-radius:99px; }

    /* ── Section label ── */
    .lb-section {
        font-size:.70rem; font-weight:700;
        text-transform:uppercase; letter-spacing:.10em;
        color:#64748B; margin:24px 0 12px;
        display:flex; align-items:center; gap:10px;
    }
    .lb-section::before {
        content:''; width:3px; height:14px;
        background:linear-gradient(180deg,#6366F1,#818CF8);
        border-radius:99px; flex-shrink:0;
    }
    .lb-section::after {
        content:''; flex:1; height:1px;
        background:linear-gradient(to right,#E2E8F4,transparent);
    }

    @media (max-width:600px) {
        .pod-grid-3 { grid-template-columns:1fr; }
        .pod-grid-2 { grid-template-columns:1fr; }
        .lb-stats   { gap:10px; }
        .lb-row     { border-radius:14px; padding:12px 14px; gap:10px; }
        .lb-medal   { font-size:1.6rem; min-width:38px; }
    }
    </style>
    """, unsafe_allow_html=True)

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="prem-hero" style="padding:28px 28px 24px;">'
        '<div class="prem-hero-avatar">🏆</div>'
        '<div class="prem-hero-title">Department Leaderboard</div>'
        '<div class="prem-hero-sub">'
        + html.escape(dept_name) +
        ' &nbsp;·&nbsp; Top Performers &amp; Your Standing'
        '</div>'
        '<div class="prem-hero-stats">'
        '<div class="prem-hstat h-amber"><div class="prem-hstat-num">🥇</div>'
        '<div class="prem-hstat-lbl">Top Ranked</div></div>'
        '<div class="prem-hstat h-blue"><div class="prem-hstat-num">⭐</div>'
        '<div class="prem-hstat-lbl">By Rating</div></div>'
        '<div class="prem-hstat h-green"><div class="prem-hstat-num">✅</div>'
        '<div class="prem-hstat-lbl">Resolved</div></div>'
        '<div class="prem-hstat"><div class="prem-hstat-num">📈</div>'
        '<div class="prem-hstat-lbl">Your Rank</div></div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    # Ranking rules
    with st.expander("ℹ️ How ranking works", expanded=False):
        st.write("**Eligibility:** At least **1 resolved complaint** required to be ranked.")
        st.write("**Primary factor:** Average citizen rating (higher = better).")
        st.write("**Tie-breaker:** Total resolved complaints.")
        st.write("**Resolution rate** = (resolved ÷ assigned) × 100%, capped at 100%.")
        st.write("**Average rating** = mean of all citizen feedback scores (1–5 ⭐).")

    # ── FETCH ─────────────────────────────────────────────────────────────────
    board         = api("get", "/admin/leaderboard/department/" + str(dept_id))
    board         = board if isinstance(board, list) else []
    all_officials = api("get", "/admin/officials/all")
    all_officials = all_officials if isinstance(all_officials, list) else []
    current       = next((o for o in all_officials if o.get("id") == off_id), {})

    # ── COMPUTED STATS ─────────────────────────────────────────────────────────
    total_resolved = current.get("total_resolved", 0)
    total_assigned = current.get("total_assigned", 0)
    success_rate   = min(round(total_resolved / max(total_assigned, 1) * 100, 1), 100)
    avg_rating     = min(max(current.get("avg_rating", 0), 0), 5)
    rating_count   = current.get("rating_count", 0)
    stars_str      = _rating_stars_display(avg_rating, rating_count)
    eligible_count = len([o for o in board if o.get("eligible")])
    user_entry     = next((o for o in board if o.get("id") == off_id), None)
    user_rank      = user_entry.get("rank") if user_entry else None

    # ── YOUR PERFORMANCE ───────────────────────────────────────────────────────
    st.markdown('<div class="lb-section">Your Performance</div>', unsafe_allow_html=True)

    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        st.metric("✅ Resolved", total_resolved)
    with pc2:
        st.metric("📋 Assigned", total_assigned)
    with pc3:
        st.metric("📈 Success Rate", str(success_rate) + "%")
    with pc4:
        st.metric("⭐ Avg Rating", str(round(avg_rating, 1)),
                  delta=str(rating_count) + " vote" + ("s" if rating_count != 1 else ""))

    st.progress(
        success_rate / 100,
        text="📈 Resolution Rate: " + str(success_rate) + "%"
    )

    # ── YOUR RANK CARD ─────────────────────────────────────────────────────────
    st.markdown('<div class="lb-section">Your Ranking</div>', unsafe_allow_html=True)

    if user_rank and isinstance(user_rank, int):
        medal      = {1: "🥇", 2: "🥈", 3: "🥉"}.get(user_rank, "🏅")
        rank_color = ("#FFD700" if user_rank == 1 else
                      "#C0C0C0" if user_rank == 2 else
                      "#CD7F32" if user_rank == 3 else "#6366F1")
        rank_cls   = ("rank-1" if user_rank == 1 else
                      "rank-2" if user_rank == 2 else
                      "rank-3" if user_rank == 3 else "")

        # FIX 2: uses _bar_grad() not the now-removed bar_grad variable
        st.markdown(
            '<div class="prem-lb-card ' + rank_cls + '" style="border:2px solid ' + rank_color + ';">'
            '<div class="prem-lb-rank" style="font-size:2.6rem;">' + medal + '</div>'
            '<div class="prem-lb-info">'
            '<div class="prem-lb-name">👑 Your Current Rank'
            '<span class="prem-lb-dept">' + html.escape(dept_name) + '</span></div>'
            '<div class="prem-lb-stats">'

            '<div class="prem-lb-stat-item">'
            '<div class="prem-lb-stat-lbl">🏅 Rank</div>'
            '<div class="prem-lb-stat-val" style="font-size:1.5rem;color:' + rank_color + ';">#' + str(user_rank) + '</div>'
            '</div>'

            '<div class="prem-lb-stat-item">'
            '<div class="prem-lb-stat-lbl">👥 Out of</div>'
            '<div class="prem-lb-stat-val">' + str(eligible_count) + '</div>'
            '</div>'

            '<div class="prem-lb-stat-item">'
            '<div class="prem-lb-stat-lbl">⭐ Rating</div>'
            '<div class="prem-lb-stat-val">' + str(round(avg_rating, 1)) + '</div>'
            '</div>'

            '<div class="prem-lb-stat-item">'
            '<div class="prem-lb-stat-lbl">✅ Resolved</div>'
            '<div class="prem-lb-stat-val">' + str(total_resolved) + '</div>'
            '</div>'

            '<div class="prem-lb-stat-item">'
            '<div class="prem-lb-stat-lbl">📈 Rate</div>'
            '<div class="prem-lb-stat-val">' + str(success_rate) + '%</div>'
            '</div>'

            '</div>'
            '<div style="margin-top:12px;">'
            '<div class="lb-bar-wrap">'
            '<div class="lb-bar-fill" style="width:' + str(success_rate) + '%;background:' + _bar_grad(success_rate) + ';"></div>'
            '</div></div>'
            '<div style="font-size:.78rem;color:#10B981;margin-top:10px;font-weight:600;">'
            '⬆️ Keep delivering quality service to climb higher!'
            '</div></div></div>',
            unsafe_allow_html=True
        )
    else:
        st.warning("🔹 Not yet ranked — resolve at least 1 complaint to appear on the leaderboard.")

    # ══════════════════════════════════════════════════════════════════════════
    #  TABS
    # ══════════════════════════════════════════════════════════════════════════
    tab1, tab2 = st.tabs(["🏆 Top Performers", "📋 All Officials"])

    # ── TAB 1: TOP PERFORMERS ─────────────────────────────────────────────────
    with tab1:
        eligible_list = [
            o for o in board
            if o.get("eligible") and isinstance(o.get("rank"), int)
        ]
        top10 = sorted(eligible_list, key=lambda x: x.get("rank", 999))[:10]

        if not top10:
            st.markdown("""
            <div class="prem-empty-state">
                <span class="prem-empty-icon">📭</span>
                <div class="prem-empty-title">No ranked officials yet</div>
                <div class="prem-empty-sub">Resolve at least 1 complaint to appear here.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            top3 = [o for o in top10 if o.get("rank") in (1, 2, 3)]

            # ── PODIUM ────────────────────────────────────────────────────
            if top3:
                n      = len(top3)
                g_cls  = "pod-grid-" + str(n)
                p_html = '<div class="lb-section">🏅 Podium</div>'
                p_html += '<div class="pod-grid ' + g_cls + '">'

                for o in sorted(top3, key=lambda x: x.get("rank")):
                    rank     = o.get("rank")
                    medal    = {1: "🥇", 2: "🥈", 3: "🥉"}[rank]
                    is_me    = o.get("id") == off_id
                    stars    = _rating_stars_display(
                        min(max(o.get("avg_rating", 0), 0), 5),
                        o.get("rating_count", 0)
                    )
                    res_rate = min(float(o.get("resolution_rate", 0)), 100.0)
                    me_cls   = "me" if is_me else ""
                    you_b    = '<div class="pod-you-badge">👑 YOU</div>' if is_me else ""
                    # FIX 4: use _bar_color() — no more fragile .split()
                    b_color  = _bar_color(res_rate)

                    p_html += (
                        '<div class="pod-card ' + me_cls + '">'
                        + you_b +
                        '<div class="pod-rank-badge">' + str(rank) + '</div>'
                        '<div class="pod-medal">' + medal + '</div>'
                        '<div class="pod-name">' + html.escape(o.get("name", "")) + '</div>'
                        '<div class="pod-dept">' + html.escape(o.get("department", dept_name)) + '</div>'
                        '<div class="pod-stars">' + stars + '</div>'
                        '<div class="pod-stats">✅ ' + str(o.get("total_resolved", 0)) +
                        ' resolved &nbsp;·&nbsp; 📈 ' + str(round(res_rate, 1)) + '%</div>'
                        '<div class="pod-bar-wrap">'
                        '<div class="pod-bar-fill" style="width:' + str(round(res_rate, 1)) +
                        '%;background:' + _bar_grad(res_rate) + ';"></div>'
                        '</div></div>'
                    )

                p_html += "</div>"
                st.markdown(p_html, unsafe_allow_html=True)

            # ── TOP 10 LIST ───────────────────────────────────────────────
            l_html = '<div class="lb-section">🏆 Top 10 Rankings</div>'

            for o in top10:
                rank     = o.get("rank")
                is_me    = o.get("id") == off_id
                res_rate = min(float(o.get("resolution_rate", 0)), 100.0)
                resolved = o.get("total_resolved", 0)
                assigned = o.get("total_assigned", 0)
                votes    = o.get("rating_count", 0)
                stars    = _rating_stars_display(
                    min(max(o.get("avg_rating", 0), 0), 5), votes
                )
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(
                    rank, "#" + str(rank) if isinstance(rank, int) else "🏅"
                )
                # FIX 3: .strip() prevents trailing-space class names
                row_cls = (
                    ("gold me" if is_me else "gold")   if rank == 1 else
                    ("silver me" if is_me else "silver") if rank == 2 else
                    ("bronze me" if is_me else "bronze") if rank == 3 else
                    ("me"   if is_me else "")
                )
                you_b = '<span class="lb-you">👑 You</span>' if is_me else ""

                l_html += (
                    '<div class="lb-row ' + row_cls.strip() + '">'
                    '<div class="lb-medal">' + str(medal) + '</div>'
                    '<div class="lb-body">'
                    '<div class="lb-name">' + html.escape(o.get("name", "Unknown")) + " " + you_b + '</div>'
                    '<div class="lb-stats">'
                    '<div class="lb-stat"><div class="lb-stat-val">' + stars + '</div><div class="lb-stat-lbl">Rating</div></div>'
                    '<div class="lb-stat"><div class="lb-stat-val">' + str(resolved) + '</div><div class="lb-stat-lbl">Resolved</div></div>'
                    '<div class="lb-stat"><div class="lb-stat-val">' + str(assigned) + '</div><div class="lb-stat-lbl">Assigned</div></div>'
                    '<div class="lb-stat"><div class="lb-stat-val">' + str(round(res_rate, 1)) + '%</div><div class="lb-stat-lbl">Rate</div></div>'
                    '<div class="lb-stat"><div class="lb-stat-val">' + str(votes) + '</div><div class="lb-stat-lbl">Votes</div></div>'
                    '</div>'
                    '<div class="lb-bar-wrap">'
                    '<div class="lb-bar-fill" style="width:' + str(round(res_rate, 1)) + '%;background:' + _bar_grad(res_rate) + ';"></div>'
                    '</div></div></div>'
                )

            st.markdown(l_html, unsafe_allow_html=True)

    # ── TAB 2: ALL OFFICIALS ──────────────────────────────────────────────────
    with tab2:
        all_sorted = sorted(
            board,
            key=lambda x: (
                not x.get("eligible"),
                x.get("rank", 999) if isinstance(x.get("rank"), int) else 999,
            ),
        )

        if not all_sorted:
            st.info("No officials found in this department.")
        else:
            a_html = '<div class="lb-section">All Officials in Department</div>'

            for o in all_sorted:
                is_me    = o.get("id") == off_id
                eligible = o.get("eligible", False)
                rank     = o.get("rank")
                res_rate = min(float(o.get("resolution_rate", 0)), 100.0)
                resolved = o.get("total_resolved", 0)
                assigned = o.get("total_assigned", 0)  # used once — FIX 2
                votes    = o.get("rating_count", 0)
                stars    = _rating_stars_display(
                    min(max(o.get("avg_rating", 0), 0), 5), votes
                )
                medal = (
                    {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, "#" + str(rank))
                    if eligible and isinstance(rank, int) else "📋"
                )
                rank_lbl = "#" + str(rank) if (eligible and isinstance(rank, int)) else "Not ranked"

                # FIX 3: clean row class without trailing spaces
                row_cls = (
                    ("gold me" if is_me else "gold")     if (rank == 1 and eligible) else
                    ("silver me" if is_me else "silver") if (rank == 2 and eligible) else
                    ("bronze me" if is_me else "bronze") if (rank == 3 and eligible) else
                    ("me"         if is_me else "ineligible" if not eligible else "")
                )
                you_b = '<span class="lb-you">👑 You</span>'       if is_me    else ""
                unr_b = '<span class="lb-unranked">Not ranked</span>' if not eligible else ""

                a_html += (
                    '<div class="lb-row ' + row_cls.strip() + '">'
                    '<div class="lb-medal">' + str(medal) + '</div>'
                    '<div class="lb-body">'
                    '<div class="lb-name">'
                    + html.escape(o.get("name", "Unknown")) + " " + you_b + " " + unr_b +
                    '</div>'
                    '<div class="lb-stats">'
                    # FIX 2: only ONE Assigned column now
                    '<div class="lb-stat"><div class="lb-stat-val">' + stars + '</div><div class="lb-stat-lbl">Rating</div></div>'
                    '<div class="lb-stat"><div class="lb-stat-val">' + str(resolved) + '</div><div class="lb-stat-lbl">Resolved</div></div>'
                    '<div class="lb-stat"><div class="lb-stat-val">' + str(assigned) + '</div><div class="lb-stat-lbl">Assigned</div></div>'
                    '<div class="lb-stat"><div class="lb-stat-val">' + str(round(res_rate, 1)) + '%</div><div class="lb-stat-lbl">Rate</div></div>'
                    '<div class="lb-stat"><div class="lb-stat-val">' + str(votes) + '</div><div class="lb-stat-lbl">Votes</div></div>'
                    '</div>'
                    '<div class="lb-bar-wrap">'
                    '<div class="lb-bar-fill" style="width:' + str(round(res_rate, 1)) + '%;background:' + _bar_grad(res_rate) + ';"></div>'
                    '</div></div></div>'
                )

            st.markdown(a_html, unsafe_allow_html=True)

    # ── TIP + REFRESH ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="prem-tip-bar">
        <span class="prem-tip-icon">💡</span>
        <span class="prem-tip-text">
            <strong>Tip:</strong> Resolve complaints faster and earn higher citizen ratings
            to climb the leaderboard. Ratings are submitted by citizens after resolution.
        </span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Refresh Leaderboard", use_container_width=True):
        st.rerun()
# ═════════════════════════════════════════════════════════════════════════════
# ADMIN SCREENS
# ═════════════════════════════════════════════════════════════════════════════
def pg_admin_dashboard():
    _apply_layout("admin")  
    dark  = st.session_state.get("dark_mode", False)
    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)

    _CARD = "#10161F" if dark else "#FFFFFF"
    _BG2  = "#080C14" if dark else "#F4F6FB"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
    _A1   = "#6366F1"
    _A2   = "#8B5CF6"

    st.markdown(f"""
<style>
/* ── admin hero ── */
.adm-hero{{
    background:linear-gradient(135deg,#1e1b4b 0%,#312e81 45%,#1e3a5f 100%);
    border-radius:22px;padding:2rem 2rem 1.75rem;
    margin-bottom:1.75rem;position:relative;overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,0.30);
}}
.adm-hero::before{{content:'';position:absolute;top:-70px;right:-70px;
    width:260px;height:260px;border-radius:50%;
    background:radial-gradient(circle,rgba(255,255,255,0.08) 0%,transparent 70%);
    pointer-events:none;}}
.adm-hero::after{{content:'';position:absolute;bottom:-80px;left:20%;
    width:220px;height:220px;border-radius:50%;
    background:radial-gradient(circle,rgba(139,92,246,0.12) 0%,transparent 70%);
    pointer-events:none;}}
.adm-hero-title{{font-family:'Sora',sans-serif;font-size:1.75rem;font-weight:800;
    color:#fff;margin-bottom:6px;position:relative;z-index:1;
    text-shadow:0 2px 12px rgba(0,0,0,0.20);}}
.adm-hero-sub{{font-size:0.86rem;color:rgba(255,255,255,0.70);
    position:relative;z-index:1;font-weight:500;}}

/* ── metric card ── */
.adm-metric{{
    background:{_CARD};border:1px solid {_BOR};border-radius:18px;
    padding:20px 16px 16px;text-align:center;position:relative;overflow:hidden;
    box-shadow:0 2px 8px rgba(15,23,42,0.07);
    transition:transform 0.20s,box-shadow 0.20s;
}}
.adm-metric::before{{content:'';position:absolute;top:0;left:0;right:0;
    height:4px;border-radius:18px 18px 0 0;}}
.adm-metric:hover{{transform:translateY(-3px);box-shadow:0 12px 32px rgba(99,102,241,0.14);}}
.adm-metric-num{{font-family:'Sora',sans-serif;font-size:2.2rem;font-weight:800;
    line-height:1.1;margin-bottom:5px;}}
.adm-metric-lbl{{font-size:0.70rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.08em;color:{_SUB};}}

/* ── section header ── */
.adm-sec{{font-size:0.72rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.10em;color:{_SUB};margin:24px 0 12px;
    display:flex;align-items:center;gap:10px;}}
.adm-sec::before{{content:'';width:4px;height:16px;
    background:linear-gradient(180deg,{_A1},{_A2});border-radius:3px;flex-shrink:0;}}
.adm-sec::after{{content:'';flex:1;height:1px;
    background:linear-gradient(to right,{_BOR},transparent);}}

/* ── satisfaction card ── */
.adm-sat{{
    background:linear-gradient(135deg,#1e3a5f 0%,{_A1} 50%,{_A2} 100%);
    border-radius:20px;padding:1.75rem 1.5rem;text-align:center;
    color:#fff;margin-bottom:1rem;position:relative;overflow:hidden;
}}
.adm-sat::before{{content:'';position:absolute;top:-50px;right:-50px;
    width:180px;height:180px;border-radius:50%;
    background:rgba(255,255,255,0.07);pointer-events:none;}}
.adm-sat-emoji{{font-size:2.5rem;display:block;margin-bottom:8px;
    position:relative;z-index:1;}}
.adm-sat-pct{{font-family:'Sora',sans-serif;font-size:3rem;font-weight:800;
    line-height:1;color:#fff;position:relative;z-index:1;}}
.adm-sat-lbl{{font-size:0.85rem;color:rgba(255,255,255,0.80);margin-top:6px;
    position:relative;z-index:1;}}

/* ── sentiment pill ── */
.adm-sent-card{{
    background:{_CARD};border:1px solid {_BOR};border-radius:16px;
    padding:16px;text-align:center;
    box-shadow:0 2px 8px rgba(15,23,42,0.05);
}}
.adm-sent-num{{font-family:'Sora',sans-serif;font-size:1.6rem;font-weight:800;margin-bottom:4px;}}
.adm-sent-lbl{{font-size:0.68rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.08em;color:{_SUB};}}

/* ── workload card ── */
.adm-wl-card{{
    background:{_CARD};border:1px solid {_BOR};border-radius:14px;
    padding:14px 16px;margin-bottom:8px;
    box-shadow:0 2px 8px rgba(15,23,42,0.05);
    transition:transform 0.18s;
}}
.adm-wl-card:hover{{transform:translateX(4px);}}
.adm-wl-head{{display:flex;justify-content:space-between;align-items:center;
    margin-bottom:10px;flex-wrap:wrap;gap:6px;}}
.adm-wl-name{{font-size:0.88rem;font-weight:700;color:{_TXT};}}
.adm-wl-stats{{display:flex;gap:10px;}}
.adm-wl-pill{{font-size:0.68rem;font-weight:700;padding:3px 10px;border-radius:20px;}}
.adm-wl-pill.assigned{{background:rgba(99,102,241,0.12);color:{_A1};}}
.adm-wl-pill.pending {{background:{"rgba(248,113,113,0.18)" if dark else "#FFF1F2"};
    color:{"#F87171" if dark else "#BE123C"};}}
.adm-wl-pill.resolved{{background:{"rgba(74,222,128,0.15)" if dark else "#F0FDF4"};
    color:{"#4ADE80" if dark else "#15803D"};}}
.adm-prog-track{{background:{_BOR};border-radius:10px;height:8px;overflow:hidden;}}
.adm-prog-fill{{height:100%;border-radius:10px;
    background:linear-gradient(90deg,{_A1},{_A2});
    transition:width 0.4s ease;}}

/* ── category bar ── */
.adm-cat-row{{margin:6px 0;}}
.adm-cat-lbl{{display:flex;justify-content:space-between;
    font-size:0.78rem;margin-bottom:4px;}}
.adm-cat-name{{font-weight:700;text-transform:capitalize;color:{_TXT};}}
.adm-cat-cnt{{color:{_SUB};font-size:0.73rem;}}
.adm-cat-track{{height:10px;background:{_BOR};border-radius:5px;overflow:hidden;}}
.adm-cat-fill{{height:100%;border-radius:5px;
    background:linear-gradient(90deg,#D97706,#059669);transition:width 0.4s;}}

/* ── area cards ── */
.adm-area-card{{
    background:{_CARD};border:1px solid {_BOR};border-radius:14px;
    padding:14px 16px;text-align:center;
    box-shadow:0 2px 8px rgba(15,23,42,0.05);
}}
.adm-area-lbl{{font-size:0.68rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.08em;color:{_SUB};margin-bottom:6px;}}
.adm-area-val{{font-size:0.92rem;font-weight:700;color:{_TXT};}}
.adm-area-cnt{{font-size:0.72rem;color:{_SUB};margin-top:3px;}}

/* ── feedback item ── */
.adm-fb-item{{
    background:{"#0A0E18" if dark else "#F8FAFF"};
    border:1px solid {_BOR};border-radius:12px;
    padding:12px 14px;margin-bottom:8px;
    display:flex;gap:12px;align-items:flex-start;
}}
.adm-fb-stars{{font-size:0.85rem;flex-shrink:0;}}
.adm-fb-text{{font-size:0.78rem;color:{_SUB};line-height:1.5;flex:1;}}
.adm-fb-id{{font-size:0.68rem;color:{_A1};font-weight:700;
    font-family:'Courier New',monospace;margin-bottom:3px;}}

/* ── warning banner ── */
.adm-warn{{
    background:{"#1C1408" if dark else "#FFFBEB"};
    border:1.5px solid {"#78350F" if dark else "#FDE68A"};
    border-radius:14px;padding:14px 18px;
    display:flex;gap:12px;align-items:center;margin-top:16px;
}}
.adm-warn-text{{font-size:0.82rem;font-weight:600;
    color:{"#FCD34D" if dark else "#B45309"};flex:1;}}

@media(max-width:600px){{
    .adm-hero{{padding:1.5rem 1rem;border-radius:18px;}}
    .adm-hero-title{{font-size:1.4rem;}}
    .adm-sat-pct{{font-size:2.2rem;}}
    .adm-metric-num{{font-size:1.8rem;}}
}}
</style>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # FETCH STATS
    # ════════════════════════════════════════════════════════
    s = api("get", "/admin/stats")
    if "error" in s:
        st.error(f"API Error: {s['error']}")
        return

    # ════════════════════════════════════════════════════════
    # HERO
    # ════════════════════════════════════════════════════════
    pend_approval = s.get("pending_approval", 0)
    st.markdown(
        f"<div class='adm-hero'>"
        f"<div class='adm-hero-title'>👑 Admin Dashboard</div>"
        f"<div class='adm-hero-sub'>System overview · analytics · citizen satisfaction"
        f"{'  &nbsp;·&nbsp; <span style=\"background:rgba(239,68,68,0.25);color:#FCA5A5;border-radius:20px;padding:2px 10px;font-size:0.72rem;font-weight:700;\">⚠️ ' + str(pend_approval) + ' pending approval</span>' if pend_approval else ''}"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════
    # METRIC CARDS  (2 rows × 3)
    # ════════════════════════════════════════════════════════
    METRICS = [
        ("👤", "Total Users",      s.get("total_users",0),       "#6366F1","#6366F1"),
        ("📋", "Complaints",       s.get("total_complaints",0),  "#F59E0B","#F59E0B"),
        ("✅", "Resolved",         s.get("resolved",0),          "#22C55E","#22C55E"),
        ("⏳", "Pending",          s.get("pending",0),           "#EF4444","#EF4444"),
        ("🏢", "Departments",      s.get("total_departments",0), "#3B82F6","#3B82F6"),
        ("👥", "Officials Active", s.get("approved_officials",0),"#10B981","#10B981"),
    ]
    st.markdown("<div class='adm-sec'>📊 Key Metrics</div>", unsafe_allow_html=True)
    row1 = st.columns(3)
    row2 = st.columns(3)
    for i, (icon, lbl, val, clr, grad) in enumerate(METRICS):
        col = row1[i] if i < 3 else row2[i-3]
        with col:
            st.markdown(
                f"<div class='adm-metric'>"
                f"<style>.adm-metric:nth-child({i+1})::before{{background:{clr};}}</style>"
                f"<div style='position:absolute;top:0;left:0;right:0;height:4px;"
                f"background:{clr};border-radius:18px 18px 0 0;'></div>"
                f"<div class='adm-metric-num' style='color:{clr};'>{val}</div>"
                f"<div class='adm-metric-lbl'>{icon} {lbl}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # resolution rate
    pct = s.get("resolution_rate", 0)
    st.markdown(
        f"<div class='adm-sec'>📈 Resolution Rate</div>"
        f"<div style='background:{_CARD};border:1px solid {_BOR};border-radius:14px;"
        f"padding:14px 18px;margin-bottom:4px;'>"
        f"<div style='display:flex;justify-content:space-between;"
        f"font-size:0.80rem;font-weight:700;color:{_TXT};margin-bottom:8px;'>"
        f"<span>Overall Resolution Rate</span>"
        f"<span style='color:{'#22C55E' if pct>=70 else '#F59E0B' if pct>=40 else '#EF4444'};'>{pct}%</span></div>"
        f"<div class='adm-prog-track'>"
        f"<div class='adm-prog-fill' style='width:{pct}%;background:"
        f"linear-gradient(90deg,{'#22C55E,#10B981' if pct>=70 else '#F59E0B,#D97706' if pct>=40 else '#EF4444,#DC2626'});'>"
        f"</div></div></div>",
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════
    # CITY HEALTH SNAPSHOT
    # ════════════════════════════════════════════════════════
    st.markdown("<div class='adm-sec'>🏙️ City Health Snapshot</div>", unsafe_allow_html=True)
    comps_all = api("get", "/complaints/all")
    if isinstance(comps_all, list) and comps_all:
        loc_counts = {}
        for c in comps_all:
            loc = c.get("location","Unknown").split(",")[0].strip()
            loc_counts[loc] = loc_counts.get(loc, 0) + 1
        if loc_counts:
            top_area    = max(loc_counts, key=loc_counts.get)
            bottom_area = min(loc_counts, key=loc_counts.get)
            a1, a2 = st.columns(2)
            with a1:
                st.markdown(
                    f"<div class='adm-area-card'>"
                    f"<div class='adm-area-lbl'>🔥 Most Complaints</div>"
                    f"<div class='adm-area-val'>{top_area}</div>"
                    f"<div class='adm-area-cnt'>{loc_counts[top_area]} complaints</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with a2:
                st.markdown(
                    f"<div class='adm-area-card'>"
                    f"<div class='adm-area-lbl'>🍃 Least Complaints</div>"
                    f"<div class='adm-area-val'>{bottom_area}</div>"
                    f"<div class='adm-area-cnt'>{loc_counts[bottom_area]} complaints</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏙️ View Full City Health Score →", key="adm_city", use_container_width=True):
            st.session_state.screen = "city_health_score"
            st.rerun()
    else:
        st.info("Not enough data to show city snapshot.")

    # ════════════════════════════════════════════════════════
    # OFFICIAL WORKLOAD (sorted, searchable, paginated)
    # ════════════════════════════════════════════════════════
    officials = api("get", "/admin/officials/all")
    if isinstance(officials, list) and officials:
        st.markdown("<div class='adm-sec'>👥 Official Workload</div>", unsafe_allow_html=True)

        # ── Sort by workload (total_assigned) descending ──
        officials_sorted = sorted(
            officials,
            key=lambda o: o.get("total_assigned", 0),
            reverse=True,
        )

        # ── Search bar (by email / gmail) ──
        st.markdown(
            f"<div style='margin-bottom:12px;'>"
            f"<div style='font-size:0.72rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.08em;color:{_SUB};margin-bottom:6px;'>🔍 Search Official by Email</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if "adm_wl_search" not in st.session_state:
            st.session_state.adm_wl_search = ""
        wl_search = st.text_input(
            label="Search officials by email",
            label_visibility="collapsed",
            placeholder="🔍 Search by email / gmail...",
            value=st.session_state.adm_wl_search,
            key="adm_wl_search_input",
        )
        if wl_search != st.session_state.adm_wl_search:
            st.session_state.adm_wl_search = wl_search
            st.session_state.adm_wl_page = 1
            st.rerun()

        # ── Apply search filter ──
        if st.session_state.adm_wl_search.strip():
            search_term = st.session_state.adm_wl_search.strip().lower()
            officials_filtered = [
                o for o in officials_sorted
                if search_term in (o.get("email", "") or "").lower()
                or search_term in (o.get("name", "") or "").lower()
            ]
        else:
            officials_filtered = officials_sorted

        # ── Pagination (10 per page) ──
        PAGE_SIZE = 10
        total_officials = len(officials_filtered)
        total_pages = max(1, (total_officials + PAGE_SIZE - 1) // PAGE_SIZE)

        if "adm_wl_page" not in st.session_state:
            st.session_state.adm_wl_page = 1
        current_page = max(1, min(st.session_state.adm_wl_page, total_pages))

        start_idx = (current_page - 1) * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total_officials)
        page_officials = officials_filtered[start_idx:end_idx]

        # ── Results count ──
        st.markdown(
            f"<div style='display:flex;align-items:center;justify-content:space-between;"
            f"flex-wrap:wrap;gap:8px;margin:8px 0 12px;'>"
            f"<span style='background:rgba(99,102,241,0.10);color:{_A1};border:1.5px solid rgba(99,102,241,0.22);"
            f"border-radius:20px;padding:5px 16px;font-size:0.76rem;font-weight:800;'>"
            f"Showing <strong>{start_idx+1}–{end_idx}</strong> of <strong>{total_officials}</strong> officials</span>"
            f"<span style='font-size:0.72rem;color:{_SUB};font-weight:600;'>"
            f"📊 Sorted by workload (highest first)</span></div>",
            unsafe_allow_html=True,
        )

        if not page_officials:
            st.markdown(
                f"<div style='text-align:center;padding:2rem;background:{_CARD};"
                f"border:1.5px dashed {_BOR};border-radius:18px;margin:1rem 0;'>"
                f"<span style='font-size:2.5rem;display:block;margin-bottom:10px;'>🔍</span>"
                f"<div style='font-size:0.92rem;font-weight:700;color:{_TXT};margin-bottom:6px;'>"
                f"No officials found</div>"
                f"<div style='font-size:0.78rem;color:{_SUB};'>Try a different search term.</div></div>",
                unsafe_allow_html=True,
            )
        else:
            for off in page_officials:
                assigned = off.get("total_assigned", 0)
                resolved = off.get("total_resolved", 0)
                pending  = max(0, assigned - resolved)
                util_pct = max(0, min(100, int((pending / max(assigned, 1)) * 100)))
                bar_color = (
                    "#EF4444,#DC2626" if util_pct >= 75
                    else "#F59E0B,#D97706" if util_pct >= 40
                    else "#22C55E,#10B981"
                )
                email_display = off.get("email", "—")
                st.markdown(
                    f"<div class='adm-wl-card'>"
                    f"<div class='adm-wl-head'>"
                    f"<div class='adm-wl-name'>👤 {off.get('name','—')}"
                    f"<span style='font-size:0.68rem;color:{_SUB};margin-left:8px;"
                    f"font-weight:500;'>✉️ {email_display}</span></div>"
                    f"<div class='adm-wl-stats'>"
                    f"<span class='adm-wl-pill assigned'>📋 {assigned} assigned</span>"
                    f"<span class='adm-wl-pill pending'>⏳ {pending} pending</span>"
                    f"<span class='adm-wl-pill resolved'>✅ {resolved} resolved</span>"
                    f"</div></div>"
                    f"<div class='adm-prog-track'>"
                    f"<div class='adm-prog-fill' style='width:{util_pct}%;"
                    f"background:linear-gradient(90deg,{bar_color});'></div>"
                    f"</div>"
                    f"<div style='font-size:0.65rem;color:{_SUB};margin-top:4px;text-align:right;'>"
                    f"Utilisation {util_pct}%</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # ── Pagination controls ──
        if total_pages > 1:
            st.markdown(
                f"<div style='display:flex;align-items:center;justify-content:center;"
                f"gap:6px;margin:16px 0 8px;font-size:0.78rem;color:{_SUB};font-weight:600;'>"
                f"Page {current_page} of {total_pages}</div>",
                unsafe_allow_html=True,
            )
            pg_col1, pg_col2, pg_col3 = st.columns([1, 1, 1])
            with pg_col1:
                if current_page > 1:
                    if st.button("⬅️ Previous 10", key="adm_wl_prev", use_container_width=True):
                        st.session_state.adm_wl_page = current_page - 1
                        st.rerun()
            with pg_col2:
                st.markdown(
                    f"<div style='text-align:center;font-size:0.75rem;color:{_A1};"
                    f"font-weight:800;padding:8px 0;'>{current_page} / {total_pages}</div>",
                    unsafe_allow_html=True,
                )
            with pg_col3:
                if current_page < total_pages:
                    if st.button("Next 10 ➡️", key="adm_wl_next", use_container_width=True):
                        st.session_state.adm_wl_page = current_page + 1
                        st.rerun()

    # ════════════════════════════════════════════════════════
    # PUBLIC SATISFACTION SCORE
    # ════════════════════════════════════════════════════════
    st.markdown("<div class='adm-sec'>😊 Public Satisfaction Score</div>", unsafe_allow_html=True)

    all_complaints = api("get", "/complaints/all")
    all_complaints = all_complaints if isinstance(all_complaints, list) else []

    rated_complaints = []
    for c in all_complaints:
        rating = c.get("rating")
        if rating and isinstance(rating, dict) and rating.get("stars"):
            rated_complaints.append({
                "stars":        rating.get("stars"),
                "comment":      rating.get("comment",""),
                "complaint_id": c.get("complaint_id",""),
            })

    total_rated = len(rated_complaints)
    if total_rated == 0:
        st.markdown(
            f"<div class='trk-empty' style='border-radius:18px;'>"
            f"<span style='font-size:2.5rem;display:block;margin-bottom:10px;'>📊</span>"
            f"<div style='font-size:0.92rem;font-weight:700;color:{_TXT};margin-bottom:6px;'>"
            f"No ratings yet</div>"
            f"<div style='font-size:0.78rem;color:{_SUB};'>"
            f"Once complaints are resolved and rated, satisfaction metrics will appear here.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        counts = {"positive": 0, "neutral": 0, "negative": 0}
        for rc in rated_complaints:
            sent = analyze_sentiment(rc["stars"], rc["comment"])
            counts[sent] += 1

        pos_pct = (counts["positive"] / total_rated) * 100
        neu_pct = (counts["neutral"]  / total_rated) * 100
        neg_pct = (counts["negative"] / total_rated) * 100

        # big satisfaction card
        sat_emoji = "😊" if pos_pct >= 70 else "😐" if pos_pct >= 40 else "😞"
        sat_grad  = (
            "linear-gradient(135deg,#14532D,#15803D)"  if pos_pct >= 70
            else "linear-gradient(135deg,#78350F,#B45309)" if pos_pct >= 40
            else "linear-gradient(135deg,#7F1D1D,#BE123C)"
        )
        st.markdown(
            f"<div class='adm-sat' style='background:{sat_grad};'>"
            f"<span class='adm-sat-emoji'>{sat_emoji}</span>"
            f"<div class='adm-sat-pct'>{pos_pct:.1f}%</div>"
            f"<div class='adm-sat-lbl'>Citizens satisfied · based on {total_rated} reviews</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # sentiment breakdown
        sc1, sc2, sc3 = st.columns(3)
        for col, key, emoji, clr in [
            (sc1,"positive","😊","#22C55E"),
            (sc2,"neutral", "😐","#F59E0B"),
            (sc3,"negative","😠","#EF4444"),
        ]:
            pct_val = (counts[key] / total_rated) * 100
            with col:
                st.markdown(
                    f"<div class='adm-sent-card'>"
                    f"<div class='adm-sent-num' style='color:{clr};'>{emoji} {counts[key]}</div>"
                    f"<div class='adm-sent-lbl'>{key.title()} · {pct_val:.1f}%</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # sentiment distribution bar
        st.markdown(
            f"<div style='background:{_CARD};border:1px solid {_BOR};border-radius:14px;"
            f"padding:14px 18px;margin-top:12px;'>"
            f"<div style='font-size:0.72rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.08em;color:{_SUB};margin-bottom:10px;'>Sentiment Distribution</div>"
            f"<div style='display:flex;height:14px;border-radius:10px;overflow:hidden;gap:2px;'>"
            f"<div style='width:{pos_pct:.1f}%;background:#22C55E;border-radius:10px 0 0 10px;' title='Positive {pos_pct:.1f}%'></div>"
            f"<div style='width:{neu_pct:.1f}%;background:#F59E0B;' title='Neutral {neu_pct:.1f}%'></div>"
            f"<div style='width:{neg_pct:.1f}%;background:#EF4444;border-radius:0 10px 10px 0;' title='Negative {neg_pct:.1f}%'></div>"
            f"</div>"
            f"<div style='display:flex;gap:16px;margin-top:8px;'>"
            f"<span style='font-size:0.68rem;color:#22C55E;font-weight:600;'>● Positive {pos_pct:.1f}%</span>"
            f"<span style='font-size:0.68rem;color:#F59E0B;font-weight:600;'>● Neutral {neu_pct:.1f}%</span>"
            f"<span style='font-size:0.68rem;color:#EF4444;font-weight:600;'>● Negative {neg_pct:.1f}%</span>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        # recent feedback samples
        with st.expander("📝 Recent Feedback Samples", expanded=False):
            recent = sorted(rated_complaints,
                            key=lambda x: x.get("complaint_id",""), reverse=True)[:10]
            for rc in recent:
                stars   = rc["stars"]
                comment = rc["comment"][:120] if rc["comment"] else "(no comment)"
                sent    = analyze_sentiment(stars, comment)
                emoji_s = "😊" if sent=="positive" else "😐" if sent=="neutral" else "😠"
                star_str= "⭐" * stars
                st.markdown(
                    f"<div class='adm-fb-item'>"
                    f"<div class='adm-fb-stars'>{emoji_s} {star_str}</div>"
                    f"<div><div class='adm-fb-id'>#{rc['complaint_id']}</div>"
                    f"<div class='adm-fb-text'>{comment}</div></div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # ════════════════════════════════════════════════════════
    # COMPLAINTS BY CATEGORY
    # ════════════════════════════════════════════════════════
    comps = api("get", "/complaints/all")
    comps = comps if isinstance(comps, list) else []
    if comps:
        cats = {}
        for c in comps:
            k = c.get("category","other")
            cats[k] = cats.get(k, 0) + 1
        mx = max(cats.values()) if cats else 1

        st.markdown("<div class='adm-sec'>📂 Complaints by Category</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='background:{_CARD};border:1px solid {_BOR};"
            f"border-radius:16px;padding:16px 20px;'>",
            unsafe_allow_html=True,
        )
        for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
            fill = int(cnt / mx * 100)
            st.markdown(
                f"<div class='adm-cat-row'>"
                f"<div class='adm-cat-lbl'>"
                f"<span class='adm-cat-name'>{cat}</span>"
                f"<span class='adm-cat-cnt'>{cnt}</span></div>"
                f"<div class='adm-cat-track'>"
                f"<div class='adm-cat-fill' style='width:{fill}%;'></div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # PENDING APPROVAL WARNING
    # ════════════════════════════════════════════════════════
    if pend_approval > 0:
        st.markdown(
            f"<div class='adm-warn'>"
            f"<span style='font-size:1.3rem;'>⚠️</span>"
            f"<div class='adm-warn-text'>"
            f"{pend_approval} official(s) awaiting approval — go to the Officials section.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        wa1, wa2, wa3 = st.columns([1, 2, 1])
        with wa2:
            if st.button("👥 Review Pending Officials →", key="adm_pend_off", use_container_width=True):
                st.session_state.screen = "manage_officials"
                st.rerun()

def pg_admin_departments():
    _apply_layout("admin")  
    if st.session_state.viewing_dept_id:
        _dept_drill()
        return

    dark  = st.session_state.get("dark_mode", False)
    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)

    _CARD = "#10161F" if dark else "#FFFFFF"
    _BG2  = "#080C14" if dark else "#F4F6FB"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
    _A1   = "#6366F1"
    _A2   = "#8B5CF6"

    # ── FIX: input_bg and a1_soft derived for use in CSS ──
    _INPUT = "#0F1828" if dark else "#F0F4FB"
    _A1_SOFT = "rgba(99,102,241,0.12)" if dark else "rgba(79,70,229,0.08)"
    _HOVER = "#16213A" if dark else "#E8EDF7"
    _POP_SHADOW = "0 4px 20px rgba(0,0,0,0.55),0 12px 40px rgba(0,0,0,0.35)" if dark else "0 4px 16px rgba(11,20,40,0.08),0 12px 32px rgba(11,20,40,0.06)"

    st.markdown(f"""
<style>
/* ── hero ── */
.dept-hero{{
    background:linear-gradient(135deg,#1e1b4b 0%,#312e81 50%,#1e3a5f 100%);
    border-radius:22px;padding:1.75rem 2rem;margin-bottom:1.75rem;
    position:relative;overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,0.25);
}}
.dept-hero::before{{content:'';position:absolute;top:-60px;right:-60px;
    width:220px;height:220px;border-radius:50%;
    background:radial-gradient(circle,rgba(255,255,255,0.08) 0%,transparent 70%);
    pointer-events:none;}}
.dept-hero-title{{font-family:'Sora',sans-serif;font-size:1.75rem;font-weight:800;
    color:#fff;margin-bottom:5px;position:relative;z-index:1;
    text-shadow:0 2px 12px rgba(0,0,0,0.20);}}
.dept-hero-sub{{font-size:0.86rem;color:rgba(255,255,255,0.65);
    position:relative;z-index:1;font-weight:500;}}
.dept-hero-badge{{
    position:absolute;top:20px;right:20px;z-index:1;
    background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);
    border-radius:12px;padding:10px 16px;text-align:center;
    backdrop-filter:blur(8px);
}}
.dept-hero-badge-num{{font-family:'Sora',sans-serif;font-size:1.6rem;
    font-weight:800;color:#fff;line-height:1;}}
.dept-hero-badge-lbl{{font-size:0.60rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.08em;color:rgba(255,255,255,0.60);margin-top:2px;}}

/* ── section header ── */
.dept-sec{{font-size:0.70rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.10em;color:{_SUB};margin:22px 0 12px;
    display:flex;align-items:center;gap:10px;}}
.dept-sec::before{{content:'';width:4px;height:16px;
    background:linear-gradient(180deg,{_A1},{_A2});border-radius:3px;flex-shrink:0;}}
.dept-sec::after{{content:'';flex:1;height:1px;
    background:linear-gradient(to right,{_BOR},transparent);}}

/* ── create form card ── */
.dept-form-wrap{{
    background:{_CARD};border:1px solid {_BOR};border-radius:18px;
    padding:20px 22px 8px 22px;margin-bottom:18px;
    box-shadow:0 2px 8px rgba(15,23,42,0.06);
}}
.dept-form-title{{font-size:0.90rem;font-weight:700;color:{_TXT};
    margin-bottom:14px;display:flex;align-items:center;gap:8px;}}

/* ═══════���════════════════════════════════════════
   FIX 1 — SELECTBOX TRIGGER (closed state)
   Streamlit v1.30+ uses two div levels inside
   .stSelectbox before reaching the styled div.
   We target every nesting level with !important
   to beat Streamlit's inline style="" overrides.
════════════════════════════════════════════════ */
.stSelectbox > div > div,
.stSelectbox [data-baseweb="select"] > div {{
    background:{_INPUT}!important;
    border:1.5px solid {_BOR}!important;
    border-radius:14px!important;
    min-height:44px!important;
    padding:0 12px!important;
    display:flex!important;
    align-items:center!important;
    transition:border-color 0.15s ease,box-shadow 0.15s ease!important;
    cursor:pointer!important;
}}
.stSelectbox > div > div:hover,
.stSelectbox [data-baseweb="select"] > div:hover {{
    border-color:{_A1}!important;
    box-shadow:0 0 0 3px {_A1_SOFT}!important;
}}
/* Selected value text */
.stSelectbox > div > div > div,
.stSelectbox > div > div > div > div,
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] p {{
    color:{_TXT}!important;
    font-size:0.875rem!important;
    font-family:'DM Sans','Noto Sans Devanagari',sans-serif!important;
    font-weight:400!important;
    background:transparent!important;
}}
/* Chevron arrow */
.stSelectbox svg {{
    fill:{_SUB}!important;
    flex-shrink:0!important;
}}

/* ════════════════════════════════════════════════
   FIX 2 — DROPDOWN POPOVER (open list)
════════════════════════════════════════════════ */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[data-testid="stWidgetDropdownList"] {{
    background:{_CARD}!important;
    border:1.5px solid {_BOR}!important;
    border-radius:16px!important;
    box-shadow:{_POP_SHADOW}!important;
    overflow:hidden!important;
    z-index:99999!important;
    padding:4px!important;
}}
div[data-baseweb="option"],
li[role="option"] {{
    background:transparent!important;
    color:{_TXT}!important;
    font-size:0.875rem!important;
    font-family:'DM Sans',sans-serif!important;
    padding:9px 14px!important;
    border-radius:10px!important;
    margin:1px 4px!important;
    cursor:pointer!important;
    transition:background 0.15s ease!important;
}}
div[data-baseweb="option"]:hover,
li[role="option"]:hover {{
    background:{_HOVER}!important;
    color:{_TXT}!important;
}}
div[data-baseweb="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] {{
    background:{_A1_SOFT}!important;
    color:{_A1}!important;
    font-weight:700!important;
}}

/* ════════════════════════════════════════════════
   FIX 3 — TEXT INPUT inside the form
════════════════════════════════════════════════ */
.stTextInput > div > div > input {{
    background:{_INPUT}!important;
    border:1.5px solid {_BOR}!important;
    border-radius:14px!important;
    color:{_TXT}!important;
    font-family:'DM Sans',sans-serif!important;
    font-size:0.875rem!important;
    padding:10px 14px!important;
    transition:border-color 0.15s ease,box-shadow 0.15s ease!important;
}}
.stTextInput > div > div > input:focus {{
    border-color:{_A1}!important;
    box-shadow:0 0 0 3px {_A1_SOFT}!important;
    outline:none!important;
    background:{_CARD}!important;
}}
.stTextInput > div > div > input::placeholder {{
    color:{_SUB}!important;
    opacity:0.65!important;
}}

/* ════════════════════════════════════════════════
   FIX 4 — FORM submit button styling
════════════════════════════════════════════════ */
.stForm [data-testid="stFormSubmitButton"] > button,
[data-testid="stFormSubmitButton"] > button {{
    background:linear-gradient(135deg,{_A1},{_A2})!important;
    color:#fff!important;
    border:none!important;
    border-radius:14px!important;
    padding:11px 20px!important;
    font-weight:700!important;
    font-size:0.875rem!important;
    width:100%!important;
    cursor:pointer!important;
    transition:transform 0.18s ease,box-shadow 0.18s ease!important;
    box-shadow:0 2px 8px rgba(99,102,241,0.30)!important;
    margin-top:8px!important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    transform:translateY(-2px)!important;
    box-shadow:0 6px 20px rgba(99,102,241,0.40)!important;
    filter:brightness(1.05)!important;
}}

/* ── dept card ── */
.dept-card{{
    background:{_CARD};border:1px solid {_BOR};
    border-radius:18px;padding:18px 20px;
    margin-bottom:12px;position:relative;overflow:hidden;
    box-shadow:0 2px 10px rgba(15,23,42,0.06);
    transition:transform 0.20s,box-shadow 0.20s;
}}
.dept-card:hover{{
    transform:translateY(-2px);
    box-shadow:0 10px 32px rgba(99,102,241,0.12);
}}
.dept-card-accent{{
    position:absolute;top:0;left:0;bottom:0;
    width:4px;border-radius:18px 0 0 18px;
}}
.dept-card-body{{padding-left:14px;}}
.dept-card-top{{
    display:flex;justify-content:space-between;
    align-items:flex-start;flex-wrap:wrap;gap:10px;
    margin-bottom:14px;
}}
.dept-card-name{{font-size:1rem;font-weight:800;color:{_TXT};margin-bottom:3px;}}
.dept-card-name-hi{{font-size:0.78rem;color:{_SUB};margin-bottom:5px;}}
.dept-card-meta{{
    display:flex;gap:8px;flex-wrap:wrap;align-items:center;
    font-size:0.70rem;color:{_SUB};
}}
.dept-meta-pill{{
    background:{"#1A2236" if dark else "#F1F5F9"};
    border:1px solid {_BOR};border-radius:20px;
    padding:2px 9px;font-size:0.68rem;font-weight:600;color:{_SUB};
}}
/* ═══════════════════════════════════════════════
   COMPLAINT ACTION BUTTON FIX
═══════════════════════════════════════════════ */

.dept-action-row{{

    display:flex!important;

    flex-wrap:wrap!important;

    gap:12px!important;

    align-items:center!important;

    margin-top:14px!important;
}}

/* Prevent hidden/stretched buttons */
.dept-action-row .stButton{{

    width:auto!important;

    display:inline-flex!important;

    flex:none!important;

    visibility:visible!important;

    opacity:1!important;
}}

/* Prevent Streamlit columns stretching */
.dept-action-row .stColumn{{

    width:auto!important;

    flex:none!important;
}}

/* Main button style */
.dept-action-row .stButton>button{{

    width:auto!important;

    min-width:130px!important;

    max-width:100%!important;

    height:44px!important;

    padding:0 18px!important;

    border-radius:14px!important;

    display:inline-flex!important;

    align-items:center!important;

    justify-content:center!important;

    white-space:nowrap!important;

    font-weight:700!important;

    font-size:.92rem!important;

    border:none!important;

    transition:all .18s ease!important;
}}

/* Resolve button */
.resolve-btn .stButton>button{{

    background:
        linear-gradient(135deg,#10B981,#059669)!important;

    color:#FFFFFF!important;

    box-shadow:
        0 8px 22px rgba(16,185,129,.22)!important;
}}

/* Reject button */
.reject-btn .stButton>button{{

    background:
        linear-gradient(135deg,#EF4444,#DC2626)!important;

    color:#FFFFFF!important;

    box-shadow:
        0 8px 22px rgba(239,68,68,.22)!important;
}}

/* Progress button */
.progress-btn .stButton>button{{

    background:
        linear-gradient(135deg,#6366F1,#8B5CF6)!important;

    color:#FFFFFF!important;

    box-shadow:
        0 8px 22px rgba(99,102,241,.24)!important;
}}

/* Hover */
.dept-action-row .stButton>button:hover{{

    transform:
        translateY(-2px)!important;

    filter:
        brightness(1.04)!important;
}}

/* Disabled */
.stButton>button:disabled{{

    opacity:.55!important;

    cursor:not-allowed!important;

    filter:grayscale(.08)!important;
}}

/* Mobile */
@media(max-width:768px){{

    .dept-action-row{{

        flex-direction:column!important;

        align-items:stretch!important;
    }}

    .dept-action-row .stButton{{

        width:100%!important;
    }}

    .dept-action-row .stButton>button{{

        width:100%!important;
    }}
}}
.dept-card-code{{
    font-family:'Courier New',monospace;font-size:1.1rem;
    font-weight:800;line-height:1;margin-bottom:3px;
}}

.dept-card-code-lbl{{
    font-size:0.60rem;font-weight:600;text-transform:uppercase;
    letter-spacing:0.08em;color:{_SUB};opacity:0.7;
}}
/* ── stat mini-grid ── */
.dept-stats{{
    display:grid;grid-template-columns:repeat(4,1fr);
    gap:8px;margin-top:4px;
}}
.dept-stat{{
    border-radius:12px;padding:10px 6px;text-align:center;
    border:1px solid;
}}
.dept-stat-num{{font-size:1.1rem;font-weight:800;line-height:1;margin-bottom:3px;}}
.dept-stat-lbl{{font-size:0.58rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.05em;opacity:0.70;}}

.dept-stat.total   {{background:{"#1C1408" if dark else "#FFFBEB"};border-color:{"#78350F" if dark else "#FDE68A"};}}
.dept-stat.total   .dept-stat-num{{color:{"#FCD34D" if dark else "#B45309"};}}
.dept-stat.total   .dept-stat-lbl{{color:{"#FCD34D" if dark else "#B45309"};}}

.dept-stat.pending {{background:{"#1C0808" if dark else "#FFF1F2"};border-color:{"#7F1D1D" if dark else "#FECDD3"};}}
.dept-stat.pending .dept-stat-num{{color:{"#F87171" if dark else "#BE123C"};}}
.dept-stat.pending .dept-stat-lbl{{color:{"#F87171" if dark else "#BE123C"};}}

.dept-stat.resolved{{background:{"#0A2218" if dark else "#F0FDF4"};border-color:{"#14532D" if dark else "#BBF7D0"};}}
.dept-stat.resolved .dept-stat-num{{color:{"#4ADE80" if dark else "#15803D"};}}
.dept-stat.resolved .dept-stat-lbl{{color:{"#4ADE80" if dark else "#15803D"};}}

.dept-stat.officials{{background:{"#080F1C" if dark else "#EFF6FF"};border-color:{"#1E3A5F" if dark else "#BFDBFE"};}}
.dept-stat.officials .dept-stat-num{{color:{"#60A5FA" if dark else "#1D4ED8"};}}
.dept-stat.officials .dept-stat-lbl{{color:{"#60A5FA" if dark else "#1D4ED8"};}}

@media(max-width:600px){{
    .dept-hero{{padding:1.4rem 1rem;border-radius:18px;}}
    .dept-hero-title{{font-size:1.4rem;}}
    .dept-hero-badge{{display:none;}}
    .dept-stats{{grid-template-columns:repeat(2,1fr);gap:6px;}}
    .dept-card-top{{flex-direction:column;}}
}}
</style>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # FETCH
    # ════════════════════════════════════════════════════════
    depts = api("get", "/admin/departments")
    depts = depts if isinstance(depts, list) else []

    # ════════════════════════════════════════════════════════
    # HERO
    # ════════════════════════════════════════════════════════
    st.markdown(
        f"<div class='dept-hero'>"
        f"<div class='dept-hero-badge'>"
        f"<div class='dept-hero-badge-num'>{len(depts)}</div>"
        f"<div class='dept-hero-badge-lbl'>Departments</div>"
        f"</div>"
        f"<div class='dept-hero-title'>🏢 Departments</div>"
        f"<div class='dept-hero-sub'>Create · manage officials · view complaints by department</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════
    # CREATE FORM
    # FIX: Removed the orphaned st.markdown("<div class='dept-form-wrap'>")
    # and st.markdown("</div>") wrappers — Streamlit does not support wrapping
    # native widgets (st.form, st.columns, st.text_input etc.) inside raw HTML
    # divs opened/closed with separate st.markdown() calls. The open <div> and
    # close </div> end up in different parts of the DOM and break the layout.
    # Instead we use a st.container() with a border, which Streamlit renders
    # correctly around the form.
    # ════════════════════════════════════════════════════════
    st.markdown("<div class='dept-sec'>➕ Create New Department</div>", unsafe_allow_html=True)

    # ── styled container replaces the broken dept-form-wrap div ──
    with st.container(border=True):
        st.markdown(
            f"<div class='dept-form-title'>➕ New Department Details</div>",
            unsafe_allow_html=True,
        )

        # FIX: form is correctly inside the container — submit button present
        with st.form("dept_create_form", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                nm  = st.text_input("Name (English) *", placeholder="e.g. Water Supply Department")
                ct  = st.text_input("Category", placeholder="e.g., sanitation, transport, etc.")
            with fc2:
                nmh = st.text_input("नाम (हिंदी)", placeholder="जैसे जल आपूर्ति विभाग")
                lc  = st.text_input("City / Location", placeholder="e.g. Downtown, Sector 45")

            submitted = st.form_submit_button(
                "➕  Create Department",
                use_container_width=True,
            )

        # FIX: handle submission OUTSIDE the with st.form() block but still
        # inside the container — this is the correct Streamlit pattern
        if submitted:
            if nm.strip():
                resp = api("post", "/admin/departments", json={
                    "name":     nm.strip(),
                    "name_hi":  nmh.strip(),
                    "category": ct.strip(),
                    "location": lc.strip(),
                })
                if resp.get("success"):
                    st.success(f"✅ Department created!  Code: **{resp.get('dept_id')}**")
                    st.rerun()
                else:
                    st.error(resp.get("detail", "Failed to create department."))
            else:
                st.warning("Department name (English) is required.")

    # ════════════════════════════════════════════════════════
    # DEPARTMENT CARDS
    # ════════════════════════════════════════════════════════
    if not depts:
        st.markdown(
            f"<div style='text-align:center;padding:3rem 2rem;"
            f"background:{_CARD};border-radius:22px;"
            f"border:1.5px dashed {_BOR};margin-top:10px;'>"
            f"<div style='font-size:3rem;opacity:0.5;margin-bottom:12px;'>🏢</div>"
            f"<div style='font-size:0.95rem;font-weight:700;color:{_TXT};margin-bottom:6px;'>"
            f"No departments yet</div>"
            f"<div style='font-size:0.78rem;color:{_SUB};'>"
            f"Create your first department using the form above.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown("<div class='dept-sec'>🏢 All Departments</div>", unsafe_allow_html=True)

    CAT_META = {

        "water": (
            "#0369A1",
            "#DBEAFE",
            "💧"
        ),

        "electricity": (
            "#D97706",
            "#FEF3C7",
            "⚡"
        ),

        "road": (
            "#7C3AED",
            "#F3F0FF",
            "🛣"
        ),

        "waste": (
            "#059669",
            "#ECFDF5",
            "♻️"
        ),

        "drainage": (
            "#0284C7",
            "#E0F2FE",
            "🌊"
        ),

        "health": (
            "#DC2626",
            "#FFF1F2",
            "🏥"
        ),

        "other": (
            "#6B7280",
            "#F3F4F6",
            "📋"
        ),
    }

    # ─────────────────────────────────────────────
    # DYNAMIC CATEGORY STYLE HELPER
    # ─────────────────────────────────────────────

    def get_category_meta(category):

        category = str(category).lower().strip()

        return CAT_META.get(

            category,

            (
                "#2563EB",     # default border/accent
                "#EFF6FF",     # default background
                "📌"           # default icon
            )
        )

    for d in depts:
        did      = d.get("id")
        cat      = d.get("category", "other")
        cat_col, cat_bg, cat_icon = CAT_META.get(cat, ("#6B7280", "#F3F4F6", "📋"))
        badge_bg = (
            f"rgba({int(cat_col[1:3],16)},{int(cat_col[3:5],16)},{int(cat_col[5:7],16)},0.18)"
            if dark else cat_bg
        )

        total_c  = d.get("total_complaints", 0)
        pend_c   = d.get("pending_complaints", 0)
        res_c    = d.get("resolved_complaints", 0)
        appr_off = d.get("approved_officials", 0)
        tot_off  = d.get("total_officials", 0)
        res_rate = int(res_c / max(total_c, 1) * 100)

        st.markdown(
            f"<div class='dept-card'>"
            f"<div class='dept-card-accent' style='background:{cat_col};'></div>"
            f"<div class='dept-card-body'>"

            f"<div class='dept-card-top'>"

            f"<div style='flex:1;min-width:0;'>"
            f"<div class='dept-card-name'>{cat_icon} {d.get('name','')}</div>"
            f"{'<div class=\"dept-card-name-hi\">' + d.get('name_hi','') + '</div>' if d.get('name_hi') else ''}"
            f"<div class='dept-card-meta'>"
            f"<span class='dept-meta-pill'>📂 {cat.title()}</span>"
            f"<span class='dept-meta-pill'>📍 {d.get('location','—')}</span>"
            f"<span class='dept-meta-pill'>📈 {res_rate}% resolved</span>"
            f"</div>"
            f"</div>"

            f"<div style='text-align:right;flex-shrink:0;'>"
            f"<div class='dept-card-code' style='color:{cat_col};'>{d.get('dept_id','')}</div>"
            f"<div class='dept-card-code-lbl'>Share with officials</div>"
            f"</div>"

            f"</div>"

            f"<div class='dept-stats'>"
            f"<div class='dept-stat total'>"
            f"<div class='dept-stat-num'>{total_c}</div>"
            f"<div class='dept-stat-lbl'>Total</div>"
            f"</div>"
            f"<div class='dept-stat pending'>"
            f"<div class='dept-stat-num'>{pend_c}</div>"
            f"<div class='dept-stat-lbl'>Pending</div>"
            f"</div>"
            f"<div class='dept-stat resolved'>"
            f"<div class='dept-stat-num'>{res_c}</div>"
            f"<div class='dept-stat-lbl'>Resolved</div>"
            f"</div>"
            f"<div class='dept-stat officials'>"
            f"<div class='dept-stat-num'>{appr_off}"
            f"<span style='font-size:0.65rem;font-weight:600;opacity:0.6;'>/{tot_off}</span>"
            f"</div>"
            f"<div class='dept-stat-lbl'>Officials</div>"
            f"</div>"
            f"</div>"

            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        bc1, bc2, bc3 = st.columns([1, 2, 1])
        with bc2:
            if st.button(
                f"🔍 Open {d.get('name','')} →",
                key=f"od_{did}",
                use_container_width=True,
            ):
                st.session_state.viewing_dept_id   = did
                st.session_state.viewing_dept_name = d.get("name", "")
                st.session_state.viewing_dept_code = d.get("dept_id", "")
                st.rerun()

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

def pg_city_health_score():
    _apply_layout("admin")  
    dark  = st.session_state.get("dark_mode", False)
    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)

    _CARD = "#10161F" if dark else "#FFFFFF"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
    _A1   = "#6366F1"
    _A2   = "#8B5CF6"

    st.markdown(f"""
<style>
.chs-hero{{background:linear-gradient(135deg,#064E3B 0%,#065F46 45%,#0C4A6E 100%);border-radius:22px;padding:1.75rem 2rem;margin-bottom:1.75rem;position:relative;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.25);}}
.chs-hero::before{{content:'';position:absolute;top:-60px;right:-60px;width:220px;height:220px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,0.07) 0%,transparent 70%);pointer-events:none;}}
.chs-hero-title{{font-family:'Sora',sans-serif;font-size:1.75rem;font-weight:800;color:#fff;margin-bottom:5px;position:relative;z-index:1;}}
.chs-hero-sub{{font-size:0.86rem;color:rgba(255,255,255,0.65);position:relative;z-index:1;font-weight:500;}}
.chs-sec{{font-size:0.70rem;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;color:{_SUB};margin:22px 0 12px;display:flex;align-items:center;gap:10px;}}
.chs-sec::before{{content:'';width:4px;height:16px;background:linear-gradient(180deg,#10B981,#059669);border-radius:3px;flex-shrink:0;}}
.chs-sec::after{{content:'';flex:1;height:1px;background:linear-gradient(to right,{_BOR},transparent);}}
.chs-summary-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:6px;}}
.chs-sum-card{{background:{_CARD};border:1px solid {_BOR};border-radius:16px;padding:16px 14px;text-align:center;position:relative;overflow:hidden;box-shadow:0 2px 8px rgba(15,23,42,0.06);}}
.chs-sum-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:4px;border-radius:16px 16px 0 0;}}
.chs-sum-card.green::before{{background:linear-gradient(90deg,#10B981,#059669);}}
.chs-sum-card.red::before{{background:linear-gradient(90deg,#EF4444,#DC2626);}}
.chs-sum-card.blue::before{{background:linear-gradient(90deg,{_A1},{_A2});}}
.chs-sum-num{{font-family:'Sora',sans-serif;font-size:1.4rem;font-weight:800;line-height:1.2;color:{_TXT};margin-bottom:4px;}}
.chs-sum-lbl{{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;color:{_SUB};}}
.chs-rank-card{{background:{_CARD};border:1px solid {_BOR};border-radius:16px;padding:16px 18px;margin-bottom:10px;position:relative;overflow:hidden;box-shadow:0 2px 8px rgba(15,23,42,0.06);transition:transform 0.18s,box-shadow 0.18s;}}
.chs-rank-card:hover{{transform:translateY(-2px);box-shadow:0 10px 28px rgba(16,185,129,0.12);}}
.chs-rank-card.gold{{border-left:5px solid #FFD700;background:{"rgba(255,215,0,0.06)" if dark else "#FFFBEB"};}}
.chs-rank-card.silver{{border-left:5px solid #C0C0C0;background:{"rgba(192,192,192,0.06)" if dark else "#F8FAFC"};}}
.chs-rank-card.bronze{{border-left:5px solid #CD7F32;background:{"rgba(205,127,50,0.06)" if dark else "#FFF7ED"};}}
.chs-rank-card.normal{{border-left:4px solid {_BOR};}}
.chs-rank-top{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;}}
.chs-rank-name{{font-size:1rem;font-weight:800;color:{_TXT};display:flex;align-items:center;gap:8px;}}
.chs-rank-score{{font-family:'Sora',sans-serif;font-size:1.5rem;font-weight:800;}}
.chs-rank-meta{{display:flex;gap:12px;flex-wrap:wrap;font-size:0.73rem;color:{_SUB};margin-bottom:8px;}}
.chs-prog-track{{background:{_BOR};border-radius:10px;height:8px;overflow:hidden;}}
.chs-prog-fill{{height:100%;border-radius:10px;background:linear-gradient(90deg,#10B981,#059669);transition:width 0.4s ease;}}
.chs-all-item{{background:{_CARD};border:1px solid {_BOR};border-radius:12px;padding:12px 16px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;}}
.chs-all-name{{font-size:0.85rem;font-weight:700;color:{_TXT};}}
.chs-all-meta{{font-size:0.70rem;color:{_SUB};display:flex;gap:10px;flex-wrap:wrap;}}
.chs-score-pill{{font-size:0.78rem;font-weight:800;padding:3px 10px;border-radius:20px;}}
@media(max-width:600px){{
    .chs-hero{{padding:1.4rem 1rem;border-radius:18px;}}.chs-hero-title{{font-size:1.4rem;}}
    .chs-summary-grid{{grid-template-columns:1fr 1fr;}}
    .chs-rank-meta{{gap:7px;}}
}}
</style>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # HERO
    # ════════════════════════════════════════════════════════
    st.markdown(
        "<div class='chs-hero'>"
        "<div class='chs-hero-title'>🏙️ City Health Score</div>"
        "<div class='chs-hero-sub'>Ranking areas by cleanliness, efficiency &amp; citizen satisfaction</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════
    # FETCH + GUARD
    # ════════════════════════════════════════════════════════
    comps = api("get", "/complaints/all")
    if not isinstance(comps, list) or not comps:
        st.markdown(
            f"<div style='text-align:center;padding:3rem 2rem;"
            f"background:{_CARD};border-radius:22px;"
            f"border:1.5px dashed {_BOR};'>"
            f"<div style='font-size:3rem;opacity:0.5;margin-bottom:12px;'>🏙️</div>"
            f"<div style='font-size:0.95rem;font-weight:700;color:{_TXT};'>"
            f"No complaints data available</div>"
            f"<div style='font-size:0.78rem;color:{_SUB};margin-top:6px;'>"
            f"Area rankings will appear once complaints are filed.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        return

    # ════════════════════════════════════════════════════════
    # AGGREGATE BY AREA
    # ════════════════════════════════════════════════════════
    areas: dict = {}
    total_complaints = len(comps)

    for c in comps:
        loc  = c.get("location","Unknown Area")
        area = loc.split(",")[0].strip() if "," in loc else loc.strip() or "Unknown Area"
        if area not in areas:
            areas[area] = {"total":0,"resolved":0,"ratings_sum":0.0,"ratings_count":0}
        areas[area]["total"] += 1
        if c.get("status") in ("resolved","closed"):
            areas[area]["resolved"] += 1
        rating = c.get("rating")
        if rating and isinstance(rating, dict):
            stars = rating.get("stars")
            try:
                stars = float(stars)
                if 0 < stars <= 5:
                    areas[area]["ratings_sum"]   += stars
                    areas[area]["ratings_count"] += 1
            except (TypeError, ValueError):
                pass

    # ═════════════════════���══════════════════════════════════
    # COMPUTE HEALTH SCORE  (all values clamped)
    # ════════════════════════════════════════════════════════
    area_metrics = []
    for area, d in areas.items():
        total    = max(d["total"], 1)
        resolved = max(0, min(d["resolved"], total))          # clamp 0–total
        res_rate = round(resolved / total * 100, 1)           # 0–100
        avg_rat  = round(
            d["ratings_sum"] / d["ratings_count"], 1
        ) if d["ratings_count"] > 0 else 2.5
        avg_rat  = max(0.0, min(5.0, avg_rat))               # clamp 0–5

        # density penalty: share of total complaints × 10  (0–10)
        density_penalty = min(10.0, round(d["total"] / total_complaints * 10, 2))

        # health score: 0–100 range theoretical
        # res_rate*0.5 (0–50) + avg_rat*10 (0–50) - density (0–10) → clamp 0–100
        raw_score = (res_rate * 0.5) + (avg_rat * 10.0) - density_penalty
        health_score = round(max(0.0, min(100.0, raw_score)), 1)

        area_metrics.append({
            "area":            area,
            "total":           d["total"],
            "resolved":        resolved,
            "resolution_rate": res_rate,
            "avg_rating":      avg_rat,
            "rating_count":    d["ratings_count"],
            "health_score":    health_score,
        })

    area_metrics.sort(key=lambda x: x["health_score"], reverse=True)

    # ════════════════════════════════════════════════════════
    # SUMMARY CARDS
    # ════════════════════════════════════════════════════════
    best  = area_metrics[0]  if area_metrics else None
    worst = area_metrics[-1] if len(area_metrics) > 1 else None

    st.markdown("<div class='chs-summary-grid'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # close immediately; use columns below

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(
            f"<div class='chs-sum-card green'>"
            f"<div class='chs-sum-num'>{'🥇 ' + best['area'] if best else 'N/A'}</div>"
            f"<div class='chs-sum-lbl'>🏆 Cleanest Area</div>"
            f"{'<div style=\"font-size:0.72rem;color:#10B981;margin-top:4px;font-weight:700;\">Score ' + str(best['health_score']) + '</div>' if best else ''}"
            f"</div>",
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            f"<div class='chs-sum-card red'>"
            f"<div class='chs-sum-num'>{'⚠️ ' + worst['area'] if worst else 'N/A'}</div>"
            f"<div class='chs-sum-lbl'>⚠️ Needs Attention</div>"
            f"{'<div style=\"font-size:0.72rem;color:#EF4444;margin-top:4px;font-weight:700;\">Score ' + str(worst['health_score']) + '</div>' if worst else ''}"
            f"</div>",
            unsafe_allow_html=True,
        )
    with sc3:
        st.markdown(
            f"<div class='chs-sum-card blue'>"
            f"<div class='chs-sum-num'>{len(area_metrics)}</div>"
            f"<div class='chs-sum-lbl'>📊 Areas Analysed</div>"
            f"<div style='font-size:0.72rem;color:{_A1};margin-top:4px;font-weight:700;'>"
            f"{total_complaints} total complaints</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ════════════════════════════════════════════════════════
    # LEADERBOARD — top 10
    # ════════════════════════════════════════════════════════
    st.markdown("<div class='chs-sec'>🏙️ Area Ranking Leaderboard</div>", unsafe_allow_html=True)

    MEDALS    = {0:"🥇",1:"🥈",2:"🥉"}
    CARD_CLS  = {0:"gold",1:"silver",2:"bronze"}
    SCORE_CLR = {
        True:  ("#22C55E","rgba(34,197,94,0.15)") if True else None,  # placeholder
    }

    for idx, a in enumerate(area_metrics[:10]):
        medal    = MEDALS.get(idx, f"#{idx+1}")
        card_cls = CARD_CLS.get(idx, "normal")

        # score pill color
        sc = a["health_score"]
        if sc >= 70:
            score_color, score_bg = "#22C55E", "rgba(34,197,94,0.15)"
        elif sc >= 40:
            score_color, score_bg = "#F59E0B", "rgba(245,158,11,0.15)"
        else:
            score_color, score_bg = "#EF4444", "rgba(239,68,68,0.15)"

        # star display
        avg = max(0.0, min(5.0, float(a["avg_rating"])))
        full_s  = int(avg)
        half_s  = 1 if (avg - full_s) >= 0.5 else 0
        empty_s = 5 - full_s - half_s
        star_str = "★"*full_s + ("⯨" if half_s else "") + "☆"*empty_s

        # resolution bar clamped 0–100
        bar_w = max(0, min(100, int(a["resolution_rate"])))

        st.markdown(
            f"<div class='chs-rank-card {card_cls}'>"
            f"<div class='chs-rank-top'>"
            f"<div class='chs-rank-name'>{medal} {a['area']}</div>"
            f"<div class='chs-rank-score' style='color:{score_color};background:{score_bg};"
            f"border-radius:12px;padding:4px 14px;font-size:1.2rem;'>{sc}</div>"
            f"</div>"
            f"<div class='chs-rank-meta'>"
            f"<span>📋 {a['total']} complaints</span>"
            f"<span>✅ {a['resolved']} resolved</span>"
            f"<span>📈 {a['resolution_rate']}%</span>"
            f"<span style='color:#F59E0B;'>{star_str} {a['avg_rating']}"
            f"{'  (' + str(a['rating_count']) + ' reviews)' if a['rating_count'] else '  (no ratings)'}"
            f"</span>"
            f"</div>"
            f"<div class='chs-prog-track'>"
            f"<div class='chs-prog-fill' style='width:{bar_w}%;'></div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ════════════════════════════════════════════════════════
    # ALL AREAS EXPANDER
    # ════════════════════════════════════════════════════════
    with st.expander(f"📋 View All {len(area_metrics)} Areas", expanded=False):
        for a in area_metrics:
            sc = a["health_score"]
            sc_color = "#22C55E" if sc>=70 else "#F59E0B" if sc>=40 else "#EF4444"
            sc_bg    = ("rgba(34,197,94,0.12)" if sc>=70
                        else "rgba(245,158,11,0.12)" if sc>=40
                        else "rgba(239,68,68,0.12)")
            st.markdown(
                f"<div class='chs-all-item'>"
                f"<div>"
                f"<div class='chs-all-name'>{a['area']}</div>"
                f"<div class='chs-all-meta'>"
                f"<span>📋 {a['total']}</span>"
                f"<span>✅ {a['resolved']}</span>"
                f"<span>📈 {a['resolution_rate']}%</span>"
                f"<span>⭐ {a['avg_rating']}</span>"
                f"</div>"
                f"</div>"
                f"<span class='chs-score-pill' style='color:{sc_color};background:{sc_bg};'>{sc}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ════════════════════════════════════════════════════════
    # TOP 5 BAR CHART
    # ════════════════════════════════════════════════════════
    st.markdown("<div class='chs-sec'>📊 Health Score — Top 5 Areas</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='background:{_CARD};border:1px solid {_BOR};"
        f"border-radius:16px;padding:16px 20px;'>",
        unsafe_allow_html=True,
    )
    for a in area_metrics[:5]:
        sc   = a["health_score"]
        pct  = max(0, min(100, sc))   # score is already 0–100
        clr  = "#22C55E" if sc>=70 else "#F59E0B" if sc>=40 else "#EF4444"
        st.markdown(
            f"<div style='margin-bottom:10px;'>"
            f"<div style='display:flex;justify-content:space-between;"
            f"font-size:0.80rem;font-weight:700;color:{_TXT};margin-bottom:5px;'>"
            f"<span>{a['area']}</span><span style='color:{clr};'>{sc}</span></div>"
            f"<div style='background:{_BOR};border-radius:10px;height:10px;overflow:hidden;'>"
            f"<div style='width:{pct}%;height:100%;border-radius:10px;"
            f"background:linear-gradient(90deg,{clr},{clr}CC);'></div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    bc1, bc2, bc3 = st.columns([1,2,1])
    with bc2:
        if st.button("← Back to Dashboard", key="chs_back", use_container_width=True):
            st.session_state.screen = "admin_dashboard"
            st.rerun()


# ════════════════════════════════════════════════════════════════
# DEPT DRILL
# ════════════════════════════════════════════════════════════════
def _dept_drill():
    _apply_layout("admin")  
    dark  = st.session_state.get("dark_mode", False)
    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)

    _CARD = "#10161F" if dark else "#FFFFFF"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
    _A1   = "#6366F1"
    _A2   = "#8B5CF6"

    meta_pill_bg = "#1A2236" if dark else "#F1F5F9"

    st.markdown(f"""
<style>
/* ── drill hero ── */
.dd-hero{{
    background:linear-gradient(135deg,#1e1b4b 0%,#312e81 50%,#1e3a5f 100%);
    border-radius:22px;padding:1.75rem 2rem;margin-bottom:1.75rem;
    position:relative;overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,0.25);
}}
.dd-hero::before{{
    content:'';position:absolute;top:-60px;right:-60px;
    width:200px;height:200px;border-radius:50%;
    background:radial-gradient(circle,rgba(255,255,255,0.07) 0%,transparent 70%);
    pointer-events:none;
}}
.dd-hero-title{{
    font-family:'Sora',sans-serif;font-size:1.6rem;font-weight:800;
    color:#fff;margin-bottom:5px;position:relative;z-index:1;
}}
.dd-hero-code{{
    font-family:'Courier New',monospace;font-size:0.82rem;
    color:rgba(255,255,255,0.65);position:relative;z-index:1;
}}

/* ── section header ── */
.dd-sec{{
    font-size:0.70rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.10em;color:{_SUB};margin:18px 0 10px;
    display:flex;align-items:center;gap:10px;
}}
.dd-sec::before{{
    content:'';width:4px;height:16px;
    background:linear-gradient(180deg,{_A1},{_A2});
    border-radius:3px;flex-shrink:0;
}}
.dd-sec::after{{
    content:'';flex:1;height:1px;
    background:linear-gradient(to right,{_BOR},transparent);
}}

/* ── official cards ── */
.dd-off-card{{
    background:{_CARD};border:1px solid {_BOR};border-left:4px solid;
    border-radius:14px;padding:14px 16px;margin-bottom:8px;
    transition:transform 0.18s;
}}
.dd-off-card:hover{{transform:translateX(3px);}}
.dd-off-name{{font-size:0.90rem;font-weight:800;color:{_TXT};margin-bottom:5px;}}
.dd-off-meta{{
    display:flex;gap:8px;flex-wrap:wrap;align-items:center;
    font-size:0.72rem;color:{_SUB};
}}
.dd-meta-tag{{
    background:{meta_pill_bg};border:1px solid {_BOR};
    border-radius:20px;padding:2px 9px;font-size:0.68rem;font-weight:600;color:{_SUB};
}}

/* ── stat chips on official cards ── */
.dd-stat-row{{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;}}
.dd-stat{{border-radius:10px;padding:6px 12px;border:1px solid;text-align:center;}}
.dd-stat-num{{font-size:0.82rem;font-weight:800;line-height:1;margin-bottom:1px;}}
.dd-stat-lbl{{font-size:0.58rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.05em;opacity:0.70;}}
.dd-stat.res{{
    background:{"rgba(74,222,128,0.10)" if dark else "#F0FDF4"};
    border-color:{"rgba(74,222,128,0.22)" if dark else "#BBF7D0"};
}}
.dd-stat.res .dd-stat-num{{color:{"#4ADE80" if dark else "#15803D"};}}
.dd-stat.rat{{
    background:{"rgba(251,146,60,0.10)" if dark else "#FFF7ED"};
    border-color:{"rgba(251,146,60,0.22)" if dark else "#FED7AA"};
}}
.dd-stat.rat .dd-stat-num{{color:{"#FB923C" if dark else "#C2410C"};}}

/* ── pending card wrapper: card + buttons inside one visual block ── */
.dd-pending-wrap{{
    background:{_CARD};
    border:1px solid {_BOR};
    border-left:4px solid #D97706;
    border-radius:14px;
    padding:14px 16px 10px;
    margin-bottom:10px;
    transition:transform 0.18s;
}}
.dd-pending-wrap:hover{{transform:translateX(3px);}}
.dd-pending-wrap .dd-off-name{{
    font-size:0.90rem;font-weight:800;color:{_TXT};margin-bottom:5px;
}}
.dd-pending-wrap .dd-off-meta{{
    display:flex;gap:8px;flex-wrap:wrap;align-items:center;
    font-size:0.72rem;color:{_SUB};margin-bottom:10px;
}}

/* Make the button row inside pending wrap blend with the card */
.dd-pending-wrap div[data-testid="stHorizontalBlock"]{{
    gap:8px !important;
}}

/* ── action button overrides ── */
div[data-testid="stButton"].dd-approve > button,
div[data-testid="stButton"] > button[kind="primary"].dd-approve-btn{{
    background:linear-gradient(135deg,#15803D,#22C55E) !important;
    color:#fff !important;border:none !important;
    box-shadow:0 4px 10px rgba(34,197,94,0.28) !important;
}}

/* Approve button (green) - targets buttons with specific keys */
button[data-testid="baseButton-secondary"][kind="secondary"]:has(div:contains("✅")){{
    background:linear-gradient(135deg,#15803D,#22C55E) !important;
}}

/* Generic styling for buttons inside pending wrap */
.dd-pending-wrap div[data-testid="stButton"] > button{{
    border-radius:10px !important;
    font-weight:700 !important;
    height:38px !important;
    transition:all 0.18s !important;
}}
</style>
""", unsafe_allow_html=True)

    did = st.session_state.viewing_dept_id
    dnm = st.session_state.viewing_dept_name
    dcd = st.session_state.viewing_dept_code

    # ── back button ───────────────────────────────────────────────
    bc1, bc2, bc3 = st.columns([1, 2, 1])
    with bc2:
        if st.button("← Back to Departments", key="dd_back", use_container_width=True):
            st.session_state.viewing_dept_id = None
            st.rerun()

    # ── hero ──────────────────────────────────────────────────────
    st.markdown(
        f"<div class='dd-hero'>"
        f"<div class='dd-hero-title'>🏢 {dnm}</div>"
        f"<div class='dd-hero-code'>"
        f"Dept Code: <strong>{dcd}</strong> · Share with officials to join"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── tabs ───��──────────────────────────────────────────────────
    def _stars(avg, cnt):
        try:
            v = max(0.0, min(5.0, float(avg or 0)))
        except (TypeError, ValueError):
            v = 0.0
        if not cnt:
            return "☆☆☆☆☆", "No ratings"
        f_ = int(v)
        h_ = 1 if (v - f_) >= 0.5 else 0
        e_ = 5 - f_ - h_
        s  = "★" * f_ + ("⯨" if h_ else "") + "☆" * e_
        return s, f"{v:.1f} ({cnt})"

    tab1, tab2, tab3 = st.tabs(["👥 Officials", "📢 Complaints", "🏆 Leaderboard"])

    # ── TAB 1 — Officials ─────────────────────────────────────────
    with tab1:
        officials  = api("get", f"/admin/departments/{did}/officials")
        officials  = officials if isinstance(officials, list) else []
        pending_o  = [o for o in officials if not o.get("is_approved")]
        approved_o = [o for o in officials if     o.get("is_approved")]

        # pending
        st.markdown(
            f"<div class='dd-sec'>⏳ Pending Approval"
            f"{' (' + str(len(pending_o)) + ')' if pending_o else ''}"
            f"</div>",
            unsafe_allow_html=True,
        )
        if not pending_o:
            st.info("No pending officials in this department.")
        else:
            for o in pending_o:
                oid = o.get("id")
                joined_tag = (
                    f"<span class='dd-meta-tag'>📅 {o['joined']}</span>"
                    if o.get("joined") else ""
                )

                # Use a container with custom class to wrap card + buttons
                with st.container():
                    st.markdown(
                        f"<div class='dd-pending-wrap'>"
                        f"<div class='dd-off-name'>👤 {o.get('name','—')}</div>"
                        f"<div class='dd-off-meta'>"
                        f"<span class='dd-meta-tag'>📧 {o.get('email','—')}</span>"
                        f"{joined_tag}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    # Buttons inline inside the card visual block
                    pa1, pa2, pa3 = st.columns([4, 1, 1])
                    with pa2:
                        st.markdown("<div class='dd-approve'>", unsafe_allow_html=True)
                        if st.button("✅ Approve", key=f"da_{oid}", use_container_width=True, help="Approve"):
                            api("put", f"/admin/officials/{oid}/approve")
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    with pa3:
                        st.markdown("<div class='dd-reject'>", unsafe_allow_html=True)
                        if st.button("❌ Reject", key=f"dr_{oid}", use_container_width=True, help="Reject"):
                            api("put", f"/admin/officials/{oid}/reject")
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

        # approved
        st.markdown(
            f"<div class='dd-sec'>✅ Approved"
            f"{' (' + str(len(approved_o)) + ')' if approved_o else ''}"
            f"</div>",
            unsafe_allow_html=True,
        )
        if not approved_o:
            st.info("No approved officials yet.")
        else:
            for o in approved_o:
                oid      = o.get("id")
                resolved = max(0, int(o.get("total_resolved", 0) or 0))
                assigned = max(1, int(o.get("total_assigned", 1) or 1))
                res_rate = min(100, round(resolved / assigned * 100, 1))
                s_str, s_lbl = _stars(o.get("avg_rating", 0), o.get("rating_count", 0))

                joined_tag = (
                    f"<span class='dd-meta-tag'>📅 {o['joined']}</span>"
                    if o.get("joined") else ""
                )

                st.markdown(
                    f"<div class='dd-off-card' style='border-left-color:#22C55E;'>"
                    f"<div class='dd-off-name'>👤 {o.get('name','—')}</div>"
                    f"<div class='dd-off-meta'>"
                    f"<span class='dd-meta-tag'>📧 {o.get('email','—')}</span>"
                    f"{joined_tag}"
                    f"</div>"
                    f"<div class='dd-stat-row'>"
                    f"<div class='dd-stat res'>"
                    f"<div class='dd-stat-num'>{res_rate}%</div>"
                    f"<div class='dd-stat-lbl'>Res. Rate</div>"
                    f"</div>"
                    f"<div class='dd-stat res'>"
                    f"<div class='dd-stat-num'>{resolved}</div>"
                    f"<div class='dd-stat-lbl'>Resolved</div>"
                    f"</div>"
                    f"<div class='dd-stat rat'>"
                    f"<div class='dd-stat-num' style='color:#F59E0B;'>{s_str}</div>"
                    f"<div class='dd-stat-lbl'>{s_lbl}</div>"
                    f"</div>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # ── TAB 2 — Complaints ────────────────────────────────────────
    with tab2:
        comps = api("get", f"/admin/departments/{did}/complaints")
        comps = comps if isinstance(comps, list) else []
        if not comps:
            st.info("No complaints for this department yet.")
        else:
            _complaint_list(comps, "dd", None)

    # ── TAB 3 — Leaderboard ───────────────────────────────────────
    with tab3:
        _dept_leaderboard(did)
 
 
def _dept_leaderboard(dept_id):
    _apply_layout("admin")  
    board = api("get", f"/admin/leaderboard/department/{dept_id}")
    board = board if isinstance(board, list) else []
    _render_leaderboard(board)


def pg_admin_officials():
    _apply_layout("admin")  
    dark  = st.session_state.get("dark_mode", False)
    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)

    _CARD = "#10161F" if dark else "#FFFFFF"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
    _HOV  = "#16213A" if dark else "#F8FAFF"
    _A1   = "#6366F1"
    _A2   = "#8B5CF6"

    st.markdown(f"""
<style>
/* ── HERO ── */
.off-hero{{
    background:linear-gradient(135deg,#1e1b4b 0%,#312e81 50%,#0f2744 100%);
    border-radius:22px;padding:1.75rem 2rem;margin-bottom:1.75rem;
    position:relative;overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,0.25);
}}
.off-hero::before{{content:'';position:absolute;top:-60px;right:-60px;
    width:220px;height:220px;border-radius:50%;
    background:radial-gradient(circle,rgba(255,255,255,0.07) 0%,transparent 70%);
    pointer-events:none;}}
.off-hero-title{{font-family:'Sora',sans-serif;font-size:1.75rem;font-weight:800;
    color:#fff;margin-bottom:5px;position:relative;z-index:1;}}
.off-hero-sub{{font-size:0.86rem;color:rgba(255,255,255,0.65);
    position:relative;z-index:1;font-weight:500;}}
.off-hero-badges{{display:flex;gap:10px;margin-top:14px;position:relative;z-index:1;flex-wrap:wrap;}}
.off-hero-stat{{
    background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.18);
    border-radius:12px;padding:10px 16px;text-align:center;min-width:80px;
}}
.off-hero-stat-num{{font-family:'Sora',sans-serif;font-size:1.5rem;font-weight:800;
    color:#fff;line-height:1;margin-bottom:3px;}}
.off-hero-stat-lbl{{font-size:0.60rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.08em;color:rgba(255,255,255,0.55);}}

/* ── SECTION HEADER ── */
.off-sec{{font-size:0.70rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.10em;color:{_SUB};margin:22px 0 12px;
    display:flex;align-items:center;gap:10px;}}
.off-sec::before{{content:'';width:4px;height:16px;
    background:linear-gradient(180deg,{_A1},{_A2});border-radius:3px;flex-shrink:0;}}
.off-sec::after{{content:'';flex:1;height:1px;
    background:linear-gradient(to right,{_BOR},transparent);}}

/* ── NO PENDING BANNER ── */
.off-no-pending{{
    background:{"rgba(74,222,128,0.08)" if dark else "#F0FDF4"};
    border:1px solid {"rgba(74,222,128,0.20)" if dark else "#BBF7D0"};
    border-radius:14px;padding:14px 18px;
    display:flex;gap:10px;align-items:center;margin-bottom:4px;
}}
.off-no-pending-text{{font-size:0.83rem;font-weight:600;
    color:{"#4ADE80" if dark else "#15803D"};}}

/* ── META TAG ── */
.off-meta-tag{{
    background:{"#1A2236" if dark else "#F1F5F9"};
    border:1px solid {_BOR};border-radius:20px;
    padding:2px 9px;font-size:0.68rem;font-weight:600;color:{_SUB};
    display:inline-flex;align-items:center;gap:4px;
}}
.off-meta-tag.code{{
    background:rgba(99,102,241,0.12);color:{_A1};
    border-color:rgba(99,102,241,0.25);font-family:'Courier New',monospace;font-weight:800;
}}

/* ── PENDING CARD ── */
.off-pend-card{{
    background:{_CARD};
    border:1px solid {"rgba(217,119,6,0.35)" if dark else "#FDE68A"};
    border-left:4px solid #D97706;
    border-radius:18px;padding:18px 20px 14px;
    box-shadow:0 0 0 3px {"rgba(120,53,15,0.10)" if dark else "#FFFBEB"};
    margin-bottom:4px;
}}

/* ── APPROVED CARD ── */
.off-appr-card{{
    background:{_CARD};
    border:1px solid {_BOR};
    border-left:4px solid #22C55E;
    border-radius:18px;padding:18px 20px 14px;
    box-shadow:0 2px 12px rgba(15,23,42,0.06);
    margin-bottom:4px;
    transition:box-shadow 0.18s;
}}
.off-appr-card:hover{{box-shadow:0 8px 28px rgba(34,197,94,0.10);}}

/* ── CARD NAME ── */
.off-card-name{{
    font-size:0.96rem;font-weight:800;color:{_TXT};
    margin-bottom:6px;display:flex;align-items:center;gap:8px;
}}
.off-card-meta{{
    display:flex;gap:8px;flex-wrap:wrap;align-items:center;
    margin-bottom:12px;
}}

/* ── STAT PILLS ── */
.off-stats-row{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;}}
.off-stat-pill{{
    border-radius:10px;padding:7px 13px;text-align:center;border:1px solid;min-width:72px;
}}
.off-stat-pill-num{{font-size:0.90rem;font-weight:800;line-height:1;margin-bottom:2px;}}
.off-stat-pill-lbl{{font-size:0.58rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.05em;opacity:0.70;}}
.off-stat-pill.assigned{{
    background:rgba(99,102,241,0.10);border-color:rgba(99,102,241,0.22);}}
.off-stat-pill.assigned .off-stat-pill-num{{color:{_A1};}}
.off-stat-pill.assigned .off-stat-pill-lbl{{color:{_A1};}}
.off-stat-pill.resolved{{
    background:{"rgba(74,222,128,0.12)" if dark else "#F0FDF4"};
    border-color:{"rgba(74,222,128,0.25)" if dark else "#BBF7D0"};}}
.off-stat-pill.resolved .off-stat-pill-num{{color:{"#4ADE80" if dark else "#15803D"};}}
.off-stat-pill.resolved .off-stat-pill-lbl{{color:{"#4ADE80" if dark else "#15803D"};}}
.off-stat-pill.rate{{
    background:{"rgba(251,191,36,0.12)" if dark else "#FFFBEB"};
    border-color:{"rgba(251,191,36,0.25)" if dark else "#FDE68A"};}}
.off-stat-pill.rate .off-stat-pill-num{{color:{"#FBBF24" if dark else "#B45309"};}}
.off-stat-pill.rate .off-stat-pill-lbl{{color:{"#FBBF24" if dark else "#B45309"};}}
.off-stat-pill.rating{{
    background:{"rgba(251,146,60,0.12)" if dark else "#FFF7ED"};
    border-color:{"rgba(251,146,60,0.22)" if dark else "#FED7AA"};}}
.off-stat-pill.rating .off-stat-pill-num{{color:{"#FB923C" if dark else "#C2410C"};}}
.off-stat-pill.rating .off-stat-pill-lbl{{color:{"#FB923C" if dark else "#C2410C"};}}

/* ── DIVIDER INSIDE CARD ── */
.off-card-divider{{
    height:1px;
    background:linear-gradient(90deg,transparent,{_BOR},transparent);
    margin:10px 0 12px;
}}

/* ── ACTION BUTTONS INSIDE CARD ── */
.off-btn-approve .stButton>button{{
    background:linear-gradient(135deg,#15803D,#22C55E)!important;
    color:#fff!important;border:none!important;
    border-radius:10px!important;font-size:0.80rem!important;
    font-weight:700!important;height:38px!important;
    box-shadow:0 4px 12px rgba(34,197,94,0.28)!important;
    transition:all 0.18s!important;
}}
.off-btn-approve .stButton>button:hover{{
    transform:translateY(-2px)!important;
    box-shadow:0 8px 20px rgba(34,197,94,0.40)!important;
    filter:brightness(1.05)!important;
}}
.off-btn-reject .stButton>button{{
    background:{"rgba(220,38,38,0.10)" if dark else "#FFF1F2"}!important;
    color:{"#F87171" if dark else "#BE123C"}!important;
    border:1.5px solid {"rgba(220,38,38,0.25)" if dark else "#FECDD3"}!important;
    border-radius:10px!important;font-size:0.80rem!important;
    font-weight:700!important;height:38px!important;
    box-shadow:none!important;transition:all 0.18s!important;
}}
.off-btn-reject .stButton>button:hover{{
    background:{"rgba(220,38,38,0.18)" if dark else "#FFE4E6"}!important;
    transform:translateY(-1px)!important;
}}
.off-btn-remove .stButton>button{{
    background:{"rgba(220,38,38,0.10)" if dark else "#FFF1F2"}!important;
    color:{"#F87171" if dark else "#BE123C"}!important;
    border:1.5px solid {"rgba(220,38,38,0.25)" if dark else "#FECDD3"}!important;
    border-radius:12px!important;font-size:1.1rem!important;
    font-weight:700!important;height:40px!important;width:40px!important;
    min-width:40px!important;max-width:40px!important;
    padding:0!important;display:inline-flex!important;
    align-items:center!important;justify-content:center!important;
    box-shadow:none!important;transition:all 0.18s!important;
}}
.off-btn-remove .stButton>button:hover{{
    background:{"rgba(220,38,38,0.22)" if dark else "#FFE4E6"}!important;
    transform:translateY(-2px)!important;
    box-shadow:0 4px 12px rgba(239,68,68,0.20)!important;
}}

@media(max-width:600px){{
    .off-hero{{padding:1.4rem 1rem;border-radius:18px;}}
    .off-hero-title{{font-size:1.4rem;}}
    .off-stats-row{{gap:6px;}}
    .off-card-meta{{gap:5px;}}
}}
</style>
""", unsafe_allow_html=True)

    # ── FETCH ─────────────────────────────────────────────────────
    pending  = api("get", "/admin/officials/pending")
    all_offs = api("get", "/admin/officials/all")
    pending  = pending  if isinstance(pending,  list) else []
    all_offs = all_offs if isinstance(all_offs, list) else []
    approved = [o for o in all_offs if o.get("is_approved")]

    # ── HERO ──────────────────────────────────────────────────────
    st.markdown(
        f"<div class='off-hero'>"
        f"<div class='off-hero-title'>👥 Officials Management</div>"
        f"<div class='off-hero-sub'>Approve · reject · monitor performance</div>"
        f"<div class='off-hero-badges'>"
        f"<div class='off-hero-stat'><div class='off-hero-stat-num'>{len(approved)}</div>"
        f"<div class='off-hero-stat-lbl'>✅ Active</div></div>"
        f"<div class='off-hero-stat'><div class='off-hero-stat-num' style='color:#FCD34D;'>{len(pending)}</div>"
        f"<div class='off-hero-stat-lbl'>⏳ Pending</div></div>"
        f"<div class='off-hero-stat'><div class='off-hero-stat-num'>{len(all_offs)}</div>"
        f"<div class='off-hero-stat-lbl'>👥 Total</div></div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    # ── PENDING APPROVALS ──────────────────────────────────────────
    st.markdown(
        f"<div class='off-sec'>⏳ Awaiting Approval"
        f"{'  (' + str(len(pending)) + ')' if pending else ''}</div>",
        unsafe_allow_html=True,
    )

    if not pending:
        st.markdown(
            f"<div class='off-no-pending'>"
            f"<span style='font-size:1.2rem;'>🎉</span>"
            f"<div class='off-no-pending-text'>No pending approvals — all caught up!</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        for o in pending:
            oid  = o.get("id")
            dept = o.get("department", "—")
            code = o.get("dept_code", "—")

            # Card header
            st.markdown(
                f"<div class='off-pend-card'>"
                f"<div class='off-card-name'>"
                f"<span style='background:rgba(217,119,6,0.15);border-radius:50%;width:32px;height:32px;"
                f"display:inline-flex;align-items:center;justify-content:center;font-size:0.9rem;'>👤</span>"
                f"{o.get('name','—')}"
                f"<span style='background:#FFFBEB;color:#92400E;border-radius:6px;"
                f"padding:2px 8px;font-size:0.62rem;font-weight:700;border:1px solid #FDE68A;'>⏳ PENDING</span>"
                f"</div>"
                f"<div class='off-card-meta'>"
                f"<span class='off-meta-tag'>📧 {o.get('email','—')}</span>"
                f"<span class='off-meta-tag'>🏢 {dept}</span>"
                f"<span class='off-meta-tag code'>🔑 {code}</span>"
                f"{'<span class=\"off-meta-tag\">📅 ' + str(o.get('joined','')) + '</span>' if o.get('joined') else ''}"
                f"</div>"
                f"<div class='off-card-divider'></div>",
                unsafe_allow_html=True,
            )

            # Approve / Reject buttons inside card
            ba1, ba2 = st.columns(2)
            with ba1:
                st.markdown("<div class='off-btn-approve'>", unsafe_allow_html=True)
                if st.button("✅ Approve", key=f"apv_{oid}", use_container_width=True):
                    api("put", f"/admin/officials/{oid}/approve")
                    st.success("✅ Approved!")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with ba2:
                st.markdown("<div class='off-btn-reject'>", unsafe_allow_html=True)
                if st.button("❌ Reject", key=f"rej_{oid}", use_container_width=True):
                    api("put", f"/admin/officials/{oid}/reject")
                    st.warning("Rejected.")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div><div style='height:8px'></div>", unsafe_allow_html=True)

    # ── ACTIVE OFFICIALS ────────────────────────────────────────��──
    if approved:
        st.markdown(
            f"<div class='off-sec'>✅ Active Officials ({len(approved)})</div>",
            unsafe_allow_html=True,
        )

        for o in approved:
            oid        = o.get("id")
            assigned   = o.get("total_assigned", 0)
            resolved   = o.get("total_resolved", 0)
            avg_rating = float(o.get("avg_rating", 0) or 0)
            rating_cnt = o.get("rating_count", 0) or 0
            res_rate   = round(resolved / max(assigned, 1) * 100, 1)

            full  = int(avg_rating)
            half  = 1 if (avg_rating - full) >= 0.5 else 0
            empty = 5 - full - half
            star_str = "★" * full + ("½" if half else "") + "☆" * empty

            bar_color = (
                "linear-gradient(90deg,#22C55E,#10B981)" if res_rate >= 70
                else "linear-gradient(90deg,#F59E0B,#D97706)" if res_rate >= 40
                else "linear-gradient(90deg,#EF4444,#DC2626)"
            )

            # Card
            st.markdown(
                f"<div class='off-appr-card'>"
                f"<div class='off-card-name'>"
                f"<span style='background:rgba(34,197,94,0.12);border-radius:50%;width:32px;height:32px;"
                f"display:inline-flex;align-items:center;justify-content:center;font-size:0.9rem;'>👤</span>"
                f"{o.get('name','—')}"
                f"<span style='background:#F0FDF4;color:#15803D;border-radius:6px;"
                f"padding:2px 8px;font-size:0.62rem;font-weight:700;border:1px solid #BBF7D0;'>✅ ACTIVE</span>"
                f"</div>"
                f"<div class='off-card-meta'>"
                f"<span class='off-meta-tag'>📧 {o.get('email','—')}</span>"
                f"<span class='off-meta-tag'>🏢 {o.get('department','—')}</span>"
                f"{'<span class=\"off-meta-tag\">📅 ' + str(o.get('joined','')) + '</span>' if o.get('joined') else ''}"
                f"</div>"
                f"<div class='off-stats-row'>"
                f"<div class='off-stat-pill assigned'>"
                f"<div class='off-stat-pill-num'>{assigned}</div>"
                f"<div class='off-stat-pill-lbl'>Assigned</div></div>"
                f"<div class='off-stat-pill resolved'>"
                f"<div class='off-stat-pill-num'>{resolved}</div>"
                f"<div class='off-stat-pill-lbl'>Resolved</div></div>"
                f"<div class='off-stat-pill rate'>"
                f"<div class='off-stat-pill-num'>{res_rate}%</div>"
                f"<div class='off-stat-pill-lbl'>Rate</div></div>"
                f"<div class='off-stat-pill rating'>"
                f"<div class='off-stat-pill-num'>"
                f"<span style='color:#F59E0B;'>{star_str}</span> "
                f"<span style='font-size:0.72rem;'>{avg_rating:.1f}</span></div>"
                f"<div class='off-stat-pill-lbl'>{rating_cnt} reviews</div></div>"
                f"</div>"
                # Resolution progress bar
                f"<div style='background:{_BOR};border-radius:99px;height:6px;margin-bottom:4px;overflow:hidden;'>"
                f"<div style='width:{min(res_rate,100)}%;height:100%;border-radius:99px;"
                f"background:{bar_color};'></div></div>",
                unsafe_allow_html=True,
            )

            # Remove button (icon only) — inside card
            rc1, rc2 = st.columns([8, 1])
            with rc2:
                st.markdown("<div class='off-btn-remove'>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"rem_{oid}", use_container_width=True, help="Remove official"):
                    api("put", f"/admin/officials/{oid}/reject")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div><div style='height:8px'></div>", unsafe_allow_html=True)

def pg_admin_complaints():
    _apply_layout("admin")  

    # ══════════════════════════════════════════════════════════════════════════
    # NUCLEAR CSS — fixes black dropdown + premium overhaul
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <style>
    /* ════════════════════════════════════════════
       DROPDOWN / SELECTBOX — full nuclear override
       Streamlit portals dropdowns outside the app
       root so we must target every possible layer
    ════════════════════════════════════════════ */

    /* The portal container itself */
    body > div[data-portal="true"],
    body > div[data-portal="true"] *,
    [data-baseweb="popover"],
    [data-baseweb="popover"] *,
    [data-baseweb="menu"],
    [data-baseweb="menu"] * {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    /* Dropdown outer shell */
    [data-baseweb="popover"] {
        border-radius: 16px !important;
        border: 1.5px solid #E2E8F4 !important;
        box-shadow: 0 12px 40px rgba(15,23,42,0.14) !important;
        overflow: hidden !important;
        background: #FFFFFF !important;
    }

    /* Inner list wrapper */
    [data-baseweb="menu"],
    ul[role="listbox"],
    [role="listbox"] {
        background: #FFFFFF !important;
        padding: 6px !important;
    }

    /* Each option item */
    [data-baseweb="option"],
    li[role="option"],
    [role="option"] {
        background: #FFFFFF !important;
        color: #0F172A !important;
        border-radius: 10px !important;
        padding: 9px 14px !important;
        margin: 2px 0 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: background .15s !important;
        cursor: pointer !important;
    }

    [data-baseweb="option"]:hover,
    li[role="option"]:hover,
    [role="option"]:hover {
        background: #F1F5F9 !important;
        color: #6366F1 !important;
    }

    /* Selected option highlight */
    [aria-selected="true"][data-baseweb="option"],
    [aria-selected="true"][role="option"] {
        background: linear-gradient(135deg, rgba(99,102,241,.10), rgba(139,92,246,.08)) !important;
        color: #6366F1 !important;
        font-weight: 700 !important;
    }

    /* Selectbox trigger box */
    .stSelectbox > div > div {
        background: #FFFFFF !important;
        border: 1.5px solid #E2E8F4 !important;
        border-radius: 12px !important;
        color: #0F172A !important;
        transition: border-color .18s, box-shadow .18s !important;
    }
    .stSelectbox > div > div:focus-within {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,.12) !important;
    }

    /* All text inside selectbox trigger */
    .stSelectbox span,
    .stSelectbox div[data-baseweb="select"] span,
    .stSelectbox div[data-baseweb="select"] div,
    .stSelectbox [data-baseweb="select"] * {
        color: #0F172A !important;
        background: transparent !important;
    }

    /* Dropdown arrow icon */
    .stSelectbox svg {
        fill: #64748B !important;
    }

    /* ════════════════════════════════════════════
       RADIO → PILL TABS
    ════════════════════════════════════════════ */
    div[data-testid="stRadio"] > label { display: none !important; }

    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        background: transparent !important;
        padding: 4px 0 !important;
    }

    /* Every pill label */
    div[data-testid="stRadio"] > div > label {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: #F8FAFC !important;
        border: 1.5px solid #E2E8F4 !important;
        border-radius: 24px !important;
        padding: 7px 20px !important;
        font-size: .82rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
        cursor: pointer !important;
        letter-spacing: .01em !important;
        transition: all .18s ease !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }
    div[data-testid="stRadio"] > div > label:hover {
        border-color: #6366F1 !important;
        color: #6366F1 !important;
        background: rgba(99,102,241,.06) !important;
    }
    div[data-testid="stRadio"] > div > label[aria-checked="true"] {
        background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
        border-color: transparent !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(99,102,241,.38) !important;
    }
    /* Hide radio dot */
    div[data-testid="stRadio"] > div > label > div:first-child,
    div[data-testid="stRadio"] input[type="radio"] { display: none !important; }

    /* Label text */
    div[data-testid="stRadio"] p {
        font-size: .82rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    /* ════════════════════════════════════════════
       EXPANDER — premium style
    ════════════════════════════════════════════ */
    .streamlit-expanderHeader {
        background: #F8FAFC !important;
        border: 1.5px solid #E2E8F4 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        color: #475569 !important;
        font-size: 0.83rem !important;
        padding: 11px 16px !important;
        transition: all .18s !important;
    }
    .streamlit-expanderHeader:hover {
        border-color: #6366F1 !important;
        color: #6366F1 !important;
        background: rgba(99,102,241,.04) !important;
    }
    .streamlit-expanderContent {
        background: #FAFBFF !important;
        border: 1.5px solid #E2E8F4 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── FETCH DATA ────────────────────────────────────────────────────────────
    comps = api("get", "/complaints/all")
    comps = comps if isinstance(comps, list) else []

    total = len(comps)
    pen   = len([c for c in comps if c.get("status") == "pending"])
    inp   = len([c for c in comps if c.get("status") == "in_progress"])
    res   = len([c for c in comps if c.get("status") in ("resolved", "closed")])
    rej   = len([c for c in comps if c.get("status") == "rejected"])
    hi    = len([c for c in comps if c.get("priority") == "high"])
    emer  = len([c for c in comps if c.get("is_emergency")])
    rate  = round(res / total * 100) if total else 0

    # ── HERO ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="prem-hero" style="padding:28px 28px 24px;margin-bottom:0;">
        <div class="prem-hero-avatar">🛡️</div>
        <div class="prem-hero-title">Complaints Dashboard</div>
        <p class="prem-hero-sub">
            Monitor, filter and resolve all citizen complaints in real-time.
        </p>
        <div class="prem-hero-stats">
            <div class="prem-hstat">
                <div class="prem-hstat-num">""" + str(total) + """</div>
                <div class="prem-hstat-lbl">Total</div>
            </div>
            <div class="prem-hstat h-amber">
                <div class="prem-hstat-num">""" + str(pen) + """</div>
                <div class="prem-hstat-lbl">Pending</div>
            </div>
            <div class="prem-hstat h-blue">
                <div class="prem-hstat-num">""" + str(inp) + """</div>
                <div class="prem-hstat-lbl">In Progress</div>
            </div>
            <div class="prem-hstat h-green">
                <div class="prem-hstat-num">""" + str(res) + """</div>
                <div class="prem-hstat-lbl">Resolved</div>
            </div>
            <div class="prem-hstat h-red">
                <div class="prem-hstat-num">""" + str(hi) + """</div>
                <div class="prem-hstat-lbl">High Priority</div>
            </div>
            <div class="prem-hstat h-red">
                <div class="prem-hstat-num">🚨 """ + str(emer) + """</div>
                <div class="prem-hstat-lbl">Emergency</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── RESOLUTION RATE + QUICK INSIGHT ROW ──────────────────────────────────
    r_color = "#10b981" if rate >= 70 else "#F59E0B" if rate >= 40 else "#EF4444"
    r_label = "On Track 🎯" if rate >= 70 else "Needs Attention ⚠️" if rate >= 40 else "Critical 🚨"

    st.markdown(
        '<div class="prem-card" style="padding:18px 22px;margin:16px 0 6px;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">'
        '<div>'
        '<div style="font-size:.72rem;font-weight:800;text-transform:uppercase;'
        'letter-spacing:.08em;color:#64748B;margin-bottom:2px;">📊 Resolution Rate</div>'
        '<div style="font-size:.78rem;color:' + r_color + ';font-weight:700;">' + r_label + '</div>'
        '</div>'
        '<div style="font-size:2rem;font-weight:800;color:' + r_color + ';'
        'font-family:Sora,sans-serif;">' + str(rate) + '%</div>'
        '</div>'
        '<div class="prem-prog-wrap" style="height:14px;">'
        '<div class="prem-prog-fill" style="width:' + str(rate) + '%;'
        'background:linear-gradient(90deg,' + r_color + ',' + r_color + 'aa);">'
        '<span class="prem-prog-text" style="font-size:.62rem;">' + str(rate) + '%</span>'
        '</div></div>'
        '<div style="display:flex;justify-content:space-between;margin-top:6px;'
        'font-size:.67rem;color:#CBD5E1;font-weight:600;">'
        '<span>0%</span><span style="color:#94A3B8;">🎯 Target: 80%</span><span>100%</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ── FILTER SECTION ────────────────────────────────────────────────────────
    st.markdown('<div class="prem-section-header">🔽 Filter &amp; Search</div>', unsafe_allow_html=True)

    # Status pills
    st_r = st.radio(
        "",
        ["All", "Pending", "In Progress", "Resolved", "Rejected", "Closed"],
        horizontal=True, key="ac_radio"
    )
    smap = {
        "All": "all", "Pending": "pending", "In Progress": "in_progress",
        "Resolved": "resolved", "Rejected": "rejected", "Closed": "closed"
    }
    sf = smap[st_r]

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Filter dropdowns + search
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        fpr = st.selectbox("🎯 Priority", ["all", "high", "medium", "low"], key="ac_pr")
    with f2:
        depts = api("get", "/admin/departments")
        dn    = ["all"] + [d.get("name", "") for d in (depts if isinstance(depts, list) else [])]
        fdp   = st.selectbox("🏢 Department", dn, key="ac_dp")
    with f3:
        fsq = st.text_input(
            "", placeholder="🔍 Search description, name, or complaint ID…",
            key="ac_q", label_visibility="collapsed"
        )

    # ── APPLY FILTERS ─────────────────────────────────────────────────────────
    filtered = comps
    if sf  != "all": filtered = [c for c in filtered if c.get("status") == sf]
    if fpr != "all": filtered = [c for c in filtered if c.get("priority") == fpr]
    if fdp != "all": filtered = [c for c in filtered if c.get("department", "") == fdp]
    if fsq:
        q = fsq.lower()
        filtered = [c for c in filtered if
                    q in c.get("description", "").lower() or
                    q in c.get("user_name", "").lower() or
                    q in c.get("complaint_id", "").lower()]

    # ── RESULTS SUMMARY ───────────────────────────────────────────────────────
    BADGE_MAP = {
        "all":         ("#EEF2FF", "#4338CA"),
        "pending":     ("#FFFBEB", "#B45309"),
        "in_progress": ("#EFF6FF", "#1D4ED8"),
        "resolved":    ("#F0FDF4", "#15803D"),
        "rejected":    ("#FFF1F2", "#BE123C"),
        "closed":      ("#F8FAFC", "#475569"),
    }
    bg_c, tx_c = BADGE_MAP.get(sf, BADGE_MAP["all"])

    cat_counts = {}
    for idx, c in enumerate(filtered, start=1):
        cat = c.get("category", "other").title()
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    top_cats = sorted(cat_counts.items(), key=lambda x: -x[1])[:4]

    cat_pills_html = ""
    for k, v in top_cats:
        cat_pills_html += (
            '<span style="background:#F1F5F9;color:#475569;border-radius:20px;'
            'padding:4px 12px;font-size:.68rem;font-weight:700;display:inline-block;'
            'border:1px solid #E2E8F4;">' + str(k) + ' <b>' + str(v) + '</b></span>'
        )

    hidden_count = total - len(filtered)
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'flex-wrap:wrap;gap:8px;margin:14px 0 10px;">'
        '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
        '<span style="background:' + bg_c + ';color:' + tx_c + ';border-radius:20px;'
        'padding:5px 16px;font-size:.80rem;font-weight:800;'
        'border:1.5px solid ' + tx_c + '44;display:inline-block;">'
        + str(len(filtered)) + ' results</span>'
        + cat_pills_html +
        '</div>'
        '<span style="font-size:.72rem;color:#94A3B8;font-weight:600;">'
        + str(hidden_count) + ' hidden by filters</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # ── EMPTY STATE ───────────────────────────────────────────────────────────
    if not filtered:
        st.markdown("""
        <div class="prem-empty-state" style="margin-top:20px;">
            <span class="prem-empty-icon">🔍</span>
            <div class="prem-empty-title">No complaints match your filters</div>
            <div class="prem-empty-sub">
                Try clearing the search or selecting a different status tab.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── LOOKUP TABLES ─────────────────────────────────────────────────────────
    STATUS_CFG = {
        "pending":     ("#FFFBEB", "#B45309", "#FDE68A", "⏳"),
        "in_progress": ("#EFF6FF", "#1D4ED8", "#BFDBFE", "🔄"),
        "resolved":    ("#F0FDF4", "#15803D", "#BBF7D0", "✅"),
        "closed":      ("#F8FAFC", "#475569", "#E2E8F4", "🔒"),
        "rejected":    ("#FFF1F2", "#BE123C", "#FECDD3", "❌"),
    }
    PRI_CFG = {
        "high":   ("prem-badge prem-badge-high",   "🔴 High"),
        "medium": ("prem-badge prem-badge-medium",  "🟡 Medium"),
        "low":    ("prem-badge prem-badge-low",     "🟢 Low"),
    }
    CAT_ICON = {
        "water": "💧", "electricity": "⚡", "road": "🛣️",
        "waste": "🗑️", "drainage": "🌊", "health": "🏥", "other": "📋",
    }
    CAT_COLOR = {
        "water":       ("rgba(14,165,233,.10)",  "rgba(14,165,233,.18)"),
        "electricity": ("rgba(234,179,8,.10)",   "rgba(234,179,8,.18)"),
        "road":        ("rgba(107,114,128,.10)", "rgba(107,114,128,.2)"),
        "waste":       ("rgba(34,197,94,.10)",   "rgba(34,197,94,.18)"),
        "drainage":    ("rgba(6,182,212,.10)",   "rgba(6,182,212,.18)"),
        "health":      ("rgba(239,68,68,.10)",   "rgba(239,68,68,.18)"),
        "other":       ("rgba(99,102,241,.10)",  "rgba(99,102,241,.18)"),
    }

    # ── COMPLAINT CARDS ───────────────────────────────────────────────────────
    for idx, c in enumerate(filtered, start=1):
        cid      = str(c.get("complaint_id", "—"))
        status   = c.get("status", "pending")
        priority = c.get("priority", "medium")
        category = c.get("category", "other")
        desc     = c.get("description", "")
        location = c.get("location", "")
        user     = c.get("user_name", "Citizen")
        dept     = c.get("department", "")
        created  = c.get("created_at", "")
        is_emg   = bool(c.get("is_emergency", False))

        sb, st_tx, sbd, st_ico = STATUS_CFG.get(status, STATUS_CFG["pending"])
        pri_cls, pri_lbl       = PRI_CFG.get(priority, PRI_CFG["medium"])
        cat_ico                = CAT_ICON.get(category, "📋")
        cat_bg, cat_bd         = CAT_COLOR.get(category, CAT_COLOR["other"])
        border_col             = "#EF4444" if is_emg else st_tx
        emg_strip              = "background:linear-gradient(135deg,rgba(239,68,68,.05),rgba(220,38,38,.02));" if is_emg else ""
        desc_short             = (desc[:120] + "…") if len(desc) > 120 else desc
        loc_short              = (location[:40] + "…") if len(location) > 40 else location
        date_str               = created[:16] if created else ""

        # Build all chips as plain strings (no f-string quote conflicts)
        emg_badge    = '<span class="prem-badge prem-badge-emergency" style="font-size:.66rem;">🚨 Emergency</span> ' if is_emg else ""
        status_chip  = (
            '<span style="background:' + sb + ';color:' + st_tx + ';border:1.5px solid ' + sbd + ';'
            'border-radius:20px;padding:3px 12px;font-size:.70rem;font-weight:700;">'
            + st_ico + ' ' + status.replace('_', ' ').title() + '</span>'
        )
        date_chip    = ('<span style="font-size:.68rem;color:#94A3B8;font-weight:600;margin-left:auto;">🕐 ' + date_str + '</span>') if date_str else ""
        dept_chip    = ('<span style="font-size:.72rem;color:#64748B;background:#F1F5F9;border-radius:8px;padding:2px 8px;">🏢 ' + dept + '</span>') if dept else ""
        loc_chip     = ('<span style="font-size:.72rem;color:#64748B;">📍 ' + loc_short + '</span>') if loc_short else ""

        card = (
            # Outer card
            '<div class="prem-complaint-item" style="'
            'border-left: 4px solid ' + border_col + ';'
            + emg_strip +
            'padding:18px 20px 14px;margin-bottom:10px;'
            'transition:transform .2s,box-shadow .2s;">'

            # Row 1: ID + status + priority + date
            '<div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px;">'
            '<span class="prem-complaint-id">' + str(idx) + '. ' + cid + '</span>'
            + emg_badge + status_chip
            + '<span class="' + pri_cls + '">' + pri_lbl + '</span>'
            + date_chip +
            '</div>'

            # Row 2: icon + category label + description
            '<div style="display:flex;gap:14px;align-items:flex-start;margin-bottom:12px;">'
            '<div style="width:44px;height:44px;border-radius:13px;flex-shrink:0;'
            'background:' + cat_bg + ';border:1.5px solid ' + cat_bd + ';'
            'display:flex;align-items:center;justify-content:center;font-size:1.25rem;">'
            + cat_ico +
            '</div>'
            '<div style="flex:1;min-width:0;">'
            '<div style="font-size:.67rem;font-weight:800;text-transform:uppercase;'
            'letter-spacing:.07em;color:#6366F1;margin-bottom:3px;">'
            + category.title() +
            '</div>'
            '<div style="font-size:.88rem;font-weight:600;color:#0F172A;line-height:1.5;'
            'overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">'
            + desc_short +
            '</div>'
            '</div></div>'

            # Row 3: meta chips
            '<div style="display:flex;align-items:center;flex-wrap:wrap;gap:10px;'
            'padding-top:10px;border-top:1px solid #F1F5F9;">'
            '<span style="font-size:.75rem;color:#334155;font-weight:600;">👤 ' + str(user) + '</span>'
            + dept_chip + loc_chip +
            '</div>'
            '</div>'
        )
        st.markdown(card, unsafe_allow_html=True)

        # ── Manage expander ───────────────────────────────────────────────────
        with st.expander("⚙️ Manage  ·  " + cid, expanded=False):
            mc1, mc2, mc3 = st.columns([2, 2, 1])
            s_opts = ["pending", "in_progress", "resolved", "rejected", "closed"]
            p_opts = ["low", "medium", "high"]
            with mc1:
                new_status = st.selectbox(
                    "Status", s_opts,
                    index=s_opts.index(status) if status in s_opts else 0,
                    key="s_" + cid
                )
            with mc2:
                new_priority = st.selectbox(
                    "Priority", p_opts,
                    index=p_opts.index(priority) if priority in p_opts else 1,
                    key="p_" + cid
                )
            with mc3:
                st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
                if st.button("💾 Save", key="sv_" + cid, use_container_width=True):
                    result = api("put", "/complaints/" + cid + "/update",
                                 json={"status": new_status, "priority": new_priority})
                    if result and result.get("success"):
                        st.success("✅ " + cid + " updated!")
                        st.rerun()
                    else:
                        st.error("❌ Update failed — please try again.")

            note = st.text_area(
                "📝 Admin note (internal only)",
                placeholder="Add a note visible only to admins…",
                key="note_" + cid, height=70
            )
            if note and st.button("📌 Save Note", key="sn_" + cid):
                api("post", "/complaints/" + cid + "/note", json={"note": note})
                st.success("Note saved!")

def pg_admin_leaderboard():
    _apply_layout("admin")  

    st.markdown("""
    <div class="prem-hero">
        <div class="prem-hero-title">🏆 Official Performance Leaderboard</div>
        <div class="prem-hero-sub">Track, compare, and celebrate top‑performing officials across all departments</div>
        <div class="prem-hero-stats">
            <div class="prem-hstat h-amber">
                <div class="prem-hstat-num">🥇</div>
                <div class="prem-hstat-lbl">Top Ranked</div>
            </div>
            <div class="prem-hstat h-blue">
                <div class="prem-hstat-num">⭐</div>
                <div class="prem-hstat-lbl">By Rating</div>
            </div>
            <div class="prem-hstat h-green">
                <div class="prem-hstat-num">📊</div>
                <div class="prem-hstat-lbl">Analytics</div>
            </div>
            <div class="prem-hstat">
                <div class="prem-hstat-num">🏢</div>
                <div class="prem-hstat-lbl">By Dept</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # How ranking works — native Streamlit only inside expander (no HTML!)
    with st.expander("ℹ️ How ranking works", expanded=False):
        st.write("**Eligibility:** Officials must have resolved at least **1 complaint** to appear in the ranked list.")
        st.write("**Primary factor:** Average citizen rating (higher = better).")
        st.write("**Tie‑breaker:** Total resolved complaints.")
        st.write("**Resolution rate** = (resolved ÷ assigned) × 100%, capped at 100%.")
        st.write("**Average rating** = mean of all citizen feedback scores (1–5 ⭐).")

    tab1, tab2, tab3 = st.tabs(["🏆 Overall Rankings", "🏢 Department Rankings", "📊 Performance Analytics"])
    with tab1:
        _render_overall_leaderboard()
    with tab2:
        _render_department_leaderboard()
    with tab3:
        _render_performance_analytics()


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _bar_color(pct: float) -> str:
    if pct < 40:  return "linear-gradient(90deg,#EF4444,#F97316)"
    if pct < 70:  return "linear-gradient(90deg,#F59E0B,#EAB308)"
    return "linear-gradient(90deg,#6366F1,#10B981)"

def _rank_class(rank, eligible: bool) -> str:
    if not eligible:          return "ineligible"
    if rank == 1:             return "rank-1"
    if rank == 2:             return "rank-2"
    if rank == 3:             return "rank-3"
    return ""

def _medal(rank, eligible: bool) -> str:
    if not eligible:          return "📋"
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    if rank in medals:        return medals[rank]
    if isinstance(rank, int) and rank <= 10: return f"#{rank}"
    return "🏅"

def _stat_card(value, label, color="#6366F1", sub=""):
    sub_html = f'<div style="font-size:0.73rem;color:#5A6A85;margin-top:4px;">{html.escape(str(sub))}</div>' if sub else ""
    return f"""
    <div class="prem-stat-card">
        <div class="prem-stat-num" style="color:{color}">{value}</div>
        <div class="prem-stat-lbl">{label}</div>
        {sub_html}
    </div>"""

def _lb_row(o: dict) -> str:
    rank       = o.get("rank")
    eligible   = o.get("eligible", False)
    res_rate   = min(o.get("resolution_rate", 0), 100)
    avg_rating = min(max(o.get("avg_rating", 0), 0), 5)
    stars_str  = _rating_stars_display(avg_rating, o.get("rating_count", 0))
    not_ranked = "" if eligible else "<span class='prem-tag' style='background:#FEF9C3;color:#854D0E;'>Not ranked</span>"
    dept_tag   = f"<span class='prem-lb-dept'>{html.escape(o.get('department','N/A'))}</span>"

    return f"""
    <div class="prem-lb-card {_rank_class(rank, eligible)}">
        <div class="prem-lb-rank">{_medal(rank, eligible)}</div>
        <div class="prem-lb-info">
            <div class="prem-lb-name">
                {html.escape(o.get('name','Unknown'))} {dept_tag} {not_ranked}
            </div>
            <div class="prem-lb-stats">
                <div class="prem-lb-stat-item">
                    <div class="prem-lb-stat-lbl">⭐ Rating</div>
                    <div class="prem-lb-stat-val">{stars_str}</div>
                </div>
                <div class="prem-lb-stat-item">
                    <div class="prem-lb-stat-lbl">✅ Resolved</div>
                    <div class="prem-lb-stat-val">{o.get('total_resolved',0)}</div>
                </div>
                <div class="prem-lb-stat-item">
                    <div class="prem-lb-stat-lbl">📋 Assigned</div>
                    <div class="prem-lb-stat-val">{o.get('total_assigned',0)}</div>
                </div>
                <div class="prem-lb-stat-item">
                    <div class="prem-lb-stat-lbl">📈 Rate</div>
                    <div class="prem-lb-stat-val">{res_rate:.1f}%</div>
                </div>
                <div class="prem-lb-stat-item">
                    <div class="prem-lb-stat-lbl">🗳️ Votes</div>
                    <div class="prem-lb-stat-val">{o.get('rating_count',0)}</div>
                </div>
            </div>
            <div class="prem-prog-wrap" style="height:13px;margin-top:8px;">
                <div class="prem-prog-fill"
                     style="width:{res_rate}%;background:{_bar_color(res_rate)};height:13px;">
                    <span class="prem-prog-text" style="font-size:0.58rem;">{res_rate:.0f}%</span>
                </div>
            </div>
        </div>
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
#  OVERALL LEADERBOARD
# ─────────────────────────────────────────────────────────────────────────────
def _render_overall_leaderboard():
    _apply_layout("admin")  
    board = api("get", "/admin/leaderboard/overall")
    board = board if isinstance(board, list) else []

    if not board:
        st.markdown("""
        <div class="prem-empty-state">
            <span class="prem-empty-icon">📭</span>
            <div class="prem-empty-title">No ranked officials yet</div>
            <div class="prem-empty-sub">Officials need at least 1 resolved complaint to appear here.</div>
        </div>""", unsafe_allow_html=True)
        return

    eligible_list = [o for o in board if o.get("eligible")]
    total_res     = sum(o.get("total_resolved", 0) for o in board)
    rated         = [o for o in board if o.get("rating_count", 0) > 0]
    overall_rating = sum(o.get("avg_rating", 0) for o in rated) / len(rated) if rated else 0

    # ── SUMMARY STATS ─────────────────────────────────────────────────────────
    st.markdown('<div class="prem-section-header">Overview</div>', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:  st.markdown(_stat_card(len(board),          "Total Officials",       "#6366F1"), unsafe_allow_html=True)
    with sc2:  st.markdown(_stat_card(len(eligible_list),  "Ranked (≥1 resolved)",  "#10B981"), unsafe_allow_html=True)
    with sc3:  st.markdown(_stat_card(total_res,            "Total Resolved",        "#F59E0B"), unsafe_allow_html=True)
    with sc4:  st.markdown(_stat_card(f"{overall_rating:.1f}⭐", "Avg Platform Rating", "#0EA5E9"), unsafe_allow_html=True)

    # ── TOP 3 PODIUM ──────────────────────────────────────────────────────────
    top3 = sorted([o for o in eligible_list if o.get("rank") in (1, 2, 3)],
                  key=lambda x: x.get("rank", 99))
    if top3:
        st.markdown('<div class="prem-section-header">Top Performers</div>', unsafe_allow_html=True)
        cols = st.columns(len(top3))
        for i, o in enumerate(top3):
            rank      = o.get("rank")
            medal     = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, "🏅")
            stars_str = _rating_stars_display(min(max(o.get("avg_rating", 0), 0), 5), o.get("rating_count", 0))
            with cols[i]:
                st.markdown(f"""
                <div class="prem-performer-card">
                    <div class="prem-rank-badge">{rank}</div>
                    <div class="prem-performer-name">{medal} {html.escape(o.get('name',''))}</div>
                    <div class="prem-performer-dept">{html.escape(o.get('department',''))}</div>
                    <div class="prem-performer-stars">{stars_str}</div>
                    <div class="prem-performer-stats">
                        ✅ {o.get('total_resolved',0)} resolved &nbsp;·&nbsp;
                        📈 {min(o.get('resolution_rate',0),100):.1f}%
                    </div>
                </div>""", unsafe_allow_html=True)

    # ── FILTERS ───────────────────────────────────────────────────────────────
    st.markdown('<div class="prem-section-header">All Officials</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        show_filter = st.selectbox("Show",
            ["All Officials", "Eligible Only (Ranked)", "Not Yet Eligible"], key="lb_show")
    with f2:
        search  = st.text_input("🔍 Search", placeholder="Name…", key="lb_search")
    with f3:
        sort_by = st.selectbox("Sort By",
            ["Rank", "Rating", "Resolution Rate", "Resolved Count"], key="lb_sort")

    filtered = board[:]
    if show_filter == "Eligible Only (Ranked)":
        filtered = [o for o in filtered if o.get("eligible")]
    elif show_filter == "Not Yet Eligible":
        filtered = [o for o in filtered if not o.get("eligible")]
    if search:
        filtered = [o for o in filtered if search.lower() in o.get("name", "").lower()]

    sort_keys = {
        "Rating":          lambda x: -x.get("avg_rating", 0),
        "Resolution Rate": lambda x: -x.get("resolution_rate", 0),
        "Resolved Count":  lambda x: -x.get("total_resolved", 0),
        "Rank":            lambda x: (not x.get("eligible"),
                                      -x.get("avg_rating", 0),
                                      -x.get("total_resolved", 0)),
    }
    filtered.sort(key=sort_keys.get(sort_by, sort_keys["Rank"]))

    st.markdown(
        f'<div style="font-size:0.80rem;color:#5A6A85;margin-bottom:10px;">'
        f'Showing <strong>{len(filtered)}</strong> of {len(board)} officials</div>',
        unsafe_allow_html=True)

    for o in filtered[:50]:
        st.markdown(_lb_row(o), unsafe_allow_html=True)

    # ── EXPORT ────────────────────────────────────────────────────────────────
    st.markdown('<div class="prem-section-header">Export</div>', unsafe_allow_html=True)
    if st.button("📥 Export Leaderboard as CSV", use_container_width=True, key="lb_export"):
        import pandas as pd
        df = pd.DataFrame([{
            "Rank":              o.get("rank", "—") if o.get("eligible") else "Not eligible",
            "Name":              o.get("name"),
            "Department":        o.get("department"),
            "Avg Rating":        min(max(o.get("avg_rating", 0), 0), 5),
            "Total Resolved":    o.get("total_resolved", 0),
            "Total Assigned":    o.get("total_assigned", 0),
            "Resolution Rate %": min(o.get("resolution_rate", 0), 100),
            "Rating Count":      o.get("rating_count", 0),
        } for o in board])
        st.download_button("⬇️ Download leaderboard.csv",
            df.to_csv(index=False), "leaderboard.csv", "text/csv",
            use_container_width=True, key="lb_dl")


# ─────────────────────────────────────────────────────────────────────────────
#  DEPARTMENT LEADERBOARD
# ─────────────────────────────────────────────────────────────────────────────
def _render_department_leaderboard():
    _apply_layout("admin")  
    depts = api("get", "/admin/departments")
    depts = depts if isinstance(depts, list) else []
    if not depts:
        st.info("No departments found.")
        return

    selected_dept = st.selectbox(
        "Select Department",
        options=[d["id"] for d in depts],
        format_func=lambda x: next((d["name"] for d in depts if d["id"] == x), str(x)),
        key="dept_rank_select"
    )
    if not selected_dept:
        return

    dept_name = next((d["name"] for d in depts if d["id"] == selected_dept), "Department")
    board     = api("get", f"/admin/leaderboard/department/{selected_dept}")
    board     = board if isinstance(board, list) else []

    if not board:
        st.markdown(f"""
        <div class="prem-empty-state">
            <span class="prem-empty-icon">🏢</span>
            <div class="prem-empty-title">No ranked officials in {html.escape(dept_name)}</div>
            <div class="prem-empty-sub">At least 1 resolved complaint needed to appear in rankings.</div>
        </div>""", unsafe_allow_html=True)
        return

    eligible_count  = len([o for o in board if o.get("eligible")])
    total_resolved  = sum(o.get("total_resolved", 0) for o in board)
    total_assigned  = sum(o.get("total_assigned", 0) for o in board)
    rated           = [o for o in board if o.get("rating_count", 0) > 0]
    avg_dept_rating = (
        min(max(sum(o.get("avg_rating", 0) for o in rated) / len(rated), 0), 5)
        if rated else 0
    )
    dept_res_rate = min(total_resolved / max(total_assigned, 1) * 100, 100)

    st.markdown(
        f'<div class="prem-section-header">{html.escape(dept_name)} — Summary</div>',
        unsafe_allow_html=True)

    dc1, dc2, dc3, dc4 = st.columns(4)
    with dc1: st.markdown(_stat_card(len(board),           "Officials",        "#6366F1"), unsafe_allow_html=True)
    with dc2: st.markdown(_stat_card(eligible_count,        "Ranked",           "#10B981"), unsafe_allow_html=True)
    with dc3: st.markdown(_stat_card(total_resolved,        "Total Resolved",   "#F59E0B"), unsafe_allow_html=True)
    with dc4: st.markdown(_stat_card(f"{avg_dept_rating:.1f}⭐", "Dept Avg Rating", "#0EA5E9"), unsafe_allow_html=True)

    st.markdown(f"""
    <div class="prem-card" style="padding:16px 20px;margin:8px 0 16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-weight:700;font-size:0.84rem;">🏢 Department Resolution Rate</span>
            <span class="prem-chip">{dept_res_rate:.1f}%</span>
        </div>
        <div class="prem-prog-wrap">
            <div class="prem-prog-fill"
                 style="width:{dept_res_rate}%;background:{_bar_color(dept_res_rate)};">
                <span class="prem-prog-text">{dept_res_rate:.0f}%</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="prem-section-header">Officials in this Department</div>',
                unsafe_allow_html=True)
    for o in board:
        st.markdown(_lb_row(o), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PERFORMANCE ANALYTICS  — single, definitive version
# ─────────────────────────────────────────────────────────────────────────────
def _render_performance_analytics():
    _apply_layout("admin")  
    import pandas as pd

    board = api("get", "/admin/leaderboard/overall")
    board = board if isinstance(board, list) else []
    if not board:
        st.info("No data available yet.")
        return

    df = pd.DataFrame([{
        "Name":            o.get("name", "Unknown"),
        "Department":      o.get("department", "N/A"),
        "Avg Rating":      round(min(max(o.get("avg_rating", 0), 0), 5), 2),
        "Resolved":        o.get("total_resolved", 0),
        "Assigned":        o.get("total_assigned", 0),
        "Resolution Rate": round(min(o.get("resolution_rate", 0), 100), 1),
        "Rating Count":    o.get("rating_count", 0),
        "Eligible":        o.get("eligible", False),
    } for o in board])

    eligible_df = df[df["Eligible"]]

    # ── HIGHLIGHT STAT CARDS ──────────────────────────────────────────────────
    st.markdown('<div class="prem-section-header">Platform Highlights</div>', unsafe_allow_html=True)

    best      = eligible_df.loc[eligible_df["Avg Rating"].idxmax()]      if not eligible_df.empty else None
    top_res   = eligible_df.loc[eligible_df["Resolved"].idxmax()]        if not eligible_df.empty else None
    top_rate  = eligible_df.loc[eligible_df["Resolution Rate"].idxmax()] if not eligible_df.empty else None
    dept_sums = df.groupby("Department")["Resolved"].sum()
    top_dept  = dept_sums.idxmax() if not dept_sums.empty else "—"

    h1, h2, h3, h4 = st.columns(4)
    with h1:
        st.markdown(_stat_card(
            f"⭐ {best['Avg Rating']}" if best is not None else "—",
            "Highest Rating", "#F59E0B",
            best["Name"] if best is not None else ""), unsafe_allow_html=True)
    with h2:
        st.markdown(_stat_card(
            f"✅ {int(top_res['Resolved'])}" if top_res is not None else "—",
            "Most Resolved", "#10B981",
            top_res["Name"] if top_res is not None else ""), unsafe_allow_html=True)
    with h3:
        st.markdown(_stat_card(
            f"📈 {top_rate['Resolution Rate']}%" if top_rate is not None else "—",
            "Best Resolution Rate", "#6366F1",
            top_rate["Name"] if top_rate is not None else ""), unsafe_allow_html=True)
    with h4:
        st.markdown(_stat_card("🏢", "Top Department", "#0EA5E9", top_dept),
                    unsafe_allow_html=True)

    # ── TOP 10 PERFORMERS ────────────���────────────────────────────────────────
    st.markdown('<div class="prem-section-header">Top 10 by Rating</div>', unsafe_allow_html=True)
    top10 = eligible_df[eligible_df["Rating Count"] > 0].nlargest(10, "Avg Rating")
    if not top10.empty:
        st.markdown('<div class="prem-performer-grid">', unsafe_allow_html=True)
        for i, (_, row) in enumerate(top10.iterrows()):
            stars_str = _rating_stars_display(row["Avg Rating"], row["Rating Count"])
            st.markdown(f"""
            <div class="prem-performer-card">
                <div class="prem-rank-badge">#{i+1}</div>
                <div class="prem-performer-name">{html.escape(str(row['Name'])[:22])}</div>
                <div class="prem-performer-dept">{html.escape(str(row['Department']))}</div>
                <div class="prem-performer-stars">{stars_str}</div>
                <div class="prem-performer-stats">
                    ✅ {int(row['Resolved'])} resolved &nbsp;·&nbsp;
                    📈 {row['Resolution Rate']}%
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No rated officials yet.")

    # ── DEPARTMENT SUMMARY CARDS ──────────────────────────────────────────────
    st.markdown('<div class="prem-section-header">Department Summary</div>', unsafe_allow_html=True)

    dept_perf = (
        df.groupby("Department")
        .agg(Officials=("Name","count"),
             Resolved=("Resolved","sum"),
             Assigned=("Assigned","sum"),
             Avg_Rating=("Avg Rating","mean"),
             Rating_Count=("Rating Count","sum"))
        .reset_index()
    )
    dept_perf["Res Rate"] = (
        dept_perf["Resolved"] / dept_perf["Assigned"].replace(0, 1) * 100
    ).clip(upper=100).round(1)

    for _, row in dept_perf.sort_values("Res Rate", ascending=False).iterrows():
        rate = row["Res Rate"]
        st.markdown(f"""
        <div class="prem-lb-card">
            <div class="prem-lb-rank" style="font-size:1.6rem;">🏢</div>
            <div class="prem-lb-info">
                <div class="prem-lb-name">
                    {html.escape(str(row['Department']))}
                    <span class="prem-lb-dept">{int(row['Officials'])} officials</span>
                </div>
                <div class="prem-lb-stats">
                    <div class="prem-lb-stat-item">
                        <div class="prem-lb-stat-lbl">⭐ Avg Rating</div>
                        <div class="prem-lb-stat-val">{row['Avg_Rating']:.1f}</div>
                    </div>
                    <div class="prem-lb-stat-item">
                        <div class="prem-lb-stat-lbl">✅ Resolved</div>
                        <div class="prem-lb-stat-val">{int(row['Resolved'])}</div>
                    </div>
                    <div class="prem-lb-stat-item">
                        <div class="prem-lb-stat-lbl">📋 Assigned</div>
                        <div class="prem-lb-stat-val">{int(row['Assigned'])}</div>
                    </div>
                    <div class="prem-lb-stat-item">
                        <div class="prem-lb-stat-lbl">🗳️ Ratings</div>
                        <div class="prem-lb-stat-val">{int(row['Rating_Count'])}</div>
                    </div>
                    <div class="prem-lb-stat-item">
                        <div class="prem-lb-stat-lbl">📈 Rate</div>
                        <div class="prem-lb-stat-val">{rate}%</div>
                    </div>
                </div>
                <div class="prem-prog-wrap" style="height:13px;margin-top:8px;">
                    <div class="prem-prog-fill"
                         style="width:{rate}%;background:{_bar_color(rate)};height:13px;">
                        <span class="prem-prog-text" style="font-size:0.58rem;">{rate:.0f}%</span>
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── DISTRIBUTION CHARTS ───────────────────────────────────────────────────
    st.markdown('<div class="prem-section-header">Distributions</div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns(2)

    with ch1:
        st.caption("⭐ Top 10 Officials by Rating")
        rating_chart = eligible_df[eligible_df["Rating Count"] > 0].nlargest(10, "Avg Rating")
        if not rating_chart.empty:
            st.bar_chart(rating_chart.set_index("Name")["Avg Rating"],
                         use_container_width=True, height=240, color="#6366F1")
        else:
            st.info("No rated officials yet.")

    with ch2:
        st.caption("✅ Complaints Resolved by Department")
        dept_chart = dept_perf.set_index("Department")["Resolved"]
        if not dept_chart.empty:
            st.bar_chart(dept_chart, use_container_width=True, height=240, color="#10B981")
        else:
            st.info("No resolved complaints yet.")

    # ── RATING DISTRIBUTION (star breakdown) ──────────────────────────────────
    st.markdown('<div class="prem-section-header">⭐ Star Rating Breakdown</div>', unsafe_allow_html=True)
    rating_counts = df["Avg Rating"].round().value_counts().sort_index(ascending=False)
    total_officials = len(df)
    for star in [5, 4, 3, 2, 1]:
        count = int(rating_counts.get(star, 0))
        pct   = round(count / max(total_officials, 1) * 100, 1)
        width = round(count / max(rating_counts.max() if not rating_counts.empty else 1, 1) * 100, 1)
        st.markdown(f"""
        <div style="margin:6px 0;">
            <div style="display:flex;justify-content:space-between;
                        font-size:0.78rem;font-weight:600;margin-bottom:4px;">
                <span>{'⭐' * star} {star} star{"s" if star > 1 else ""}</span>
                <span style="color:#5A6A85;">{count} official{"s" if count != 1 else ""} ({pct}%)</span>
            </div>
            <div class="prem-prog-wrap" style="height:12px;">
                <div class="prem-prog-fill"
                     style="width:{width}%;background:linear-gradient(90deg,#F59E0B,#EAB308);height:12px;">
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── RESOLUTION RATE DISTRIBUTION ─────────────────────────────────────────
    st.markdown('<div class="prem-section-header">📈 Resolution Rate Breakdown</div>', unsafe_allow_html=True)
    bins   = [(85,101,"#10B981"), (70,85,"#6366F1"), (50,70,"#F59E0B"), (30,50,"#F97316"), (0,30,"#EF4444")]
    labels = ["85–100%", "70–85%", "50–70%", "30–50%", "0–30%"]
    max_bin = max(
        len(df[(df["Resolution Rate"] >= lo) & (df["Resolution Rate"] < hi)])
        for lo, hi, _ in bins
    ) or 1
    for (lo, hi, color), label in zip(bins, labels):
        cnt   = len(df[(df["Resolution Rate"] >= lo) & (df["Resolution Rate"] < hi)])
        pct   = round(cnt / max(total_officials, 1) * 100, 1)
        width = round(cnt / max_bin * 100, 1)
        st.markdown(f"""
        <div style="margin:6px 0;">
            <div style="display:flex;justify-content:space-between;
                        font-size:0.78rem;font-weight:600;margin-bottom:4px;">
                <span>{label}</span>
                <span style="color:#5A6A85;">{cnt} official{"s" if cnt != 1 else ""} ({pct}%)</span>
            </div>
            <div class="prem-prog-wrap" style="height:12px;">
                <div class="prem-prog-fill"
                     style="width:{width}%;background:{color};height:12px;">
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── FULL TABLE + EXPORT ───────────────────────────────────────────────────
    st.markdown('<div class="prem-section-header">Full Data Table</div>', unsafe_allow_html=True)
    # Native Streamlit only inside expander
    with st.expander("📋 View & Export Full Table", expanded=False):
        display_df = df.sort_values("Avg Rating", ascending=False).reset_index(drop=True)
        display_df.index += 1
        st.dataframe(display_df, use_container_width=True)
        st.download_button(
            "⬇️ Download performance_analytics.csv",
            display_df.to_csv(index=True),
            "performance_analytics.csv", "text/csv",
            use_container_width=True, key="analytics_dl")

    st.markdown("""
    <div class="prem-tip-bar">
        <span class="prem-tip-icon">💡</span>
        <span class="prem-tip-text">
            <strong>Tip:</strong> Ratings are collected from citizen feedback after resolution.
            Officials with higher ratings and faster resolution times rank higher on the leaderboard.
        </span>
    </div>""", unsafe_allow_html=True)

def _rating_stars_display(rating: float, count: int = 0) -> str:
    _apply_layout("admin")  
    rating = float(rating or 0)
    full = int(rating)
    half = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    stars = "★" * full + ("½" if half else "") + "☆" * empty
    if count > 0:
        return f'{stars} {rating:.1f} ({count} vote{"s" if count != 1 else ""})'
    else:
        return f'{stars} (no ratings)'


def pg_admin_schemes():
    _apply_layout("admin")  
    lang  = st.session_state.language
    admin = st.session_state.admin or {}
    dark  = st.session_state.get("dark_mode", False)
    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)

    _CARD = "#10161F" if dark else "#FFFFFF"
    _BG2  = "#080C14" if dark else "#F4F6FB"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
    _A1   = "#6366F1"
    _A2   = "#8B5CF6"

    st.markdown(f"""
<style>
/* ── hero ── */
.sch-adm-hero{{
    background:linear-gradient(135deg,#1e1b4b 0%,#3730A3 50%,#1e3a5f 100%);
    border-radius:22px;padding:1.75rem 2rem;margin-bottom:1.75rem;
    position:relative;overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,0.25);
}}
.sch-adm-hero::before{{content:'';position:absolute;top:-60px;right:-60px;
    width:220px;height:220px;border-radius:50%;
    background:radial-gradient(circle,rgba(255,255,255,0.07) 0%,transparent 70%);
    pointer-events:none;}}
.sch-adm-hero-title{{font-family:'Sora',sans-serif;font-size:1.75rem;font-weight:800;
    color:#fff;margin-bottom:5px;position:relative;z-index:1;}}
.sch-adm-hero-sub{{font-size:0.86rem;color:rgba(255,255,255,0.65);
    position:relative;z-index:1;font-weight:500;}}

/* ── section header ── */
.sch-adm-sec{{font-size:0.70rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.10em;color:{_SUB};margin:20px 0 12px;
    display:flex;align-items:center;gap:10px;}}
.sch-adm-sec::before{{content:'';width:4px;height:16px;
    background:linear-gradient(180deg,{_A1},{_A2});border-radius:3px;flex-shrink:0;}}
.sch-adm-sec::after{{content:'';flex:1;height:1px;
    background:linear-gradient(to right,{_BOR},transparent);}}

/* ── form card ── */
.sch-adm-form-card{{
    background:{_CARD};border:1px solid {_BOR};border-radius:18px;
    padding:20px 22px;margin-bottom:16px;
    box-shadow:0 2px 8px rgba(15,23,42,0.06);
}}

/* ── voice preview ── */
.sch-voice-prev{{
    background:{"#1C1408" if dark else "#FFFBEB"};
    border:1.5px solid {"#78350F" if dark else "#FDE68A"};
    border-left:4px solid #F59E0B;
    border-radius:14px;padding:14px 16px;margin:12px 0;
}}
.sch-voice-text{{font-size:0.80rem;color:{"#FCD34D" if dark else "#B45309"};
    line-height:1.6;margin-bottom:4px;}}
.sch-voice-hint{{font-size:0.68rem;color:{_SUB};}}

/* ── scheme row card ── */
.sch-row-card{{
    background:{_CARD};border:1px solid {_BOR};
    border-left:4px solid {_A1};border-radius:16px;
    padding:16px 18px;margin-bottom:10px;
    box-shadow:0 2px 8px rgba(15,23,42,0.05);
    transition:transform 0.18s,box-shadow 0.18s;
}}
.sch-row-card:hover{{transform:translateX(3px);
    box-shadow:0 8px 24px rgba(99,102,241,0.12);}}
.sch-row-title{{font-size:0.93rem;font-weight:800;color:{_TXT};margin-bottom:5px;}}
.sch-row-desc{{font-size:0.78rem;color:{_SUB};line-height:1.6;margin-bottom:8px;}}
.sch-row-meta{{display:flex;gap:8px;flex-wrap:wrap;align-items:center;}}
.sch-row-tag{{
    background:{"rgba(16,185,129,0.15)" if dark else "#ECFDF5"};
    color:{"#4ADE80" if dark else "#059669"};
    border-radius:20px;padding:2px 10px;font-size:0.68rem;font-weight:700;
}}
.sch-row-sub{{font-size:0.68rem;color:{_SUB};}}

/* ── count pill ── */
.sch-count{{font-size:0.75rem;color:{_SUB};font-weight:600;
    text-align:right;margin:0 0 10px;}}

/* ── empty ── */
.sch-adm-empty{{text-align:center;padding:3rem 2rem;
    background:{_CARD};border-radius:22px;border:1.5px dashed {_BOR};}}
.sch-adm-empty-icon{{font-size:3rem;opacity:.5;display:block;margin-bottom:12px;}}
.sch-adm-empty-title{{font-size:.95rem;font-weight:700;color:{_TXT};margin-bottom:6px;}}
.sch-adm-empty-sub{{font-size:.78rem;color:{_SUB};}}

/* ── play button green ── */
div[data-testid="stButton"].sch-play > button{{
    background:linear-gradient(135deg,#15803D,#22C55E) !important;
    color:#fff !important;border:none !important;
    box-shadow:0 4px 10px rgba(34,197,94,0.28) !important;
    font-size:0.78rem !important;
}}
div[data-testid="stButton"].sch-play > button:hover{{
    transform:translateY(-2px) !important;filter:brightness(1.05) !important;
}}
/* ── delete button red ── */
div[data-testid="stButton"].sch-del > button{{
    background:{"#1C0808" if dark else "#FFF1F2"} !important;
    color:{"#F87171" if dark else "#BE123C"} !important;
    border:1.5px solid {"#7F1D1D" if dark else "#FECDD3"} !important;
    box-shadow:none !important;font-size:0.78rem !important;
}}
div[data-testid="stButton"].sch-del > button:hover{{
    background:{"#2C1010" if dark else "#FFE4E6"} !important;
    transform:translateY(-1px) !important;filter:none !important;
}}

@media(max-width:600px){{
    .sch-adm-hero{{padding:1.4rem 1rem;border-radius:18px;}}
    .sch-adm-hero-title{{font-size:1.4rem;}}
    .sch-row-meta{{flex-direction:column;gap:5px;}}
}}
</style>
""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # HERO
    # ════════════════════════════════════════════════════════
    st.markdown(
        "<div class='sch-adm-hero'>"
        "<div class='sch-adm-hero-title'>📜 Scheme Management</div>"
        "<div class='sch-adm-hero-sub'>"
        "Create · manage · notify citizens automatically"
        "</div></div>",
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs([
        "➕ Create New Scheme",
        "📋 Manage Existing Schemes",
    ])

    # ════════════════════════════════════════════════════════
    # TAB 1 — CREATE
    # ════════════════════════════════════════════════════════
    with tab1:
        st.markdown("<div class='sch-adm-sec'>📝 Scheme Details</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='background:{"rgba(99,102,241,0.08)" if dark else "#EEF2FF"};"
            f"border:1px solid {"rgba(99,102,241,0.20)" if dark else "#C7D2FE"};"
            f"border-radius:12px;padding:12px 16px;font-size:0.80rem;"
            f"color:{"#818CF8" if dark else "#4338CA"};margin-bottom:16px;'>"
            f"💡 All users will be notified immediately when you publish a scheme."
            f"</div>",
            unsafe_allow_html=True,
        )

        with st.form(key="create_scheme_admin", clear_on_submit=True):
            st.markdown("<div class='sch-adm-form-card'>", unsafe_allow_html=True)

            fc1, fc2 = st.columns(2)
            with fc1:
                title_en = st.text_input(
                    "Title (English) *",
                    placeholder="e.g., PM Kisan Samman Nidhi",
                )
                desc_en = st.text_area(
                    "Description (English) *",
                    height=130,
                    placeholder="Detailed description — benefits, eligibility, application process…",
                )
                # Fetch categories dynamically
                cat_resp = api("get", "/categories")

                categories = cat_resp.get(
                    "categories",
                    []
                )

                # Fallback if API fails
                if not categories:

                    categories = [
                        "housing",
                        "water",
                        "energy",
                        "health",
                        "education",
                        "agriculture",
                        "financial",
                        "general",
                    ]

                # Remove duplicates + sort
                categories = sorted(
                    list(set(categories))
                )

                existing_categories = api(
                    "get",
                    "/categories"
                ).get("categories", [])

                col1, col2 = st.columns(2)

                with col1:

                    selected_category = st.selectbox(

                        "Existing Category",

                        [""] + existing_categories
                    )

                with col2:

                    custom_category = st.text_input(

                        "New Category",

                        placeholder="cybercrime"
                    )

                category = (

                    custom_category.strip().lower()

                    if custom_category.strip()

                    else selected_category
                )

            with fc2:
                title_hi = st.text_input(
                    "शीर्षक (हिंदी)",
                    placeholder="जैसे पीएम किसान सम्मान निधि",
                )
                desc_hi = st.text_area(
                    "विवरण (हिंदी)",
                    height=130,
                    placeholder="योजना के लाभ, पात्रता और आवेदन प्रक्रिया…",
                )

                st.markdown(
                    f"<div style='font-size:0.72rem;font-weight:700;text-transform:uppercase;"
                    f"letter-spacing:0.08em;color:{_SUB};margin-bottom:8px;'>🖼 Scheme Image</div>",
                    unsafe_allow_html=True,
                )
                image_source = st.radio(
                    "Image Source",
                    ["📷 Upload Image", "🔗 Image URL"],
                    horizontal=True,
                    label_visibility="collapsed",
                )
                uploaded_image = None
                image_url      = ""
                if image_source == "📷 Upload Image":
                    uploaded_image = st.file_uploader(
                        "Upload (JPG / PNG / WEBP)",
                        type=["jpg","jpeg","png","webp","gif"],
                        label_visibility="collapsed",
                    )
                    if uploaded_image:
                        st.image(uploaded_image, width=160, caption="Preview")
                else:
                    image_url = st.text_input(
                        "Image URL",
                        placeholder="https://example.com/image.jpg",
                        label_visibility="collapsed",
                    )
                    if image_url:
                        try:
                            st.image(image_url, width=160, caption="Preview")
                        except Exception:
                            st.warning("⚠️ Could not load image from that URL.")

            st.markdown("</div>", unsafe_allow_html=True)

            # ── voice preview ─────────────────────────────
            safe_title = (title_en or "").replace('"',"'")
            safe_desc  = (desc_en  or "")[:150].replace('"',"'")
            voice_text = f"Attention citizens. A new government scheme has been launched. {safe_title}. {safe_desc}…"
            st.markdown("<div class='sch-adm-sec'>📢 Voice Announcement Preview</div>",
                        unsafe_allow_html=True)
            st.markdown(
                f"<div class='sch-voice-prev'>"
                f"<div class='sch-voice-text'>🔊 {voice_text}</div>"
                f"<div class='sch-voice-hint'>"
                f"This announcement plays when users open the scheme details.</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # ── submit ────────────────────────────────────
            sc1, sc2, sc3 = st.columns([1,2,1])
            with sc2:
                submitted = st.form_submit_button(
                    "🚀 Publish Scheme & Notify All Users",
                    use_container_width=True,
                )

            if submitted:
                if not title_en.strip() or not desc_en.strip():
                    st.error("❌ Title and Description (English) are required.")
                else:
                    with st.spinner("Publishing scheme and notifying users…"):
                        try:
                            if uploaded_image:
                                files  = {"image": (
                                    uploaded_image.name,
                                    uploaded_image.getvalue(),
                                    uploaded_image.type,
                                )}
                                data = {
                                    "title":            title_en.strip(),
                                    "title_hi":         title_hi.strip(),
                                    "description":      desc_en.strip(),
                                    "description_hi":   desc_hi.strip(),
                                    "category":         category,
                                    "uploaded_by":      str(admin.get("admin_id","")),
                                    "uploaded_by_type": "admin",
                                }
                                resp   = _req.post(
                                    f"{API_BASE}/schemes/create-with-image",
                                    data=data, files=files, timeout=30,
                                )
                                result = resp.json()
                            else:
                                result = api("post", "/schemes/create", json={
                                    "title":            title_en.strip(),
                                    "title_hi":         title_hi.strip(),
                                    "description":      desc_en.strip(),
                                    "description_hi":   desc_hi.strip(),
                                    "image_url":        image_url.strip(),
                                    "category":         category,
                                    "uploaded_by":      str(admin.get("admin_id","")),
                                    "uploaded_by_type": "admin",
                                })

                            if result.get("success"):
                                st.success(f"✅ {result.get('message','Scheme published successfully!')}")
                                st.balloons()
                                # play announcement
                                vm = result.get("voice_announcement", voice_text)
                                safe_vm = vm[:200].replace('"',"'").replace("\n"," ")
                                st.components.v1.html(
                                    f'<script>'
                                    f'var u=new SpeechSynthesisUtterance("{safe_vm}");'
                                    f'u.lang="en-IN";u.rate=0.9;'
                                    f'window.speechSynthesis.speak(u);'
                                    f'</script>',
                                    height=0,
                                )
                                st.rerun()
                            else:
                                st.error(f"Error: {result.get('detail', result.get('error','Unknown error'))}")
                        except Exception as exc:
                            st.error(f"Request failed: {exc}")

    # ════════════════════════════════════════════════════════
    # TAB 2 — MANAGE
    # ════════════════════════════════════════════════════════
    with tab2:
        schemes = api("get", "/schemes/all")
        schemes = schemes if isinstance(schemes, list) else []

        if not schemes:
            st.markdown(
                "<div class='sch-adm-empty'>"
                "<span class='sch-adm-empty-icon'>📜</span>"
                "<div class='sch-adm-empty-title'>No schemes yet</div>"
                "<div class='sch-adm-empty-sub'>"
                "Create your first scheme using the tab above.</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            return

        # search
        srch = st.text_input(
            "search_schemes_adm",
            label_visibility="collapsed",
            placeholder="🔍 Search by title, category…",
            key="adm_sch_search",
        )
        filtered = schemes
        if srch.strip():
            term = srch.strip().lower()
            filtered = [
                s for s in schemes
                if term in s.get("title","").lower()
                or term in s.get("category","").lower()
                or term in s.get("description","").lower()
            ]

        st.markdown(
            f"<div class='sch-count'>"
            f"Showing <strong>{len(filtered)}</strong> of "
            f"<strong>{len(schemes)}</strong> schemes"
            f"</div>",
            unsafe_allow_html=True,
        )

        CATEGORY_ICONS = {

            "health":      "🏥",

            "education":   "🎓",

            "agriculture": "🌾",

            "housing":     "🏠",

            "financial":   "💰",

            "water":       "💧",

            "energy":      "⚡",

            "general":     "📋",
        }

        # ─────────────────────────────────────────────
        # SAFE DYNAMIC CATEGORY ICON
        # ─────────────────────────────────────────────

        def get_category_icon(category):

            category = str(category).lower().strip()

            return CATEGORY_ICONS.get(

                category,

                "📌"   # default icon
            )

        for idx, s in enumerate(filtered):
            sid      = s.get("id","")
            s_title  = s.get("title","Untitled")
            s_desc   = s.get("description","")
            s_cat    = s.get("category","general")
            s_date   = s.get("created_at","—")
            s_by     = s.get("uploaded_by","Admin")
            s_icon   = CATEGORY_ICONS.get(s_cat.lower(),"📋")
            s_short  = s_desc[:110] + "…" if len(s_desc) > 110 else s_desc

            # image
            img_url = s.get("image_url","")
            if img_url and img_url.startswith("/"):
                img_url = f"https://bfo-backend.onrender.com{img_url}"

            st.markdown(
                f"<div class='sch-row-card'>"
                f"<div class='sch-row-title'>{s_icon} {s_title}</div>"
                f"<div class='sch-row-desc'>{s_short}</div>"
                f"<div class='sch-row-meta'>"
                f"<span class='sch-row-tag'>{s_cat.title()}</span>"
                f"<span class='sch-row-sub'>📅 {s_date}</span>"
                f"<span class='sch-row-sub'>👤 {s_by}</span>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

            # image + action buttons
            ma1, ma2, ma3, ma4 = st.columns([3, 2, 1, 1])

            with ma2:
                if img_url:
                    try:
                        st.image(img_url, width=110)
                    except Exception:
                        st.markdown(
                            f"<div style='font-size:2rem;text-align:center;'>📜</div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        f"<div style='font-size:2rem;text-align:center;'>📜</div>",
                        unsafe_allow_html=True,
                    )

            with ma3:
                st.markdown("<div class='sch-play'>", unsafe_allow_html=True)
                if st.button(
                    "🔊 Play",
                    key=f"play_{sid}_{idx}",
                    use_container_width=True,
                ):
                    safe_desc = s_desc[:300].replace('"',"'").replace("\n"," ")
                    st.components.v1.html(
                        f'<script>'
                        f'var u=new SpeechSynthesisUtterance("{safe_desc}");'
                        f'u.lang="en-IN";u.rate=0.85;'
                        f'window.speechSynthesis.speak(u);'
                        f'</script>',
                        height=0,
                    )
                    st.toast("🔊 Playing scheme details…")
                st.markdown("</div>", unsafe_allow_html=True)

            with ma4:
                st.markdown("<div class='sch-del'>", unsafe_allow_html=True)
                if st.button(
                    "🗑 Delete",
                    key=f"del_{sid}_{idx}",
                    use_container_width=True,
                ):
                    resp = api("delete", f"/schemes/{sid}")
                    if resp.get("success") or resp is True:
                        st.success("✅ Scheme deleted.")
                        st.rerun()
                    else:
                        st.error(f"Delete failed: {resp.get('detail','Unknown error')}")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

def pg_admin_heatmap():
    _apply_layout("admin")  

    # ── FETCH DATA ────────────────────────────────────────────────────────────
    comps = api("get", "/complaints/all")
    comps = comps if isinstance(comps, list) else []

    geo = [
        (c.get("latitude"), c.get("longitude"), c.get("priority", "medium"),
         c.get("complaint_id", ""), c.get("status", "pending"), c.get("category", "other"),
         c.get("location", ""), c.get("is_emergency", False))
        for c in comps if c.get("latitude") and c.get("longitude")
    ]

    total    = len(comps)
    hi       = len([c for c in comps if c.get("priority") == "high"])
    geotagged = len(geo)
    emer     = len([c for c in comps if c.get("is_emergency")])
    geo_pct  = round(geotagged / total * 100) if total else 0

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="prem-hero" style="padding:28px 28px 24px;margin-bottom:0;">'
        '<div class="prem-hero-avatar">🗺️</div>'
        '<div class="prem-hero-title">Complaint Heatmap</div>'
        '<p class="prem-hero-sub">Geographic distribution of all citizen complaints across the city.</p>'
        '<div class="prem-hero-stats">'
        '<div class="prem-hstat"><div class="prem-hstat-num">' + str(total) + '</div><div class="prem-hstat-lbl">Total</div></div>'
        '<div class="prem-hstat h-red"><div class="prem-hstat-num">' + str(hi) + '</div><div class="prem-hstat-lbl">High Priority</div></div>'
        '<div class="prem-hstat h-green"><div class="prem-hstat-num">' + str(geotagged) + '</div><div class="prem-hstat-lbl">Geotagged</div></div>'
        '<div class="prem-hstat h-amber"><div class="prem-hstat-num">' + str(geo_pct) + '%</div><div class="prem-hstat-lbl">Coverage</div></div>'
        '<div class="prem-hstat h-red"><div class="prem-hstat-num">🚨' + str(emer) + '</div><div class="prem-hstat-lbl">Emergency</div></div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── MAP CONTROLS ROW ──────────────────────────────────────────────────────
    st.markdown('<div class="prem-section-header">🗺️ Interactive Map</div>', unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1, 1, 1, 1])
    with ctrl1:
        filter_pri = st.selectbox("🎯 Priority", ["All", "High", "Medium", "Low"], key="hm_pri")
    with ctrl2:
        filter_stat = st.selectbox("📋 Status",
                                   ["All", "Pending", "In Progress", "Resolved", "Rejected"],
                                   key="hm_stat")
    with ctrl3:
        # Build category list from data
        all_cats = sorted(set(g[5] for g in geo)) if geo else []
        cat_options = ["All"] + [c.title() for c in all_cats]
        filter_cat = st.selectbox("📂 Category", cat_options, key="hm_cat")
    with ctrl4:
        map_style = st.selectbox("🎨 Map Style",
                                 ["Standard", "Dark (CartoDB)", "Satellite (Esri)"],
                                 key="hm_style")

    # ── APPLY FILTERS ─────────────────────────────────────────────────────────
    stat_map = {
        "All": "all", "Pending": "pending", "In Progress": "in_progress",
        "Resolved": "resolved", "Rejected": "rejected"
    }
    filtered_geo = geo
    if filter_pri != "All":
        filtered_geo = [g for g in filtered_geo if g[2].lower() == filter_pri.lower()]
    if filter_stat != "All":
        filtered_geo = [g for g in filtered_geo if g[4] == stat_map[filter_stat]]
    if filter_cat != "All":
        filtered_geo = [g for g in filtered_geo if g[5].lower() == filter_cat.lower()]

    # ── TILE LAYER URL ────────────────────────────────────────────────────────
    tile_urls = {
        "Standard":           "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        "Dark (CartoDB)":     "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        "Satellite (Esri)":   "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    }
    tile_url  = tile_urls.get(map_style, tile_urls["Standard"])
    tile_attr = "OpenStreetMap" if map_style == "Standard" else "CartoDB" if "CartoDB" in map_style else "Esri"

    # ── BUILD MARKERS JS ──────────────────────────────────────────────────────
    markers_js = ""
    heat_points_js = ""
    for lat, lon, pri, cid, stat, cat, loc, is_emg in filtered_geo:
        if is_emg:
            col, rad, stroke, opacity, intensity = "#FF2D2D", 14, "#fff", 0.95, 1.0
        elif pri == "high":
            col, rad, stroke, opacity, intensity = "#EF4444", 11, "#fff", 0.90, 0.8
        elif pri == "medium":
            col, rad, stroke, opacity, intensity = "#F59E0B", 9, "#fff", 0.88, 0.5
        else:
            col, rad, stroke, opacity, intensity = "#10B981", 7, "#fff", 0.85, 0.3

        stat_label = stat.replace("_", " ").title()
        cat_label  = cat.title()
        loc_label  = (loc[:35] + "…") if len(loc) > 35 else loc
        emg_tag    = " 🚨 EMERGENCY" if is_emg else ""
        popup_html = (
            "<div style=\\\'font-family:Inter,sans-serif;min-width:200px;padding:4px;\\\'>"
            "<div style=\\\'font-size:.7rem;font-weight:800;color:#6366F1;margin-bottom:4px;\\\'>#" + str(cid) + emg_tag + "</div>"
            "<div style=\\\'font-size:.82rem;font-weight:700;color:#0F172A;margin-bottom:2px;\\\'>" + cat_label + "</div>"
            "<div style=\\\'font-size:.72rem;color:#475569;margin-bottom:6px;\\\'>" + loc_label + "</div>"
            "<div style=\\\'display:flex;gap:6px;\\\'>"
            "<span style=\\\'background:#EEF2FF;color:#4338CA;border-radius:6px;padding:2px 8px;font-size:.65rem;font-weight:700;\\\'>" + stat_label + "</span>"
            "<span style=\\\'background:#FEF3C7;color:#92400E;border-radius:6px;padding:2px 8px;font-size:.65rem;font-weight:700;\\\'>" + pri.title() + "</span>"
            "</div></div>"
        )

        pulse = ""
        if is_emg:
            pulse = (
                "L.circleMarker([" + str(lat) + "," + str(lon) + "],"
                "{radius:22,fillColor:'#FF2D2D',color:'#FF2D2D',weight:1,fillOpacity:.12,className:'pulse-ring'}).addTo(map);"
            )

        markers_js += (
            pulse
            + "L.circleMarker([" + str(lat) + "," + str(lon) + "],"
            "{radius:" + str(rad) + ",fillColor:'" + col + "',"
            "color:'" + stroke + "',weight:2,fillOpacity:" + str(opacity) + "})"
            ".addTo(map).bindPopup('" + popup_html + "');"
        )
        heat_points_js += "[" + str(lat) + "," + str(lon) + "," + str(intensity) + "],"

    # Map center
    if filtered_geo:
        avg_lat = sum(g[0] for g in filtered_geo) / len(filtered_geo)
        avg_lon = sum(g[1] for g in filtered_geo) / len(filtered_geo)
    else:
        avg_lat, avg_lon = 23.2599, 77.4126

    is_dark = map_style == "Dark (CartoDB)"
    popup_bg = "#1E293B" if is_dark else "#fff"
    popup_col = "#E2E8F0" if is_dark else "#0F172A"

    # ── RENDER MAP ────────────────────────────────────────────────────────────
    map_html = (
        "<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/>"
        "<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>"
        "<script src='https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js'></script>"
        "<style>"
        "  * { margin:0; padding:0; box-sizing:border-box; }"
        "  body { margin:0; padding:0; background:transparent; }"
        "  #hmap { height:520px; width:100%; border-radius:18px; overflow:hidden;"
        "          border:1.5px solid #E2E8F4; }"
        "  .leaflet-popup-content-wrapper {"
        "    border-radius:14px!important; box-shadow:0 8px 28px rgba(15,23,42,.14)!important;"
        "    border:1px solid #E2E8F4!important; padding:6px!important;"
        "    background:" + popup_bg + "!important; color:" + popup_col + "!important;"
        "  }"
        "  .leaflet-popup-tip { background:" + popup_bg + "!important; }"
        "  .leaflet-popup-content { margin:8px 10px!important; }"
        "  .leaflet-control-zoom a {"
        "    border-radius:10px!important; font-weight:700!important;"
        "    color:#6366F1!important; border-color:#E2E8F4!important;"
        "    width:34px!important; height:34px!important; line-height:34px!important;"
        "  }"
        "  .leaflet-control-zoom { border-radius:12px!important; overflow:hidden;"
        "    border:1.5px solid #E2E8F4!important; box-shadow:0 4px 16px rgba(0,0,0,.08)!important; }"
        "  @keyframes pulse-anim { 0%{transform:scale(1);opacity:.4} 100%{transform:scale(2.5);opacity:0} }"
        "  .pulse-ring { animation: pulse-anim 2s ease-out infinite; transform-origin:center; }"
        "</style>"
        "<div id='hmap'></div>"
        "<script>"
        "var map=L.map('hmap',{zoomControl:true,scrollWheelZoom:true}).setView(["
        + str(round(avg_lat, 6)) + "," + str(round(avg_lon, 6)) + "],12);"
        "L.tileLayer('" + tile_url + "',"
        "{maxZoom:19,attribution:'" + tile_attr + "'}).addTo(map);"
        + markers_js +
        "var heatData=[" + heat_points_js + "];"
        "if(heatData.length>0){"
        "L.heatLayer(heatData,{radius:28,blur:20,maxZoom:15,"
        "gradient:{0.2:'#22D3EE',0.4:'#10B981',0.6:'#F59E0B',0.8:'#EF4444',1.0:'#DC2626'}}).addTo(map);"
        "}"
        "setTimeout(function(){map.invalidateSize();},200);"
        "</script>"
    )
    st.components.v1.html(map_html, height=540)

    # ── LEGEND + SUMMARY ROW ──────────────────────────────────────────────────
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'flex-wrap:wrap;gap:12px;margin-top:14px;">'

        '<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">'
        '<span style="font-size:.68rem;font-weight:800;text-transform:uppercase;'
        'letter-spacing:.08em;color:#94A3B8;">Legend</span>'

        '<div style="display:flex;align-items:center;gap:6px;">'
        '<div style="width:14px;height:14px;border-radius:50%;background:#FF2D2D;'
        'box-shadow:0 0 0 3px rgba(255,45,45,.25);"></div>'
        '<span style="font-size:.75rem;font-weight:700;color:#334155;">Emergency</span></div>'

        '<div style="display:flex;align-items:center;gap:6px;">'
        '<div style="width:12px;height:12px;border-radius:50%;background:#EF4444;"></div>'
        '<span style="font-size:.75rem;font-weight:600;color:#334155;">High</span></div>'

        '<div style="display:flex;align-items:center;gap:6px;">'
        '<div style="width:10px;height:10px;border-radius:50%;background:#F59E0B;"></div>'
        '<span style="font-size:.75rem;font-weight:600;color:#334155;">Medium</span></div>'

        '<div style="display:flex;align-items:center;gap:6px;">'
        '<div style="width:8px;height:8px;border-radius:50%;background:#10B981;"></div>'
        '<span style="font-size:.75rem;font-weight:600;color:#334155;">Low</span></div>'

        '<div style="display:flex;align-items:center;gap:6px;">'
        '<div style="width:18px;height:8px;border-radius:4px;'
        'background:linear-gradient(90deg,#22D3EE,#10B981,#F59E0B,#EF4444,#DC2626);"></div>'
        '<span style="font-size:.75rem;font-weight:600;color:#334155;">Heat Intensity</span></div>'
        '</div>'

        '<span style="background:#EEF2FF;color:#4338CA;border-radius:20px;'
        'padding:5px 16px;font-size:.78rem;font-weight:800;border:1.5px solid #C7D2FE;">'
        '📍 ' + str(len(filtered_geo)) + ' of ' + str(geotagged) + ' geotagged shown</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # ── CATEGORY BREAKDOWN CARDS ──────────────────────────────────────────────
    if filtered_geo:
        st.markdown('<div class="prem-section-header" style="margin-top:22px;">📊 Category Breakdown</div>',
                    unsafe_allow_html=True)

        cat_counts = {}
        for _, _, _, _, _, cat, _, _ in filtered_geo:
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        top_cats = sorted(cat_counts.items(), key=lambda x: -x[1])

        CAT_ICON = {

            "water":       "💧",

            "electricity": "⚡",

            "road":        "🛣️",

            "waste":       "🗑️",

            "drainage":    "🌊",

            "health":      "🏥",

            "other":       "📋",
        }

        # ─────────────────────────────────────────────
        # SAFE DYNAMIC CATEGORY ICON HELPER
        # ─────────────────────────────────────────────

        def get_cat_icon(category):

            category = str(category).lower().strip()

            return CAT_ICON.get(

                category,

                "📌"   # default icon
            )
        CAT_COLOR = {

            "water":       "#0EA5E9",

            "electricity": "#EAB308",

            "road":        "#6B7280",

            "waste":       "#22C55E",

            "drainage":    "#06B6D4",

            "health":      "#EF4444",

            "other":       "#6366F1",
        }

        # ─────────────────────────────────────────────
        # SAFE DYNAMIC CATEGORY COLOR
        # ─────────────────────────────────────────────

        def get_cat_color(category):

            category = str(category).lower().strip()

            return CAT_COLOR.get(

                category,

                "#2563EB"   # default modern blue
            )

        num_cols = min(len(top_cats), 4)
        if num_cols > 0:
            cols = st.columns(num_cols)
            for i, (cat, count) in enumerate(top_cats[:4]):
                pct   = round(count / len(filtered_geo) * 100)
                icon  = CAT_ICON.get(cat, "📋")
                color = CAT_COLOR.get(cat, "#6366F1")
                with cols[i]:
                    st.markdown(
                        '<div class="prem-stat-card" style="padding:16px 12px 14px;">'
                        '<div style="font-size:1.5rem;margin-bottom:6px;">' + icon + '</div>'
                        '<div class="prem-stat-num" style="font-size:1.6rem;color:' + color + ';">' + str(count) + '</div>'
                        '<div class="prem-stat-lbl">' + cat.title() + '</div>'
                        '<div style="margin-top:8px;">'
                        '<div style="background:#F1F5F9;border-radius:6px;height:5px;overflow:hidden;">'
                        '<div style="height:5px;border-radius:6px;background:' + color + ';width:' + str(pct) + '%;"></div>'
                        '</div>'
                        '<div style="font-size:.65rem;color:#94A3B8;font-weight:600;margin-top:3px;">'
                        + str(pct) + '% of shown</div>'
                        '</div></div>',
                        unsafe_allow_html=True
                    )

    # ── STATUS BREAKDOWN ──────────────────────────────────────────────────────
    if filtered_geo:
        st.markdown('<div class="prem-section-header" style="margin-top:18px;">📋 Status Distribution</div>',
                    unsafe_allow_html=True)
        stat_counts = {}
        for _, _, _, _, stat, _, _, _ in filtered_geo:
            stat_counts[stat] = stat_counts.get(stat, 0) + 1

        STAT_ICON = {"pending":"⏳","in_progress":"🔄","resolved":"✅","rejected":"❌","closed":"🔒"}
        STAT_COL  = {"pending":"#F59E0B","in_progress":"#3B82F6","resolved":"#22C55E","rejected":"#EF4444","closed":"#6B7280"}

        num_s = min(len(stat_counts), 5)
        if num_s > 0:
            scols = st.columns(num_s)
            for i, (s, cnt) in enumerate(sorted(stat_counts.items(), key=lambda x: -x[1])[:5]):
                pct = round(cnt / len(filtered_geo) * 100)
                with scols[i]:
                    st.markdown(
                        '<div class="prem-stat-card" style="padding:14px 10px 12px;">'
                        '<div style="font-size:1.3rem;margin-bottom:4px;">' + STAT_ICON.get(s,"📋") + '</div>'
                        '<div class="prem-stat-num" style="font-size:1.4rem;color:' + STAT_COL.get(s,"#6366F1") + ';">' + str(cnt) + '</div>'
                        '<div class="prem-stat-lbl">' + s.replace("_"," ").title() + '</div>'
                        '<div style="font-size:.62rem;color:#94A3B8;font-weight:600;margin-top:4px;">' + str(pct) + '%</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )

    # ── NO GEO DATA STATE ─────────────────────────────────────────────────────
    if not geo:
        st.markdown("""
        <div class="prem-empty-state" style="margin-top:16px;">
            <span class="prem-empty-icon">📍</span>
            <div class="prem-empty-title">No geotagged complaints yet</div>
            <div class="prem-empty-sub">
                Complaints with GPS coordinates will appear on this map automatically.
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif not filtered_geo:
        st.markdown("""
        <div class="prem-empty-state" style="margin-top:16px;">
            <span class="prem-empty-icon">🔍</span>
            <div class="prem-empty-title">No results for current filters</div>
            <div class="prem-empty-sub">Try changing the priority, status, or category filter above.</div>
        </div>
        """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# SHARED: complaint list + leaderboard
# ═════════════════════════════════════════════════════════════════════════════
 
def _complaint_list(comps, pfx, off_id):
    _apply_layout("admin")  
    dark = st.session_state.get("dark_mode", False)
 
    # colour / icon maps
    SC = {
        "pending":     "#f59e0b",
        "in_progress": "#3b82f6",
        "resolved":    "#22c55e",
        "closed":      "#6b7280",
        "rejected":    "#ef4444",
    }
    SI = {
        "pending":     "⏳",
        "in_progress": "🔄",
        "resolved":    "✅",
        "closed":      "🔒",
        "rejected":    "❌",
    }
    PRIORITY_STYLE = {
        "high":   ("#991b1b", "#fee2e2"),
        "medium": ("#92400e", "#fef3c7"),
        "low":    ("#065f46", "#d1fae5"),
    }
 
    desc_bg  = "#0D1117" if dark else "#f8fafc"
    desc_bor = "#1E2A3D" if dark else "#e2e8f0"
    desc_col = "#E2E8F0" if dark else "#0f172a"
 
    for c in comps[:50]:
        s   = c.get("status", "pending")
        p   = c.get("priority", "medium")
        sc  = SC.get(s, "#888")
        si  = SI.get(s, "📋")
        cid = c.get("complaint_id", "")
        fb  = c.get("feedback", "")
        rat = c.get("rating")
 
        p_col, p_bg = PRIORITY_STYLE.get(p, ("#64748b", "#f1f5f9"))
 
        # ── SLA ──────────────────────────────────────────────────
        sla_info = format_sla_display(c)
        is_overdue   = bool(sla_info and sla_info.get("is_overdue"))
        border_color = "#dc2626" if is_overdue else sc
 
        # ── feedback badge ────────────────────────────────────────
        if fb == "satisfied":
            fb_html = ('<span style="background:#f0fdf4;color:#15803d;border-radius:6px;'
                       'padding:2px 8px;font-size:.72rem;font-weight:700;">👍 Satisfied</span>')
        elif fb == "not_satisfied":
            fb_html = ('<span style="background:#fef2f2;color:#b91c1c;border-radius:6px;'
                       'padding:2px 8px;font-size:.72rem;font-weight:700;">❌ Not Satisfied</span>')
        elif fb == "auto_closed":
            fb_html = ('<span style="background:#f9fafb;color:#6b7280;border-radius:6px;'
                       'padding:2px 8px;font-size:.72rem;font-weight:700;">🔒 Auto Closed</span>')
        else:
            fb_html = ""
 
        # ── rating stars ──────────────────────────────────────────
        rat_html = ""
        if rat:
            rat_html = f'<span style="margin-left:4px;">{stars_html(rat.get("stars", 0))}</span>'
 
        # ── SLA badge ─────────────────────────────────────────────
        sla_html = ""
        if sla_info:
            sla_c = sla_info["color"]
            sla_html = (
                f'<span style="background:{sla_c}20;color:{sla_c};border-radius:6px;'
                f'padding:2px 8px;font-size:.72rem;font-weight:700;">'
                f'{sla_info["text"]}</span>'
            )
 
        # ── SLA deadline ──────────────────────────────────────────
        sla_deadline_html = ""
        if c.get("sla_deadline"):
            sla_deadline_html = (
                f'<span style="font-size:.7rem;opacity:.7;">⏰ Deadline: {c["sla_deadline"]}</span>'
            )
 
        # ── priority pill ─────────────────────────────────────────
        priority_html = (
            f'<span style="background:{p_bg};color:{p_col};border-radius:40px;'
            f'padding:4px 12px;font-size:.7rem;font-weight:700;">'
            f'{p.title()}</span>'
        )
 
        # ── status pill ───────────────────────────────────────────
        status_html = (
            f'<span style="color:{sc};font-weight:700;font-size:.78rem;">'
            f'{si} {s.replace("_"," ").title()}</span>'
        )
 
        # ── overdue background ────────────────────────────────────
        overdue_bg = "#fef2f2" if (is_overdue and not dark) else ("rgba(220,38,38,0.08)" if is_overdue else "transparent")
 
        # ── expander label ────────────────────────────────────────
        expander_label = (
            f"{'🚨 ' if is_overdue else ''}"
            f"{si} #{cid}  ·  {c.get('category','').title()}  ·  "
            f"{c.get('department', c.get('user_name',''))}"
            f"{' — SLA BREACHED' if is_overdue else ''}"
        )
 
        with st.expander(expander_label):
            # ── main card HTML ────────────────────────────────────
            st.markdown(
                f"<div style='border-left:4px solid {border_color};padding:10px 14px;"
                f"border-radius:0 10px 10px 0;background:{overdue_bg};'>"
 
                # description
                f"<div style='background:{desc_bg};padding:14px;border-radius:12px;"
                f"margin-bottom:10px;border:1px solid {desc_bor};color:{desc_col};"
                f"font-size:.9rem;line-height:1.55;white-space:pre-wrap;"
                f"word-wrap:break-word;max-height:200px;overflow-y:auto;'>"
                f"{c.get('description', '')}"
                f"</div>"
 
                # badges row
                f"<div style='display:flex;gap:8px;flex-wrap:wrap;align-items:center;"
                f"margin-bottom:8px;'>"
                f"{priority_html}"
                f"{status_html}"
                f"{sla_html}"
                f"{fb_html}"
                f"{rat_html}"
                f"</div>"
 
                # meta row
                f"<div style='font-size:.75rem;opacity:.6;margin-bottom:4px;'>"
                f"📍 {c.get('location','N/A')} · "
                f"👤 {c.get('user_name','')} · "
                f"📞 {c.get('user_phone','')} · "
                f"🕐 {c.get('created_at','')}"
                f"</div>"
 
                # SLA deadline
                + (f"<div style='font-size:.7rem;margin-top:2px;'>{sla_deadline_html}</div>" if sla_deadline_html else "")
                + "</div>",
                unsafe_allow_html=True,
            )
 
            # resolution time
            if c.get("time_to_resolve_hours") and s in ("resolved", "closed"):
                st.info(f"⏱️ Resolution time: {c['time_to_resolve_hours']} hours")
 
            # ========== IMPROVED IMAGE DISPLAY ==========
            if c.get("image_path"):
                img_url = f"{API_BASE}{c['image_path']}"
                # Button to open image in new tab
                st.markdown(
                    f'<a href="{img_url}" target="_blank" style="text-decoration:none;">'
                    '<button style="background: #6366F1; color: white; border: none; '
                    'border-radius: 8px; padding: 6px 12px; cursor: pointer; '
                    'font-weight: 600; margin: 8px 0;">🔍 View Attached Image</button></a>',
                    unsafe_allow_html=True
                )
                # Optional thumbnail preview (uncomment if you want a small image)
                # st.image(img_url, width=200, caption="Preview (click button for full size)")
 
            # not-satisfied warning
            if fb == "not_satisfied":
                st.warning("⚠️ User not satisfied — please re-investigate!")
 
            # action buttons
            if s not in ("closed",) and fb not in ("satisfied", "auto_closed"):
                note = st.text_input(
                    "Resolution note",
                    key=f"{pfx}_note_{cid}",
                    placeholder="Describe action taken…",
                    label_visibility="collapsed",
                )
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("🔄 In Progress", key=f"{pfx}_ip_{cid}", use_container_width=True):
                        _do_status(cid, "in_progress", note or "Being processed by the department.", off_id)
                with b2:
                    if st.button("✅ Resolve", key=f"{pfx}_res_{cid}", use_container_width=True):
                        _do_status(cid, "resolved", note or "Resolved by official.", off_id)
                with b3:
                    if st.button("❌ Reject", key=f"{pfx}_rej_{cid}", use_container_width=True):
                        _do_status(cid, "rejected", note or "Rejected.", off_id)
            else:
                st.info("ℹ️ No further action required.")

def pg_public_transparency():
    _apply_layout("user")
    dark  = st.session_state.get("dark_mode", False)
    st.markdown(get_css(dark_mode=dark), unsafe_allow_html=True)

    _CARD = "#10161F" if dark else "#FFFFFF"
    _BG2  = "#080C14" if dark else "#F4F6FB"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
    _A1   = "#6366F1"
    _A2   = "#8B5CF6"

    st.markdown(f"""
<style>
/* ── hero ── */
.pt-hero{{
    background:linear-gradient(135deg,#064E3B 0%,#065F46 40%,#0C4A6E 100%);
    border-radius:22px;padding:1.75rem 2rem;margin-bottom:1.75rem;
    position:relative;overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,0.25);
}}
.pt-hero::before{{content:'';position:absolute;top:-60px;right:-60px;width:220px;height:220px;
    border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,0.07) 0%,transparent 70%);
    pointer-events:none;}}
.pt-hero-title{{font-family:'Sora',sans-serif;font-size:1.75rem;font-weight:800;
    color:#fff;margin-bottom:6px;position:relative;z-index:1;}}
.pt-hero-sub{{font-size:0.86rem;color:rgba(255,255,255,0.65);
    position:relative;z-index:1;font-weight:500;}}
.pt-hero-chips{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;position:relative;z-index:1;}}
.pt-hero-chip{{background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.20);
    border-radius:20px;padding:4px 12px;font-size:0.70rem;font-weight:700;color:#fff;}}

/* ── section header ── */
.pt-sec{{font-size:0.70rem;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;
    color:{_SUB};margin:22px 0 12px;display:flex;align-items:center;gap:10px;}}
.pt-sec::before{{content:'';width:4px;height:16px;
    background:linear-gradient(180deg,#10B981,#059669);border-radius:3px;flex-shrink:0;}}
.pt-sec::after{{content:'';flex:1;height:1px;
    background:linear-gradient(to right,{_BOR},transparent);}}

/* ── metric cards ── */
.pt-metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:6px;}}
.pt-metric{{background:{_CARD};border:1px solid {_BOR};border-radius:18px;
    padding:18px 12px 14px;text-align:center;position:relative;overflow:hidden;
    box-shadow:0 2px 8px rgba(15,23,42,0.06);transition:transform 0.20s,box-shadow 0.20s;}}
.pt-metric::before{{content:'';position:absolute;top:0;left:0;right:0;height:4px;
    border-radius:18px 18px 0 0;}}
.pt-metric:hover{{transform:translateY(-3px);box-shadow:0 10px 28px rgba(16,185,129,0.12);}}
.pt-metric-num{{font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;line-height:1.1;margin-bottom:5px;}}
.pt-metric-lbl{{font-size:0.68rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.07em;color:{_SUB};}}

/* ── resolution bar ── */
.pt-res-wrap{{background:{_CARD};border:1px solid {_BOR};border-radius:14px;
    padding:16px 20px;margin:4px 0;box-shadow:0 2px 8px rgba(15,23,42,0.05);}}
.pt-res-header{{display:flex;justify-content:space-between;
    font-size:0.80rem;font-weight:700;color:{_TXT};margin-bottom:8px;}}
.pt-prog-track{{background:{_BOR};border-radius:10px;height:10px;overflow:hidden;}}
.pt-prog-fill{{height:100%;border-radius:10px;transition:width 0.4s ease;}}

/* ── area cards ── */
.pt-area-card{{background:{_CARD};border:1px solid {_BOR};border-radius:14px;
    padding:14px 16px;margin-bottom:8px;display:flex;justify-content:space-between;
    align-items:center;flex-wrap:wrap;gap:8px;
    box-shadow:0 2px 6px rgba(15,23,42,0.04);
    transition:transform 0.18s;}}
.pt-area-card:hover{{transform:translateX(4px);}}
.pt-area-name{{font-size:0.88rem;font-weight:700;color:{_TXT};}}
.pt-area-meta{{font-size:0.72rem;color:{_SUB};margin-top:2px;}}
.pt-area-rate{{font-size:0.80rem;font-weight:800;}}
.pt-area-prog-track{{background:{_BOR};border-radius:6px;height:6px;
    overflow:hidden;margin-top:6px;}}
.pt-area-prog-fill{{height:100%;border-radius:6px;
    background:linear-gradient(90deg,#10B981,#059669);transition:width 0.4s;}}

/* ── trend bar ── */
.pt-trend-row{{margin-bottom:8px;}}
.pt-trend-label{{display:flex;justify-content:space-between;
    font-size:0.76rem;font-weight:600;color:{_TXT};margin-bottom:4px;}}
.pt-trend-cnt{{color:{_SUB};font-size:0.70rem;font-weight:600;}}
.pt-trend-track{{background:{_BOR};border-radius:6px;height:8px;overflow:hidden;}}
.pt-trend-fill{{height:100%;border-radius:6px;
    background:linear-gradient(90deg,{_A1},{_A2});transition:width 0.4s;}}

/* ── timestamp ── */
.pt-ts{{font-size:0.68rem;color:{_SUB};text-align:right;margin-top:10px;}}

/* ── empty ── */
.pt-empty{{text-align:center;padding:2.5rem 2rem;background:{_CARD};
    border-radius:18px;border:1.5px dashed {_BOR};}}
.pt-empty-icon{{font-size:2.5rem;opacity:0.5;display:block;margin-bottom:10px;}}
.pt-empty-txt{{font-size:0.85rem;color:{_SUB};}}

@media(max-width:600px){{
    .pt-hero{{padding:1.4rem 1rem;border-radius:18px;}}.pt-hero-title{{font-size:1.4rem;}}
    .pt-metrics{{grid-template-columns:repeat(2,1fr);}}
}}
</style>
""", unsafe_allow_html=True)

    # ═══════════════════════════════════��════════════════════
    # HERO
    # ════════════════════════════════════════════════════════
    now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
    st.markdown(
        "<div class='pt-hero'>"
        "<div class='pt-hero-title'>📊 Public Transparency Portal</div>"
        "<div class='pt-hero-sub'>Real-time grievance metrics · Open data for accountable governance</div>"
        "<div class='pt-hero-chips'>"
        "<span class='pt-hero-chip'>🔄 Live Data</span>"
        "<span class='pt-hero-chip'>🔓 Open Access</span>"
        "<span class='pt-hero-chip'>🏛️ Accountable Governance</span>"
        f"<span class='pt-hero-chip'>🕐 {now_str}</span>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════
    # FETCH
    # ════════════════════════════════════════════════════════
    stats = api("get", "/admin/stats")
    if "error" in stats:
        st.markdown(
            "<div class='pt-empty'><span class='pt-empty-icon'>⚠️</span>"
            "<div class='pt-empty-txt'>Unable to load statistics right now. Please try again later.</div></div>",
            unsafe_allow_html=True,
        )
        bc1, bc2, bc3 = st.columns([1,2,1])
        with bc2:
            if st.button("← Back to Home", key="pt_back_err", use_container_width=True):
                st.session_state.screen = "language"; st.rerun()
        return

    total        = stats.get("total_complaints", 0)
    res_rate     = max(0, min(100, stats.get("resolution_rate", 0)))
    pending      = stats.get("pending", 0)
    resolved     = stats.get("resolved", 0)
    in_progress  = stats.get("in_progress", 0)

    # ════════════════════════════════════════════════════════
    # METRIC CARDS
    # ════════════════════════════════════════════════════════
    st.markdown("<div class='pt-sec'>📈 Key Metrics</div>", unsafe_allow_html=True)

    METRICS = [
        (total,       "📋 Total Filed",     "#6366F1","linear-gradient(90deg,#6366F1,#8B5CF6)"),
        (resolved,    "✅ Resolved",        "#22C55E","linear-gradient(90deg,#22C55E,#16A34A)"),
        (pending,     "⏳ Pending",         "#F59E0B","linear-gradient(90deg,#F59E0B,#D97706)"),
        (in_progress, "🔄 In Progress",     "#0EA5E9","linear-gradient(90deg,#0EA5E9,#0369A1)"),
    ]
    st.markdown("<div class='pt-metrics'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    mc = st.columns(4)
    for col,(val,lbl,clr,grad) in zip(mc, METRICS):
        with col:
            st.markdown(
                f"<div class='pt-metric'>"
                f"<div style='position:absolute;top:0;left:0;right:0;height:4px;"
                f"background:{grad};border-radius:18px 18px 0 0;'></div>"
                f"<div class='pt-metric-num' style='color:{clr};'>{val}</div>"
                f"<div class='pt-metric-lbl'>{lbl}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── overall resolution bar ────────────────────────────
    bar_clr = "#22C55E" if res_rate>=70 else "#F59E0B" if res_rate>=40 else "#EF4444"
    st.markdown(
        f"<div class='pt-res-wrap'>"
        f"<div class='pt-res-header'>"
        f"<span>Overall Resolution Rate</span>"
        f"<span style='color:{bar_clr};'>{res_rate}%</span>"
        f"</div>"
        f"<div class='pt-prog-track'>"
        f"<div class='pt-prog-fill' style='width:{res_rate}%;"
        f"background:linear-gradient(90deg,{bar_clr},{bar_clr}CC);'></div>"
        f"</div>"
        f"<div style='font-size:0.68rem;color:{_SUB};margin-top:5px;'>"
        f"{resolved} of {total} complaints resolved</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════
    # AREA PERFORMANCE
    # ════════════════════════════════════════════════════════
    complaints = api("get", "/complaints/all")
    if isinstance(complaints, list) and complaints:

        # aggregate by area
        area_stats: dict = {}
        for idx, c in enumerate(complaints, start=1):
            loc  = c.get("location","Unknown")
            area = loc.split(",")[0].strip() if "," in loc else loc.strip() or "Unknown"
            if area not in area_stats:
                area_stats[area] = {"total":0,"resolved":0}
            area_stats[area]["total"] += 1
            if c.get("status") in ("resolved","closed"):
                area_stats[area]["resolved"] += 1

        area_list = []
        for area,data in area_stats.items():
            t_ = max(data["total"],1)
            r_ = max(0, min(data["resolved"], t_))
            rate = round(r_ / t_ * 100, 1)
            area_list.append({"area":area,"total":data["total"],"resolved":r_,"rate":rate})
        area_list.sort(key=lambda x: x["total"], reverse=True)

        st.markdown("<div class='pt-sec'>🏙️ Area Performance</div>", unsafe_allow_html=True)

        ap1, ap2 = st.columns(2)

        def area_card(a):
            rate = a["rate"]
            clr  = "#22C55E" if rate>=70 else "#F59E0B" if rate>=40 else "#EF4444"
            bar  = int(rate)
            st.markdown(
                f"<div class='pt-area-card'>"
                f"<div style='flex:1;min-width:0;'>"
                f"<div class='pt-area-name'>{a['area']}</div>"
                f"<div class='pt-area-meta'>📋 {a['total']} complaints · ✅ {a['resolved']} resolved</div>"
                f"<div class='pt-area-prog-track'>"
                f"<div class='pt-area-prog-fill' style='width:{bar}%;'></div>"
                f"</div>"
                f"</div>"
                f"<div class='pt-area-rate' style='color:{clr};'>{rate}%</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with ap1:
            st.markdown(
                f"<div style='font-size:0.72rem;font-weight:700;color:{_TXT};"
                f"margin-bottom:8px;'>🔥 Most Active Areas</div>",
                unsafe_allow_html=True,
            )
            for a in area_list[:5]:
                area_card(a)

        with ap2:
            st.markdown(
                f"<div style='font-size:0.72rem;font-weight:700;color:{_TXT};"
                f"margin-bottom:8px;'>🍃 Least Active Areas</div>",
                unsafe_allow_html=True,
            )
            for a in [x for x in area_list[-5:] if x["total"]>0]:
                area_card(a)

        # ── complaint trends (last 7 days) ────────────────────
        st.markdown("<div class='pt-sec'>📅 Complaint Trends — Last 7 Days</div>", unsafe_allow_html=True)

        from collections import defaultdict
        daily: dict = defaultdict(int)
        DATE_FMTS = ["%d %b %Y, %I:%M %p","%Y-%m-%dT%H:%M:%S","%Y-%m-%d %H:%M:%S","%d/%m/%Y %H:%M"]
        for idx, c in enumerate(complaints, start=1):
            raw = c.get("created_at","")
            for fmt in DATE_FMTS:
                try:
                    dt  = datetime.strptime(str(raw).strip(), fmt)
                    day = dt.strftime("%d %b")
                    daily[day] += 1
                    break
                except ValueError:
                    continue

        if daily:
            sorted_days = sorted(daily.keys(),
                                  key=lambda d: datetime.strptime(d, "%d %b").replace(year=datetime.now().year))
            last7 = sorted_days[-7:]
            mx    = max(daily[d] for d in last7) or 1

            st.markdown(
                f"<div style='background:{_CARD};border:1px solid {_BOR};"
                f"border-radius:16px;padding:16px 20px;'>",
                unsafe_allow_html=True,
            )
            for day in last7:
                cnt = daily[day]
                pct = int(cnt / mx * 100)
                st.markdown(
                    f"<div class='pt-trend-row'>"
                    f"<div class='pt-trend-label'>"
                    f"<span>{day}</span>"
                    f"<span class='pt-trend-cnt'>{cnt} complaints</span>"
                    f"</div>"
                    f"<div class='pt-trend-track'>"
                    f"<div class='pt-trend-fill' style='width:{pct}%;'></div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No date-indexed complaint data available.")

        # ── category breakdown ────────────────────────────────
        cats: dict = {}
        for idx, c in enumerate(complaints, start=1):
            k = c.get("category","other")
            cats[k] = cats.get(k,0) + 1

        if cats:
            st.markdown("<div class='pt-sec'>📂 Complaints by Category</div>", unsafe_allow_html=True)
            mx_cat = max(cats.values()) or 1
            st.markdown(
                f"<div style='background:{_CARD};border:1px solid {_BOR};"
                f"border-radius:16px;padding:16px 20px;'>",
                unsafe_allow_html=True,
            )
            CAT_ICONS = {

                "water":       "💧",

                "electricity": "⚡",

                "road":        "🛣️",

                "waste":       "🗑️",

                "drainage":    "🌊",

                "health":      "🏥",

                "other":       "📋",
            }

            # ─────────────────────────────────────────────
            # SAFE CATEGORY ICON HELPER
            # ─────────────────────────────────────────────

            def get_cat_icon(category):

                category = str(category).lower().strip()

                # Smart auto-matching
                AUTO_ICONS = {

                    "cyber":     "💻",

                    "internet":  "🌐",

                    "telecom":   "📡",

                    "transport": "🚌",

                    "police":    "🚓",

                    "fire":      "🔥",

                    "tourism":   "✈️",

                    "bank":      "🏦",

                    "finance":   "💰",

                    "education": "🎓",

                    "housing":   "🏠",
                }

                for key, icon in AUTO_ICONS.items():

                    if key in category:

                        return icon

                # Default safe fallback
                return CAT_ICONS.get(

                    category,

                    "📌"
                )
            for cat,cnt in sorted(cats.items(), key=lambda x:-x[1]):
                pct = int(cnt / mx_cat * 100)
                icon = CAT_ICONS.get(cat,"📋")
                st.markdown(
                    f"<div class='pt-trend-row'>"
                    f"<div class='pt-trend-label'>"
                    f"<span>{icon} {cat.title()}</span>"
                    f"<span class='pt-trend-cnt'>{cnt}</span>"
                    f"</div>"
                    f"<div class='pt-trend-track'>"
                    f"<div class='pt-trend-fill' style='width:{pct}%;'></div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown(
            "<div class='pt-empty'><span class='pt-empty-icon'>📭</span>"
            "<div class='pt-empty-txt'>No complaint data available yet.</div></div>",
            unsafe_allow_html=True,
        )

    # ════════════════════════════════════════════════════════
    # TIMESTAMP + BACK
    # ════════════════════���═══════════════════════════════════
    st.markdown(
        f"<div class='pt-ts'>🕐 Last updated: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}"
        f" · Data refreshes in real-time</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    bc1, bc2, bc3 = st.columns([1,2,1])
    with bc2:
        if st.button("← Back to Home", key="pt_back", use_container_width=True):
            st.session_state.screen = "language"
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# STATUS UPDATE HELPER
# ═══════════════════════════════════════════════════════════════
def _do_status(cid, status, note, off_id=None):
    """Update complaint status via API and show result."""
    payload = {"status": status, "note": note}
    if off_id:
        payload["official_id"] = off_id

    d = api("put", f"/complaints/{cid}/status", json=payload)

    if d.get("success"):
        if status == "resolved":
            st.success(
                "✅ Marked as Resolved! The citizen has been notified and has 2 days to confirm & rate."
            )
        else:
            st.success(
                f"✅ Status updated to **{status.replace('_',' ').title()}** successfully."
            )
        st.rerun()
    else:
        err = d.get("error") or d.get("detail") or "Unknown error"
        st.error(f"⚠️ Update failed: {err}")





def _render_leaderboard(board):
    if not board:
        st.info("No eligible officials yet (need at least 1 resolved complaint).")
        return
 
    dark  = st.session_state.get("dark_mode", False)
    _CARD = "#10161F" if dark else "#FFFFFF"
    _BOR  = "#1E2A3D" if dark else "#E2E8F4"
    _TXT  = "#F0F4FF" if dark else "#0F172A"
    _SUB  = "#8896B0" if dark else "#64748B"
 
    MEDAL = {1: "🥇", 2: "🥈", 3: "🥉"}
 
    for o in board:
        rank      = o.get("rank", "-")
        eligible  = o.get("eligible", True)
        medal     = MEDAL.get(rank, "🏅") if isinstance(rank, int) else "⏳"
        avg       = o.get("avg_rating", 0)
        res       = o.get("total_resolved", 0)
        ass       = o.get("total_assigned", 0)
        rate      = min(o.get("resolution_rate", 0), 100)
        rc        = o.get("rating_count", 0)
        dept_lbl  = f" · 🏢 {o['department']}" if o.get("department") else ""
        opacity   = "1" if eligible else "0.5"
 
        # rank badge colour
        rank_color = (
            "#F59E0B" if rank == 1 else
            "#94A3B8" if rank == 2 else
            "#CD7C4E" if rank == 3 else
            "#6366F1"
        )
        rank_bg = (
            "rgba(245,158,11,0.12)"  if rank == 1 else
            "rgba(148,163,184,0.12)" if rank == 2 else
            "rgba(205,124,78,0.12)"  if rank == 3 else
            "rgba(99,102,241,0.10)"
        )
 
        ineligible_note = (
            '<span style="font-style:italic;opacity:.6;font-size:.72rem;">'
            ' · Needs more resolved complaints to rank</span>'
            if not eligible else ""
        )
 
        st.markdown(
            f"<div style='"
            f"display:flex;align-items:center;gap:14px;"
            f"background:{_CARD};border:1px solid {_BOR};"
            f"border-radius:16px;padding:14px 18px;"
            f"margin-bottom:10px;opacity:{opacity};"
            f"transition:transform .18s,box-shadow .18s;"
            f"'>"
 
            # medal
            f"<div style='font-size:1.8rem;flex-shrink:0;line-height:1;'>{medal}</div>"
 
            # name + stars + meta
            f"<div style='flex:1;min-width:0;'>"
            f"<div style='font-size:.95rem;font-weight:800;color:{_TXT};margin-bottom:3px;'>"
            f"{o.get('name','')}{dept_lbl}"
            f"</div>"
            f"<div style='margin:4px 0;'>{stars_html(avg, rc)}</div>"
            f"<div style='font-size:.75rem;color:{_SUB};margin-top:2px;'>"
            f"✅ {res} resolved · 📋 {ass} assigned · 📈 {rate}% success rate"
            f"{ineligible_note}"
            f"</div>"
            f"</div>"
 
            # rank badge
            f"<div style='"
            f"background:{rank_bg};color:{rank_color};"
            f"border:1.5px solid {rank_color};"
            f"border-radius:12px;padding:8px 14px;"
            f"font-family:monospace;font-size:1.1rem;font-weight:800;"
            f"flex-shrink:0;text-align:center;min-width:48px;"
            f"'>#{rank}</div>"
 
            f"</div>",
            unsafe_allow_html=True,
        )

# Add to frontend/app.py - Predictive Governance Screen

# Add this after pg_admin_heatmap() function or near other admin functions

def pg_predictive_analytics():
    _apply_layout("user")
    

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="prem-hero">
        <div class="prem-hero-title">🔮 Predictive Governance</div>
        <div class="prem-hero-sub">
            AI-powered predictions to anticipate issues before they escalate
        </div>
        <div class="prem-hero-stats">
            <div class="prem-hstat h-red">
                <div class="prem-hstat-num">⚠️</div>
                <div class="prem-hstat-lbl">Risk Zones</div>
            </div>
            <div class="prem-hstat h-blue">
                <div class="prem-hstat-num">📊</div>
                <div class="prem-hstat-lbl">Workload</div>
            </div>
            <div class="prem-hstat h-amber">
                <div class="prem-hstat-num">🔥</div>
                <div class="prem-hstat-lbl">Hotspots</div>
            </div>
            <div class="prem-hstat h-green">
                <div class="prem-hstat-num">📈</div>
                <div class="prem-hstat-lbl">Trends</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ACTIVE ALERTS ─────────────────────────────────────────────────────────
    summary      = api("get", "/admin/predictive/alert-summary")
    summary_data = summary.get("summary", {}) if isinstance(summary, dict) else {}
    alerts       = summary_data.get("active_alerts", [])

    if alerts:
        st.markdown('<div class="prem-section-header">🚨 Active Alerts</div>', unsafe_allow_html=True)
        for alert in alerts:
            t = alert.get("type", "info")
            msg = alert.get("message", "")
            if t == "critical":
                st.error(f"🔴 {msg}")
            elif t == "warning":
                st.warning(f"🟠 {msg}")
            else:
                st.info(f"🔵 {msg}")

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚠️ Risk Zones",
        "📊 Workload Forecast",
        "🔥 Hotspots Map",
        "📈 Complaint Trends",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 1 — RISK ZONES
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="prem-section-header">High-Risk Zones</div>', unsafe_allow_html=True)
        st.caption("Areas predicted to have complaint surges based on historical patterns")

        risk_data  = api("get", "/admin/predictive/risk-zones",
                         params={"threshold": 2, "days_back": 30})
        risk_zones = risk_data.get("risk_zones", []) if isinstance(risk_data, dict) else []

        if not risk_zones:
            st.markdown("""
            <div class="prem-empty-state">
                <span class="prem-empty-icon">✅</span>
                <div class="prem-empty-title">No significant risk zones detected</div>
                <div class="prem-empty-sub">System is stable — continue monitoring.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            critical = len([z for z in risk_zones if z.get("risk_level") == "critical"])
            high     = len([z for z in risk_zones if z.get("risk_level") == "high"])
            medium   = len([z for z in risk_zones if z.get("risk_level") == "medium"])

            # Summary stat cards
            rc1, rc2, rc3, rc4 = st.columns(4)
            with rc1:
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#EF4444">{critical}</div>
                    <div class="prem-stat-lbl">🔴 Critical</div>
                </div>""", unsafe_allow_html=True)
            with rc2:
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#F97316">{high}</div>
                    <div class="prem-stat-lbl">🟠 High Risk</div>
                </div>""", unsafe_allow_html=True)
            with rc3:
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#F59E0B">{medium}</div>
                    <div class="prem-stat-lbl">🟡 Medium Risk</div>
                </div>""", unsafe_allow_html=True)
            with rc4:
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#6366F1">{len(risk_zones)}</div>
                    <div class="prem-stat-lbl">📊 Total Zones</div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="prem-section-header">Zone Details</div>', unsafe_allow_html=True)

            RISK_COLORS = {
                "critical": "#EF4444",
                "high":     "#F97316",
                "medium":   "#F59E0B",
                "low":      "#10B981",
            }
            RISK_BADGE = {
                "critical": "prem-badge-high",
                "high":     "prem-badge-high",
                "medium":   "prem-badge-medium",
                "low":      "prem-badge-low",
            }

            for zone in risk_zones[:10]:
                risk_level  = zone.get("risk_level", "low")
                risk_score  = zone.get("risk_score", 0)
                risk_color  = RISK_COLORS.get(risk_level, "#10B981")
                badge_cls   = RISK_BADGE.get(risk_level, "prem-badge-low")
                location    = zone.get("location", "Unknown Area")
                action      = zone.get("action_required", "Monitor situation")
                trend       = zone.get("trend", "stable").title()
                top_cat     = zone.get("top_category", "N/A").title()
                predicted_d = zone.get("predicted_next_complaint_days", "N/A")

                # Card rendered OUTSIDE expander — HTML works here
                st.markdown(f"""
                <div class="prem-complaint-item" style="border-left-color:{risk_color};">
                    <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px;">
                        <span class="prem-complaint-id">📍 {html.escape(location)}</span>
                        <span class="prem-badge {badge_cls}">{risk_level.upper()}</span>
                        <span class="prem-chip">Score: {risk_score}</span>
                        <span style="margin-left:auto;font-size:0.72rem;color:#5A6A85;">
                            Trend: {html.escape(trend)}
                        </span>
                    </div>
                    <div class="prem-complaint-meta">
                        <span>📋 Total: <strong>{zone.get('complaint_count',0)}</strong></span>
                        <span>🕐 Recent 7d: <strong>{zone.get('recent_count',0)}</strong></span>
                        <span>📂 Top: <strong>{html.escape(top_cat)}</strong></span>
                        <span>🔮 Next in: <strong>{html.escape(str(predicted_d))} days</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Expander with details — pure native Streamlit inside
                with st.expander(f"🔍 View details — {location}", expanded=False):
                    st.write(f"**🎯 Action Required:** {action}")
                    st.divider()

                    d1, d2 = st.columns(2)
                    with d1:
                        st.caption("📊 Statistics")
                        st.write(f"• Total Complaints: **{zone.get('complaint_count', 0)}**")
                        st.write(f"• Recent (7 days): **{zone.get('recent_count', 0)}**")
                        st.write(f"• Top Category: **{top_cat}**")
                        st.write(f"• Predicted Next: **{predicted_d} days**")
                        st.write(f"• Trend: **{trend}**")

                    with d2:
                        st.caption("📂 Category Breakdown")
                        categories = zone.get("category_distribution", {})
                        if categories:
                            for cat, count in sorted(categories.items(),
                                                     key=lambda x: -x[1])[:5]:
                                st.write(f"• {cat.title()}: **{count}** complaints")
                        else:
                            st.write("No category data.")

                    st.divider()
                    st.caption("⚡ Priority Distribution")
                    priorities = zone.get("priority_distribution", {})
                    pc1, pc2, pc3 = st.columns(3)
                    pc1.metric("🔴 High",   priorities.get("high",   0))
                    pc2.metric("🟠 Medium", priorities.get("medium", 0))
                    pc3.metric("🟢 Low",    priorities.get("low",    0))

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 2 — WORKLOAD FORECAST
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="prem-section-header">Department Workload Forecast</div>',
                    unsafe_allow_html=True)
        st.caption("Predicted complaint volume for each department over the next 7 days")

        forecast_data = api("get", "/admin/predictive/workload-forecast",
                            params={"days_ahead": 7})
        forecast = forecast_data.get("forecast", []) if isinstance(forecast_data, dict) else []

        if not forecast:
            st.markdown("""
            <div class="prem-empty-state">
                <span class="prem-empty-icon">📊</span>
                <div class="prem-empty-title">No forecast data available</div>
                <div class="prem-empty-sub">More historical complaints are needed to generate forecasts.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Summary header metrics
            total_predicted = sum(d.get("predicted_complaints_7d", 0) for d in forecast)
            total_backlog   = sum(d.get("current_backlog", 0) for d in forecast)
            high_load       = [d for d in forecast if d.get("predicted_complaints_7d", 0) > 25]

            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#6366F1">{total_predicted}</div>
                    <div class="prem-stat-lbl">Total Forecast (7d)</div>
                </div>""", unsafe_allow_html=True)
            with fc2:
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#F59E0B">{total_backlog}</div>
                    <div class="prem-stat-lbl">Current Backlog</div>
                </div>""", unsafe_allow_html=True)
            with fc3:
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#EF4444">{len(high_load)}</div>
                    <div class="prem-stat-lbl">High-Load Depts</div>
                </div>""", unsafe_allow_html=True)

            if high_load:
                names = ", ".join(d.get("department_name", "?") for d in high_load)
                st.warning(f"📢 **Recommendation:** {len(high_load)} department(s) facing high load: **{names}**. Consider temporary staffing adjustments.")

            st.markdown('<div class="prem-section-header">Forecast by Department</div>',
                        unsafe_allow_html=True)

            for dept in sorted(forecast,
                                key=lambda x: x.get("predicted_complaints_7d", 0),
                                reverse=True):
                predicted = dept.get("predicted_complaints_7d", 0)
                daily_avg = dept.get("daily_avg_complaints", 0)
                backlog   = dept.get("current_backlog", 0)
                res_rate  = min(dept.get("resolution_rate", 0), 100)
                dept_name = dept.get("department_name", "Unknown")

                if predicted > 30:
                    border_color = "#EF4444"
                    badge_cls    = "prem-badge-high"
                    status_text  = "⚠️ High workload expected"
                elif predicted > 15:
                    border_color = "#F59E0B"
                    badge_cls    = "prem-badge-medium"
                    status_text  = "📈 Moderate increase expected"
                else:
                    border_color = "#10B981"
                    badge_cls    = "prem-badge-low"
                    status_text  = "✅ Normal workload"

                bar_pct = min(int(predicted / 50 * 100), 100)
                bar_color = (
                    "linear-gradient(90deg,#EF4444,#F97316)" if predicted > 30
                    else "linear-gradient(90deg,#F59E0B,#EAB308)" if predicted > 15
                    else "linear-gradient(90deg,#6366F1,#10B981)"
                )

                st.markdown(f"""
                <div class="prem-lb-card" style="border-left:4px solid {border_color};">
                    <div class="prem-lb-rank"
                         style="font-size:2rem;color:{border_color};">
                        {predicted}
                    </div>
                    <div class="prem-lb-info">
                        <div class="prem-lb-name">
                            🏢 {html.escape(dept_name)}
                            <span class="prem-badge {badge_cls}">{status_text}</span>
                        </div>
                        <div class="prem-lb-stats">
                            <div class="prem-lb-stat-item">
                                <div class="prem-lb-stat-lbl">📅 Daily Avg</div>
                                <div class="prem-lb-stat-val">{daily_avg}</div>
                            </div>
                            <div class="prem-lb-stat-item">
                                <div class="prem-lb-stat-lbl">📋 Backlog</div>
                                <div class="prem-lb-stat-val">{backlog}</div>
                            </div>
                            <div class="prem-lb-stat-item">
                                <div class="prem-lb-stat-lbl">📈 Resolution</div>
                                <div class="prem-lb-stat-val">{res_rate}%</div>
                            </div>
                            <div class="prem-lb-stat-item">
                                <div class="prem-lb-stat-lbl">🔮 7d Forecast</div>
                                <div class="prem-lb-stat-val">{predicted}</div>
                            </div>
                        </div>
                        <div class="prem-prog-wrap" style="height:12px;margin-top:8px;">
                            <div class="prem-prog-fill"
                                 style="width:{bar_pct}%;background:{bar_color};height:12px;">
                                <span class="prem-prog-text" style="font-size:0.58rem;">{bar_pct}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 3 — HOTSPOTS MAP
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="prem-section-header">Complaint Hotspots Map</div>',
                    unsafe_allow_html=True)
        st.caption("Geographic clusters of repeated complaints — circle size = complaint volume")

        hotspots_data = api("get", "/admin/predictive/hotspots", params={"top_n": 10})
        hotspots = hotspots_data.get("hotspots", []) if isinstance(hotspots_data, dict) else []

        if not hotspots:
            st.markdown("""
            <div class="prem-empty-state">
                <span class="prem-empty-icon">🗺️</span>
                <div class="prem-empty-title">No hotspots detected</div>
                <div class="prem-empty-sub">Add more geotagged complaints for hotspot mapping.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            hm1, hm2, hm3 = st.columns(3)
            with hm1:
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#EF4444">{len(hotspots)}</div>
                    <div class="prem-stat-lbl">🔥 Active Hotspots</div>
                </div>""", unsafe_allow_html=True)
            with hm2:
                total_comp = sum(h.get("complaint_count", 0) for h in hotspots)
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#6366F1">{total_comp}</div>
                    <div class="prem-stat-lbl">📊 Total Complaints</div>
                </div>""", unsafe_allow_html=True)
            with hm3:
                top_cat = hotspots[0].get("top_category", "N/A").title() if hotspots else "N/A"
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="font-size:1.2rem;color:#F59E0B">
                        {html.escape(top_cat)}
                    </div>
                    <div class="prem-stat-lbl">🎯 Top Category</div>
                </div>""", unsafe_allow_html=True)

            # Build Leaflet markers
            markers_js = []
            for h in hotspots:
                lat = h.get("latitude")
                lon = h.get("longitude")
                if lat and lon:
                    count    = h.get("complaint_count", 0)
                    top_c    = h.get("top_category", "unknown").title()
                    risk     = min(count * 1.5, 10)
                    color    = "#dc2626" if risk > 7 else "#d97706" if risk > 4 else "#eab308"
                    radius   = min(12 + count, 28)
                    safe_cat = top_c.replace("'", "\\'")
                    markers_js.append(f"""
                    L.circleMarker([{lat}, {lon}], {{
                        radius: {radius},
                        fillColor: '{color}',
                        color: 'white',
                        weight: 2,
                        fillOpacity: 0.85,
                        opacity: 1
                    }}).addTo(map).bindPopup(
                        '<b>{safe_cat}</b><br>{count} complaints<br>Risk score: {risk:.1f}'
                    );""")

            if markers_js:
                st.components.v1.html(f"""
                <link rel="stylesheet"
                      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                <div id="hotspot-map"
                     style="height:460px;border-radius:18px;overflow:hidden;
                            border:1.5px solid #CBD5E9;box-shadow:0 4px 20px rgba(11,20,40,0.10);">
                </div>
                <script>
                    var map = L.map('hotspot-map').setView([23.2599, 77.4126], 11);
                    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                        maxZoom: 19,
                        attribution: '© OpenStreetMap'
                    }}).addTo(map);
                    {''.join(markers_js)}
                </script>
                """, height=490)
            else:
                st.info("No geotagged complaints available for mapping.")

            # Hotspot detail cards
            st.markdown('<div class="prem-section-header">Hotspot Details</div>',
                        unsafe_allow_html=True)
            for h in hotspots[:5]:
                count     = h.get("complaint_count", 0)
                risk_s    = h.get("risk_score", 0)
                cat       = h.get("top_category", "Unknown").title()
                risk_clr  = (
                    "#EF4444" if risk_s > 7
                    else "#F97316" if risk_s > 4
                    else "#F59E0B"
                )
                badge_cls = "prem-badge-high" if risk_s > 4 else "prem-badge-medium"
                st.markdown(f"""
                <div class="prem-complaint-item" style="border-left-color:{risk_clr};">
                    <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                        <span class="prem-complaint-id">📍 {html.escape(cat)}</span>
                        <span class="prem-badge {badge_cls}">Risk {risk_s:.1f}</span>
                        <span style="margin-left:auto;font-size:0.78rem;font-weight:600;">
                            {count} complaints
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 4 — COMPLAINT TRENDS
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="prem-section-header">Complaint Trends Analysis</div>',
                    unsafe_allow_html=True)

        trends_data = api("get", "/admin/predictive/trends", params={"days_back": 30})
        trends = trends_data.get("trends", {}) if isinstance(trends_data, dict) else {}

        if not trends:
            st.markdown("""
            <div class="prem-empty-state">
                <span class="prem-empty-icon">📈</span>
                <div class="prem-empty-title">Not enough data for trend analysis</div>
                <div class="prem-empty-sub">Collect more complaints over time to see patterns.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Summary
            t1, t2 = st.columns(2)
            with t1:
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#6366F1">
                        {trends.get('total_complaints', 0)}
                    </div>
                    <div class="prem-stat-lbl">Total Complaints (30d)</div>
                </div>""", unsafe_allow_html=True)
            with t2:
                st.markdown(f"""
                <div class="prem-stat-card">
                    <div class="prem-stat-num" style="color:#10B981">
                        {trends.get('period_days', 30)}
                    </div>
                    <div class="prem-stat-lbl">Analysis Period (days)</div>
                </div>""", unsafe_allow_html=True)

            # ── Category distribution bars ────────────────────────────────────
            categories = trends.get("category_trend", {})
            if categories:
                st.markdown('<div class="prem-section-header">Category Distribution</div>',
                            unsafe_allow_html=True)
                max_count  = max(categories.values()) if categories else 1
                GRAD_PAIRS = [
                    "linear-gradient(90deg,#6366F1,#818CF8)",
                    "linear-gradient(90deg,#F59E0B,#EAB308)",
                    "linear-gradient(90deg,#10B981,#059669)",
                    "linear-gradient(90deg,#EF4444,#F97316)",
                    "linear-gradient(90deg,#0EA5E9,#22D3EE)",
                    "linear-gradient(90deg,#8B5CF6,#A78BFA)",
                ]
                for i, (cat, count) in enumerate(
                    sorted(categories.items(), key=lambda x: -x[1])
                ):
                    pct   = round(count / max_count * 100, 1)
                    grad  = GRAD_PAIRS[i % len(GRAD_PAIRS)]
                    total = trends.get("total_complaints", 1)
                    share = round(count / max(total, 1) * 100, 1)
                    st.markdown(f"""
                    <div style="margin:10px 0;">
                        <div style="display:flex;justify-content:space-between;
                                    font-size:0.82rem;font-weight:600;margin-bottom:5px;">
                            <span>{html.escape(cat.title())}</span>
                            <span class="prem-chip">{count} &nbsp;·&nbsp; {share}%</span>
                        </div>
                        <div class="prem-prog-wrap" style="height:16px;">
                            <div class="prem-prog-fill"
                                 style="width:{pct}%;background:{grad};height:16px;">
                                <span class="prem-prog-text" style="font-size:0.62rem;">
                                    {pct:.0f}%
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Top locations ─────────────────────────────────────────────────
            locations = trends.get("locations", {})
            if locations:
                st.markdown('<div class="prem-section-header">Top Complaint Locations</div>',
                            unsafe_allow_html=True)
                top_locs = sorted(
                    locations.items(),
                    key=lambda x: x[1].get("count", 0),
                    reverse=True
                )[:8]

                for loc_name, loc_data in top_locs:
                    count = loc_data.get("count", 0)
                    cats  = loc_data.get("categories", {})
                    top_c = (
                        sorted(cats.items(), key=lambda x: -x[1])[0][0].title()
                        if cats else "N/A"
                    )
                    max_loc = max(
                        (v.get("count", 0) for _, v in top_locs), default=1
                    )
                    pct = round(count / max(max_loc, 1) * 100, 1)

                    st.markdown(f"""
                    <div class="prem-complaint-item">
                        <div style="display:flex;justify-content:space-between;
                                    align-items:center;margin-bottom:6px;">
                            <span class="prem-complaint-id">📍 {html.escape(loc_name)}</span>
                            <span class="prem-chip">{count} complaints</span>
                        </div>
                        <div class="prem-complaint-meta" style="margin-bottom:8px;">
                            <span>🏷️ Top category: <strong>{html.escape(top_c)}</strong></span>
                        </div>
                        <div class="prem-prog-wrap" style="height:10px;">
                            <div class="prem-prog-fill"
                                 style="width:{pct}%;
                                        background:linear-gradient(90deg,#6366F1,#10B981);
                                        height:10px;">
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── TIPS BAR ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="prem-tip-bar">
        <span class="prem-tip-icon">💡</span>
        <span class="prem-tip-text">
            <strong>Tip:</strong> Predictive analytics uses the last 30 days of complaint data.
            More historical data leads to more accurate risk predictions and workload forecasts.
        </span>
    </div>
    """, unsafe_allow_html=True)

# Add to frontend/app.py

# Add this function after stars_html() function

def format_sla_display(complaint):
    _apply_layout("user")
    """Format SLA information for display"""
    if not complaint.get('sla_deadline'):
        return None
    
    try:
        from datetime import datetime
        sla_deadline = datetime.strptime(complaint['sla_deadline'], "%d %b %Y, %I:%M %p")
        now = datetime.now()
        
        if complaint.get('status') in ['resolved', 'closed']:
            if complaint.get('SLA_breached'):
                return {'status': 'breached', 'text': '⚠️ SLA Breached', 'color': '#dc2626'}
            else:
                return {'status': 'met', 'text': '✅ SLA Met', 'color': '#10b981'}
        
        # Still pending/in_progress
        if sla_deadline < now:
            overdue_hours = (now - sla_deadline).total_seconds() / 3600
            return {
                'status': 'overdue', 
                'text': f'⏰ OVERDUE by {overdue_hours:.0f}h', 
                'color': '#dc2626',
                'is_overdue': True,
                'overdue_hours': overdue_hours
            }
        else:
            remaining = sla_deadline - now
            remaining_hours = remaining.total_seconds() / 3600
            if remaining_hours < 6:
                color = '#dc2626'
                status_text = '🔴 URGENT'
            elif remaining_hours < 24:
                color = '#d97706'
                status_text = '⚠️ Soon'
            else:
                color = '#10b981'
                status_text = '✅ On Track'
            
            return {
                'status': 'active',
                'text': f'⏱️ {remaining_hours:.0f}h remaining',
                'color': color,
                'status_text': status_text,
                'deadline': sla_deadline.strftime("%d %b, %I:%M %p")
            }
    except Exception as e:
        return None
def render_simple_steps(complaint):
    steps = ["submitted", "assigned", "in_progress", "resolved"]
    current = complaint.get("status", "pending")
    status_map = {"pending":"submitted","assigned":"assigned","in_progress":"in_progress","resolved":"resolved"}
    current_step = status_map.get(current, "submitted")
    active_index = steps.index(current_step) if current_step in steps else 0
    html = '<div style="display: flex; gap: 8px; margin: 12px 0;">'
    for i, s in enumerate(steps):
        icon = "✅" if i < active_index else "⏳" if i == active_index else "○"
        color = "#10b981" if i < active_index else "#3b82f6" if i == active_index else "#d1d5db"
        html += f'<div style="flex:1; text-align:center;"><div style="color:{color};">{icon}</div><div style="font-size:0.7rem;">{s.replace("_"," ").title()}</div></div>'
        if i < len(steps)-1:
            html += '<div style="flex:0.5; text-align:center;">→</div>'
    html += '</div>'
    return html
   
def pg_sla_management():
    _apply_layout("user")
    """SLA Management Dashboard — premium prem-* design, no HTML inside expanders."""

    DEFAULT_SLA = {

        "water":       24,

        "electricity": 24,

        "road":        72,

        "waste":       48,

        "drainage":    48,

        "health":      36,

        "other":       72,
    }

    # ─────────────────────────────────────────────
    # SAFE DYNAMIC SLA HELPER
    # ─────────────────────────────────────────────

    def get_default_sla(category):

        category = str(category).lower().strip()

        # Smart automatic SLA mapping
        AUTO_SLA = {

            "cyber":     12,

            "internet":  12,

            "telecom":   18,

            "police":     6,

            "fire":       2,

            "health":    12,

            "transport": 24,

            "bank":      24,

            "finance":   24,

            "education": 48,

            "housing":   72,
        }

        for key, hrs in AUTO_SLA.items():

            if key in category:

                return hrs

        # Safe fallback
        return DEFAULT_SLA.get(

            category,

            48
        )

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="prem-hero">
        <div class="prem-hero-title">⏱️ Smart SLA Tracking</div>
        <div class="prem-hero-sub">
            Service Level Agreement monitoring and compliance tracking across all departments
        </div>
        <div class="prem-hero-stats">
            <div class="prem-hstat h-blue">
                <div class="prem-hstat-num">⏰</div>
                <div class="prem-hstat-lbl">Overdue</div>
            </div>
            <div class="prem-hstat h-green">
                <div class="prem-hstat-num">📊</div>
                <div class="prem-hstat-lbl">By Category</div>
            </div>
            <div class="prem-hstat h-amber">
                <div class="prem-hstat-num">⚙️</div>
                <div class="prem-hstat-lbl">Policies</div>
            </div>
            <div class="prem-hstat">
                <div class="prem-hstat-num">📈</div>
                <div class="prem-hstat-lbl">Performance</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── COMPLIANCE STATS ──────────────────────────────────────────────────────
    stats      = api("get", "/admin/sla/compliance-stats")
    stats_data = stats if isinstance(stats, dict) else {}

    total_resolved  = stats_data.get("total_resolved", 0)
    met_sla         = stats_data.get("met_sla", 0)
    breached_sla    = stats_data.get("breached_sla", 0)
    compliance_rate = min(stats_data.get("overall_compliance_rate", 0), 100)

    compliance_color = (
        "#10B981" if compliance_rate >= 80
        else "#F59E0B" if compliance_rate >= 60
        else "#EF4444"
    )
    bar_gradient = (
        "linear-gradient(90deg,#6366F1,#10B981)" if compliance_rate >= 80
        else "linear-gradient(90deg,#F59E0B,#EAB308)" if compliance_rate >= 60
        else "linear-gradient(90deg,#EF4444,#F97316)"
    )
    compliance_badge = (
        "prem-badge-resolved" if compliance_rate >= 80
        else "prem-badge-medium" if compliance_rate >= 60
        else "prem-badge-high"
    )
    compliance_label = (
        "✅ Good" if compliance_rate >= 80
        else "⚠️ Needs Improvement"
        if compliance_rate >= 60 else "🔴 Critical"
    )

    st.markdown('<div class="prem-section-header">Compliance Overview</div>',
                unsafe_allow_html=True)

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(f"""
        <div class="prem-stat-card">
            <div class="prem-stat-num" style="color:#6366F1">{total_resolved}</div>
            <div class="prem-stat-lbl">Total Resolved</div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
        <div class="prem-stat-card">
            <div class="prem-stat-num" style="color:#10B981">{met_sla}</div>
            <div class="prem-stat-lbl">✅ SLA Met</div>
        </div>""", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""
        <div class="prem-stat-card">
            <div class="prem-stat-num" style="color:#EF4444">{breached_sla}</div>
            <div class="prem-stat-lbl">❌ SLA Breached</div>
        </div>""", unsafe_allow_html=True)
    with sc4:
        st.markdown(f"""
        <div class="prem-stat-card">
            <div class="prem-stat-num" style="color:{compliance_color}">{compliance_rate}%</div>
            <div class="prem-stat-lbl">Compliance Rate</div>
        </div>""", unsafe_allow_html=True)

    # Overall compliance progress bar
    st.markdown(f"""
    <div class="prem-card" style="padding:16px 22px; margin:4px 0 8px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-weight:700; font-size:0.88rem;">📊 Overall SLA Compliance</span>
            <span class="prem-badge {compliance_badge}">{compliance_label}</span>
        </div>
        <div class="prem-prog-wrap">
            <div class="prem-prog-fill" style="width:{compliance_rate}%; background:{bar_gradient};">
                <span class="prem-prog-text">{compliance_rate}%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "⏰ Overdue Complaints",
        "📊 Category SLA",
        "⚙️ SLA Policies",
        "📈 Performance",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 1 — OVERDUE COMPLAINTS
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="prem-section-header">⏰ Overdue Complaints</div>',
                    unsafe_allow_html=True)
        st.caption("Complaints that have exceeded their SLA deadline")

        overdue_data = api("get", "/admin/sla/overdue-complaints")
        overdue      = overdue_data.get("complaints", []) if isinstance(overdue_data, dict) else []

        if not overdue:
            st.markdown("""
            <div class="prem-empty-state">
                <span class="prem-empty-icon">✅</span>
                <div class="prem-empty-title">No overdue complaints!</div>
                <div class="prem-empty-sub">All complaints are within their SLA deadlines.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="prem-notif-bar">'
                f'<div class="prem-notif-bar-dot"></div>'
                f'<div class="prem-notif-bar-text">'
                f'{len(overdue)} complaint(s) have breached their SLA — immediate action required.'
                f'</div>'
                f'<span class="prem-notif-bar-badge">{len(overdue)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            for c in overdue:
                cid           = c.get("complaint_id", "N/A")
                category      = c.get("category", "other").title()
                overdue_hours = c.get("overdue_hours", 0)
                description   = c.get("description", "")
                location      = c.get("location", "N/A")
                user_name     = c.get("user_name", "Unknown")
                department    = c.get("department", "N/A")
                sla_deadline  = c.get("sla_deadline", "N/A")
                priority      = c.get("priority", "medium")
                p_emoji       = {"high": "🔴", "medium": "🟠", "low": "🟢"}.get(priority, "⚪")

                # Card rendered outside expander — HTML works here
                st.markdown(f"""
                <div class="prem-complaint-item" style="border-left-color:#EF4444;">
                    <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;
                                margin-bottom:10px;">
                        <span class="prem-complaint-id">#{html.escape(str(cid))}</span>
                        <span class="prem-badge prem-badge-high">🚨 OVERDUE</span>
                        <span class="prem-badge prem-badge-medium">{p_emoji} {priority.title()}</span>
                        <span style="margin-left:auto;" class="prem-chip">
                            ⏰ {overdue_hours:.0f}h overdue
                        </span>
                    </div>
                    <div class="prem-complaint-title">{html.escape(category)}</div>
                    <div class="prem-complaint-desc">
                        {html.escape(description[:120])}{"…" if len(description) > 120 else ""}
                    </div>
                    <div class="prem-complaint-meta">
                        <span>👤 {html.escape(str(user_name))}</span>
                        <span>🏢 {html.escape(str(department))}</span>
                        <span>📍 {html.escape(str(location))}</span>
                        <span>📅 SLA: {html.escape(str(sla_deadline))}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Expander — pure native Streamlit only inside
                with st.expander(f"🔍 Actions — #{cid}", expanded=True):
                    d1, d2 = st.columns([3, 1])
                    with d1:
                        st.caption("Complaint Details")
                        st.write(f"**Description:** {description}")
                        st.write(f"**Location:** {location}")
                        st.write(f"**Citizen:** {user_name}")
                        st.write(f"**Department:** {department}")
                        st.write(f"**SLA Deadline:** {sla_deadline}")
                    with d2:
                        st.error(f"⏰ OVERDUE\nby **{overdue_hours:.0f}h**")
                        st.caption(f"Deadline: {sla_deadline}")

                    if st.button("🚨 Flag as Urgent",
                                 key=f"urgent_{c.get('id', cid)}",
                                 use_container_width=True):
                        st.warning(f"Urgent action flagged for complaint #{cid}")

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 2 — CATEGORY SLA COMPLIANCE
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="prem-section-header">Category-wise SLA Compliance</div>',
                    unsafe_allow_html=True)

        category_stats = stats_data.get("category_stats", {})
        if not category_stats:
            st.markdown("""
            <div class="prem-empty-state">
                <span class="prem-empty-icon">📊</span>
                <div class="prem-empty-title">No category data yet</div>
                <div class="prem-empty-sub">Resolve more complaints to see per-category SLA stats.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for cat, data in sorted(
                category_stats.items(),
                key=lambda x: x[1].get("compliance_rate", 0),
                reverse=True,
            ):
                compliance  = min(data.get("compliance_rate", 0), 100)
                met         = data.get("met", 0)
                breached    = data.get("breached", 0)
                total       = data.get("total", 0)

                if compliance >= 80:
                    bar_grad  = "linear-gradient(90deg,#6366F1,#10B981)"
                    badge_cls = "prem-badge-resolved"
                    badge_lbl = "✅ Good"
                elif compliance >= 60:
                    bar_grad  = "linear-gradient(90deg,#F59E0B,#EAB308)"
                    badge_cls = "prem-badge-medium"
                    badge_lbl = "⚠️ Moderate"
                else:
                    bar_grad  = "linear-gradient(90deg,#EF4444,#F97316)"
                    badge_cls = "prem-badge-high"
                    badge_lbl = "🔴 Poor"

                st.markdown(f"""
                <div class="prem-card" style="padding:16px 20px; margin:8px 0;">
                    <div style="display:flex;justify-content:space-between;
                                align-items:center;margin-bottom:8px;">
                        <span style="font-weight:700;font-size:0.90rem;">
                            {html.escape(cat.title())}
                        </span>
                        <div style="display:flex;gap:8px;align-items:center;">
                            <span class="prem-chip">{compliance}%</span>
                            <span class="prem-badge {badge_cls}">{badge_lbl}</span>
                        </div>
                    </div>
                    <div class="prem-prog-wrap" style="height:14px;margin-bottom:10px;">
                        <div class="prem-prog-fill"
                             style="width:{compliance}%;background:{bar_grad};height:14px;">
                            <span class="prem-prog-text" style="font-size:0.60rem;">
                                {compliance:.0f}%
                            </span>
                        </div>
                    </div>
                    <div class="prem-complaint-meta">
                        <span>✅ Met: <strong>{met}</strong></span>
                        <span>❌ Breached: <strong>{breached}</strong></span>
                        <span>📊 Total: <strong>{total}</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════���═══════════════════════════
    #  TAB 3 — SLA POLICIES
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="prem-section-header">SLA Policy Configuration</div>',
                    unsafe_allow_html=True)
        st.caption("Set resolution time expectations per complaint category")

        policies      = api("get", "/admin/sla/policies")
        policies_list = policies if isinstance(policies, list) else []

        CAT_ICONS = {

            "water":       "💧",

            "electricity": "⚡",

            "road":        "🛣️",

            "waste":       "🗑️",

            "drainage":    "🚰",

            "health":      "🏥",

            "other":       "📋",
        }

        # ─────────────────────────────────────────────
        # SAFE DYNAMIC CATEGORY ICON
        # ─────────────────────────────────────────────

        def get_cat_icon(category):

            category = str(category).lower().strip()

            # Smart automatic icon detection
            AUTO_ICONS = {

                "cyber":     "💻",

                "internet":  "🌐",

                "telecom":   "📡",

                "transport": "🚌",

                "police":    "🚓",

                "fire":      "🔥",

                "tourism":   "✈️",

                "bank":      "🏦",

                "finance":   "💰",

                "education": "🎓",

                "housing":   "🏠",

                "electric":  "⚡",

                "water":     "💧",

                "drain":     "🚰",

                "health":    "🏥",

                "waste":     "🗑️",

                "road":      "🛣️",
            }

            # Auto match keywords
            for key, icon in AUTO_ICONS.items():

                if key in category:

                    return icon

            # Exact match fallback
            return CAT_ICONS.get(

                category,

                "📌"
            )

        for category, default_hours in DEFAULT_SLA.items():
            existing      = next(
                (p for p in policies_list if p.get("category") == category), None
            )
            current_hours = existing.get("hours_to_resolve") if existing else default_hours
            icon          = CAT_ICONS.get(category, "📋")

            st.markdown(f"""
            <div class="prem-card" style="padding:14px 20px; margin:6px 0;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
                    <span style="font-size:1.2rem;">{icon}</span>
                    <span style="font-weight:700;font-size:0.92rem;">
                        {html.escape(category.title())}
                    </span>
                    <span class="prem-chip" style="margin-left:auto;">
                        Default: {default_hours}h
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            pc1, pc2, pc3 = st.columns([3, 1, 1])
            with pc1:
                st.caption(f"Resolution window for {category.title()} complaints")
            with pc2:
                new_hours = st.number_input(
                    "Hours",
                    min_value=1,
                    max_value=168,
                    value=int(current_hours),
                    key=f"sla_{category}",
                    label_visibility="collapsed",
                )
            with pc3:
                if st.button("💾 Save", key=f"update_{category}",
                             use_container_width=True):
                    resp = api("post", "/admin/sla/policies", json={
                        "category":            category,
                        "hours_to_resolve":    new_hours,
                        "priority_multiplier": 1.0,
                    })
                    if resp.get("success"):
                        st.success(f"✅ {category.title()} SLA → {new_hours}h")
                        st.rerun()
                    else:
                        st.error("Update failed. Please try again.")

        st.markdown("""
        <div class="prem-tip-bar">
            <span class="prem-tip-icon">⚖️</span>
            <span class="prem-tip-text">
                <strong>SLA Rules:</strong>
                Water &amp; Electricity: 24h (critical infrastructure) ·
                Road/Drainage: 48–72h ·
                High-priority complaints automatically get a 30% faster SLA target ·
                Overdue complaints are flagged in red across all dashboards.
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 4 — PERFORMANCE TRENDS
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="prem-section-header">SLA Performance Trends</div>',
                    unsafe_allow_html=True)

        all_complaints  = api("get", "/complaints/all")
        complaints_list = all_complaints if isinstance(all_complaints, list) else []

        if not complaints_list:
            st.markdown("""
            <div class="prem-empty-state">
                <span class="prem-empty-icon">📈</span>
                <div class="prem-empty-title">Not enough data yet</div>
                <div class="prem-empty-sub">
                    Resolve more complaints to generate performance trend analysis.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Build resolution time buckets per category
            resolution_times: dict[str, list] = {}
            for c in complaints_list:
                if (c.get("time_to_resolve_hours")
                        and c.get("status") in ("resolved", "closed")):
                    cat = c.get("category", "other")
                    resolution_times.setdefault(cat, []).append(
                        c.get("time_to_resolve_hours")
                    )

            if not resolution_times:
                st.info("No resolved complaints with timing data found.")
            else:
                # Summary stat cards
                within_sla = sum(
                    1 for cat, times in resolution_times.items()
                    if (sum(times) / len(times)) <= DEFAULT_SLA.get(cat, 72)
                )
                total_cats = len(resolution_times)

                ps1, ps2, ps3 = st.columns(3)
                with ps1:
                    st.markdown(f"""
                    <div class="prem-stat-card">
                        <div class="prem-stat-num" style="color:#6366F1">{total_cats}</div>
                        <div class="prem-stat-lbl">Categories Tracked</div>
                    </div>""", unsafe_allow_html=True)
                with ps2:
                    st.markdown(f"""
                    <div class="prem-stat-card">
                        <div class="prem-stat-num" style="color:#10B981">{within_sla}</div>
                        <div class="prem-stat-lbl">✅ Within SLA Target</div>
                    </div>""", unsafe_allow_html=True)
                with ps3:
                    exceeding = total_cats - within_sla
                    st.markdown(f"""
                    <div class="prem-stat-card">
                        <div class="prem-stat-num" style="color:#EF4444">{exceeding}</div>
                        <div class="prem-stat-lbl">❌ Exceeding Target</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(
                    '<div class="prem-section-header">Average Resolution Time by Category</div>',
                    unsafe_allow_html=True,
                )

                # Sort worst performers first
                sorted_cats = sorted(
                    resolution_times.items(),
                    key=lambda x: (sum(x[1]) / len(x[1])) / DEFAULT_SLA.get(x[0], 72),
                    reverse=True,
                )

                for cat, times in sorted_cats:
                    avg_time = sum(times) / len(times)
                    target   = DEFAULT_SLA.get(cat, 72)
                    ratio    = avg_time / max(target, 1)
                    bar_pct  = min(int(ratio * 100), 100)
                    within   = avg_time <= target
                    icon     = CAT_ICONS.get(cat, "📋") if "CAT_ICONS" in dir() else "📋"

                    if within:
                        bar_grad  = "linear-gradient(90deg,#6366F1,#10B981)"
                        badge_cls = "prem-badge-resolved"
                        status    = "✅ Within SLA"
                    else:
                        bar_grad  = "linear-gradient(90deg,#EF4444,#F97316)"
                        badge_cls = "prem-badge-high"
                        status    = "❌ Exceeds SLA"

                    st.markdown(f"""
                    <div class="prem-card" style="padding:16px 20px; margin:8px 0;">
                        <div style="display:flex;justify-content:space-between;
                                    align-items:center;margin-bottom:8px;">
                            <span style="font-weight:700;font-size:0.90rem;">
                                {html.escape(cat.title())}
                            </span>
                            <div style="display:flex;gap:8px;align-items:center;">
                                <span class="prem-chip">{avg_time:.1f}h avg</span>
                                <span class="prem-badge {badge_cls}">{status}</span>
                            </div>
                        </div>
                        <div class="prem-prog-wrap" style="height:14px;margin-bottom:8px;">
                            <div class="prem-prog-fill"
                                 style="width:{bar_pct}%;background:{bar_grad};height:14px;">
                                <span class="prem-prog-text" style="font-size:0.60rem;">
                                    {bar_pct}%
                                </span>
                            </div>
                        </div>
                        <div class="prem-complaint-meta">
                            <span>🎯 Target: <strong>{target}h</strong></span>
                            <span>⏱️ Actual: <strong>{avg_time:.1f}h</strong></span>
                            <span>📊 Samples: <strong>{len(times)}</strong></span>
                            <span>{"✅ Saving " + str(round(target-avg_time,1)) + "h"
                                   if within
                                   else "⚠️ Over by " + str(round(avg_time-target,1)) + "h"}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("""
        <div class="prem-tip-bar">
            <span class="prem-tip-icon">💡</span>
            <span class="prem-tip-text">
                <strong>Tip:</strong> Track average resolution time vs SLA target.
                Categories shown in red need attention — consider reassigning staff
                or adjusting SLA targets in the Policies tab.
            </span>
        </div>
        """, unsafe_allow_html=True)
# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
render_sidebar()
route()
