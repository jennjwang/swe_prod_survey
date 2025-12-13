"""
Survey pages package.
Organized into logical sections: pre-study, task, and post-PR.
"""

# Import from organized sections
from .pre_study import (
    participant_id_page,
    ai_tools_page,
    repository_assignment_page,
    setup_checklist_page,
    code_experience_page,
    pre_study_complete_page
)

from .task import (
    issue_assignment_page,
    time_estimation_page,
    issue_completion_page
)

from .post_pr import (
    ai_condition_questions_page,
    post_issue_questions_page,
    post_issue_reflection_page,
    completion_page
)

from .pr_closed import (
    update_issue_page,
    collaboration_questions_page,
    engagement_questions_page,
    learning_outcomes_questions_page,
    pr_closed_thank_you_page
)

from .post_exp1 import (
    study_val_page,
    ai_usage_page,
    thank_you_page
)

from .post_exp2 import (
    end_of_study_thank_you_page,
    code_activities_value_page,
    final_thank_you_page
)

__all__ = [
    # Pre-study pages
    'participant_id_page',
    'ai_tools_page',
    'repository_assignment_page',
    'setup_checklist_page',
    'code_experience_page',
    'pre_study_complete_page',
    
    # Task pages
    'issue_assignment_page',
    'time_estimation_page',
    'issue_completion_page',
    
    # Post-PR pages
    'ai_condition_questions_page',
    'post_issue_questions_page',
    'post_issue_reflection_page',
    'completion_page',
    'thank_you_page',

    # PR closed pages
    'update_issue_page',
    'collaboration_questions_page',
    'engagement_questions_page',
    'learning_outcomes_questions_page',
    'pr_closed_thank_you_page',

    # Post-Exp1 pages
    'study_val_page',
    'ai_usage_page',

    # Post-Exp2 pages
    'end_of_study_thank_you_page',
    'code_activities_value_page',
    'final_thank_you_page',
]
