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
div[data-baseweb="option"]{{
    background:var(--c-card)!important;
    color:var(--c-text)!important;
}}
div[data-baseweb="option"] *{{
    color:var(--c-text)!important;
    opacity:1!important;
}}
div[data-baseweb="option"]:hover{{
    background:var(--c-hover)!important;
    color:var(--c-text)!important;
}}
div[data-baseweb="option"]:hover *{{
    color:var(--c-text)!important;
}}
div[data-baseweb="option"][aria-selected="true"]{{
    background:var(--c-a1-soft)!important;
    color:var(--c-a1)!important;
}}
div[data-baseweb="option"][aria-selected="true"] *{{
    color:var(--c-a1)!important;
    font-weight:700!important;
}}
div[data-baseweb="menu"] > *:not([data-baseweb="option"]),
ul[data-testid="stWidgetDropdownList"] > *:not([role="option"]){{
    color:{text}!important;background-color:transparent!important;}}
div[data-baseweb="option"]{{background:transparent!important;border-radius:10px!important;
    margin:2px 6px!important;padding:8px 12px!important;color:{text}!important;}}
div[data-baseweb="option"]:hover,li[role="option"]:hover{{background:{hover_bg}!important;}}
div[data-baseweb="option"]:hover *,li[role="option"]:hover *{{color:{text}!important;}}
div[data-baseweb="option"][aria-selected="true"],li[role="option"][aria-selected="true"]{{
    background:{a1_soft}!important;}}
div[data-baseweb="option"][aria-selected="true"] *,li[role="option"][aria-selected="true"] *{{
    color:{accent2}!important;font-weight:700!important;}}
