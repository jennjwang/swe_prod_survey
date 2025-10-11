"""
Completion page for the survey.
"""

import streamlit as st


def completion_page():
    """Display the survey completion page."""
    st.header("🎉 Study Complete!")
    
    st.markdown("""
        <p style='font-size:20px'>
        Thank you for completing the entire study process, including your assigned issue!
        </p>
        """, unsafe_allow_html=True)
    
    st.success("✅ All steps completed successfully!")
    
    issue_completed = st.session_state['survey_responses'].get('issue_completed', False)
    if issue_completed:
        st.success("✅ Your issue completion has been recorded!")
    
    # Display assigned repository and issue details
    participant_id = st.session_state['survey_responses'].get('participant_id', 'N/A')
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', 'N/A')
    forked_repo_url = st.session_state['survey_responses'].get('forked_repository_url', 'N/A')
    code_experience = st.session_state['survey_responses'].get('code_experience', 'N/A')
    assigned_issue_url = st.session_state['survey_responses'].get('issue_url', 'N/A')
    time_estimation = st.session_state['survey_responses'].get('time_estimation', 'N/A')
    pr_url = st.session_state['survey_responses'].get('pr_url', None)
    
    st.markdown("---")
    st.markdown("""
        <p style='font-size:18px; font-weight: 600; margin-top: 2rem; margin-bottom: 1rem'>
        Your Assignment Details:
        </p>
        """, unsafe_allow_html=True)
    
    # Build the details HTML
    details_html = f"""
        <p style='font-size:18px'>
        <strong>Participant ID:</strong> {participant_id}<br>
        <strong>Assigned Repository:</strong> {assigned_repo}<br>
        <strong>Your Forked Repository:</strong> <a href="{forked_repo_url}" target="_blank">{forked_repo_url}</a><br>
        <strong>Assigned Issue:</strong> <a href="{assigned_issue_url}" target="_blank">{assigned_issue_url}</a><br>
        <strong>Estimated Time:</strong> {time_estimation}<br>
    """
    
    # Add PR URL if it exists
    if pr_url:
        details_html += f'<strong>Pull Request:</strong> <a href="{pr_url}" target="_blank">{pr_url}</a><br>'
    
    details_html += f"""
        <strong>Code Experience:</strong> {code_experience}
        </p>
    """
    
    st.markdown(details_html, unsafe_allow_html=True)
    
    st.info("📝 Your participation in this study is complete. Thank you for your valuable contribution!")
    
    with st.expander("View all your responses"):
        st.json(st.session_state['survey_responses'])

