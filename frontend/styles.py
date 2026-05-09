def get_css(dark_mode=False):
    # ── colour tokens ─────────────────────────────────────────────────────────
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
        shadow_sm   = "0 1px 4px rgba(0,0,0,0.50),0 4px 12px rgba(0,0,0,0.30)"
        shadow_md   = "0 4px 20px rgba(0,0,0,0.55),0 12px 40px rgba(0,0,0,0.35)"
        shadow_lg   = "0 16px 60px rgba(0,0,0,0.65),0 40px 80px rgba(0,0,0,0.40)"
        green_bg    = "#071A10";  green_bd  = "#166534";  green_text  = "#4ADE80"
        amber_bg    = "#1A1000";  amber_bd  = "#92400E";  amber_text  = "#FCD34D"
        red_bg      = "#1A0505";  red_bd    = "#991B1B";  red_text    = "#FCA5A5"
        blue_bg     = "#04091A";  blue_bd   = "#1E40AF";  blue_text   = "#93C5FD"
        glass_bg    = "rgba(255,255,255,0.04)"
        glass_bd    = "rgba(255,255,255,0.08)"
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
        shadow_sm   = "0 1px 3px rgba(11,20,40,0.06),0 4px 12px rgba(11,20,40,0.06)"
        shadow_md   = "0 4px 16px rgba(11,20,40,0.08),0 12px 32px rgba(11,20,40,0.06)"
        shadow_lg   = "0 12px 48px rgba(11,20,40,0.12),0 32px 64px rgba(11,20,40,0.08)"
        green_bg    = "#F0FDF4";  green_bd  = "#86EFAC";  green_text  = "#166534"
        amber_bg    = "#FFFBEB";  amber_bd  = "#FDE68A";  amber_text  = "#92400E"
        red_bg      = "#FEF2F2";  red_bd    = "#FECACA";  red_text    = "#991B1B"
        blue_bg     = "#EFF6FF";  blue_bd   = "#BFDBFE";  blue_text   = "#1E40AF"
        glass_bg    = "rgba(255,255,255,0.70)"
        glass_bd    = "rgba(255,255,255,0.90)"

    dark_overrides = ""
    if dark_mode:
        dark_overrides = f"""
/* ── DARK MODE WIDGET OVERRIDES ── */
.stSelectbox svg,.stTextInput svg{{fill:{subtext}!important;}}
div[data-baseweb="popover"],div[data-baseweb="menu"],ul[data-testid="stWidgetDropdownList"]{{
    background:{card_bg}!important;border:1px solid {border}!important;
    border-radius:16px!important;box-shadow:{shadow_md}!important;}}
div[data-baseweb="option"]{{background:var(--c-card)!important;color:var(--c-text)!important;}}
div[data-baseweb="option"] *{{color:var(--c-text)!important;opacity:1!important;}}
div[data-baseweb="option"]:hover{{background:var(--c-hover)!important;color:var(--c-text)!important;}}
div[data-baseweb="option"]:hover *{{color:var(--c-text)!important;}}
div[data-baseweb="option"][aria-selected="true"]{{background:var(--c-a1-soft)!important;color:var(--c-a1)!important;}}
div[data-baseweb="option"][aria-selected="true"] *{{color:var(--c-a1)!important;font-weight:700!important;}}
div[data-baseweb="menu"] > *:not([data-baseweb="option"]),
ul[data-testid="stWidgetDropdownList"] > *:not([role="option"]){{color:{text}!important;background-color:transparent!important;}}
div[data-baseweb="option"]{{background:transparent!important;border-radius:10px!important;margin:2px 6px!important;padding:8px 12px!important;color:{text}!important;}}
.stTextInput input,.stTextArea textarea{{caret-color:{accent2}!important;}}
.stRadio label, .stRadio [data-testid="stMarkdownContainer"] p, .stRadio [data-baseweb="radio"] + label{{color:{text}!important;}}
.prem-notif-bar-text{{color:{amber_text}!important;}}
.prem-notif-bar-badge{{color:#fff!important;background:{amber_text}!important;}}
.complaint-desc-box{{color:{text}!important;}}
.prem-badge-closed{{background:{hover_bg}!important;color:{subtext}!important;border:1px solid {border}!important;}}
"""

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Mono:wght@400;500&family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&display=swap');