.stTextInput input,.stTextArea textarea{{caret-color:{accent2}!important;}}
.stRadio label{{color:{text}!important;}}
.stRadio [data-testid="stMarkdownContainer"] p{{color:{text}!important;}}
.stRadio [data-baseweb="radio"] + label{{color:{text}!important;}}
.prem-notif-bar-text{{color:{amber_text}!important;}}
.prem-notif-bar-badge{{color:#fff!important;background:{amber_text}!important;}}
.complaint-desc-box{{color:{text}!important;}}
.prem-badge-closed{{background:{hover_bg}!important;color:{subtext}!important;border:1px solid {border}!important;}}
"""

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Mono:wght@400;500&family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&display=swap');

/* ═══════════════════════════════════════════════════════
   CSS VARIABLES — single source of truth
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
    --r-xs:   clamp(6px, 1.5vw, 8px);
    --r-sm:   clamp(8px, 2vw, 10px);
    --r-md:   clamp(10px, 2.5vw, 14px);
    --r-lg:   clamp(14px, 3vw, 18px);
    --r-xl:   clamp(18px, 4vw, 24px);
    --r-2xl:  clamp(22px, 5vw, 28px);
    --fs-2xs: clamp(0.625rem, 1.5vw, 0.6875rem);
    --fs-xs:  clamp(0.6875rem, 1.8vw, 0.75rem);
    --fs-sm:  clamp(0.75rem, 2vw, 0.875rem);
    --fs-base:clamp(0.875rem, 2.2vw, 1rem);
    --fs-md:  clamp(0.9375rem, 2.5vw, 1.0625rem);
    --fs-lg:  clamp(1.0625rem, 3vw, 1.25rem);
    --fs-xl:  clamp(1.25rem, 3.5vw, 1.5rem);
    --fs-2xl: clamp(1.5rem, 4vw, 1.75rem);
    --fs-3xl: clamp(1.75rem, 5vw, 2.25rem);
    --fs-4xl: clamp(2rem, 6vw, 2.5rem);
    --sp-1:  clamp(4px, 1vw, 6px);
    --sp-2:  clamp(8px, 1.5vw, 10px);
    --sp-3:  clamp(12px, 2vw, 14px);
    --sp-4:  clamp(16px, 2.5vw, 20px);
    --sp-5:  clamp(20px, 3vw, 24px);
    --sp-6:  clamp(24px, 4vw, 32px);
    --sp-8:  clamp(32px, 5vw, 48px);
    --t-fast: 0.15s cubic-bezier(0.4,0,0.2,1);
    --t-base: 0.22s cubic-bezier(0.4,0,0.2,1);
    --t-slow: 0.35s cubic-bezier(0.4,0,0.2,1);
}}

/* ═══════════════════════════════════════════════════════
   RESET & BASE — Prevent overflow & improve performance
═══════════════════════════════════════════════════════ */
*,*::before,*::after{{box-sizing:border-box;}}
html,body,.stApp{{
    background-color:var(--c-bg)!important;
    color:var(--c-text)!important;
    font-family:'DM Sans','Noto Sans Devanagari',system-ui,sans-serif!important;
    font-size:var(--fs-base);
    line-height:1.6;
    -webkit-font-smoothing:antialiased;
    overflow-x:clip!important;
    max-width:100%!important;
}}
body, .stApp {{
    overflow-x: hidden !important;
    width: 100% !important;
    margin: 0 auto !important;
}}
p,span,label,small{{color:var(--c-text)!important;}}
.prem-empty-state,
.prem-empty-state *{{color:var(--c-text)!important;opacity:1!important;}}
.prem-section-header,
.prem-section-header *{{color:var(--c-text)!important;}}
#MainMenu,footer,header,.stDeployButton{{visibility:hidden!important;display:none!important;}}
.viewerBadge_container__1QSob{{display:none!important;}}

/* ── ANIMATED TOP STRIPE ── */
.stApp::before{{
    content:'';display:block;position:fixed;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,{accent1},{accent2},{accent3},{accent1});
    background-size:200% 100%;
    animation:prem-gradient-move 6s ease infinite;
    z-index:9999;pointer-events:none;
}}

/* ═══════════════════════════════════════════════════════
   RESPONSIVE MAIN CONTAINER — Fixes spacing & stretching
═══════════════════════════════════════════════════════ */
.main .block-container{{
    padding:clamp(1rem, 3vw, 2rem) clamp(1rem, 4vw, 3rem) clamp(3rem, 6vw, 5rem)!important;
    max-width:min(1200px, 90vw)!important;
    margin:0 auto!important;
    width:100%!important;
}}

/* ═══════════════════════════════════════════════════════
   SIDEBAR — Mobile & Tablet friendly
═══════════════════════════════════════════════════════ */
section[data-testid="stSidebar"]{{
    background:{sidebar_bg}!important;
    border-right:1px solid var(--c-border)!important;
    color:var(--c-text)!important;
}}
@media (max-width: 768px) {{
    section[data-testid="stSidebar"] {{
        width: 280px !important;
    }}
    section[data-testid="stSidebar"] .stButton>button {{
        padding: 8px 12px !important;
        font-size: var(--fs-sm) !important;
    }}
}}
section[data-testid="stSidebar"] .stButton>button{{
    background:var(--c-card2)!important;
    color:var(--c-text)!important;
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-md)!important;
    font-weight:600!important;
    text-align:left!important;
    justify-content:flex-start!important;
    padding:clamp(8px, 2vw, 12px) clamp(12px, 3vw, 18px)!important;
    transition:all var(--t-fast)!important;
}}
section[data-testid="stSidebar"] .stButton>button:hover{{
    background:var(--c-hover)!important;
    border-color:var(--c-a1)!important;
    transform:translateX(3px)!important;
}}

/* ═══════════════════════════════════════════════════════
   BUTTONS — Responsive sizing
═══════════════════════════════════════════════════════ */
.stButton>button{{
    background:linear-gradient(135deg,{accent1},{accent2})!important;
    color:#fff!important;border:none!important;
    border-radius:var(--r-md)!important;
    padding:clamp(8px, 2vw, 12px) clamp(16px, 4vw, 24px)!important;
    font-weight:600!important;
    font-size:var(--fs-base)!important;
    width:100%!important;
    cursor:pointer!important;
    transition:transform var(--t-base),box-shadow var(--t-base),filter var(--t-fast)!important;
    box-shadow:0 2px 8px {a1_glow}!important;
}}
.stButton>button:hover{{
    transform:translateY(-2px) scale(1.006)!important;
    box-shadow:0 6px 20px {a1_glow}!important;
    filter:brightness(1.05)!important;
}}
@media (max-width: 768px) {{
    .stButton>button {{
        padding: 8px 14px !important;
        font-size: var(--fs-sm) !important;
    }}
}}

/* ═══════════════════════════════════════════════════════
   INPUTS & SELECTBOX — Prevent overflow
═══════════════════════════════════════════════════════ */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div>div{{
    background:var(--c-input)!important;
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-md)!important;
    color:var(--c-text)!important;
    padding:clamp(8px, 2vw, 12px) clamp(10px, 2.5vw, 14px)!important;
    width:100%!important;
}}
.stSelectbox > div > div{{
    background:var(--c-input)!important;
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-md)!important;
    min-height:44px!important;
}}
div[data-baseweb="popover"]{{
    background:var(--c-card)!important;
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-lg)!important;
    max-height: 60vh;
    overflow-y: auto;
}}
div[data-baseweb="option"]{{
    background:transparent!important;
    color:var(--c-text)!important;
    padding:clamp(6px, 2vw, 10px) clamp(10px, 2.5vw, 14px)!important;
    margin:3px 6px!important;
    border-radius:var(--r-sm)!important;
    word-break: break-word;
}}
/* fix text overflow in dropdowns */
div[data-baseweb="option"] span {{
    white-space: normal !important;
    word-break: break-word !important;
}}

/* ═══════════════════════════════════════════════════════
   TABS — Mobile overflow protection
═══════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"]{{
    background:var(--c-card)!important;
    border-radius:var(--r-lg)!important;
    padding:clamp(4px, 1.5vw, 8px)!important;
    flex-wrap: wrap !important;
}}
.stTabs [data-baseweb="tab"]{{
    border-radius:var(--r-sm)!important;
    font-weight:600!important;
    font-size:var(--fs-sm)!important;
    padding:clamp(6px, 2vw, 10px) clamp(12px, 3vw, 20px)!important;
}}
@media (max-width: 640px) {{
    .stTabs [data-baseweb="tab-list"] {{
        flex-direction: column !important;
        gap: 6px !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        width: 100% !important;
        text-align: center !important;
    }}
}}

/* ═══════════════════════════════════════════════════════
   EXPANDER — Better mobile layout
═══════════════════════════════════════════════════════ */
[data-testid="stExpander"]{{
    border:1px solid var(--c-border)!important;
    border-radius:var(--r-md)!important;
    background:var(--c-card)!important;
    margin-bottom:var(--sp-4)!important;
    overflow:hidden!important;
}}
.streamlit-expanderHeader{{
    background:var(--c-card)!important;
    color:var(--c-text)!important;
    padding:clamp(10px, 2.5vw, 14px) clamp(14px, 3vw, 18px)!important;
    font-size:var(--fs-base)!important;
}}
.streamlit-expanderContent{{
    background:var(--c-card)!important;
    padding:clamp(12px, 3vw, 20px) clamp(12px, 4vw, 24px)!important;
}}

/* ═══════════════════════════════════════════════════════
   COMPLAINT CARD — Consistent & responsive
═══════════════════════════════════════════════════════ */
.prem-complaint-item{{
    background:var(--c-card);
    border-radius:var(--r-lg);
    padding:clamp(12px, 3vw, 20px) clamp(16px, 4vw, 28px);
    margin:var(--sp-3) 0;
    border:1px solid var(--c-border)!important;
    border-left:4px solid {accent1};
    transition:all var(--t-base);
    word-break:break-word;
    overflow-x:auto;
}}
.complaint-desc-box{{
    background:var(--c-card2);
    padding:var(--sp-3) var(--sp-4);
    border-radius:var(--r-md);
    margin:var(--sp-3) 0;
    border:1px solid var(--c-border);
    color:var(--c-text)!important;
    word-break:break-word;
    max-height:clamp(150px, 30vh, 200px);
    overflow-y:auto;
}}
.complaint-meta{{
    display:flex;
    gap:var(--sp-3);
    flex-wrap:wrap;
    font-size:var(--fs-xs);
    color:var(--c-sub);
}}
.action-buttons{{
    display:flex;
    gap:var(--sp-2);
    flex-wrap:wrap;
}}

/* ═══════════════════════════════════════════════════════
   GRID SYSTEMS — Responsive card layouts
═══════════════════════════════════════════════════════ */
.prem-hero-stats,
.prem-performer-grid,
.prem-stat-grid {{
    display:grid;
    grid-template-columns:repeat(auto-fit, minmax(min(160px, 100%), 1fr));
    gap:var(--sp-4);
    margin:var(--sp-4) 0;
}}
.prem-stat-card,
.prem-action-card,
.prem-performer-card {{
    height:100%;
    display:flex;
    flex-direction:column;
    justify-content:center;
}}

/* ── Hero banner responsive ── */
.prem-hero{{
    background:linear-gradient(135deg,{hero_from} 0%,{hero_mid} 50%,{hero_to} 100%);
    border-radius:var(--r-xl);
    padding:clamp(24px, 6vw, 48px) clamp(20px, 5vw, 40px) clamp(20px, 5vw, 32px);
    margin-bottom:var(--sp-6);
    position:relative;
    overflow:hidden;
}}
.prem-hero-avatar{{
    position:absolute;
    top:clamp(16px, 4vw, 24px);
    right:clamp(16px, 4vw, 26px);
    width:clamp(40px, 8vw, 50px);
    height:clamp(40px, 8vw, 50px);
}}
@media (max-width: 640px) {{
    .prem-hero-avatar {{ display: none; }}
    .prem-hero-stats {{ grid-template-columns: repeat(2, 1fr); gap: var(--sp-2); }}
}}
.prem-hero-title{{
    font-size:clamp(1.5rem, 6vw, 2.25rem);
    word-break:break-word;
}}
.prem-hero-sub{{
    font-size:clamp(0.875rem, 3vw, 1rem);
}}
.prem-hstat-num{{
    font-size:clamp(1.75rem, 5vw, 2.5rem);
}}

/* ═══════════════════════════════════════════════════════
   NOTIFICATION CARDS — Prevent overlap
═══════════════════════════════════════════════════════ */
.prem-notif-card{{
    display:flex;
    flex-wrap:wrap;
    gap:var(--sp-3);
    align-items:flex-start;
}}
.prem-notif-bar{{
    flex-wrap:wrap;
    gap:var(--sp-2);
}}
.prem-notif-bar-text{{
    flex:1;
    min-width:150px;
}}

/* ═══════════════════════════════════════════════════════
   LEADERBOARD & TIMELINE — Responsive stacking
═══════════════════════════════════════════════════════ */
.prem-lb-card{{
    flex-direction:row;
    flex-wrap:wrap;
    gap:var(--sp-3);
    padding:var(--sp-4) var(--sp-5);
}}
@media (max-width: 640px) {{
    .prem-lb-card {{
        flex-direction:column;
        text-align:center;
    }}
    .prem-lb-stats {{
        justify-content:center;
    }}
}}
.prem-tl-item{{
    flex-wrap:wrap;
}}

/* ═══════════════════════════════════════════════════════
   BADGES & TAGS — Alignment fix
═══════════════════════════════════════════════════════ */
.prem-badge,
.prem-tag,
.badge-status,
.badge-priority {{
    display:inline-flex;
    align-items:center;
    white-space:nowrap;
}}
@media (max-width: 480px) {{
    .prem-badge, .prem-tag, .badge-status {{
        white-space:normal;
        word-break:keep-all;
    }}
}}

/* ═══════════════════════════════════════════════════════
   PERFORMANCE: reduce blur & shadow on mobile
═══════════════════════════════════════════════════════ */
@media (max-width: 768px) {{
    .prem-glass {{
        backdrop-filter:none !important;
        background:{glass_bg}!important;
    }}
    .prem-hero::before, .prem-hero::after {{
        display:none;
    }}
    * {{
        animation-duration: 0.25s !important;
    }}
}}

/* ═══════════════════════════════════════════════════════
   UTILITIES & OVERFLOW FIXES
═══════════════════════════════════════════════════════ */
* {{
    word-break: break-word;
    max-width: 100%;
}}
img, svg, iframe {{
    max-width: 100%;
    height: auto;
}}
.stMarkdown table {{
    display: block;
    overflow-x: auto;
    white-space: nowrap;
}}
hr {{
    margin: var(--sp-6) 0 !important;
}}
::-webkit-scrollbar {{
    width: 4px;
    height: 4px;
}}
.prem-empty-state {{
    padding: clamp(2rem, 10vw, 5rem) 1rem;
}}

/* ═══════════════════════════════════════════════════════
   ANIMATIONS (preserved)
═══════════════════════════════════════════════════════ */
@keyframes prem-fade-up{{from{{opacity:0;transform:translateY(18px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes prem-fade-in {{from{{opacity:0;}}to{{opacity:1;}}}}
@keyframes prem-scale-in{{from{{opacity:0;transform:scale(0.96);}}to{{opacity:1;transform:scale(1);}}}}
@keyframes prem-pulse-ring{{
    0%  {{box-shadow:0 0 0 0 {a1_glow};}}
    70% {{box-shadow:0 0 0 12px rgba(99,102,241,0);}}
    100%{{box-shadow:0 0 0 0 rgba(99,102,241,0);}}
}}
@keyframes prem-shimmer{{0%{{background-position:-200% 0;}}100%{{background-position:200% 0;}}}}
@keyframes prem-gradient-move{{0%,100%{{background-position:0% 50%;}}50%{{background-position:100% 50%;}}}}
@keyframes prem-float{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-8px);}}}}

.prem-card,.prem-complaint-item,.prem-notif-card,
.prem-scheme-card,.prem-lb-card,.prem-hero{{animation:prem-fade-up 0.28s ease both;}}
.prem-stat-card{{animation:prem-scale-in 0.28s ease both;}}

/* ═══════════════════════════════════════════════════════
   DARK MODE OVERRIDES (injected)
═══════════════════════════════════════════════════════ */
{dark_overrides}

/* ═══════════════════════════════════════════════════════
   ADDITIONAL TABLET / MOBILE BREAKPOINTS
═══════════════════════════════════════════════════════ */
@media (max-width: 1024px) {{
    .main .block-container {{
        max-width: 95vw !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }}
    .prem-hero-stats {{
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    }}
}}
@media (max-width: 480px) {{
    .prem-complaint-meta {{
        flex-direction: column;
        align-items: flex-start;
        gap: var(--sp-2);
    }}
    .prem-notif-bar {{
        flex-direction: column;
        text-align: center;
    }}
    .prem-filter-chips {{
        overflow-x: auto;
        flex-wrap: nowrap;
        padding-bottom: 8px;
    }}
    .prem-filter-chip {{
        white-space: nowrap;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
    }}
}}
</style>
"""