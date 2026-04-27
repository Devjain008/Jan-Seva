import streamlit as st
import requests
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from frontend.config import TRANSLATIONS, API_BASE, CHATBOT_RESPONSES

def t(key):
    lang = st.session_state.get("language", "en")
    tr = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return tr.get(key, key)

def get_bot_response(user_msg: str, lang: str) -> str:
    responses = CHATBOT_RESPONSES.get(lang, CHATBOT_RESPONSES["en"])
    msg = user_msg.lower()
    
    greet_words = ["hello", "hi", "hey", "namaste", "नमस्ते", "हैलो"]
    complaint_words = ["complaint", "file", "शिकायत", "दर्ज", "submit"]
    track_words = ["track", "status", "ट्रैक", "स्थिति", "where"]
    scheme_words = ["scheme", "yojana", "योजना", "plan", "benefit"]
    water_words = ["water", "pipe", "पानी", "नल"]
    electric_words = ["electricity", "light", "power", "बिजली"]
    road_words = ["road", "pothole", "सड़क", "गड्ढा"]
    
    if any(w in msg for w in greet_words):
        import random
        return random.choice(responses["greet"])
    elif any(w in msg for w in complaint_words):
        return responses["complaint"]
    elif any(w in msg for w in track_words):
        return responses["track"]
    elif any(w in msg for w in scheme_words):
        try:
            schemes = requests.get(f"{API_BASE}/schemes/all").json()
            if isinstance(schemes, list) and schemes:
                if lang == "hi":
                    return f"उपलब्ध योजनाएं:\n" + "\n".join([f"• {s.get('title_hi') or s.get('title','')} - {(s.get('description_hi') or s.get('description',''))[:80]}" for s in schemes[:3]])
                return "Available schemes:\n" + "\n".join([f"• {s.get('title','')} - {s.get('description','')[:80]}" for s in schemes[:3]])
        except: pass
        return responses["scheme"]
    elif any(w in msg for w in water_words):
        return responses["water"]
    elif any(w in msg for w in electric_words):
        return responses["electricity"]
    elif any(w in msg for w in road_words):
        return responses["road"]
    else:
        # Check for complaint ID query
        import re
        ids = re.findall(r'GR[A-Z0-9]{8}', user_msg.upper())
        if ids:
            try:
                resp = requests.get(f"{API_BASE}/complaints/track/{ids[0]}")
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status", "pending")
                    if lang == "hi":
                        return f"आपकी शिकायत #{ids[0]} की स्थिति: **{status.replace('_',' ').title()}**\n📍 {data.get('location','')}\n🏢 {data.get('department','')}"
                    return f"Complaint #{ids[0]} status: **{status.replace('_', ' ').title()}**\n📍 {data.get('location','')}\n🏢 {data.get('department','')}"
            except: pass
        return responses["default"]

VOICE_CHAT_HTML = """
<div style="display:flex;align-items:center;gap:10px;padding:8px 0;">
<button onclick="startChatVoice()" id="chatVoiceBtn" style="
    background: linear-gradient(135deg, #ec4899, #8b5cf6);
    color: white; border: none; border-radius: 50%;
    width: 48px; height: 48px; font-size: 1.3rem;
    cursor: pointer; flex-shrink: 0;
    box-shadow: 0 4px 15px rgba(236,72,153,0.4);
">🎤</button>
<div id="chatVoiceStatus" style="font-size:0.82rem;color:#888;font-family:sans-serif;"></div>
</div>
<script>
function startChatVoice() {
    var btn = document.getElementById('chatVoiceBtn');
    var status = document.getElementById('chatVoiceStatus');
    var lang = '""" + st.session_state.get("language","en") + """';
    
    if (!('webkitSpeechRecognition' in window)) {
        status.textContent = '❌ Use Chrome for voice';
        return;
    }
    var r = new webkitSpeechRecognition();
    r.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
    r.onstart = function() { btn.textContent = '⏸️'; status.textContent = '🎤 Listening...'; }
    r.onresult = function(e) {
        var text = e.results[0][0].transcript;
        status.textContent = '✅ ' + text;
        window.parent.postMessage({type: 'chat_voice', text: text}, '*');
    }
    r.onend = function() { btn.textContent = '🎤'; }
    r.start();
}
</script>
"""

