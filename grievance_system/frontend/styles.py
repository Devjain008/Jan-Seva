
def get_css(dark_mode=False):
    # ── colour tokens ────────────────────────────────────────────────────────
    if dark_mode:
        bg         = "#0B1220"
        card_bg    = "#121A2B"
        text       = "#F1F5F9"
        subtext    = "#808A97"
        border     = "#263247"
        input_bg   = "#0F172A"
        sidebar_bg = "#0F172A"
        hover_bg   = "#1E293B"
        stat_bg    = "#121A2B"
        tag_bg     = "#0B3A2A"
        tag_col    = "#6EE7B7"
        accent1    = "#2563EB"
        accent2    = "#0EA5A4"
        accent3    = "#A78BFA"
        a1_glow    = "rgba(37,99,235,0.35)"
        a2_glow    = "rgba(14,165,164,0.30)"
        a1_soft    = "rgba(37,99,235,0.18)"
        a2_soft    = "rgba(20,184,166,0.16)"
        hero_from  = "#1D4ED8"
        hero_mid   = "#2563EB"
        hero_to    = "#0F766E"
    else:
        bg         = "#D9DEE3"
        card_bg    = "#FFFFFF"
        text       = "#0F172A"
        subtext    = "#334155"
        border     = "#E2E8F0"
        input_bg   = "#8E969D"
        sidebar_bg = "#F1F5F9"
        hover_bg   = "#BDC8D7"
        stat_bg    = "#FFFFFF"
        tag_bg     = "#D3DCD8"
        tag_col    = "#065F46"
        accent1    = "#2563EB"
        accent2    = "#0D9488"
        accent3    = "#7C3AED"
        a1_glow    = "rgba(37,99,235,0.24)"
        a2_glow    = "rgba(13,148,136,0.20)"
        a1_soft    = "rgba(37,99,235,0.12)"
        a2_soft    = "rgba(13,148,136,0.10)"
        hero_from  = "#1D4ED8"
        hero_mid   = "#2563EB"
        hero_to    = "#0D9488"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700;800&family=DM+Serif+Display&display=swap');

/* ─── RESET & BASE ────────────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .stApp {{
    background-color: {bg} !important;
    color: {text} !important;
    font-family: 'DM Sans', 'Noto Sans Devanagari', sans-serif !important;
}}
p, span, div, label, small {{
    color: {text};
}}

/* ─── HIDE STREAMLIT CHROME ───────────────────────────────────────────── */
#MainMenu, footer, header, .stDeployButton {{ visibility: hidden !important; display: none !important; }}
.viewerBadge_container__1QSob {{ display: none !important; }}

/* ─── MAIN CONTAINER ──────────────────────────────────────────────────── */
.main .block-container {{
    padding: 1.25rem 1.5rem 2.5rem 1.5rem !important;
    max-width: 980px !important;
    margin: 0 auto !important;
}}

