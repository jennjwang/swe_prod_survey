"""
Main application file for the developer survey.
This is the modular version with separated concerns.
"""

import streamlit as st
import streamlit.components.v1 as components
from styles import SURVEY_STYLES
from pages import (
    consent_page,
    developer_experience_page,
    self_efficacy_page,
    work_satisfaction_page,
    ai_tools_page,
    repository_assignment_page,
    code_experience_page,
    completion_page
)


def initialize_session_state():
    """Initialize session state variables."""
    if 'page' not in st.session_state:
        st.session_state['page'] = 0
    
    if 'survey_responses' not in st.session_state:
        st.session_state['survey_responses'] = {}


def main():
    """Main application entry point."""
    st.set_page_config(page_title="Developer Survey", layout="centered")
    
    # Apply custom CSS styles
    st.markdown(SURVEY_STYLES, unsafe_allow_html=True)

    # All UI styling is centralized in styles.SURVEY_STYLES

    # No JS overrides to color; rely on theme and CSS
    
    # Initialize session state
    initialize_session_state()
    
    # Route to the appropriate page based on session state
    page_routes = {
        0: consent_page,
        1: developer_experience_page,
        2: self_efficacy_page,
        3: work_satisfaction_page,
        4: ai_tools_page,
        5: repository_assignment_page,
        6: code_experience_page,
        7: completion_page
    }
    
    current_page = st.session_state.get('page', 0)
    page_function = page_routes.get(current_page, consent_page)
    page_function()


if __name__ == "__main__":
    main()

