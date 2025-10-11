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
    """Ask post-issue experience questions for all participants."""
    page_header(
        "Post-Issue Experience",
        "Please rate your experience while implementing this PR."
    )
    
    # Get participant info
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    issue_id = st.session_state['survey_responses'].get('issue_id', '')
    
    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('post_issue', {})
    
    # NASA-TLX Section
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-top: 2rem; margin-bottom: 1rem;'>
        Please rate your experience while implementing this PR. [Drawn from NASA-TLX]
        </p>
        <p style='font-size:16px; margin-bottom: 1.5rem;'>
        (Scale: 1 = Very low, 7 = Very high)
        </p>
        """, unsafe_allow_html=True)
    
    nasa_tlx_responses = {}
    for key, question in NASA_TLX_QUESTIONS.items():
        nasa_tlx_responses[key] = slider_question(
            question,
            NASA_TLX_OPTIONS,
            f"nasa_tlx_{key}",
            previous_responses.get(key, "Not selected"),
            font_size=18,
            font_weight=400
        )
    
    st.divider()
    
    # Code Quality Section
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-top: 2rem; margin-bottom: 1rem;'>
        Rate the following statements about the code you wrote:
        </p>
        <p style='font-size:16px; margin-bottom: 1.5rem;'>
        (Scale: 1 = Strongly disagree, 5 = Strongly agree)
        </p>
        """, unsafe_allow_html=True)
    
    code_quality_responses = {}
    for key, statement in CODE_QUALITY_QUESTIONS.items():
        code_quality_responses[key] = slider_question(
            statement,
            CODE_QUALITY_OPTIONS,
            f"code_quality_{key}",
            previous_responses.get(key, "Not selected"),
            font_size=18,
            font_weight=400
        )
    
    # Combine all responses
    all_responses = {**nasa_tlx_responses, **code_quality_responses}
    
    # Validation function
    def validate():
        return all(v != "Not selected" for v in all_responses.values())
    
    # Custom save and navigate function for this page
    def save_and_continue():
        if not validate():
            st.error("⚠️ Please fill out all fields before proceeding.")
            return
        
        if participant_id and issue_id:
            # Convert responses to database format (remove "Not selected", extract numbers)
            # Map to numbered columns as per schema: nasa_tlx_1, nasa_tlx_2, etc.
            db_responses = {}
            
            # Convert NASA-TLX responses (1-7) to numbered columns
            nasa_keys = ['mental_demand', 'pace', 'success', 'effort', 'frustration']
            for i, key in enumerate(nasa_keys, start=1):
                value = nasa_tlx_responses.get(key)
                if value != "Not selected":
                    # Extract the number from strings like "1 - Very low" or "4"
                    db_responses[f'nasa_tlx_{i}'] = int(value.split()[0])
            
            # Convert code quality responses (1-5) to numbered columns
            code_keys = ['readability', 'analyzability', 'modifiability', 'testability', 'stability', 'correctness', 'compliance']
            for i, key in enumerate(code_keys, start=1):
                value = code_quality_responses.get(key)
                if value != "Not selected":
                    # Extract the number from strings like "1 - Strongly disagree" or "3"
                    db_responses[f'code_quality_{i}'] = int(value.split()[0])
            
            # Save responses to database
            with st.spinner('Saving your responses...'):
                result = save_post_issue_responses(
                    participant_id, 
                    int(issue_id),
                    db_responses
                )
            
            if result['success']:
                print(f"✅ Post-issue responses saved for participant {participant_id}")
                # Save to session state
                st.session_state['survey_responses']['post_issue'] = all_responses
                # Save PR survey completion status
                save_pr_survey_completion_status(participant_id, True)
                # Proceed to completion
                from survey_utils import next_page
                next_page()
            else:
                st.error(f"⚠️ Error saving responses: {result['error']}")
                print(f"Failed to save post-issue responses: {result['error']}")
        else:
            st.error("⚠️ Missing participant ID or issue ID. Please contact the study administrator.")
    
    # Navigation buttons
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("Back", key="post_issue_back"):
            save_and_navigate('back', post_issue=all_responses)
    
    with col3:
        if st.button("Submit", key="post_issue_submit"):
            save_and_continue()
