"""
Data layer for database operations.
"""

from typing import Dict, Any, Optional
import streamlit as st
import functools
import traceback
from supabase import create_client


# Initialize Supabase client
def get_supabase_client():
    """Get initialized Supabase client based on mode."""
    if st.secrets['MODE'] == 'dev':
        return create_client(
            st.secrets['SUPABASE_DEV_URL'],
            st.secrets['SUPABASE_DEV_KEY'],
        )
    elif st.secrets['MODE'] == 'prod':
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"],
        )
    return None


supabase_client = get_supabase_client()


def extract_repo_name(repo_string: str) -> str:
    """
    Extract repository name from owner/repo format.

    Args:
        repo_string: Repository string (e.g., "owner/repo" or "repo")

    Returns:
        Repository name only (e.g., "repo")
    """
    if '/' in repo_string:
        return repo_string.split('/')[-1]
    return repo_string


def safe_db_operation(error_defaults=None, success_key='success'):
    """
    Decorator to handle Supabase connection checks and exception handling.
    
    Args:
        error_defaults (dict): Dictionary of default values to return on error.
                               'success' (or success_key) will be set to False,
                               and 'error' will be set to the exception message.
        success_key (str): The key to use for success status (default: 'success').
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not supabase_client:
                result = {success_key: False, 'error': 'Database client not initialized'}
                if error_defaults:
                    result.update(error_defaults)
                return result
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"❌ ERROR in {func.__name__}: {e}")
                traceback.print_exc()
                result = {success_key: False, 'error': f"Error in {func.__name__}: {str(e)}"}
                if error_defaults:
                    result.update(error_defaults)
                return result
        return wrapper
    return decorator


@safe_db_operation(error_defaults={'repository': None, 'url': None})
def get_repository_assignment(participant_id: str):
    """
    Get repository assignment for a participant.
    
    Args:
        participant_id: The participant's ID
        
    Returns:
        dict with 'success', 'repository' (formatted as name), 'url', and 'error' keys
    """
    # Normalize email to lowercase for case-insensitive matching
    participant_id_lower = participant_id.lower()

    # Query the database (case-insensitive)
    response = supabase_client.table('participant-repos').select('*').ilike('participant_id', participant_id_lower).execute()
    print(f"Query for participant_id='{participant_id}' (case-insensitive)")
    print(f"Response: {response}")
    
    if response.data and len(response.data) > 0:
        row = response.data[0]
        print(f"Row data: {row}")
        
        # Extract repository details (owner may be derived from URL)
        repository_name = row.get('repository_name')
        repository_url = row.get('repository_url') or row.get('repo_url')

        print(f"Repository name: {repository_name}")
        print(f"Repository URL: {repository_url}")

        if repository_name:
            # Return only the repository name (not owner/repo)
            return {
                'success': True,
                'repository': repository_name,
                'url': repository_url,
                'error': None
            }
        else:
            return {
                'success': False,
                'error': f"Repository information incomplete. Available columns: {list(row.keys())}",
                'repository': None,
                'url': None
            }
    else:
        # Try to get sample IDs for debugging
        all_records = supabase_client.table('participant-repos').select('participant_id').limit(5).execute()
        sample_ids = [r.get('participant_id') for r in all_records.data if all_records.data]
        print(f"Sample participant IDs in table: {sample_ids}")
        
        return {
            'success': False,
            'error': f"Email '{participant_id}' not found in the system.",
            'repository': None,
            'url': None
        }


def validate_participant_id(participant_id: str):
    """
    Validate that a participant ID (email) exists in the database.
    Email matching is case-insensitive.

    Args:
        participant_id: The participant's ID (email) to validate

    Returns:
        dict with 'valid' (bool), 'error' (str or None) keys
    """
    if not supabase_client:
        return {
            'valid': False,
            'error': 'Database client not initialized'
        }

    if not participant_id or not participant_id.strip():
        return {
            'valid': False,
            'error': 'Email cannot be empty'
        }

    try:
        # Normalize email to lowercase for case-insensitive matching
        participant_id_lower = participant_id.lower()

        # Check if participant ID exists in participant-repos table (case-insensitive)
        response = supabase_client.table('participant-repos').select('participant_id').ilike('participant_id', participant_id_lower).execute()
        
        if response.data and len(response.data) > 0:
            print(f"Participant ID '{participant_id}' validated successfully")
            return {
                'valid': True,
                'error': None
            }
        else:
            print(f"Participant ID '{participant_id}' not found in database")
            return {
                'valid': False,
                'error': f"Email '{participant_id}' not found in the system. Please check your email and try again."
            }
            
    except Exception as e:
        print(f"Error validating participant ID: {e}")
        traceback.print_exc()
        
        # Check if it's a type conversion error (invalid format for bigint)
        error_str = str(e)
        if 'invalid input syntax for type bigint' in error_str or '22P02' in error_str:
            return {
                'valid': False,
                'error': f"Email '{participant_id}' not found in the system. Please check your email and try again."
            }

        return {
            'valid': False,
            'error': f"Email '{participant_id}' not found in the system. Please check your email and try again."
        }


@safe_db_operation()
def save_survey_responses(participant_id: str, responses: dict):
    """
    Save survey responses to Supabase pre-study table.
    
    Args:
        participant_id: The participant's ID
        responses: Dictionary of all survey responses
        
    Returns:
        dict with 'success' and 'error' keys
    """
    # Flatten nested dictionaries into individual columns
    data = {
        'participant_id': participant_id,
        'assigned_repository': responses.get('assigned_repository'),
        'repository_url': responses.get('repository_url'),
        'forked_repository_url': responses.get('forked_repository_url'),
        'code_experience': responses.get('code_experience'),
        'checklist_completed': responses.get('checklist_completed'),
    }
    
    # Flatten ai_experience dict
    ai_experience = responses.get('ai_experience', {})
    data['ai_experience_llm_hours'] = ai_experience.get('llm_hours')
    data['ai_agent_experience_hours'] = ai_experience.get('agent_hours')

    print(f"Prepared data for participant {participant_id}: {data}")
    
    # Check if participant already has responses
    existing = supabase_client.table('pre-study').select('participant_id').eq('participant_id', participant_id).execute()
    
    if existing.data and len(existing.data) > 0:
        # Update existing record
        supabase_client.table('pre-study').update(data).eq('participant_id', participant_id).execute()
        print(f"Updated responses for participant: {participant_id}")
    else:
        # Insert new record
        supabase_client.table('pre-study').insert(data).execute()
        print(f"Inserted responses for participant: {participant_id}")
    
    return {
        'success': True,
        'error': None
    }


@safe_db_operation()
def mark_checklist_completed(participant_id: str):
    """
    Mark the setup checklist as completed for a participant in the pre-study table.
    Uses upsert to create the record if it doesn't exist.

    Args:
        participant_id: The participant's ID

    Returns:
        dict with 'success' and 'error' keys
    """
    if not participant_id:
        return {
            'success': False,
            'error': 'Participant ID is required to mark checklist completion'
        }

    upsert_data = {
        'participant_id': participant_id,
        'checklist_completed': True
    }

    # Use upsert to create or update the record
    supabase_client.table('pre-study')\
        .upsert(upsert_data, on_conflict='participant_id')\
        .execute()

    return {
        'success': True,
        'error': None
    }


@safe_db_operation(error_defaults={'progress': None})
def get_participant_progress(participant_id: str):
    """
    Get the progress status of a participant.
    
    Args:
        participant_id: The participant's ID
        
    Returns:
        dict with 'success', 'progress' (dict with status info), and 'error' keys
    """
    # Check pre-study completion
    pre_study = supabase_client.table('pre-study').select('*').eq('participant_id', participant_id).execute()
    
    # Check if issue assigned
    issue = supabase_client.table('repo-issues').select('*').eq('participant_id', participant_id).execute()
    
    # Check if issue is completed
    issue_completed = False
    survey_completed = False
    if issue.data and len(issue.data) > 0:
        issue_data = issue.data[0]
        is_completed_value = issue_data.get('is_completed')
        survey_completed_value = issue_data.get('survey_completed')
        # Only consider it completed if explicitly True
        issue_completed = is_completed_value is True
        survey_completed = survey_completed_value is True
    
    checklist_completed = False
    if pre_study.data and len(pre_study.data) > 0:
        checklist_completed = pre_study.data[0].get('checklist_completed') is True

    progress = {
        'pre_study_completed': len(pre_study.data) > 0 if pre_study.data else False,
        'issue_assigned': len(issue.data) > 0 if issue.data else False,
        'issue_completed': issue_completed,
        'survey_completed': survey_completed,
        'checklist_completed': checklist_completed,
        'pre_study_data': pre_study.data[0] if pre_study.data and len(pre_study.data) > 0 else None,
        'issue_data': issue.data[0] if issue.data and len(issue.data) > 0 else None
    }
    
    print(f"Progress for participant {participant_id}: {progress}")
    
    return {
        'success': True,
        'progress': progress,
        'error': None
    }


@safe_db_operation(error_defaults={'issue': None})
def get_random_unassigned_issue(repository: str):
    """
    Get a random unassigned issue from a repository (without assigning it yet).

    Args:
        repository: Repository name (e.g., "zed")

    Returns:
        dict with 'success', 'issue' (dict with url, id), and 'error' keys
    """
    # Get all unassigned issues for this repository (match by repository name only)
    print(f"Getting unassigned issues for repository: {repository}")
    response = supabase_client.table('repo-issues').select('*').eq('repository', repository).eq('is_assigned', False).execute()

    print(f"Found {len(response.data) if response.data else 0} unassigned issues for {repository}")
    if not response.data or len(response.data) == 0:
        return {
            'success': False,
            'error': f"No unassigned issues found for repository {repository}",
            'issue': None
        }
    
    # Randomly select one issue (but don't assign yet)
    import random
    selected_issue = random.choice(response.data)
    
    print(f"Retrieved issue {selected_issue['issue_id']} (not yet assigned)")
    
    return {
        'success': True,
        'issue': {
            'url': selected_issue['issue_url'],
            'id': selected_issue['issue_id'],
            'repository': selected_issue['repository']
        },
        'error': None
    }


@safe_db_operation()
def assign_issue_to_participant(participant_id: str, issue_id: int):
    """
    Assign a specific issue to a participant by updating the database.
    
    Args:
        participant_id: The participant's ID
        issue_id: The issue ID to assign
        
    Returns:
        dict with 'success' and 'error' keys
    """
    print(f"=== STARTING ISSUE ASSIGNMENT ===")

    # Check how many issues this participant has and their AI conditions
    existing_issues = supabase_client.table('repo-issues').select('using_ai').eq('participant_id', participant_id).execute()

    ai_count = sum(1 for issue in (existing_issues.data or []) if issue.get('using_ai') is True)
    no_ai_count = sum(1 for issue in (existing_issues.data or []) if issue.get('using_ai') is False)
    total_count = len(existing_issues.data) if existing_issues.data else 0

    print(f"Participant {participant_id} current issues: {total_count} total, {ai_count} with AI, {no_ai_count} without AI")

    # Determine AI condition for this issue
    # Target: 2 with AI, 2 without AI (4 total)
    import random
    if ai_count >= 2:
        # Already has 2 with AI, must assign without AI
        using_ai = False
    elif no_ai_count >= 2:
        # Already has 2 without AI, must assign with AI
        using_ai = True
    else:
        # Can go either way, randomly assign
        using_ai = random.choice([True, False])

    print(f"Assigning issue with using_ai = {using_ai}")

    # Update the issue to mark as assigned with timestamp
    from datetime import datetime, timezone

    update_data = {
        'is_assigned': True,
        'participant_id': participant_id,
        'accepted_on': datetime.now(timezone.utc).isoformat(),  # Current UTC timestamp
        'using_ai': using_ai  # Randomly assigned AI condition
    }
    
    print(f"Update data: {update_data}")
    print(f"Updating table 'repo-issues' where issue_id = {issue_id}")
    
    result = supabase_client.table('repo-issues').update(update_data).eq('issue_id', issue_id).execute()
    
    print(f"Update result: {result}")
    
    if result.data and len(result.data) > 0:
        print(f"✅ Successfully assigned issue {issue_id} to participant {participant_id}")
        print(f"Updated row: {result.data[0]}")
        return {
            'success': True,
            'error': None,
            'using_ai': using_ai  # Return the AI condition
        }
    else:
        print(f"⚠️ Update returned empty data - issue may not exist or RLS policy blocked the update")
        print(f"TROUBLESHOOTING:")
        print(f"1. Check if issue_id {issue_id} exists in repo-issues table")
        print(f"2. Check if participant_id {participant_id} exists in participant-repos table")
        print(f"3. Check RLS policy on repo-issues table - it may be blocking the update")
        print(f"4. Try disabling RLS temporarily to test: ALTER TABLE \"repo-issues\" DISABLE ROW LEVEL SECURITY;")
        return {
            'success': False,
            'error': f"Issue {issue_id} not found or RLS policy blocked the update. Check server logs."
        }


@safe_db_operation()
def assign_all_issues_to_participant(participant_id: str, repository: str):
    """
    Assign all 4 issues to a participant at once with randomized order and AI conditions.

    Args:
        participant_id: The participant's ID
        repository_name: The repository name to get issues from

    Returns:
        dict with 'success', 'error', and 'issues' keys
    """
    print(f"=== ASSIGNING ALL 4 ISSUES TO PARTICIPANT ===")
    print(f"Participant: {participant_id}")
    print(f"Repository: {repository}")

    # Get 4 random unassigned issues from the repository
    result = supabase_client.table('repo-issues')\
        .select('*')\
        .eq('repository', repository)\
        .eq('is_assigned', False)\
        .limit(4)\
        .execute()

    if not result.data or len(result.data) < 4:
        error_msg = f"Not enough unassigned issues available. Found {len(result.data) if result.data else 0}, need 4."
        print(f"⚠️ {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'issues': []
        }

    issues = result.data
    print(f"Found {len(issues)} unassigned issues")

    # Randomly shuffle the issues to randomize order
    import random
    random.shuffle(issues)

    # Randomly assign AI conditions (2 with AI, 2 without)
    ai_conditions = [True, True, False, False]
    random.shuffle(ai_conditions)

    # Assign all 4 issues with sequence numbers and AI conditions
    from datetime import datetime, timezone
    assigned_issues = []

    for idx, issue in enumerate(issues):
        issue_id = issue['issue_id']
        sequence = idx + 1  # 1, 2, 3, 4
        using_ai = ai_conditions[idx]

        update_data = {
            'is_assigned': True,
            'participant_id': participant_id,
            'accepted_on': datetime.now(timezone.utc).isoformat(),
            'using_ai': using_ai,
            'issue_sequence': sequence
        }

        print(f"Assigning issue {issue_id}: sequence={sequence}, using_ai={using_ai}")

        update_result = supabase_client.table('repo-issues')\
            .update(update_data)\
            .eq('issue_id', issue_id)\
            .execute()

        if update_result.data and len(update_result.data) > 0:
            assigned_issues.append({
                **issue,
                'issue_sequence': sequence,
                'using_ai': using_ai
            })
        else:
            print(f"⚠️ Failed to assign issue {issue_id}")

    if len(assigned_issues) == 4:
        print(f"✅ Successfully assigned all 4 issues to participant {participant_id}")
        return {
            'success': True,
            'error': None,
            'issues': assigned_issues
        }
    else:
        return {
            'success': False,
            'error': f"Only {len(assigned_issues)} of 4 issues were successfully assigned",
            'issues': assigned_issues
        }


@safe_db_operation()
def check_all_issues_assigned(participant_id: str):
    """
    Check if a participant has all 4 issues assigned.

    Args:
        participant_id: The participant's ID

    Returns:
        dict with 'success', 'all_assigned' (bool), and 'count' keys
    """
    result = supabase_client.table('repo-issues')\
        .select('issue_id', count='exact')\
        .eq('participant_id', participant_id)\
        .execute()

    count = result.count if hasattr(result, 'count') else (len(result.data) if result.data else 0)

    print(f"Participant {participant_id} has {count} issues assigned")

    return {
        'success': True,
        'all_assigned': count == 4,
        'count': count
    }


@safe_db_operation()
def get_next_issue_in_sequence(participant_id: str):
    """
    Get the next incomplete issue in sequence for a participant.

    Args:
        participant_id: The participant's ID

    Returns:
        dict with 'success', 'issue', 'sequence', 'total_completed' keys
    """
    # Get all issues for participant ordered by sequence
    result = supabase_client.table('repo-issues')\
        .select('*')\
        .eq('participant_id', participant_id)\
        .order('issue_sequence')\
        .execute()

    if not result.data:
        return {
            'success': False,
            'error': 'No issues found for participant',
            'issue': None,
            'sequence': None,
            'total_completed': 0
        }

    issues = result.data
    total_completed = sum(1 for issue in issues if issue.get('is_completed', False))

    # Find first incomplete issue
    next_issue = None
    for issue in issues:
        if not issue.get('is_completed', False):
            next_issue = issue
            break

    if next_issue:
        sequence = next_issue.get('issue_sequence', 0)
        print(f"Next issue for participant {participant_id}: sequence {sequence}, issue_id {next_issue['issue_id']}")
        return {
            'success': True,
            'issue': next_issue,
            'sequence': sequence,
            'total_completed': total_completed,
            'error': None
        }
    else:
        # All issues complete
        print(f"All issues complete for participant {participant_id}")
        return {
            'success': True,
            'issue': None,
            'sequence': None,
            'total_completed': total_completed,
            'error': None
        }


@safe_db_operation()
def request_different_issue(participant_id: str, current_issue_id: int, justification: str):
    """
    Request a different issue. Participant can only do this once.
    Swaps current issue with another unassigned issue from the same repository.

    Args:
        participant_id: The participant's ID
        current_issue_id: The current issue ID to swap out
        justification: Reason for requesting a different issue

    Returns:
        dict with 'success', 'new_issue', 'already_used', and 'error' keys
    """
    print(f"=== ISSUE SWAP REQUEST ===")
    print(f"Participant: {participant_id}")
    print(f"Current Issue: {current_issue_id}")
    print(f"Justification: {justification}")

    # Check if participant has already used their swap
    result = supabase_client.table('pre-study')\
        .select('issue_swap_used')\
        .eq('participant_id', participant_id)\
        .execute()

    if result.data and len(result.data) > 0:
        already_used = result.data[0].get('issue_swap_used', False)
        if already_used:
            print("Participant has already used their issue swap")
            return {
                'success': False,
                'already_used': True,
                'new_issue': None,
                'error': 'You have already used your one-time issue swap.'
            }

    # Get current issue details
    current_issue_result = supabase_client.table('repo-issues')\
        .select('*')\
        .eq('issue_id', current_issue_id)\
        .execute()

    if not current_issue_result.data:
        return {
            'success': False,
            'already_used': False,
            'new_issue': None,
            'error': 'Current issue not found'
        }

    current_issue = current_issue_result.data[0]
    repository = current_issue['repository']
    sequence = current_issue['issue_sequence']
    using_ai = current_issue['using_ai']

    # Find a new unassigned issue from the same repository
    new_issue_result = supabase_client.table('repo-issues')\
        .select('*')\
        .eq('repository', repository)\
        .eq('is_assigned', False)\
        .limit(1)\
        .execute()

    if not new_issue_result.data:
        return {
            'success': False,
            'already_used': False,
            'new_issue': None,
            'error': 'No available issues to swap with. Please contact the study administrator.'
        }

    new_issue = new_issue_result.data[0]
    new_issue_id = new_issue['issue_id']

    # Unassign current issue (keep justification for tracking)
    supabase_client.table('repo-issues').update({
        'is_assigned': False,
        'participant_id': None,
        'accepted_on': None,
        'using_ai': None,
        'issue_sequence': None,
        'swap_justification': justification  # Track why it was swapped
    }).eq('issue_id', current_issue_id).execute()

    # Assign new issue with same sequence and AI condition
    from datetime import datetime, timezone
    supabase_client.table('repo-issues').update({
        'is_assigned': True,
        'participant_id': participant_id,
        'accepted_on': datetime.now(timezone.utc).isoformat(),
        'using_ai': using_ai,
        'issue_sequence': sequence
    }).eq('issue_id', new_issue_id).execute()

    # Mark swap as used in pre-study table
    supabase_client.table('pre-study').update({
        'issue_swap_used': True
    }).eq('participant_id', participant_id).execute()

    print(f"✅ Issue swap successful: {current_issue_id} -> {new_issue_id}")

    return {
        'success': True,
        'already_used': False,
        'new_issue': new_issue,
        'error': None
    }


@safe_db_operation()
def update_issue_time_estimate(issue_id: int, time_estimate: str):
    """
    Update the time estimate for an assigned issue.
    
    Args:
        issue_id: The issue's ID
        time_estimate: The participant's time estimate (e.g., "<30 minutes", "1-2 hours")
        
    Returns:
        dict with 'success' and 'error' keys
    """
    print(f"=== UPDATING TIME ESTIMATE ===")
    print(f"Issue ID: {issue_id}")
    print(f"Time Estimate: {time_estimate}")
    
    # Update the participant_estimate field
    update_data = {
        'participant_estimate': time_estimate
    }
    
    result = supabase_client.table('repo-issues').update(update_data).eq('issue_id', issue_id).execute()
    
    print(f"Update result: {result}")
    
    if result.data and len(result.data) > 0:
        print(f"✅ Successfully updated time estimate for issue {issue_id}")
        return {
            'success': True,
            'error': None
        }
    else:
        print(f"⚠️ Update returned empty data - issue may not exist")
        return {
            'success': False,
            'error': f"Issue {issue_id} not found"
        }


@safe_db_operation()
def mark_issue_completed(issue_id: int, pr_url: str = None):
    """
    Mark an issue as completed with timestamp and PR URL.
    
    Args:
        issue_id: The issue's ID
        pr_url: The pull request URL (optional)
        
    Returns:
        dict with 'success' and 'error' keys
    """
    from datetime import datetime, timezone
    
    print(f"=== MARKING ISSUE AS COMPLETED ===")
    print(f"Issue ID: {issue_id}")
    print(f"PR URL: {pr_url}")
    
    # Update is_completed, completed_on, and pr_url fields
    update_data = {
        'is_completed': True,
        'completed_on': datetime.now(timezone.utc).isoformat()
    }
    
    # Add PR URL if provided
    if pr_url:
        update_data['pr_url'] = pr_url
    
    result = supabase_client.table('repo-issues').update(update_data).eq('issue_id', issue_id).execute()
    
    print(f"Update result: {result}")
    
    if result.data and len(result.data) > 0:
        print(f"✅ Successfully marked issue {issue_id} as completed")
        return {
            'success': True,
            'error': None
        }
    else:
        print(f"⚠️ Update returned empty data - issue may not exist")
        return {
            'success': False,
            'error': f"Issue {issue_id} not found"
        }


@safe_db_operation(error_defaults={'using_ai': False})
def check_participant_ai_condition(participant_id: str, issue_id: int):
    """
    Check if AI is enabled for a specific issue from repo-issues table.

    Args:
        participant_id: The participant's ID
        issue_id: The issue's ID

    Returns:
        dict with 'success', 'using_ai' (boolean), and 'error' keys
    """
    print(f"=== CHECKING AI CONDITION ===")
    print(f"Participant ID: {participant_id}, Issue ID: {issue_id}")

    result = supabase_client.table('repo-issues').select('using_ai').eq('issue_id', issue_id).execute()

    print(f"AI condition result: {result}")

    if result.data and len(result.data) > 0:
        using_ai = result.data[0].get('using_ai', False)
        print(f"✅ Issue {issue_id} using AI: {using_ai}")
        return {
            'success': True,
            'using_ai': using_ai,
            'error': None
        }
    else:
        print(f"⚠️ No issue data found for issue {issue_id}")
        return {
            'success': False,
            'error': f"No issue data found for issue {issue_id}",
            'using_ai': False
        }


@safe_db_operation()
def save_ai_condition_responses(participant_id: str, issue_id: int, ai_speed_multiplier: float, code_review_approach: str):
    """
    Save AI condition responses to the post-PR table.
    
    Args:
        participant_id: The participant's ID
        issue_id: The issue's ID
        ai_speed_multiplier: Speed multiplier (e.g., 2.0 for 2x faster, 0.5 for 2x slower)
        code_review_approach: Selected code review approach
        
    Returns:
        dict with 'success' and 'error' keys
    """
    print(f"=== SAVING AI CONDITION RESPONSES ===")
    print(f"Participant ID: {participant_id}")
    print(f"Issue ID: {issue_id}")
    print(f"Speed Multiplier: {ai_speed_multiplier}")
    print(f"Code Review Approach: {code_review_approach}")

    # Insert into post-PR table
    data = {
        'participant_id': participant_id,
        'issue_id': issue_id,
        'ai_speed_multiplier': ai_speed_multiplier,
        'ai_code_review_approach': code_review_approach
    }
    
    # Use upsert to update if participant_id already exists, insert if not
    result = supabase_client.table('post-PR').upsert(data, on_conflict='participant_id').execute()
    
    print(f"Upsert result: {result}")
    print(f"Data being upserted: {data}")
    
    if result.data and len(result.data) > 0:
        print(f"✅ Successfully saved AI condition responses for participant {participant_id}")
        return {
            'success': True,
            'error': None
        }
    else:
        print(f"⚠️ Upsert returned empty data")
        print(f"TROUBLESHOOTING RLS POLICY:")
        print(f"1. Check if RLS is enabled on 'post-PR' table")
        print(f"2. Check if there's an INSERT/UPDATE policy for 'post-PR' table")
        print(f"3. Try disabling RLS temporarily: ALTER TABLE \"post-PR\" DISABLE ROW LEVEL SECURITY;")
        print(f"4. Or create a policy: CREATE POLICY \"Allow upsert\" ON \"post-PR\" FOR ALL WITH CHECK (true);")
        return {
            'success': False,
            'error': f"Failed to save AI condition responses - RLS policy blocked upsert"
        }


@safe_db_operation(error_defaults={'completed': False})
def check_pr_survey_completion(participant_id: str, issue_id: int):
    """
    Check if a participant has already completed PR survey responses for a specific issue.
    Checks repo-issues for survey_completed flag, using_ai, and post-PR for nasa_tlx_1.

    Args:
        participant_id: The participant's ID
        issue_id: The issue's ID

    Returns:
        dict with 'success', 'completed', 'using_ai', 'nasa_tlx_1', and 'error' keys
    """
    # Check actual survey completion status and AI condition from repo-issues table
    repo_result = supabase_client.table('repo-issues').select('survey_completed, using_ai').eq('participant_id', participant_id).eq('issue_id', int(issue_id)).execute()

    completed = False
    using_ai = False
    if repo_result.data and len(repo_result.data) > 0:
        completed = repo_result.data[0].get('survey_completed') is True
        using_ai = repo_result.data[0].get('using_ai') is True

    # Also check nasa_tlx_1 from post-PR table for routing purposes
    post_pr_result = supabase_client.table('post-PR').select('nasa_tlx_1').eq('participant_id', participant_id).eq('issue_id', int(issue_id)).execute()

    nasa_tlx_1_value = None
    if post_pr_result.data and len(post_pr_result.data) > 0:
        nasa_tlx_1_value = post_pr_result.data[0].get('nasa_tlx_1')

    print(f"PR survey completion check for participant {participant_id}, issue {issue_id}: completed={completed}, using_ai={using_ai}, nasa_tlx_1={nasa_tlx_1_value}")

    return {
        'success': True,
        'completed': completed,
        'using_ai': using_ai,
        'nasa_tlx_1': nasa_tlx_1_value,
        'error': None
    }


@safe_db_operation()
def save_pr_survey_completion_status(participant_id: str, issue_id: int, completed: bool):
    """
    Save the PR survey completion status to track participant progress.
    Updates the repo-issues table to mark survey as completed for a specific issue.
    
    Args:
        participant_id: The participant's ID
        issue_id: The issue's ID
        completed: Whether the participant has completed PR survey
        
    Returns:
        dict with 'success' and 'error' keys
    """
    from datetime import datetime, timezone
    
    # Update the participant's assigned issue with survey completion status
    data = {
        'survey_completed': completed
    }
    
    # Add timestamp if completed
    if completed:
        data['survey_completed_at'] = datetime.now(timezone.utc).isoformat()
    
    # Update by both participant_id and issue_id for precision
    result = supabase_client.table('repo-issues').update(data).eq('participant_id', (participant_id)).eq('issue_id', int(issue_id)).execute()
    
    if result.data and len(result.data) > 0:
        print(f"✅ Updated repo-issues: survey_completed={completed} for participant {participant_id}, issue {issue_id}")
        return {
            'success': True,
            'error': None
        }
    else:
        print(f"⚠️ No rows updated in repo-issues for participant {participant_id}, issue {issue_id}")
        return {
            'success': False,
            'error': 'No matching issue found for participant'
        }


@safe_db_operation()
def save_post_issue_responses(participant_id: str, issue_id: int, responses: dict):
    """
    Save post-issue experience responses to the database.
    
    Args:
        participant_id: The participant's ID
        issue_id: The issue's ID
        responses: Dictionary of all responses (NASA-TLX and code quality)
        
    Returns:
        dict with 'success' and 'error' keys
    """
    print(f"=== SAVING POST-ISSUE RESPONSES ===")
    print(f"Participant ID: {participant_id}")
    print(f"Issue ID: {issue_id}")
    print(f"Responses: {responses}")
    
    # Prepare data for insertion
    data = {
        'participant_id': participant_id,
        'issue_id': issue_id,
        **responses  # Spread all response fields
    }

    # Check if record already exists, then update or insert accordingly
    existing_record = supabase_client.table('post-PR').select('participant_id').eq('participant_id', participant_id).eq('issue_id', issue_id).execute()

    if existing_record.data and len(existing_record.data) > 0:
        # Record exists, update it
        print(f"Updating existing record for participant {participant_id}, issue {issue_id}")
        result = supabase_client.table('post-PR').update(data).eq('participant_id', participant_id).eq('issue_id', issue_id).execute()
    else:
        # Record doesn't exist, insert new one
        print(f"Inserting new record for participant {participant_id}, issue {issue_id}")
        result = supabase_client.table('post-PR').insert(data).execute()
    
    print(f"Database operation result: {result}")
    print(f"Data being saved: {data}")
    
    if result.data and len(result.data) > 0:
        print(f"✅ Successfully saved post-issue responses for participant {participant_id}")
        return {
            'success': True,
            'error': None
        }
    else:
        print(f"⚠️ Insert returned empty data")
        print(f"TROUBLESHOOTING RLS POLICY:")
        print(f"1. Check if RLS is enabled on 'post-PR' table")
        print(f"2. Check if there's an INSERT policy for 'post-PR' table")
        print(f"3. Try disabling RLS temporarily: ALTER TABLE \"post-PR\" DISABLE ROW LEVEL SECURITY;")
        print(f"4. Or create a policy: CREATE POLICY \"Allow insert\" ON \"post-PR\" FOR INSERT WITH CHECK (true);")
        return {
            'success': False,
            'error': f"Failed to save post-issue responses - RLS policy blocked insert"
        }


@safe_db_operation()
def save_post_issue_reflection(participant_id: str, issue_id: int, responses: dict):
    """
    Save post-issue reflection responses to the database.

    Args:
        participant_id: The participant's ID
        issue_id: The issue's ID
        responses: Dictionary of reflection responses (satisfaction, confidence, difficulty, challenge)

    Returns:
        dict with 'success' and 'error' keys
    """
    print(f"=== SAVING POST-ISSUE REFLECTION ===")
    print(f"Participant ID: {participant_id}")
    print(f"Issue ID: {issue_id}")
    print(f"Responses: {responses}")

    # Update the existing post-PR record with reflection data
    data = responses

    # Check if record exists
    existing_record = supabase_client.table('post-PR').select('participant_id').eq('participant_id', participant_id).eq('issue_id', issue_id).execute()

    if existing_record.data and len(existing_record.data) > 0:
        # Record exists, update it with reflection data
        print(f"Updating existing record with reflection data for participant {participant_id}, issue {issue_id}")
        result = supabase_client.table('post-PR').update(data).eq('participant_id', participant_id).eq('issue_id', issue_id).execute()

        print(f"Database operation result: {result}")

        if result.data and len(result.data) > 0:
            print(f"✅ Successfully saved post-issue reflection for participant {participant_id}")
            return {
                'success': True,
                'error': None
            }
        else:
            print(f"⚠️ Update returned empty data")
            return {
                'success': False,
                'error': f"Failed to save post-issue reflection"
            }
    else:
        print(f"⚠️ No existing post-PR record found for participant {participant_id}, issue {issue_id}")
        return {
            'success': False,
            'error': "No existing post-PR record found. Please complete post-issue questions first."
        }


@safe_db_operation()
def save_post_exp1_responses(participant_id: str, responses: dict):
    """
    Save post-experience 1 responses (AttrakDiff, AI Perception, Post-task Self-Efficacy) to the database.
    
    Args:
        participant_id: The participant's ID
        responses: Dictionary of all responses
        
    Returns:
        dict with 'success' and 'error' keys
    """
    print(f"=== SAVING POST-EXP1 RESPONSES ===")
    print(f"Participant ID: {participant_id}")
    print(f"Responses: {responses}")

    # Prepare data for insertion
    data = {
        'participant_id': participant_id,
        **responses  # Spread all response fields
    }

    # Try different strategies to handle RLS policy issues
    result = None

    # Strategy 1: Try upsert first
    try:
        result = supabase_client.table('post-exp1').upsert(data, on_conflict='participant_id').execute()
        print(f"✅ Upsert successful")
    except Exception as upsert_error:
        print(f"⚠️ Upsert failed: {upsert_error}")

        # Strategy 2: Try insert only
        try:
            result = supabase_client.table('post-exp1').insert(data).execute()
            print(f"✅ Insert successful")
        except Exception as insert_error:
            print(f"⚠️ Insert failed: {insert_error}")

            # Strategy 3: Try update only (in case record exists)
            try:
                result = supabase_client.table('post-exp1').update(data).eq('participant_id', participant_id).execute()
                print(f"✅ Update successful")
            except Exception as update_error:
                print(f"❌ All strategies failed. Update error: {update_error}")
                raise upsert_error  # Re-raise the original error
    
    print(f"Upsert result: {result}")
    print(f"Data being upserted: {data}")
    
    if result.data and len(result.data) > 0:
        print(f"✅ Successfully saved post-exp1 responses for participant {participant_id}")
        return {
            'success': True,
            'error': None
        }
    else:
        print(f"⚠️ Upsert returned empty data")
        print(f"TROUBLESHOOTING RLS POLICY:")
        print(f"1. Check if RLS is enabled on 'post-exp1' table")
        print(f"2. Check if there's an INSERT/UPDATE policy for 'post-exp1' table")
        print(f"3. Try disabling RLS temporarily: ALTER TABLE \"post-exp1\" DISABLE ROW LEVEL SECURITY;")
        print(f"4. Or create a policy: CREATE POLICY \"Allow upsert\" ON \"post-exp1\" FOR ALL WITH CHECK (true);")
        return {
            'success': False,
            'error': f"Failed to save post-exp1 responses - RLS policy blocked upsert"
        }


def assign_random_issue(participant_id: str, repository: str):
    """
    Randomly assign an unassigned issue to a participant from their repository.
    (Combined function that gets and assigns in one step)

    Args:
        participant_id: The participant's ID
        repository: Repository in format "owner/repository"

    Returns:
        dict with 'success', 'issue' (dict with url, id), and 'error' keys
    """
    # First get a random unassigned issue
    result = get_random_unassigned_issue(repository)

    if not result['success']:
        return result

    # Then assign it to the participant
    issue = result['issue']
    assign_result = assign_issue_to_participant(participant_id, issue['id'])

    if not assign_result['success']:
        return {
            'success': False,
            'error': assign_result['error'],
            'issue': None
        }

    return {
        'success': True,
        'issue': issue,
        'error': None
    }


@safe_db_operation(error_defaults={'issue': None})
def get_issue_needing_survey(participant_id: str):
    """
    Get an issue that is completed but hasn't had its survey finished yet.

    Args:
        participant_id: The participant's ID

    Returns:
        dict with 'success', 'issue' (issue data or None), 'using_ai', 'nasa_tlx_1', and 'error' keys
    """
    # Find issues where is_completed=True but survey_completed is not True
    result = supabase_client.table('repo-issues')\
        .select('*')\
        .eq('participant_id', participant_id)\
        .eq('is_completed', True)\
        .execute()

    if result.data:
        for issue in result.data:
            if issue.get('survey_completed') is not True:
                issue_id = issue['issue_id']
                using_ai = issue.get('using_ai') is True

                # Check nasa_tlx_1 from post-PR table
                post_pr_result = supabase_client.table('post-PR').select('nasa_tlx_1').eq('participant_id', participant_id).eq('issue_id', int(issue_id)).execute()
                nasa_tlx_1 = None
                if post_pr_result.data and len(post_pr_result.data) > 0:
                    nasa_tlx_1 = post_pr_result.data[0].get('nasa_tlx_1')

                print(f"Found issue needing survey: {issue_id}, using_ai={using_ai}, nasa_tlx_1={nasa_tlx_1}")
                return {
                    'success': True,
                    'issue': issue,
                    'using_ai': using_ai,
                    'nasa_tlx_1': nasa_tlx_1,
                    'error': None
                }

    return {
        'success': True,
        'issue': None,
        'using_ai': False,
        'nasa_tlx_1': None,
        'error': None
    }


@safe_db_operation(error_defaults={'has_more_issues': False, 'completed_count': 0, 'total_count': 0})
def check_participant_has_more_issues(participant_id: str):
    """
    Check if a participant has more uncompleted assigned issues.

    Args:
        participant_id: The participant's ID

    Returns:
        dict with 'success', 'has_more_issues' (boolean), 'completed_count', 'total_count', and 'error' keys
    """
    print(f"=== CHECKING FOR MORE ISSUES ===")
    print(f"Participant ID: {participant_id}")

    # Get all issues assigned to this participant
    all_issues = supabase_client.table('repo-issues').select('*').eq('participant_id', participant_id).execute()

    if not all_issues.data:
        print(f"No issues found for participant {participant_id}")
        return {
            'success': True,
            'has_more_issues': False,
            'completed_count': 0,
            'total_count': 0,
            'error': None
        }

    # Count completed vs total issues
    total_count = len(all_issues.data)
    completed_count = sum(1 for issue in all_issues.data if issue.get('is_completed') is True)

    has_more = completed_count < total_count

    print(f"✅ Participant {participant_id}: {completed_count}/{total_count} issues completed")
    print(f"Has more issues: {has_more}")

    return {
        'success': True,
        'has_more_issues': has_more,
        'completed_count': completed_count,
        'total_count': total_count,
        'error': None
    }
