# Developer Productivity Survey Application

A Streamlit-based survey application for studying the impact of AI on developer productivity. Participants complete a multi-issue study where AI assistance is randomly assigned per issue (2 with AI, 2 without).

## 📁 File Structure

```
survey/
├── main.py                    # Main application entry point with page routing
├── pages/                     # Page components organized by survey section
│   ├── __init__.py           # Package initialization and exports
│   ├── pre_study/            # Pre-study survey pages (consent, demographics, etc.)
│   ├── task/                 # Task-related pages (issue assignment, time estimation)
│   ├── post_pr/              # Post-PR survey pages
│   └── post_exp1/            # Post-experiment pages
├── survey_data.py            # Database operations (Supabase integration)
├── survey_utils.py           # Utility functions (navigation, OpenAI client)
├── survey_components.py      # Reusable UI components
├── survey_questions.py       # Question text and configuration data
├── styles.py                 # CSS styling for the application
├── survey_pages.py           # Legacy page components
├── wake_app.py               # App wake-up automation script
├── WAKE_APP_SETUP.md         # Documentation for wake-up automation
├── requirements.txt          # Python dependencies
├── .devcontainer/            # Dev container configuration
├── .github/                  # GitHub workflows and configuration
└── .streamlit/               # Streamlit configuration
```

## 🗂️ Core Components

### `main.py`

**Purpose:** Main application file and entry point

- Initializes the Streamlit app with page configuration
- Sets up session state for tracking user progress
- Routes to different pages based on survey flow (pages 0-15)
- Clean routing with organized sections: Pre-study (0-6), Task (7-9), Post-PR (10-11), Post-Exp1 (12-13), Completion (14-15)

**Key Functions:**
- `initialize_session_state()` - Sets up session variables
- `main()` - Application entry point with page routing

### `pages/` Package

**Purpose:** All page/screen components organized by survey section

**Structure:**
- `pages/pre_study/` - Initial survey pages
  - Consent form
  - Participant email entry (email-based authentication)
  - AI tools experience (LLM and AI agent hours)
  - Repository assignment
  - Code experience questions
  - Pre-study completion

- `pages/task/` - Task execution pages
  - Issue assignment with AI condition acknowledgment
  - Time estimation
  - Issue completion & PR submission

- `pages/post_pr/` - Post-task survey pages
  - AI condition questions (for AI users)
  - Post-issue experience questions (NASA-TLX scales + audio/text input for time/effort)
  - Post-issue reflection (AI users only - code quality, work division, decision-making)
  - Completion page

- `pages/post_exp1/` - Final survey pages
  - Study validation (workflow comparison)
  - AI usage and perception
  - Thank you page

### `survey_data.py`

**Purpose:** Database operations and Supabase integration

- Provides Supabase client initialization with dev/prod mode support
- Handles all database interactions with error handling decorator (`@safe_db_operation`)
- Manages survey response storage and retrieval
- **AI Condition Assignment**: Randomly assigns AI usage per issue (ensures 2 with AI, 2 without per participant)
- **Participant Authentication**: Email-based participant identification (case-insensitive)
- Key functions:
  - `assign_issue_to_participant()` - Assigns issues with random AI condition balancing (ensures 2-2 split)
  - `check_participant_ai_condition()` - Checks AI flag for specific issues from repo-issues table
  - `save_post_issue_responses()` - Saves NASA-TLX and time/effort data
  - `save_post_issue_reflection()` - Saves AI reflection data (code quality, work division, decision-making)
  - `validate_participant_id()` - Case-insensitive email validation
  - `extract_repo_name()` - Helper function for consistent repository name extraction

### `survey_utils.py`

**Purpose:** Utility functions used across the application

**Key Functions:**
- `next_page()` - Navigate to the next survey page
- `previous_page()` - Navigate to the previous page
- `record_audio()` - Record and transcribe audio responses using OpenAI Whisper API
- OpenAI client initialization for AI-powered features

### `survey_components.py`

**Purpose:** Reusable UI components for consistent styling

**Components:**
- `page_header()` - Consistent page headers
- `question_label()` - Formatted question labels
- `slider_question()` - Slider input with custom styling (used for NASA-TLX scales)
- `text_input_question()` - Text input fields
- `navigation_buttons()` - Consistent navigation with validation
- Other shared UI elements

