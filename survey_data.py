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

