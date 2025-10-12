"""
Already completed page for participants who have already submitted PR survey responses.
"""

import streamlit as st
from survey_components import page_header


def already_completed_page():
    """Display page for participants who have already completed PR survey responses."""
    page_header(
        "Survey Already Completed",
        "You have already completed the PR survey responses."
    )
    
    st.markdown("""
        <div style='margin-top: 3rem;'>
            <p style='font-size:20px; margin-bottom: 2rem;'>
            Thank you for your participation!
            </p>
            <p style='font-size:18px; margin-bottom: 2rem;'>
            You have already submitted your PR survey responses for this study.
            </p>
            <p style='font-size:16px; margin-bottom: 3rem; color: #666;'>
            No further action is required from you at this time.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display completion details
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    pr_url = st.session_state['survey_responses'].get('pr_url', '')
    
    if participant_id:
        st.info(f"**Participant ID:** {participant_id}")
    
    if pr_url:
        st.info(f"**Pull Request:** [{pr_url}]({pr_url})")
    
    st.markdown("""
        <div style='margin-top: 3rem;'>
            <p style='font-size:16px; color: #666;'>
            If you have any questions or concerns, please contact the study administrator.
            </p>
        </div>
        """, unsafe_allow_html=True)
