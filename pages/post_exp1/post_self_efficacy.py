"""
Post-task self-efficacy assessment page.
Shows after post-experience questions to assess confidence after completing tasks.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import save_and_navigate
from survey_data import save_post_exp1_responses


# Post-task Self-Efficacy questions (1-5 scale)
POST_SELF_EFFICACY_QUESTIONS = {
    'comprehension': "I can understand and navigate unfamiliar parts of the codebase.",
    'design': "I can plan the steps needed to develop a program from its requirements.",
    'implementation': "I can write code that solves a specified problem.",
    'debugging': "I can identify and fix errors in a codebase.",
    'testing': "I can write tests to verify the correctness of a program.",
    'cooperation': "I can explain my design decisions clearly during code reviews."
}

POST_SELF_EFFICACY_OPTIONS = ["Not selected", "1 - Not confident at all", "2", "3", "4", "5 - Absolutely confident"]


def post_self_efficacy_page():
    """Display post-task self-efficacy assessment page."""
    page_header(
        "Self-Efficacy Assessment",
        "Please rate how confident you are that you can perform each of the following tasks effectively."
    )

    # st.markdown("""
    #     <p style='font-size:16px; margin-bottom: 1.5rem; color: #666;'>
    #     (1 = Not confident at all, 5 = Absolutely confident)
    #     </p>
    #     """, unsafe_allow_html=True)

    # Load previous responses from post_exp1 data (if returning to this page)
    previous_responses = st.session_state['survey_responses'].get('post_exp1', {})

    # Display all self-efficacy questions
    post_efficacy_responses = {}
    for key, statement in POST_SELF_EFFICACY_QUESTIONS.items():
        post_efficacy_responses[key] = slider_question(
            statement,
            POST_SELF_EFFICACY_OPTIONS,
            f"post_efficacy_{key}",
            previous_responses.get(key, "Not selected")
        )

    # Validation function
    def validate():
        return all(v != "Not selected" for v in post_efficacy_responses.values())

    # Custom navigation handlers to save to database
    def handle_back():
        # Save to session state in post_exp1 (to maintain combined data structure)
        if 'post_exp1' not in st.session_state['survey_responses']:
            st.session_state['survey_responses']['post_exp1'] = {}
        st.session_state['survey_responses']['post_exp1'].update(post_efficacy_responses)
        st.session_state['page'] -= 1
        st.rerun()

    def handle_next():
        if not validate():
            return

        # Extract numeric values from responses
        db_responses = {}
        for key, value in post_efficacy_responses.items():
            if isinstance(value, str) and value != "Not selected":
                # Extract numeric part from strings like "1 - Not confident at all" or "2"
                numeric_value = value.split(' - ')[0].strip()
                try:
                    db_responses[key] = int(numeric_value)
                except ValueError:
                    db_responses[key] = None
            else:
                db_responses[key] = value

        # Merge with existing post_exp1 data
        if 'post_exp1' not in st.session_state['survey_responses']:
            st.session_state['survey_responses']['post_exp1'] = {}
        st.session_state['survey_responses']['post_exp1'].update(post_efficacy_responses)

        # Save to database with numeric values (combines with other post_exp1 data)
        participant_id = st.session_state['survey_responses'].get('participant_id', '')
        if participant_id:
            # Merge numeric responses with existing post_exp1 data
            all_post_exp1_data = {**st.session_state['survey_responses']['post_exp1'], **db_responses}
            result = save_post_exp1_responses(participant_id, all_post_exp1_data)
            if not result['success']:
                st.error(f"Error saving responses: {result['error']}")
                return

        # Mark post-exp1 as completed
        st.session_state['post_exp1_completed'] = True

        # Navigate to thank you page
        st.session_state['page'] = 19  # Thank you page
        st.rerun()

    # Navigation
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_next,
        back_key="post_efficacy_back",
        next_key="post_efficacy_next",
        validation_fn=validate,
        validation_error="⚠️ Please fill out all fields before proceeding."
    )