/* ═══════════════════════════════════════════════════════
   CSS VARIABLES — System Core
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
    
    /* Responsive Spacing & Radii */
    --r-xs:  8px;
    --r-sm:  10px;
    --r-md:  14px;
    --r-lg:  clamp(14px, 2vw, 18px);
    --r-xl:  clamp(18px, 3vw, 24px);
    --r-2xl: clamp(20px, 4vw, 28px);
    
    /* Fluid Typography Strategy */
    --fs-2xs: clamp(0.625rem, 1vw, 0.6875rem);
    --fs-xs:  clamp(0.6875rem, 1.2vw, 0.75rem);
    --fs-sm:  clamp(0.75rem, 1.5vw, 0.875rem);
    --fs-base:clamp(0.875rem, 1.8vw, 0.9375rem);
    --fs-md:  clamp(0.9375rem, 2vw, 1.0625rem);
    --fs-lg:  clamp(1.0625rem, 2.2vw, 1.25rem);
    --fs-xl:  clamp(1.25rem, 2.5vw, 1.5rem);
    --fs-2xl: clamp(1.5rem, 3vw, 1.75rem);
    --fs-3xl: clamp(1.75rem, 4vw, 2.25rem);
    --fs-4xl: clamp(2rem, 5vw, 2.75rem);
    
    /* Strict Spacing System */
    --sp-1: 4px;  --sp-2: 8px;   --sp-3: 12px;
    --sp-4: 16px; --sp-5: 20px;  --sp-6: 24px;
    --sp-8: 32px;
    
    --icon-sm:  1.0rem; --icon-md:  1.25rem;
    --icon-lg:  1.5rem; --icon-xl:  1.75rem;
    --icon-2xl: 2.25rem;
    
    --t-fast: 0.15s cubic-bezier(0.4,0,0.2,1);
    --t-base: 0.22s cubic-bezier(0.4,0,0.2,1);
    --t-slow: 0.35s cubic-bezier(0.4,0,0.2,1);
}}

/* ═══════════════════════════════════════════════════════
   RESET & LAYOUT FOUNDATION
═══════════════════════════════════════════════════════ */
*,*::before,*::after{{box-sizing:border-box;}}

html, body, .stApp {{
    background-color: var(--c-bg) !important;
    color: var(--c-text) !important;
    font-family: 'DM Sans', 'Noto Sans Devanagari', system-ui, sans-serif !important;
    font-size: var(--fs-base);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    letter-spacing: -0.01em;
    overflow-x: hidden !important; /* CRITICAL: Kills mobile horizontal scroll */
}}

p, span, label, small {{ color: var(--c-text) !important; }}

/* ── HIDE CHROME ── */
#MainMenu, footer, header, .stDeployButton {{visibility:hidden!important; display:none!important;}}
.viewerBadge_container__1QSob {{display:none!important;}}

/* ── ANIMATED TOP STRIPE ── */
.stApp::before {{
    content:''; display:block; position:fixed; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg, {accent1}, {accent2}, {accent3}, {accent1});
    background-size:200% 100%;
    animation:prem-gradient-move 6s ease infinite;
    z-index:9999; pointer-events:none;
}}

/* ── MAIN CONTAINER RESPONSIVENESS ── */
.main .block-container {{
    padding: clamp(1rem, 4vw, 2.5rem) clamp(1rem, 5vw, 3rem) 4rem !important;
    max-width: 1280px !important; /* Upgraded for laptop/desktop visual balance */
    margin: 0 auto !important;
    width: 100% !important;
    overflow-x: hidden !important;
}}

