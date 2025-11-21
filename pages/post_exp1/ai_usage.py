"""
AI usage questions page (post-exp1).
Shows AI perception ratings and interview questions about AI helpfulness.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import save_and_navigate, record_audio
from survey_data import save_post_exp1_responses


def ai_usage_page():
    """Display AI usage questions with perception ratings and interview questions."""
    page_header(
        "AI Usage Patterns",
        "Please reflect on your overall experience using AI tools during this experiment."
    )

    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('ai_usage', {})

    # Interview Questions Section with Audio
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        What kinds of tasks do you find AI most and least helpful for?
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
        transcript_helpful = record_audio("ai_helpful_tasks", min_duration=10, max_duration=300)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response_helpful = st.text_area(
            "Your response:",
            key="ai_helpful_tasks_text",
            value=previous_responses.get('ai_helpful_tasks', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript_helpful:
        ai_helpful_tasks_response = transcript_helpful
    elif text_response_helpful and text_response_helpful.strip():
        ai_helpful_tasks_response = text_response_helpful
    else:
        ai_helpful_tasks_response = previous_responses.get('ai_helpful_tasks', '')

    st.divider()

    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        How do you decide when to accept, modify, or reject an AI-generated suggestion?
        </p>
        """, unsafe_allow_html=True)

    # Create tabs for audio and text input
    tab5, tab6 = st.tabs(["🎤 Record Audio", "⌨️ Type Response"])

    with tab5:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Click the microphone button below to record your response. Your audio will be transcribed automatically.
            </p>
            """, unsafe_allow_html=True)
        transcript_suggestions = record_audio("ai_suggestion_decisions", min_duration=10, max_duration=300)

    with tab6:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response_suggestions = st.text_area(
            "Your response:",
            key="ai_suggestion_decisions_text",
            value=previous_responses.get('ai_suggestion_decisions', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript_suggestions:
        ai_suggestion_decisions_response = transcript_suggestions
    elif text_response_suggestions and text_response_suggestions.strip():
        ai_suggestion_decisions_response = text_response_suggestions
    else:
        ai_suggestion_decisions_response = previous_responses.get('ai_suggestion_decisions', '')

    st.divider()

    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        What does an ideal interaction with an AI coding assistant look like for you? What do you wish these tools did differently?
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
        transcript_wish = record_audio("ai_wish_different", min_duration=10, max_duration=300)

    with tab4:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response_wish = st.text_area(
            "Your response:",
            key="ai_wish_different_text",
            value=previous_responses.get('ai_wish_different', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript_wish:
        ai_wish_different_response = transcript_wish
    elif text_response_wish and text_response_wish.strip():
        ai_wish_different_response = text_response_wish
    else:
        ai_wish_different_response = previous_responses.get('ai_wish_different', '')

    # Combine all responses
    interview_responses = {
        'ai_helpful_tasks': ai_helpful_tasks_response,
        'ai_wish_different': ai_wish_different_response,
        'ai_suggestion_decisions': ai_suggestion_decisions_response
    }
    all_responses = {**interview_responses}

    # Validation function
    def validate():
        # Check that audio/text responses are not empty
        if not ai_helpful_tasks_response or not ai_helpful_tasks_response.strip():
            return False
        if not ai_wish_different_response or not ai_wish_different_response.strip():
            return False
        if not ai_suggestion_decisions_response or not ai_suggestion_decisions_response.strip():
            return False
        return True

    # # Custom navigation handlers
    # def handle_back():
    #     # Save to session state
    #     st.session_state['survey_responses']['ai_usage'] = all_responses
    #     st.session_state['page'] -= 1
    #     st.rerun()

    def handle_next():
        if not validate():
            return

        # Save to session state
        st.session_state['survey_responses']['ai_usage'] = all_responses

        # Save to database
        participant_id = st.session_state['survey_responses'].get('participant_id', '')
        if participant_id:
            result = save_post_exp1_responses(participant_id, all_responses)
            if not result['success']:
                st.error(f"Error saving responses: {result['error']}")
                return

        # Navigate to thank you page
        st.session_state['page'] = 16  # Thank you page (page 16)
        st.rerun()

    # Navigation
    navigation_buttons(
        on_back=None,
        on_next=handle_next,
        back_key="ai_usage_back",
        next_key="ai_usage_next",
        validation_fn=validate,
        validation_error="⚠️ Please fill out all fields before proceeding."
    )
