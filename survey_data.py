"""
Data layer for database operations.
"""

import streamlit as st
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


def get_repository_assignment(participant_id: str):
    """
    Get repository assignment for a participant.
    
    Args:
        participant_id: The participant's ID
        
    Returns:
        dict with 'success', 'repository' (formatted as owner/name), 'url', and 'error' keys
    """
    if not supabase_client:
        return {
            'success': False,
            'error': 'Database client not initialized',
            'repository': None,
            'url': None
        }
    
    try:
        # Query the database
        response = supabase_client.table('participant-repos').select('*').eq('participant_id', participant_id).execute()
        print(f"Query for participant_id='{participant_id}'")
        print(f"Response: {response}")
        
        if response.data and len(response.data) > 0:
            row = response.data[0]
            print(f"Row data: {row}")
            
            # Extract repository details
            owner = row.get('repository_owner')
            repository_name = row.get('repository_name')
            repository_url = row.get('repository_url')
            
            print(f"Owner: {owner}")
            print(f"Repository name: {repository_name}")
            print(f"Repository URL: {repository_url}")
            
            if owner and repository_name:
                return {
                    'success': True,
                    'repository': f"{owner}/{repository_name}",
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
                'error': f"Participant ID '{participant_id}' not found in the system.",
                'repository': None,
                'url': None
            }
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error retrieving repository assignment: {str(e)}",
            'repository': None,
            'url': None
        }


