"""
Survey pages package.
Organized into logical sections: pre-study, task, and post-PR.
"""

# Import from organized sections
from .pre_study import (
    consent_page,
    participant_id_page,
    developer_experience_page,
    self_efficacy_page,
    work_satisfaction_page,
    ai_tools_page,
    repository_assignment_page,
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
    code_quality_page,
    post_issue_questions_page,
    completion_page
)

from .post_exp1 import (
    ai_usage_page,
    tool_preference_page,
    post_self_efficacy_page,
    thank_you_page
)

__all__ = [
    # Pre-study pages
    'consent_page',
    'participant_id_page',
    'developer_experience_page',
    'self_efficacy_page',
    'work_satisfaction_page',
    'ai_tools_page',
    'repository_assignment_page',
    'code_experience_page',
    'pre_study_complete_page',
    
    # Task pages
    'issue_assignment_page',
    'time_estimation_page',
    'issue_completion_page',
    
    # Post-PR pages
    'ai_condition_questions_page',
    'code_quality_page',
    'post_issue_questions_page',
    'completion_page',
    'thank_you_page',

    # Post-Exp1 pages
    'ai_usage_page',
    'tool_preference_page',
    'post_self_efficacy_page'
]