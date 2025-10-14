"""
Study validation questions page (post-exp1).
Asks about how the study workflow compared to normal work.
"""

import streamlit as st
from survey_components import page_header, navigation_buttons
from survey_utils import record_audio
from survey_data import save_post_exp1_responses


def study_val_page():
    """Display study validation questions about workflow comparison."""
    page_header(
        "Study Experience",
        "Please reflect on how this study compared to your normal work."
    )

    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('study_val', {})

    # Question: Workflow comparison
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        How different did your workflow in this study feel compared to your normal day-to-day responsibilities? How did the issues you worked on during this study compare to the issues you handle in your work?
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
        transcript = record_audio("workflow_comparison", min_duration=10, max_duration=300)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response = st.text_area(
            "Your response:",
            key="workflow_comparison_text",
            value=previous_responses.get('workflow_comparison', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript:
        workflow_comparison_response = transcript
    elif text_response and text_response.strip():
        workflow_comparison_response = text_response
    else:
        workflow_comparison_response = previous_responses.get('workflow_comparison', '')

    # Combine all responses
    all_responses = {
        'workflow_comparison': workflow_comparison_response
    }

    # Validation function
    def validate():
        # Check that audio/text response is not empty
        if not workflow_comparison_response or not workflow_comparison_response.strip():
            return False
        return True

    def handle_next():
        if not validate():
            return

        # Save to session state
        st.session_state['survey_responses']['study_val'] = all_responses

        # Save to database
        participant_id = st.session_state['survey_responses'].get('participant_id', '')
        if participant_id:
            result = save_post_exp1_responses(participant_id, all_responses)
            if not result['success']:
                st.error(f"Error saving responses: {result['error']}")
                return

        # Navigate to next page (ai_usage_page)
        st.session_state['page'] += 1
        st.rerun()

    # Navigation
    navigation_buttons(
        on_back=None,
        on_next=handle_next,
        back_key="study_val_back",
        next_key="study_val_next",
        validation_fn=validate,
        validation_error="⚠️ Please answer the question before proceeding."
    )
