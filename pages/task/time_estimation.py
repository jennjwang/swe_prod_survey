"""
Time estimation page after issue assignment.
"""

import streamlit as st
from survey_components import page_header, navigation_buttons
from survey_utils import save_and_navigate
from survey_data import update_issue_time_estimate


# Time estimation options
TIME_ESTIMATION_OPTIONS = [
    "<30 minutes",
    "30–60 minutes",
    "1–2 hours",
    "2–4 hours",
    ">4 hours"
]


def time_estimation_page():
    """Display the time estimation question page."""
    page_header(
        "Time Estimation",
        "Before starting to work on this issue, please estimate how long you think it will take."
    )
    
    # Display assigned issue for context
    issue_url = st.session_state['survey_responses'].get('issue_url', '')
    if issue_url:
        st.info(f"**Your Assigned Issue:** [{issue_url}]({issue_url})")
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    # Load previous response if exists
    previous_estimation = st.session_state['survey_responses'].get('time_estimation', None)
    
    # Question
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom:1rem;'>
        Before starting to work on this issue, how long do you think it will take you to complete it?
        </p>
        """, unsafe_allow_html=True)
    
    # Set index based on previous response
    if previous_estimation and previous_estimation in TIME_ESTIMATION_OPTIONS:
        default_index = TIME_ESTIMATION_OPTIONS.index(previous_estimation)
    else:
        default_index = None
    
    time_estimation = st.selectbox(
        label="",
        options=TIME_ESTIMATION_OPTIONS,
        index=default_index,
        key="time_estimation_select"
    )
    
    # Navigation (no back button - can't change issue assignment)
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([4, 1, 1])
    with col3:
        next_clicked = st.button("Next", key="time_est_next")
    
    if next_clicked:
        if time_estimation:
            # Save to database FIRST (repo-issues table)
            issue_id = st.session_state['survey_responses'].get('issue_id')
            if issue_id:
                result = update_issue_time_estimate(issue_id, time_estimation)
                if result['success']:
                    print(f"✅ Time estimate saved to database for issue {issue_id}")
                else:
                    print(f"⚠️ Failed to save time estimate: {result['error']}")
                    # Don't block progression if database save fails
            
            # Then save to session state and navigate (this triggers page rerun)
            save_and_navigate('next', time_estimation=time_estimation)
        else:
            st.error("Please select your time estimation to proceed.")

