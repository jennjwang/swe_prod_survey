"""
Post-PR learning outcomes questions page.
Asks about learning from code review feedback.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import record_audio
from survey_data import save_pr_closed_responses


# Learning outcome questions (5-point Likert scale)
LEARNING_QUESTIONS = {
    'codebase_understanding': "The feedback I received helped me understand the codebase more deeply.",
    'team_conventions': "The feedback I received helped me understand my team's coding standards and conventions.",
    'code_quality': "The feedback I received helped me learn to write higher-quality code.",
    'professional_growth': "The feedback I received contributed to my growth as a developer."
}

LIKERT_5_OPTIONS = ["Not selected", "1 - Strongly disagree", "2 - Disagree", "3 - Neutral", "4 - Agree", "5 - Strongly agree"]


def learning_outcomes_questions_page():
    """Ask about learning outcomes from code review."""
    page_header(
        "Learning Outcomes",
        "Describe the ways in which the review process supported your learning."
    )

    # Get selected issue from session state
    selected_issue = st.session_state.get('pr_closed_selected_issue')
    if not selected_issue:
        st.error("⚠️ No issue selected. Please return to the previous page.")
        if st.button("Back"):
            st.session_state['page'] = 18
            st.rerun()
        return

    pr_url = selected_issue.get('pr_url', 'Unknown')
    issue_id = selected_issue.get('issue_id')
    st.info(f"**Pull Request:** [{pr_url}]({pr_url})")
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Load previous responses
    previous_responses = st.session_state.get('pr_closed_learning', {})

    # Question 1: Learning outcome ratings (5-point Likert scale)
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-bottom: 1rem;'>
        For each of the following statements, rate how much you agree or disagree.
        </p>
        """, unsafe_allow_html=True)

    learning_ratings = {}
    for key, question in LEARNING_QUESTIONS.items():
        learning_ratings[key] = slider_question(
            question,
            LIKERT_5_OPTIONS,
            f"learn_{key}",
            previous_responses.get(key, "Not selected")
        )

    st.divider()

    # Question 2: Specific learning examples (audio or text)
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-bottom: 1.5rem;'>
        If you agreed with any of the statements above, please describe specific examples of what you learned through the code review process.</p>
        """, unsafe_allow_html=True)

    # Create tabs for audio and text input
    tab1, tab2 = st.tabs(["🎤 Record Audio", "⌨️ Type Response"])

    with tab1:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Click the microphone button below to record your response. Your audio will be transcribed automatically.
            </p>
            """, unsafe_allow_html=True)
        transcript = record_audio("learning_examples", min_duration=10, max_duration=600)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response = st.text_area(
            "Your response:",
            key="learning_examples_text",
            value=previous_responses.get('learning_examples', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript:
        learning_examples = transcript
    elif text_response and text_response.strip():
        learning_examples = text_response
    else:
        learning_examples = previous_responses.get('learning_examples', '')

    # Combine all responses
    all_responses = {
        **learning_ratings,
        'learning_examples': learning_examples
    }

    # Validation function
    def validate():
        # Check all rating questions
        unanswered_ratings = []
        for key, v in learning_ratings.items():
            if v == "Not selected":
                unanswered_ratings.append(key)

        # Check learning examples
        has_learning_examples = learning_examples and learning_examples.strip()

        # Debug output
        if unanswered_ratings:
            st.warning(f"⚠️ Please answer all rating questions. Missing: {', '.join(unanswered_ratings)}")
            return False

        if not has_learning_examples:
            st.warning("⚠️ Please provide specific examples of what you learned (either by recording audio or typing a response).")
            return False

        return True

    # Custom save function for database
    def save_to_database():
        """Convert and save all PR-closed responses to database."""
        participant_id = st.session_state['survey_responses'].get('participant_id', '')

        if not (participant_id and issue_id):
            return {'success': False, 'error': 'Missing participant ID or issue ID'}

        # Gather all responses from session state
        collaboration = st.session_state.get('pr_closed_collaboration', {})
        engagement = st.session_state.get('pr_closed_engagement', {})
        learning = all_responses

        # Convert Likert scale responses to numeric values (extract number from "1 - Strongly disagree" format)
        db_responses = {}

        # Collaboration questions (collab_1, collab_2, etc.)
        collab_keys = ['psych_safety', 'constructiveness', 'shared_ownership', 'problem_solving']
        for i, key in enumerate(collab_keys, start=1):
            value = collaboration.get(key)
            if value and value != "Not selected":
                db_responses[f'collab_{i}'] = int(value.split()[0])

        db_responses['collaboration_description'] = collaboration.get('collaboration_description', '')

        # Collaboration factors question (now part of collaboration page)
        db_responses['collaboration_factors'] = collaboration.get('collaboration_factors', '')

        # Engagement questions (engage_1, engage_2, etc.)
        engage_keys = ['impact', 'clarity', 'coverage']
        for i, key in enumerate(engage_keys, start=1):
            value = engagement.get(key)
            if value and value != "Not selected":
                db_responses[f'engage_{i}'] = int(value.split()[0])

        db_responses['engagement_description'] = engagement.get('engagement_description', '')

        # Learning questions (learn_1, learn_2, etc.)
        learn_keys = ['codebase_understanding', 'team_conventions', 'code_quality', 'professional_growth']
        for i, key in enumerate(learn_keys, start=1):
            value = learning.get(key)
            if value and value != "Not selected":
                db_responses[f'learn_{i}'] = int(value.split()[0])

        db_responses['learning_examples'] = learning.get('learning_examples', '')

        # Save to database
        result = save_pr_closed_responses(participant_id, int(issue_id), db_responses)
        return result

    # Navigation handlers
    def handle_back():
        # Save to session state
        st.session_state['pr_closed_learning'] = all_responses
        st.session_state['page'] = 20  # Back to engagement questions page
        st.rerun()

    def handle_next():
        if not validate():
            return

        # Save to session state
        st.session_state['pr_closed_learning'] = all_responses

        # Save all responses to database
        with st.spinner('Saving your responses...'):
            result = save_to_database()

        if result['success']:
            participant_id = st.session_state['survey_responses'].get('participant_id', '')
            print(f"✅ PR-closed responses saved for participant {participant_id}")

            # Clear session state for pr_closed responses
            st.session_state.pop('pr_closed_selected_issue', None)
            st.session_state.pop('pr_closed_collaboration', None)
            st.session_state.pop('pr_closed_engagement', None)
            st.session_state.pop('pr_closed_feedback', None)
            st.session_state.pop('pr_closed_learning', None)

            # Show success message and redirect to PR closed thank you page
            st.success("✅ Thank you! Your responses have been saved successfully.")
            st.session_state['page'] = 23  # Redirect to PR closed thank you page
            st.rerun()
        else:
            st.error(f"⚠️ Error saving responses: {result['error']}")
            print(f"Failed to save pr-closed responses: {result['error']}")

    # Navigation buttons
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_next,
        back_key="learn_back",
        next_key="learn_next",
        next_label="Submit",
        validation_fn=validate,
        validation_error="Please answer all questions before proceeding."
    )
