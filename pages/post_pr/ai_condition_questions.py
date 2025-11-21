"""
AI condition questions page.
Shows only for participants who used AI tools.
"""

import streamlit as st
from survey_components import page_header, navigation_buttons
from survey_utils import record_audio
from survey_data import save_ai_condition_responses, check_participant_ai_condition


def ai_condition_questions_page():
    """Display AI condition questions for AI users."""
    # Get participant info
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    issue_id = st.session_state['survey_responses'].get('issue_id', '')

    # Check if this issue uses AI
    if participant_id and issue_id:
        ai_check = check_participant_ai_condition(participant_id, issue_id)
        print(f"DEBUG: AI condition check for issue {issue_id}: {ai_check}")
        if ai_check['success'] and not ai_check['using_ai']:
            # Not using AI for this issue, skip to post-issue questions page
            print(f"DEBUG: Issue {issue_id} not using AI, skipping to page 11")
            st.session_state['page'] = 11  # post_issue_questions_page
            st.rerun()
            return
        print(f"DEBUG: Showing AI condition questions for issue {issue_id}")

    page_header(
        "AI Tool Experience",
        "Please tell us about your experience using AI tools for this task."
    )

    # Display assigned issue for context
    issue_url = st.session_state['survey_responses'].get('issue_url', '')
    if issue_url:
        st.info(f"**Your Assigned Issue:** [{issue_url}]({issue_url})")
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Load previous response
    previous_response = st.session_state['survey_responses'].get('ai_code_quality_description', '')

    # Single question: AI code quality description
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
        transcript = record_audio("ai_code_quality_description", min_duration=10, max_duration=300)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response = st.text_area(
            "Your response:",
            key="ai_code_quality_description_text",
            value=previous_response,
            height=200,
            placeholder="Please describe your thoughts in 2-3 sentences...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript:
        ai_code_quality = transcript
    elif text_response and text_response.strip():
        ai_code_quality = text_response
    else:
        ai_code_quality = previous_response

    # Validation function
    def validate():
        return ai_code_quality.strip() != ""

    # Custom save function for database
    def save_to_database():
        """Save AI condition responses to database."""
        if not (participant_id and issue_id):
            return {'success': False, 'error': 'Missing participant ID or issue ID'}

        # AI code quality description is kept in session state only
        # No database saving needed for this text response
        return {'success': True, 'error': None}

    # Custom navigation handlers
    def handle_back():
        # Save to session state
        st.session_state['survey_responses']['ai_code_quality_description'] = ai_code_quality
        st.session_state['page'] -= 1
        st.rerun()

    def handle_next():
        if not validate():
            return

        # Save to session state
        st.session_state['survey_responses']['ai_code_quality_description'] = ai_code_quality

        # Save to database
        with st.spinner('Saving your responses...'):
            result = save_to_database()

        if result['success']:
            print(f"✅ AI condition responses saved for participant {participant_id}")
            # Navigate to post-issue questions page
            st.session_state['page'] = 11  # post_issue_questions_page
            st.rerun()
        else:
            st.error(f"⚠️ Error saving responses: {result['error']}")
            print(f"Failed to save AI condition responses: {result['error']}")

    # Navigation
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_next,
        back_key="ai_condition_back",
        next_key="ai_condition_next",
        validation_fn=validate,
        validation_error="⚠️ Please answer the question before proceeding."
    )
