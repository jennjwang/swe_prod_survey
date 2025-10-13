"""
AI condition questions page.
Shows only for participants in AI condition after PR submission.
"""

import streamlit as st
from survey_components import page_header, selectbox_question, navigation_buttons
from survey_utils import save_and_navigate, record_audio
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
            st.session_state['page'] = 18  # Already completed page (completion_page)
            st.rerun()
            return
    
    page_header(
        "AI Usage",
        "Tell us about your experience using AI for this PR implementation."
    )
    
    # Check if participant is in AI condition
    if 'ai_condition_checked' not in st.session_state:
        with st.spinner('Checking your study condition...'):
            ai_condition_result = check_participant_ai_condition(participant_id)
            st.session_state['ai_condition_checked'] = True
            st.session_state['using_ai'] = ai_condition_result.get('using_ai', False)
    
    using_ai = st.session_state.get('using_ai', False)
    
    if not using_ai:
        # Not in AI condition, skip to code quality page
        st.info("You are not in the AI condition for this study. Proceeding to code quality assessment.")
        st.session_state['page'] = 13  # Code quality page
        st.rerun()
        return
    
    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('ai_condition', {})
    
    # Speed multiplier question
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        How much did AI decrease or increase the time it took you to complete this issue?
        </p>
        """, unsafe_allow_html=True)
    
    # Instructions box with better formatting
    st.markdown("""
        <div style='background-color: #f8f9fa; border-left: 4px solid #4CAF50; padding: 1rem 1.5rem; margin-bottom: 1.5rem; border-radius: 4px;'>
            <p style='font-size:16px; font-weight:600; margin-bottom: 0.75rem; color: #333;'>
            How to enter your response:
            </p>
            <div style='font-size:15px; color: #555; line-height: 1.8;'>
                <p style='margin: 0.5rem 0;'>
                    <strong style='color: #4CAF50;'>2x faster</strong> → enter <code style='background-color: #e8f5e9; padding: 2px 8px; border-radius: 3px; font-weight: 600;'>2</code>
                </p>
                <p style='margin: 0.5rem 0;'>
                    <strong style='color: #FF9800;'>2x slower</strong> → enter <code style='background-color: #fff3e0; padding: 2px 8px; border-radius: 3px; font-weight: 600;'>0.5</code>
                </p>
                <p style='margin: 0.5rem 0;'>
                    <strong style='color: #2196F3;'>No change</strong> → enter <code style='background-color: #e3f2fd; padding: 2px 8px; border-radius: 3px; font-weight: 600;'>1</code>
                </p>
                <p style='margin: 0.75rem 0 0.25rem 0; color: #666; font-style: italic;'>
                    Or enter any other multiplier that best represents your experience
                </p>
            </div>
        </div>
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

    st.divider()

    # Question 2: Code editing
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        How did AI tools help or hinder your work on this issue? Please provide specific examples.
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
        transcript_q2 = record_audio("ai_code_editing_q2", min_duration=10, max_duration=300)

    with tab4:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response_q2 = st.text_area(
            "Your response:",
            key="ai_code_editing_text_q2",
            value=previous_responses.get('ai_code_editing_q2', ''),
            height=150,
            placeholder="Type your answer here..."
        )

    # Use whichever response is available
    if transcript_q2:
        ai_code_editing_q2 = transcript_q2
    elif text_response_q2 and text_response_q2.strip():
        ai_code_editing_q2 = text_response_q2
    else:
        ai_code_editing_q2 = previous_responses.get('ai_code_editing_q2', '')

    # Validation function
    def validate():
        # Check required fields
        if ai_speed_multiplier is None:
            return False
        if code_review_approach == "Not selected":
            return False
        # Check audio/text responses
        if not ai_code_editing_q2 or not ai_code_editing_q2.strip():
            return False
        return True
    
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
            'code_review_approach': code_review_approach,
            'ai_code_editing_q2': ai_code_editing_q2
        }
        from survey_utils import previous_page
        previous_page()

    if next_clicked:
        if not validate():
            with error_container:
                st.error("⚠️ Please answer all questions to proceed.")
        elif not issue_id:
            with error_container:
                st.error("⚠️ Issue ID not found. Please contact the study administrator.")
        else:
            # Save responses to database
            with st.spinner('Saving your responses...'):
                # First save the basic AI condition responses
                result = save_ai_condition_responses(
                    participant_id,
                    int(issue_id),
                    float(ai_speed_multiplier),
                    code_review_approach
                )

                # Then save the audio/text responses via save_post_issue_responses
                if result['success']:
                    from survey_data import save_post_issue_responses
                    audio_responses = {
                        'ai_code_editing_q2': ai_code_editing_q2
                    }
                    audio_result = save_post_issue_responses(participant_id, int(issue_id), audio_responses)

                    if not audio_result['success']:
                        result = audio_result  # Override with audio result if it failed

            if result['success']:
                print(f"✅ AI condition responses saved for participant {participant_id}")
                # Save to session state
                st.session_state['survey_responses']['ai_condition'] = {
                    'speed_multiplier': ai_speed_multiplier,
                    'code_review_approach': code_review_approach,
                    'ai_code_editing_q2': ai_code_editing_q2
                }
                # Proceed to code quality page
                st.session_state['page'] = 13  # Code quality page
                st.rerun()
            else:
                with error_container:
                    st.error(f"⚠️ Error saving responses: {result['error']}")
                print(f"Failed to save AI condition responses: {result['error']}")
