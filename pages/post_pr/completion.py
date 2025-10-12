"""
Unified completion page for the survey.
Handles both regular completion and already-completed scenarios.
"""

import streamlit as st
from survey_components import page_header


def completion_page():
    """Display the survey completion page."""
    # Check if this is a return visit (already completed)
    is_return_visit = st.session_state.get('completion_type') == 'already_completed'
    
    if is_return_visit:
        # Already completed scenario
        page_header(
            "Survey Completed",
            "You have already completed the PR survey responses."
        )
        
        st.markdown("""
            <div>
                <p style='font-size:16px; color: #666;'>
                No further action is required from you at this time.
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Fresh completion scenario
        st.header("Study Complete!")
        
        st.markdown("""
            <p style='font-size:20px; margin-bottom: 2rem;'>
            Thank you for completing the entire study process, including your assigned issue!
            </p>
            """, unsafe_allow_html=True)
        
        st.success("All steps completed successfully!")
    
    # Display participant details (common to both scenarios)
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', '')
    assigned_issue_url = st.session_state['survey_responses'].get('issue_url', '')
    pr_url = st.session_state['survey_responses'].get('pr_url', '')
    time_estimation = st.session_state['survey_responses'].get('time_estimation', '')
    
    # Debug: Print what's in session state
    print(f"DEBUG - Session state survey_responses keys: {st.session_state['survey_responses'].keys()}")
    print(f"DEBUG - pr_url value: '{pr_url}'")
    
    # Show key information
    st.markdown("---")
    st.markdown("""
        <p style='font-size:18px; font-weight: 600; margin-bottom: 1rem'>
        Your Assignment Details:
        </p>
        """, unsafe_allow_html=True)
    
    if participant_id:
        st.info(f"**Participant ID:** {participant_id}")
    
    if assigned_repo:
        st.info(f"**Assigned Repository:** {assigned_repo}")
    
    # if assigned_issue_url:
    #     st.info(f"**Assigned Issue:** [{assigned_issue_url}]({assigned_issue_url})")
    
    # if time_estimation:
    #     st.info(f"**Estimated Time:** {time_estimation}")
    
    if pr_url:
        st.info(f"**Pull Request:** [{pr_url}]({pr_url})")
    # Closing message
    st.markdown("---")
    st.markdown("""
        <div>
            <p style='font-size:16px; color: #666'>
            If you have any questions or concerns, please contact the study administrator.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Optional: View all responses (for debugging/transparency)
    with st.expander("View all your responses"):
        st.json(st.session_state['survey_responses'])


def already_completed_page():
    """Redirect to completion page with already_completed flag."""
    st.session_state['completion_type'] = 'already_completed'
    completion_page()
