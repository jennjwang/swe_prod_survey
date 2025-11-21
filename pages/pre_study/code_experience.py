"""
Code experience page for the survey.
"""

import streamlit as st
from survey_components import page_header, selectbox_question, navigation_buttons
from survey_utils import save_and_navigate
from survey_questions import CODE_EXPERIENCE_OPTIONS
from survey_data import save_survey_responses


def code_experience_page():
    """Display the code experience question page."""
    page_header(
        "Codebase Familiarity",
        "Tell us about your experience with the assigned repository."
    )
    
    # Get assigned repository info for context
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', 'N/A')
    repo_url = st.session_state['survey_responses'].get('repository_url', '')

    if assigned_repo != 'N/A':
        if repo_url:
            st.info(f"**Assigned Repository:** [{assigned_repo}]({repo_url})")
        else:
            st.info(f"**Assigned Repository:** {assigned_repo}")
        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Load previous response
    previous_code_exp = st.session_state['survey_responses'].get('code_experience', None)
    
    # Display question
    code_experience = selectbox_question(
        "How many lines of code, approximately, have you personally written or modified in this codebase?",
        CODE_EXPERIENCE_OPTIONS,
        "code_experience_select",
        previous_code_exp
    )
    
    # Validation function
    def validate():
        return code_experience is not None
    
    # Custom navigation handlers to save to database
    def handle_back():
        # Save to session state
        st.session_state['survey_responses']['code_experience'] = code_experience
        st.session_state['page'] -= 1
        st.rerun()
    
    def handle_next():
        if not validate():
            return
        
        # Save to session state
        st.session_state['survey_responses']['code_experience'] = code_experience
        
        # Save to database
        participant_id = st.session_state['survey_responses'].get('participant_id', '')
        if participant_id:
            result = save_survey_responses(participant_id, st.session_state['survey_responses'])
            if not result['success']:
                st.error(f"Error saving responses: {result['error']}")
                return
        
        # Navigate to next page
        st.session_state['page'] += 1
        st.rerun()
    
    # Navigation
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_next,
        back_key="code_exp_back",
        next_key="code_exp_next",
        validation_fn=validate,
        validation_error="Please complete all questions to proceed."
    )
