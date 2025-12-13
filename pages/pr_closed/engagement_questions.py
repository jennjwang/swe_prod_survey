"""
Post-PR engagement questions page.
Asks about engagement with reviewer's comments.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import record_audio
from survey_data import save_pr_closed_responses


# Engagement rating questions (5-point Likert scale)
ENGAGEMENT_QUESTIONS = {
    'impact': "The feedback I received helped me improve my PR.",
    'clarity': "The review comments were clear and easy to act on.",
    'coverage': "The review identified the most important issues in my PR."
}

LIKERT_5_OPTIONS = ["Not selected", "1 - Strongly disagree", "2 - Disagree", "3 - Neutral", "4 - Agree", "5 - Strongly agree"]


def engagement_questions_page():
    """Ask about engagement with reviewer's comments."""
    page_header(
        "Reviewer Engagement",
        "Tell us about how you responded to the feedback you received during the PR review."
    )

    # Get selected issue from session state
    selected_issue = st.session_state.get('pr_closed_selected_issue')
    if not selected_issue:
        st.error("No issue selected. Please return to the previous page.")
        if st.button("Back"):
            st.session_state['page'] = 18
            st.rerun()
        return

    pr_url = selected_issue.get('pr_url', 'Unknown')
    st.info(f"**Pull Request:** [{pr_url}]({pr_url})")
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Load previous responses
    previous_responses = st.session_state.get('pr_closed_engagement', {})

    # Question 1: Engagement description (audio or text)
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-bottom: 1.5rem;'>
        During the code review, how did you engage with the reviewer's comments?
        </p>
        """, unsafe_allow_html=True)

    # Create tabs for audio and text input
    tab1, tab2 = st.tabs(["🎤 Record Audio", "⌨️ Type Response"])

    with tab1:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Click the microphone button below to record your response. Your audio will be transcribed automatically.
            </p>
            """, unsafe_allow_html=True)
        transcript = record_audio("engagement_description", min_duration=10, max_duration=600)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response = st.text_area(
            "Your response:",
            key="engagement_description_text",
            value=previous_responses.get('engagement_description', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript:
        engagement_description = transcript
    elif text_response and text_response.strip():
        engagement_description = text_response
    else:
        engagement_description = previous_responses.get('engagement_description', '')

    st.divider()

    # Question 2: Engagement statements (5-point Likert scale)
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-bottom: 1rem;'>
        Refer back to your recent PR review. For each of the following statements,
        rate how much you agree or disagree.
        </p>
        """, unsafe_allow_html=True)

    engagement_ratings = {}
    for key, question in ENGAGEMENT_QUESTIONS.items():
        engagement_ratings[key] = slider_question(
            question,
            LIKERT_5_OPTIONS,
            f"engage_{key}",
            previous_responses.get(key, "Not selected")
        )

    # Combine all responses
    all_responses = {
        'engagement_description': engagement_description,
        **engagement_ratings
    }

    # Validation function
    def validate():
        # Check engagement description
        if not engagement_description or not engagement_description.strip():
            st.warning('Please describe how you engaged with the reviewer\'s comments.')
            print('engagement description is empty')
            return False
        # Check all rating questions
        unanswered = []
        for key, v in engagement_ratings.items():
            print(f'engagement rating for {key} is {v}')
            if v == "Not selected":
                unanswered.append(key)

        if unanswered:
            st.warning(f'Please answer all engagement rating questions. Missing: {", ".join(unanswered)}')
            print(f'engagement ratings missing: {unanswered}')
            return False

        return True

    # Navigation handlers
    def handle_back():
        # Save to session state
        st.session_state['pr_closed_engagement'] = all_responses
        st.session_state['page'] = 19  # Back to collaboration questions
        st.rerun()

    def handle_next():
        if not validate():
            return
        # Save to session state
        st.session_state['pr_closed_engagement'] = all_responses

        # Save engagement data to database (includes collaboration data from previous page)
        participant_id = st.session_state['survey_responses'].get('participant_id', '')
        issue_id = selected_issue.get('issue_id')

        if participant_id and issue_id:
            # Gather collaboration and engagement responses
            collaboration = st.session_state.get('pr_closed_collaboration', {})
            engagement = all_responses

            # Convert Likert scale responses to numeric values
            db_responses = {}

            # Collaboration questions (collab_1, collab_2, etc.)
            collab_keys = ['psych_safety', 'constructiveness', 'shared_ownership', 'problem_solving']
            for i, key in enumerate(collab_keys, start=1):
                value = collaboration.get(key)
                if value and value != "Not selected":
                    db_responses[f'collab_{i}'] = int(value.split()[0])

            db_responses['collaboration_description'] = collaboration.get('collaboration_description', '')
            db_responses['collaboration_factors'] = collaboration.get('collaboration_factors', '')

            # Engagement questions (engage_1, engage_2, etc.)
            engage_keys = ['impact', 'clarity', 'coverage']
            for i, key in enumerate(engage_keys, start=1):
                value = engagement.get(key)
                if value and value != "Not selected":
                    db_responses[f'engage_{i}'] = int(value.split()[0])

            db_responses['engagement_description'] = engagement.get('engagement_description', '')

            # Save to database
            with st.spinner('Saving your responses...'):
                result = save_pr_closed_responses(participant_id, int(issue_id), db_responses)

            if result['success']:
                print(f"Engagement responses saved for participant {participant_id}")
            else:
                st.error(f"⚠️ Error saving responses: {result['error']}")
                print(f"Failed to save engagement responses: {result['error']}")
                return

        st.session_state['page'] = 22  # Learning outcomes page (skip feedback quality)
        st.rerun()

    # Navigation buttons
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_next,
        back_key="engage_back",
        next_key="engage_next",
        next_label="Next",
        show_back=False,
        validation_fn=validate,
        validation_error="Please answer all questions before proceeding."
    )
