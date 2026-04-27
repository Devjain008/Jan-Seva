import streamlit as st
import requests
import json
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from frontend.config import TRANSLATIONS, API_BASE

def t(key):
    lang = st.session_state.get("language", "en")
    tr = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return tr.get(key, key)

def _qp_first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v

def _reverse_geocode(lat: float, lon: float) -> str:
    """Convert coordinates to human-readable location text."""
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"format": "jsonv2", "lat": lat, "lon": lon, "zoom": 16, "addressdetails": 1},
            headers={"User-Agent": "jan-seva-portal/1.0"},
            timeout=6,
        )
        if r.status_code == 200:
            d = r.json()
            addr = d.get("address", {})
            parts = [
                addr.get("suburb") or addr.get("neighbourhood") or addr.get("village") or addr.get("hamlet"),
                addr.get("city") or addr.get("town") or addr.get("county"),
                addr.get("state"),
            ]
            text = ", ".join([p for p in parts if p])
            return text or d.get("display_name", "")
    except Exception:
        pass
    return ""

VOICE_HTML = """
<div style="text-align:center;padding:20px;">
<button onclick="startVoiceCapture()" id="voiceBtn" style="
    background: linear-gradient(135deg, #ec4899, #8b5cf6);
    color: white; border: none; border-radius: 50%;
    width: 72px; height: 72px; font-size: 2rem;
    cursor: pointer; box-shadow: 0 4px 20px rgba(236,72,153,0.5);
    transition: all 0.3s;
">🎤</button>
<div id="voiceStatus" style="margin-top:12px;font-size:0.9rem;color:#666;font-family:sans-serif;"></div>
<div id="voiceResult" style="margin-top:8px;font-size:0.85rem;background:#f0f0ff;border-radius:10px;padding:8px 12px;display:none;"></div>
</div>

<script>
var voiceText = '';
function startVoiceCapture() {
    var btn = document.getElementById('voiceBtn');
    var status = document.getElementById('voiceStatus');
    var result = document.getElementById('voiceResult');
    
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        status.textContent = '❌ Voice not supported. Use Chrome browser.';
        return;
    }
    
    var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    var lang = '""" + st.session_state.get("language", "en") + """';
    recognition.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = true;
    
    btn.style.animation = 'pulse 1s infinite';
    btn.textContent = '⏸️';
    status.textContent = '🎤 Listening... Speak now';
    status.style.color = '#6366f1';
    
    recognition.onresult = function(event) {
        var transcript = '';
        for (var i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        result.style.display = 'block';
        result.textContent = '📝 ' + transcript;
        voiceText = transcript;
    };
    
    recognition.onend = function() {
        btn.style.animation = '';
        btn.textContent = '🎤';
        if (voiceText) {
            status.textContent = '✅ Voice captured!';
            status.style.color = '#16a34a';
            try {
                var doc = window.parent.document;
                var ta = doc.querySelector('textarea[data-testid="stTextArea"]');
                if (ta) {
                    ta.value = voiceText;
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                    ta.dispatchEvent(new Event('change', { bubbles: true }));
                }
            } catch (e) {}
            // Keep captured voice in the input only; avoid full page reload
            // because reload can reset Streamlit session and force login.
        } else {
            status.textContent = '❌ No speech detected. Try again.';
            status.style.color = '#dc2626';
        }
    };
    
    recognition.onerror = function(e) {
        btn.style.animation = '';
        btn.textContent = '🎤';
        status.textContent = '❌ Error: ' + e.error;
        status.style.color = '#dc2626';
    };
    
    recognition.start();
}
</script>
<style>
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(236,72,153,0.6); }
    70% { box-shadow: 0 0 0 20px rgba(236,72,153,0); }
    100% { box-shadow: 0 0 0 0 rgba(236,72,153,0); }
}
</style>
"""

LOCATION_HTML = """
<div style="text-align:center;padding:10px;">
<button onclick="getLocation()" id="locBtn" style="
    background: linear-gradient(135deg, #06b6d4, #6366f1);
    color: white; border: none; border-radius: 14px;
    padding: 12px 24px; font-size: 0.9rem; font-weight: 700;
    cursor: pointer; box-shadow: 0 4px 15px rgba(6,182,212,0.4);
    font-family: sans-serif;
">📍 Get My Location</button>
<div id="locStatus" style="margin-top:8px;font-size:0.82rem;color:#666;font-family:sans-serif;"></div>
</div>
<script>
function getLocation() {
    var btn = document.getElementById('locBtn');
    var status = document.getElementById('locStatus');
    status.textContent = '⏳ Fetching location...';
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(pos) {
            var lat = pos.coords.latitude.toFixed(5);
            var lon = pos.coords.longitude.toFixed(5);
            status.textContent = '✅ Location: ' + lat + ', ' + lon;
            status.style.color = '#16a34a';
            fetch('https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=' + pos.coords.latitude + '&lon=' + pos.coords.longitude)
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    var a = d.address || {};
                    var pretty = [
                        a.suburb || a.neighbourhood || a.village || a.hamlet || '',
                        a.city || a.town || a.county || '',
                        a.state || ''
                    ].filter(Boolean).join(', ');
                    if (!pretty) pretty = d.display_name || 'Current location';

                    // Show location to user without hard reload.
                    status.textContent = '✅ Location: ' + pretty;
                    status.style.color = '#16a34a';
                })
                .catch(function() {
                    status.textContent = '✅ Coordinates captured successfully.';
                    status.style.color = '#16a34a';
                });
        }, function(err) {
            status.textContent = '❌ Could not fetch location. Please allow permission.';
            status.style.color = '#dc2626';
        });
    } else {
        status.textContent = '❌ Geolocation not supported.';
    }
}

// Do not auto-capture on load; auto reload loops can break login session.
</script>
"""

