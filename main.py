"""
Main Streamlit application for the developer productivity survey.
Organized into three main sections: Pre-study, Task, and Post-PR.
"""

import streamlit as st
import streamlit.components.v1 as components
from styles import SURVEY_STYLES
from pages import (
    # Pre-study pages
    participant_id_page,
    ai_tools_page,
    repository_assignment_page,
    setup_checklist_page,
    code_experience_page,
    pre_study_complete_page,

    # Task pages
    issue_assignment_page,
    time_estimation_page,
    issue_completion_page,

    # Post-PR pages
    post_issue_questions_page,
    post_issue_reflection_page,

    # Post-Exp1 pages
    study_val_page,
    ai_usage_page,

    # Completion pages
    completion_page,
    thank_you_page,

    # PR closed pages
    update_issue_page,
    collaboration_questions_page,
    engagement_questions_page,
    learning_outcomes_questions_page,
    pr_closed_thank_you_page,

    # Post-Exp2 pages
    end_of_study_thank_you_page,
    code_activities_value_page,
    final_thank_you_page
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
    # Organized by survey sections: Pre-study (0-7), Task (8-10), Post-PR (11-13), Post-Exp1 (14-15), Completion (16-17)
    page_routes = {
        # Pre-study section
        # 0: consent_page,                    # Consent form
        0: participant_id_page,              # (Consent temporarily disabled) Start at Participant ID
        1: participant_id_page,              # Participant ID entry
        # 2: developer_experience_page,      # Professional experience (REMOVED)
        3: ai_tools_page,                    # AI tools experience
        4: repository_assignment_page,       # Repository assignment
        5: code_experience_page,             # Code experience questions
        6: setup_checklist_page,             # Setup checklist and reminders
        7: pre_study_complete_page,          # Pre-study completion

        # Task section
        8: issue_assignment_page,            # Issue assignment
        9: time_estimation_page,             # Time estimation
        10: issue_completion_page,           # Issue completion & PR submission

        # Post-PR section
        11: post_issue_questions_page,       # Alias to post-issue questions (AI page removed)
        12: post_issue_questions_page,       # Post-issue experience questions (all users) + interview audio
        13: post_issue_reflection_page,      # Post-issue reflection (satisfaction, confidence, difficulty)

        # Post-Exp1 section
        14: study_val_page,                  # Study validation (workflow comparison)
        15: ai_usage_page,                   # AI usage (AI perception + interview questions)

        # Completion section
        16: completion_page,                 # Single issue completion
        17: thank_you_page,                  # Final thank you (all issues complete)

        # PR closed section
        18: update_issue_page,               # Update previously closed issues
        19: collaboration_questions_page,    # Collaboration questions (includes collaboration factors)
        20: engagement_questions_page,       # Engagement questions
        22: learning_outcomes_questions_page,# Learning outcomes questions
        23: pr_closed_thank_you_page,        # PR closed thank you page

        # Post-Exp2 section
        25: end_of_study_thank_you_page,     # End of study questions (AI responsibility)
        24: code_activities_value_page,      # Code activities value rating
        26: final_thank_you_page             # Final thank you after all questions
    }
    
    current_page = st.session_state.get('page', 0)

    page_function = page_routes.get(current_page, participant_id_page)
    page_function()


if __name__ == "__main__":
    main()
