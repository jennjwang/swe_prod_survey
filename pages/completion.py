"""
Completion page for the survey.
"""

import streamlit as st


def completion_page():
    """Display the survey completion page."""
    st.header("Thank You!")
    
    st.markdown("""
        <p style='font-size:20px'>
        Thank you for completing the survey! Your responses have been recorded.
        </p>
        """, unsafe_allow_html=True)
    
    st.success("✅ Survey completed successfully!")
    
    # Display assigned repository details
    participant_id = st.session_state['survey_responses'].get('participant_id', 'N/A')
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', 'N/A')
    forked_repo_url = st.session_state['survey_responses'].get('forked_repository_url', 'N/A')
    code_experience = st.session_state['survey_responses'].get('code_experience', 'N/A')
    
    st.markdown("---")
    st.markdown("""
        <p style='font-size:18px; font-weight: 600; margin-top: 2rem; margin-bottom: 1rem'>
        Your Assignment Details:
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <p style='font-size:18px'>
        <strong>Participant ID:</strong> {participant_id}<br>
        <strong>Assigned Repository:</strong> {assigned_repo}<br>
        <strong>Your Forked Repository:</strong> <a href="{forked_repo_url}" target="_blank">{forked_repo_url}</a><br>
        <strong>Code Experience:</strong> {code_experience}
        </p>
        """, unsafe_allow_html=True)
    
    st.info("📝 Please save these details for the next phase of the study. You will be working on your forked repository.")
    
    with st.expander("View all your responses"):
        st.json(st.session_state['survey_responses'])

