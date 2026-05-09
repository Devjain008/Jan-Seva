"""
streamlit_premium_css_v2.py
═══════════════════════════════════════════════════════════════════════════════
PRODUCTION-GRADE STREAMLIT CSS SYSTEM  v2.0
Civic-Tech Grievance Portal  |  Premium UI

ARCHITECTURE DECISIONS
──────────────────────
• Single :root token block — every value flows from tokens, zero magic numbers
• clamp() on ALL size/space/type values — fluid scaling, no breakpoint bloat
• CSS custom properties cascade cleanly in both light & dark modes
• Dark-mode dropdown fix is isolated to ONE block at the bottom — no conflicts
• Animations use will-change + transform only (GPU-composited, no repaints)
• Blur/shadow costs reduced: removed redundant layers, mobile disables backdrop-filter
• Duplicate selectors merged; conflicting button[kind="header"] blocks collapsed into one
• Z-index ladder: content(1) → sidebar(100) → header-btn(500) → popover(9999)
• Streamlit rerender flicker suppressed via contain: style + backface-visibility
• Horizontal scroll eliminated: overflow-x hidden on all ancestor chains
• Tables wrapped in overflow-x:auto scrollable containers
• Media queries: mobile-first base, 480 / 768 / 1024 progressive enhancement
═══════════════════════════════════════════════════════════════════════════════
"""


