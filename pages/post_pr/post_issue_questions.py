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
    'pace': "How hurried or rushed was the pace of the task?",
    'success': "How successful were you in accomplishing what you were asked to do?",
    'effort': "How hard did you have to work to accomplish your level of performance?",
    'frustration': "How frustrated, annoyed, or stressed did you feel while reviewing this PR?"
}

NASA_TLX_OPTIONS = ["Not selected", "1 - Very low", "2", "3", "4", "5", "6", "7 - Very high"]

# Code quality questions with 5-point scale
CODE_QUALITY_QUESTIONS = {
    'readability': "This code is easy to read (readability)",
    'analyzability': "This code's logic and structure are easy to understand (analyzability)",
    'modifiability': "This code would be easy to modify or extend (modifiability)",
    'testability': "This code would be easy to test (testability)",
    'stability': "This code would be stable when changes are made. (stability)",
    'correctness': "This code performs as intended. (correctness)",
    'compliance': "This code follows the repository's established standards and practices. (compliance)"
}

CODE_QUALITY_OPTIONS = ["Not selected", "1 - Strongly disagree", "2", "3", "4", "5 - Strongly agree"]


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
            st.session_state['page'] = 14  # Already completed page
            st.rerun()
            return
    
    page_header(
        "Post-PR Experience",
        "Please tell us about your experience with this PR."
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
    
    # Code Quality Section
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-top: 2rem; margin-bottom: 1rem;'>
        Rate the following statements about the code you wrote:
        </p>
        <p style='font-size:16px; margin-bottom: 1.5rem;'>
        </p>
        """, unsafe_allow_html=True)
    
    code_quality_responses = {}
    for key, statement in CODE_QUALITY_QUESTIONS.items():
        code_quality_responses[key] = slider_question(
            statement,
            CODE_QUALITY_OPTIONS,
            f"code_quality_{key}",
            previous_responses.get(key, "Not selected")
        )
    
    # Combine all responses
    all_responses = {**nasa_tlx_responses, **code_quality_responses}
    
    # Validation function
    def validate():
        return all(v != "Not selected" for v in all_responses.values())
    
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
        
        # Convert code quality responses (1-5) to numbered columns
        code_keys = ['readability', 'analyzability', 'modifiability', 'testability', 'stability', 'correctness', 'compliance']
        for i, key in enumerate(code_keys, start=1):
            value = code_quality_responses.get(key)
            if value != "Not selected":
                db_responses[f'code_quality_{i}'] = int(value.split()[0])
        
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
    
    # Navigation
    from survey_components import navigation_buttons
    navigation_buttons(
        on_back=lambda: save_and_navigate('back', post_issue=all_responses),
        on_next=lambda: save_and_navigate('next', post_issue=all_responses) if handle_next() else None,
        back_key="post_issue_back",
        next_key="post_issue_submit",
        next_label="Submit",
        validation_fn=validate,
        validation_error="⚠️ Please fill out all fields before proceeding."
    )
