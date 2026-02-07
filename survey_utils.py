"""
Utility functions for the survey application.
"""

import io
import wave

import streamlit as st
import openai


# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=st.secrets.get('OPENAI_KEY', ''))


def next_page():
    """Navigate to the next page."""
    st.session_state['page'] += 1
    st.rerun()


def previous_page():
    """Navigate to the previous page."""
    st.session_state['page'] -= 1
    st.rerun()


def clear_form_cache_between_issues():
    """
    Clear form/widget state and app cache when transitioning between issues.
    Call this before st.rerun() after form submission so the next issue sees a fresh form.
    """
    form_keys = [
        'completion_choice',
        'specstory_upload',
        'screenrec_upload',
        'selected_update_pr_index',
    ]
    for key in form_keys:
        st.session_state.pop(key, None)
    try:
        st.cache_data.clear()
    except Exception:
        pass


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


def record_audio(question_key, min_duration=10, max_duration=600):
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


def save_and_navigate(direction: str, **responses):
    """
    Save responses to session state and navigate.
    
    Args:
        direction: 'next' or 'back'
        **responses: Key-value pairs to save to survey_responses
    """
    for key, value in responses.items():
        if value is not None:
            st.session_state['survey_responses'][key] = value
    
    if direction == 'next':
        next_page()
    elif direction == 'back':
        previous_page()
