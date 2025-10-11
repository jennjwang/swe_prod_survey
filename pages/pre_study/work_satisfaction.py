"""
Work satisfaction page for the survey.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import save_and_navigate
from survey_questions import SATISFACTION_QUESTIONS, SATISFACTION_SLIDER_OPTIONS


def work_satisfaction_page():
    """Display the work satisfaction questions page."""
    page_header(
        "Work Satisfaction",
        "Rate how satisfied you are with the following aspects of your work as a developer."
    )
    
    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('satisfaction', {})
    
    # Display all questions
    responses = {}
    for key, question in SATISFACTION_QUESTIONS.items():
        responses[key] = slider_question(
            question,
            SATISFACTION_SLIDER_OPTIONS,
            f"satisfaction_{key}",
            previous_responses.get(key, "Not selected")
        )
    
    # Validation function
    def validate():
        return all(v != "Not selected" for v in responses.values())
    
    # Navigation
    navigation_buttons(
        on_back=lambda: save_and_navigate('back', satisfaction=responses),
        on_next=lambda: save_and_navigate('next', satisfaction=responses),
        back_key="satisfaction_back",
        next_key="satisfaction_next",
        validation_fn=validate,
        validation_error="Please fill out all fields before proceeding."
    )