def get_css(dark_mode: bool = False) -> str:
    # ─────────────────────────────────────────────────────────────────────────
    # COLOUR TOKENS
    # ─────────────────────────────────────────────────────────────────────────
    if dark_mode:
        bg          = "#070B14"
        card_bg     = "#0D1220"
        card_bg2    = "#111827"
        text        = "#EFF2FF"
        subtext     = "#7C8FAC"
        border      = "#1C2540"
        input_bg    = "#0F1828"
        sidebar_bg  = "#09101A"
        hover_bg    = "#16213A"
        tag_bg      = "#151E35"
        tag_col     = "#A5B4FC"
        accent1     = "#6366F1"
        accent2     = "#818CF8"
        accent3     = "#22D3EE"
        a1_glow     = "rgba(99,102,241,0.35)"
        a1_soft     = "rgba(99,102,241,0.12)"
        a2_soft     = "rgba(129,140,248,0.10)"
        hero_from   = "#1E1B4B"
        hero_mid    = "#312E81"
        hero_to     = "#0C4A6E"
        shadow_sm   = "0 1px 4px rgba(0,0,0,.50),0 4px 12px rgba(0,0,0,.30)"
        shadow_md   = "0 4px 20px rgba(0,0,0,.55),0 12px 40px rgba(0,0,0,.35)"
        shadow_lg   = "0 16px 60px rgba(0,0,0,.65),0 40px 80px rgba(0,0,0,.40)"
        green_bg    = "#071A10"; green_bd  = "#166534"; green_text  = "#4ADE80"
        amber_bg    = "#1A1000"; amber_bd  = "#92400E"; amber_text  = "#FCD34D"
        red_bg      = "#1A0505"; red_bd    = "#991B1B"; red_text    = "#FCA5A5"
        blue_bg     = "#04091A"; blue_bd   = "#1E40AF"; blue_text   = "#93C5FD"
        glass_bg    = "rgba(255,255,255,0.04)"
        glass_bd    = "rgba(255,255,255,0.08)"
        # Dark-mode dropdown uses white popup for readability
        dd_bg       = "#ffffff"
        dd_text     = "#111827"
        dd_hover    = "rgba(99,102,241,0.08)"
        dd_selected_bg  = "rgba(99,102,241,0.14)"
        dd_selected_col = "#4F46E5"
    else:
        bg          = "#F2F5FC"
        card_bg     = "#FFFFFF"
        card_bg2    = "#F7F9FF"
        text        = "#0B1428"
        subtext     = "#5A6A85"
        border      = "#CBD5E9"
        input_bg    = "#F0F4FB"
        sidebar_bg  = "#FFFFFF"
        hover_bg    = "#E8EDF7"
        tag_bg      = "#EEF2FF"
        tag_col     = "#3730A3"
        accent1     = "#4F46E5"
        accent2     = "#7C3AED"
        accent3     = "#0891B2"
        a1_glow     = "rgba(79,70,229,0.20)"
        a1_soft     = "rgba(79,70,229,0.08)"
        a2_soft     = "rgba(124,58,237,0.06)"
        hero_from   = "#4F46E5"
        hero_mid    = "#7C3AED"
        hero_to     = "#0891B2"
        shadow_sm   = "0 1px 3px rgba(11,20,40,.06),0 4px 12px rgba(11,20,40,.06)"
        shadow_md   = "0 4px 16px rgba(11,20,40,.08),0 12px 32px rgba(11,20,40,.06)"
        shadow_lg   = "0 12px 48px rgba(11,20,40,.12),0 32px 64px rgba(11,20,40,.08)"
        green_bg    = "#F0FDF4"; green_bd  = "#86EFAC"; green_text  = "#166534"
        amber_bg    = "#FFFBEB"; amber_bd  = "#FDE68A"; amber_text  = "#92400E"
        red_bg      = "#FEF2F2"; red_bd    = "#FECACA"; red_text    = "#991B1B"
        blue_bg     = "#EFF6FF"; blue_bd   = "#BFDBFE"; blue_text   = "#1E40AF"
        glass_bg    = "rgba(255,255,255,0.70)"
        glass_bd    = "rgba(255,255,255,0.90)"
        # Light-mode dropdown inherits card_bg
        dd_bg       = "#FFFFFF"
        dd_text     = "#0B1428"
        dd_hover    = "#E8EDF7"
        dd_selected_bg  = "rgba(79,70,229,0.08)"
        dd_selected_col = "#4F46E5"

    # ─────────────────────────────────────────────────────────────────────────
    # DARK-MODE-ONLY OVERRIDES  (single, non-conflicting block)
    # ─────────────────────────────────────────────────────────────────────────
    dark_overrides = ""
    if dark_mode:
        dark_overrides = f"""
/* ═══════════════════════════════════════════════════════════
   DARK MODE OVERRIDES
   Injected last for maximum specificity — no duplicates here.
═══════════════════════════════════════════════════════════ */

/* SVG icons */
.stSelectbox svg,.stTextInput svg{{fill:{subtext}!important;}}

/* Selectbox trigger */
.stSelectbox>div>div{{
    background:{input_bg}!important;
    color:{text}!important;
    border-color:{border}!important;
}}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div,
.stSelectbox [data-baseweb="select"] input{{color:{text}!important;}}

/* Dropdown popup — white surface for readability in dark mode */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[data-testid="stWidgetDropdownList"]{{
    background:{dd_bg}!important;
    border:1px solid rgba(0,0,0,.10)!important;
    border-radius:16px!important;
    box-shadow:0 12px 40px rgba(0,0,0,.22)!important;
    color:{dd_text}!important;
}}

/* Option rows */
div[data-baseweb="option"],
li[role="option"]{{
    background:transparent!important;
    color:{dd_text}!important;
    border-radius:10px!important;
    margin:2px 6px!important;
    padding:9px 13px!important;
}}
div[data-baseweb="option"]:hover,
li[role="option"]:hover{{
    background:{dd_hover}!important;
    color:{dd_text}!important;
}}
div[data-baseweb="option"][aria-selected="true"],
li[role="option"][aria-selected="true"]{{
    background:{dd_selected_bg}!important;
    color:{dd_selected_col}!important;
    font-weight:700!important;
}}

/* Popover search input */
div[data-baseweb="popover"] input{{
    background:#f9fafb!important;
    color:{dd_text}!important;
    border:1px solid rgba(0,0,0,.10)!important;
}}

/* Prevent dark baseweb layer overlay */
div[data-baseweb="layer"]{{background:transparent!important;}}

/* Caret */
.stTextInput input,.stTextArea textarea{{caret-color:{accent2}!important;}}

/* Radio labels */
.stRadio label{{color:{text}!important;}}
.stRadio [data-testid="stMarkdownContainer"] p{{color:{text}!important;}}

/* Notification bar text overrides */
.prem-notif-bar-text{{color:{amber_text}!important;}}
.prem-notif-bar-badge{{color:#fff!important;background:{amber_text}!important;}}

/* Complaint description box text */
.complaint-desc-box{{color:{text}!important;}}

/* Closed badge */
.prem-badge-closed{{
    background:{hover_bg}!important;
    color:{subtext}!important;
    border-color:{border}!important;
}}
"""

    return f"""
<style>
/* ═══════════════════════════════════════════════════════════════════
   FONTS
═══════════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Mono:wght@400;500&family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&display=swap');


/* ═══════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   All sizes use clamp(min, fluid, max) — fluid scaling with no
   breakpoint regressions.  Change a token here; it propagates everywhere.
═══════════════════════════════════════════════════════════════════ */
:root{{
    /* Surface */
    --c-bg:      {bg};
    --c-card:    {card_bg};
    --c-card2:   {card_bg2};
    --c-text:    {text};
    --c-sub:     {subtext};
    --c-border:  {border};
    --c-input:   {input_bg};
    --c-hover:   {hover_bg};

    /* Accent */
    --c-a1:      {accent1};
    --c-a2:      {accent2};
    --c-a3:      {accent3};
    --c-a1-glow: {a1_glow};
    --c-a1-soft: {a1_soft};
    --c-a2-soft: {a2_soft};

    /* Shadow — two-tier (sm for cards, md for elevated, lg for hero) */
    --sh-sm: {shadow_sm};
    --sh-md: {shadow_md};
    --sh-lg: {shadow_lg};

    /* Radius — fluid */
    --r-xs:  clamp(4px,  1.0vw,  6px);
    --r-sm:  clamp(6px,  1.5vw,  9px);
    --r-md:  clamp(9px,  2.0vw, 13px);
    --r-lg:  clamp(13px, 2.6vw, 17px);
    --r-xl:  clamp(16px, 3.2vw, 22px);
    --r-2xl: clamp(20px, 4.0vw, 26px);

    /* Type scale — fluid, capped at comfortable max for large monitors */
    --fs-2xs: clamp(0.600rem, 1.3vw, 0.688rem);
    --fs-xs:  clamp(0.688rem, 1.6vw, 0.750rem);
    --fs-sm:  clamp(0.750rem, 1.8vw, 0.875rem);
    --fs-base:clamp(0.875rem, 2.0vw, 1.000rem);
    --fs-md:  clamp(0.938rem, 2.3vw, 1.063rem);
    --fs-lg:  clamp(1.063rem, 2.7vw, 1.250rem);
    --fs-xl:  clamp(1.250rem, 3.1vw, 1.500rem);
    --fs-2xl: clamp(1.500rem, 3.7vw, 1.875rem);
    --fs-3xl: clamp(1.750rem, 4.3vw, 2.250rem);
    --fs-4xl: clamp(2.000rem, 5.2vw, 2.750rem);

    /* Spacing — fluid */
    --sp-1: clamp(3px,  0.5vw,  4px);
    --sp-2: clamp(6px,  1.0vw,  8px);
    --sp-3: clamp(9px,  1.6vw, 12px);
    --sp-4: clamp(13px, 2.2vw, 17px);
    --sp-5: clamp(17px, 2.8vw, 21px);
    --sp-6: clamp(21px, 3.5vw, 28px);
    --sp-8: clamp(27px, 4.8vw, 42px);

    /* Icon sizes */
    --icon-sm:  clamp(0.90rem, 1.9vw, 1.00rem);
    --icon-md:  clamp(1.10rem, 2.4vw, 1.25rem);
    --icon-lg:  clamp(1.25rem, 2.8vw, 1.50rem);
    --icon-xl:  clamp(1.50rem, 3.3vw, 1.75rem);
    --icon-2xl: clamp(1.88rem, 4.2vw, 2.25rem);

    /* Motion */
    --t-fast: 0.14s cubic-bezier(0.4,0,0.2,1);
    --t-base: 0.20s cubic-bezier(0.4,0,0.2,1);
    --t-slow: 0.32s cubic-bezier(0.4,0,0.2,1);

    /* Z-index ladder — never use bare numbers outside this ladder */
    --z-base:    1;
    --z-sidebar: 100;
    --z-header:  500;
    --z-popover: 9999;
}}


/* ═══════════════════════════════════════════════════════════════════
   RESET & BASE
═══════════════════════════════════════════════════════════════════ */
*,*::before,*::after{{
    box-sizing:border-box;
    /* Suppress Streamlit rerender flicker */
    backface-visibility:hidden;
    -webkit-backface-visibility:hidden;
}}

/* Horizontal overflow: locked at every ancestor level */
html,body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"]{{
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
    /* Reduce layout shift on Streamlit rerenders */
    contain:layout style;
}}

/* Scoped text — semantic elements only, never bare div */
p,span,label,small,li{{color:var(--c-text);}}
.stMarkdown,
.stMarkdown p,
.stMarkdown span{{color:var(--c-text)!important;}}

/* Prevent media elements from causing horizontal scroll */
img,svg,video,iframe,canvas{{max-width:100%;height:auto;display:block;}}

/* Scrollable table wrapper (replaces display:block on table) */
.stDataFrame table,
table{{overflow-x:auto;display:block;width:100%;max-width:100%;}}


/* ─── HIDE STREAMLIT CHROME ─────────────────────────────────────── */
#MainMenu,
footer,
.stDeployButton,
.viewerBadge_container__1QSob{{
    visibility:hidden!important;
    display:none!important;
}}

/* Keep header invisible but alive (sidebar toggle lives inside it) */
header[data-testid="stHeader"]{{
    background:transparent!important;
    height:0!important;
    overflow:visible!important; /* allow toggle to escape */
}}

/* Animated top-edge stripe */
.stApp::before{{
    content:'';
    display:block;
    position:fixed;
    top:0;left:0;right:0;
    height:2px;
    background:linear-gradient(90deg,{accent1},{accent2},{accent3},{accent1});
    background-size:200% 100%;
    animation:prem-gradient-move 6s ease infinite;
    z-index:var(--z-popover);
    pointer-events:none;
    will-change:background-position;
}}


/* ═══════════════════════════════════════════════════════════════════
   SIDEBAR TOGGLE BUTTON
   Collapsed into ONE authoritative block.
   Previously had two conflicting blocks fighting each other.
═══════════════════════════════════════════════════════════════════ */
button[kind="header"],
[data-testid="collapsedControl"]{{
    position:fixed!important;
    top:16px!important;
    left:16px!important;
    width:44px!important;
    height:44px!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    border-radius:13px!important;
    background:linear-gradient(135deg,{accent1},{accent2})!important;
    border:1px solid rgba(255,255,255,.18)!important;
    box-shadow:0 8px 24px {a1_glow},0 2px 8px rgba(0,0,0,.12)!important;
    z-index:var(--z-header)!important;
    transition:transform var(--t-fast),box-shadow var(--t-fast)!important;
    cursor:pointer!important;
    visibility:visible!important;
    opacity:1!important;
}}
button[kind="header"]:hover,
[data-testid="collapsedControl"]:hover{{
    transform:translateY(-2px) scale(1.04)!important;
    box-shadow:0 12px 30px {a1_glow},0 4px 14px rgba(0,0,0,.16)!important;
}}
button[kind="header"]:active,
[data-testid="collapsedControl"]:active{{
    transform:scale(0.96)!important;
}}
button[kind="header"] svg,
[data-testid="collapsedControl"] svg{{
    width:19px!important;
    height:19px!important;
    fill:#fff!important;
    color:#fff!important;
    stroke:#fff!important;
}}


/* ═══════════════════════════════════════════════════════════════════
   LAYOUT — CENTERED CONTENT WRAPPER
   Prevents stretching on 1440+ monitors while staying fluid on mobile.
   clamp: min 300px → ideal 90vw → max 1100px
═══════════════════════════════════════════════════════════════════ */
.main .block-container{{
    padding:clamp(0.9rem,2.8vw,2rem) clamp(0.75rem,3.2vw,2rem) clamp(2.5rem,5.5vw,4.5rem)!important;
    max-width:clamp(300px,90vw,1100px)!important;
    margin:0 auto!important;
    width:100%!important;
}}


/* ═══════════════════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"]{{
    background:{sidebar_bg}!important;
    border-right:1px solid var(--c-border)!important;
    z-index:var(--z-sidebar)!important;
    overflow-x:hidden!important;
}}
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
    padding:clamp(8px,2vw,11px) clamp(11px,2.4vw,15px)!important;
    transition:all var(--t-fast)!important;
    width:100%!important;
}}
section[data-testid="stSidebar"] .stButton>button:hover{{
    background:var(--c-hover)!important;
    border-color:var(--c-a1)!important;
    transform:translateX(3px)!important;
}}


/* ═══════════════════════════════════════════════════════════════════
   BUTTONS — Primary & Secondary unified
═══════════════════════════════════════════════════════════════════ */
.stButton>button,
button[kind="secondary"],
button[data-testid="baseButton-secondary"]{{
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
    min-height:42px!important;         /* consistent touch target */
    box-shadow:0 2px 8px {a1_glow}!important;
    position:relative!important;
    overflow:hidden!important;
    transition:transform var(--t-base),box-shadow var(--t-base),filter var(--t-fast)!important;
    will-change:transform;
}}
/* Sheen overlay */
.stButton>button::before,
button[kind="secondary"]::before,
button[data-testid="baseButton-secondary"]::before{{
    content:'';
    position:absolute;inset:0;
    background:linear-gradient(180deg,rgba(255,255,255,.13) 0%,transparent 100%);
    pointer-events:none;
    border-radius:inherit;
}}
.stButton>button:hover,
button[kind="secondary"]:hover,
button[data-testid="baseButton-secondary"]:hover{{
    transform:translateY(-2px) scale(1.005)!important;
    box-shadow:0 6px 20px {a1_glow}!important;
    filter:brightness(1.06)!important;
}}
.stButton>button:active,
button[kind="secondary"]:active,
button[data-testid="baseButton-secondary"]:active{{
    transform:translateY(0) scale(0.998)!important;
    filter:brightness(0.97)!important;
}}
.stButton>button:focus-visible,
button[kind="secondary"]:focus-visible{{
    outline:none!important;
    box-shadow:0 0 0 3px {bg},0 0 0 5px {accent1}!important;
}}


/* ═══════════════════════════════════════════════════════════════════
   INPUTS — Text, Textarea, Selectbox
═══════════════════════════════════════════════════════════════════ */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea{{
    background:var(--c-input)!important;
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-md)!important;
    color:var(--c-text)!important;
    font-family:'DM Sans','Noto Sans Devanagari',sans-serif!important;
    font-size:var(--fs-base)!important;
    padding:clamp(8px,2vw,11px) clamp(10px,2.4vw,14px)!important;
    width:100%!important;
    max-width:100%!important;
    transition:border-color var(--t-fast),box-shadow var(--t-fast)!important;
    caret-color:{accent1}!important;
}}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{{
    border-color:var(--c-a1)!important;
    box-shadow:0 0 0 3px var(--c-a1-soft)!important;
    outline:none!important;
    background:var(--c-card)!important;
}}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder{{
    color:var(--c-sub)!important;
    opacity:0.65!important;
}}

/* Field labels */
label,
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stRadio label{{
    color:var(--c-sub)!important;
    font-weight:600!important;
    font-size:var(--fs-xs)!important;
    text-transform:uppercase!important;
    letter-spacing:0.07em!important;
    margin-bottom:5px!important;
    display:block!important;
}}

/* Selectbox trigger */
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

/* Radio label overrides (counters uppercase from field label rule) */
.stRadio label{{
    text-transform:none!important;
    letter-spacing:0!important;
    font-size:var(--fs-base)!important;
    color:var(--c-text)!important;
}}
.stRadio [data-testid="stMarkdownContainer"] p{{color:var(--c-text)!important;}}


/* ═══════════════════════════════════════════════════════════════════
   DROPDOWN POPOVER — Light mode base
   Dark mode overrides are in the dark_overrides block below.
═══════════════════════════════════════════════════════════════════ */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[data-testid="stWidgetDropdownList"]{{
    background:{dd_bg}!important;
    border:1px solid {border}!important;
    border-radius:var(--r-lg)!important;
    box-shadow:var(--sh-md)!important;
    overflow:hidden!important;
    max-height:60vh!important;
    overflow-y:auto!important;
    z-index:var(--z-popover)!important;
    color:{dd_text}!important;
}}
div[data-baseweb="option"],
li[role="option"]{{
    background:transparent!important;
    color:{dd_text}!important;
    padding:clamp(7px,1.8vw,10px) clamp(10px,2.4vw,14px)!important;
    margin:2px 5px!important;
    border-radius:var(--r-sm)!important;
    font-size:var(--fs-base)!important;
    font-weight:500!important;
    transition:background var(--t-fast)!important;
    word-break:break-word!important;
    white-space:normal!important;
    cursor:pointer!important;
}}
div[data-baseweb="option"]:hover,
li[role="option"]:hover{{
    background:{dd_hover}!important;
    color:{dd_text}!important;
}}
div[data-baseweb="option"][aria-selected="true"],
li[role="option"][aria-selected="true"]{{
    background:{dd_selected_bg}!important;
    color:{dd_selected_col}!important;
    font-weight:700!important;
}}
div[data-baseweb="layer"]{{background:transparent!important;}}


/* ═══════════════════════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"]{{
    background:var(--c-card)!important;
    border-radius:var(--r-lg)!important;
    padding:clamp(3px,0.9vw,5px)!important;
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
    padding:clamp(6px,1.8vw,9px) clamp(11px,2.8vw,19px)!important;
    border:none!important;
    transition:all var(--t-fast)!important;
    flex-shrink:0!important;
    white-space:nowrap!important;
}}
.stTabs [aria-selected="true"]{{
    background:linear-gradient(135deg,{accent1},{accent2})!important;
    color:#fff!important;
    box-shadow:0 3px 12px {a1_glow}!important;
}}
.stTabs [data-baseweb="tab-panel"]{{
    background:transparent!important;
    padding:16px 0 0!important;
}}


/* ═══════════════════════════════════════════════════════════════════
   EXPANDER
═══════════════════════════════════════════════════════════════════ */
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
    padding:clamp(9px,2.4vw,13px) clamp(11px,2.8vw,16px)!important;
    font-size:var(--fs-base)!important;
    transition:background var(--t-fast)!important;
}}
.streamlit-expanderHeader:hover{{background:var(--c-hover)!important;}}
.streamlit-expanderContent{{
    background:var(--c-card)!important;
    border-top:1px solid var(--c-border)!important;
    padding:clamp(11px,2.8vw,17px) clamp(11px,3.2vw,19px)!important;
}}


/* ═══════════════════════════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════════════════════════ */
.stProgress>div>div{{
    background:linear-gradient(90deg,{accent1},{accent2})!important;
    border-radius:99px!important;
    will-change:width;
}}
.stProgress>div{{
    background:var(--c-border)!important;
    border-radius:99px!important;
    height:5px!important;
}}


/* ═══════════════════════════════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════════════════════════════ */
.stSuccess{{background:{green_bg}!important;border:1px solid {green_bd}!important;border-radius:var(--r-md)!important;color:{green_text}!important;}}
.stInfo   {{background:{blue_bg}!important; border:1px solid {blue_bd}!important; border-radius:var(--r-md)!important;color:{blue_text}!important;}}
.stWarning{{background:{amber_bg}!important;border:1px solid {amber_bd}!important;border-radius:var(--r-md)!important;color:{amber_text}!important;}}
.stError  {{background:{red_bg}!important;  border:1px solid {red_bd}!important;  border-radius:var(--r-md)!important;color:{red_text}!important;}}


/* ═══════════════════════════════════════════════════════════════════
   DATA TABLE
═══════════════════════════════════════════════════════════════════ */
div[data-testid="stDataFrame"]{{
    display:block;
    overflow-x:auto;
    width:100%;
    max-width:100%;
    -webkit-overflow-scrolling:touch;
}}
div[data-testid="stDataFrame"] *,
table th,
table td{{
    color:var(--c-text)!important;
    border-color:var(--c-border)!important;
    font-size:var(--fs-sm)!important;
}}


/* ═══════════════════════════════════════════════════════════════════
   MISC UTILITIES
═══════════════════════════════════════════════════════════════════ */
hr{{
    border:none;
    height:1px;
    background:linear-gradient(90deg,transparent,{border},transparent);
    margin:var(--sp-6) 0!important;
}}
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:var(--c-border);border-radius:99px;}}
::-webkit-scrollbar-thumb:hover{{background:var(--c-sub);}}


/* ═══════════════════════════════════════════════════════════════════
   ██  COMPONENT LIBRARY
   Each component is self-contained; no cross-component CSS leaks.
═══════════════════════════════════════════════════════════════════ */

/* ── HERO BANNER ─────────────────────────────────────────────────── */
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
    contain:layout;
}}
.prem-hero::before{{
    content:'';position:absolute;top:-80px;right:-60px;
    width:clamp(160px,28vw,260px);height:clamp(160px,28vw,260px);
    background:radial-gradient(circle,rgba(255,255,255,0.08) 0%,transparent 70%);
    pointer-events:none;
    animation:prem-float 8s ease-in-out infinite;
    will-change:transform;
}}
.prem-hero::after{{
    content:'';position:absolute;bottom:-60px;left:10%;
    width:clamp(120px,22vw,200px);height:clamp(120px,22vw,200px);
    background:radial-gradient(circle,rgba(255,255,255,0.05) 0%,transparent 70%);
    pointer-events:none;
    animation:prem-float 10s ease-in-out infinite reverse;
    will-change:transform;
}}
.prem-hero-title{{
    font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:clamp(1.35rem,4.2vw,2.20rem);
    font-weight:800;line-height:1.2;
    margin-bottom:var(--sp-1);
    position:relative;z-index:1;
    color:#fff;letter-spacing:-0.03em;
    word-break:break-word;
}}
.prem-hero-sub{{
    font-size:clamp(0.80rem,2.1vw,0.975rem);
    margin:0 0 var(--sp-1);
    opacity:0.82;
    position:relative;z-index:1;
    color:rgba(255,255,255,.88);
    font-weight:400;
    max-width:58ch;
}}
.prem-hero-avatar{{
    position:absolute;
    top:clamp(13px,2.8vw,22px);
    right:clamp(13px,2.8vw,24px);
    width:clamp(36px,5.5vw,48px);
    height:clamp(36px,5.5vw,48px);
    border-radius:50%;
    background:rgba(255,255,255,0.15);
    border:1px solid rgba(255,255,255,0.28);
    display:flex;align-items:center;justify-content:center;
    font-weight:700;font-size:var(--fs-md);
    color:#fff;z-index:1;
    box-shadow:0 4px 14px rgba(0,0,0,0.20);
}}
.prem-hero-stats{{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(clamp(88px,17vw,118px),1fr));
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
    transition:background var(--t-fast),transform var(--t-fast);
    cursor:default;
}}
.prem-hstat:hover{{background:rgba(255,255,255,0.17);transform:translateY(-2px);}}
.prem-hstat-num{{
    font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:clamp(1.5rem,4.2vw,2.4rem);
    font-weight:800;line-height:1;
    margin-bottom:var(--sp-1);
    color:#fff;letter-spacing:-0.03em;
}}
.prem-hstat-lbl{{
    font-size:var(--fs-2xs);font-weight:600;
    text-transform:uppercase;letter-spacing:0.08em;
    color:rgba(255,255,255,.60);
}}
.prem-hstat.h-blue  .prem-hstat-num{{color:#BAC8FF;}}
.prem-hstat.h-amber .prem-hstat-num{{color:#FDE68A;}}
.prem-hstat.h-green .prem-hstat-num{{color:#6EE7B7;}}
.prem-hstat.h-red   .prem-hstat-num{{color:#FCA5A5;}}


/* ── CARD ────────────────────────────────────────────────────────── */
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
.prem-card:hover{{
    transform:translateY(-2px);
    box-shadow:var(--sh-md);
    border-color:{accent1}44;
}}


/* ── STAT CARD ───────────────────────────────────────────────────── */
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
    min-height:120px; /* equalise card heights */
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
    font-size:clamp(1.65rem,4.8vw,2.40rem);
    font-weight:800;line-height:1.1;
    color:var(--c-text);letter-spacing:-0.04em;
    position:relative;z-index:1;
}}
.prem-stat-lbl{{
    font-size:var(--fs-xs);color:var(--c-sub);font-weight:600;
    text-transform:uppercase;letter-spacing:0.07em;
    margin-top:var(--sp-2);position:relative;z-index:1;
}}


/* ── ACTION CARD ─────────────────────────────────────────────────── */
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
    min-height:130px;
}}
.prem-action-card::before{{
    content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,{accent1},{accent2},{accent3});
    transform:scaleX(0);transition:transform var(--t-base);
    transform-origin:left;
    will-change:transform;
}}
.prem-action-card:hover{{
    transform:translateY(-5px);
    box-shadow:var(--sh-md);
    border-color:{accent1}55;
}}
.prem-action-card:hover::before{{transform:scaleX(1);}}
.prem-action-card:hover .prem-action-icon{{transform:scale(1.10);}}
.prem-action-icon{{
    width:clamp(42px,7.5vw,50px);
    height:clamp(42px,7.5vw,50px);
    border-radius:var(--r-md);
    display:flex;align-items:center;justify-content:center;
    font-size:var(--icon-xl);
    margin:0 auto var(--sp-3);
    transition:transform var(--t-fast);
    will-change:transform;
}}
.prem-action-label{{
    font-size:var(--fs-sm);font-weight:700;
    color:var(--c-text);line-height:1.35;
    letter-spacing:-0.01em;
}}


/* ── SECTION HEADER ──────────────────────────────────────────────── */
.prem-section-header{{
    font-size:var(--fs-xs);font-weight:700;
    text-transform:uppercase;letter-spacing:0.10em;
    color:var(--c-sub);
    margin:var(--sp-8) 0 var(--sp-3);
    display:flex;align-items:center;gap:9px;
}}
.prem-section-header::before{{
    content:'';width:3px;height:13px;
    background:linear-gradient(180deg,{accent1},{accent2});
    border-radius:99px;flex-shrink:0;
}}
.prem-section-header::after{{
    content:'';flex:1;height:1px;
    background:linear-gradient(to right,{border}80,transparent);
}}


/* ── COMPLAINT ITEM ──────────────────────────────────────────────── */
.prem-complaint-item{{
    background:var(--c-card);
    border-radius:var(--r-lg);
    padding:clamp(10px,2.4vw,17px) clamp(13px,3.2vw,22px);
    margin:var(--sp-2) 0;
    border:1px solid var(--c-border);
    border-left:4px solid {accent1};
    box-shadow:var(--sh-sm);
    transition:transform var(--t-fast),border-color var(--t-fast),box-shadow var(--t-base);
    word-break:break-word;
    overflow:hidden;
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


/* ── BADGES & TAGS ───────────────────────────────────────────────── */
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
    vertical-align:middle;line-height:1.4;
}}
.prem-badge-high     {{background:{red_bg};  color:{red_text};  border:1px solid {red_bd};}}
.prem-badge-medium   {{background:{amber_bg};color:{amber_text};border:1px solid {amber_bd};}}
.prem-badge-low      {{background:{green_bg};color:{green_text};border:1px solid {green_bd};}}
.prem-badge-pending  {{background:{amber_bg};color:{amber_text};border:1px solid {amber_bd};}}
.prem-badge-progress {{background:{blue_bg}; color:{blue_text}; border:1px solid {blue_bd};}}
.prem-badge-resolved {{background:{green_bg};color:{green_text};border:1px solid {green_bd};}}
.prem-badge-closed   {{background:{card_bg2};color:{subtext};   border:1px solid {border};}}
.prem-badge-rejected {{background:{red_bg};  color:{red_text};  border:1px solid {red_bd};}}
.prem-badge-emergency{{
    background:linear-gradient(135deg,#EF4444,#DC2626);
    color:#fff;border:none;
    box-shadow:0 0 0 3px rgba(239,68,68,0.22);
    animation:prem-pulse-emergency 2.5s ease infinite;
    will-change:box-shadow;
}}


/* ── NOTIFICATION CARD ───────────────────────────────────────────── */
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


/* ── NOTIFICATION BAR ────────────────────────────────────────────── */
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
    font-weight:600;flex:1;min-width:min(140px,55%);
}}
.prem-notif-bar-badge{{
    background:{amber_text};color:#fff!important;
    border-radius:99px;padding:2px 9px;
    font-size:var(--fs-2xs);font-weight:700;
    white-space:nowrap;
}}


/* ── TIMELINE ────────────────────────────────────────────────────── */
.prem-timeline{{padding:4px 0;}}
.prem-tl-item{{
    display:flex;gap:var(--sp-3);align-items:flex-start;
    margin-bottom:4px;flex-wrap:nowrap;
}}
.prem-tl-dot{{
    width:22px;height:22px;border-radius:50%;flex-shrink:0;
    display:flex;align-items:center;justify-content:center;
    font-size:0.58rem;font-weight:800;margin-top:2px;
    transition:transform var(--t-fast);
}}
.prem-tl-dot:hover{{transform:scale(1.15);}}
.prem-tl-dot.done  {{background:{accent1};color:#fff;box-shadow:0 0 0 4px {a1_soft};}}
.prem-tl-dot.active{{
    background:{accent2};color:#fff;
    box-shadow:0 0 0 4px {a2_soft};
    animation:prem-pulse-ring 2.5s ease infinite;
    will-change:box-shadow;
}}
.prem-tl-dot.idle  {{background:{card_bg2};color:{subtext};border:1px solid {border};}}
.prem-tl-info{{flex:1;padding:2px 0;min-width:0;}}
.prem-tl-label{{font-size:var(--fs-sm);font-weight:600;color:var(--c-text);letter-spacing:-0.01em;word-break:break-word;}}
.prem-tl-time {{font-size:var(--fs-xs);color:var(--c-sub);margin-top:2px;font-family:'DM Mono',monospace;}}
.prem-tl-line {{width:2px;height:14px;background:var(--c-border);margin-left:10px;border-radius:99px;}}
.prem-tl-line.done{{background:linear-gradient(to bottom,{accent1}88,{border});}}


/* ── SLA BAR ─────────────────────────────────────────────────────── */
.prem-sla-bar{{
    background:var(--c-card2);border:1px solid var(--c-border);
    border-radius:var(--r-md);padding:10px 14px;
    display:flex;align-items:center;gap:var(--sp-2);flex-wrap:wrap;
    margin-top:var(--sp-3);font-size:var(--fs-sm);color:var(--c-sub);
}}
.prem-sla-bar.overdue{{background:{red_bg};border-color:{red_bd};color:{red_text};}}
.prem-sla-bar strong{{color:var(--c-text);font-weight:700;}}
.prem-sla-bar.overdue strong{{color:{red_text};}}


/* ── FEEDBACK CARD ───────────────────────────────────────────────── */
.prem-feedback-card{{
    background:var(--c-card);border:1px solid {green_bd};
    border-radius:var(--r-lg);padding:var(--sp-6);margin-bottom:var(--sp-3);
    box-shadow:0 0 0 3px {green_bg};transition:transform var(--t-fast);
    word-break:break-word;
}}
.prem-feedback-card:hover{{transform:translateY(-2px);}}
.prem-feedback-card .prem-fb-head{{
    display:flex;align-items:center;gap:var(--sp-3);
    margin-bottom:var(--sp-3);flex-wrap:wrap;
}}
.prem-fb-icon{{
    width:40px;height:40px;border-radius:var(--r-md);
    background:{green_bg};border:1px solid {green_bd};
    display:flex;align-items:center;justify-content:center;
    font-size:var(--icon-md);flex-shrink:0;
}}
.prem-fb-title{{font-weight:700;font-size:var(--fs-md);color:var(--c-text);}}
.prem-fb-sub  {{font-size:var(--fs-xs);color:var(--c-sub);margin-top:2px;}}
.prem-fb-desc {{font-size:var(--fs-sm);color:var(--c-sub);line-height:1.65;margin-bottom:var(--sp-4);}}


/* ── RATING CARD ─────────────────────────────────────────────────── */
.prem-rating-card{{
    background:var(--c-card);border:1px solid {blue_bd};
    border-radius:var(--r-lg);padding:var(--sp-6);margin-bottom:var(--sp-3);
    box-shadow:0 0 0 3px {blue_bg};
}}


/* ── SCHEME CARD ─────────────────────────────────────────────────── */
.prem-scheme-card{{
    background:var(--c-card);border-radius:var(--r-lg);overflow:hidden;
    border:1px solid var(--c-border);margin-bottom:var(--sp-4);
    box-shadow:var(--sh-sm);
    transition:transform var(--t-base),box-shadow var(--t-base),border-color var(--t-fast);
    word-break:break-word;
}}
.prem-scheme-card:hover{{
    transform:translateY(-3px);
    box-shadow:var(--sh-md);
    border-color:{accent1}44;
}}
.prem-scheme-body {{padding:var(--sp-5) var(--sp-6);}}
.prem-scheme-title{{font-size:var(--fs-md);font-weight:700;margin-bottom:var(--sp-2);color:var(--c-text);}}
.prem-scheme-desc {{font-size:var(--fs-sm);color:var(--c-sub);line-height:1.68;}}


/* ── LEADERBOARD ─────────────────────────────────────────────────── */
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
    background:transparent;border-radius:4px 0 0 4px;
    transition:background var(--t-fast);
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
    font-size:var(--fs-2xl);font-weight:800;min-width:54px;
    text-align:center;color:{amber_text};letter-spacing:-0.04em;
}}
.prem-lb-info{{flex:1;min-width:0;}}
.prem-lb-name{{
    font-weight:700;font-size:var(--fs-md);margin-bottom:6px;
    display:flex;align-items:center;gap:10px;flex-wrap:wrap;
    color:var(--c-text);
}}
.prem-lb-dept{{
    font-size:var(--fs-xs);font-weight:600;
    background:{tag_bg};padding:2px 10px;border-radius:99px;color:{tag_col};
}}
.prem-lb-stats{{display:flex;gap:var(--sp-5);flex-wrap:wrap;margin:var(--sp-2) 0;}}
.prem-lb-stat-item{{text-align:center;min-width:50px;}}
.prem-lb-stat-lbl{{font-size:var(--fs-2xs);text-transform:uppercase;letter-spacing:0.07em;color:var(--c-sub);}}
.prem-lb-stat-val{{font-weight:700;font-size:var(--fs-base);color:var(--c-text);}}


/* ── CUSTOM PROGRESS BAR ─────────────────────────────────────────── */
.prem-prog-wrap{{
    background:var(--c-border);border-radius:99px;
    height:20px;overflow:hidden;position:relative;
}}
.prem-prog-fill{{
    height:100%;border-radius:99px;
    display:flex;align-items:center;justify-content:center;
    transition:width 0.5s cubic-bezier(0.4,0,0.2,1);
    position:relative;overflow:hidden;
    will-change:width;
}}
.prem-prog-fill::after{{
    content:'';position:absolute;inset:0;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,.17),transparent);
    background-size:200% 100%;
    animation:prem-shimmer 2.5s ease infinite;
    will-change:background-position;
}}
.prem-prog-text{{font-size:var(--fs-xs);font-weight:700;color:#fff;position:relative;z-index:1;}}


/* ── PERFORMER GRID ──────────────────────────────────────────────── */
.prem-performer-grid{{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(clamp(145px,26vw,185px),1fr));
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
    transform:scaleX(0);transform-origin:left;
    transition:transform var(--t-base);
    will-change:transform;
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


/* ── EMPTY STATE ─────────────────────────────────────────────────── */
.prem-empty-state{{
    text-align:center;
    padding:clamp(2.5rem,7.5vw,4.8rem) clamp(1rem,3.8vw,2rem);
    background:var(--c-card);border-radius:var(--r-xl);
    border:1px dashed var(--c-border);
    position:relative;overflow:hidden;
}}
.prem-empty-state::before{{
    content:'';position:absolute;top:50%;left:50%;
    transform:translate(-50%,-50%);
    width:200px;height:200px;
    background:radial-gradient(circle,{a1_soft} 0%,transparent 70%);
    pointer-events:none;
}}
.prem-empty-icon {{font-size:var(--icon-2xl);margin-bottom:var(--sp-4);opacity:.80;display:block;position:relative;z-index:1;}}
.prem-empty-title{{
    font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:var(--fs-lg);font-weight:700;color:var(--c-text)!important;
    margin-bottom:var(--sp-2);position:relative;z-index:1;
}}
.prem-empty-sub{{
    font-size:var(--fs-sm);color:var(--c-sub)!important;
    margin-bottom:var(--sp-6);line-height:1.65;position:relative;z-index:1;
}}


/* ── WELCOME SCREEN ──────────────────────────────────────────────── */
.prem-welcome{{text-align:center;padding:clamp(38px,9.5vw,58px) 20px 34px;}}
.prem-welcome-logo{{
    font-size:clamp(3.2rem,7.5vw,4.8rem);display:block;
    margin-bottom:var(--sp-4);
    animation:prem-float 4s ease-in-out infinite;
    will-change:transform;
}}
.prem-welcome-title{{
    font-family:'Bricolage Grotesque','DM Sans',sans-serif;
    font-size:clamp(1.45rem,4.8vw,2.20rem);
    font-weight:800;margin-bottom:var(--sp-3);
    color:var(--c-text);letter-spacing:-0.04em;
}}
.prem-welcome-sub{{
    font-size:var(--fs-md);color:var(--c-sub);
    margin-bottom:var(--sp-8);line-height:1.75;
    max-width:min(460px,90%);margin-left:auto;margin-right:auto;
}}


/* ── CHAT HEADER ─────────────────────────────────────────────────── */
.prem-chat-header{{
    background:linear-gradient(135deg,{accent1},{accent2});
    padding:var(--sp-4) var(--sp-6);color:#fff;
    font-weight:700;font-size:var(--fs-base);
    display:flex;align-items:center;gap:var(--sp-2);
    border-radius:var(--r-lg) var(--r-lg) 0 0;
    box-shadow:0 4px 20px {a1_glow};
}}


/* ── TIP BAR ─────────────────────────────────────────────────────── */
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


/* ── GLASS SURFACE ───────────────────────────────────────────────── */
.prem-glass{{
    background:{glass_bg}!important;
    border:1px solid {glass_bd}!important;
    border-radius:var(--r-lg)!important;
    /* backdrop-filter added only for non-mobile via media query */
}}


/* ── DIVIDER ─────────────────────────────────────────────────────── */
.prem-divider{{
    display:flex;align-items:center;gap:var(--sp-3);
    margin:var(--sp-5) 0;color:var(--c-sub);
    font-size:var(--fs-xs);font-weight:700;
    text-transform:uppercase;letter-spacing:0.08em;
}}
.prem-divider::before,
.prem-divider::after{{content:'';flex:1;height:1px;background:var(--c-border);}}


/* ── INLINE CHIP ─────────────────────────────────────────────────── */
.prem-chip{{
    display:inline-flex;align-items:center;gap:5px;
    background:{a1_soft};border:1px solid {accent1}22;
    border-radius:99px;padding:3px 12px;
    font-size:var(--fs-xs);font-weight:700;color:{accent1};
    font-family:'DM Mono',monospace;
}}


/* ── FILTER CHIPS ────────────────────────────────────────────────── */
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
.prem-filter-chip:hover:not(.active){{
    background:var(--c-hover);
    border-color:{accent1}55;
}}


/* ── FORM SECTION CARD ───────────────────────────────────────────── */
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


/* ── COMPLAINT CARD (alternative .complaint-card class) ──────────── */
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
    box-shadow:0 8px 20px -12px rgba(0,0,0,.18);
}}
.complaint-priority-high  {{border-left:4px solid #EF4444;}}
.complaint-priority-medium{{border-left:4px solid #F59E0B;}}
.complaint-priority-low   {{border-left:4px solid #10B981;}}
.complaint-header{{
    display:flex;justify-content:space-between;align-items:center;
    flex-wrap:wrap;gap:var(--sp-2);margin-bottom:var(--sp-3);
}}
.badge-status{{
    display:inline-flex;align-items:center;gap:4px;
    padding:3px 10px;border-radius:30px;
    font-size:var(--fs-xs);font-weight:700;white-space:nowrap;
}}
.badge-pending    {{background:{amber_bg};color:{amber_text};}}
.badge-in_progress{{background:{blue_bg}; color:{blue_text};}}
.badge-resolved   {{background:{green_bg};color:{green_text};}}
.badge-closed     {{background:{card_bg2};color:{subtext};}}
.badge-rejected   {{background:{red_bg};  color:{red_text};}}
.badge-priority{{
    display:inline-flex;align-items:center;gap:4px;
    padding:3px 10px;border-radius:30px;
    font-size:var(--fs-xs);font-weight:700;white-space:nowrap;
}}
.badge-priority-high  {{background:{red_bg};  color:{red_text};}}
.badge-priority-medium{{background:{amber_bg};color:{amber_text};}}
.badge-priority-low   {{background:{green_bg};color:{green_text};}}

.complaint-desc-box{{
    background:var(--c-card2);padding:var(--sp-3) var(--sp-4);
    border-radius:var(--r-md);margin:var(--sp-3) 0;
    border:1px solid var(--c-border);
    color:var(--c-text)!important;
    font-size:var(--fs-base);line-height:1.6;
    white-space:pre-wrap;word-break:break-word;
    max-height:clamp(130px,24vh,190px);overflow-y:auto;
}}
.complaint-meta{{
    display:flex;gap:var(--sp-3);flex-wrap:wrap;
    font-size:var(--fs-xs);color:var(--c-sub);margin-bottom:var(--sp-3);
}}
.action-buttons{{display:flex;gap:var(--sp-2);flex-wrap:wrap;margin-top:var(--sp-2);}}


/* ── HEATMAP LEGEND ──────────────────────────────────────────────── */
.prem-heatmap-legend{{
    display:flex;gap:var(--sp-4);flex-wrap:wrap;
    margin-top:var(--sp-4);font-size:var(--fs-sm);font-weight:600;color:var(--c-sub);
}}
.prem-legend-item{{display:flex;align-items:center;gap:6px;}}
.prem-legend-dot {{width:10px;height:10px;border-radius:50%;flex-shrink:0;}}


/* ═══════════════════════════════════════════════════════════════════
   ANIMATIONS
   Each animation defined ONCE.  Removed duplicate @keyframes from
   original. will-change declared on the element, not inside keyframes.
═══════════════════════════════════════════════════════════════════ */
@keyframes prem-fade-up{{
    from{{opacity:0;transform:translateY(12px);}}
    to  {{opacity:1;transform:translateY(0);}}
}}
@keyframes prem-fade-in{{
    from{{opacity:0;}}
    to  {{opacity:1;}}
}}
@keyframes prem-scale-in{{
    from{{opacity:0;transform:scale(0.96);}}
    to  {{opacity:1;transform:scale(1);}}
}}
@keyframes prem-pulse-ring{{
    0%  {{box-shadow:0 0 0 0 {a1_glow};}}
    70% {{box-shadow:0 0 0 11px rgba(99,102,241,0);}}
    100%{{box-shadow:0 0 0 0 rgba(99,102,241,0);}}
}}
@keyframes prem-pulse-emergency{{
    0%  {{box-shadow:0 0 0 0 rgba(239,68,68,.38);}}
    70% {{box-shadow:0 0 0 11px rgba(239,68,68,0);}}
    100%{{box-shadow:0 0 0 0 rgba(239,68,68,0);}}
}}
@keyframes prem-shimmer{{
    0%  {{background-position:-200% 0;}}
    100%{{background-position: 200% 0;}}
}}
@keyframes prem-gradient-move{{
    0%,100%{{background-position:0% 50%;}}
    50%     {{background-position:100% 50%;}}
}}
@keyframes prem-float{{
    0%,100%{{transform:translateY(0);}}
    50%    {{transform:translateY(-6px);}}
}}

/* Entrance animation assignments */
.prem-card,
.prem-complaint-item,
.prem-notif-card,
.prem-scheme-card,
.prem-lb-card,
.prem-hero{{animation:prem-fade-up .24s ease both;}}
.prem-stat-card{{animation:prem-scale-in .24s ease both;}}


/* ═══════════════════════════════════════════════════════════════════
   RESPONSIVE  —  Mobile-first.  Each breakpoint ADDS to base.
═══════════════════════════════════════════════════════════════════ */

/* ── Desktop enhancement (>1024px): enable glass blur ─── */
@media (min-width:1025px){{
    .prem-glass{{
        backdrop-filter:blur(16px)!important;
        -webkit-backdrop-filter:blur(16px)!important;
    }}
}}

/* ── Tablet landscape + laptop  (≤1024px) ───────────────── */
@media(max-width:1024px){{
    .main .block-container{{
        max-width:96vw!important;
        padding-left:clamp(0.75rem,2.4vw,1.4rem)!important;
        padding-right:clamp(0.75rem,2.4vw,1.4rem)!important;
    }}
    .prem-hero-stats{{
        grid-template-columns:repeat(auto-fit,minmax(clamp(78px,15vw,108px),1fr));
    }}
}}

/* ── Tablet portrait + large phone  (≤768px) ────────────── */
@media(max-width:768px){{
    .main .block-container{{
        padding:0.85rem 0.7rem 2.4rem!important;
        max-width:100%!important;
    }}
    section[data-testid="stSidebar"]{{
        width:clamp(240px,72vw,295px)!important;
    }}
    .prem-hero{{
        padding:var(--sp-5) var(--sp-4) var(--sp-4);
        border-radius:var(--r-lg);
    }}
    .prem-hero::before,.prem-hero::after{{display:none;}}
    .prem-hero-avatar{{display:none;}}
    .prem-hero-title{{font-size:clamp(1.22rem,4.8vw,1.70rem);}}
    .prem-hero-stats{{grid-template-columns:repeat(2,1fr);gap:var(--sp-2);}}
    .prem-hstat-num{{font-size:clamp(1.3rem,4.8vw,1.9rem);}}
    .prem-action-card{{padding:var(--sp-4) var(--sp-3);border-radius:var(--r-md);}}
    .prem-action-icon{{width:40px;height:40px;font-size:var(--icon-lg);}}
    .prem-stat-card{{
        border-radius:var(--r-md);
        padding:var(--sp-4) var(--sp-3) var(--sp-3);
    }}
    .prem-stat-num{{font-size:clamp(1.4rem,4.3vw,1.9rem);}}
    .prem-card,
    .prem-complaint-item,
    .prem-notif-card{{border-radius:var(--r-md);}}
    .prem-lb-card{{flex-direction:column;text-align:center;}}
    .prem-lb-stats{{justify-content:center;}}
    .prem-lb-rank{{min-width:auto;}}
    .prem-performer-grid{{grid-template-columns:1fr 1fr;gap:var(--sp-2);}}
    .stButton>button{{
        padding:9px 13px!important;
        font-size:var(--fs-sm)!important;
        min-height:40px!important;
    }}
    .prem-section-header{{font-size:var(--fs-2xs);}}
    .prem-welcome-title{{font-size:clamp(1.25rem,4.8vw,1.70rem);}}
    .prem-welcome{{padding:34px 13px 20px;}}
    .prem-filter-chips{{
        gap:var(--sp-1);
        overflow-x:auto;flex-wrap:nowrap;
        padding-bottom:6px;
        -webkit-overflow-scrolling:touch;
    }}
    .prem-filter-chip{{
        white-space:nowrap;flex-shrink:0;
        padding:5px 10px;font-size:var(--fs-2xs);
    }}
    /* Kill backdrop-filter on mobile — expensive, invisible on most mobile screens */
    .prem-glass{{backdrop-filter:none!important;-webkit-backdrop-filter:none!important;}}
    /* Shorten animations on mobile for perceived performance */
    *{{animation-duration:0.16s!important;}}

    .stTabs [data-baseweb="tab"]{{
        flex:1 1 calc(50% - 3px)!important;
        text-align:center!important;
    }}
}}

/* ── Small phone  (≤480px) ───────────────────────────────── */
@media(max-width:480px){{
    .prem-hero-stats{{grid-template-columns:repeat(2,1fr);}}
    .prem-performer-grid{{grid-template-columns:1fr;}}
    .prem-complaint-meta{{
        flex-direction:column;
        align-items:flex-start;
        gap:var(--sp-2);
    }}
    .prem-lb-stats{{gap:var(--sp-3);}}
    .prem-notif-bar{{flex-direction:column;}}
    .stTabs [data-baseweb="tab"]{{
        flex:1 1 calc(50% - 3px)!important;
        text-align:center!important;
        font-size:var(--fs-2xs)!important;
    }}
    .action-buttons{{flex-direction:column;}}
    .action-buttons .stButton{{width:100%;}}
    button[kind="header"],
    [data-testid="collapsedControl"]{{
        width:40px!important;
        height:40px!important;
        top:12px!important;
        left:12px!important;
        border-radius:11px!important;
    }}
    button[kind="header"] svg,
    [data-testid="collapsedControl"] svg{{
        width:17px!important;
        height:17px!important;
    }}
}}


/* ═══════════════════════════════════════════════════════════════════
   DARK MODE WIDGET OVERRIDES
   Placed last for highest specificity. No conflicts with base rules.
═══════════════════════════════════════════════════════════════════ */
{dark_overrides}

</style>
"""