/* ═══════════════════════════════════════════════════════
   STREAMLIT CORE COMPONENTS
═══════════════════════════════════════════════════════ */
/* Sidebar */
section[data-testid="stSidebar"] {{
    background: {sidebar_bg} !important;
    border-right: 1px solid var(--c-border) !important;
    color: var(--c-text) !important;
}}
section[data-testid="stSidebar"] .stButton>button {{
    background: var(--c-card2) !important; color: var(--c-text) !important;
    border: 1px solid var(--c-border) !important; border-radius: var(--r-md) !important;
    box-shadow: none !important; font-size: var(--fs-base) !important; font-weight: 600 !important;
    text-align: left !important; justify-content: flex-start !important;
    padding: 10px 15px !important; transition: all var(--t-fast) !important;
}}
section[data-testid="stSidebar"] .stButton>button:hover {{
    background: var(--c-hover) !important; border-color: var(--c-a1) !important;
    transform: translateX(3px) !important;
}}

/* Primary Buttons */
.stButton>button {{
    background: linear-gradient(135deg, {accent1}, {accent2}) !important;
    color: #fff !important; border: none !important; border-radius: var(--r-md) !important;
    padding: 12px 24px !important; font-weight: 600 !important;
    font-size: var(--fs-base) !important; font-family: inherit !important;
    width: 100% !important; letter-spacing: -0.01em !important; cursor: pointer !important;
    line-height: 1.4 !important; position: relative !important; overflow: hidden !important;
    box-shadow: 0 2px 8px {a1_glow} !important;
    will-change: transform, box-shadow;
    transition: transform var(--t-base), box-shadow var(--t-base), filter var(--t-fast) !important;
}}
.stButton>button::before {{
    content:''; position:absolute; inset:0; pointer-events:none; border-radius:inherit;
    background:linear-gradient(180deg, rgba(255,255,255,0.14) 0%, transparent 100%);
}}
.stButton>button:hover {{
    transform: translateY(-2px) scale(1.006) !important;
    box-shadow: 0 6px 20px {a1_glow} !important; filter: brightness(1.05) !important;
}}
.stButton>button:active {{ transform: translateY(0) scale(0.998) !important; }}

/* Secondary Buttons */
button[kind="secondary"], button[data-testid="baseButton-secondary"] {{
    background: linear-gradient(135deg, var(--c-a1), var(--c-a2)) !important;
    color: #fff !important; border: none !important; border-radius: var(--r-md) !important;
    box-shadow: 0 4px 14px var(--c-a1-glow) !important;
}}
button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover {{
    transform: translateY(-2px) !important; filter: brightness(1.05) !important;
    box-shadow: 0 8px 24px var(--c-a1-glow) !important;
}}

/* Inputs & Selects */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {{
    background: var(--c-input) !important; border: 1px solid var(--c-border) !important;
    border-radius: var(--r-md) !important; color: var(--c-text) !important;
    font-family: inherit !important; font-size: var(--fs-base) !important;
    padding: 12px 16px !important; width: 100% !important;
    transition: border-color var(--t-fast), box-shadow var(--t-fast) !important;
}}
.stSelectbox > div > div {{ min-height: 44px !important; }}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus, .stSelectbox>div>div:hover {{
    border-color: var(--c-a1) !important; box-shadow: 0 0 0 3px var(--c-a1-soft) !important;
    outline: none !important; background: var(--c-card) !important;
}}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {{ color: var(--c-sub) !important; opacity: 0.65 !important; }}

/* Form Labels */
label, .stTextInput label, .stTextArea label, .stSelectbox label {{
    color: var(--c-sub) !important; font-weight: 600 !important; font-size: var(--fs-xs) !important;
    text-transform: uppercase !important; letter-spacing: 0.07em !important; margin-bottom: 6px !important;
    display: block !important;
}}

