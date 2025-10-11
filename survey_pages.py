"""
Individual page components for the developer survey.
"""

import io
import wave
import streamlit as st
import openai
from survey_questions import (
    SATISFACTION_QUESTIONS,
    SATISFACTION_SLIDER_OPTIONS,
    EXPERIENCE_OPTIONS,
    SELF_EFFICACY_QUESTIONS,
    SELF_EFFICACY_OPTIONS,
    AI_FREQUENCY_QUESTIONS,
    FREQUENCY_OPTIONS,
    TASK_ESTIMATION_QUESTIONS,
    QUALITY_CHANGE_OPTIONS
)

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=st.secrets.get('OPENAI_KEY', ''))

# Demo mode for testing
DEMO_MODE = str(st.secrets.get('DEMO_MODE', 'false')).lower() in ('1', 'true', 'yes', 'on')


def get_audio_duration(file):
    """Get the duration of an audio file in seconds."""
    try:
        with wave.open(file, 'rb') as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            duration_seconds = frames / float(rate)
            return duration_seconds
    except wave.Error:
        st.error("Audio format not supported. Please upload a WAV file.")
        return None


def record_audio(question_key, min_duration=20, max_duration=120):
    """
    Record and transcribe audio for a question.
    
    Args:
        question_key: Unique key for the question
        min_duration: Minimum audio duration in seconds
        max_duration: Maximum audio duration in seconds
        
    Returns:
        The transcribed (and optionally edited) text, or None if not yet completed
    """
    work_audio = None
    
    # Prefer stable API if available
    if hasattr(st, "audio_input"):
        work_audio = st.audio_input(
            "Your voice recording will not be stored; only a transcript of the audio will be collected. ",
            # f"Please provide at least {min_duration} seconds of audio and restrict your recording to "
            # f"{max_duration // 60} minutes or less.",
            key=f"audio_{question_key}"
        )
    elif hasattr(st, "experimental_audio_input"):
        work_audio = st.experimental_audio_input(
            "Your voice recording will not be stored; only a transcript of the audio will be collected. "
            f"Please provide at least {min_duration} seconds of audio and restrict your recording to "
            f"{max_duration // 60} minutes or less.",
            key=f"audio_{question_key}"
        )
    else:
        st.info("Audio recording is not supported in this Streamlit version.")
        if DEMO_MODE:
            demo_text = st.text_area("Enter your response (demo mode):", key=f"demo_text_{question_key}")
            if st.button("Use demo text", key=f"demo_use_{question_key}"):
                st.session_state[f'audio_transcript_{question_key}'] = demo_text or ""
                st.success("Recorded demo text. Please review and edit below.")

    if st.button("Transcribe", key=f"transcript_{question_key}"):
        if work_audio:
            # Read the audio bytes
            audio_bytes = work_audio.read()
            audio_file = io.BytesIO(audio_bytes)
            
            # Get the duration of the audio file
            duration_seconds = get_audio_duration(audio_file)
            
            if duration_seconds is None:
                st.error("Unsupported audio format. Please record in WAV format.")
            elif duration_seconds < min_duration:
                st.error(f"Please record at least {min_duration} seconds of audio before proceeding.")
            elif duration_seconds > max_duration:
                st.error(f"Please record less than {max_duration // 60} minutes of audio.")
            else:
                st.info("Please wait while we transcribe your audio... Do not refresh the page or click the button again.")
                try:
                    audio_file.seek(0)
                    if not hasattr(audio_file, 'name'):
                        audio_file.name = 'audio.wav'
                    transcription = openai_client.audio.transcriptions.create(
                        model='whisper-1',
                        file=audio_file
                    )
                    st.session_state[f'audio_transcript_{question_key}'] = transcription.text
                    st.success("Transcription complete. Please review and edit if needed.")
                except Exception as e:
                    if DEMO_MODE:
                        st.warning(f"Transcription failed in demo mode: {e}. Using placeholder text.")
                        st.session_state[f'audio_transcript_{question_key}'] = "[Demo transcription placeholder]"
                    else:
                        st.error(f"Transcription failed: {e}")
        else:
            st.warning("Please record audio first before transcribing.")

    # Display the transcript for review and editing
    if f'audio_transcript_{question_key}' in st.session_state:
        edited_transcript = st.text_area(
            "Review and edit your transcript below before submitting:",
            value=st.session_state[f'audio_transcript_{question_key}'],
            key=f"edit_transcript_{question_key}"
        )
        return edited_transcript
    
    return None


def next_page():
    """Navigate to the next page."""
    st.session_state['page'] += 1
    st.rerun()


def previous_page():
    """Navigate to the previous page."""
    st.session_state['page'] -= 1
    st.rerun()


