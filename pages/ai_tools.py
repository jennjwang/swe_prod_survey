"""
AI tools experience page for the survey.
"""

import streamlit as st
from survey_components import page_header, selectbox_question, navigation_buttons
from survey_utils import save_and_navigate
from survey_questions import AI_EXPERIENCE_QUESTIONS, AI_HOURS_OPTIONS


def ai_tools_page():
    """Display the AI tools experience page."""
    page_header(
        "AI Tool Experience",
        "Tell us about your experience with AI tools."
    )
    
    # Load previous responses
    previous_experience = st.session_state['survey_responses'].get('ai_experience', {})
    
    # Display all questions with dividers
    responses = {}
    for idx, (key, question) in enumerate(AI_EXPERIENCE_QUESTIONS.items()):
        responses[key] = selectbox_question(
            question,
            AI_HOURS_OPTIONS,
            f"ai_exp_{key}",
            previous_experience.get(key, None)
        )
        
        # Add divider between questions (but not after the last one)
        if idx < len(AI_EXPERIENCE_QUESTIONS) - 1:
            st.divider()
    
    # Validation function
    def validate():
        return all(v != "Not selected" for v in responses.values())
    
    # Navigation
    navigation_buttons(
        on_back=lambda: save_and_navigate('back', ai_experience=responses),
        on_next=lambda: save_and_navigate('next', ai_experience=responses),
        back_key="ai_tools_back",
        next_key="ai_tools_next",
        validation_fn=validate,
        validation_error="Please fill out all fields before proceeding."
    )

