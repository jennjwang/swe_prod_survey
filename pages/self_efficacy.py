"""
Self-efficacy assessment page for the survey.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import save_and_navigate
from survey_questions import SELF_EFFICACY_QUESTIONS, SELF_EFFICACY_OPTIONS


def self_efficacy_page():
    """Display the self-efficacy assessment page."""
    page_header(
        "Self-Efficacy Assessment",
        "Please rate how confident you are that you can perform each of the following tasks effectively."
    )
    
    # Load previous responses
    previous_efficacy = st.session_state['survey_responses'].get('self_efficacy', {})
    
    # Display all questions
    responses = {}
    for key, question in SELF_EFFICACY_QUESTIONS.items():
        responses[key] = slider_question(
            question,
            SELF_EFFICACY_OPTIONS,
            f"efficacy_{key}",
            previous_efficacy.get(key, "Not selected")
        )
    
    # Validation function
    def validate():
        return all(v != "Not selected" for v in responses.values())
    
    # Navigation
    navigation_buttons(
        on_back=lambda: save_and_navigate('back', self_efficacy=responses),
        on_next=lambda: save_and_navigate('next', self_efficacy=responses),
        back_key="efficacy_back",
        next_key="efficacy_next",
        validation_fn=validate,
        validation_error="Please fill out all fields before proceeding."
    )