def consent_page():
    """Display the consent page."""
    st.header("Developer Work Survey")
    st.markdown("""
        <p style='font-size:20px'>
        Thank you for considering participating in our study! <strong>We are researchers studying 
        software development practices and AI tool usage</strong>, and your insights are invaluable 
        to us.
        </p>
        
        <p style='font-size:20px'>
        <strong>📋 This survey consists of:</strong>
        </p>
        
        <p style='font-size:20px'>
        1. Work satisfaction and experience questions<br>
        2. AI tool usage questions<br>
        3. Self-efficacy assessment<br>
        4. Task estimation questions
        </p>
        
        <p style='font-size:20px'>
        ⌛ The survey will take approximately <strong>10–15 minutes</strong>.
        </p>
        
        <p style='font-size:20px'>
        🔒 Your responses will be kept fully anonymous and confidential.
        </p>
        """, unsafe_allow_html=True)
    
    if st.button("I am at least 18 years old and I agree to participate in this study."):
        next_page()


def work_satisfaction_page():
    """Display the work satisfaction questions page."""
    st.header("Work Satisfaction")
    st.markdown("""
     <p style='font-size:18px; font-weight: 600; margin-bottom: 2rem'>
     Rate how satisfied you are with the following aspects of your work as a developer.
     </p>
     """, unsafe_allow_html=True)
    
    # Load previous responses if they exist
    previous_responses = st.session_state['survey_responses'].get('satisfaction', {})
    
    responses = {}
    for idx, (key, question) in enumerate(SATISFACTION_QUESTIONS.items()):
        is_first = idx == 0
        
        # Use very bold font weight for first question label, normal for others
        font_weight = '400'
        st.markdown(f"<p style='font-size:18px; margin-bottom:0rem; font-weight:{font_weight};'>{question}</p>", 
                   unsafe_allow_html=True)
        
        # Get previous value or default to "Not selected"
        default_value = previous_responses.get(key, "Not selected")
        
        responses[key] = st.select_slider(
            label="",
            options=SATISFACTION_SLIDER_OPTIONS,
            value=default_value,
            key=f"satisfaction_{key}"
        )
    
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1, 4, 1])
    with b1:
        back_clicked = st.button("Back", key="satisfaction_back")
    with b3:
        next_clicked = st.button("Next", key="satisfaction_next")
    
    if back_clicked:
        # Save responses even when going back
        st.session_state['survey_responses']['satisfaction'] = responses
        previous_page()
    elif next_clicked:
        if all(v != "Not selected" for v in responses.values()):
            st.session_state['survey_responses']['satisfaction'] = responses
            next_page()
        else:
            st.error("Please fill out all fields before proceeding.")


def developer_experience_page():
    """Display the developer experience page."""
    st.header("Developer Experience")
    st.markdown("""
        <p style='font-size:18px; margin-bottom: 0.75rem;'>
        Tell us about your background and experience.
        </p>
        """, unsafe_allow_html=True)
    
    # Load previous responses if they exist
    previous_experience = st.session_state['survey_responses'].get('professional_experience', None)
    previous_occupation = st.session_state['survey_responses'].get('occupation_description', '')
    
    st.markdown("<p style='font-size:18px; font-weight:500; margin-bottom:0.5rem;'>How many years of professional development experience do you have?</p>", 
               unsafe_allow_html=True)
    
    # Set index based on previous response
    if previous_experience and previous_experience in EXPERIENCE_OPTIONS:
        default_index = EXPERIENCE_OPTIONS.index(previous_experience)
    else:
        default_index = None
    
    professional_experience = st.selectbox(
        label="",
        options=EXPERIENCE_OPTIONS,
        index=default_index,
        key="professional_experience"
    )
    
    st.divider()
    
    st.markdown("<p style='font-size:18px; font-weight:500; margin-bottom:0.5rem;'>Please briefly describe your current occupation.</p>", 
               unsafe_allow_html=True)
    occupation_description = st.text_area(
        label="",
        value=previous_occupation,
        key="occupation_description",
        height=100
    )
    
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    d1, d2, d3 = st.columns([1, 4, 1])
    with d1:
        dev_exp_back = st.button("Back", key="dev_exp_back")
    with d3:
        dev_exp_next = st.button("Next", key="dev_exp_next")
    
    if dev_exp_back:
        # Save responses even when going back
        if professional_experience:
            st.session_state['survey_responses']['professional_experience'] = professional_experience
        if occupation_description:
            st.session_state['survey_responses']['occupation_description'] = occupation_description
        previous_page()
    elif dev_exp_next:
        if professional_experience and occupation_description:
            st.session_state['survey_responses']['professional_experience'] = professional_experience
            st.session_state['survey_responses']['occupation_description'] = occupation_description
            next_page()
        else:
            st.error("Please fill out all fields before proceeding.")