/* Expanders */
[data-testid="stExpander"] {{
    border: 1px solid var(--c-border) !important; border-radius: var(--r-md) !important;
    background: var(--c-card) !important; margin-bottom: var(--sp-4) !important;
    overflow: hidden !important; box-shadow: var(--sh-sm) !important;
    transition: all var(--t-fast) !important;
}}
.streamlit-expanderHeader {{
    background: var(--c-card) !important; border-radius: var(--r-md) !important;
    font-weight: 600 !important; color: var(--c-text) !important; border: none !important;
    padding: 14px 18px !important; font-size: var(--fs-base) !important;
}}
.streamlit-expanderHeader:hover {{ color: var(--c-a1) !important; background: var(--c-hover) !important; }}
.streamlit-expanderContent {{
    background: var(--c-card) !important; border-top: 1px solid var(--c-border) !important;
    padding: var(--sp-4) clamp(12px, 3vw, 24px) !important;
}}

/* Alerts & Progress */
.stSuccess {{background:{green_bg}!important; border:1px solid {green_bd}!important; border-radius:var(--r-md)!important; color:{green_text}!important; padding:var(--sp-3)!important;}}
.stInfo    {{background:{blue_bg}!important; border:1px solid {blue_bd}!important; border-radius:var(--r-md)!important; color:{blue_text}!important; padding:var(--sp-3)!important;}}
.stWarning {{background:{amber_bg}!important; border:1px solid {amber_bd}!important; border-radius:var(--r-md)!important; color:{amber_text}!important; padding:var(--sp-3)!important;}}
.stError   {{background:{red_bg}!important; border:1px solid {red_bd}!important; border-radius:var(--r-md)!important; color:{red_text}!important; padding:var(--sp-3)!important;}}

.stProgress>div>div {{ background: linear-gradient(90deg, {accent1}, {accent2}) !important; border-radius: 99px !important; }}
.stProgress>div {{ background: var(--c-border) !important; border-radius: 99px !important; height: 6px !important; }}

