"""
Post-issue experience questions page.
Shows for all participants after completing an issue.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import save_and_navigate, record_audio
from survey_data import save_post_issue_responses, save_pr_survey_completion_status


# NASA-TLX questions with 7-point scale
NASA_TLX_QUESTIONS = {
    'mental_demand': "How mentally demanding was the task?",
    'pace': "How hurried or rushed was the pace of the task?",
    'success': "How successful were you in accomplishing what you were asked to do?",
    'effort': "How hard did you have to work to accomplish your level of performance?",
    'frustration': "How frustrated, annoyed, or stressed did you feel while implementing this PR?"
}

NASA_TLX_OPTIONS = ["Not selected", "1 - Very low", "2", "3", "4", "5", "6", "7 - Very high"]


# Interview questions
INTERVIEW_QUESTIONS = [
    "What went well, and what was challenging?",
    # "How did you approach solving this issue? Walk us through your problem-solving process."
]


def post_issue_questions_page():
    """Ask post-PR experience questions for all participants."""
    # Get participant info
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    issue_id = st.session_state['survey_responses'].get('issue_id', '')
    
    
    # Check if participant has already completed post-issue questions
    if participant_id and issue_id:
        from survey_data import check_pr_survey_completion
        completion_result = check_pr_survey_completion(participant_id, int(issue_id))
        
        if completion_result['success'] and completion_result['completed']:
            # Already completed, redirect to already completed page
            st.session_state['page'] = 18  # Already completed page (completion_page)
            st.rerun()
            return
    
    page_header(
        "General Experience",
        "Please tell us about your experience implementing this PR."
    )
    
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

    # Interview Questions Section
    interview_responses = {}
    for i, question in enumerate(INTERVIEW_QUESTIONS, start=1):
        st.markdown(f"""
            <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
            {question}
            </p>
            """, unsafe_allow_html=True)

        # Create tabs for audio and text input
        tab_audio, tab_text = st.tabs(["🎤 Record Audio", "⌨️ Type Response"])

        with tab_audio:
            st.markdown("""
                <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
                Click the microphone button below to record your response. Your audio will be transcribed automatically.
                </p>
                """, unsafe_allow_html=True)
            transcript = record_audio(f"interview_{i}", min_duration=10, max_duration=300)

        with tab_text:
            st.markdown("""
                <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
                Type your response in the text box below.
                </p>
                """, unsafe_allow_html=True)
            text_response = st.text_area(
                "Your response:",
                key=f"interview_text_{i}",
                value=previous_responses.get(f"interview_{i}", ""),
                height=150,
                placeholder="Type your answer here..."
            )

        # Use whichever response is available
        if transcript:
            interview_responses[f"interview_{i}"] = transcript
        elif text_response and text_response.strip():
            interview_responses[f"interview_{i}"] = text_response
        else:
            interview_responses[f"interview_{i}"] = previous_responses.get(f"interview_{i}", "")

        if i < len(INTERVIEW_QUESTIONS):
            st.divider()

    # Combine all responses
    all_responses = {**nasa_tlx_responses, **interview_responses}
    
    # Validation function
    def validate():
        # Check NASA-TLX responses
        for v in nasa_tlx_responses.values():
            if v == "Not selected":
                return False
        # Check interview responses - must have text
        for i in range(1, len(INTERVIEW_QUESTIONS) + 1):
            response = interview_responses.get(f"interview_{i}", "")
            if not response or not response.strip():
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
            if value != "Not selected":
                db_responses[f'nasa_tlx_{i}'] = int(value.split()[0])
        

        # Add interview responses (text)
        for i in range(1, len(INTERVIEW_QUESTIONS) + 1):
            interview_key = f'interview_{i}'
            if interview_key in interview_responses:
                db_responses[interview_key] = interview_responses[interview_key]

        # Save responses to database
        result = save_post_issue_responses(participant_id, int(issue_id), db_responses)
        
        if result['success']:
            # Save PR survey completion status
            save_pr_survey_completion_status(participant_id, int(issue_id), True)
        
        return result
    
    # Custom navigation handler
    def handle_next():
        """Handle next button with database save."""
        if not validate():
            return False
        
        with st.spinner('Saving your responses...'):
            result = save_to_database()
        
        if result['success']:
            print(f"✅ Post-issue responses saved for participant {participant_id}")
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
            # Navigate to completion page (checks if more issues, then redirects appropriately)
            st.session_state['page'] = 18  # completion page
            st.rerun()
    
    # Navigation
    from survey_components import navigation_buttons
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_next_nav,
        back_key="post_issue_back",
        next_key="post_issue_submit",
        next_label="Submit",
        validation_fn=validate,
        validation_error="⚠️ Please fill out all fields before proceeding."
    )
