def get_css(dark_mode=False):
    """
    Light-only stylesheet — NagarSeva warm orange palette.
    dark_mode param kept for API compatibility but ignored.
    """

    # ── COLOUR TOKENS (light only) ────────────────────────────────────────────
    bg          = "#FAF8F5"          # warm cream page background
    card_bg     = "#FFFFFF"          # pure white cards
    card_bg2    = "#FDF9F6"          # warm off-white secondary surface
    text        = "#1A1A1A"          # near-black primary text
    subtext     = "#6B7280"          # medium-gray subtext
    border      = "#EDE8E2"          # warm beige border
    input_bg    = "#F5F2EE"          # warm input background
    sidebar_bg  = "#FFFFFF"
    hover_bg    = "#F5F0EA"          # warm hover surface
    tag_bg      = "#FFF0E6"          # orange-tinted tag background
    tag_col     = "#C2410C"          # deep orange tag text

    accent1     = "#E8590C"          # primary orange  (from screenshot)
    accent2     = "#D4500B"          # darker orange
    accent3     = "#F07D3A"          # lighter orange

    a1_glow     = "rgba(232,89,12,0.18)"
    a1_soft     = "rgba(232,89,12,0.08)"
    a2_soft     = "rgba(212,80,11,0.06)"

    hero_from   = "#2D3A1F"          # dark olive — exact header colour
    hero_mid    = "#3D5028"
    hero_to     = "#1E2D14"

    shadow_sm   = "0 1px 3px rgba(26,20,10,0.06),0 4px 12px rgba(26,20,10,0.05)"
    shadow_md   = "0 4px 16px rgba(26,20,10,0.08),0 12px 32px rgba(26,20,10,0.06)"
    shadow_lg   = "0 12px 48px rgba(26,20,10,0.10),0 32px 64px rgba(26,20,10,0.07)"

    green_bg  = "#F0FDF4";  green_bd  = "#86EFAC";  green_text  = "#166534"
    amber_bg  = "#FFF7ED";  amber_bd  = "#FED7AA";  amber_text  = "#C2410C"
    red_bg    = "#FEF2F2";  red_bd    = "#FECACA";  red_text    = "#991B1B"
    blue_bg   = "#EFF6FF";  blue_bd   = "#BFDBFE";  blue_text   = "#1E40AF"
    glass_bg  = "rgba(255,255,255,0.80)"
    glass_bd  = "rgba(255,255,255,0.95)"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700;800;900&family=DM+Mono:wght@400;500&family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&display=swap');

/* ═══════════════════════════════════════════════════════
   CSS VARIABLES
═══════════════════════════════════════════════════════ */
:root {{
    --c-bg:        {bg};
    --c-card:      {card_bg};
    --c-card2:     {card_bg2};
    --c-text:      {text};
    --c-sub:       {subtext};
    --c-border:    {border};
    --c-input:     {input_bg};
    --c-hover:     {hover_bg};
    --c-a1:        {accent1};
    --c-a2:        {accent2};
    --c-a3:        {accent3};
    --c-a1-glow:   {a1_glow};
    --c-a1-soft:   {a1_soft};
    --c-a2-soft:   {a2_soft};
    --sh-sm:       {shadow_sm};
    --sh-md:       {shadow_md};
    --sh-lg:       {shadow_lg};
    /* radii */
    --r-xs:  6px;   --r-sm:  10px;  --r-md:  14px;
    --r-lg:  18px;  --r-xl:  22px;  --r-2xl: 28px;
    /* type scale */
    --fs-2xs: 0.625rem;    --fs-xs:  0.6875rem;
    --fs-sm:  0.75rem;     --fs-base:0.875rem;
    --fs-md:  0.9375rem;   --fs-lg:  1.0625rem;
    --fs-xl:  1.25rem;     --fs-2xl: 1.5rem;
    --fs-3xl: 1.75rem;     --fs-4xl: 2.25rem;
    /* spacing */
    --sp-1:4px; --sp-2:8px;  --sp-3:12px; --sp-4:16px;
    --sp-5:20px;--sp-6:24px; --sp-8:32px;
    /* icons */
    --icon-sm:1.0rem; --icon-md:1.25rem; --icon-lg:1.5rem;
    --icon-xl:1.75rem; --icon-2xl:2.25rem;
    /* transitions */
    --t-fast:0.15s cubic-bezier(0.4,0,0.2,1);
    --t-base:0.22s cubic-bezier(0.4,0,0.2,1);
    --t-slow:0.35s cubic-bezier(0.4,0,0.2,1);
}}

/* ═══════════════════════════════════════════════════════
   RESET & BASE
═══════════════════════════════════════════════════════ */
*,*::before,*::after{{box-sizing:border-box;}}

html,body,.stApp{{
    background-color:{bg}!important;
    color:{text}!important;
    font-family:'Inter','Noto Sans Devanagari',system-ui,sans-serif!important;
    font-size:0.875rem;
    line-height:1.6;
    -webkit-font-smoothing:antialiased;
    letter-spacing:-0.01em;
}}

p,span,div,label,small{{color:{text};}}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu,footer,.stDeployButton{{visibility:hidden!important;display:none!important;}}
.viewerBadge_container__1QSob{{display:none!important;}}

header[data-testid="stHeader"]{{
    background:transparent!important;
    height:0!important;
    overflow:visible!important;
    pointer-events:none!important;
    z-index:99998!important;
}}
button[kind="header"]{{
    background:transparent!important;border:none!important;box-shadow:none!important;
}}

/* ── ANIMATED TOP STRIPE ── */
.stApp::before{{
    content:'';display:block;position:fixed;
    top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,{accent1},{accent3},{accent2},{accent1});
    background-size:200% 100%;
    animation:prem-gradient-move 6s ease infinite;
    z-index:9999;pointer-events:none;
}}

/* ═══════════════════════════════════════════════════════
   LAYOUT
═══════════════════════════════════════════════════════ */
.main .block-container {{
    padding: 1.75rem 2rem 4rem !important;
    margin: 0 auto !important;
    width: 100% !important;
}}

/* ===== FIX: Sidebar collapse/expand toggle button ===== */
    
    /* The collapse button (visible when sidebar is OPEN) */
    section[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"],
    section[data-testid="stSidebar"] button[kind="header"],
    section[data-testid="stSidebar"] [data-testid="collapsedControl"] {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: {CARD} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
        color: {ACCENT} !important;
        width: 32px !important;
        height: 32px !important;
        z-index: 999999 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
    }}

    section[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"] svg,
    section[data-testid="stSidebar"] button[kind="header"] svg {{
        color: {ACCENT} !important;
        fill: {ACCENT} !important;
        width: 18px !important;
        height: 18px !important;
    }}

    section[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"]:hover {{
        background: {ACTIVE_BG} !important;
        border-color: {ACCENT} !important;
        transform: scale(1.05);
    }}

    /* The EXPAND button (visible when sidebar is CLOSED) — floats on main page */
    button[data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[kind="headerNoPadding"] {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: white !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
        color: {ACCENT} !important;
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
        color: {ACCENT} !important;
        fill: {ACCENT} !important;
        width: 20px !important;
        height: 20px !important;
    }}

    button[data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="collapsedControl"]:hover {{
        background: {ACTIVE_BG} !important;
        border-color: {ACCENT} !important;
        transform: scale(1.05);
        transition: all 0.15s ease;
    }}

    /* Make sure the header area doesn't hide the toggle */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        z-index: 999 !important;
    }}

/* ═══════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════ */
section[data-testid="stSidebar"]{{
    background:{sidebar_bg}!important;
    border-right:1px solid {border}!important;
}}
section[data-testid="stSidebar"] *{{color:{text}!important;}}
section[data-testid="stSidebar"] .stButton>button{{
    background:{card_bg2}!important;color:{text}!important;
    border:1px solid {border}!important;border-radius:var(--r-md)!important;
    box-shadow:none!important;font-size:0.875rem!important;font-weight:600!important;
    text-align:left!important;justify-content:flex-start!important;
    padding:10px 15px!important;transition:all var(--t-fast)!important;
}}
section[data-testid="stSidebar"] .stButton>button:hover{{
    background:{hover_bg}!important;
    border-color:{accent1}!important;
    transform:translateX(3px)!important;
}}