### `survey_questions.py`

**Purpose:** Centralized question text and configuration data

- All survey questions in one location
- Easy to update question text
- No code logic - just data
- Contains question sets for different survey sections

### `styles.py`

**Purpose:** CSS styling for the entire application

- Centralized styling definitions
- Button styling
- Slider customization
- Layout and spacing
- Typography
- Color theme

### `wake_app.py`

**Purpose:** Automated app wake-up script

- Keeps Streamlit app active
- Prevents cold starts
- See `WAKE_APP_SETUP.md` for setup instructions

## 🚀 How to Run

### Run the application:

```bash
streamlit run main.py
```

### Install dependencies:

```bash
pip install -r requirements.txt
```

## ✨ Benefits of This Structure

### 1. **Modular Organization**
- Pages are organized by survey section (pre-study, task, post-PR, post-experiment)
- Clear separation of concerns
- Easy to find and modify specific pages

### 2. **Easier to Edit**
- Want to change question text? → Edit `survey_questions.py`
- Want to change colors/styling? → Edit `styles.py`
- Want to modify a specific page? → Navigate to the appropriate `pages/` subdirectory
- Want to add database operations? → Edit `survey_data.py`
- Want to add utility functions? → Edit `survey_utils.py`

### 3. **Reusable Components**
- UI components in `survey_components.py` can be used across all pages
- Consistent look and feel throughout the application
- Reduces code duplication

### 4. **Scalable Architecture**
- Easy to add new survey sections
- Each section is independently maintainable
- Clear data layer separation

### 5. **Development Features**
- Dev container support for consistent development environment
- GitHub workflows for automation
- Mode switching (dev/prod) for testing

## 📝 Making Changes

### To add a new question:
1. Add the question to `survey_questions.py`
2. Update the relevant page in the appropriate `pages/` subdirectory

### To add a new page:
1. Create a new function in the appropriate `pages/` subdirectory
2. Export it from `pages/__init__.py`
3. Add the page to the routing dictionary in `main.py`
4. Update the page numbering accordingly

### To change styling:
1. Edit the CSS in `styles.py`
2. Changes will apply to all pages automatically

### To modify database operations:
1. Update functions in `survey_data.py`
2. Maintain separation between dev and prod environments

### To change page order:
1. Update the `page_routes` dictionary in `main.py`
2. Adjust page numbers as needed

## 🔧 Configuration

- **Streamlit config:** `.streamlit/config.toml`
- **Secrets:** Use Streamlit secrets management for:
  - `SUPABASE_URL` and `SUPABASE_KEY` (production)
  - `SUPABASE_DEV_URL` and `SUPABASE_DEV_KEY` (development)
  - `OPENAI_KEY` (for audio transcription)
  - `MODE` - Set to 'dev' or 'prod'

## 🎯 Key Features

### AI Condition Randomization
- Each participant completes 4 issues total
- AI usage is randomly assigned per issue (not per participant)
- Ensures balanced 2-2 split: 2 issues with AI, 2 without
- Participants explicitly acknowledge AI condition before starting each issue

### Email-Based Authentication
- Participant IDs are now email addresses (strings)
- Case-insensitive email matching for robustness
- No numeric conversion required

### Multi-Issue Workflow
1. Participant enters email → Pre-study survey (AI experience, code experience)
2. Issue 1 assigned → AI condition revealed & acknowledged → Time estimation → Work → Post-issue survey
3. Issue 2 assigned → AI condition revealed & acknowledged → Time estimation → Work → Post-issue survey
4. Issue 3 assigned → AI condition revealed & acknowledged → Time estimation → Work → Post-issue survey
5. Issue 4 assigned → AI condition revealed & acknowledged → Time estimation → Work → Post-issue survey
6. Post-experiment survey (workflow comparison, AI perception) → Completion

### Audio/Text Input Support
- Post-issue questions include flexible input options
- Participants can record audio responses (auto-transcribed via OpenAI Whisper API)
- Or type text responses directly
- Particularly useful for open-ended questions like "Where did you spend the most time or effort?"

## 📚 Additional Documentation

- See `WAKE_APP_SETUP.md` for information on setting up the app wake-up automation
- GitHub workflows are configured in `.github/workflows/`
- Dev container configuration is in `.devcontainer/`
