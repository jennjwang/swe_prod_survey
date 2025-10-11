"""
Task execution pages package.
Contains all pages related to the actual task execution (issue assignment, time estimation, completion).
"""

from .issue_assignment import issue_assignment_page
from .time_estimation import time_estimation_page
from .issue_completion import issue_completion_page

__all__ = [
    'issue_assignment_page',
    'time_estimation_page',
    'issue_completion_page'
]
