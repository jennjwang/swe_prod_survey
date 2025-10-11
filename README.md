# Developer Survey - Modular Structure

This directory contains a reorganized, modular version of the developer survey application.

## 📁 File Structure

```
survey/
├── dev_survey_modular.py    # Main application entry point
├── survey_pages.py           # All page components (consent, questions, completion)
├── survey_questions.py       # Question text and configuration data
├── styles.py                 # CSS styling for the application
└── README_MODULAR.md        # This file
```

## 🗂️ File Descriptions

### `dev_survey_modular.py`

**Purpose:** Main application file and entry point

- Initializes the Streamlit app
- Sets up session state
- Routes to different pages based on user progress
- Clean and minimal - only ~60 lines

**Key Functions:**

- `initialize_session_state()` - Sets up session variables
- `main()` - Application entry point with page routing

### `survey_pages.py`

**Purpose:** All page/screen components

- Contains all survey page functions
- Each page is a separate function
- Handles user interactions and navigation

**Pages Included:**

- `consent_page()` - Initial consent screen
- `work_satisfaction_page()` - Work satisfaction questions
- `ai_tools_page()` - AI tool usage questions
- `self_efficacy_page()` - Self-efficacy assessment
- `task_estimation_page()` - Task time estimation
- `completion_page()` - Thank you screen

**Helper Functions:**

- `next_page()` - Navigate forward
- `previous_page()` - Navigate backward

### `survey_questions.py`

**Purpose:** All question text and configuration data

- Centralized location for all survey questions
- Easy to update question text
- No code logic - just data

**Contains:**

- `SATISFACTION_QUESTIONS` - Work satisfaction questions
- `AI_FREQUENCY_QUESTIONS` - AI tool usage questions
- `SELF_EFFICACY_QUESTIONS` - Self-efficacy statements
- `TASK_ESTIMATION_QUESTIONS` - Time estimation questions
- All slider/selectbox options

### `styles.py`

**Purpose:** CSS styling

- All visual styling in one place
- Easy to update colors, fonts, spacing
- Separated from logic

**Styles:**

- Button styling
- Slider customization (blue theme)
- Layout and spacing
- Typography

## 🚀 How to Run

### Run the modular version:

```bash
streamlit run dev_survey_modular.py
```

### Run the original version:

```bash
streamlit run dev_survey.py
```

## ✨ Benefits of Modular Structure

### 1. **Easier to Read**

- Each file has a single responsibility
- Functions are organized logically
- Less scrolling to find what you need

### 2. **Easier to Edit**

- Want to change question text? → Edit `survey_questions.py`
- Want to change colors/styling? → Edit `styles.py`
- Want to modify page flow? → Edit `survey_pages.py`
- Want to add a new page? → Add function to `survey_pages.py`, update routing in `dev_survey_modular.py`

### 3. **Easier to Test**

- Each function can be tested independently
- Mock data is easier to create
- Debugging is more straightforward

### 4. **Easier to Collaborate**

- Multiple people can work on different files
- Less merge conflicts
- Clear ownership of components

### 5. **Reusability**

- Questions can be reused in other surveys
- Styling can be shared across projects
- Page components can be mixed and matched

## 📝 Making Changes

### To add a new question:

1. Add the question to `survey_questions.py`
2. Update the relevant page in `survey_pages.py`

### To add a new page:

1. Create a new function in `survey_pages.py`
2. Add the page to the routing dictionary in `dev_survey_modular.py`

### To change styling:

1. Edit the CSS in `styles.py`
2. Changes will apply to all pages automatically

### To change page order:

1. Update the routing dictionary in `dev_survey_modular.py`