def show_assistant():
    lang = st.session_state.get("language", "en")
    user = st.session_state.get("user", {})

    if st.button(f"↩️ {t('back')}", key="back_asst"):
        st.session_state.screen = "user_dashboard"
        st.rerun()

    # Init chat
    if "chat_history" not in st.session_state:
        greeting = "नमस्ते! मैं आपका AI सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं? 🙏" if lang == "hi" else "Hello! I'm your AI assistant. How can I help you today? 😊"
        st.session_state.chat_history = [{"role": "bot", "text": greeting, "time": datetime.now().strftime("%I:%M %p")}]

    # Chat header
    st.markdown(f"""
    <div class="chat-container">
        <div class="chat-header">
            <div style="font-size:1.8rem;">🤖</div>
            <div>
                <div>{'AI सहायक' if lang=='hi' else 'AI Assistant'}</div>
                <div style="font-size:0.75rem;opacity:0.85;">{'हमेशा उपलब्ध' if lang=='hi' else 'Always available'}</div>
            </div>
            <div style="margin-left:auto;font-size:0.75rem;background:rgba(255,255,255,0.2);padding:4px 10px;border-radius:20px;">🟢 Online</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat messages
    chat_html = '<div class="chat-messages" id="chatBox">'
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            chat_html += f'<div class="msg-user">{msg["text"]}<div class="msg-time">{msg["time"]}</div></div>'
        else:
            chat_html += f'<div class="msg-bot">🤖 {msg["text"]}<div class="msg-time">{msg["time"]}</div></div>'
    chat_html += '</div>'
    
    st.components.v1.html(f"""
    <style>
    .chat-messages {{ max-height: 380px; overflow-y: auto; padding: 16px; }}
    .msg-user {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border-radius: 18px 18px 4px 18px; padding: 10px 16px; margin: 6px 0 6px auto; font-size: 0.88rem; max-width: 85%; width: fit-content; }}
    .msg-bot {{ background: #f0f0ff; color: #1a1a2e; border-radius: 18px 18px 18px 4px; padding: 10px 16px; margin: 6px 0; font-size: 0.88rem; max-width: 85%; border: 1px solid #e0e0ff; white-space: pre-line; }}
    .msg-time {{ font-size: 0.68rem; opacity: 0.6; margin-top: 3px; }}
    #chatBox {{ scroll-behavior: smooth; }}
    </style>
    {chat_html}
    <script>
    var box = document.getElementById('chatBox');
    if(box) box.scrollTop = box.scrollHeight;
    </script>
    """, height=420)

    # Suggested questions
    if len(st.session_state.chat_history) <= 2:
        st.markdown("**Quick questions:**")
        suggestions = (
            ["शिकायत कैसे दर्ज करें?", "सरकारी योजनाएं", "शिकायत ट्रैक करें", "पानी की शिकायत"] if lang == "hi"
            else ["How to file a complaint?", "Government schemes", "Track my complaint", "Water issue"]
        )
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(s, key=f"sug_{i}", use_container_width=True):
                    bot_response = get_bot_response(s, lang)
                    now = datetime.now().strftime("%I:%M %p")
                    st.session_state.chat_history.append({"role": "user", "text": s, "time": now})
                    st.session_state.chat_history.append({"role": "bot", "text": bot_response, "time": now})
                    st.rerun()

    # Input
    st.markdown("---")
    col1, col2, col3 = st.columns([5, 1, 1])
    with col1:
        user_input = st.text_input("", placeholder=t("chat_placeholder"), key="chat_input", label_visibility="collapsed")
    with col2:
        send_btn = st.button(f"📤", key="chat_send", use_container_width=True)
    with col3:
        voice_btn = st.button("🎤", key="voice_chat_btn", use_container_width=True)

    if send_btn and user_input:
        bot_response = get_bot_response(user_input, lang)
        now = datetime.now().strftime("%I:%M %p")
        st.session_state.chat_history.append({"role": "user", "text": user_input, "time": now})
        st.session_state.chat_history.append({"role": "bot", "text": bot_response, "time": now})
        
        # Speak bot response
        st.components.v1.html(f"""
        <script>
        var msg = new SpeechSynthesisUtterance("{bot_response[:200]}");
        msg.lang = '{"hi-IN" if lang=="hi" else "en-IN"}';
        msg.rate = 0.9;
        window.speechSynthesis.speak(msg);
        </script>
        """, height=0)
        st.rerun()

    if voice_btn:
        st.components.v1.html(VOICE_CHAT_HTML, height=80)
    
    # Clear chat
    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()
