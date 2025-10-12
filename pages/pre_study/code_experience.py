"""
Code experience page for the survey.
"""

import streamlit as st
from survey_components import page_header, selectbox_question, slider_question, navigation_buttons
from survey_utils import save_and_navigate
from survey_questions import CODE_EXPERIENCE_OPTIONS
from survey_data import save_survey_responses

# Code quality questions with 5-point scale
CODE_QUALITY_QUESTIONS = {
    'readability': "This code is easy to read (readability)",
    'analyzability': "This code's logic and structure are easy to understand (analyzability)",
    'modifiability': "This code would be easy to modify or extend (modifiability)",
    'testability': "This code would be easy to test (testability)",
    'stability': "This code would be stable when changes are made. (stability)",
    'correctness': "This code performs as intended. (correctness)",
    'compliance': "This code follows the repository's established standards and practices. (compliance)"
}

CODE_QUALITY_OPTIONS = ["Not selected", "1 - Strongly disagree", "2", "3", "4", "5 - Strongly agree"]


def code_experience_page():
    """Display the code experience question page."""
    page_header(
        "Codebase Familiarity",
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
    
    st.divider()
    
    # Code Quality Section
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-top: 2rem; margin-bottom: 1rem;'>
        Rate the following statements about the code you wrote:
        </p>
        <p style='font-size:16px; margin-bottom: 1.5rem; color: #666;'>
        (1 = Strongly disagree, 5 = Strongly agree)
        </p>
        """, unsafe_allow_html=True)
    
    # Load previous code quality responses
    previous_code_quality = st.session_state['survey_responses'].get('code_quality', {})
    
    code_quality_responses = {}
    for key, statement in CODE_QUALITY_QUESTIONS.items():
        code_quality_responses[key] = slider_question(
            statement,
            CODE_QUALITY_OPTIONS,
            f"code_quality_{key}",
            previous_code_quality.get(key, "Not selected")
        )
    
    # Validation function
    def validate():
        return (code_experience is not None and 
                all(v != "Not selected" for v in code_quality_responses.values()))
    
    # Custom navigation handlers to save to database
    def handle_back():
        # Save to session state
        st.session_state['survey_responses']['code_experience'] = code_experience
        st.session_state['survey_responses']['code_quality'] = code_quality_responses
        st.session_state['page'] -= 1
        st.rerun()
    
    def handle_next():
        if not validate():
            return
        
        # Save to session state
        st.session_state['survey_responses']['code_experience'] = code_experience
        st.session_state['survey_responses']['code_quality'] = code_quality_responses
        
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