/* ─── SIDEBAR ─────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: {sidebar_bg} !important;
    border-right: 1px solid {border} !important;
}}
section[data-testid="stSidebar"] * {{
    color: {text} !important;
}}
section[data-testid="stSidebar"] .stButton > button {{
    background: {card_bg} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 9px 12px !important;
    transition: all 0.18s !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {hover_bg} !important;
    border-color: {accent1} !important;
    color: {text} !important;
    transform: none !important;
    box-shadow: 0 0 0 2px {a1_soft} !important;
}}

/* ─── BUTTONS (main area) ─────────────────────────────────────────────── */
.stButton > button {{
    background: linear-gradient(135deg, {accent1} 0%, {accent2} 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 16px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    font-family: 'DM Sans', 'Noto Sans Devanagari', sans-serif !important;
    width: 100% !important;
    transition: transform 0.18s, box-shadow 0.18s !important;
    box-shadow: 0 4px 14px {a1_glow} !important;
    cursor: pointer !important;
    letter-spacing: 0.02em !important;
}}
.stButton > button:focus,
.stButton > button:focus-visible {{
    outline: none !important;
    box-shadow: 0 0 0 3px {a1_soft}, 0 4px 14px {a1_glow} !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 20px {a1_glow} !important;
    filter: brightness(1.03) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* ─── INPUTS ──────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stSelectbox > div > div > div {{
    background: {input_bg} !important;
    border: 1px solid {border} !important;
    border-radius: 12px !important;
    color: {text} !important;
    font-family: 'DM Sans', 'Noto Sans Devanagari', sans-serif !important;
}}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: {subtext} !important;
    opacity: 0.8 !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {{
    border-color: {accent1} !important;
    box-shadow: 0 0 0 3px {a1_soft} !important;
    outline: none !important;
}}
label, .stTextInput label, .stTextArea label, .stSelectbox label {{
    color: {text} !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}}
.stMarkdown, .stMarkdown p, .stMarkdown span, .stCaption, .stText {{
    color: {text} !important;
}}

/* ─── TABS ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: {card_bg} !important;
    border-radius: 14px !important;
    padding: 4px !important;
    border: 1.5px solid {border} !important;
    gap: 4px !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    color: {subtext} !important;
    padding: 8px 16px !important;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {accent1}, {accent2}) !important;
    color: #fff !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: transparent !important;
    padding: 12px 0 0 0 !important;
}}

/* ─── EXPANDER ────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {{
    background: {card_bg} !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    color: {text} !important;
    border: 1px solid {border} !important;
    padding: 12px 16px !important;
}}
.streamlit-expanderContent {{
    border: 1px solid {border} !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    background: {card_bg} !important;
    padding: 12px 16px !important;
}}

/* ─── SELECT BOX ──────────────────────────────────────────────────────── */
.stSelectbox div[data-baseweb="select"] > div {{
    background: {input_bg} !important;
    border-color: {border} !important;
    color: {text} !important;
}}
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[data-testid="stWidgetDropdownList"] {{
    background: {card_bg} !important;
    border: 1px solid {border} !important;
}}
div[data-baseweb="option"] {{
    color: {text} !important;
    background: transparent !important;
}}
div[data-baseweb="option"]:hover {{
    background: {hover_bg} !important;
}}

/* ─── PROGRESS BAR ────────────────────────────────────────────────────── */
.stProgress > div > div {{
    background: linear-gradient(90deg, {accent1}, {accent2}) !important;
    border-radius: 6px !important;
}}
.stProgress > div {{
    background: {border} !important;
    border-radius: 6px !important;
}}

/* ─── ALERTS ──────────────────────────────────────────────────────────── */
.stSuccess, .stInfo, .stWarning, .stError {{
    border-radius: 12px !important;
    font-size: 0.86rem !important;
    color: {text} !important;
}}

/* ─── DIVIDER ─────────────────────────────────────────────────────────── */
hr {{ border-color: {border} !important; opacity: 0.7; }}

/* ─── SCROLLBAR ───────────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {border}; border-radius: 3px; }}

/* ══════════════════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════════════════════════════════════════════════ */

/* ─── HERO BANNER ─────────────────────────────────────────────────────── */
.hero {{
    background: linear-gradient(135deg, {hero_from} 0%, {hero_mid} 45%, {hero_to} 100%);
    border-radius: 18px;
    padding: 24px 22px 20px 22px;
    color: #fff;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
}}
.hero::before {{
    content: '';
    position: absolute;
    top: -50%; right: -6%;
    width: 240px; height: 240px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}}
.hero::after {{ content: ''; }}
.hero h1 {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.65rem; font-weight: 400; margin: 0 0 6px 0;
    position: relative; z-index: 1;
    text-shadow: 0 1px 4px rgba(0,0,0,0.25);
}}
.hero p {{
    font-size: 0.88rem; margin: 0; opacity: 0.9;
    position: relative; z-index: 1;
}}

/* ─── CARD ────────────────────────────────────────────────────────────── */
.card {{
    background: {card_bg};
    border-radius: 14px;
    padding: 16px;
    margin: 10px 0;
    border: 1px solid {border};
    box-shadow: 0 2px 10px rgba(2,6,23,0.08);
    transition: transform 0.18s, box-shadow 0.18s;
}}
.card:hover {{
    transform: translateY(-1px);
    box-shadow: 0 8px 28px {a1_soft};
}}

/* ─── STAT CARD ───────────────────────────────────────────────────────── */
.stat-card {{
    background: {stat_bg};
    border-radius: 14px;
    padding: 16px 12px;
    text-align: center;
    border: 1px solid {border};
    box-shadow: 0 1px 8px rgba(2,6,23,0.05);
    position: relative;
    overflow: hidden;
}}
.stat-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, {accent1}, {accent2});
}}
.stat-number {{
    font-size: 2.1rem; font-weight: 800; line-height: 1.1;
    font-family: 'DM Serif Display', serif;
}}
.stat-label {{
    font-size: 0.7rem; color: {subtext}; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.6px; margin-top: 5px;
}}
.stat-number, .stat-label {{
    color: {text};
}}

/* ─── ACTION CARD (dashboard tiles) ──────────────────────────────────── */
.action-card {{
    background: {card_bg};
    border-radius: 14px;
    padding: 22px 14px;
    text-align: center;
    border: 1px solid {border};
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    margin-bottom: 6px;
    position: relative;
    overflow: hidden;
}}
.action-card::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, {accent1}, {accent2});
    transform: scaleX(0);
    transition: transform 0.2s;
    transform-origin: left;
}}
.action-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 30px {a1_soft};
    border-color: {accent1};
}}
.action-card:hover::after {{ transform: scaleX(1); }}
.action-icon  {{ font-size: 2.4rem; margin-bottom: 10px; }}
.action-label {{ font-size: 0.84rem; font-weight: 700; color: {text}; }}

