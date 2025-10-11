"""
Survey pages package.
Each page is now a separate module for better organization.
"""

from .consent import consent_page
from .developer_experience import developer_experience_page
from .self_efficacy import self_efficacy_page
from .work_satisfaction import work_satisfaction_page
from .ai_tools import ai_tools_page
from .repository_assignment import repository_assignment_page
from .code_experience import code_experience_page
from .completion import completion_page

__all__ = [
    'consent_page',
    'developer_experience_page',
    'self_efficacy_page',
    'work_satisfaction_page',
    'ai_tools_page',
    'repository_assignment_page',
    'code_experience_page',
    'completion_page'
]

