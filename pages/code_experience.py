"""
Code experience page for the survey.
"""

import streamlit as st
from survey_components import page_header, selectbox_question, navigation_buttons
from survey_utils import save_and_navigate
from survey_questions import CODE_EXPERIENCE_OPTIONS


def code_experience_page():
    """Display the code experience question page."""
    page_header(
        "Code Experience",
        "Tell us about your experience with the assigned repository."
    )
    
    # Get assigned repository info for context
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', 'N/A')
    if assigned_repo != 'N/A':
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
    
    # Navigation
    navigation_buttons(
        on_back=lambda: save_and_navigate('back', code_experience=code_experience),
        on_next=lambda: save_and_navigate('next', code_experience=code_experience),
        back_key="code_exp_back",
        next_key="code_exp_next",
        validation_fn=validate,
        validation_error="Please select your code experience level to proceed."
    )
