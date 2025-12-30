"""
Post-issue experience questions page.
Shows for all participants after completing an issue.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import record_audio
from survey_data import save_post_issue_responses, save_pr_survey_completion_status


# NASA-TLX questions with 7-point scale
NASA_TLX_QUESTIONS = {
    'mental_demand': "How mentally demanding was the task?",
    'effort': "How hard did you have to work to accomplish your level of performance?",
    'frustration': "How frustrated, annoyed, or stressed did you feel while implementing this PR?"
}

NASA_TLX_OPTIONS = ["Not selected", "1 - Very low", "2", "3", "4", "5", "6", "7 - Very high"]


def post_issue_questions_page():
    """Ask post-PR experience questions for all participants."""
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
            print(f"DEBUG: Recovered issue_id {issue_id} from database for post-issue questions")
        else:
            # No issue needing survey, redirect to completion page
            print("DEBUG: No issue needing survey, redirecting to completion page")
            st.session_state['page'] = 16
            st.rerun()
            return

    # Check if participant has already completed post-issue questions
    if participant_id and issue_id:
        from survey_data import check_pr_survey_completion
        completion_result = check_pr_survey_completion(participant_id, int(issue_id))

        if completion_result['success'] and completion_result['completed']:
            # Already completed, redirect to already completed page
            st.session_state['page'] = 16  # Already completed page (completion_page)
            st.rerun()
            return
    
    page_header(
        "General Experience",
        "Please tell us about your experience implementing this PR."
    )

    # Display assigned issue for context
    issue_url = st.session_state['survey_responses'].get('issue_url', '')
    if issue_url:
        st.info(f"**Your Assigned Issue:** [{issue_url}]({issue_url})")
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('post_issue', {})
    
    # Display all NASA-TLX questions
    nasa_tlx_responses = {}
    for key, question in NASA_TLX_QUESTIONS.items():
        nasa_tlx_responses[key] = slider_question(
            question,
            NASA_TLX_OPTIONS,
            f"nasa_tlx_{key}",
            previous_responses.get(key, "Not selected")
        )

    st.divider()

    # Open-ended question about time/effort (audio or text)
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        Where did you spend the most time or effort while implementing this PR?
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
        transcript = record_audio("time_effort_description", min_duration=10, max_duration=600)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response = st.text_area(
            "Your response:",
            key="time_effort_description_text",
            value=previous_responses.get('time_effort_description', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript:
        time_effort_description = transcript
    elif text_response and text_response.strip():
        time_effort_description = text_response
    else:
        time_effort_description = previous_responses.get('time_effort_description', '')

    # Combine all responses
    all_responses = {**nasa_tlx_responses, 'time_effort_description': time_effort_description}
    
    # Validation function
    def validate():
        # Check NASA-TLX responses
        for v in nasa_tlx_responses.values():
            if v == "Not selected":
                return False
        # Check open-ended question
        if not time_effort_description or not time_effort_description.strip():
            return False
        return True
    
    # Custom save function for database
    def save_to_database():
        """Convert and save responses to database."""
        if not (participant_id and issue_id):
            return {'success': False, 'error': 'Missing participant ID or issue ID'}
        
        # Convert responses to database format (remove "Not selected", extract numbers)
        # Map to numbered columns as per schema: nasa_tlx_1, nasa_tlx_2, etc.
        db_responses = {}
        
        # Convert NASA-TLX responses (1-7) to numbered columns
        nasa_keys = ['mental_demand', 'pace', 'success', 'effort', 'frustration']
        for i, key in enumerate(nasa_keys, start=1):
            value = nasa_tlx_responses.get(key)
            if value and value != "Not selected":
                db_responses[f'nasa_tlx_{i}'] = int(value.split()[0])

        # Add open-ended question
        db_responses['time_effort_description'] = time_effort_description


        # Save responses to database
        result = save_post_issue_responses(participant_id, int(issue_id), db_responses)

        # Note: Don't mark survey as completed here - it will be marked complete
        # after the reflection page (for AI users) or in the reflection page skip logic (for non-AI users)

        return result
    
    # Custom navigation handler
    def handle_next():
        """Handle next button with database save."""
        if not validate():
            return False
        
        with st.spinner('Saving your responses...'):
            result = save_to_database()
        
        if result['success']:
            print(f"Post-issue responses saved for participant {participant_id}")
            # Save to session state
            st.session_state['survey_responses']['post_issue'] = all_responses
            return True
        else:
            st.error(f"⚠️ Error saving responses: {result['error']}")
            print(f"Failed to save post-issue responses: {result['error']}")
            return False
    
    # Custom navigation handlers
    def handle_back():
        # Save to session state
        st.session_state['survey_responses']['post_issue'] = all_responses
        st.session_state['page'] -= 1
        st.rerun()
    
    def handle_next_nav():
        if not validate():
            return

        # Save to database and session state
        if handle_next():
            # Navigate to reflection page
            st.session_state['page'] = 13  # post_issue_reflection_page
            st.rerun()
    
    # Navigation
    from survey_components import navigation_buttons
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_next_nav,
        back_key="post_issue_back",
        next_key="post_issue_next",
        next_label="Next",
        validation_fn=validate,
        validation_error="⚠️ Please fill out all fields before proceeding."
    )
