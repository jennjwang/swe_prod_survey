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
    developer_experience_page,
    self_efficacy_page,
    work_satisfaction_page,
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
    code_quality_page,
    post_issue_questions_page,

    # Post-Exp1 pages
    ai_usage_page,
    tool_preference_page,
    post_self_efficacy_page,

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
    # Organized by survey sections: Pre-study (0-8), Task (9-11), Post-PR (12-14), Post-Exp1 (15-17), Completion (18-19)
    page_routes = {
        # Pre-study section
        # 0: consent_page,                    # Consent form
        0: participant_id_page,              # (Consent temporarily disabled) Start at Participant ID
        1: participant_id_page,              # Participant ID entry
        2: developer_experience_page,        # Professional experience
        3: self_efficacy_page,               # Self-efficacy questions
        4: work_satisfaction_page,           # Work satisfaction questions
        5: ai_tools_page,                    # AI tools experience
        6: repository_assignment_page,       # Repository assignment
        7: code_experience_page,             # Code experience questions
        8: pre_study_complete_page,          # Pre-study completion

        # Task section
        9: issue_assignment_page,            # Issue assignment
        10: time_estimation_page,             # Time estimation
        11: issue_completion_page,            # Issue completion & PR submission

        # Post-PR section
        12: ai_condition_questions_page,     # AI condition questions (AI users only)
        13: code_quality_page,               # Code quality assessment (all users)
        14: post_issue_questions_page,       # Post-issue experience questions (all users) + interview audio

        # Post-Exp1 section
        15: ai_usage_page,                   # AI usage (AI perception + interview questions)
        16: tool_preference_page,            # Tool use preference (AttrakDiff + tool switching)
        17: post_self_efficacy_page,         # Post-task self-efficacy

        # Completion section
        18: completion_page,                  # Single issue completion
        19: thank_you_page                    # Final thank you (all issues complete)
    }
    
    current_page = st.session_state.get('page', 0)
    page_function = page_routes.get(current_page, participant_id_page)
    page_function()


if __name__ == "__main__":
    main()

