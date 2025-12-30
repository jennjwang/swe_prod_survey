"""
Post-issue reflection page.
Shows for all participants after completing post-issue questions.
Asks AI-specific questions for participants who used AI.
"""

import streamlit as st
from survey_components import page_header, navigation_buttons
from survey_data import save_post_issue_reflection, check_participant_ai_condition
from survey_utils import record_audio


def post_issue_reflection_page():
    """Ask post-issue reflection questions for all participants."""
    # Get participant info
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    issue_id = st.session_state['survey_responses'].get('issue_id', '')

    # Recovery logic: if issue_id is missing, try to recover from database
    if participant_id and not issue_id:
        from survey_data import get_issue_needing_survey
        survey_check = get_issue_needing_survey(participant_id)
        if survey_check['success'] and survey_check['issue']:
            issue = survey_check['issue']
            issue_id = issue['issue_id']
            st.session_state['survey_responses']['issue_id'] = issue_id
            st.session_state['survey_responses']['issue_url'] = issue.get('issue_url', '')
            st.session_state['survey_responses']['current_issue_using_ai'] = survey_check.get('using_ai', False)
            print(f"DEBUG: Recovered issue_id {issue_id} from database for post-issue reflection")
        else:
            # No issue needing survey, redirect to completion page
            print("DEBUG: No issue needing survey, redirecting to completion page")
            st.session_state['page'] = 16
            st.rerun()
            return

    # Check if this issue used AI
    using_ai = False
    if participant_id and issue_id:
        ai_check = check_participant_ai_condition(participant_id, issue_id)
        if ai_check['success']:
            using_ai = ai_check['using_ai']
            print(f"DEBUG: Issue {issue_id} using_ai = {using_ai}")

    # If not using AI, skip this page entirely
    if not using_ai:
        print(f"DEBUG: Issue {issue_id} not using AI, skipping reflection page")
        # Mark survey as complete for non-AI users
        from survey_data import save_pr_survey_completion_status
        save_pr_survey_completion_status(participant_id, int(issue_id), True)
        st.session_state['page'] = 16  # completion page
        st.rerun()
        return

    page_header(
        "AI Experience",
        "Please reflect on your experience using AI tools for this issue."
    )

    # Display assigned issue for context
    issue_url = st.session_state['survey_responses'].get('issue_url', '')
    if issue_url:
        st.info(f"**Your Assigned Issue:** [{issue_url}]({issue_url})")
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('post_issue_reflection', {})

    all_responses = {}

    # Question 1: AI code quality
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        How would you describe the quality of the AI-generated code? Can you give an example of something it did well or poorly compared to your own code?
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
        transcript1 = record_audio("ai_code_quality", min_duration=10, max_duration=600)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response1 = st.text_area(
            "Your response:",
            key="ai_code_quality_text",
            value=previous_responses.get('ai_code_quality', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript1:
        ai_code_quality = transcript1
    elif text_response1 and text_response1.strip():
        ai_code_quality = text_response1
    else:
        ai_code_quality = previous_responses.get('ai_code_quality', '')

    all_responses['ai_code_quality'] = ai_code_quality

    st.divider()

    # Question 2: Work division
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        How did you divide work between AI-generated suggestions and your own reasoning or implementation?
        </p>
        """, unsafe_allow_html=True)

    # Create tabs for audio and text input
    tab3, tab4 = st.tabs(["🎤 Record Audio", "⌨️ Type Response"])

    with tab3:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Click the microphone button below to record your response. Your audio will be transcribed automatically.
            </p>
            """, unsafe_allow_html=True)
        transcript2 = record_audio("work_division", min_duration=10, max_duration=600)

    with tab4:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response2 = st.text_area(
            "Your response:",
            key="work_division_text",
            value=previous_responses.get('work_division', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript2:
        work_division = transcript2
    elif text_response2 and text_response2.strip():
        work_division = text_response2
    else:
        work_division = previous_responses.get('work_division', '')

    all_responses['work_division'] = work_division

    st.divider()

    # Validation function
    def validate():
        # Check all three questions
        if not ai_code_quality or not ai_code_quality.strip():
            return False
        if not work_division or not work_division.strip():
            return False
        return True

    # Custom save function for database
    def save_to_database():
        """Convert and save reflection responses to database."""
        if not (participant_id and issue_id):
            return {'success': False, 'error': 'Missing participant ID or issue ID'}

        # Save responses to database
        result = save_post_issue_reflection(participant_id, int(issue_id), all_responses)
        return result

    # Custom navigation handlers
    def handle_back():
        # Save to session state
        st.session_state['survey_responses']['post_issue_reflection'] = all_responses
        st.session_state['page'] -= 1
        st.rerun()

    def handle_next():
        if not validate():
            return

        # Save to session state
        st.session_state['survey_responses']['post_issue_reflection'] = all_responses

        # Save to database
        with st.spinner('Saving your responses...'):
            result = save_to_database()

        if result['success']:
            print(f"Post-issue reflection saved for participant {participant_id}")
            # Mark survey as complete for AI users
            from survey_data import save_pr_survey_completion_status
            save_pr_survey_completion_status(participant_id, int(issue_id), True)
            # Navigate to completion page
            st.session_state['page'] = 16  # completion page
            st.rerun()
        else:
            st.error(f"⚠️ Error saving responses: {result['error']}")
            print(f"Failed to save post-issue reflection: {result['error']}")

    # Navigation
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_next,
        back_key="reflection_back",
        next_key="reflection_submit",
        next_label="Submit",
        validation_fn=validate,
        validation_error="⚠️ Please fill out all fields before proceeding."
    )