def validate_participant_id(participant_id: str):
    """
    Validate that a participant ID exists in the database.
    
    Args:
        participant_id: The participant's ID to validate
        
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
            'error': 'Participant ID cannot be empty'
        }
    
    try:
        # Check if participant ID exists in participant-repos table
        response = supabase_client.table('participant-repos').select('participant_id').eq('participant_id', participant_id).execute()
        
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
                'error': f"Participant ID '{participant_id}' not found in the system. Please check your ID and try again."
            }
            
    except Exception as e:
        print(f"Error validating participant ID: {e}")
        import traceback
        traceback.print_exc()
        
        # Check if it's a type conversion error (invalid format for bigint)
        error_str = str(e)
        if 'invalid input syntax for type bigint' in error_str or '22P02' in error_str:
            return {
                'valid': False,
                'error': f"Participant ID '{participant_id}' not found in the system. Please check your ID and try again."
            }
        
        return {
            'valid': False,
            'error': f"Participant ID '{participant_id}' not found in the system. Please check your ID and try again."
        }


def save_survey_responses(participant_id: str, responses: dict):
    """
    Save survey responses to Supabase pre-study table.
    
    Args:
        participant_id: The participant's ID
        responses: Dictionary of all survey responses
        
    Returns:
        dict with 'success' and 'error' keys
    """
    if not supabase_client:
        return {
            'success': False,
            'error': 'Database client not initialized'
        }
    
    try:
        # Flatten nested dictionaries into individual columns
        data = {
            'participant_id': participant_id,
            'professional_experience': responses.get('professional_experience'),
            'occupation_description': responses.get('occupation_description'),
            'assigned_repository': responses.get('assigned_repository'),
            'repository_url': responses.get('repository_url'),
            'forked_repository_url': responses.get('forked_repository_url'),
            'code_experience': responses.get('code_experience'),
        }
        
        # Flatten self_efficacy dict
        self_efficacy = responses.get('self_efficacy', {})
        data['self_efficacy_comprehension'] = self_efficacy.get('comprehension')
        data['self_efficacy_design'] = self_efficacy.get('design')
        data['self_efficacy_implementation'] = self_efficacy.get('implementation')
        data['self_efficacy_debugging'] = self_efficacy.get('debugging')
        data['self_efficacy_testing'] = self_efficacy.get('testing')
        data['self_efficacy_cooperation'] = self_efficacy.get('cooperation')
        
        # Flatten satisfaction dict
        satisfaction = responses.get('satisfaction', {})
        data['satisfaction_abilities_use'] = satisfaction.get('abilities_use')
        data['satisfaction_community_recognition'] = satisfaction.get('community_recognition')
        data['satisfaction_work_alone'] = satisfaction.get('work_alone')
        data['satisfaction_freedom_judgment'] = satisfaction.get('freedom_judgment')
        data['satisfaction_own_methods'] = satisfaction.get('own_methods')
        data['satisfaction_accomplishment'] = satisfaction.get('accomplishment')
        data['satisfaction_learning'] = satisfaction.get('learning')
        data['satisfaction_praise'] = satisfaction.get('praise')
        
        # Flatten ai_experience dict
        ai_experience = responses.get('ai_experience', {})
        data['ai_experience_llm_hours'] = ai_experience.get('llm_hours')
        data['ai_experience_cursor_hours'] = ai_experience.get('cursor_hours')
        data['ai_experience_ai_agents_hours'] = ai_experience.get('ai_agents_hours')
        
        print(f"Prepared data for participant {participant_id}: {data}")
        
        # Check if participant already has responses
        existing = supabase_client.table('pre-study').select('participant_id').eq('participant_id', participant_id).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update existing record
            result = supabase_client.table('pre-study').update(data).eq('participant_id', participant_id).execute()
            print(f"Updated responses for participant: {participant_id}")
        else:
            # Insert new record
            result = supabase_client.table('pre-study').insert(data).execute()
            print(f"Inserted responses for participant: {participant_id}")
        
        return {
            'success': True,
            'error': None
        }
        
    except Exception as e:
        print(f"Error saving survey responses: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error saving responses: {str(e)}"
        }


def get_participant_progress(participant_id: str):
    """
    Get the progress status of a participant.
    
    Args:
        participant_id: The participant's ID
        
    Returns:
        dict with 'success', 'progress' (dict with status info), and 'error' keys
    """
    if not supabase_client:
        return {
            'success': False,
            'error': 'Database client not initialized',
            'progress': None
        }
    
    try:
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
            print(f"DEBUG: Raw is_completed value: {is_completed_value} (type: {type(is_completed_value)})")
            print(f"DEBUG: Raw survey_completed value: {survey_completed_value} (type: {type(survey_completed_value)})")
            # Only consider it completed if explicitly True
            issue_completed = is_completed_value is True
            survey_completed = survey_completed_value is True
        
        progress = {
            'pre_study_completed': len(pre_study.data) > 0 if pre_study.data else False,
            'issue_assigned': len(issue.data) > 0 if issue.data else False,
            'issue_completed': issue_completed,
            'survey_completed': survey_completed,
            'pre_study_data': pre_study.data[0] if pre_study.data and len(pre_study.data) > 0 else None,
            'issue_data': issue.data[0] if issue.data and len(issue.data) > 0 else None
        }
        
        print(f"Progress for participant {participant_id}: {progress}")
        
        return {
            'success': True,
            'progress': progress,
            'error': None
        }
        
    except Exception as e:
        print(f"Error getting participant progress: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error getting progress: {str(e)}",
            'progress': None
        }


def get_random_unassigned_issue(repository: str):
    """
    Get a random unassigned issue from a repository (without assigning it yet).
    
    Args:
        repository: Repository in format "owner/repository"
        
    Returns:
        dict with 'success', 'issue' (dict with url, id), and 'error' keys
    """
    if not supabase_client:
        return {
            'success': False,
            'error': 'Database client not initialized',
            'issue': None
        }
    
    try:
        # Parse repository
        if '/' not in repository:
            return {
                'success': False,
                'error': 'Invalid repository format',
                'issue': None
            }
        
        owner, repo_name = repository.split('/', 1)
        
        # Get all unassigned issues for this repository
        response = supabase_client.table('repo-issues').select('*').eq('owner', owner).eq('repository', repo_name).eq('is_assigned', False).execute()
        
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
                'owner': selected_issue['owner'],
                'repository': selected_issue['repository']
            },
            'error': None
        }
        
    except Exception as e:
        print(f"Error getting random issue: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error getting issue: {str(e)}",
            'issue': None
        }


def assign_issue_to_participant(participant_id: str, issue_id: int):
    """
    Assign a specific issue to a participant by updating the database.
    
    Args:
        participant_id: The participant's ID
        issue_id: The issue ID to assign
        
    Returns:
        dict with 'success' and 'error' keys
    """
    if not supabase_client:
        print("ERROR: Database client not initialized")
        return {
            'success': False,
            'error': 'Database client not initialized'
        }
    
    try:
        print(f"=== STARTING ISSUE ASSIGNMENT ===")
        print(f"Participant ID: {participant_id} (type: {type(participant_id)})")
        print(f"Issue ID: {issue_id} (type: {type(issue_id)})")
        
        # Convert participant_id to int (bigint in database)
        try:
            participant_id_int = int(participant_id)
            print(f"Converted participant_id to int: {participant_id_int}")
        except (ValueError, TypeError):
            print(f"ERROR: Could not convert participant_id '{participant_id}' to integer")
            return {
                'success': False,
                'error': f"Invalid participant ID format: {participant_id}"
            }
        
        # Update the issue to mark as assigned with timestamp
        from datetime import datetime, timezone
        
        update_data = {
            'is_assigned': True,
            'participant_id': participant_id_int,  # Use integer
            'accepted_on': datetime.now(timezone.utc).isoformat()  # Current UTC timestamp
        }
        
        print(f"Update data: {update_data}")
        print(f"Updating table 'repo-issues' where issue_id = {issue_id}")
        
        result = supabase_client.table('repo-issues').update(update_data).eq('issue_id', issue_id).execute()
        
        print(f"Update result: {result}")
        
        if result.data and len(result.data) > 0:
            print(f"✅ Successfully assigned issue {issue_id} to participant {participant_id_int}")
            print(f"Updated row: {result.data[0]}")
            return {
                'success': True,
                'error': None
            }
        else:
            print(f"⚠️ Update returned empty data - issue may not exist or RLS policy blocked the update")
            print(f"TROUBLESHOOTING:")
            print(f"1. Check if issue_id {issue_id} exists in repo-issues table")
            print(f"2. Check if participant_id {participant_id_int} exists in participant-repos table")
            print(f"3. Check RLS policy on repo-issues table - it may be blocking the update")
            print(f"4. Try disabling RLS temporarily to test: ALTER TABLE \"repo-issues\" DISABLE ROW LEVEL SECURITY;")
            return {
                'success': False,
                'error': f"Issue {issue_id} not found or RLS policy blocked the update. Check server logs."
            }
        
    except Exception as e:
        print(f"❌ ERROR assigning issue: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error assigning issue: {str(e)}"
        }


def update_issue_time_estimate(issue_id: int, time_estimate: str):
    """
    Update the time estimate for an assigned issue.
    
    Args:
        issue_id: The issue's ID
        time_estimate: The participant's time estimate (e.g., "<30 minutes", "1-2 hours")
        
    Returns:
        dict with 'success' and 'error' keys
    """
    if not supabase_client:
        return {
            'success': False,
            'error': "Database connection not available"
        }
    
    try:
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
        
    except Exception as e:
        print(f"❌ ERROR updating time estimate: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error updating time estimate: {str(e)}"
        }


def mark_issue_completed(issue_id: int, pr_url: str = None):
    """
    Mark an issue as completed with timestamp and PR URL.
    
    Args:
        issue_id: The issue's ID
        pr_url: The pull request URL (optional)
        
    Returns:
        dict with 'success' and 'error' keys
    """
    if not supabase_client:
        return {
            'success': False,
            'error': "Database connection not available"
        }
    
    try:
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
        
    except Exception as e:
        print(f"❌ ERROR marking issue as completed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error marking issue as completed: {str(e)}"
        }


def check_participant_ai_condition(participant_id: str):
    """
    Check if participant is in AI condition.
    
    Args:
        participant_id: The participant's ID
        
    Returns:
        dict with 'success', 'using_ai' (boolean), and 'error' keys
    """
    if not supabase_client:
        return {
            'success': False,
            'error': "Database connection not available",
            'using_ai': False
        }
    
    try:
        print(f"=== CHECKING AI CONDITION ===")
        print(f"Participant ID: {participant_id}")
        
        result = supabase_client.table('participant-condition').select('using_AI').eq('participant_id', participant_id).execute()
        
        print(f"AI condition result: {result}")
        
        if result.data and len(result.data) > 0:
            using_ai = result.data[0].get('using_AI', False)
            print(f"✅ Participant {participant_id} using AI: {using_ai}")
            return {
                'success': True,
                'using_ai': using_ai,
                'error': None
            }
        else:
            print(f"⚠️ No AI condition data found for participant {participant_id}")
            return {
                'success': False,
                'error': f"No AI condition data found for participant {participant_id}",
                'using_ai': False
            }
        
    except Exception as e:
        print(f"❌ ERROR checking AI condition: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error checking AI condition: {str(e)}",
            'using_ai': False
        }


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
    if not supabase_client:
        return {
            'success': False,
            'error': "Database connection not available"
        }
    
    try:
        print(f"=== SAVING AI CONDITION RESPONSES ===")
        print(f"Participant ID: {participant_id}")
        print(f"Issue ID: {issue_id}")
        print(f"Speed Multiplier: {ai_speed_multiplier}")
        print(f"Code Review Approach: {code_review_approach}")
        
        # Insert into post-PR table
        data = {
            'participant_id': int(participant_id),
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
        
    except Exception as e:
        print(f"❌ ERROR saving AI condition responses: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error saving AI condition responses: {str(e)}"
        }


def check_pr_survey_completion(participant_id: str):
    """
    Check if a participant has already completed PR survey responses for their assigned issue.
    
    Args:
        participant_id: The participant's ID
        
    Returns:
        dict with 'success', 'completed' (boolean), and 'error' keys
    """
    if not supabase_client:
        return {
            'success': False,
            'completed': False,
            'error': 'Database client not initialized'
        }
    
    try:
        # Check if participant's assigned issue has survey_completed = true
        result = supabase_client.table('repo-issues').select('survey_completed').eq('participant_id', int(participant_id)).execute()
        
        completed = False
        if result.data and len(result.data) > 0:
            survey_completed_value = result.data[0].get('survey_completed')
            completed = survey_completed_value is True
        
        print(f"PR survey completion check for participant {participant_id}: {completed}")
        
        return {
            'success': True,
            'completed': completed,
            'error': None
        }
        
    except Exception as e:
        print(f"Error checking PR survey completion: {e}")
        return {
            'success': False,
            'completed': False,
            'error': f"Error checking PR survey completion: {str(e)}"
        }


def save_pr_survey_completion_status(participant_id: str, completed: bool):
    """
    Save the PR survey completion status to track participant progress.
    
    Args:
        participant_id: The participant's ID
        completed: Whether the participant has completed PR survey
        
    Returns:
        dict with 'success' and 'error' keys
    """
    if not supabase_client:
        return {
            'success': False,
            'error': 'Database client not initialized'
        }
    
    try:
        # Update the participant's assigned issue with survey completion status
        data = {
            'survey_completed': completed,
            'survey_completed_at': 'now()' if completed else None
        }
        
        result = supabase_client.table('repo-issues').update(data).eq('participant_id', int(participant_id)).execute()
        
        print(f"Updated PR survey completion status for participant {participant_id}: {completed}")
        
        return {
            'success': True,
            'error': None
        }
        
    except Exception as e:
        print(f"Error saving PR survey completion status: {e}")
        return {
            'success': False,
            'error': f"Error saving PR survey completion status: {str(e)}"
        }


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
    if not supabase_client:
        return {
            'success': False,
            'error': "Database connection not available"
        }
    
    try:
        print(f"=== SAVING POST-ISSUE RESPONSES ===")
        print(f"Participant ID: {participant_id}")
        print(f"Issue ID: {issue_id}")
        print(f"Responses: {responses}")
        
        # Prepare data for insertion
        data = {
            'participant_id': int(participant_id),
            'issue_id': issue_id,
            **responses  # Spread all response fields
        }
        
        # Use upsert to update if participant_id already exists, insert if not
        result = supabase_client.table('post-PR').upsert(data, on_conflict='participant_id').execute()
        
        print(f"Upsert result: {result}")
        print(f"Data being upserted: {data}")
        
        if result.data and len(result.data) > 0:
            print(f"✅ Successfully saved post-issue responses for participant {participant_id}")
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
                'error': f"Failed to save post-issue responses - RLS policy blocked upsert"
            }
        
    except Exception as e:
        print(f"❌ ERROR saving post-issue responses: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f"Error saving post-issue responses: {str(e)}"
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

