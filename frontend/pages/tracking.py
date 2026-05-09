import streamlit as st
import requests
from frontend.config import API_BASE

def show_tracking():
    user = st.session_state.get("user", {})
    lang = st.session_state.get("language", "en")
    
    st.markdown("""
    <div class="hero">
        <h1>🔍 Track Complaint</h1>
        <p>Check status of your complaints</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search by ID
    st.markdown("### Search by Complaint ID")
    col1, col2 = st.columns([3, 1])
    with col1:
        complaint_id = st.text_input("", placeholder="Enter complaint ID (e.g., GR1A2B3C4D)", label_visibility="collapsed")
    with col2:
        search = st.button("🔍 Search", use_container_width=True)
    
    if search and complaint_id:
        try:
            response = requests.get(f"{API_BASE}/api/complaints/track/{complaint_id}")
            if response.status_code == 200:
                complaint = response.json()
                show_complaint_details(complaint, user)
            else:
                st.error("Complaint not found")
        except:
            st.error("Error fetching complaint")
    
    # User's complaints list
    st.markdown("---")
    st.markdown("### Your Complaints")
    
    try:
        response = requests.get(f"{API_BASE}/api/complaints/user/{user.get('user_id')}")
        if response.status_code == 200:
            complaints = response.json()
            
            if complaints:
                for complaint in complaints:
                    with st.expander(f"#{complaint.get('complaint_id')} - {complaint.get('title')} - {complaint.get('status', '').upper()}"):
                        show_complaint_details(complaint, user, compact=True)
            else:
                st.info("No complaints found")
    except:
        st.error("Could not load complaints")

def show_complaint_details(complaint, user, compact=False):
    status_colors = {
        "pending": "#D97706",
        "in_progress": "#2563EB",
        "resolved": "#059669",
        "rejected": "#DC2626"
    }
    status_color = status_colors.get(complaint.get("status", "pending"), "#666")
    
    st.markdown(f"""
    <div style="background: var(--card-bg); border-radius: 12px; padding: 16px; border-left: 4px solid {status_color};">
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div>
                <div style="font-weight: 700; font-size: 1.1rem;">{complaint.get('title', '')}</div>
                <div style="margin-top: 8px;">{complaint.get('description', '')}</div>
            </div>
            <div>
                <span class="badge badge-{complaint.get('status', '').replace('_', '-')}">{complaint.get('status', '').replace('_', ' ').title()}</span>
                <span class="badge badge-{complaint.get('priority', 'medium')}" style="margin-left: 8px;">{complaint.get('priority', '').upper()}</span>
            </div>
        </div>
        <div style="margin-top: 12px; font-size: 0.875rem; color: #666;">
            📍 {complaint.get('location', 'N/A')} | 🏢 {complaint.get('department', 'N/A')} | 🕐 {complaint.get('created_at', '')}
        </div>
    """, unsafe_allow_html=True)
    
    if not compact:
        # Show timeline
        timeline = complaint.get("timeline", [])
        if timeline:
            st.markdown("#### Timeline")
            for item in timeline:
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                        <div class="timeline-status">{item.get('status', '').replace('_', ' ').title()}</div>
                        <div>{item.get('note', '')}</div>
                        <div class="timeline-time">{item.get('time', '')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Show rating if resolved
        if complaint.get("status") == "resolved" and not complaint.get("rating"):
            st.markdown("#### Rate this Resolution")
            stars = st.select_slider(
                "Your rating",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: "⭐" * x,
                key=f"rating_{complaint.get('complaint_id')}"
            )
            comment = st.text_area("Feedback (optional)", key=f"comment_{complaint.get('complaint_id')}")
            
            if st.button("Submit Rating", key=f"submit_{complaint.get('complaint_id')}"):
                try:
                    rating_data = {
                        "user_id": user.get("user_id"),
                        "official_id": complaint.get("official_id") or 1,
                        "stars": stars,
                        "comment": comment
                    }
                    response = requests.post(
                        f"{API_BASE}/api/complaints/{complaint.get('complaint_id')}/rate",
                        json=rating_data
                    )
                    if response.status_code == 200:
                        st.success("Thank you for your feedback!")
                        st.rerun()
                except:
                    st.error("Could not submit rating")
        
        elif complaint.get("rating"):
            st.markdown(f"<div class='stars'>{'⭐' * complaint.get('rating')}</div>", unsafe_allow_html=True)
            if complaint.get("rating_comment"):
                st.caption(f"Comment: {complaint.get('rating_comment')}")
    
    st.markdown("</div>", unsafe_allow_html=True)