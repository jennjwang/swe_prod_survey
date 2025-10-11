"""
Individual page components for the developer survey.
"""

import io
import wave
import streamlit as st
import openai
from supabase import create_client
from survey_questions import (
    SATISFACTION_QUESTIONS,
    SATISFACTION_SLIDER_OPTIONS,
    EXPERIENCE_OPTIONS,
    SELF_EFFICACY_QUESTIONS,
    SELF_EFFICACY_OPTIONS,
    AI_EXPERIENCE_QUESTIONS,
    AI_HOURS_OPTIONS,
    TASK_ESTIMATION_QUESTIONS,
    QUALITY_CHANGE_OPTIONS
)

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=st.secrets.get('OPENAI_KEY', ''))

# Initialize Supabase client
if st.secrets['MODE'] == 'dev':
    supabase_client = create_client(
        st.secrets['SUPABASE_DEV_URL'],
        st.secrets['SUPABASE_DEV_KEY'],
    )
elif st.secrets['MODE'] == 'prod':
    supabase_client = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )
else:
    supabase_client = None



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
        <p style='font-size:18px; font-weight: 600; margin-bottom: 2rem'>
        Tell us about your background and experience.
        </p>
        """, unsafe_allow_html=True)
    
    # Load previous responses if they exist
    previous_experience = st.session_state['survey_responses'].get('professional_experience', None)
    previous_occupation = st.session_state['survey_responses'].get('occupation_description', '')
    
    st.markdown("<p style='font-size:18px; font-weight:400; margin-bottom:0.5rem;'>How many years of professional development experience do you have?</p>", 
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
    
    st.markdown("<p style='font-size:18px; font-weight:400; margin-bottom:0.5rem;'>Please briefly describe your current occupation.</p>", 
               unsafe_allow_html=True)
    occupation_description = st.text_area(
        label="",
        value=previous_occupation,
        key="occupation_description",
        height=100,
        placeholder="1-2 sentences to describe your work."
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
    """Display the AI tools experience page."""
    st.header("AI Tool Experience")
    
    st.markdown("""
        <p style='font-size:18px; font-weight: 600; margin-bottom: 2rem'>
        Tell us about your experience with AI tools.
        </p>
        """, unsafe_allow_html=True)
    
    # Load previous responses if they exist
    previous_experience = st.session_state['survey_responses'].get('ai_experience', {})
    
    responses = {}
    for idx, (key, question) in enumerate(AI_EXPERIENCE_QUESTIONS.items()):
        st.markdown(f"<p style='font-size:18px; font-weight:400; margin-bottom:0.5rem;'>{question}</p>", 
                   unsafe_allow_html=True)
        
        # Get previous value or default to None
        default_value = previous_experience.get(key, None)
        if default_value and default_value in AI_HOURS_OPTIONS:
            default_index = AI_HOURS_OPTIONS.index(default_value)
        else:
            default_index = None
        
        responses[key] = st.selectbox(
            label="",
            options=AI_HOURS_OPTIONS,
            index=default_index,
            key=f"ai_exp_{key}"
        )
        
        # Add divider between questions (but not after the last one)
        if idx < len(AI_EXPERIENCE_QUESTIONS) - 1:
            st.divider()
    
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    a1, a2, a3 = st.columns([1, 4, 1])
    with a1:
        ai_tools_back = st.button("Back", key="ai_tools_back")
    with a3:
        ai_tools_next = st.button("Next", key="ai_tools_next")
    
    if ai_tools_back:
        # Save responses even when going back
        st.session_state['survey_responses']['ai_experience'] = responses
        previous_page()
    elif ai_tools_next:
        if all(v != "Not selected" for v in responses.values()):
            st.session_state['survey_responses']['ai_experience'] = responses
            next_page()
        else:
            st.error("Please fill out all fields before proceeding.")


def self_efficacy_page():
    """Display the self-efficacy assessment page."""
    st.header("Self-Efficacy Assessment")
    
    st.markdown("""
        <p style='font-size:18px; font-weight: 600; margin-bottom: 2rem'>
        Please rate how confident you are that you can perform each of the following tasks effectively.
        </p>
        """, unsafe_allow_html=True)
    
    # Load previous responses if they exist
    previous_efficacy = st.session_state['survey_responses'].get('self_efficacy', {})
    
    responses = {}
    for key, question in SELF_EFFICACY_QUESTIONS.items():
        st.markdown(f"<p style='font-size:18px; margin-bottom:0rem; font-weight:400;'>{question}</p>", 
                   unsafe_allow_html=True)
        default_value = previous_efficacy.get(key, "Not selected")
        responses[key] = st.select_slider(
            label="",
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
    """Display the repository assignment page."""
    st.header("Repository Assignment")
    
    st.markdown("""
        <p style='font-size:18px; font-weight: 600; margin-bottom: 2rem'>
        You will be assigned a repository to work on for this study.
        </p>
        """, unsafe_allow_html=True)
    
    # Load previous responses if they exist
    previous_participant_id = st.session_state['survey_responses'].get('participant_id', '')
    previous_repo = st.session_state['survey_responses'].get('assigned_repository', None)
    
    st.markdown("<p style='font-size:18px; font-weight:400; margin-bottom:0.5rem;'>Please enter your Participant ID:</p>", 
               unsafe_allow_html=True)
    participant_id = st.text_input(
        label="",
        value=previous_participant_id,
        key="participant_id_input",
        placeholder="Enter your participant ID"
    )
    
    st.divider()
    
    # Show assigned repository from database
    assigned_repo = None
    if previous_repo:
        assigned_repo = previous_repo
        st.success(f"You have been assigned repository: **{assigned_repo}**")
    else:
        if participant_id:
            try:
                # Query all columns to see what's in the table
                response = supabase_client.table('participant-repos').select('*').eq('participant_id', participant_id).execute()
                print(f"Query for participant_id='{participant_id}'")
                print(f"Response: {response}")
                
                if response.data and len(response.data) > 0:
                    # Get repository info from response
                    row = response.data[0]
                    print(f"Row data: {row}")
                    
                    # Extract repository details from new schema
                    owner = row.get('repository_owner')
                    repository_name = row.get('repository_name')
                    repository_url = row.get('repository_url')
                    
                    print(f"Owner: {owner}")
                    print(f"Repository name: {repository_name}")
                    print(f"Repository URL: {repository_url}")
                    
                    if owner and repository_name:
                        assigned_repo = f"{owner}/{repository_name}"
                        st.session_state['survey_responses']['assigned_repository'] = assigned_repo
                        st.session_state['survey_responses']['repository_url'] = repository_url
                        st.success(f"You have been assigned repository: **{assigned_repo}**")
                    else:
                        st.error(f"Repository information incomplete. Available columns: {list(row.keys())}")
                        assigned_repo = None
                else:
                    # Try to get all records to debug
                    all_records = supabase_client.table('participant-repos').select('participant_id').limit(5).execute()
                    print(f"Sample participant IDs in table: {[r.get('participant_id') for r in all_records.data if all_records.data]}")
                    st.error(f"⚠️ Participant ID '{participant_id}' not found in the system. Please check your ID and try again.")
                    st.info("Note: Participant IDs are case-sensitive. Please ensure you entered it exactly as provided.")
                    assigned_repo = None
            except Exception as e:
                st.error(f"Error retrieving repository assignment: {str(e)}")
                print(f"Exception: {e}")
                import traceback
                traceback.print_exc()
                assigned_repo = None
        else:
            st.warning("Please enter your Participant ID to receive your repository assignment.")
    
    # Show fork instructions if repository is assigned
    if assigned_repo:
        # Get the repository URL from session state
        repo_url = st.session_state['survey_responses'].get('repository_url', f"https://github.com/{assigned_repo}")
        
        st.divider()
        st.markdown("""
            <p style='font-size:20px; font-weight: 600; margin-top: 1rem; margin-bottom: 1rem'>
            Next Steps:
            </p>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <p style='font-size:18px; margin-bottom: 0.5rem'>
            1. Go to <a href="{repo_url}" target="_blank" style="color: #0066cc;">{repo_url}</a>
            </p>
            <p style='font-size:18px; margin-bottom: 0.5rem'>
            2. Click the <strong>"Fork"</strong> button in the top-right corner
            </p>
            <p style='font-size:18px; margin-bottom: 0.5rem'>
            3. Create the fork in your anonymous GitHub account
            </p>
            <p style='font-size:18px; margin-bottom: 1rem'>
            4. Copy and paste the URL of your forked repository below
            </p>
            """, unsafe_allow_html=True)
        
        # Load previous forked repo URL if exists
        previous_forked_url = st.session_state['survey_responses'].get('forked_repository_url', '')
        
        st.markdown("<p style='font-size:18px; font-weight:400; margin-bottom:0.5rem;'>Enter your forked repository URL:</p>", 
                   unsafe_allow_html=True)
        forked_repo_url = st.text_input(
            label="",
            value=previous_forked_url,
            key="forked_repo_url_input",
            placeholder="https://github.com/YOUR_USERNAME/repository-name"
        )
    else:
        forked_repo_url = None
    
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    t1, t2, t3 = st.columns([1, 4, 1])
    with t1:
        task_back = st.button("Back", key="task_back")
    with t3:
        task_next = st.button("Next", key="task_next")
    
    if task_back:
        # Save responses even when going back
        if participant_id:
            st.session_state['survey_responses']['participant_id'] = participant_id
        if assigned_repo:
            st.session_state['survey_responses']['assigned_repository'] = assigned_repo
        if forked_repo_url:
            st.session_state['survey_responses']['forked_repository_url'] = forked_repo_url
        previous_page()
    elif task_next:
        if participant_id and assigned_repo and forked_repo_url:
            st.session_state['survey_responses']['participant_id'] = participant_id
            st.session_state['survey_responses']['assigned_repository'] = assigned_repo
            st.session_state['survey_responses']['forked_repository_url'] = forked_repo_url
            next_page()
        elif not participant_id:
            st.error("Please enter your Participant ID to proceed.")
        elif not assigned_repo:
            st.error("Please wait for your repository assignment to load.")
        elif not forked_repo_url:
            st.error("Please enter the URL of your forked repository to proceed.")


def code_experience_page():
    """Display the code experience question page."""
    st.header("Code Experience")
    
    st.markdown("""
        <p style='font-size:18px; font-weight: 600; margin-bottom: 2rem'>
        Tell us about your experience with the assigned repository.
        </p>
        """, unsafe_allow_html=True)
    
    # Get assigned repository info for context
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', 'N/A')
    
    if assigned_repo != 'N/A':
        st.info(f"**Assigned Repository:** {assigned_repo}")
        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Load previous code experience response if exists
    previous_code_exp = st.session_state['survey_responses'].get('code_experience', None)
    
    st.markdown("<p style='font-size:18px; font-weight:400; margin-bottom:0.5rem;'>How many lines of code, approximately, have you personally written or modified in this codebase?</p>", 
               unsafe_allow_html=True)
    
    CODE_EXPERIENCE_OPTIONS = [
        "Fewer than 100",
        "100–1,000",
        "1,001–10,000",
        "10,001–50,000",
        "More than 50,000"
    ]
    
    # Set index based on previous response
    if previous_code_exp and previous_code_exp in CODE_EXPERIENCE_OPTIONS:
        default_code_index = CODE_EXPERIENCE_OPTIONS.index(previous_code_exp)
    else:
        default_code_index = None
    
    code_experience = st.selectbox(
        label="",
        options=CODE_EXPERIENCE_OPTIONS,
        index=default_code_index,
        key="code_experience_select"
    )
    
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        code_exp_back = st.button("Back", key="code_exp_back")
    with c3:
        code_exp_next = st.button("Next", key="code_exp_next")
    
    if code_exp_back:
        # Save response even when going back
        if code_experience:
            st.session_state['survey_responses']['code_experience'] = code_experience
        previous_page()
    elif code_exp_next:
        if code_experience:
            st.session_state['survey_responses']['code_experience'] = code_experience
            next_page()
        else:
            st.error("Please select your code experience level to proceed.")


def completion_page():
    """Display the survey completion page."""
    st.header("Thank You!")
    
    st.markdown("""
        <p style='font-size:20px'>
        Thank you for completing the survey! Your responses have been recorded.
        </p>
        """, unsafe_allow_html=True)
    
    st.success("✅ Survey completed successfully!")
    
    # Display assigned repository
    participant_id = st.session_state['survey_responses'].get('participant_id', 'N/A')
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', 'N/A')
    forked_repo_url = st.session_state['survey_responses'].get('forked_repository_url', 'N/A')
    code_experience = st.session_state['survey_responses'].get('code_experience', 'N/A')
    
    st.markdown("---")
    st.markdown("""
        <p style='font-size:18px; font-weight: 600; margin-top: 2rem; margin-bottom: 1rem'>
        Your Assignment Details:
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <p style='font-size:18px'>
        <strong>Participant ID:</strong> {participant_id}<br>
        <strong>Assigned Repository:</strong> {assigned_repo}<br>
        <strong>Your Forked Repository:</strong> <a href="{forked_repo_url}" target="_blank">{forked_repo_url}</a><br>
        <strong>Code Experience:</strong> {code_experience}
        </p>
        """, unsafe_allow_html=True)
    
    st.info("📝 Please save these details for the next phase of the study. You will be working on your forked repository.")
    
    with st.expander("View all your responses"):
        st.json(st.session_state['survey_responses'])

