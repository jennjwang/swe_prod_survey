"""
Tool use preference questions page (post-exp1).
Shows AttrakDiff questions and tool switching questions about Cursor/Claude Code.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import save_and_navigate, record_audio
from survey_data import save_post_exp1_responses


# AttrakDiff questions (1-7 scale, bipolar) - format: (left_word, right_word)
ATTRAKDIFF_QUESTIONS = {
    'complicated_simple': ("Complicated", "Simple"),
    'confusing_clear': ("Confusing", "Clear"),
    'unpredictable_predictable': ("Unpredictable", "Predictable"),
    'cumbersome_straightforward': ("Cumbersome", "Straightforward"),
    'unimaginative_creative': ("Unimaginative", "Creative"),
    'conventional_inventive': ("Conventional", "Inventive"),
    'isolating_connective': ("Isolating", "Connective"),
    'unpresentable_presentable': ("Unpresentable", "Presentable"),
    'discouraging_motivating': ("Discouraging", "Motivating"),
    'bad_good': ("Bad", "Good")
}


def bipolar_question(left_word, right_word, key, previous_value=None):
    """
    Render a bipolar scale question with labels on each side.
    Uses radio buttons in a horizontal layout with clear visual separation.
    """
    # Add custom CSS for radio buttons
    st.markdown("""
        <style>
        div[role="radiogroup"] {
            gap: 0.5rem;
            justify-content: center;
        }
        div[role="radiogroup"] label {
            background-color: #f0f2f6;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid transparent;
        }
        div[role="radiogroup"] label:hover {
            background-color: #e0e3e9;
            border-color: #4CAF50;
        }
        div[role="radiogroup"] label[data-checked="true"] {
            background-color: #4CAF50;
            color: white;
            border-color: #4CAF50;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create labels row
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; margin-top: 1.5rem;'>
            <span style='font-size: 16px; font-weight: 600; color: #333; flex: 0 0 140px;'>{left_word}</span>
            <span style='flex: 1;'></span>
            <span style='font-size: 16px; font-weight: 600; color: #333; flex: 0 0 140px; text-align: right;'>{right_word}</span>
        </div>
        """, unsafe_allow_html=True)

    # Radio buttons for the scale - using Streamlit radio with horizontal orientation
    options = ["1", "2", "3", "4", "5", "6", "7"]

    # Determine default index
    if previous_value and previous_value != "Not selected":
        try:
            default_index = options.index(str(int(previous_value)))
        except (ValueError, TypeError):
            default_index = 0
    else:
        default_index = 0

    # Use radio buttons in horizontal layout
    selected = st.radio(
        label="Select a value",
        options=options,
        index=default_index,
        key=key,
        horizontal=True,
        label_visibility="collapsed"
    )

    return int(selected) if selected else "Not selected"


def tool_preference_page():
    """Display tool use preference questions with AttrakDiff and tool switching questions."""
    page_header(
        "Tool Use Patterns",
        "Please reflect on your experience with your coding tools."
    )

    # Load previous responses
    previous_responses = st.session_state['survey_responses'].get('tool_preference', {})

    # Get AI tool name from session state (default to "AI tools")
    ai_tool_name = st.session_state['survey_responses'].get('ai_tool_name', 'AI tools')

    # Question 1: AI suggestion decision making
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        How do you decide when to accept, modify, or reject an AI-generated suggestion?
        </p>
        """, unsafe_allow_html=True)

    # Create tabs for audio and text input - Question 1
    tab1_q1, tab2_q1 = st.tabs(["🎤 Record Audio", "⌨️ Type Response"])

    with tab1_q1:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Click the microphone button below to record your response. Your audio will be transcribed automatically.
            </p>
            """, unsafe_allow_html=True)
        transcript_q1 = record_audio("ai_suggestion_decision_q1", min_duration=10, max_duration=300)

    with tab2_q1:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response_q1 = st.text_area(
            "Your response:",
            key="ai_suggestion_decision_text_q1",
            value=previous_responses.get('ai_suggestion_decision_q1', ''),
            height=150,
            placeholder="Type your answer here..."
        )

    # Use whichever response is available
    if transcript_q1:
        ai_suggestion_decision_q1 = transcript_q1
    elif text_response_q1 and text_response_q1.strip():
        ai_suggestion_decision_q1 = text_response_q1
    else:
        ai_suggestion_decision_q1 = previous_responses.get('ai_suggestion_decision_q1', '')

    st.divider()

    # # AttrakDiff Section
    # st.markdown(f"""
    #     <p style='font-size:18px; font-weight:600; margin-bottom: 1rem;'>
    #     Rate your experience with {ai_tool_name}
    #     </p>
    #     <p style='font-size:16px; margin-bottom: 2rem; color: #666;'>
    #     For each row, select a number from 1 to 7 based on which word better describes your experience.<br>
    #     <strong>1</strong> means the left word describes your experience, <strong>7</strong> means the right word describes your experience.
    #     </p>
    #     """, unsafe_allow_html=True)

    # attrakdiff_responses = {}
    # for key, (left_word, right_word) in ATTRAKDIFF_QUESTIONS.items():
    #     attrakdiff_responses[key] = bipolar_question(
    #         left_word,
    #         right_word,
    #         f"attrakdiff_{key}",
    #         previous_responses.get(key, "Not selected")
    #     )

    # st.divider()

    # Question 2: Tool switching
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        Do you use Cursor and Claude Code for different purposes? When do you switch between them, and why?
        </p>
        """, unsafe_allow_html=True)

    # Create tabs for audio and text input - Question 2
    tab1_q2, tab2_q2 = st.tabs(["🎤 Record Audio", "⌨️ Type Response"])

    with tab1_q2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Click the microphone button below to record your response. Your audio will be transcribed automatically.
            </p>
            """, unsafe_allow_html=True)
        transcript_switching = record_audio("tool_switching", min_duration=10, max_duration=300)

    with tab2_q2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response_switching = st.text_area(
            "Your response:",
            key="tool_switching_text",
            value=previous_responses.get('tool_switching', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript_switching:
        tool_switching_response = transcript_switching
    elif text_response_switching and text_response_switching.strip():
        tool_switching_response = text_response_switching
    else:
        tool_switching_response = previous_responses.get('tool_switching', '')

    st.divider()

    # Question 2: Ideal interaction
    st.markdown("""
        <p style='font-size:18px; font-weight:400; margin-bottom: 1.5rem;'>
        How would you describe an "ideal" interaction with your coding tools?
        </p>
        """, unsafe_allow_html=True)

    # Create tabs for audio and text input - Question 2
    tab3, tab4 = st.tabs(["🎤 Record Audio", "⌨️ Type Response"])

    with tab3:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Click the microphone button below to record your response. Your audio will be transcribed automatically.
            </p>
            """, unsafe_allow_html=True)
        transcript_ideal = record_audio("ideal_interaction", min_duration=10, max_duration=300)

    with tab4:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response_ideal = st.text_area(
            "Your response:",
            key="ideal_interaction_text",
            value=previous_responses.get('ideal_interaction', ''),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript_ideal:
        ideal_interaction_response = transcript_ideal
    elif text_response_ideal and text_response_ideal.strip():
        ideal_interaction_response = text_response_ideal
    else:
        ideal_interaction_response = previous_responses.get('ideal_interaction', '')

    # Combine all responses
    tool_usage_responses = {
        'ai_suggestion_decision_q1': ai_suggestion_decision_q1,
        'tool_switching': tool_switching_response,
        'ideal_interaction': ideal_interaction_response
    }
    # all_responses = {**attrakdiff_responses, **tool_usage_responses}
    all_responses = {**tool_usage_responses}

    # Validation function
    def validate():
        # Check that text responses are not empty
        if not ai_suggestion_decision_q1 or not ai_suggestion_decision_q1.strip():
            return False
        if not tool_switching_response or not tool_switching_response.strip():
            return False
        if not ideal_interaction_response or not ideal_interaction_response.strip():
            return False
        # Check that all AttrakDiff responses are selected
        # for key, v in attrakdiff_responses.items():
        #     if v == "Not selected":
        #         return False
        return True

    # Custom navigation handlers
    def handle_back():
        # Save to session state
        st.session_state['survey_responses']['tool_preference'] = all_responses
        st.session_state['page'] -= 1
        st.rerun()

    def handle_next():
        if not validate():
            return

        # Save to session state
        st.session_state['survey_responses']['tool_preference'] = all_responses

        # Save to database
        participant_id = st.session_state['survey_responses'].get('participant_id', '')
        if participant_id:
            result = save_post_exp1_responses(participant_id, all_responses)
            if not result['success']:
                st.error(f"Error saving responses: {result['error']}")
                return

        # Navigate to next page
        st.session_state['page'] += 1
        st.rerun()

    # Navigation
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_next,
        back_key="tool_preference_back",
        next_key="tool_preference_next",
        validation_fn=validate,
        validation_error="⚠️ Please fill out all fields before proceeding."
    )