/* ═══════════════════════════════════════════════════════
   BUTTONS — warm orange gradient
═══════════════════════════════════════════════════════ */
.stButton>button{{
    background:linear-gradient(135deg,{accent1},{accent2})!important;
    color:#FFFFFF!important;
    border:none!important;
    border-radius:var(--r-md)!important;
    padding:10px 20px!important;
    font-weight:600!important;
    font-size:0.875rem!important;
    font-family:'Inter','Noto Sans Devanagari',sans-serif!important;
    width:100%!important;
    letter-spacing:-0.01em!important;
    cursor:pointer!important;
    line-height:1.4!important;
    transition:transform var(--t-base),box-shadow var(--t-base),filter var(--t-fast)!important;
    box-shadow:0 2px 10px {a1_glow}!important;
    position:relative!important;overflow:hidden!important;
}}
.stButton>button::before{{
    content:'';position:absolute;inset:0;
    background:linear-gradient(180deg,rgba(255,255,255,0.15) 0%,transparent 100%);
    pointer-events:none;border-radius:inherit;
}}
.stButton>button:hover{{
    transform:translateY(-2px) scale(1.006)!important;
    box-shadow:0 8px 24px {a1_glow}!important;
    filter:brightness(1.05)!important;
}}
.stButton>button:active{{
    transform:translateY(0) scale(0.998)!important;
    filter:brightness(0.96)!important;
}}
.stButton>button:focus-visible{{
    outline:none!important;
    box-shadow:0 0 0 3px {bg},0 0 0 5px {accent1}!important;
}}
.stButton>button:disabled{{
    opacity:0.45!important;cursor:not-allowed!important;transform:none!important;
}}

/* ═══════════════════════════════════════════════════════
   INPUTS
═══════════════════════════════════════════════════════ */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div>div{{
    background:{input_bg}!important;
    border:1.5px solid {border}!important;
    border-radius:var(--r-md)!important;
    color:{text}!important;
    font-family:'Inter','Noto Sans Devanagari',sans-serif!important;
    font-size:0.875rem!important;
    padding:10px 14px!important;
    transition:border-color var(--t-fast),box-shadow var(--t-fast)!important;
    box-shadow:0 1px 3px rgba(26,20,10,0.04)!important;
}}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{{
    border-color:{accent1}!important;
    box-shadow:0 0 0 3px {a1_soft}!important;
    outline:none!important;
    background:{card_bg}!important;
}}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{{
    color:{subtext}!important;opacity:0.65!important;
}}
.stTextInput input,.stTextArea textarea{{caret-color:{accent1}!important;}}

label,.stTextInput label,.stTextArea label,.stSelectbox label{{
    color:{subtext}!important;
    font-weight:600!important;
    font-size:0.6875rem!important;
    text-transform:uppercase!important;
    letter-spacing:0.07em!important;
    margin-bottom:5px!important;
}}
.stMarkdown,.stMarkdown p,.stMarkdown span{{color:{text}!important;}}
.stRadio label{{text-transform:none!important;letter-spacing:0!important;font-size:0.875rem!important;}}
.stRadio [data-testid="stMarkdownContainer"] p{{color:{text}!important;}}

/* ═══════════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"]{{
    background:{card_bg}!important;border-radius:var(--r-lg)!important;
    padding:5px!important;border:1.5px solid {border}!important;
    gap:3px!important;box-shadow:{shadow_sm}!important;
}}
.stTabs [data-baseweb="tab"]{{
    border-radius:var(--r-sm)!important;font-weight:600!important;
    font-size:0.75rem!important;color:{subtext}!important;
    padding:8px 18px!important;border:none!important;
    transition:all var(--t-fast)!important;background:transparent!important;
}}
.stTabs [aria-selected="true"]{{
    background:linear-gradient(135deg,{accent1},{accent2})!important;
    color:#FFFFFF!important;
    box-shadow:0 3px 12px {a1_glow}!important;
}}
.stTabs [data-baseweb="tab-panel"]{{background:transparent!important;padding:20px 0 0!important;}}

/* ═══════════════════════════════════════════════════════
   EXPANDER
═══════════════════════════════════════════════════════ */
.streamlit-expanderHeader{{
    background:{card_bg}!important;border-radius:var(--r-md)!important;
    font-weight:600!important;color:{text}!important;
    border:1.5px solid {border}!important;
    padding:12px 16px!important;font-size:0.875rem!important;
    transition:border-color var(--t-fast),box-shadow var(--t-fast)!important;
}}
.streamlit-expanderHeader:hover{{
    border-color:{accent1}!important;
    box-shadow:0 0 0 3px {a1_soft}!important;
}}
.streamlit-expanderContent{{
    background:{card_bg}!important;
    border:1.5px solid {border}!important;border-top:none!important;
    border-radius:0 0 var(--r-md) var(--r-md)!important;
    padding:14px 16px!important;
}}

/* ═══════════════════════════════════════════════════════
   SELECT BOX DROPDOWN
═══════════════════════════════════════════════════════ */
.stSelectbox div[data-baseweb="select"]>div{{
    background:{input_bg}!important;border-color:{border}!important;
    border-radius:var(--r-md)!important;
}}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div,
.stSelectbox [data-baseweb="select"] p{{color:{text}!important;}}
div[data-baseweb="popover"],div[data-baseweb="menu"],
ul[data-testid="stWidgetDropdownList"]{{
    background:{card_bg}!important;border:1.5px solid {border}!important;
    border-radius:var(--r-lg)!important;box-shadow:{shadow_md}!important;
    overflow:hidden!important;
}}
div[data-baseweb="popover"] *,div[data-baseweb="menu"] *,
ul[data-testid="stWidgetDropdownList"] *{{
    color:{text}!important;background-color:transparent!important;
}}
div[data-baseweb="option"]{{
    background:transparent!important;border-radius:var(--r-sm)!important;
    margin:2px 6px!important;font-size:0.875rem!important;
    font-weight:500!important;padding:8px 12px!important;
    transition:background var(--t-fast)!important;
}}
div[data-baseweb="option"]:hover,li[role="option"]:hover{{
    background:{hover_bg}!important;color:{text}!important;
}}
div[data-baseweb="option"][aria-selected="true"],
li[role="option"][aria-selected="true"]{{
    background:{a1_soft}!important;color:{accent1}!important;font-weight:700!important;
}}

/* ═══════════════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════════════ */
.stProgress>div>div{{
    background:linear-gradient(90deg,{accent1},{accent3})!important;
    border-radius:99px!important;
}}
.stProgress>div{{
    background:{border}!important;border-radius:99px!important;height:5px!important;
}}

/* ═══════════════════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════════════════ */
.stSuccess{{background:{green_bg}!important;border:1px solid {green_bd}!important;border-radius:var(--r-md)!important;color:{green_text}!important;}}
.stInfo   {{background:{blue_bg}!important; border:1px solid {blue_bd}!important; border-radius:var(--r-md)!important;color:{blue_text}!important;}}
.stWarning{{background:{amber_bg}!important;border:1px solid {amber_bd}!important;border-radius:var(--r-md)!important;color:{amber_text}!important;}}
.stError  {{background:{red_bg}!important;  border:1px solid {red_bd}!important;  border-radius:var(--r-md)!important;color:{red_text}!important;}}

/* ═══════════════════════════════════════════════════════
   MISC
═══════════════════════════════════════════════════════ */
hr{{border:none;height:1px;background:linear-gradient(90deg,transparent,{border},transparent);margin:2rem 0!important;}}
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:{border};border-radius:99px;}}
::-webkit-scrollbar-thumb:hover{{background:{subtext};}}
div[data-testid="stDataFrame"] *,table,th,td{{
    color:{text}!important;border-color:{border}!important;
    font-size:0.75rem!important;
}}