def ai_tools_page():
    """Display the AI tools usage page."""
    st.header("AI Tool Usage")
    
    st.markdown("<p style='font-size:18px'><strong>How frequently do you use AI tools?</strong></p>", 
               unsafe_allow_html=True)
    
    # Load previous responses if they exist
    previous_frequency = st.session_state['survey_responses'].get('ai_frequency', {})
    previous_tools = st.session_state['survey_responses'].get('ai_tools_used', '')
    
    responses = {}
    for key, question in AI_FREQUENCY_QUESTIONS.items():
        default_value = previous_frequency.get(key, "Not selected")
        responses[key] = st.select_slider(
            label=f"**{question}**",
            options=FREQUENCY_OPTIONS,
            value=default_value,
            key=f"ai_freq_{key}"
        )
    
    st.divider()
    
    ai_tools_used = st.text_area(
        "**Which AI tools do you use regularly? (e.g., GitHub Copilot, ChatGPT, etc.)**",
        value=previous_tools,
        key="ai_tools_used"
    )
    
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    a1, a2, a3 = st.columns([1, 4, 1])
    with a1:
        ai_tools_back = st.button("Back", key="ai_tools_back")
    with a3:
        ai_tools_next = st.button("Next", key="ai_tools_next")
    
    if ai_tools_back:
        # Save responses even when going back
        st.session_state['survey_responses']['ai_frequency'] = responses
        if ai_tools_used:
            st.session_state['survey_responses']['ai_tools_used'] = ai_tools_used
        previous_page()
    elif ai_tools_next:
        if all(v != "Not selected" for v in responses.values()) and ai_tools_used:
            st.session_state['survey_responses']['ai_frequency'] = responses
            st.session_state['survey_responses']['ai_tools_used'] = ai_tools_used
            next_page()
        else:
            st.error("Please fill out all fields before proceeding.")


def self_efficacy_page():
    """Display the self-efficacy assessment page."""
    st.header("Self-Efficacy Assessment")
    
    st.markdown("""
        <p style='font-size:18px'>
        Please rate how true the following statements are for you.
        </p>
        """, unsafe_allow_html=True)
    
    # Load previous responses if they exist
    previous_efficacy = st.session_state['survey_responses'].get('self_efficacy', {})
    
    responses = {}
    for key, question in SELF_EFFICACY_QUESTIONS.items():
        default_value = previous_efficacy.get(key, "Not selected")
        responses[key] = st.select_slider(
            label=f"**{question}**",
            options=SELF_EFFICACY_OPTIONS,
            value=default_value,
            key=f"efficacy_{key}"
        )
    
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    e1, e2, e3 = st.columns([1, 4, 1])
    with e1:
        efficacy_back = st.button("Back", key="efficacy_back")
    with e3:
        efficacy_next = st.button("Next", key="efficacy_next")
    
    if efficacy_back:
        # Save responses even when going back
        st.session_state['survey_responses']['self_efficacy'] = responses
        previous_page()
    elif efficacy_next:
        if all(v != "Not selected" for v in responses.values()):
            st.session_state['survey_responses']['self_efficacy'] = responses
            next_page()
        else:
            st.error("Please fill out all fields before proceeding.")


def task_estimation_page():
    """Display the task estimation page."""
    st.header("Task Estimation")
    
    st.markdown("""
        <p style='font-size:18px'>
        Please estimate your time spent on coding tasks before and after using AI tools.
        </p>
        """, unsafe_allow_html=True)
    
    # Load previous responses if they exist
    previous_task_est = st.session_state['survey_responses'].get('task_estimation', {})
    
    hours_before = st.number_input(
        "**How many hours per week did you spend on coding tasks BEFORE using AI tools?**",
        min_value=0,
        max_value=168,
        step=1,
        value=previous_task_est.get('hours_before', 0),
        key="hours_before"
    )
    
    hours_after = st.number_input(
        "**How many hours per week do you spend on coding tasks AFTER using AI tools?**",
        min_value=0,
        max_value=168,
        step=1,
        value=previous_task_est.get('hours_after', 0),
        key="hours_after"
    )
    
    quality_change = st.select_slider(
        "**Has the quality of your work changed after using AI tools?**",
        options=QUALITY_CHANGE_OPTIONS,
        value=previous_task_est.get('quality_change', "Not selected"),
        key="quality_change"
    )
    
    additional_comments = st.text_area(
        "**Any additional comments about how AI tools have impacted your work? (Optional)**",
        value=previous_task_est.get('additional_comments', ''),
        key="additional_comments"
    )
    
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    t1, t2, t3 = st.columns([1, 4, 1])
    with t1:
        task_back = st.button("Back", key="task_back")
    with t3:
        task_submit = st.button("Submit", key="task_submit")
    
    if task_back:
        # Save responses even when going back
        st.session_state['survey_responses']['task_estimation'] = {
            'hours_before': hours_before,
            'hours_after': hours_after,
            'quality_change': quality_change,
            'additional_comments': additional_comments
        }
        previous_page()
    elif task_submit:
        if quality_change != "Not selected":
            st.session_state['survey_responses']['task_estimation'] = {
                'hours_before': hours_before,
                'hours_after': hours_after,
                'quality_change': quality_change,
                'additional_comments': additional_comments
            }
            next_page()
        else:
            st.error("Please answer all required questions before proceeding.")


def completion_page():
    """Display the survey completion page."""
    st.header("Thank You!")
    
    st.markdown("""
        <p style='font-size:20px'>
        Thank you for completing the survey! Your responses have been recorded.
        </p>
        
        <p style='font-size:18px'>
        Your insights will help us better understand how AI tools are impacting 
        software development practices.
        </p>
        """, unsafe_allow_html=True)
    
    st.success("✅ Survey completed successfully!")
    
    with st.expander("View your responses"):
        st.json(st.session_state['survey_responses'])

