# Survey Pages Organization

The survey pages have been refactored and organized into three logical sections for better maintainability and clarity.

## Directory Structure

```
survey/pages/
├── __init__.py                 # Main imports and exports
├── pre_study/                  # Pre-study survey pages
│   ├── __init__.py
│   ├── consent.py
│   ├── participant_id.py
│   ├── developer_experience.py
│   ├── self_efficacy.py
│   ├── work_satisfaction.py
│   ├── ai_tools.py
│   ├── repository_assignment.py
│   ├── code_experience.py
│   └── pre_study_complete.py
├── task/                       # Task execution pages
│   ├── __init__.py
│   ├── issue_assignment.py
│   ├── time_estimation.py
│   └── issue_completion.py
└── post_pr/                    # Post-PR survey pages
    ├── __init__.py
    ├── ai_condition_questions.py
    ├── post_issue_questions.py
    └── completion.py
```

## Page Flow

### Pre-Study Section (Pages 0-8)

Participants complete these pages before starting their assigned task:

1. **Consent** (Page 0) - Consent form
2. **Participant ID** (Page 1) - Participant ID entry and validation
3. **Developer Experience** (Page 2) - Professional development experience
4. **Self-Efficacy** (Page 3) - Self-efficacy questions
5. **Work Satisfaction** (Page 4) - Work satisfaction questions
6. **AI Tools** (Page 5) - AI tools experience
7. **Repository Assignment** (Page 6) - Repository assignment
8. **Code Experience** (Page 7) - Code experience questions
9. **Pre-Study Complete** (Page 8) - Pre-study completion confirmation

### Task Section (Pages 9-11)

Participants complete these pages during task execution:

1. **Issue Assignment** (Page 9) - Random issue assignment
2. **Time Estimation** (Page 10) - Time estimation for the task
3. **Issue Completion** (Page 11) - Issue completion and PR submission

### Post-PR Section (Pages 12-14)

Participants complete these pages after submitting their PR:

1. **AI Condition Questions** (Page 12) - AI-specific questions (AI users only)
2. **Post-Issue Questions** (Page 13) - NASA-TLX and code quality questions (all users)
3. **Completion** (Page 14) - Final completion page

## Benefits of This Organization

### 1. **Logical Grouping**

- Pages are grouped by survey phase
- Easy to understand the flow
- Clear separation of concerns

### 2. **Maintainability**

- Easier to find and modify specific pages
- Reduced cognitive load when working on specific sections
- Better code organization

### 3. **Scalability**

- Easy to add new pages to specific sections
- Clear structure for future enhancements
- Modular design supports team collaboration

### 4. **Documentation**

- Self-documenting structure
- Clear comments in routing code
- Easy to understand page flow

## Import Structure

Each section has its own `__init__.py` file that exports the relevant pages:

```python
# pre_study/__init__.py
from .consent import consent_page
from .participant_id import participant_id_page
# ... etc

# task/__init__.py
from .issue_assignment import issue_assignment_page
# ... etc

# post_pr/__init__.py
from .ai_condition_questions import ai_condition_questions_page
# ... etc
```

The main `pages/__init__.py` imports from all sections and provides a unified interface.

## Usage

The refactored structure maintains backward compatibility. All existing imports continue to work:

```python
from pages import consent_page, issue_assignment_page, completion_page
```

The main application (`dev_survey_modular.py`) has been updated with clear comments showing the page flow and organization.