/* ─── BADGES ──────────────────────────────────────────────────────────── */
.badge-high   {{ background:#fef2f2; color:#b91c1c; border:1.5px solid #fca5a5;
                 border-radius:8px; padding:3px 10px; font-size:0.73rem; font-weight:700; display:inline-block; }}
.badge-medium {{ background:#fffbeb; color:#b45309; border:1.5px solid #fcd34d;
                 border-radius:8px; padding:3px 10px; font-size:0.73rem; font-weight:700; display:inline-block; }}
.badge-low    {{ background:#f0fdf4; color:#15803d; border:1.5px solid #86efac;
                 border-radius:8px; padding:3px 10px; font-size:0.73rem; font-weight:700; display:inline-block; }}

.status-pending    {{ background:#fffbeb; color:#b45309; border:1.5px solid #fcd34d;
                      border-radius:8px; padding:3px 10px; font-size:0.73rem; font-weight:700; display:inline-block; }}
.status-inprogress {{ background:#eff6ff; color:#1d4ed8; border:1.5px solid #93c5fd;
                      border-radius:8px; padding:3px 10px; font-size:0.73rem; font-weight:700; display:inline-block; }}
.status-resolved   {{ background:#f0fdf4; color:#15803d; border:1.5px solid #86efac;
                      border-radius:8px; padding:3px 10px; font-size:0.73rem; font-weight:700; display:inline-block; }}

/* ─── COMPLAINT ITEM ──────────────────────────────────────────────────── */
.complaint-item {{
    background: {card_bg};
    border-radius: 14px;
    padding: 16px 18px;
    margin: 10px 0;
    border: 1px solid {border};
    border-left: 4px solid {accent1};
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    transition: transform 0.15s, border-color 0.15s;
}}
.complaint-item:hover {{
    transform: translateX(3px);
    border-left-color: {accent2};
}}
.complaint-id    {{ font-size: 0.73rem; color: {subtext}; font-weight: 700; letter-spacing: 0.05em; }}
.complaint-title {{ font-size: 0.95rem; font-weight: 700; margin: 4px 0; color: {text}; }}
.complaint-meta  {{ font-size: 0.77rem; color: {subtext}; display:flex; gap:12px; flex-wrap:wrap; margin-top:6px; }}

/* ─── NOTIFICATION CARD ───────────────────────────────────────────────── */
.notif-card {{
    background: {card_bg};
    border-radius: 14px;
    padding: 14px 16px;
    margin: 8px 0;
    border: 1px solid {border};
    display: flex;
    gap: 12px;
    align-items: flex-start;
    transition: transform 0.15s, box-shadow 0.15s;
}}
.notif-card:hover {{
    transform: translateX(3px);
    box-shadow: 0 4px 16px {a1_soft};
}}
.notif-title {{ font-weight: 700; font-size: 0.88rem; color: {text}; }}
.notif-msg   {{ font-size: 0.8rem; color: {subtext}; margin-top: 2px; }}
.notif-time  {{ font-size: 0.7rem; color: {subtext}; margin-top: 4px; }}

/* ─── TIMELINE ────────────────────────────────────────────────────────── */
.timeline-item {{
    display: flex;
    gap: 14px;
    margin-bottom: 16px;
    align-items: flex-start;
}}
.timeline-dot {{
    width: 14px; height: 14px;
    border-radius: 50%;
    background: {accent1};
    flex-shrink: 0;
    margin-top: 5px;
    box-shadow: 0 0 0 4px {a1_soft};
}}
.timeline-line {{
    width: 2px;
    min-height: 28px;
    background: linear-gradient(to bottom, {accent1}, {border});
    margin-left: 6px;
    flex-shrink: 0;
}}
.timeline-content {{
    background: {input_bg};
    border-radius: 12px;
    padding: 10px 14px;
    flex: 1;
    border: 1px solid {border};
}}
.timeline-status {{ font-weight: 700; font-size: 0.84rem; color: {accent1}; }}
.timeline-note   {{ font-size: 0.8rem; color: {subtext}; margin-top: 2px; }}
.timeline-time   {{ font-size: 0.72rem; color: {subtext}; margin-top: 4px; }}

/* ─── CHAT HEADER ─────────────────────────────────────────────────────── */
.chat-header {{
    background: linear-gradient(135deg, {accent1}, {accent2});
    padding: 16px 20px;
    color: white;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
    border-radius: 20px 20px 0 0;
}}