/* ═══════════════════════════════════════════════════════
   PREMIUM CUSTOM COMPONENTS
═══════════════════════════════════════════════════════ */
/* ── HERO BANNER ── */
.prem-hero {{
    background: linear-gradient(135deg, {hero_from} 0%, {hero_mid} 50%, {hero_to} 100%);
    border-radius: var(--r-xl); padding: clamp(20px, 5vw, 40px) clamp(20px, 5vw, 40px) var(--sp-6);
    color: #fff; margin-bottom: var(--sp-6); position: relative; overflow: hidden;
    box-shadow: var(--sh-lg); border: 1px solid rgba(255,255,255,0.10);
}}
.prem-hero-title {{
    font-family: 'Bricolage Grotesque', sans-serif; font-size: var(--fs-3xl);
    font-weight: 800; line-height: 1.2; margin-bottom: var(--sp-1);
    position: relative; z-index: 1; color: #fff; letter-spacing: -0.03em;
}}
.prem-hero-sub {{ font-size: var(--fs-base); opacity: 0.88; position: relative; z-index: 1; font-weight: 400; max-width: 800px; margin-bottom: var(--sp-4); line-height: 1.5; }}
.prem-hero-avatar {{
    position: absolute; top: clamp(16px, 3vw, 24px); right: clamp(16px, 3vw, 26px);
    width: clamp(40px, 8vw, 56px); height: clamp(40px, 8vw, 56px); border-radius: 50%;
    background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.28);
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: var(--fs-md); z-index: 1; backdrop-filter: blur(12px);
}}
.prem-hero-stats {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 120px), 1fr));
    gap: var(--sp-3); margin-top: var(--sp-5); position: relative; z-index: 1;
}}
.prem-hstat {{
    background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.16);
    border-radius: var(--r-md); padding: var(--sp-3) var(--sp-2); text-align: center;
    backdrop-filter: blur(12px); transition: background var(--t-fast), transform var(--t-fast);
}}
.prem-hstat-num {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: var(--fs-3xl); font-weight: 800; line-height: 1; margin-bottom: var(--sp-1); }}
.prem-hstat-lbl {{ font-size: var(--fs-2xs); font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.8; }}
.prem-hstat.h-blue  .prem-hstat-num{{color:#BAC8FF;}} .prem-hstat.h-amber .prem-hstat-num{{color:#FDE68A;}}
.prem-hstat.h-green .prem-hstat-num{{color:#6EE7B7;}} .prem-hstat.h-red   .prem-hstat-num{{color:#FCA5A5;}}

/* ── CARDS & DASHBOARDS ── */
.prem-card {{
    background: var(--c-card); border-radius: var(--r-lg); padding: clamp(16px, 3vw, 24px);
    margin: var(--sp-2) 0; border: 1px solid var(--c-border); box-shadow: var(--sh-sm);
    transition: transform var(--t-base), box-shadow var(--t-base), border-color var(--t-fast);
    will-change: transform, box-shadow; width: 100%; overflow: hidden;
}}
.prem-card:hover {{ transform: translateY(-3px); box-shadow: var(--sh-md); border-color: {accent1}44; }}

.prem-stat-card {{
    background: var(--c-card); border-radius: var(--r-lg); padding: var(--sp-6) var(--sp-4);
    text-align: center; border: 1px solid var(--c-border); box-shadow: var(--sh-sm);
    position: relative; overflow: hidden; transition: transform var(--t-base), box-shadow var(--t-base);
    height: 100%; display: flex; flex-direction: column; justify-content: center;
}}
.prem-stat-card::before {{ content:''; position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg,{accent1},{accent2}); }}
.prem-stat-num {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: var(--fs-3xl); font-weight: 800; color: var(--c-text); }}
.prem-stat-lbl {{ font-size: var(--fs-xs); color: var(--c-sub); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: var(--sp-2); }}

.prem-action-card {{
    background: var(--c-card); border-radius: var(--r-lg); padding: var(--sp-5) var(--sp-4);
    text-align: center; border: 1px solid var(--c-border); cursor: pointer;
    box-shadow: var(--sh-sm); position: relative; overflow: hidden; transition: all var(--t-base);
}}
.prem-action-card:hover {{ transform: translateY(-5px); box-shadow: var(--sh-md); border-color: {accent1}66; }}
.prem-action-icon {{ width: 56px; height: 56px; border-radius: var(--r-md); display: flex; align-items: center; justify-content: center; font-size: var(--icon-xl); margin: 0 auto var(--sp-3); background: var(--c-hover); color: var(--c-a1); }}

/* ── COMPLAINT CARDS ── */
.complaint-card {{
    background: var(--c-card); border-radius: var(--r-xl); margin-bottom: var(--sp-4);
    border: 1px solid var(--c-border) !important; transition: all var(--t-base);
    overflow: hidden; display: flex; flex-direction: column; width: 100%;
    box-shadow: var(--sh-sm);
}}
.complaint-card:hover {{ transform: translateY(-3px); box-shadow: var(--sh-md); border-color: var(--c-a1) !important; }}
.complaint-priority-high   {{ border-left: 5px solid #EF4444 !important; }}
.complaint-priority-medium {{ border-left: 5px solid #F59E0B !important; }}
.complaint-priority-low    {{ border-left: 5px solid #10B981 !important; }}

.complaint-header {{
    display: flex; justify-content: space-between; align-items: flex-start;
    flex-wrap: wrap; gap: var(--sp-3); margin-bottom: var(--sp-3); padding: var(--sp-4) var(--sp-5) 0;
}}
.complaint-desc-box {{
    background: var(--c-card2); padding: clamp(12px, 2vw, 16px); border-radius: var(--r-md);
    margin: 0 var(--sp-5) var(--sp-3); border: 1px solid var(--c-border);
    color: var(--c-text) !important; font-size: var(--fs-base); line-height: 1.6;
    white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere;
    max-height: 250px; overflow-y: auto;
}}
.complaint-meta {{
    display: flex; flex-wrap: wrap; gap: var(--sp-3); font-size: var(--fs-xs);
    color: var(--c-sub); padding: 0 var(--sp-5) var(--sp-4); border-bottom: 1px solid var(--c-border);
}}
.action-buttons {{ display: flex; flex-wrap: wrap; gap: var(--sp-2); padding: var(--sp-3) var(--sp-5); background: var(--c-bg); }}

/* ── BADGES & TAGS ── */
.badge-status, .badge-priority, .prem-badge, .prem-tag {{
    display: inline-flex; align-items: center; gap: 4px; border-radius: 30px;
    padding: 4px 12px; font-size: var(--fs-xs); font-weight: 700; white-space: nowrap;
    text-transform: uppercase; letter-spacing: 0.04em; flex-shrink: 0;
}}
.badge-pending {{background:{amber_bg}; color:{amber_text}; border: 1px solid {amber_bd};}}
.badge-in_progress {{background:{blue_bg}; color:{blue_text}; border: 1px solid {blue_bd};}}
.badge-resolved {{background:{green_bg}; color:{green_text}; border: 1px solid {green_bd};}}
.badge-closed {{background:{hover_bg}; color:{subtext}; border: 1px solid {border};}}
.badge-priority-high {{background:{red_bg}; color:{red_text}; border: 1px solid {red_bd};}}
.badge-priority-medium {{background:{amber_bg}; color:{amber_text}; border: 1px solid {amber_bd};}}
.badge-priority-low {{background:{green_bg}; color:{green_text}; border: 1px solid {green_bd};}}

/* ── LEADERBOARD & PERFORMERS ── */
.prem-lb-card {{
    background: var(--c-card); border-radius: var(--r-lg); padding: var(--sp-4) clamp(16px, 3vw, 24px);
    margin: var(--sp-2) 0; border: 1px solid var(--c-border); box-shadow: var(--sh-sm);
    display: flex; gap: var(--sp-4); align-items: center; flex-wrap: wrap; width: 100%;
    position: relative; overflow: hidden; transition: transform var(--t-fast);
}}
.prem-lb-rank {{
    font-family: 'Bricolage Grotesque', sans-serif; font-size: var(--fs-2xl); font-weight: 800;
    min-width: 50px; text-align: center; color: {amber_text}; flex-shrink: 0;
}}
.prem-lb-info {{ flex: 1 1 min(100%, 200px); min-width: 0; }} /* Prevents flex blowout */
.prem-lb-name {{ font-weight: 700; font-size: var(--fs-md); margin-bottom: 4px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; color: var(--c-text); }}
.prem-lb-stats {{ display: flex; gap: var(--sp-4); flex-wrap: wrap; flex-shrink: 0; }}
.prem-performer-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 160px), 1fr));
    gap: var(--sp-3); margin: var(--sp-4) 0;
}}

/* ── NOTIFICATIONS & TIMELINES ── */
.prem-notif-card {{
    background: var(--c-card); border-radius: var(--r-md); padding: var(--sp-4);
    margin: var(--sp-2) 0; border: 1px solid var(--c-border); display: flex; gap: var(--sp-3);
    align-items: flex-start; box-shadow: var(--sh-sm); width: 100%;
}}
.prem-tl-item {{ display: flex; gap: var(--sp-3); align-items: flex-start; margin-bottom: 8px; width: 100%; }}
.prem-tl-dot {{ width: 24px; height: 24px; border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: 800; margin-top: 2px; }}
.prem-tl-info {{ flex: 1; padding: 2px 0; min-width: 0; }} /* Protect text overflow */
.prem-tl-label {{ font-size: var(--fs-sm); font-weight: 600; color: var(--c-text); word-wrap: break-word; }}

/* ── SECTION HEADERS & UTILS ── */
.prem-section-header {{
    font-size: var(--fs-xs); font-weight: 700; text-transform: uppercase; letter-spacing: 0.10em;
    color: var(--c-sub); margin: var(--sp-8) 0 var(--sp-4); display: flex; align-items: center; gap: 10px; width: 100%;
}}
.prem-section-header::before {{ content:''; width:4px; height:16px; background:linear-gradient(180deg,{accent1},{accent2}); border-radius:99px; }}
.prem-section-header::after {{ content:''; flex:1; height:1px; background:var(--c-border); }}

/* ═══════════════════════════════════════════════════════
   ANIMATIONS
═══════════════════════════════════════════════════════ */
@keyframes prem-fade-up {{ from{{opacity:0; transform:translateY(15px);}} to{{opacity:1; transform:translateY(0);}} }}
@keyframes prem-scale-in {{ from{{opacity:0; transform:scale(0.97);}} to{{opacity:1; transform:scale(1);}} }}
@keyframes prem-gradient-move {{ 0%,100%{{background-position:0% 50%;}} 50%{{background-position:100% 50%;}} }}

.prem-card, .complaint-card, .prem-notif-card, .prem-lb-card, .prem-hero {{ animation: prem-fade-up 0.3s ease both; }}
.prem-stat-card, .prem-action-card {{ animation: prem-scale-in 0.3s ease both; }}

/* ═══════════════════════════════════════════════════════
   RESPONSIVE ARCHITECTURE (Mobile First overrides)
═══════════════════════════════════════════════════════ */

/* ── TABLET PORTRAIT & SMALL LAPTOPS (<= 1024px) ── */
@media(max-width: 1024px) {{
    .main .block-container {{ padding: 1.5rem 1.5rem 3rem !important; max-width: 100% !important; }}
    .prem-hero-avatar {{ display: none; }} /* Free up header space */
    .prem-lb-card {{ flex-direction: column; align-items: flex-start; gap: var(--sp-3); }}
    .prem-lb-stats {{ width: 100%; justify-content: flex-start; }}
    .prem-performer-grid {{ grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }}
    .complaint-header {{ flex-direction: column; align-items: flex-start; }}
}}

/* ── MOBILE LARGE (<= 768px) ── */
@media(max-width: 768px) {{
    .main .block-container {{ padding: 1rem 1rem 2.5rem !important; }}
    .prem-hero {{ padding: var(--sp-5) var(--sp-4); text-align: center; }}
    .prem-hero-stats {{ grid-template-columns: repeat(2, 1fr); gap: var(--sp-2); }}
    .prem-action-card {{ padding: var(--sp-4) var(--sp-3); }}
    .prem-action-icon {{ width: 48px; height: 48px; font-size: var(--icon-lg); }}
    .stButton>button {{ padding: 12px 16px !important; }}
    
    /* Force Streamlit Columns to Stack Earlier */
    [data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; margin-bottom: var(--sp-4) !important; }}
    
    /* Complaint Cards Mobile Optimization */
    .complaint-meta {{ flex-direction: column; gap: var(--sp-2); }}
    .action-buttons {{ justify-content: stretch; }}
    .action-buttons > button {{ flex: 1 1 100%; }}
}}

/* ── MOBILE SMALL (<= 480px) ── */
@media(max-width: 480px) {{
    .prem-hero-stats {{ grid-template-columns: 1fr; }} /* Stack stats vertically on tiny screens */
    .prem-lb-stats {{ gap: var(--sp-2); justify-content: space-between; }}
    .prem-lb-stat-item {{ text-align: left; }}
    .badge-status, .badge-priority {{ padding: 6px 12px; font-size: 10px; width: fit-content; }}
    .prem-section-header {{ margin: var(--sp-5) 0 var(--sp-3); }}
}}

{dark_overrides}
</style>
"""