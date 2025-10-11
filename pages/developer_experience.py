"""
Developer experience page for the survey.
"""

import streamlit as st
from survey_components import page_header, selectbox_question, text_area_question, navigation_buttons
from survey_utils import save_and_navigate
from survey_questions import EXPERIENCE_OPTIONS


def developer_experience_page():
    """Display the developer experience page."""
    page_header(
        "Developer Experience",
        "Tell us about your background and experience."
    )
    
    # Load previous responses
    previous_experience = st.session_state['survey_responses'].get('professional_experience', None)
    previous_occupation = st.session_state['survey_responses'].get('occupation_description', '')
    
    # Professional experience question
    professional_experience = selectbox_question(
        "How many years of professional development experience do you have?",
        EXPERIENCE_OPTIONS,
        "professional_experience",
        previous_experience
    )
    
    st.divider()
    
    # Occupation description question
    occupation_description = text_area_question(
        "Please briefly describe your current occupation.",
        "occupation_description",
        previous_occupation,
        height=100,
        placeholder="1-2 sentences to describe your work."
    )
    
    # Validation function
    def validate():
        return professional_experience and occupation_description.strip()
    
    # Navigation
    navigation_buttons(
        on_back=lambda: save_and_navigate('back', 
                                          professional_experience=professional_experience,
                                          occupation_description=occupation_description),
        on_next=lambda: save_and_navigate('next',
                                          professional_experience=professional_experience,
                                          occupation_description=occupation_description),
        back_key="dev_exp_back",
        next_key="dev_exp_next",
        validation_fn=validate,
        validation_error="Please fill out all fields before proceeding."
    )

