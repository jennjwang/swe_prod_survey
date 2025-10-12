"""
Code quality assessment page.
Shows for all participants after AI condition questions (or after issue completion for non-AI users).
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import save_and_navigate, record_audio
from survey_data import save_post_issue_responses


# Code quality rating questions (1-5 scale)
CODE_QUALITY_QUESTIONS = {
    'readability': "This code is easy to read",
    'analyzability': "This code's logic and structure are easy to understand",
    'modifiability': "This code would be easy to modify or extend",
    'testability': "This code would be easy to test",
    'stability': "This code would be stable when changes are made",
    'correctness': "This code performs as intended",
    'compliance': "This code follows the repository's established standards and practices"
}

CODE_QUALITY_OPTIONS = ["Not selected", "1 - Strongly disagree", "2", "3", "4", "5 - Strongly agree"]


def code_quality_page():
    """Ask code quality assessment questions."""
    page_header(
        "Code Quality",
        "Please rate the quality of the code you submitted for this issue."
    )

    # Get participant info
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    issue_id = st.session_state['survey_responses'].get('issue_id', '')

    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('code_quality', {})

    # # Display code quality rating questions
    # st.markdown("""
    #     <p style='font-size:18px; font-weight:600; margin-bottom: 1rem;'>
    #     Rate the following statements (1 = strongly disagree, 5 = strongly agree):
    #     </p>
    #     """, unsafe_allow_html=True)

    code_quality_responses = {}
    for key, statement in CODE_QUALITY_QUESTIONS.items():
        code_quality_responses[key] = slider_question(
            statement,
            CODE_QUALITY_OPTIONS,
            f"code_quality_{key}",
            previous_responses.get(key, "Not selected")
        )

    st.divider()

    # Audio question about code quality
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        How would you describe the quality of the code that AI generated? How does it compare to the quality of the code you wrote?
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
        transcript = record_audio("code_quality_description", min_duration=10, max_duration=300)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response = st.text_area(
            "Your response:",
            key="code_quality_description_text",
            value=previous_responses.get('code_quality_description', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript:
        code_quality_description = transcript
    elif text_response and text_response.strip():
        code_quality_description = text_response
    else:
        code_quality_description = previous_responses.get('code_quality_description', '')

    # Combine all responses
    all_responses = {**code_quality_responses, 'code_quality_description': code_quality_description}

    # Validation function
    def validate():
        # Check that all rating questions are answered
        for v in code_quality_responses.values():
            if v == "Not selected":
                return False
        # Check that audio/text response is not empty
        if not code_quality_description or not code_quality_description.strip():
            return False
        return True

    # Custom save function for database
    def save_to_database():
        """Convert and save responses to database."""
        if not (participant_id and issue_id):
            return {'success': False, 'error': 'Missing participant ID or issue ID'}

        # Convert responses to database format
        db_responses = {}

        # Convert rating responses (1-5) to numbered columns
        quality_keys = ['readability', 'analyzability', 'modifiability', 'testability', 'stability', 'correctness', 'compliance']
        for i, key in enumerate(quality_keys, start=1):
            value = code_quality_responses.get(key)
            if value != "Not selected":
                db_responses[f'code_quality_{i}'] = int(value.split()[0])

        # Add description (text/audio)
        db_responses['code_quality_description'] = code_quality_description

        # Save responses to database
        result = save_post_issue_responses(participant_id, int(issue_id), db_responses)

        return result

    # Custom navigation handler
    def handle_next():
        """Handle next button with database save."""
        if not validate():
            return False

        with st.spinner('Saving your responses...'):
            result = save_to_database()

        if result['success']:
            print(f"✅ Code quality responses saved for participant {participant_id}")
            # Save to session state
            st.session_state['survey_responses']['code_quality'] = all_responses
            return True
        else:
            st.error(f"⚠️ Error saving responses: {result['error']}")
            print(f"Failed to save code quality responses: {result['error']}")
            return False

    # Navigation
    navigation_buttons(
        on_back=lambda: save_and_navigate('back', code_quality=all_responses),
        on_next=lambda: save_and_navigate('next', code_quality=all_responses) if handle_next() else None,
        back_key="code_quality_back",
        next_key="code_quality_next",
        validation_fn=validate,
        validation_error="⚠️ Please fill out all fields before proceeding."
    )
