import streamlit as st
import requests
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from frontend.config import TRANSLATIONS, API_BASE

def t(key, lang=None):
    if lang is None:
        lang = st.session_state.get("language", "en")
    tr = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return tr.get(key, key)

def show_language_select():
    st.markdown("""
    <div class="welcome-screen">
        <div class="welcome-logo">🏛️</div>
        <div class="welcome-title">Jan Seva Portal<br>जन सेवा पोर्टल</div>
        <div class="welcome-sub">AI-Powered Citizen Grievance System<br>AI-संचालित नागरिक शिकायत प्रणाली</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🌐 Select Language / भाषा चुनें")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇬🇧 English", key="lang_en", use_container_width=True):
            st.session_state.language = "en"
            st.session_state.screen = "login_type"
            st.rerun()
    with col2:
        if st.button("🇮🇳 हिंदी", key="lang_hi", use_container_width=True):
            st.session_state.language = "hi"
            st.session_state.screen = "login_type"
            st.rerun()

    # Voice greeting
    st.components.v1.html("""
    <script>
    setTimeout(function() {
        var msg = new SpeechSynthesisUtterance("Welcome to Jan Seva Portal. Please select your language.");
        msg.lang = 'en-IN';
        msg.rate = 0.85;
        window.speechSynthesis.speak(msg);
    }, 500);
    </script>
    """, height=0)

def show_login_type():
    lang = st.session_state.get("language", "en")
    st.markdown(f"""
    <div class="hero">
        <h1>🏛️ {t('app_title')}</h1>
        <p>{t('app_subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### {t('login')}")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"👤 {t('user_login')}", use_container_width=True):
            st.session_state.screen = "user_login"
            st.rerun()
    with col2:
        if st.button(f"🏢 {t('official_login')}", use_container_width=True):
            st.session_state.screen = "official_login"
            st.rerun()
    with col3:
        if st.button(f"👑 {t('admin_login')}", use_container_width=True):
            st.session_state.screen = "admin_login"
            st.rerun()
    
    st.markdown("---")
    if st.button(f"↩️ {t('back')}", use_container_width=True):
        st.session_state.screen = "language"
        st.rerun()

def show_user_login():
    lang = st.session_state.get("language", "en")
    st.markdown(f"""
    <div class="card">
        <div class="section-header">👤 {t('user_login')}</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"🔑 {t('login')}", f"📝 {t('signup')}"])
    
    with tab1:
        st.markdown(f"**{t('phone')}**")
        phone = st.text_input("", placeholder="e.g. 9876543210", key="login_phone", label_visibility="collapsed")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"📲 {t('send_otp')}", use_container_width=True):
                if phone:
                    try:
                        resp = requests.post(f"{API_BASE}/auth/user/send-otp", json={"phone": phone})
                        data = resp.json()
                        if data.get("success"):
                            st.session_state.login_phone_val = phone
                            st.session_state.simulated_otp = data.get("otp")
                            st.session_state.otp_sent = True
                            st.success(f"✅ OTP sent! (Demo: {data.get('otp')})")
                        else:
                            st.error(data.get("detail", "Error"))
                    except Exception as e:
                        st.error(f"Server error: {e}")
                else:
                    st.warning(f"Enter {t('phone')}")

        if st.session_state.get("otp_sent"):
            st.markdown(f"**{t('otp')}**")
            otp = st.text_input("", placeholder="6-digit OTP", key="login_otp", label_visibility="collapsed")
            with col2:
                if st.button(f"✅ {t('verify_otp')}", use_container_width=True):
                    if otp:
                        try:
                            resp = requests.post(f"{API_BASE}/auth/user/verify-otp", json={
                                "phone": st.session_state.login_phone_val, "otp": otp
                            })
                            data = resp.json()
                            if data.get("success"):
                                st.session_state.user = data
                                st.session_state.role = "user"
                                st.session_state.screen = "user_dashboard"
                                st.session_state.otp_sent = False
                                st.rerun()
                            else:
                                st.error(data.get("detail", "Invalid OTP"))
                        except Exception as e:
                            st.error(f"Server error: {e}")
    
    with tab2:
        name = st.text_input(f"{t('name')}", key="su_name")
        phone_su = st.text_input(f"{t('phone')}", key="su_phone", placeholder="10-digit number")
        address = st.text_area(f"{t('address')}", key="su_address", height=80)
        
        if st.button(f"📝 {t('register')}", use_container_width=True):
            if name and phone_su and address:
                try:
                    resp = requests.post(f"{API_BASE}/auth/user/signup", json={
                        "name": name, "phone": phone_su, "address": address,
                        "language": lang
                    })
                    data = resp.json()
                    if data.get("success"):
                        st.success("✅ Registered! Now login with your phone number.")
                    else:
                        st.error(data.get("detail", "Error"))
                except Exception as e:
                    st.error(f"Server error: {e}")
            else:
                st.warning("Fill all fields")
    
    st.markdown("---")
    if st.button(f"↩️ {t('back')}", key="back_ul", use_container_width=True):
        st.session_state.screen = "login_type"
        st.rerun()

def show_official_login():
    lang = st.session_state.get("language", "en")
    st.markdown(f"""
    <div class="card">
        <div class="section-header">🏢 {t('official_login')}</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"🔑 {t('login')}", f"📝 {t('signup')}"])
    
    with tab1:
        email = st.text_input(f"{t('email')}", key="off_email")
        password = st.text_input(f"{t('password')}", type="password", key="off_pass")
        if st.button(f"🔑 {t('login')}", use_container_width=True):
            if email and password:
                try:
                    resp = requests.post(f"{API_BASE}/auth/official/login", json={"email": email, "password": password})
                    data = resp.json()
                    if data.get("success"):
                        st.session_state.official = data
                        st.session_state.role = "official"
                        st.session_state.screen = "official_dashboard"
                        st.rerun()
                    else:
                        st.error(data.get("detail", "Login failed"))
                except Exception as e:
                    st.error(f"Server error: {e}")
    
    with tab2:
        name = st.text_input(f"{t('name')}", key="off_name")
        email_su = st.text_input(f"{t('email')}", key="off_email_su")
        pass_su = st.text_input(f"{t('password')}", type="password", key="off_pass_su")
        dept_code = st.text_input(f"{t('dept_code')}", key="off_dept", placeholder="e.g. WAT-0001",
                                  help=t("dept_code_hint"))
        if st.button(f"📝 {t('register')}", key="off_register", use_container_width=True):
            if all([name, email_su, pass_su, dept_code]):
                try:
                    resp = requests.post(f"{API_BASE}/auth/official/signup", json={
                        "name": name, "email": email_su, "password": pass_su, "dept_code": dept_code
                    })
                    data = resp.json()
                    if data.get("success"):
                        st.success("✅ Registration submitted. Await admin approval.")
                    else:
                        st.error(data.get("detail", "Error"))
                except Exception as e:
                    st.error(f"Server error: {e}")
            else:
                st.warning("Fill all fields")
    
    st.markdown("---")
    if st.button(f"↩️ {t('back')}", key="back_ol", use_container_width=True):
        st.session_state.screen = "login_type"
        st.rerun()

def show_admin_login():
    st.markdown("""
    <div class="card">
        <div class="section-header">👑 Admin Login</div>
    </div>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Username", key="adm_user")
    password = st.text_input("Password", type="password", key="adm_pass")
    st.caption("Default: admin / admin123")
    
    if st.button("👑 Admin Login", use_container_width=True):
        if username and password:
            try:
                resp = requests.post(f"{API_BASE}/auth/admin/login", json={"username": username, "password": password})
                data = resp.json()
                if data.get("success"):
                    st.session_state.admin = data
                    st.session_state.role = "admin"
                    st.session_state.screen = "admin_panel"
                    st.rerun()
                else:
                    st.error(data.get("detail", "Login failed"))
            except Exception as e:
                st.error(f"Server error: {e}")
    
    st.markdown("---")
    if st.button(f"↩️ Back", key="back_adm", use_container_width=True):
        st.session_state.screen = "login_type"
        st.rerun()