/* ─── SCHEME CARD ─────────────────────────────────────────────────────── */
.scheme-card {{
    background: {card_bg};
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid {border};
    margin-bottom: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}}
.scheme-body  {{ padding: 16px 20px; }}
.scheme-title {{ font-size: 1rem; font-weight: 700; margin-bottom: 6px; color: {text}; }}
.scheme-desc  {{ font-size: 0.83rem; color: {subtext}; line-height: 1.65; }}
.scheme-tag   {{
    background: {tag_bg}; color: {tag_col};
    border-radius: 8px; padding: 3px 10px;
    font-size: 0.72rem; font-weight: 700;
    display: inline-block; margin-top: 10px;
}}

/* ─── OFFICIAL COMPLAINT ──────────────────────────────────────────────── */
.official-complaint        {{ background: {card_bg}; border-radius: 16px; padding: 14px 16px;
                              margin: 8px 0; border: 1.5px solid {border}; }}
.official-complaint.high   {{ border-left: 4px solid #b91c1c; }}
.official-complaint.medium {{ border-left: 4px solid {accent1}; }}
.official-complaint.low    {{ border-left: 4px solid {accent2}; }}

/* ─── SECTION HEADER ──────────────────────────────────────────────────── */
.section-header {{
    font-size: 1rem;
    font-weight: 800;
    margin: 22px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
    color: {text};
}}
.section-header::after {{
    content: '';
    flex: 1;
    height: 2px;
    background: linear-gradient(
        to right,
        rgba(37, 99, 235, 0.45),
        rgba(20, 184, 166, 0.30),
        transparent
    );
    border-radius: 2px;
}}

/* ─── WELCOME SCREEN ──────────────────────────────────────────────────── */
.welcome-screen {{
    text-align: center;
    padding: 50px 20px 30px 20px;
}}
.welcome-logo  {{ font-size: 5rem; margin-bottom: 16px; display: block; }}
.welcome-title {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.95rem; font-weight: 400; margin-bottom: 8px; color: {text};
}}
.welcome-sub {{ font-size: 1rem; color: {subtext}; margin-bottom: 30px; line-height: 1.65; }}

/* ─── HEATMAP LEGEND ──────────────────────────────────────────────────── */
.heatmap-legend {{
    display: flex; gap: 18px; flex-wrap: wrap;
    margin-top: 14px; font-size: 0.78rem; font-weight: 600; color: {subtext};
}}
.legend-item  {{ display: flex; align-items: center; gap: 6px; }}
.legend-dot   {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}

/* ─── TRICOLOUR TOP STRIPE (visual flourish) ──────────────────────────── */
.stApp::before {{
    content: '';
    display: block;
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {accent1} 0%, {accent2} 100%);
    z-index: 9999;
    pointer-events: none;
}}

/* ─── DATAFRAME / TABLE READABILITY ───────────────────────────────────── */
div[data-testid="stDataFrame"] *,
table, th, td {{
    color: {text} !important;
    border-color: {border} !important;
}}

/* ─── RESPONSIVE IMPROVEMENTS ─────────────────────────────────────────── */
@media (max-width: 768px) {{
    .main .block-container {{
        padding: 0.9rem 0.8rem 2rem 0.8rem !important;
        max-width: 100% !important;
    }}
    .hero {{
        padding: 18px 16px 16px 16px;
        border-radius: 14px;
    }}
    .hero h1 {{
        font-size: 1.28rem;
    }}
    .card, .stat-card, .action-card, .complaint-item {{
        border-radius: 12px;
    }}
    .stButton > button {{
        padding: 10px 12px !important;
        font-size: 0.86rem !important;
    }}
}}

/* ─── DARK MODE WIDGET OVERRIDES ──────────────────────────────────────── */
{"" if not dark_mode else f"""
.stSelectbox svg, .stTextInput svg {{ fill: {subtext} !important; }}
div[data-baseweb="popover"] {{
    background: {card_bg} !important;
    border: 1.5px solid {border} !important;
}}
div[data-baseweb="menu"]  {{ background: {card_bg} !important; }}
div[data-baseweb="option"]:hover {{ background: {hover_bg} !important; }}
"""}

/* ─── ANIMATIONS ──────────────────────────────────────────────────────── */
@keyframes pulse-ring {{
    0%   {{ box-shadow: 0 0 0 0 rgba(217,119,6,0.6); }}
    70%  {{ box-shadow: 0 0 0 18px rgba(217,119,6,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(217,119,6,0); }}
}}
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes shimmer {{
    0%   {{ background-position: -200% 0; }}
    100% {{ background-position:  200% 0; }}
}}
.card, .complaint-item, .notif-card, .stat-card {{
    animation: fadeInUp 0.28s ease forwards;
}}
</style>
"""