def show_file_complaint():
    lang = st.session_state.get("language", "en")
    user = st.session_state.get("user", {})
    user_id = user.get("user_id")

    if st.button(f"↩️ {t('back')}", key="back_fc"):
        st.session_state.screen = "user_dashboard"
        st.rerun()

    st.markdown(f"""
    <div class="hero">
        <h1>📢 {t('file_complaint')} · TEST BUILD 19:11</h1>
        <p>{'अपनी समस्या हमें बताएं' if lang=='hi' else 'Tell us about your issue'}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card" style="border-left:4px solid #16a34a;">
            <div style="font-weight:800;">Complaint Voice/Location Sync: ACTIVE</div>
            <div style="font-size:0.82rem;opacity:0.85;margin-top:4px;">
                Build marker: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Read JS-pushed query params (voice + location) and sync session state
    qp = st.query_params
    q_voice = _qp_first(qp.get("voice_text"))
    q_lat = _qp_first(qp.get("loc_lat"))
    q_lon = _qp_first(qp.get("loc_lon"))
    q_loc_text = _qp_first(qp.get("loc_text"))

    if q_voice:
        st.session_state.voice_captured = q_voice
        st.success("Voice captured.")
        try:
            del qp["voice_text"]
        except Exception:
            pass

    if q_lat and q_lon:
        try:
            lat = float(q_lat)
            lon = float(q_lon)
            st.session_state.loc_lat = lat
            st.session_state.loc_lon = lon
            human_loc = q_loc_text or _reverse_geocode(lat, lon)
            st.session_state.location_text = human_loc or "Current location detected"
            st.session_state.complaint_loc = st.session_state.location_text
            st.success(f"Location updated: {st.session_state.location_text}")
            try:
                del qp["loc_lat"]
                del qp["loc_lon"]
                if "loc_text" in qp:
                    del qp["loc_text"]
            except Exception:
                pass
        except Exception:
            pass

    # Keep location helper synced; voice text is intentionally separate
    if st.session_state.get("location_text") and not st.session_state.get("complaint_loc"):
        st.session_state.complaint_loc = st.session_state.location_text

    # Category
    cats = t("categories")
    cat_keys = list(cats.keys())
    cat_labels = [cats[k] for k in cat_keys]
    
    st.markdown(f"**{t('category')}**")
    cat_cols = st.columns(4)
    selected_cat = st.session_state.get("selected_category", "other")
    for i, (key, label) in enumerate(zip(cat_keys, cat_labels)):
        with cat_cols[i % 4]:
            if st.button(label, key=f"cat_{key}", use_container_width=True):
                st.session_state.selected_category = key
                st.rerun()
    
    selected_cat = st.session_state.get("selected_category", "other")
    st.info(f"Selected: {cats.get(selected_cat, 'Other')}")

    st.markdown(f"**{'Voice and Location Controls' if lang == 'en' else 'आवाज और लोकेशन कंट्रोल'}**")
    vc1, vc2 = st.columns([2, 1])
    with vc1:
        st.components.v1.html(VOICE_HTML, height=200)
        voice_desc = st.text_input(
            "Voice captured text",
            key="voice_captured",
            placeholder="Speak and this text will be copied below automatically...",
            label_visibility="collapsed",
        )
    with vc2:
        st.components.v1.html(LOCATION_HTML, height=90)

    st.markdown(f"**{t('description')}**")
    description = st.text_area(
        "Complaint description",
        placeholder="Describe your issue in detail..." if lang=="en" else "अपनी समस्या विस्तार से बताएं...",
        key="complaint_desc",
        height=140,
        label_visibility="collapsed",
    )
    
    # Location
    st.markdown(f"**📍 {t('location')}**")
    location_text = st.text_input(
        "Complaint location",
        key="complaint_loc", 
        placeholder="Your location or area name...",
        label_visibility="collapsed",
    )

    # Auto-fill location from JS (simulate)
    if "location_text" not in st.session_state:
        st.session_state.location_text = ""

    # Show map preview
    lat = st.session_state.get("loc_lat", 23.2599)
    lon = st.session_state.get("loc_lon", 77.4126)
    
    if location_text or st.session_state.get("loc_lat"):
        map_html = f"""
        <div style="border-radius:16px;overflow:hidden;border:2px solid #e0e0ff;margin:8px 0;">
        <iframe width="100%" height="220" frameborder="0" scrolling="no" marginheight="0" marginwidth="0"
        src="https://www.openstreetmap.org/export/embed.html?bbox={lon-0.05}%2C{lat-0.05}%2C{lon+0.05}%2C{lat+0.05}&layer=mapnik&marker={lat}%2C{lon}"
        style="border:0;"></iframe>
        </div>
        """
        st.components.v1.html(map_html, height=240)

    # AI Preview
    final_description = description
    final_location = location_text or st.session_state.get("location_text", "Bhopal, MP")
    
    if final_description:
        # AI classification preview
        desc_lower = final_description.lower()
        ai_cats = {"water": ["water","pipe","leak","supply","पानी","नल"], "electricity": ["electricity","power","light","बिजली"],
                   "road": ["road","pothole","street","सड़क","गड्ढा"], "waste": ["garbage","waste","कचरा","गंदगी"],
                   "drainage": ["drain","sewer","नाला","सीवर"], "health": ["hospital","health","अस्पताल"]}
        detected = selected_cat
        if not detected or detected == "other":
            for cat, kws in ai_cats.items():
                if any(kw in desc_lower for kw in kws):
                    detected = cat
                    break
        
        priority = "medium"
        if any(kw in desc_lower for kw in ["urgent","emergency","danger","अत्यावश्यक","खतरा","तुरंत"]):
            priority = "high"
        elif any(kw in desc_lower for kw in ["minor","small","छोटा"]):
            priority = "low"
        
        pclass = {"high": "badge-high", "medium": "badge-medium", "low": "badge-low"}[priority]
        st.markdown(f"""
        <div class="card" style="border-left:4px solid #6366f1;">
            <div style="font-size:0.8rem;font-weight:700;color:#6366f1;margin-bottom:8px;">🤖 AI Analysis Preview</div>
            <div style="display:flex;gap:10px;flex-wrap:wrap;">
                <span>📂 Category: <strong>{detected.title()}</strong></span>
                <span class="{pclass}">⚡ Priority: {priority.title()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Submit
    st.markdown("---")
    if st.button(f"🚀 {t('submit')}", use_container_width=True):
        final_description = description
        if not final_description:
            st.error("Please describe your complaint." if lang == "en" else "शिकायत का विवरण दें।")
        elif not user_id:
            st.error("Please login first.")
        else:
            try:
                resp = requests.post(f"{API_BASE}/complaints/create", json={
                    "user_id": user_id,
                    "category": st.session_state.get("selected_category", "other"),
                    "description": final_description,
                    "location": final_location or "Bhopal, MP",
                    "latitude": st.session_state.get("loc_lat", 23.2599),
                    "longitude": st.session_state.get("loc_lon", 77.4126),
                })
                data = resp.json()
                if data.get("success"):
                    st.balloons()
                    comp_id = data.get("complaint_id")
                    ai_cat = data.get("ai_category", "")
                    priority = data.get("priority", "")
                    dept = data.get("department", "")
                    
                    st.markdown(f"""
                    <div class="card" style="border:2px solid #16a34a;border-radius:20px;text-align:center;padding:30px;">
                        <div style="font-size:3rem;">✅</div>
                        <div style="font-size:1.2rem;font-weight:800;color:#16a34a;margin:10px 0;">{t('complaint_filed')}</div>
                        <div style="font-size:1.3rem;font-weight:800;color:#6366f1;letter-spacing:2px;">#{comp_id}</div>
                        <div style="margin-top:12px;font-size:0.85rem;opacity:0.7;">
                            📂 {ai_cat.title()} · ⚡ {priority.title()} · 🏢 {dept}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # TTS confirmation
                    confirm_msg = f"Your complaint {comp_id} has been filed successfully." if lang == "en" else f"आपकी शिकायत {comp_id} सफलतापूर्वक दर्ज हो गई है।"
                    st.components.v1.html(f"""
                    <script>
                    var msg = new SpeechSynthesisUtterance("{confirm_msg}");
                    msg.lang = '{"hi-IN" if lang=="hi" else "en-IN"}';
                    window.speechSynthesis.speak(msg);
                    </script>
                    """, height=0)
                    
                    # Clear form
                    if "selected_category" in st.session_state:
                        del st.session_state.selected_category
                else:
                    st.error(data.get("detail", "Error filing complaint"))
            except Exception as e:
                st.error(f"Server error: {e}")
