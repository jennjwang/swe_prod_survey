"""
AI usage questions page (post-exp1).
Shows AI perception ratings and interview questions about AI helpfulness.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import save_and_navigate, record_audio
from survey_data import save_post_exp1_responses


# AI Perception questions (1-7 scale, agreement)
AI_PERCEPTION_QUESTIONS = {
    'codebase_comprehension': "Using AI helps me locate and understand relevant parts of the codebase faster than I could on my own.",
    'code_correctness': "When using AI, I feel more confident in writing code that works correctly.",
    'solution_exploration': "Using AI helps me discover alternative ways to implement a solution.",
    'problem_solving': "When using AI, I feel more capable of solving programming problems that I would otherwise find challenging.",
    'productivity': "Using AI helps me complete programming tasks more quickly than without them."
}

AI_PERCEPTION_OPTIONS = ["Not selected", "1 - Strongly disagree", "2", "3", "4", "5", "6", "7 - Strongly agree"]


def ai_usage_page():
    """Display AI usage questions with perception ratings and interview questions."""
    page_header(
        "Effectiveness of AI Tools",
        "Please reflect on your experience using AI tools during this experiment. For each of the following statements, rate how much you agree or disagree."
    )

    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('ai_usage', {})

    # # AI Perception Section
    # st.markdown("""
    #     <p style='font-size:18px; font-weight:600; margin-bottom: 1rem;'>
    #     For each of the following statements, rate how much you agree or disagree:
    #     </p>
    #     <p style='font-size:16px; margin-bottom: 1.5rem; color: #666;'>
    #     </p>
    #     """, unsafe_allow_html=True)

    ai_perception_responses = {}
    for key, statement in AI_PERCEPTION_QUESTIONS.items():
        ai_perception_responses[key] = slider_question(
            statement,
            AI_PERCEPTION_OPTIONS,
            f"ai_perception_{key}",
            previous_responses.get(key, "Not selected")
        )

    st.divider()

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
        What do you wish these tools did differently?
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
        'ai_wish_different': ai_wish_different_response
    }
    all_responses = {**ai_perception_responses, **interview_responses}

    # Validation function
    def validate():
        # Check that audio/text responses are not empty
        if not ai_helpful_tasks_response or not ai_helpful_tasks_response.strip():
            return False
        if not ai_wish_different_response or not ai_wish_different_response.strip():
            return False
        # Check that all perception responses are selected
        for key, v in ai_perception_responses.items():
            if v == "Not selected":
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

        # Prepare data for database - extract numeric values from perception responses
        db_responses = {}
        for key, value in all_responses.items():
            if key in AI_PERCEPTION_QUESTIONS.keys():
                # Extract numeric part from strings like "1 - Strongly disagree" or "2"
                if isinstance(value, str) and value != "Not selected":
                    # Split on " - " or just take first character if it's a digit
                    numeric_value = value.split(' - ')[0].strip()
                    try:
                        db_responses[key] = int(numeric_value)
                    except ValueError:
                        db_responses[key] = None
                else:
                    db_responses[key] = value
            else:
                # Keep text responses as-is
                db_responses[key] = value

        # Save to database
        participant_id = st.session_state['survey_responses'].get('participant_id', '')
        if participant_id:
            result = save_post_exp1_responses(participant_id, db_responses)
            if not result['success']:
                st.error(f"Error saving responses: {result['error']}")
                return

        # Navigate to next page
        st.session_state['page'] += 1
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
