

def get_css(dark_mode: bool = False) -> str:
    # ─────────────────────────────────────────────────────────────────────────
    # COLOUR TOKENS
    # ─────────────────────────────────────────────────────────────────────────
    if dark_mode:
        bg         = "#070B14"
        card_bg    = "#0D1220"
        card_bg2   = "#111827"
        text       = "#EFF2FF"
        subtext    = "#7C8FAC"
        border     = "#1C2540"
        input_bg   = "#0F1828"
        sidebar_bg = "#09101A"
        hover_bg   = "#16213A"
        tag_bg     = "#151E35"
        tag_col    = "#A5B4FC"
        accent1    = "#6366F1"
        accent2    = "#818CF8"
        accent3    = "#22D3EE"
        a1_glow    = "rgba(99,102,241,0.35)"
        a1_soft    = "rgba(99,102,241,0.12)"
        a2_soft    = "rgba(129,140,248,0.10)"
        hero_from  = "#1E1B4B"
        hero_mid   = "#312E81"
        hero_to    = "#0C4A6E"
        shadow_sm  = "0 1px 4px rgba(0,0,0,.50),0 4px 12px rgba(0,0,0,.30)"
        shadow_md  = "0 4px 20px rgba(0,0,0,.55),0 12px 40px rgba(0,0,0,.35)"
        shadow_lg  = "0 16px 60px rgba(0,0,0,.65),0 40px 80px rgba(0,0,0,.40)"
        green_bg   = "#071A10"; green_bd  = "#166534"; green_text  = "#4ADE80"
        amber_bg   = "#1A1000"; amber_bd  = "#92400E"; amber_text  = "#FCD34D"
        red_bg     = "#1A0505"; red_bd    = "#991B1B"; red_text    = "#FCA5A5"
        blue_bg    = "#04091A"; blue_bd   = "#1E40AF"; blue_text   = "#93C5FD"
        glass_bg   = "rgba(255,255,255,0.04)"
        glass_bd   = "rgba(255,255,255,0.08)"
    else:
        bg         = "#F2F5FC"
        card_bg    = "#FFFFFF"
        card_bg2   = "#F7F9FF"
        text       = "#0B1428"
        subtext    = "#5A6A85"
        border     = "#CBD5E9"
        input_bg   = "#F0F4FB"
        sidebar_bg = "#FFFFFF"
        hover_bg   = "#E8EDF7"
        tag_bg     = "#EEF2FF"
        tag_col    = "#3730A3"
        accent1    = "#4F46E5"
        accent2    = "#7C3AED"
        accent3    = "#0891B2"
        a1_glow    = "rgba(79,70,229,0.20)"
        a1_soft    = "rgba(79,70,229,0.08)"
        a2_soft    = "rgba(124,58,237,0.06)"
        hero_from  = "#4F46E5"
        hero_mid   = "#7C3AED"
        hero_to    = "#0891B2"
        shadow_sm  = "0 1px 3px rgba(11,20,40,.06),0 4px 12px rgba(11,20,40,.06)"
        shadow_md  = "0 4px 16px rgba(11,20,40,.08),0 12px 32px rgba(11,20,40,.06)"
        shadow_lg  = "0 12px 48px rgba(11,20,40,.12),0 32px 64px rgba(11,20,40,.08)"
        green_bg   = "#F0FDF4"; green_bd  = "#86EFAC"; green_text  = "#166534"
        amber_bg   = "#FFFBEB"; amber_bd  = "#FDE68A"; amber_text  = "#92400E"
        red_bg     = "#FEF2F2"; red_bd    = "#FECACA"; red_text    = "#991B1B"
        blue_bg    = "#EFF6FF"; blue_bd   = "#BFDBFE"; blue_text   = "#1E40AF"
        glass_bg   = "rgba(255,255,255,0.70)"
        glass_bd   = "rgba(255,255,255,0.90)"

    # ─────────────────────────────────────────────────────────────────────────
    # DARK-ONLY WIDGET OVERRIDES
    # ONE declaration per selector state — no duplicates.
    # ─────────────────────────────────────────────────────────────────────────
    dark_overrides = ""
    if dark_mode:
        dark_overrides = f"""
/* ── SVG icons in dark widgets ── */
.stSelectbox svg,.stTextInput svg{{fill:{subtext}!important;}}

/* ═══════════════════════════════════════════════
   STREAMLIT DROPDOWN BLACK FIX
═══════════════════════════════════════════════ */

/* Main dropdown popup */
div[data-baseweb="popover"]{{
    background: #ffffff !important;
    border: 1px solid rgba(0,0,0,.08) !important;
    border-radius: 16px !important;
    box-shadow: 0 12px 40px rgba(0,0,0,.12) !important;
    overflow: hidden !important;
    z-index: 999999 !important;
}}

/* Dropdown menu */
div[data-baseweb="menu"]{{
    background: #ffffff !important;
    color: #111827 !important;
}}

/* Dropdown options */
div[data-baseweb="option"],
li[role="option"]{{
    background: #ffffff !important;
    color: #111827 !important;
    font-size: .95rem !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    margin: 4px 6px !important;
    transition: all .15s ease !important;
}}

/* Hover effect */
div[data-baseweb="option"]:hover,
li[role="option"]:hover{{
    background: rgba(99,102,241,.08) !important;
    color: #111827 !important;
}}

/* Selected option */
div[data-baseweb="option"][aria-selected="true"],
li[role="option"][aria-selected="true"]{{
    background: rgba(99,102,241,.12) !important;
    color: #4F46E5 !important;
    font-weight: 700 !important;
}}

/* Selectbox input */
.stSelectbox > div > div{{
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid rgba(0,0,0,.08) !important;
    border-radius: 14px !important;
}}

/* Selected text */
.stSelectbox div[data-baseweb="select"] span{{
    color: #111827 !important;
}}

/* Dropdown arrow */
.stSelectbox svg{{
    fill: #111827 !important;
}}

/* Search input */
div[data-baseweb="popover"] input{{
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid rgba(0,0,0,.08) !important;
}}

/* Prevent dark overlay */
div[data-baseweb="layer"]{{
    background: transparent !important;
}}

/* Remove black backgrounds everywhere */
div[data-baseweb]{{
    color: #111827 !important;
}}



/* ── Dropdown panel ── */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[data-testid="stWidgetDropdownList"]{{
    background:{card_bg}!important;
    border:1px solid {border}!important;
    border-radius:16px!important;
    box-shadow:{shadow_md}!important;
}}

/* ── Option rows: base / hover / selected ── */
div[data-baseweb="option"],
li[role="option"]{{
    background:transparent!important;
    color:{text}!important;
    border-radius:10px!important;
    margin:2px 6px!important;
    padding:8px 12px!important;
}}
div[data-baseweb="option"]:hover,
li[role="option"]:hover{{
    background:{hover_bg}!important;
    color:{text}!important;
}}
div[data-baseweb="option"][aria-selected="true"],
li[role="option"][aria-selected="true"]{{
    background:{a1_soft}!important;
    color:{accent2}!important;
    font-weight:700!important;
}}

/* ── Caret ── */
.stTextInput input,.stTextArea textarea{{caret-color:{accent2}!important;}}

/* ── Radio labels ── */
.stRadio label{{color:{text}!important;}}
.stRadio [data-testid="stMarkdownContainer"] p{{color:{text}!important;}}

/* ── Notification bar (amber text override) ── */
.prem-notif-bar-text{{color:{amber_text}!important;}}
.prem-notif-bar-badge{{color:#fff!important;background:{amber_text}!important;}}

/* ── Complaint description box ── */
.complaint-desc-box{{color:{text}!important;}}

/* ── Closed badge in dark mode ── */
.prem-badge-closed{{
    background:{hover_bg}!important;
    color:{subtext}!important;
    border:1px solid {border}!important;
}}
"""

    return f"""
<style>
/* ═══════════════════════════════════════════════════════════════
   FONTS
═══════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Mono:wght@400;500&family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&display=swap');

/* ═══════════════════════════════════════════════════════════════
   DESIGN TOKENS  (single :root block — clamp() for responsive sizing)
═══════════════════════════════════════════════════════════════ */
:root{{
    /* ── Surface ── */
    --c-bg:       {bg};
    --c-card:     {card_bg};
    --c-card2:    {card_bg2};
    --c-text:     {text};
    --c-sub:      {subtext};
    --c-border:   {border};
    --c-input:    {input_bg};
    --c-hover:    {hover_bg};
    /* ── Accent ── */
    --c-a1:       {accent1};
    --c-a2:       {accent2};
    --c-a3:       {accent3};
    --c-a1-glow:  {a1_glow};
    --c-a1-soft:  {a1_soft};
    --c-a2-soft:  {a2_soft};
    /* ── Shadow ── */
    --sh-sm:      {shadow_sm};
    --sh-md:      {shadow_md};
    --sh-lg:      {shadow_lg};
    /* ── Radius — responsive via clamp ── */
    --r-xs:  clamp(5px,  1.2vw,  8px);
    --r-sm:  clamp(8px,  1.8vw, 10px);
    --r-md:  clamp(10px, 2.2vw, 14px);
    --r-lg:  clamp(14px, 2.8vw, 18px);
    --r-xl:  clamp(18px, 3.5vw, 24px);
    --r-2xl: clamp(22px, 4.5vw, 28px);
    /* ── Type scale — clamp prevents oversizing on 1920px+ ── */
    --fs-2xs: clamp(0.60rem,  1.4vw, 0.6875rem);
    --fs-xs:  clamp(0.6875rem,1.7vw, 0.75rem);
    --fs-sm:  clamp(0.75rem,  1.9vw, 0.875rem);
    --fs-base:clamp(0.875rem, 2.1vw, 1rem);
    --fs-md:  clamp(0.9375rem,2.4vw, 1.0625rem);
    --fs-lg:  clamp(1.0625rem,2.8vw, 1.25rem);
    --fs-xl:  clamp(1.25rem,  3.2vw, 1.5rem);
    --fs-2xl: clamp(1.5rem,   3.8vw, 1.875rem);
    --fs-3xl: clamp(1.75rem,  4.5vw, 2.25rem);
    --fs-4xl: clamp(2rem,     5.5vw, 2.75rem);
    /* ── Spacing — clamp prevents giant gutters on 4K ── */
    --sp-1:  clamp(3px,  0.6vw,  5px);
    --sp-2:  clamp(6px,  1.1vw,  9px);
    --sp-3:  clamp(10px, 1.8vw, 13px);
    --sp-4:  clamp(14px, 2.4vw, 18px);
    --sp-5:  clamp(18px, 3.0vw, 22px);
    --sp-6:  clamp(22px, 3.8vw, 30px);
    --sp-8:  clamp(28px, 5.0vw, 44px);
    /* ── Icon ── */
    --icon-sm:  clamp(0.9rem,  2vw, 1.0rem);
    --icon-md:  clamp(1.1rem,  2.5vw, 1.25rem);
    --icon-lg:  clamp(1.3rem,  3vw, 1.5rem);
    --icon-xl:  clamp(1.5rem,  3.5vw, 1.75rem);
    --icon-2xl: clamp(1.9rem,  4.5vw, 2.25rem);
    /* ── Motion ── */
    --t-fast: 0.15s cubic-bezier(0.4,0,0.2,1);
    --t-base: 0.22s cubic-bezier(0.4,0,0.2,1);
    --t-slow: 0.35s cubic-bezier(0.4,0,0.2,1);
}}

/* ═══════════════════════════════════════════════════════════════
   RESET & BASE
═══════════════════════════════════════════════════════════════ */
*,*::before,*::after{{box-sizing:border-box;}}

/* Prevent horizontal overflow everywhere */
html,body,.stApp,[data-testid="stAppViewContainer"]{{
    overflow-x:hidden!important;
    max-width:100%!important;
}}
html,body,.stApp{{
    background-color:var(--c-bg)!important;
    color:var(--c-text)!important;
    font-family:'DM Sans','Noto Sans Devanagari',system-ui,sans-serif!important;
    font-size:var(--fs-base);
    line-height:1.6;
    -webkit-font-smoothing:antialiased;
    -moz-osx-font-smoothing:grayscale;
    letter-spacing:-0.01em;
}}

/* Scoped text color — semantic elements only, NOT div globally */
p,span,label,small{{color:var(--c-text);}}
.stMarkdown,.stMarkdown p,.stMarkdown span{{color:var(--c-text)!important;}}

/* Prevent any element from causing horizontal scroll */
img,svg,iframe,video{{max-width:100%;height:auto;}}
table{{display:block;overflow-x:auto;}}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu,footer,.stDeployButton{{visibility:hidden!important;display:none!important;}}
.viewerBadge_container__1QSob{{display:none!important;}}
/* Keep header hidden (contains sidebar toggle on mobile — re-enable if needed) */
/* Keep Streamlit header hidden visually
   BUT preserve sidebar toggle button */

header{{
    background:transparent!important;
    height:0!important;
}}

/* Show sidebar collapse/expand button */
button[kind="header"],
[data-testid="collapsedControl"]{{
    display:flex!important;
    visibility:visible!important;
    opacity:1!important;
    z-index:999999!important;

    background:var(--c-card)!important;
    border:1px solid var(--c-border)!important;
    border-radius:12px!important;

    width:42px!important;
    height:42px!important;

    align-items:center!important;
    justify-content:center!important;

    box-shadow:var(--sh-md)!important;
    transition:all .18s ease!important;
}}

/* Hover effect */
button[kind="header"]:hover,
[data-testid="collapsedControl"]:hover{{
    background:var(--c-hover)!important;
    transform:scale(1.05)!important;
}}

/* Arrow icon */
button[kind="header"] svg,
[data-testid="collapsedControl"] svg{{
    fill:var(--c-text)!important;
    color:var(--c-text)!important;
    width:18px!important;
    height:18px!important;
}}

/* ── ANIMATED TOP STRIPE ── */
.stApp::before{{
    content:'';
    display:block;
    position:fixed;
    top:0;left:0;right:0;
    height:2px;
    background:linear-gradient(90deg,{accent1},{accent2},{accent3},{accent1});
    background-size:200% 100%;
    animation:prem-gradient-move 6s ease infinite;
    z-index:200;
    pointer-events:none;
}}

/* ═══════════════════════════════════════════════════════════════
   LAYOUT — SINGLE CONTENT WIDTH
   clamp: never narrower than 320px, ideal ~88vw, never wider than 1080px
═══════════════════════════════════════════════════════════════ */
.main .block-container{{
    padding:clamp(1rem,3vw,2rem) clamp(0.75rem,3.5vw,2rem) clamp(3rem,6vw,5rem)!important;
    max-width:clamp(320px,88vw,1080px)!important;
    margin:0 auto!important;
    width:100%!important;
}}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR
   z-index:1000 so it sits above content but below popovers (9999)
═══════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"]{{
    background:{sidebar_bg}!important;
    border-right:1px solid var(--c-border)!important;
    z-index:1000!important;
}}
/* Sidebar text without global div reset */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown{{
    color:var(--c-text)!important;
}}
section[data-testid="stSidebar"] .stButton>button{{
    background:var(--c-card2)!important;
    color:var(--c-text)!important;
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-md)!important;
    box-shadow:none!important;
    font-size:var(--fs-sm)!important;
    font-weight:600!important;
    text-align:left!important;
    justify-content:flex-start!important;
    padding:clamp(8px,2vw,11px) clamp(12px,2.5vw,16px)!important;
    transition:all var(--t-fast)!important;
    width:100%!important;
}}
section[data-testid="stSidebar"] .stButton>button:hover{{
    background:var(--c-hover)!important;
    border-color:var(--c-a1)!important;
    transform:translateX(3px)!important;
}}
@media(max-width:768px){{
    section[data-testid="stSidebar"]{{width:clamp(240px,75vw,300px)!important;}}
}}

/* ═══════════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════════ */
.stButton>button{{
    background:linear-gradient(135deg,{accent1},{accent2})!important;
    color:#fff!important;
    border:none!important;
    border-radius:var(--r-md)!important;
    padding:clamp(8px,2vw,11px) clamp(14px,3vw,22px)!important;
    font-weight:600!important;
    font-size:var(--fs-base)!important;
    font-family:'DM Sans','Noto Sans Devanagari',sans-serif!important;
    width:100%!important;
    letter-spacing:-0.01em!important;
    cursor:pointer!important;
    line-height:1.4!important;
    transition:transform var(--t-base),box-shadow var(--t-base),filter var(--t-fast)!important;
    box-shadow:0 2px 8px {a1_glow}!important;
    position:relative!important;
    overflow:hidden!important;
}}
.stButton>button::before{{
    content:'';position:absolute;inset:0;
    background:linear-gradient(180deg,rgba(255,255,255,0.12) 0%,transparent 100%);
    pointer-events:none;border-radius:inherit;
}}
.stButton>button:hover{{
    transform:translateY(-2px) scale(1.005)!important;
    box-shadow:0 6px 20px {a1_glow}!important;
    filter:brightness(1.05)!important;
}}
.stButton>button:active{{
    transform:translateY(0) scale(0.998)!important;
    filter:brightness(0.97)!important;
}}
.stButton>button:focus-visible{{
    outline:none!important;
    box-shadow:0 0 0 3px {bg},0 0 0 5px {accent1}!important;
}}
/* Secondary buttons keep the same look (override Streamlit's ghost style) */
button[kind="secondary"],
button[data-testid="baseButton-secondary"]{{
    background:linear-gradient(135deg,{accent1},{accent2})!important;
    color:#fff!important;
    border:none!important;
    border-radius:var(--r-md)!important;
    box-shadow:0 2px 8px {a1_glow}!important;
}}
button[kind="secondary"]:hover,
button[data-testid="baseButton-secondary"]:hover{{
    transform:translateY(-2px)!important;
    filter:brightness(1.05)!important;
    box-shadow:0 6px 20px {a1_glow}!important;
}}

/* ═══════════════════════════════════════════════════════════════
   INPUTS — Text, Textarea, Selectbox
═══════════════════════════════════════════════════════════════ */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea{{
    background:var(--c-input)!important;
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-md)!important;
    color:var(--c-text)!important;
    font-family:'DM Sans','Noto Sans Devanagari',sans-serif!important;
    font-size:var(--fs-base)!important;
    padding:clamp(8px,2vw,11px) clamp(10px,2.5vw,14px)!important;
    transition:border-color var(--t-fast),box-shadow var(--t-fast)!important;
    width:100%!important;
    max-width:100%!important;
}}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{{
    border-color:var(--c-a1)!important;
    box-shadow:0 0 0 3px var(--c-a1-soft)!important;
    outline:none!important;
    background:var(--c-card)!important;
}}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{{
    color:var(--c-sub)!important;opacity:0.65!important;
}}
.stTextInput input,.stTextArea textarea{{caret-color:{accent1}!important;}}

/* Field labels */
label,
.stTextInput label,
.stTextArea label,
.stSelectbox label{{
    color:var(--c-sub)!important;
    font-weight:600!important;
    font-size:var(--fs-xs)!important;
    text-transform:uppercase!important;
    letter-spacing:0.07em!important;
    margin-bottom:5px!important;
    display:block!important;
}}

/* ── SELECTBOX — trigger ── */
.stSelectbox>div>div{{
    background:var(--c-input)!important;
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-md)!important;
    min-height:44px!important;
    width:100%!important;
    transition:border-color var(--t-fast),box-shadow var(--t-fast)!important;
}}
.stSelectbox>div>div:hover{{
    border-color:var(--c-a1)!important;
    box-shadow:0 0 0 3px var(--c-a1-soft)!important;
}}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div,
.stSelectbox [data-baseweb="select"] input{{
    color:var(--c-text)!important;
    font-size:var(--fs-base)!important;
}}
.stSelectbox svg{{fill:var(--c-sub)!important;}}

/* ── DROPDOWN POPOVER (light + dark shared) ── */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[data-testid="stWidgetDropdownList"]{{
    background:var(--c-card)!important;
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-lg)!important;
    box-shadow:var(--sh-md)!important;
    overflow:hidden!important;
    max-height:60vh!important;
    overflow-y:auto!important;
    z-index:9999!important;
}}
div[data-baseweb="option"],
li[role="option"]{{
    background:transparent!important;
    color:var(--c-text)!important;
    padding:clamp(7px,2vw,10px) clamp(10px,2.5vw,14px)!important;
    margin:2px 5px!important;
    border-radius:var(--r-sm)!important;
    font-size:var(--fs-base)!important;
    font-weight:500!important;
    transition:background var(--t-fast)!important;
    word-break:break-word!important;
    white-space:normal!important;
}}
div[data-baseweb="option"]:hover,
li[role="option"]:hover{{
    background:var(--c-hover)!important;
    color:var(--c-text)!important;
}}
div[data-baseweb="option"][aria-selected="true"],
li[role="option"][aria-selected="true"]{{
    background:var(--c-a1-soft)!important;
    color:var(--c-a1)!important;
    font-weight:700!important;
}}

/* ── RADIO ── */
.stRadio label{{
    text-transform:none!important;
    letter-spacing:0!important;
    font-size:var(--fs-base)!important;
    color:var(--c-text)!important;
}}
.stRadio [data-testid="stMarkdownContainer"] p{{color:var(--c-text)!important;}}

/* ═══════════════════════════════════════════════════════════════
   TABS — responsive wrap on mobile
═══════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"]{{
    background:var(--c-card)!important;
    border-radius:var(--r-lg)!important;
    padding:clamp(3px,1vw,6px)!important;
    border:1px solid var(--c-border)!important;
    gap:3px!important;
    box-shadow:var(--sh-sm)!important;
    flex-wrap:wrap!important;
    width:100%!important;
}}
.stTabs [data-baseweb="tab"]{{
    border-radius:var(--r-sm)!important;
    font-weight:600!important;
    font-size:var(--fs-sm)!important;
    color:var(--c-sub)!important;
    padding:clamp(6px,2vw,9px) clamp(12px,3vw,20px)!important;
    border:none!important;
    transition:all var(--t-fast)!important;
    flex-shrink:0!important;
}}
.stTabs [aria-selected="true"]{{
    background:linear-gradient(135deg,{accent1},{accent2})!important;
    color:#fff!important;
    box-shadow:0 3px 12px {a1_glow}!important;
}}
.stTabs [data-baseweb="tab-panel"]{{background:transparent!important;padding:18px 0 0!important;}}
@media(max-width:480px){{
    .stTabs [data-baseweb="tab"]{{
        flex:1 1 calc(50% - 4px)!important;
        text-align:center!important;
    }}
}}

/* ═══════════════════════════════════════════════════════════════
   EXPANDER
   FIX: border uses var(--c-border), NOT var(--c-text) or #000
═══════════════════════════════════════════════════════════════ */
[data-testid="stExpander"]{{
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-md)!important;
    background:var(--c-card)!important;
    margin-bottom:var(--sp-4)!important;
    overflow:hidden!important;
    box-shadow:var(--sh-sm)!important;
}}
.streamlit-expanderHeader{{
    background:var(--c-card)!important;
    border-radius:var(--r-md)!important;
    font-weight:600!important;
    color:var(--c-text)!important;
    border:none!important;
    padding:clamp(10px,2.5vw,13px) clamp(12px,3vw,16px)!important;
    font-size:var(--fs-base)!important;
    transition:background var(--t-fast)!important;
}}
.streamlit-expanderHeader:hover{{
    background:var(--c-hover)!important;
}}
.streamlit-expanderContent{{
    background:var(--c-card)!important;
    border-top:1px solid var(--c-border)!important;
    padding:clamp(12px,3vw,18px) clamp(12px,3.5vw,20px)!important;
}}

/* ═══════════════════════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════════════════════ */
.stProgress>div>div{{
    background:linear-gradient(90deg,{accent1},{accent2})!important;
    border-radius:99px!important;
}}
.stProgress>div{{
    background:var(--c-border)!important;
    border-radius:99px!important;
    height:5px!important;
}}

/* ═══════════════════════════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════════════════════════ */
.stSuccess{{background:{green_bg}!important;border:1px solid {green_bd}!important;border-radius:var(--r-md)!important;color:{green_text}!important;}}
.stInfo   {{background:{blue_bg}!important; border:1px solid {blue_bd}!important; border-radius:var(--r-md)!important;color:{blue_text}!important;}}
.stWarning{{background:{amber_bg}!important;border:1px solid {amber_bd}!important;border-radius:var(--r-md)!important;color:{amber_text}!important;}}
.stError  {{background:{red_bg}!important;  border:1px solid {red_bd}!important;  border-radius:var(--r-md)!important;color:{red_text}!important;}}

/* ═══════════════════════════════════════════════════════════════
   DATA TABLE
═══════════════════════════════════════════════════════════════ */
div[data-testid="stDataFrame"]{{display:block;overflow-x:auto;width:100%;}}
div[data-testid="stDataFrame"] *,table,th,td{{
    color:var(--c-text)!important;
    border-color:var(--c-border)!important;
    font-size:var(--fs-sm)!important;
}}

/* ═══════════════════════════════════════════════════════════════
   MISC
═══════════════════════════════════════════════════════════════ */
hr{{
    border:none;height:1px;
    background:linear-gradient(90deg,transparent,{border},transparent);
    margin:var(--sp-6) 0!important;
}}
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:var(--c-border);border-radius:99px;}}
::-webkit-scrollbar-thumb:hover{{background:var(--c-sub);}}

/* ═══════════════════════════════════════════════════════════════
   ██  COMPONENT LIBRARY
═══════════════════════════════════════════════════════════════ */

/* ── HERO BANNER ── */
.prem-hero{{
    background:linear-gradient(135deg,{hero_from} 0%,{hero_mid} 50%,{hero_to} 100%);
    border-radius:var(--r-xl);
    padding:var(--sp-8) var(--sp-8) var(--sp-6);
    color:#fff;
    margin-bottom:var(--sp-6);
    position:relative;
    overflow:hidden;
    box-shadow:var(--sh-lg);
    border:1px solid rgba(255,255,255,0.10);
    word-break:break-word;
}}
.prem-hero::before{{
    content:'';position:absolute;top:-80px;right:-60px;
    width:clamp(180px,30vw,280px);height:clamp(180px,30vw,280px);
    background:radial-gradient(circle,rgba(255,255,255,0.09) 0%,transparent 70%);
    pointer-events:none;animation:prem-float 8s ease-in-out infinite;
}}
.prem-hero::after{{
    content:'';position:absolute;bottom:-60px;left:10%;
    width:clamp(140px,24vw,220px);height:clamp(140px,24vw,220px);
    background:radial-gradient(circle,rgba(255,255,255,0.05) 0%,transparent 70%);
    pointer-events:none;animation:prem-float 10s ease-in-out infinite reverse;
}}
.prem-hero-title{{
    font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:clamp(1.4rem,4.5vw,2.25rem);
    font-weight:800;line-height:1.2;
    margin-bottom:var(--sp-1);
    position:relative;z-index:1;
    color:#fff;letter-spacing:-0.03em;
    word-break:break-word;
}}
.prem-hero-sub{{
    font-size:clamp(0.82rem,2.2vw,1rem);
    margin:0 0 var(--sp-1);
    opacity:0.82;position:relative;z-index:1;
    color:rgba(255,255,255,0.88);font-weight:400;
    max-width:60ch;
}}
.prem-hero-avatar{{
    position:absolute;
    top:clamp(14px,3vw,24px);
    right:clamp(14px,3vw,26px);
    width:clamp(38px,6vw,50px);
    height:clamp(38px,6vw,50px);
    border-radius:50%;
    background:rgba(255,255,255,0.15);
    border:1px solid rgba(255,255,255,0.28);
    display:flex;align-items:center;justify-content:center;
    font-weight:700;font-size:var(--fs-md);
    color:#fff;z-index:1;
    backdrop-filter:blur(12px);
    box-shadow:0 4px 14px rgba(0,0,0,0.20);
}}
.prem-hero-stats{{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(clamp(90px,18vw,120px),1fr));
    gap:var(--sp-2);
    margin-top:var(--sp-5);
    position:relative;z-index:1;
}}
.prem-hstat{{
    background:rgba(255,255,255,0.10);
    border:1px solid rgba(255,255,255,0.16);
    border-radius:var(--r-md);
    padding:var(--sp-3) var(--sp-2);
    text-align:center;
    backdrop-filter:blur(10px);
    transition:background var(--t-fast),transform var(--t-fast);
    cursor:default;
}}
.prem-hstat:hover{{background:rgba(255,255,255,0.18);transform:translateY(-2px);}}
.prem-hstat-num{{
    font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:clamp(1.6rem,4.5vw,2.5rem);
    font-weight:800;line-height:1;
    margin-bottom:var(--sp-1);color:#fff;letter-spacing:-0.03em;
}}
.prem-hstat-lbl{{
    font-size:var(--fs-2xs);font-weight:600;
    text-transform:uppercase;letter-spacing:0.08em;
    color:rgba(255,255,255,0.60);
}}
.prem-hstat.h-blue  .prem-hstat-num{{color:#BAC8FF;}}
.prem-hstat.h-amber .prem-hstat-num{{color:#FDE68A;}}
.prem-hstat.h-green .prem-hstat-num{{color:#6EE7B7;}}
.prem-hstat.h-red   .prem-hstat-num{{color:#FCA5A5;}}

/* ── CARD ── */
.prem-card{{
    background:var(--c-card);
    border-radius:var(--r-lg);
    padding:var(--sp-6);
    margin:var(--sp-2) 0;
    border:1px solid var(--c-border);
    box-shadow:var(--sh-sm);
    transition:transform var(--t-base),box-shadow var(--t-base),border-color var(--t-fast);
    position:relative;overflow:hidden;
    word-break:break-word;
}}
.prem-card:hover{{transform:translateY(-2px);box-shadow:var(--sh-md);border-color:{accent1}44;}}

/* ── STAT CARD ── */
.prem-stat-card{{
    background:var(--c-card);
    border-radius:var(--r-lg);
    padding:var(--sp-6) var(--sp-4) var(--sp-4);
    text-align:center;
    border:1px solid var(--c-border);
    box-shadow:var(--sh-sm);
    position:relative;overflow:hidden;
    transition:transform var(--t-base),box-shadow var(--t-base);
    height:100%;
    display:flex;flex-direction:column;justify-content:center;
}}
.prem-stat-card::before{{
    content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,{accent1},{accent2});
    border-radius:var(--r-lg) var(--r-lg) 0 0;
}}
.prem-stat-card::after{{
    content:'';position:absolute;top:3px;left:0;right:0;bottom:0;
    background:linear-gradient(180deg,{a1_soft} 0%,transparent 50%);
    pointer-events:none;
}}
.prem-stat-card:hover{{transform:translateY(-4px);box-shadow:var(--sh-md);}}
.prem-stat-num{{
    font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:clamp(1.75rem,5vw,2.5rem);
    font-weight:800;line-height:1.1;color:var(--c-text);
    letter-spacing:-0.04em;position:relative;z-index:1;
}}
.prem-stat-lbl{{
    font-size:var(--fs-xs);color:var(--c-sub);font-weight:600;
    text-transform:uppercase;letter-spacing:0.07em;
    margin-top:var(--sp-2);position:relative;z-index:1;
}}

/* ── ACTION CARD ── */
.prem-action-card{{
    background:var(--c-card);
    border-radius:var(--r-lg);
    padding:var(--sp-6) var(--sp-4) var(--sp-5);
    text-align:center;
    border:1px solid var(--c-border);
    cursor:pointer;
    transition:all var(--t-base);
    box-shadow:var(--sh-sm);
    position:relative;overflow:hidden;
    height:100%;
    display:flex;flex-direction:column;align-items:center;justify-content:center;
}}
.prem-action-card::before{{
    content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,{accent1},{accent2},{accent3});
    transform:scaleX(0);transition:transform var(--t-base);
    transform-origin:left;
}}
.prem-action-card:hover{{
    transform:translateY(-5px);
    box-shadow:var(--sh-md);
    border-color:{accent1}55;
}}
.prem-action-card:hover::before{{transform:scaleX(1);}}
.prem-action-card:hover .prem-action-icon{{transform:scale(1.10);}}
.prem-action-icon{{
    width:clamp(44px,8vw,52px);
    height:clamp(44px,8vw,52px);
    border-radius:var(--r-md);
    display:flex;align-items:center;justify-content:center;
    font-size:var(--icon-xl);
    margin:0 auto var(--sp-3);
    transition:transform var(--t-fast);
}}
.prem-action-label{{
    font-size:var(--fs-sm);font-weight:700;
    color:var(--c-text);line-height:1.35;
    letter-spacing:-0.01em;
}}

/* ── SECTION HEADER ── */
.prem-section-header{{
    font-size:var(--fs-xs);font-weight:700;
    text-transform:uppercase;letter-spacing:0.10em;
    color:var(--c-sub);
    margin:var(--sp-8) 0 var(--sp-3);
    display:flex;align-items:center;gap:10px;
}}
.prem-section-header::before{{
    content:'';width:3px;height:14px;
    background:linear-gradient(180deg,{accent1},{accent2});
    border-radius:99px;flex-shrink:0;
}}
.prem-section-header::after{{
    content:'';flex:1;height:1px;
    background:linear-gradient(to right,{border}80,transparent);
}}

/* ── COMPLAINT ITEM
   FIX: border uses var(--c-border), NOT var(--c-text)
── */
.prem-complaint-item{{
    background:var(--c-card);
    border-radius:var(--r-lg);
    padding:clamp(10px,2.5vw,18px) clamp(14px,3.5vw,24px);
    margin:var(--sp-2) 0;
    border:1px solid var(--c-border);
    border-left:4px solid {accent1};
    box-shadow:var(--sh-sm);
    transition:transform var(--t-fast),border-color var(--t-fast),box-shadow var(--t-base);
    word-break:break-word;
    overflow-x:hidden;
}}
.prem-complaint-item:hover{{
    transform:translateX(5px);
    border-left-color:{accent2};
    box-shadow:var(--sh-md);
}}
.prem-complaint-id{{
    font-size:var(--fs-xs);color:{accent1};font-weight:700;
    letter-spacing:0.05em;font-family:'DM Mono','Courier New',monospace;
    background:{a1_soft};padding:3px 10px;border-radius:7px;
    display:inline-block;margin-bottom:var(--sp-2);
    border:1px solid {accent1}22;
}}
.prem-complaint-title{{
    font-size:var(--fs-md);font-weight:700;margin:var(--sp-1) 0;
    color:var(--c-text);line-height:1.4;letter-spacing:-0.01em;
}}
.prem-complaint-desc{{
    font-size:var(--fs-base);color:var(--c-sub);
    line-height:1.65;margin:var(--sp-1) 0 var(--sp-3);
}}
.prem-complaint-meta{{
    font-size:var(--fs-xs);color:var(--c-sub);
    display:flex;gap:var(--sp-3);flex-wrap:wrap;align-items:center;
}}

/* ── BADGES & TAGS ── */
.prem-tag{{
    background:{tag_bg};color:{tag_col};border-radius:7px;
    padding:3px 10px;font-size:var(--fs-xs);font-weight:700;
    display:inline-flex;align-items:center;white-space:nowrap;
    letter-spacing:0.01em;border:1px solid {tag_col}22;
}}
.prem-badge{{
    border-radius:7px;padding:3px 9px;
    font-size:var(--fs-2xs);font-weight:700;
    display:inline-flex;align-items:center;white-space:nowrap;
    letter-spacing:0.04em;text-transform:uppercase;
    vertical-align:middle;
}}
.prem-badge-high      {{background:{red_bg};  color:{red_text};  border:1px solid {red_bd};}}
.prem-badge-medium    {{background:{amber_bg};color:{amber_text};border:1px solid {amber_bd};}}
.prem-badge-low       {{background:{green_bg};color:{green_text};border:1px solid {green_bd};}}
.prem-badge-pending   {{background:{amber_bg};color:{amber_text};border:1px solid {amber_bd};}}
.prem-badge-progress  {{background:{blue_bg}; color:{blue_text}; border:1px solid {blue_bd};}}
.prem-badge-resolved  {{background:{green_bg};color:{green_text};border:1px solid {green_bd};}}
.prem-badge-closed    {{background:{card_bg2};color:{subtext};   border:1px solid {border};}}
.prem-badge-rejected  {{background:{red_bg};  color:{red_text};  border:1px solid {red_bd};}}
.prem-badge-emergency{{
    background:linear-gradient(135deg,#EF4444,#DC2626);
    color:#fff;border:none;
    box-shadow:0 0 0 3px rgba(239,68,68,0.22);
    animation:prem-pulse-emergency 2.5s ease infinite;
}}

/* ── NOTIFICATION CARD ── */
.prem-notif-card{{
    background:var(--c-card);
    border-radius:var(--r-md);
    padding:var(--sp-3) var(--sp-5);
    margin:var(--sp-2) 0;
    border:1px solid var(--c-border);
    display:flex;gap:var(--sp-3);align-items:flex-start;
    flex-wrap:wrap;
    box-shadow:var(--sh-sm);
    transition:transform var(--t-fast),box-shadow var(--t-base);
    position:relative;overflow:hidden;
    word-break:break-word;
}}
.prem-notif-card::before{{
    content:'';position:absolute;top:0;left:0;bottom:0;width:0;
    background:{a1_soft};transition:width var(--t-base);
}}
.prem-notif-card:hover{{transform:translateX(5px);box-shadow:var(--sh-md);}}
.prem-notif-card:hover::before{{width:3px;}}
.prem-notif-dot{{
    width:9px;height:9px;border-radius:50%;background:{accent1};
    flex-shrink:0;margin-top:5px;box-shadow:0 0 0 4px {a1_soft};
}}
.prem-notif-title{{font-weight:700;font-size:var(--fs-base);color:var(--c-text);margin-bottom:3px;}}
.prem-notif-msg  {{font-size:var(--fs-sm);color:var(--c-sub);line-height:1.55;}}
.prem-notif-time {{font-size:var(--fs-xs);color:var(--c-sub);margin-top:5px;font-family:'DM Mono',monospace;}}

/* ── NOTIFICATION BAR ── */
.prem-notif-bar{{
    background:{amber_bg};border:1px solid {amber_bd};
    border-radius:var(--r-md);
    padding:var(--sp-3) var(--sp-4);
    display:flex;align-items:center;gap:var(--sp-2);flex-wrap:wrap;
    margin-bottom:var(--sp-4);cursor:pointer;
    transition:box-shadow var(--t-fast),transform var(--t-fast);
}}
.prem-notif-bar:hover{{box-shadow:var(--sh-sm);transform:translateY(-1px);}}
.prem-notif-bar-dot{{width:7px;height:7px;border-radius:50%;background:{amber_text};flex-shrink:0;}}
.prem-notif-bar-text{{
    font-size:var(--fs-sm);color:{amber_text}!important;
    font-weight:600;flex:1;min-width:min(150px,60%);
}}
.prem-notif-bar-badge{{
    background:{amber_text};color:#fff!important;
    border-radius:99px;padding:2px 9px;
    font-size:var(--fs-2xs);font-weight:700;
    white-space:nowrap;
}}

/* ── TIMELINE ── */
.prem-timeline{{padding:4px 0;}}
.prem-tl-item{{display:flex;gap:var(--sp-3);align-items:flex-start;margin-bottom:4px;flex-wrap:nowrap;}}
.prem-tl-dot{{
    width:22px;height:22px;border-radius:50%;flex-shrink:0;
    display:flex;align-items:center;justify-content:center;
    font-size:0.58rem;font-weight:800;margin-top:2px;
    transition:transform var(--t-fast);
}}
.prem-tl-dot:hover{{transform:scale(1.15);}}
.prem-tl-dot.done  {{background:{accent1};color:#fff;box-shadow:0 0 0 4px {a1_soft};}}
.prem-tl-dot.active{{background:{accent2};color:#fff;box-shadow:0 0 0 4px {a2_soft};animation:prem-pulse-ring 2.5s ease infinite;}}
.prem-tl-dot.idle  {{background:{card_bg2};color:{subtext};border:1px solid {border};}}
.prem-tl-info{{flex:1;padding:2px 0;min-width:0;}}
.prem-tl-label{{font-size:var(--fs-sm);font-weight:600;color:var(--c-text);letter-spacing:-0.01em;word-break:break-word;}}
.prem-tl-time {{font-size:var(--fs-xs);color:var(--c-sub);margin-top:2px;font-family:'DM Mono',monospace;}}
.prem-tl-line {{width:2px;height:14px;background:var(--c-border);margin-left:10px;border-radius:99px;}}
.prem-tl-line.done{{background:linear-gradient(to bottom,{accent1}88,{border});}}

/* ── SLA BAR ── */
.prem-sla-bar{{
    background:var(--c-card2);border:1px solid var(--c-border);
    border-radius:var(--r-md);padding:10px 14px;
    display:flex;align-items:center;gap:var(--sp-2);flex-wrap:wrap;
    margin-top:var(--sp-3);font-size:var(--fs-sm);color:var(--c-sub);
}}
.prem-sla-bar.overdue{{background:{red_bg};border-color:{red_bd};color:{red_text};}}
.prem-sla-bar strong{{color:var(--c-text);font-weight:700;}}
.prem-sla-bar.overdue strong{{color:{red_text};}}

/* ── FEEDBACK CARD ── */
.prem-feedback-card{{
    background:var(--c-card);border:1px solid {green_bd};
    border-radius:var(--r-lg);padding:var(--sp-6);margin-bottom:var(--sp-3);
    box-shadow:0 0 0 3px {green_bg};transition:transform var(--t-fast);
    word-break:break-word;
}}
.prem-feedback-card:hover{{transform:translateY(-2px);}}
.prem-feedback-card .prem-fb-head{{display:flex;align-items:center;gap:var(--sp-3);margin-bottom:var(--sp-3);flex-wrap:wrap;}}
.prem-fb-icon{{
    width:40px;height:40px;border-radius:var(--r-md);
    background:{green_bg};border:1px solid {green_bd};
    display:flex;align-items:center;justify-content:center;
    font-size:var(--icon-md);flex-shrink:0;
}}
.prem-fb-title{{font-weight:700;font-size:var(--fs-md);color:var(--c-text);}}
.prem-fb-sub  {{font-size:var(--fs-xs);color:var(--c-sub);margin-top:2px;}}
.prem-fb-desc {{font-size:var(--fs-sm);color:var(--c-sub);line-height:1.65;margin-bottom:var(--sp-4);}}

/* ── RATING CARD ── */
.prem-rating-card{{
    background:var(--c-card);border:1px solid {blue_bd};
    border-radius:var(--r-lg);padding:var(--sp-6);margin-bottom:var(--sp-3);
    box-shadow:0 0 0 3px {blue_bg};
}}

/* ── SCHEME CARD ── */
.prem-scheme-card{{
    background:var(--c-card);border-radius:var(--r-lg);overflow:hidden;
    border:1px solid var(--c-border);margin-bottom:var(--sp-4);
    box-shadow:var(--sh-sm);
    transition:transform var(--t-base),box-shadow var(--t-base),border-color var(--t-fast);
    word-break:break-word;
}}
.prem-scheme-card:hover{{transform:translateY(-3px);box-shadow:var(--sh-md);border-color:{accent1}44;}}
.prem-scheme-body {{padding:var(--sp-5) var(--sp-6);}}
.prem-scheme-title{{font-size:var(--fs-md);font-weight:700;margin-bottom:var(--sp-2);color:var(--c-text);}}
.prem-scheme-desc {{font-size:var(--fs-sm);color:var(--c-sub);line-height:1.68;}}

/* ── LEADERBOARD ── */
.prem-lb-card{{
    background:var(--c-card);border-radius:var(--r-lg);
    padding:var(--sp-4) var(--sp-6);margin:var(--sp-2) 0;
    border:1px solid var(--c-border);box-shadow:var(--sh-sm);
    display:flex;gap:var(--sp-5);align-items:center;flex-wrap:wrap;
    transition:transform var(--t-fast),box-shadow var(--t-base);
    position:relative;overflow:hidden;word-break:break-word;
}}
.prem-lb-card::before{{
    content:'';position:absolute;top:0;left:0;bottom:0;width:4px;
    background:transparent;border-radius:4px 0 0 4px;transition:background var(--t-fast);
}}
.prem-lb-card:hover{{transform:translateX(5px);box-shadow:var(--sh-md);}}
.prem-lb-card:hover::before{{background:{accent1};}}
.prem-lb-card.rank-1{{background:linear-gradient(135deg,{card_bg} 60%,{amber_bg});border-color:#F59E0B44;}}
.prem-lb-card.rank-1::before{{background:#FFD700;}}
.prem-lb-card.rank-2::before{{background:#C0C0C0;}}
.prem-lb-card.rank-3::before{{background:#CD7F32;}}
.prem-lb-card.ineligible{{opacity:.50;background:{card_bg2};}}
.prem-lb-rank{{
    font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:var(--fs-2xl);font-weight:800;min-width:56px;
    text-align:center;color:{amber_text};letter-spacing:-0.04em;
}}
.prem-lb-info{{flex:1;min-width:0;}}
.prem-lb-name{{font-weight:700;font-size:var(--fs-md);margin-bottom:6px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;color:var(--c-text);}}
.prem-lb-dept{{font-size:var(--fs-xs);font-weight:600;background:{tag_bg};padding:2px 10px;border-radius:99px;color:{tag_col};}}
.prem-lb-stats{{display:flex;gap:var(--sp-5);flex-wrap:wrap;margin:var(--sp-2) 0;}}
.prem-lb-stat-item{{text-align:center;min-width:52px;}}
.prem-lb-stat-lbl{{font-size:var(--fs-2xs);text-transform:uppercase;letter-spacing:0.07em;color:var(--c-sub);}}
.prem-lb-stat-val{{font-weight:700;font-size:var(--fs-base);color:var(--c-text);}}

/* ── CUSTOM PROGRESS BAR ── */
.prem-prog-wrap{{background:var(--c-border);border-radius:99px;height:20px;overflow:hidden;position:relative;}}
.prem-prog-fill{{
    height:100%;border-radius:99px;
    display:flex;align-items:center;justify-content:center;
    transition:width 0.5s cubic-bezier(0.4,0,0.2,1);
    position:relative;overflow:hidden;
}}
.prem-prog-fill::after{{
    content:'';position:absolute;inset:0;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.18),transparent);
    background-size:200% 100%;animation:prem-shimmer 2.5s ease infinite;
}}
.prem-prog-text{{font-size:var(--fs-xs);font-weight:700;color:#fff;position:relative;z-index:1;}}

/* ── PERFORMER GRID ── */
.prem-performer-grid{{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(clamp(150px,28vw,190px),1fr));
    gap:var(--sp-3);margin:var(--sp-4) 0;
}}
.prem-performer-card{{
    background:var(--c-card);border-radius:var(--r-lg);
    padding:var(--sp-6) var(--sp-4);text-align:center;
    border:1px solid var(--c-border);box-shadow:var(--sh-sm);
    transition:transform var(--t-base),box-shadow var(--t-base);
    position:relative;overflow:hidden;
    height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;
}}
.prem-performer-card::after{{
    content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,{accent1},{accent2});
    transform:scaleX(0);transform-origin:left;transition:transform var(--t-base);
}}
.prem-performer-card:hover{{transform:translateY(-5px);box-shadow:var(--sh-md);}}
.prem-performer-card:hover::after{{transform:scaleX(1);}}
.prem-rank-badge{{
    background:linear-gradient(135deg,{accent1},{accent2});color:#fff;
    width:34px;height:34px;border-radius:50%;
    display:inline-flex;align-items:center;justify-content:center;
    font-weight:800;font-size:var(--fs-sm);margin-bottom:var(--sp-3);
    box-shadow:0 4px 14px {a1_glow};
}}
.prem-performer-name {{font-weight:700;font-size:var(--fs-base);margin-bottom:4px;color:var(--c-text);}}
.prem-performer-dept {{font-size:var(--fs-xs);color:var(--c-sub);margin-bottom:var(--sp-2);}}
.prem-performer-stars{{font-size:var(--fs-sm);color:#F59E0B;margin-bottom:5px;}}
.prem-performer-stats{{font-size:var(--fs-xs);color:var(--c-sub);}}

/* ── EMPTY STATE ── */
.prem-empty-state{{
    text-align:center;
    padding:clamp(2.5rem,8vw,5rem) clamp(1rem,4vw,2rem);
    background:var(--c-card);border-radius:var(--r-xl);
    border:1px dashed var(--c-border);
    position:relative;overflow:hidden;
}}
.prem-empty-state::before{{
    content:'';position:absolute;top:50%;left:50%;
    transform:translate(-50%,-50%);width:200px;height:200px;
    background:radial-gradient(circle,{a1_soft} 0%,transparent 70%);pointer-events:none;
}}
.prem-empty-icon {{font-size:var(--icon-2xl);margin-bottom:var(--sp-4);opacity:.80;display:block;position:relative;z-index:1;}}
.prem-empty-title{{
    font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:var(--fs-lg);font-weight:700;
    color:var(--c-text)!important;
    margin-bottom:var(--sp-2);position:relative;z-index:1;
}}
.prem-empty-sub  {{
    font-size:var(--fs-sm);
    color:var(--c-sub)!important;
    margin-bottom:var(--sp-6);line-height:1.65;position:relative;z-index:1;
}}

/* ── WELCOME SCREEN ── */
.prem-welcome{{text-align:center;padding:clamp(40px,10vw,60px) 20px 36px;}}
.prem-welcome-logo {{font-size:clamp(3.5rem,8vw,5rem);display:block;margin-bottom:var(--sp-4);animation:prem-float 4s ease-in-out infinite;}}
.prem-welcome-title{{
    font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:clamp(1.5rem,5vw,2.25rem);
    font-weight:800;margin-bottom:var(--sp-3);
    color:var(--c-text);letter-spacing:-0.04em;
}}
.prem-welcome-sub  {{
    font-size:var(--fs-md);color:var(--c-sub);
    margin-bottom:var(--sp-8);line-height:1.75;
    max-width:min(460px,90%);margin-left:auto;margin-right:auto;
}}

/* ── CHAT HEADER ── */
.prem-chat-header{{
    background:linear-gradient(135deg,{accent1},{accent2});
    padding:var(--sp-4) var(--sp-6);color:#fff;
    font-weight:700;font-size:var(--fs-base);
    display:flex;align-items:center;gap:var(--sp-2);
    border-radius:var(--r-lg) var(--r-lg) 0 0;
    box-shadow:0 4px 20px {a1_glow};
}}

/* ── TIP BAR ── */
.prem-tip-bar{{
    background:var(--c-card);border:1px solid var(--c-border);
    border-radius:var(--r-md);padding:var(--sp-3) var(--sp-4);
    display:flex;align-items:flex-start;gap:var(--sp-3);
    margin-top:var(--sp-6);box-shadow:var(--sh-sm);
    transition:border-color var(--t-fast);
    word-break:break-word;
}}
.prem-tip-bar:hover{{border-color:{accent1}44;}}
.prem-tip-icon{{font-size:var(--icon-sm);flex-shrink:0;opacity:.75;margin-top:2px;}}
.prem-tip-text{{font-size:var(--fs-sm);color:var(--c-sub);flex:1;line-height:1.58;}}
.prem-tip-text strong{{color:var(--c-text);font-weight:700;}}

/* ── GLASS SURFACE ── */
.prem-glass{{
    background:{glass_bg}!important;
    backdrop-filter:blur(16px)!important;
    -webkit-backdrop-filter:blur(16px)!important;
    border:1px solid {glass_bd}!important;
    border-radius:var(--r-lg)!important;
}}

/* ── DIVIDER ── */
.prem-divider{{
    display:flex;align-items:center;gap:var(--sp-3);
    margin:var(--sp-5) 0;color:var(--c-sub);
    font-size:var(--fs-xs);font-weight:700;
    text-transform:uppercase;letter-spacing:0.08em;
}}
.prem-divider::before,.prem-divider::after{{content:'';flex:1;height:1px;background:var(--c-border);}}

/* ── INLINE CHIP ── */
.prem-chip{{
    display:inline-flex;align-items:center;gap:5px;
    background:{a1_soft};border:1px solid {accent1}22;
    border-radius:99px;padding:3px 12px;
    font-size:var(--fs-xs);font-weight:700;color:{accent1};
    font-family:'DM Mono',monospace;
}}

/* ── FILTER CHIPS ── */
.prem-filter-chips{{
    display:flex;gap:var(--sp-2);flex-wrap:wrap;
    margin:var(--sp-1) 0 var(--sp-2);
}}
.prem-filter-chip{{
    padding:6px 14px;border-radius:30px;
    font-size:var(--fs-xs);font-weight:700;
    border:1px solid var(--c-border);
    background:var(--c-card);color:var(--c-sub);
    white-space:nowrap;cursor:pointer;
    transition:all var(--t-fast);
}}
.prem-filter-chip.active{{
    background:linear-gradient(135deg,{accent1},{accent2});
    color:#fff;border-color:transparent;
    box-shadow:0 4px 12px {a1_glow};
}}
.prem-filter-chip:hover:not(.active){{background:var(--c-hover);border-color:{accent1}55;}}

/* ── FORM SECTION CARD ── */
.prem-form-card{{
    background:var(--c-card);border:1px solid var(--c-border);
    border-radius:var(--r-xl);padding:var(--sp-6);
    margin-bottom:var(--sp-4);box-shadow:var(--sh-sm);
}}
.prem-form-section-label{{
    font-size:var(--fs-xs);font-weight:700;text-transform:uppercase;
    letter-spacing:0.09em;color:var(--c-sub);margin-bottom:var(--sp-3);
    display:flex;align-items:center;gap:7px;
}}
.prem-form-section-label::before{{
    content:'';width:3px;height:13px;
    background:linear-gradient(180deg,{accent1},{accent2});border-radius:99px;
}}

/* ── COMPLAINT CARD (alternative class name)
   FIX: border uses var(--c-border), NOT #000
── */
.complaint-card{{
    background:var(--c-card);
    border-radius:var(--r-xl);
    margin-bottom:1rem;
    border:1px solid var(--c-border)!important;
    transition:all var(--t-base);
    overflow:hidden;
    word-break:break-word;
}}
.complaint-card:hover{{
    transform:translateX(5px);
    border-color:{accent1}!important;
    box-shadow:0 8px 20px -12px rgba(0,0,0,0.20);
}}
.complaint-priority-high  {{border-left:4px solid #EF4444;}}
.complaint-priority-medium{{border-left:4px solid #F59E0B;}}
.complaint-priority-low   {{border-left:4px solid #10B981;}}
.complaint-header{{
    display:flex;justify-content:space-between;align-items:center;
    flex-wrap:wrap;gap:var(--sp-2);margin-bottom:var(--sp-3);
}}
/* status / priority badges (alternative classes) */
.badge-status{{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:30px;font-size:var(--fs-xs);font-weight:700;white-space:nowrap;}}
.badge-pending    {{background:{amber_bg};color:{amber_text};}}
.badge-in_progress{{background:{blue_bg}; color:{blue_text};}}
.badge-resolved   {{background:{green_bg};color:{green_text};}}
.badge-closed     {{background:{card_bg2};color:{subtext};}}
.badge-rejected   {{background:{red_bg};  color:{red_text};}}
.badge-priority{{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:30px;font-size:var(--fs-xs);font-weight:700;white-space:nowrap;}}
.badge-priority-high  {{background:{red_bg};  color:{red_text};}}
.badge-priority-medium{{background:{amber_bg};color:{amber_text};}}
.badge-priority-low   {{background:{green_bg};color:{green_text};}}

/* Complaint description text box */
.complaint-desc-box{{
    background:var(--c-card2);padding:var(--sp-3) var(--sp-4);
    border-radius:var(--r-md);margin:var(--sp-3) 0;
    border:1px solid var(--c-border);
    color:var(--c-text)!important;
    font-size:var(--fs-base);line-height:1.6;
    white-space:pre-wrap;word-break:break-word;
    max-height:clamp(140px,25vh,200px);overflow-y:auto;
}}
.complaint-meta{{
    display:flex;gap:var(--sp-3);flex-wrap:wrap;
    font-size:var(--fs-xs);color:var(--c-sub);margin-bottom:var(--sp-3);
}}
.action-buttons{{display:flex;gap:var(--sp-2);flex-wrap:wrap;margin-top:var(--sp-2);}}

/* ── HEATMAP LEGEND ── */
.prem-heatmap-legend{{display:flex;gap:var(--sp-4);flex-wrap:wrap;margin-top:var(--sp-4);font-size:var(--fs-sm);font-weight:600;color:var(--c-sub);}}
.prem-legend-item{{display:flex;align-items:center;gap:6px;}}
.prem-legend-dot {{width:10px;height:10px;border-radius:50%;flex-shrink:0;}}

/* ═══════════════════════════════════════════════════════════════
   ANIMATIONS  (defined ONCE — not duplicated)
═══════════════════════════════════════════════════════════════ */
@keyframes prem-fade-up{{
    from{{opacity:0;transform:translateY(14px);}}
    to  {{opacity:1;transform:translateY(0);}}
}}
@keyframes prem-fade-in {{
    from{{opacity:0;}}
    to  {{opacity:1;}}
}}
@keyframes prem-scale-in{{
    from{{opacity:0;transform:scale(0.96);}}
    to  {{opacity:1;transform:scale(1);}}
}}
@keyframes prem-pulse-ring{{
    0%  {{box-shadow:0 0 0 0 {a1_glow};}}
    70% {{box-shadow:0 0 0 12px rgba(99,102,241,0);}}
    100%{{box-shadow:0 0 0 0 rgba(99,102,241,0);}}
}}
@keyframes prem-pulse-emergency{{
    0%  {{box-shadow:0 0 0 0 rgba(239,68,68,.40);}}
    70% {{box-shadow:0 0 0 12px rgba(239,68,68,0);}}
    100%{{box-shadow:0 0 0 0 rgba(239,68,68,0);}}
}}
@keyframes prem-shimmer{{
    0%  {{background-position:-200% 0;}}
    100%{{background-position:200% 0;}}
}}
@keyframes prem-gradient-move{{
    0%,100%{{background-position:0% 50%;}}
    50%    {{background-position:100% 50%;}}
}}
@keyframes prem-float{{
    0%,100%{{transform:translateY(0);}}
    50%    {{transform:translateY(-7px);}}
}}

/* Entrance animations */
.prem-card,.prem-complaint-item,.prem-notif-card,
.prem-scheme-card,.prem-lb-card,.prem-hero{{animation:prem-fade-up 0.26s ease both;}}
.prem-stat-card{{animation:prem-scale-in 0.26s ease both;}}

/* ═══════════════════════════════════════════════════════════════
   RESPONSIVE BREAKPOINTS
   Mobile-first: base styles = mobile, media queries add complexity
═══════════════════════════════════════════════════════════════ */

/* ── 1024px — Tablet landscape / small laptop ── */
@media(max-width:1024px){{
    .main .block-container{{
        max-width:96vw!important;
        padding-left:clamp(0.75rem,2.5vw,1.5rem)!important;
        padding-right:clamp(0.75rem,2.5vw,1.5rem)!important;
    }}
    .prem-hero-stats{{grid-template-columns:repeat(auto-fit,minmax(clamp(80px,16vw,110px),1fr));}}
}}

/* ── 768px — Tablet portrait / large phone ── */
@media(max-width:768px){{
    .main .block-container{{padding:0.9rem 0.75rem 2.5rem!important;max-width:100%!important;}}
    .prem-hero{{padding:var(--sp-5) var(--sp-4) var(--sp-4);border-radius:var(--r-lg);}}
    .prem-hero-title{{font-size:clamp(1.25rem,5vw,1.75rem);}}
    .prem-hero-avatar{{display:none;}}
    .prem-hero::before,.prem-hero::after{{display:none;}}
    .prem-hero-stats{{grid-template-columns:repeat(2,1fr);gap:var(--sp-2);}}
    .prem-hstat-num{{font-size:clamp(1.4rem,5vw,2rem);}}
    .prem-action-card{{padding:var(--sp-4) var(--sp-3);border-radius:var(--r-md);}}
    .prem-action-icon{{width:42px;height:42px;font-size:var(--icon-lg);}}
    .prem-stat-card{{border-radius:var(--r-md);padding:var(--sp-4) var(--sp-3) var(--sp-3);}}
    .prem-stat-num{{font-size:clamp(1.5rem,4.5vw,2rem);}}
    .prem-card,.prem-complaint-item,.prem-notif-card{{border-radius:var(--r-md);}}
    .prem-lb-card{{flex-direction:column;text-align:center;}}
    .prem-lb-stats{{justify-content:center;}}
    .prem-lb-rank{{min-width:auto;}}
    .prem-performer-grid{{grid-template-columns:1fr 1fr;gap:var(--sp-2);}}
    .stButton>button{{padding:9px 14px!important;font-size:var(--fs-sm)!important;}}
    .prem-section-header{{font-size:var(--fs-2xs);}}
    .prem-welcome-title{{font-size:clamp(1.3rem,5vw,1.75rem);}}
    .prem-welcome{{padding:36px 14px 22px;}}
    .prem-filter-chips{{gap:var(--sp-1);overflow-x:auto;flex-wrap:nowrap;padding-bottom:6px;}}
    .prem-filter-chip{{white-space:nowrap;flex-shrink:0;padding:5px 10px;font-size:var(--fs-2xs);}}
    /* Reduce expensive effects on mobile */
    .prem-glass{{backdrop-filter:none!important;background:{glass_bg}!important;}}
    *{{animation-duration:0.18s!important;}}
}}

/* ── 480px — Small phone ── */
@media(max-width:480px){{
    .prem-hero-stats{{grid-template-columns:repeat(2,1fr);}}
    .prem-performer-grid{{grid-template-columns:1fr;}}
    .prem-complaint-meta{{flex-direction:column;align-items:flex-start;gap:var(--sp-2);}}
    .prem-lb-stats{{gap:var(--sp-3);}}
    .prem-notif-bar{{flex-direction:column;}}
    .stTabs [data-baseweb="tab"]{{
        flex:1 1 calc(50% - 3px)!important;
        text-align:center!important;
        font-size:var(--fs-2xs)!important;
    }}
    .action-buttons{{flex-direction:column;}}
    .action-buttons .stButton{{width:100%;}}
}}

/* ═══════════════════════════════════════════════════════════════
   DARK MODE WIDGET OVERRIDES  (injected last — highest specificity)
═══════════════════════════════════════════════════════════════ */
{dark_overrides}

</style>
"""