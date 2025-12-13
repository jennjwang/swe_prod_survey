"""
Post-PR collaboration questions page.
Asks about collaboration during code review.
"""

import streamlit as st
from survey_components import page_header, question_label, slider_question, navigation_buttons
from survey_utils import record_audio
from survey_data import save_pr_closed_responses


# Collaboration rating questions (5-point Likert scale)
COLLABORATION_QUESTIONS = {
    'psych_safety': "I felt that my contributions were respected by the reviewer.",
    'constructiveness': "The reviewer engaged in discussions in a constructive way.",
    'shared_ownership': "I felt a shared sense of responsibility with the reviewer for improving the code during reviews.",
    'problem_solving': "The reviewer engaged in productive discussions about code design."
}

LIKERT_5_OPTIONS = ["Not selected", "1 - Strongly disagree", "2 - Disagree", "3 - Neutral", "4 - Agree", "5 - Strongly agree"]


def collaboration_questions_page():
    """Ask about collaboration during code review."""
    page_header(
        "Code Review Collaboration",
        "Tell us about your collaboration with the reviewer during the code review process."
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
    st.info(f"**Pull Request:** [{pr_url}]({pr_url})")
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Load previous responses
    previous_responses = st.session_state.get('pr_closed_collaboration', {})

    # Question 1: Overall collaboration description (audio or text)
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-bottom: 1.5rem;'>
        How would you describe collaboration during code review overall?
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
        transcript = record_audio("collaboration_description", min_duration=10, max_duration=600)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response = st.text_area(
            "Your response:",
            key="collaboration_description_text",
            value=previous_responses.get('collaboration_description', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript:
        collaboration_description = transcript
    elif text_response and text_response.strip():
        collaboration_description = text_response
    else:
        collaboration_description = previous_responses.get('collaboration_description', '')

    st.divider()

    # Question 2: Collaboration statements (5-point Likert scale)
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-bottom: 1rem;'>
        Please rate how much you agree or disagree with the following statements.
        </p>
        """, unsafe_allow_html=True)

    collaboration_ratings = {}
    for key, question in COLLABORATION_QUESTIONS.items():
        collaboration_ratings[key] = slider_question(
            question,
            LIKERT_5_OPTIONS,
            f"collab_{key}",
            previous_responses.get(key, "Not selected")
        )

    st.divider()

    # Question 3: What helped or hindered collaboration (audio or text)
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-bottom: 1.5rem;'>
        What helped or hindered your collaboration with the reviewers? What would have made the review discussions more productive?
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
        transcript_collab = record_audio("collaboration_factors", min_duration=10, max_duration=600)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response_collab = st.text_area(
            "Your response:",
            key="collaboration_factors_text",
            value=previous_responses.get('collaboration_factors', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript_collab:
        collaboration_factors = transcript_collab
    elif text_response_collab and text_response_collab.strip():
        collaboration_factors = text_response_collab
    else:
        collaboration_factors = previous_responses.get('collaboration_factors', '')

    # Combine all responses
    all_responses = {
        'collaboration_description': collaboration_description,
        **collaboration_ratings,
        'collaboration_factors': collaboration_factors
    }

    # Validation function
    def validate():
        # Check collaboration description
        if not collaboration_description or not collaboration_description.strip():
            st.warning('⚠️ Please describe how you collaborated with reviewers.')
            print('collaboration description is empty')
            return False
        # Check all rating questions
        unanswered = []
        for key, v in collaboration_ratings.items():
            print(collaboration_ratings)
            if v == "Not selected":
                unanswered.append(key)

        if unanswered:
            st.warning(f'⚠️ Please answer all collaboration rating questions. Missing: {", ".join(unanswered)}')
            print(f'collaboration ratings missing: {unanswered}')
            return False

        # Check collaboration factors
        if not collaboration_factors or not collaboration_factors.strip():
            st.warning('⚠️ Please describe what helped or hindered collaboration (audio or text).')
            print('collaboration factors is empty')
            return False
        print('validate() passed')
        return True

    # Navigation handlers
    def handle_back():
        # Save to session state
        st.session_state['pr_closed_collaboration'] = all_responses
        st.session_state['page'] = 18  # Back to update issue page
        st.rerun()

    def handle_next():
        if not validate():
            return
        # Save to session state
        st.session_state['pr_closed_collaboration'] = all_responses

        # Save collaboration data to database
        participant_id = st.session_state['survey_responses'].get('participant_id', '')
        issue_id = selected_issue.get('issue_id')

        if participant_id and issue_id:
            # Convert Likert scale responses to numeric values
            db_responses = {}
            collab_keys = ['psych_safety', 'constructiveness', 'shared_ownership', 'problem_solving']
            for i, key in enumerate(collab_keys, start=1):
                value = collaboration_ratings.get(key)
                if value and value != "Not selected":
                    db_responses[f'collab_{i}'] = int(value.split()[0])

            db_responses['collaboration_description'] = collaboration_description
            db_responses['collaboration_factors'] = collaboration_factors

            # Save to database
            with st.spinner('Saving your responses...'):
                result = save_pr_closed_responses(participant_id, int(issue_id), db_responses)

            if result['success']:
                print(f"Collaboration responses saved for participant {participant_id}")
            else:
                st.error(f"⚠️ Error saving responses: {result['error']}")
                print(f"Failed to save collaboration responses: {result['error']}")
                return

        st.session_state['page'] = 20  # Engagement questions page
        st.rerun()

    # Navigation buttons
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_next,
        back_key="collab_back",
        next_key="collab_next",
        next_label="Next",
        show_back=False,
        validation_fn=validate,
        validation_error="Please answer all questions before proceeding."
    )