/* ═══════════════════════════════════════════════════════
   NOTIFICATION BUTTONS
═══════════════════════════════════════════════════════ */
.notif-actions{{width:100%!important;margin-top:10px!important;}}
.notif-actions .stColumn{{display:flex!important;align-items:center!important;}}
.notif-actions .stButton{{width:100%!important;}}
.notif-actions .stButton>button{{
    width:100%!important;height:42px!important;
    border-radius:12px!important;font-size:.82rem!important;
    font-weight:700!important;white-space:nowrap!important;
    transition:all .18s ease!important;
}}
.notif-read-btn .stButton>button{{
    background:linear-gradient(135deg,{accent1},{accent2})!important;
    color:#FFFFFF!important;
    box-shadow:0 8px 22px {a1_glow}!important;
}}
.notif-del-btn .stButton>button,
div[data-testid="stButton"].notif-del-btn > button{{
    background:#FFFFFF!important;background-image:none!important;
    color:#DC2626!important;
    border:1.5px solid rgba(220,38,38,.18)!important;
    box-shadow:0 4px 12px rgba(15,23,42,.05)!important;
    filter:none!important;
}}
.notif-del-btn .stButton>button:hover,
div[data-testid="stButton"].notif-del-btn > button:hover{{
    background:#FEF2F2!important;background-image:none!important;
    color:#B91C1C!important;
    border:1.5px solid rgba(220,38,38,.24)!important;
    transform:translateY(-2px)!important;
}}
div[data-testid="stButton"].notif-del-btn > button::before,
div[data-testid="stButton"].notif-del-btn > button::after{{display:none!important;}}
.notif-actions .stButton>button:hover{{transform:translateY(-2px)!important;}}

/* ── ADMIN NOTIFICATION CARDS ── */
.prem-notif-card,.notification-card,.admin-notification-card{{
    width:100%!important;overflow:hidden!important;border-radius:16px!important;
    padding:14px 16px!important;background:{card_bg}!important;
    border:1px solid {border}!important;
    box-shadow:0 4px 14px rgba(26,20,10,0.05)!important;
}}
.prem-notif-msg,.notification-message{{
    word-break:break-word!important;overflow-wrap:anywhere!important;
    line-height:1.6!important;color:{text}!important;
}}

