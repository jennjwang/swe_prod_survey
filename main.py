"""
Main Streamlit application for the developer productivity survey.
Organized into three main sections: Pre-study, Task, and Post-PR.
"""

import streamlit as st
import streamlit.components.v1 as components
from styles import SURVEY_STYLES
from pages import (
    # Pre-study pages
    consent_page,
    participant_id_page,
    ai_tools_page,
    repository_assignment_page,
    code_experience_page,
    pre_study_complete_page,

    # Task pages
    issue_assignment_page,
    time_estimation_page,
    issue_completion_page,

    # Post-PR pages
    ai_condition_questions_page,
    post_issue_questions_page,
    post_issue_reflection_page,

    # Post-Exp1 pages
    study_val_page,
    ai_usage_page,

    # Completion pages
    completion_page,
    thank_you_page
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
    # Organized by survey sections: Pre-study (0-6), Task (7-9), Post-PR (10-12), Post-Exp1 (13-14), Completion (15-16)
    page_routes = {
        # Pre-study section
        # 0: consent_page,                    # Consent form
        0: participant_id_page,              # (Consent temporarily disabled) Start at Participant ID
        1: participant_id_page,              # Participant ID entry
        # 2: developer_experience_page,      # Professional experience (REMOVED)
        3: ai_tools_page,                    # AI tools experience
        4: repository_assignment_page,       # Repository assignment
        5: code_experience_page,             # Code experience questions
        6: pre_study_complete_page,          # Pre-study completion

        # Task section
        7: issue_assignment_page,            # Issue assignment
        8: time_estimation_page,             # Time estimation
        9: issue_completion_page,            # Issue completion & PR submission

        # Post-PR section
        10: ai_condition_questions_page,     # AI condition questions (AI users only)
        11: post_issue_questions_page,       # Post-issue experience questions (all users) + interview audio
        12: post_issue_reflection_page,      # Post-issue reflection (satisfaction, confidence, difficulty)

        # Post-Exp1 section
        13: study_val_page,                  # Study validation (workflow comparison)
        14: ai_usage_page,                   # AI usage (AI perception + interview questions)

        # Completion section
        15: completion_page,                 # Single issue completion
        16: thank_you_page                   # Final thank you (all issues complete)
    }
    
    current_page = st.session_state.get('page', 0)
    page_function = page_routes.get(current_page, participant_id_page)
    page_function()


if __name__ == "__main__":
    main()

