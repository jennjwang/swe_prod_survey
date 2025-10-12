"""
AI condition questions page.
Shows only for participants in AI condition after PR submission.
"""

import streamlit as st
from survey_components import page_header, selectbox_question, navigation_buttons
from survey_utils import save_and_navigate
from survey_data import check_participant_ai_condition, save_ai_condition_responses, save_pr_survey_completion_status


# Code review approach options with "Not selected"
CODE_REVIEW_OPTIONS = [
    "Not selected",
    "I did not read the AI-generated code; I only checked that the outputs ran without errors.",
    "I skimmed the AI-generated code to see if it looked correct.",
    "I selectively reviewed lines of code that seemed most complex or error-prone.",
    "I carefully read every line of AI-generated code to check its correctness."
]


def ai_condition_questions_page():
    """Ask AI condition-specific questions after PR submission."""
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
        "AI Use",
        "Please answer these questions about your experience using AI for this task."
    )
    
    # Check if participant is in AI condition
    if 'ai_condition_checked' not in st.session_state:
        with st.spinner('Checking your study condition...'):
            ai_condition_result = check_participant_ai_condition(participant_id)
            st.session_state['ai_condition_checked'] = True
            st.session_state['using_ai'] = ai_condition_result.get('using_ai', False)
    
    using_ai = st.session_state.get('using_ai', False)
    
    if not using_ai:
        # Not in AI condition, skip to post-issue questions
        st.info("You are not in the AI condition for this study. Proceeding to post-issue questions.")
        st.session_state['page'] = 13  # Post-issue questions page
        st.rerun()
        return
    
    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('ai_condition', {})
    
    # Speed multiplier question
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1rem;'>
        How much did AI decrease or increase the time it took you to complete this issue?
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <p style='font-size:16px; margin-bottom: 1rem; color: #666;'>
        • If AI made you 2x faster, enter 2<br>
        • If AI made you 2x slower, enter 0.5<br>
        • If AI did not change your speed, enter 1<br>
        • Or type another multiplier that best represents your experience
        </p>
        """, unsafe_allow_html=True)
    
    # Speed multiplier input
    ai_speed_multiplier = st.number_input(
        label="Speed Multiplier",
        min_value=0.1,
        max_value=10.0,
        value=previous_responses.get('speed_multiplier', 1.0),
        step=0.1,
        format="%.1f",
        key="ai_speed_multiplier",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Code review question
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1rem;'>
        During this task, which best describes how you reviewed AI-generated code?
        </p>
        """, unsafe_allow_html=True)
    
    # Code review approach selection
    code_review_approach = st.selectbox(
        label="Code Review Approach",
        options=CODE_REVIEW_OPTIONS,
        index=CODE_REVIEW_OPTIONS.index(previous_responses.get('code_review_approach', 'Not selected')),
        key="code_review_approach",
        label_visibility="collapsed"
    )
    
    # Validation function
    def validate():
        return (
            ai_speed_multiplier is not None and 
            code_review_approach != "Not selected"
        )
    
    # Error message container (outside columns for full width)
    error_container = st.container()
    
    # Navigation buttons
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        back_clicked = st.button("Back", key="ai_condition_back")
    
    with col3:
        next_clicked = st.button("Next", key="ai_condition_submit")
    
    # Handle button clicks
    if back_clicked:
        # Save current responses to session state before going back
        st.session_state['survey_responses']['ai_condition'] = {
            'speed_multiplier': ai_speed_multiplier,
            'code_review_approach': code_review_approach
        }
        from survey_utils import previous_page
        previous_page()
    
    if next_clicked:
        if not validate():
            with error_container:
                st.error("⚠️ Please answer both questions to proceed.")
        elif not issue_id:
            with error_container:
                st.error("⚠️ Issue ID not found. Please contact the study administrator.")
        else:
            # Save responses to database
            with st.spinner('Saving your responses...'):
                result = save_ai_condition_responses(
                    participant_id, 
                    int(issue_id),
                    float(ai_speed_multiplier), 
                    code_review_approach
                )
            
            if result['success']:
                print(f"✅ AI condition responses saved for participant {participant_id}")
                # Save to session state
                st.session_state['survey_responses']['ai_condition'] = {
                    'speed_multiplier': ai_speed_multiplier,
                    'code_review_approach': code_review_approach
                }
                # Proceed to post-issue questions
                st.session_state['page'] = 13  # Post-issue questions page
                st.rerun()
            else:
                with error_container:
                    st.error(f"⚠️ Error saving responses: {result['error']}")
                print(f"Failed to save AI condition responses: {result['error']}")