/* ═══════════════════════════════════════════════════════
   COMPLAINT CARD FIX
═══════════════════════════════════════════════════════ */
.cc-wrap,.cc-bl,.cc-card,.cc-top,.cc-meta-box{{
    background:#FFFFFF!important;
    border:1px solid {border}!important;
    box-shadow:0 4px 14px rgba(26,20,10,0.05)!important;
}}
.cc-chip{{background:#FFFFFF!important;border:1px solid {border}!important;color:{text}!important;}}
.cc-meta-item,.cc-description,.cc-desc{{color:#374151!important;}}
.cc-category,.cc-title{{color:{text}!important;}}

/* ═══════════════════════════════════════════════════════
   ██  CUSTOM COMPONENTS
═══════════════════════════════════════════════════════ */

/* ── HERO BANNER — dark olive ── */
.prem-hero{{
    background:linear-gradient(135deg,{hero_from} 0%,{hero_mid} 50%,{hero_to} 100%);
    border-radius:var(--r-xl);
    padding:var(--sp-8) var(--sp-8) var(--sp-6);
    color:#fff;margin-bottom:var(--sp-6);
    position:relative;overflow:hidden;
    box-shadow:{shadow_lg};
    border:1px solid rgba(255,255,255,0.08);
}}
.prem-hero::before{{
    content:'';position:absolute;top:-100px;right:-80px;width:300px;height:300px;
    background:radial-gradient(circle,rgba(255,255,255,0.06) 0%,transparent 70%);
    pointer-events:none;animation:prem-float 8s ease-in-out infinite;
}}
.prem-hero::after{{
    content:'';position:absolute;bottom:-80px;left:15%;width:220px;height:220px;
    background:radial-gradient(circle,rgba(232,89,12,0.12) 0%,transparent 70%);
    pointer-events:none;animation:prem-float 10s ease-in-out infinite reverse;
}}
.prem-hero-title{{
    font-family:'Bricolage Grotesque','Inter',sans-serif;
    font-size:var(--fs-3xl);font-weight:800;line-height:1.2;
    margin-bottom:var(--sp-1);position:relative;z-index:1;
    color:#fff;letter-spacing:-0.03em;
}}
.prem-hero-sub{{
    font-size:var(--fs-base);margin:0 0 var(--sp-1);
    opacity:0.80;position:relative;z-index:1;
    color:rgba(255,255,255,0.88);font-weight:400;
}}
.prem-hero-avatar{{
    position:absolute;top:24px;right:26px;
    width:50px;height:50px;border-radius:50%;
    background:rgba(255,255,255,0.12);border:2px solid rgba(255,255,255,0.22);
    display:flex;align-items:center;justify-content:center;
    font-weight:700;font-size:var(--fs-md);color:#fff;z-index:1;
    backdrop-filter:blur(12px);box-shadow:0 4px 14px rgba(0,0,0,0.20);
}}
.prem-hero-stats{{
    display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));
    gap:var(--sp-2);margin-top:var(--sp-5);position:relative;z-index:1;
}}
.prem-hstat{{
    background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.14);
    border-radius:var(--r-md);padding:var(--sp-3) var(--sp-2);
    text-align:center;backdrop-filter:blur(12px);
    transition:background var(--t-fast),transform var(--t-fast);cursor:default;
}}
.prem-hstat:hover{{background:rgba(255,255,255,0.14);transform:translateY(-2px);}}
.prem-hstat-num{{
    font-family:'Bricolage Grotesque','Inter',sans-serif;
    font-size:var(--fs-4xl);font-weight:800;line-height:1;
    margin-bottom:var(--sp-1);color:#fff;letter-spacing:-0.03em;
}}
.prem-hstat-lbl{{
    font-size:var(--fs-2xs);font-weight:600;text-transform:uppercase;
    letter-spacing:0.08em;color:rgba(255,255,255,0.58);
}}
.prem-hstat.h-blue  .prem-hstat-num{{color:#BAC8FF;}}
.prem-hstat.h-amber .prem-hstat-num{{color:#FED7AA;}}
.prem-hstat.h-green .prem-hstat-num{{color:#6EE7B7;}}
.prem-hstat.h-red   .prem-hstat-num{{color:#FCA5A5;}}

/* ── CARD ── */
.prem-card{{
    background:{card_bg};border-radius:var(--r-lg);
    padding:var(--sp-6);margin:var(--sp-2) 0;
    border:1.5px solid {border};box-shadow:{shadow_sm};
    transition:transform var(--t-base),box-shadow var(--t-base),border-color var(--t-fast);
    position:relative;overflow:hidden;
}}
.prem-card:hover{{transform:translateY(-2px);box-shadow:{shadow_md};border-color:{accent1}44;}}

/* ── STAT CARD ── */
.prem-stat-card{{
    background:{card_bg};border-radius:var(--r-lg);
    padding:var(--sp-6) var(--sp-4) var(--sp-4);text-align:center;
    border:1.5px solid {border};box-shadow:{shadow_sm};
    position:relative;overflow:hidden;
    transition:transform var(--t-base),box-shadow var(--t-base);
}}
.prem-stat-card::before{{
    content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,{accent1},{accent3});
    border-radius:var(--r-lg) var(--r-lg) 0 0;
}}
.prem-stat-card::after{{
    content:'';position:absolute;top:3px;left:0;right:0;bottom:0;
    background:linear-gradient(180deg,{a1_soft} 0%,transparent 50%);
    pointer-events:none;border-radius:0 0 var(--r-lg) var(--r-lg);
}}
.prem-stat-card:hover{{transform:translateY(-4px);box-shadow:{shadow_md};}}
.prem-stat-num{{
    font-family:'Bricolage Grotesque','Inter',sans-serif;
    font-size:var(--fs-4xl);font-weight:800;line-height:1.1;
    color:{text};letter-spacing:-0.04em;position:relative;z-index:1;
}}
.prem-stat-lbl{{
    font-size:var(--fs-xs);color:{subtext};font-weight:600;
    text-transform:uppercase;letter-spacing:0.07em;
    margin-top:var(--sp-2);position:relative;z-index:1;
}}

/* ── ACTION CARD ── */
.prem-action-card{{
    background:{card_bg};border-radius:var(--r-lg);
    padding:var(--sp-6) var(--sp-4) var(--sp-5);text-align:center;
    border:1.5px solid {border};cursor:pointer;transition:all var(--t-base);
    box-shadow:{shadow_sm};margin-bottom:var(--sp-1);position:relative;overflow:hidden;
}}
.prem-action-card::before{{
    content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,{accent1},{accent3});
    transform:scaleX(0);transition:transform var(--t-base);
    transform-origin:left;border-radius:0 0 var(--r-lg) var(--r-lg);
}}
.prem-action-card:hover{{transform:translateY(-5px);box-shadow:{shadow_md};border-color:{accent1}55;}}
.prem-action-card:hover::before{{transform:scaleX(1);}}
.prem-action-card:hover .prem-action-icon{{transform:scale(1.10);}}
.prem-action-icon{{
    width:52px;height:52px;border-radius:var(--r-md);
    display:flex;align-items:center;justify-content:center;font-size:var(--icon-xl);
    margin:0 auto var(--sp-3);transition:transform var(--t-fast);
}}
.prem-action-label{{font-size:var(--fs-sm);font-weight:700;color:{text};line-height:1.35;letter-spacing:-0.01em;}}

/* ── SECTION HEADER ── */
.prem-section-header{{
    font-size:var(--fs-xs);font-weight:700;text-transform:uppercase;
    letter-spacing:0.10em;color:{subtext};
    margin:var(--sp-8) 0 var(--sp-3);
    display:flex;align-items:center;gap:10px;
}}
.prem-section-header::before{{
    content:'';width:3px;height:14px;
    background:linear-gradient(180deg,{accent1},{accent3});
    border-radius:99px;flex-shrink:0;
}}
.prem-section-header::after{{
    content:'';flex:1;height:1px;
    background:linear-gradient(to right,{border}80,transparent);
}}

/* ── COMPLAINT ITEM ── */
.prem-complaint-item{{
    background:{card_bg};border-radius:var(--r-lg);
    padding:var(--sp-4) var(--sp-6);margin:var(--sp-2) 0;
    border:1.5px solid {border};border-left:4px solid {accent1};
    box-shadow:{shadow_sm};
    transition:transform var(--t-fast),border-color var(--t-fast),box-shadow var(--t-base);
}}
.prem-complaint-item:hover{{transform:translateX(5px);border-left-color:{accent2};box-shadow:{shadow_md};}}
.prem-complaint-id{{
    font-size:var(--fs-xs);color:{accent1};font-weight:700;letter-spacing:0.05em;
    font-family:'DM Mono','Courier New',monospace;
    background:{a1_soft};padding:3px 10px;border-radius:7px;
    display:inline-block;margin-bottom:var(--sp-2);border:1px solid {accent1}22;
}}
.prem-complaint-title{{font-size:var(--fs-md);font-weight:700;margin:var(--sp-1) 0;color:{text};line-height:1.4;letter-spacing:-0.01em;}}
.prem-complaint-desc{{font-size:var(--fs-base);color:{subtext};line-height:1.65;margin:var(--sp-1) 0 var(--sp-3);}}
.prem-complaint-meta{{font-size:var(--fs-xs);color:{subtext};display:flex;gap:var(--sp-3);flex-wrap:wrap;align-items:center;}}

/* ── TAGS & BADGES ── */
.prem-tag{{
    background:{tag_bg};color:{tag_col};border-radius:7px;
    padding:3px 10px;font-size:var(--fs-xs);font-weight:700;
    display:inline-block;letter-spacing:0.01em;border:1px solid {tag_col}22;
}}
.prem-badge{{border-radius:7px;padding:3px 9px;font-size:var(--fs-2xs);font-weight:700;display:inline-block;letter-spacing:0.04em;text-transform:uppercase;}}
.prem-badge-high    {{background:{red_bg};  color:{red_text};  border:1px solid {red_bd};}}
.prem-badge-medium  {{background:{amber_bg};color:{amber_text};border:1px solid {amber_bd};}}
.prem-badge-low     {{background:{green_bg};color:{green_text};border:1px solid {green_bd};}}
.prem-badge-pending {{background:{amber_bg};color:{amber_text};border:1px solid {amber_bd};}}
.prem-badge-progress{{background:{blue_bg}; color:{blue_text}; border:1px solid {blue_bd};}}
.prem-badge-resolved{{background:{green_bg};color:{green_text};border:1px solid {green_bd};}}
.prem-badge-closed  {{background:{card_bg2};color:{subtext};   border:1px solid {border};}}
.prem-badge-rejected{{background:{red_bg};  color:{red_text};  border:1px solid {red_bd};}}
.prem-badge-emergency{{
    background:linear-gradient(135deg,#EF4444,#DC2626);color:#fff;border:none;
    box-shadow:0 0 0 3px rgba(239,68,68,0.20);
    animation:prem-pulse-emergency 2.5s ease infinite;
}}

/* ── NOTIFICATION CARD ── */
.prem-notif-card{{
    background:{card_bg};border-radius:var(--r-md);
    padding:var(--sp-3) var(--sp-5);margin:var(--sp-2) 0;
    border:1.5px solid {border};
    display:flex;gap:var(--sp-3);align-items:flex-start;
    box-shadow:{shadow_sm};
    transition:transform var(--t-fast),box-shadow var(--t-base);
    position:relative;overflow:hidden;
}}
.prem-notif-card::before{{
    content:'';position:absolute;top:0;left:0;bottom:0;width:0;
    background:{a1_soft};transition:width var(--t-base);
}}
.prem-notif-card:hover{{transform:translateX(5px);box-shadow:{shadow_md};}}
.prem-notif-card:hover::before{{width:3px;}}
.prem-notif-dot{{width:9px;height:9px;border-radius:50%;background:{accent1};flex-shrink:0;margin-top:5px;box-shadow:0 0 0 4px {a1_soft};}}
.prem-notif-title{{font-weight:700;font-size:var(--fs-base);color:{text};margin-bottom:3px;letter-spacing:-0.01em;}}
.prem-notif-msg  {{font-size:var(--fs-sm);color:{subtext};line-height:1.55;}}
.prem-notif-time {{font-size:var(--fs-xs);color:{subtext};margin-top:5px;font-family:'DM Mono',monospace;}}

/* ── NOTIFICATION BAR ── */
.prem-notif-bar{{
    background:{amber_bg};border:1.5px solid {amber_bd};
    border-radius:var(--r-md);padding:var(--sp-3) var(--sp-4);
    display:flex;align-items:center;gap:var(--sp-2);
    margin-bottom:var(--sp-4);cursor:pointer;
    transition:box-shadow var(--t-fast),transform var(--t-fast);
}}
.prem-notif-bar:hover{{box-shadow:{shadow_sm};transform:translateY(-1px);}}
.prem-notif-bar-dot{{width:7px;height:7px;border-radius:50%;background:{amber_text};flex-shrink:0;}}
.prem-notif-bar-text{{font-size:var(--fs-sm);color:{amber_text};font-weight:600;flex:1;}}
.prem-notif-bar-badge{{background:{amber_text};color:#fff;border-radius:99px;padding:2px 9px;font-size:var(--fs-2xs);font-weight:700;}}

/* ── TIMELINE ── */
.prem-timeline{{padding:4px 0;}}
.prem-tl-item{{display:flex;gap:var(--sp-3);align-items:flex-start;margin-bottom:4px;}}
.prem-tl-dot{{
    width:22px;height:22px;border-radius:50%;flex-shrink:0;
    display:flex;align-items:center;justify-content:center;
    font-size:0.58rem;font-weight:800;margin-top:2px;
    transition:transform var(--t-fast);
}}
.prem-tl-dot:hover{{transform:scale(1.15);}}
.prem-tl-dot.done  {{background:{accent1};color:#fff;box-shadow:0 0 0 4px {a1_soft};}}
.prem-tl-dot.active{{background:{accent3};color:#fff;box-shadow:0 0 0 4px {a2_soft};animation:prem-pulse-ring 2.5s ease infinite;}}
.prem-tl-dot.idle  {{background:{card_bg2};color:{subtext};border:2px solid {border};}}
.prem-tl-info{{flex:1;padding:2px 0;}}
.prem-tl-label{{font-size:var(--fs-sm);font-weight:600;color:{text};letter-spacing:-0.01em;}}
.prem-tl-time {{font-size:var(--fs-xs);color:{subtext};margin-top:2px;font-family:'DM Mono',monospace;}}
.prem-tl-line {{width:2px;height:14px;background:{border};margin-left:10px;border-radius:99px;}}
.prem-tl-line.done{{background:linear-gradient(to bottom,{accent1}88,{border});}}

/* ── SLA BAR ── */
.prem-sla-bar{{
    background:{card_bg2};border:1.5px solid {border};
    border-radius:var(--r-md);padding:10px 14px;
    display:flex;align-items:center;gap:var(--sp-2);
    margin-top:var(--sp-3);font-size:var(--fs-sm);color:{subtext};
}}
.prem-sla-bar.overdue{{background:{red_bg};border-color:{red_bd};color:{red_text};}}
.prem-sla-bar strong{{color:{text};font-weight:700;}}
.prem-sla-bar.overdue strong{{color:{red_text};}}

/* ── SCHEME CARD ── */
.prem-scheme-card{{
    background:{card_bg};border-radius:var(--r-lg);overflow:hidden;
    border:1.5px solid {border};margin-bottom:var(--sp-4);
    box-shadow:{shadow_sm};
    transition:transform var(--t-base),box-shadow var(--t-base),border-color var(--t-fast);
}}
.prem-scheme-card:hover{{transform:translateY(-3px);box-shadow:{shadow_md};border-color:{accent1}44;}}
.prem-scheme-body {{padding:var(--sp-5) var(--sp-6);}}
.prem-scheme-title{{font-size:var(--fs-md);font-weight:700;margin-bottom:var(--sp-2);color:{text};letter-spacing:-0.01em;}}
.prem-scheme-desc {{font-size:var(--fs-sm);color:{subtext};line-height:1.68;}}

/* ── LEADERBOARD ── */
.prem-lb-card{{
    background:{card_bg};border-radius:var(--r-lg);
    padding:var(--sp-4) var(--sp-6);margin:var(--sp-2) 0;
    border:1.5px solid {border};box-shadow:{shadow_sm};
    display:flex;gap:var(--sp-5);align-items:center;flex-wrap:wrap;
    transition:transform var(--t-fast),box-shadow var(--t-base);
    position:relative;overflow:hidden;
}}
.prem-lb-card::before{{content:'';position:absolute;top:0;left:0;bottom:0;width:4px;background:transparent;border-radius:4px 0 0 4px;transition:background var(--t-fast);}}
.prem-lb-card:hover{{transform:translateX(5px);box-shadow:{shadow_md};}}
.prem-lb-card:hover::before{{background:{accent1};}}
.prem-lb-card.rank-1{{background:linear-gradient(135deg,{card_bg} 60%,{amber_bg});border-color:#F59E0B44;}}
.prem-lb-card.rank-1::before{{background:#FFD700;}}
.prem-lb-card.rank-2::before{{background:#C0C0C0;}}
.prem-lb-card.rank-3::before{{background:#CD7F32;}}
.prem-lb-card.ineligible{{opacity:.50;background:{card_bg2};}}
.prem-lb-rank{{font-family:'Bricolage Grotesque','Inter',sans-serif;font-size:var(--fs-2xl);font-weight:800;min-width:60px;text-align:center;color:{amber_text};letter-spacing:-0.04em;}}
.prem-lb-info{{flex:1;}}
.prem-lb-name{{font-weight:700;font-size:var(--fs-md);margin-bottom:6px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;color:{text};}}
.prem-lb-dept{{font-size:var(--fs-xs);font-weight:600;background:{tag_bg};padding:2px 10px;border-radius:99px;color:{tag_col};}}
.prem-lb-stats{{display:flex;gap:var(--sp-5);flex-wrap:wrap;margin:var(--sp-2) 0;}}
.prem-lb-stat-item{{text-align:center;min-width:58px;}}
.prem-lb-stat-lbl{{font-size:var(--fs-2xs);text-transform:uppercase;letter-spacing:0.07em;color:{subtext};}}
.prem-lb-stat-val{{font-weight:700;font-size:var(--fs-base);color:{text};letter-spacing:-0.02em;}}

/* ── CUSTOM PROGRESS BAR ── */
.prem-prog-wrap{{background:{border};border-radius:99px;height:20px;overflow:hidden;position:relative;}}
.prem-prog-fill{{height:100%;border-radius:99px;display:flex;align-items:center;justify-content:center;transition:width 0.5s cubic-bezier(0.4,0,0.2,1);position:relative;overflow:hidden;}}
.prem-prog-fill::after{{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.18),transparent);background-size:200% 100%;animation:prem-shimmer 2.5s ease infinite;}}
.prem-prog-text{{font-size:var(--fs-xs);font-weight:700;color:#fff;position:relative;z-index:1;text-shadow:0 0 6px rgba(0,0,0,0.30);}}

/* ── TOP PERFORMER ── */
.prem-performer-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(176px,1fr));gap:var(--sp-3);margin:var(--sp-4) 0;}}
.prem-performer-card{{
    background:{card_bg};border-radius:var(--r-lg);
    padding:var(--sp-6) var(--sp-4);text-align:center;
    border:1.5px solid {border};box-shadow:{shadow_sm};
    transition:transform var(--t-base),box-shadow var(--t-base);
    position:relative;overflow:hidden;
}}
.prem-performer-card::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{accent1},{accent3});transform:scaleX(0);transform-origin:left;transition:transform var(--t-base);}}
.prem-performer-card:hover{{transform:translateY(-5px);box-shadow:{shadow_md};}}
.prem-performer-card:hover::after{{transform:scaleX(1);}}
.prem-rank-badge{{background:linear-gradient(135deg,{accent1},{accent2});color:#fff;width:34px;height:34px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:var(--fs-sm);margin-bottom:var(--sp-3);box-shadow:0 4px 14px {a1_glow};}}
.prem-performer-name{{font-weight:700;font-size:var(--fs-base);margin-bottom:4px;color:{text};letter-spacing:-0.02em;}}
.prem-performer-dept{{font-size:var(--fs-xs);color:{subtext};margin-bottom:var(--sp-2);}}
.prem-performer-stars{{font-size:var(--fs-sm);color:#F59E0B;margin-bottom:5px;}}
.prem-performer-stats{{font-size:var(--fs-xs);color:{subtext};}}

/* ── EMPTY STATE ── */
.prem-empty-state{{
    text-align:center;padding:4rem 2rem;
    background:{card_bg};border-radius:var(--r-xl);
    border:1.5px dashed {border};position:relative;overflow:hidden;
}}
.prem-empty-state::before{{content:'';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:200px;height:200px;background:radial-gradient(circle,{a1_soft} 0%,transparent 70%);pointer-events:none;}}
.prem-empty-icon {{font-size:var(--icon-2xl);margin-bottom:var(--sp-4);opacity:.45;display:block;position:relative;z-index:1;}}
.prem-empty-title{{font-family:'Bricolage Grotesque','Inter',sans-serif;font-size:var(--fs-lg);font-weight:700;color:{text};margin-bottom:var(--sp-2);letter-spacing:-0.02em;position:relative;z-index:1;}}
.prem-empty-sub  {{font-size:var(--fs-sm);color:{subtext};margin-bottom:var(--sp-6);line-height:1.65;position:relative;z-index:1;}}

/* ── WELCOME ── */
.prem-welcome{{text-align:center;padding:60px 20px 36px;}}
.prem-welcome-logo {{font-size:5rem;display:block;margin-bottom:var(--sp-4);animation:prem-float 4s ease-in-out infinite;}}
.prem-welcome-title{{font-family:'Bricolage Grotesque','Inter',sans-serif;font-size:var(--fs-3xl);font-weight:800;margin-bottom:var(--sp-3);color:{text};letter-spacing:-0.04em;}}
.prem-welcome-sub  {{font-size:var(--fs-md);color:{subtext};margin-bottom:var(--sp-8);line-height:1.75;max-width:460px;margin-left:auto;margin-right:auto;}}

/* ── CHAT HEADER ── */
.prem-chat-header{{
    background:linear-gradient(135deg,{hero_from},{hero_mid});
    padding:var(--sp-4) var(--sp-6);color:#fff;font-weight:700;font-size:var(--fs-base);
    display:flex;align-items:center;gap:var(--sp-2);
    border-radius:var(--r-lg) var(--r-lg) 0 0;
    box-shadow:0 4px 20px {a1_glow};letter-spacing:-0.01em;
}}

/* ── TIP BAR ── */
.prem-tip-bar{{background:{card_bg};border:1.5px solid {border};border-radius:var(--r-md);padding:var(--sp-3) var(--sp-4);display:flex;align-items:center;gap:var(--sp-3);margin-top:var(--sp-6);box-shadow:{shadow_sm};transition:border-color var(--t-fast);}}
.prem-tip-bar:hover{{border-color:{accent1}44;}}
.prem-tip-icon{{font-size:var(--icon-sm);flex-shrink:0;opacity:.75;}}
.prem-tip-text{{font-size:var(--fs-sm);color:{subtext};flex:1;line-height:1.58;}}
.prem-tip-text strong{{color:{text};font-weight:700;}}

/* ── GLASS ── */
.prem-glass{{background:{glass_bg}!important;backdrop-filter:blur(20px)!important;-webkit-backdrop-filter:blur(20px)!important;border:1px solid {glass_bd}!important;border-radius:var(--r-lg)!important;}}

/* ── DIVIDER ── */
.prem-divider{{display:flex;align-items:center;gap:var(--sp-3);margin:var(--sp-5) 0;color:{subtext};font-size:var(--fs-xs);font-weight:700;text-transform:uppercase;letter-spacing:0.08em;}}
.prem-divider::before,.prem-divider::after{{content:'';flex:1;height:1px;background:{border};}}

/* ── CHIP ── */
.prem-chip{{display:inline-flex;align-items:center;gap:5px;background:{a1_soft};border:1px solid {accent1}22;border-radius:99px;padding:3px 12px;font-size:var(--fs-xs);font-weight:700;color:{accent1};font-family:'DM Mono',monospace;}}

/* ── FILTER CHIPS ── */
.prem-filter-chips{{display:flex;gap:var(--sp-2);flex-wrap:wrap;margin:var(--sp-1) 0 var(--sp-2);}}
.prem-filter-chip{{padding:6px 14px;border-radius:30px;font-size:var(--fs-xs);font-weight:700;border:1.5px solid {border};background:{card_bg};color:{subtext};white-space:nowrap;cursor:pointer;transition:all var(--t-fast);}}
.prem-filter-chip.active{{background:linear-gradient(135deg,{accent1},{accent2});color:#fff;border-color:transparent;box-shadow:0 4px 12px {a1_glow};}}
.prem-filter-chip:hover:not(.active){{background:{hover_bg};border-color:{accent1}55;}}

/* ── FORM CARD ── */
.prem-form-card{{background:{card_bg};border:1.5px solid {border};border-radius:var(--r-xl);padding:var(--sp-6);margin-bottom:var(--sp-4);box-shadow:{shadow_sm};}}
.prem-form-section-label{{font-size:var(--fs-xs);font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:{subtext};margin-bottom:var(--sp-3);display:flex;align-items:center;gap:7px;}}
.prem-form-section-label::before{{content:'';width:3px;height:13px;background:linear-gradient(180deg,{accent1},{accent3});border-radius:99px;}}

/* ── COMPLAINT CARD ── */
.complaint-card{{background:{card_bg};border-radius:var(--r-xl);margin-bottom:1rem;border:1px solid {border};transition:all var(--t-base);overflow:hidden;}}
.complaint-card:hover{{transform:translateX(5px);border-color:{accent1};box-shadow:0 8px 20px -12px rgba(26,20,10,0.15);}}
.complaint-priority-high  {{border-left:4px solid #EF4444;}}
.complaint-priority-medium{{border-left:4px solid #F59E0B;}}
.complaint-priority-low   {{border-left:4px solid #10B981;}}
.complaint-header{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:var(--sp-2);margin-bottom:var(--sp-3);}}
.badge-status{{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:30px;font-size:var(--fs-xs);font-weight:700;}}
.badge-pending    {{background:{amber_bg};color:{amber_text};}}
.badge-in_progress{{background:{blue_bg}; color:{blue_text};}}
.badge-resolved   {{background:{green_bg};color:{green_text};}}
.badge-closed     {{background:{card_bg2};color:{subtext};}}
.badge-rejected   {{background:{red_bg};  color:{red_text};}}
.badge-priority{{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:30px;font-size:var(--fs-xs);font-weight:700;}}
.badge-priority-high  {{background:{red_bg};  color:{red_text};}}
.badge-priority-medium{{background:{amber_bg};color:{amber_text};}}
.badge-priority-low   {{background:{green_bg};color:{green_text};}}
.complaint-desc-box{{background:{card_bg2};padding:var(--sp-3) var(--sp-4);border-radius:var(--r-md);margin:var(--sp-3) 0;border:1px solid {border};color:{text};font-size:var(--fs-base);line-height:1.6;white-space:pre-wrap;word-break:break-word;max-height:200px;overflow-y:auto;}}
.complaint-meta{{display:flex;gap:var(--sp-3);flex-wrap:wrap;font-size:var(--fs-xs);color:{subtext};margin-bottom:var(--sp-3);}}
.action-buttons{{display:flex;gap:var(--sp-2);flex-wrap:wrap;margin-top:var(--sp-2);}}

/* ═══════════════════════════════════════════════════════
   UNPREFIXED ALIASES
═══════════════════════════════════════════════════════ */
.hero{{
    background:linear-gradient(135deg,{hero_from} 0%,{hero_mid} 50%,{hero_to} 100%);
    border-radius:var(--r-xl);
    padding:clamp(1.5rem,4vw,2.5rem) clamp(1.2rem,4vw,2.5rem) clamp(1.2rem,3vw,2rem);
    color:#fff;margin-bottom:var(--sp-6);position:relative;overflow:hidden;
    box-shadow:{shadow_lg};border:1px solid rgba(255,255,255,0.08);
    animation:prem-fade-up 0.32s ease both;
}}
.hero::before{{content:'';position:absolute;top:-100px;right:-80px;width:300px;height:300px;background:radial-gradient(circle,rgba(255,255,255,0.06) 0%,transparent 70%);pointer-events:none;animation:prem-float 8s ease-in-out infinite;}}
.hero h1{{font-family:'Bricolage Grotesque','Inter',sans-serif;font-size:clamp(1.5rem,4vw,var(--fs-3xl));font-weight:800;line-height:1.2;margin-bottom:var(--sp-1);position:relative;z-index:1;color:#fff;letter-spacing:-0.03em;}}
.hero p{{font-size:var(--fs-base);margin:0;opacity:0.85;position:relative;z-index:1;color:rgba(255,255,255,0.88);font-weight:400;}}
.card{{background:{card_bg};border-radius:var(--r-lg);padding:var(--sp-6);margin:var(--sp-2) 0;border:1.5px solid {border};box-shadow:{shadow_sm};transition:transform var(--t-base),box-shadow var(--t-base),border-color var(--t-fast);position:relative;overflow:hidden;animation:prem-fade-up 0.28s ease both;}}
.card:hover{{transform:translateY(-2px);box-shadow:{shadow_md};border-color:{accent1}44;}}
.stat-card{{background:{card_bg};border-radius:var(--r-lg);padding:var(--sp-6) var(--sp-4) var(--sp-4);text-align:center;border:1.5px solid {border};box-shadow:{shadow_sm};position:relative;overflow:hidden;transition:transform var(--t-base),box-shadow var(--t-base);animation:prem-scale-in 0.28s ease both;}}
.stat-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{accent1},{accent3});border-radius:var(--r-lg) var(--r-lg) 0 0;}}
.stat-card::after{{content:'';position:absolute;top:3px;left:0;right:0;bottom:0;background:linear-gradient(180deg,{a1_soft} 0%,transparent 50%);pointer-events:none;border-radius:0 0 var(--r-lg) var(--r-lg);}}
.stat-card:hover{{transform:translateY(-4px);box-shadow:{shadow_md};}}
.stat-number{{font-family:'Bricolage Grotesque','Inter',sans-serif;font-size:var(--fs-4xl);font-weight:800;line-height:1.1;color:{text};letter-spacing:-0.04em;position:relative;z-index:1;}}
.stat-label{{font-size:var(--fs-xs);color:{subtext};font-weight:600;text-transform:uppercase;letter-spacing:0.07em;margin-top:var(--sp-2);position:relative;z-index:1;}}
div.section-header:not(.prem-section-header){{font-size:var(--fs-xs);font-weight:700;text-transform:uppercase;letter-spacing:0.10em;color:{subtext};margin:var(--sp-8) 0 var(--sp-3);display:flex;align-items:center;gap:10px;}}
div.section-header:not(.prem-section-header)::before{{content:'';width:3px;height:14px;background:linear-gradient(180deg,{accent1},{accent3});border-radius:99px;flex-shrink:0;}}
div.section-header:not(.prem-section-header)::after{{content:'';flex:1;height:1px;background:linear-gradient(to right,{border}80,transparent);}}
.action-card{{background:{card_bg};border-radius:var(--r-lg);padding:var(--sp-6) var(--sp-4) var(--sp-5);text-align:center;border:1.5px solid {border};cursor:pointer;transition:all var(--t-base);box-shadow:{shadow_sm};margin-bottom:var(--sp-1);position:relative;overflow:hidden;}}
.action-card::before{{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{accent1},{accent3});transform:scaleX(0);transition:transform var(--t-base);transform-origin:left;border-radius:0 0 var(--r-lg) var(--r-lg);}}
.action-card:hover{{transform:translateY(-5px);box-shadow:{shadow_md};border-color:{accent1}55;}}
.action-card:hover::before{{transform:scaleX(1);}}
.action-card:hover .action-icon{{transform:scale(1.12);}}
.action-icon{{width:52px;height:52px;border-radius:var(--r-md);display:flex;align-items:center;justify-content:center;font-size:var(--icon-xl);margin:0 auto var(--sp-3);background:{a1_soft};border:1.5px solid {accent1}22;transition:transform var(--t-fast);}}
.action-label{{font-size:var(--fs-sm);font-weight:700;color:{text};line-height:1.35;letter-spacing:-0.01em;}}
.complaint-item{{background:{card_bg};border-radius:var(--r-lg);padding:var(--sp-4) var(--sp-6);margin:var(--sp-2) 0;border:1.5px solid {border};border-left:4px solid {accent1};box-shadow:{shadow_sm};transition:transform var(--t-fast),border-color var(--t-fast),box-shadow var(--t-base);animation:prem-fade-up 0.28s ease both;}}
.complaint-item:hover{{transform:translateX(5px);border-left-color:{accent2};box-shadow:{shadow_md};}}
.complaint-id{{font-size:var(--fs-xs);color:{accent1};font-weight:700;letter-spacing:0.05em;font-family:'DM Mono','Courier New',monospace;background:{a1_soft};padding:3px 10px;border-radius:7px;display:inline-block;margin-bottom:var(--sp-2);border:1px solid {accent1}22;}}
.complaint-title{{font-size:var(--fs-md);font-weight:700;margin:var(--sp-1) 0;color:{text};line-height:1.4;letter-spacing:-0.01em;}}
.notif-card{{background:{card_bg};border-radius:var(--r-md);padding:var(--sp-3) var(--sp-5);margin:var(--sp-2) 0;border:1.5px solid {border};display:flex;gap:var(--sp-3);align-items:flex-start;box-shadow:{shadow_sm};transition:transform var(--t-fast),box-shadow var(--t-base);position:relative;overflow:hidden;animation:prem-fade-up 0.28s ease both;}}
.notif-card::before{{content:'';position:absolute;top:0;left:0;bottom:0;width:0;background:{a1_soft};transition:width var(--t-base);}}
.notif-card:hover{{transform:translateX(5px);box-shadow:{shadow_md};}}
.notif-card:hover::before{{width:3px;}}
.notif-dot{{width:9px;height:9px;border-radius:50%;background:{accent1};flex-shrink:0;margin-top:5px;box-shadow:0 0 0 4px {a1_soft};}}
.notif-title{{font-weight:700;font-size:var(--fs-base);color:{text};margin-bottom:3px;letter-spacing:-0.01em;}}
.notif-msg  {{font-size:var(--fs-sm);color:{subtext};line-height:1.55;}}
.notif-time {{font-size:var(--fs-xs);color:{subtext};margin-top:5px;font-family:'DM Mono',monospace;}}
.notif-inline{{background:{amber_bg};border:1.5px solid {amber_bd};border-radius:var(--r-md);padding:var(--sp-3) var(--sp-4);display:flex;align-items:center;gap:var(--sp-2);margin-bottom:var(--sp-4);cursor:pointer;font-size:var(--fs-sm);color:{amber_text};font-weight:600;transition:box-shadow var(--t-fast),transform var(--t-fast);}}
.notif-inline:hover{{box-shadow:{shadow_sm};transform:translateY(-1px);}}
.welcome-screen{{text-align:center;padding:60px 20px 36px;animation:prem-fade-up 0.4s ease both;}}
.welcome-logo{{font-size:5rem;display:block;margin-bottom:var(--sp-4);animation:prem-float 4s ease-in-out infinite;filter:drop-shadow(0 8px 24px {a1_glow});}}
.welcome-title{{font-family:'Bricolage Grotesque','Inter',sans-serif;font-size:var(--fs-3xl);font-weight:800;margin-bottom:var(--sp-3);color:{text};letter-spacing:-0.04em;background:linear-gradient(135deg,{accent1},{accent2});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
.welcome-sub{{font-size:var(--fs-md);color:{subtext};margin-bottom:var(--sp-8);line-height:1.75;max-width:460px;margin-left:auto;margin-right:auto;}}
.timeline-item{{display:flex;gap:var(--sp-4);align-items:flex-start;margin-bottom:var(--sp-4);position:relative;padding-left:var(--sp-2);animation:prem-fade-up 0.28s ease both;}}
.timeline-dot{{width:14px;height:14px;border-radius:50%;flex-shrink:0;background:{accent1};margin-top:5px;box-shadow:0 0 0 4px {a1_soft};position:relative;z-index:2;}}
.timeline-dot::after{{content:'';position:absolute;top:14px;left:50%;transform:translateX(-50%);width:2px;height:calc(100% + 12px);background:{border};z-index:1;}}
.timeline-item:last-child .timeline-dot::after{{display:none;}}
.timeline-content{{flex:1;background:{card_bg};border:1.5px solid {border};border-radius:var(--r-md);padding:var(--sp-3) var(--sp-4);box-shadow:{shadow_sm};transition:border-color var(--t-fast),box-shadow var(--t-fast);}}
.timeline-content:hover{{border-color:{accent1}44;box-shadow:{shadow_md};}}
.timeline-status{{font-weight:700;font-size:var(--fs-base);color:{text};margin-bottom:var(--sp-1);letter-spacing:-0.01em;}}
.timeline-time{{font-size:var(--fs-xs);color:{subtext};margin-top:var(--sp-2);font-family:'DM Mono',monospace;}}
.scheme-tag{{display:inline-block;background:{tag_bg};color:{tag_col};border-radius:7px;padding:3px 10px;font-size:var(--fs-xs);font-weight:700;letter-spacing:0.01em;border:1px solid {tag_col}22;}}
.official-complaint{{background:{card_bg};border-radius:var(--r-md);padding:var(--sp-4);margin:var(--sp-2) 0;border:1.5px solid {border};box-shadow:{shadow_sm};transition:border-color var(--t-fast);}}
.official-complaint.high   {{border-left:4px solid {red_text};}}
.official-complaint.medium {{border-left:4px solid {amber_text};}}
.official-complaint.low    {{border-left:4px solid {green_text};}}

/* ═══════════════════════════════════════
   CUSTOM FLOATING MENU
═══════════════════════════════════════ */

.custom-menu-wrap{{

    position:fixed!important;

    top:70px!important;

    left:18px!important;

    width:260px!important;

    z-index:999999!important;

    background:rgba(255,255,255,.96)!important;

    border:1px solid rgba(99,102,241,.12)!important;

    border-radius:20px!important;

    padding:18px!important;

    box-shadow:
        0 20px 50px rgba(15,23,42,.16)!important;

    backdrop-filter:blur(18px)!important;
}}

/* Floating button */
div[data-testid="stButton"] button[key="menu_toggle"]{{

    position:fixed!important;

    top:16px!important;

    left:16px!important;

    z-index:999999!important;

    width:48px!important;

    height:48px!important;

    border-radius:14px!important;

    background:
        linear-gradient(
            135deg,
            #6366F1,
            #8B5CF6
        )!important;

    color:#FFFFFF!important;

    border:none!important;

    font-size:20px!important;

    font-weight:800!important;
}}
.sidebar-active{{background:linear-gradient(90deg,{a1_soft},transparent);border-left:3px solid {accent1};border-radius:0 var(--r-sm) var(--r-sm) 0;padding:2px 0;margin:2px 0;transition:all var(--t-fast);}}
.badge-high{{display:inline-flex;align-items:center;gap:4px;border-radius:7px;padding:3px 10px;font-size:var(--fs-2xs);font-weight:700;letter-spacing:0.04em;text-transform:uppercase;background:{red_bg};color:{red_text};border:1px solid {red_bd};}}
.badge-medium{{display:inline-flex;align-items:center;gap:4px;border-radius:7px;padding:3px 10px;font-size:var(--fs-2xs);font-weight:700;letter-spacing:0.04em;text-transform:uppercase;background:{amber_bg};color:{amber_text};border:1px solid {amber_bd};}}
.badge-low{{display:inline-flex;align-items:center;gap:4px;border-radius:7px;padding:3px 10px;font-size:var(--fs-2xs);font-weight:700;letter-spacing:0.04em;text-transform:uppercase;background:{green_bg};color:{green_text};border:1px solid {green_bd};}}
.status-pending{{display:inline-flex;align-items:center;gap:4px;border-radius:30px;padding:3px 12px;font-size:var(--fs-xs);font-weight:700;background:{amber_bg};color:{amber_text};border:1px solid {amber_bd};}}
.status-inprogress{{display:inline-flex;align-items:center;gap:4px;border-radius:30px;padding:3px 12px;font-size:var(--fs-xs);font-weight:700;background:{blue_bg};color:{blue_text};border:1px solid {blue_bd};}}
.status-resolved{{display:inline-flex;align-items:center;gap:4px;border-radius:30px;padding:3px 12px;font-size:var(--fs-xs);font-weight:700;background:{green_bg};color:{green_text};border:1px solid {green_bd};}}
.badge{{display:inline-flex;align-items:center;gap:4px;border-radius:30px;padding:3px 12px;font-size:var(--fs-xs);font-weight:700;background:{card_bg2};color:{subtext};border:1px solid {border};}}
.badge-pending   {{background:{amber_bg};color:{amber_text};border-color:{amber_bd};}}
.badge-in-progress{{background:{blue_bg};color:{blue_text};border-color:{blue_bd};}}
.badge-resolved  {{background:{green_bg};color:{green_text};border-color:{green_bd};}}
.badge-rejected  {{background:{red_bg};color:{red_text};border-color:{red_bd};}}
.stars{{font-size:var(--fs-lg);letter-spacing:2px;color:#F59E0B;display:inline-block;margin:var(--sp-1) 0;filter:drop-shadow(0 1px 3px rgba(245,158,11,0.3));}}

/* ── STREAMLIT METRIC ── */
div[data-testid="stMetric"]{{background:{card_bg};border-radius:var(--r-lg);padding:var(--sp-4) var(--sp-5);border:1.5px solid {border};box-shadow:{shadow_sm};transition:transform var(--t-fast),box-shadow var(--t-fast);}}
div[data-testid="stMetric"]:hover{{transform:translateY(-2px);box-shadow:{shadow_md};}}
div[data-testid="stMetric"] label{{text-transform:uppercase!important;letter-spacing:0.06em!important;font-size:var(--fs-2xs)!important;font-weight:700!important;color:{subtext}!important;}}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{{font-family:'Bricolage Grotesque','Inter',sans-serif!important;font-size:var(--fs-2xl)!important;font-weight:800!important;letter-spacing:-0.03em!important;color:{text}!important;}}

/* ── FILE UPLOADER ── */
.stFileUploader{{border-radius:var(--r-lg)!important;border:2px dashed {border}!important;background:{card_bg}!important;transition:border-color var(--t-fast),background var(--t-fast)!important;}}
.stFileUploader:hover{{border-color:{accent1}!important;background:{a1_soft}!important;}}

/* ── REMOVE BUTTON ── */
.dd-remove-wrap{{display:flex!important;justify-content:flex-end!important;align-items:center!important;width:100%!important;}}
.dd-remove-wrap .stButton{{width:54px!important;flex:none!important;}}
.dd-remove-wrap .stButton > button{{width:54px!important;min-width:54px!important;height:46px!important;border-radius:14px!important;border:none!important;background:linear-gradient(135deg,#EF4444,#DC2626)!important;color:#FFFFFF!important;font-size:18px!important;font-weight:700!important;box-shadow:0 10px 24px rgba(239,68,68,.24)!important;transition:all .18s ease!important;}}
.dd-remove-wrap .stButton > button:hover{{transform:translateY(-2px)!important;filter:brightness(1.04)!important;}}

/* ═══════════════════════════════════════════════════════
   ANIMATIONS
═══════════════════════════════════════════════════════ */
@keyframes prem-fade-up   {{from{{opacity:0;transform:translateY(18px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes prem-scale-in  {{from{{opacity:0;transform:scale(0.96);}}to{{opacity:1;transform:scale(1);}}}}
@keyframes prem-pulse-ring{{
    0%  {{box-shadow:0 0 0 0 {a1_glow};}}
    70% {{box-shadow:0 0 0 12px rgba(232,89,12,0);}}
    100%{{box-shadow:0 0 0 0 rgba(232,89,12,0);}}
}}
@keyframes prem-pulse-emergency{{
    0%  {{box-shadow:0 0 0 0 rgba(239,68,68,0.40);}}
    70% {{box-shadow:0 0 0 12px rgba(239,68,68,0);}}
    100%{{box-shadow:0 0 0 0 rgba(239,68,68,0);}}
}}
@keyframes prem-shimmer{{0%{{background-position:-200% 0;}}100%{{background-position:200% 0;}}}}
@keyframes prem-gradient-move{{0%,100%{{background-position:0% 50%;}}50%{{background-position:100% 50%;}}}}
@keyframes prem-float{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-8px);}}}}

.prem-card,.prem-complaint-item,.prem-notif-card,
.prem-scheme-card,.prem-lb-card,.prem-hero{{animation:prem-fade-up 0.28s ease both;}}
.prem-stat-card{{animation:prem-scale-in 0.28s ease both;}}

/* ═══════════════════════════════════════════════════════
   RESPONSIVE
═══════════════════════════════════════════════════════ */
@media(max-width:768px){{
    .main .block-container{{padding:1rem 0.875rem 2.5rem!important;max-width:100%!important;}}
    .prem-hero{{padding:var(--sp-5) var(--sp-4) var(--sp-4);border-radius:var(--r-lg);}}
    .prem-hero-title,.hero h1{{font-size:var(--fs-2xl);}}
    .prem-hero-avatar{{display:none;}}
    .prem-hero-stats{{grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:var(--sp-2);}}
    .prem-hstat-num{{font-size:var(--fs-3xl);}}
    .prem-action-card,.action-card{{padding:var(--sp-5) var(--sp-3) var(--sp-4);border-radius:var(--r-md);}}
    .prem-action-icon,.action-icon{{width:46px;height:46px;font-size:var(--icon-lg);}}
    .prem-action-label,.action-label{{font-size:var(--fs-xs);}}
    .prem-stat-card,.stat-card{{border-radius:var(--r-md);padding:var(--sp-4) var(--sp-3) var(--sp-3);}}
    .prem-stat-num,.stat-number{{font-size:var(--fs-2xl);}}
    .prem-card,.prem-complaint-item,.prem-notif-card,.complaint-item,.notif-card,.card{{border-radius:var(--r-md);}}
    .prem-lb-card{{flex-direction:column;text-align:center;}}
    .prem-lb-stats{{justify-content:center;}}
    .prem-lb-rank{{min-width:auto;}}
    .prem-performer-grid{{grid-template-columns:1fr 1fr;gap:var(--sp-2);}}
    .stButton>button{{padding:10px 14px!important;font-size:0.75rem!important;}}
    .prem-section-header{{font-size:var(--fs-2xs);}}
    .prem-filter-chips{{gap:var(--sp-1);}}
    .prem-filter-chip{{padding:5px 10px;font-size:var(--fs-2xs);}}
    .hero{{padding:var(--sp-5) var(--sp-4) var(--sp-4);border-radius:var(--r-lg);}}
    .welcome-screen,.prem-welcome{{padding:40px 16px 24px;}}
    .welcome-title,.prem-welcome-title{{font-size:var(--fs-2xl);}}
}}
@media(max-width:480px){{
    .prem-hero-stats{{grid-template-columns:repeat(2,1fr);}}
    .prem-performer-grid{{grid-template-columns:1fr;}}
    .prem-complaint-meta,.complaint-meta{{gap:var(--sp-2);}}
    .prem-lb-stats{{gap:var(--sp-3);}}
    .stat-number{{font-size:var(--fs-xl);}}
}}

</style>
"""