"""
Post-issue experience questions page.
Shows for all participants after completing an issue.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import save_and_navigate
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
    
    
    # Check if participant has already completed post-issue questions
    if participant_id and issue_id:
        from survey_data import check_pr_survey_completion
        completion_result = check_pr_survey_completion(participant_id, int(issue_id))
        
        if completion_result['success'] and completion_result['completed']:
            # Already completed, redirect to already completed page
            st.session_state['page'] = 14  # Already completed page (completion_page)
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
    
    # Use NASA-TLX responses as all responses
    all_responses = nasa_tlx_responses
    
    # Validation function
    def validate():
        # Check NASA-TLX responses
        for v in nasa_tlx_responses.values():
            if v == "Not selected":
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
            st.session_state['page'] = 14  # completion page
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
