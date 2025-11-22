import io
import os
import re
import json
import streamlit as st

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from google.oauth2.service_account import Credentials
except Exception:
    # Defer import errors to runtime in the UI, so app still loads
    build = None
    MediaIoBaseUpload = None
    Credentials = None


SCOPES = ['https://www.googleapis.com/auth/drive']


def _require_google_libs():
    if build is None or MediaIoBaseUpload is None or Credentials is None:
        raise RuntimeError(
            "Google API libraries not available. Please install 'google-api-python-client' and 'google-auth'."
        )


def get_drive_service():
    """Initialize a Google Drive service using a service account in st.secrets."""
    _require_google_libs()
    sa_info = st.secrets.get('gcp_service_account')
    if not sa_info:
        # Fallback: try loading from a JSON file path
        candidate_path = st.secrets.get('GCP_SERVICE_ACCOUNT_FILE', 'google_auth.json')
        if candidate_path and os.path.exists(candidate_path):
            with open(candidate_path, 'r') as f:
                sa_info = json.load(f)
        else:
            raise RuntimeError("Missing service account credentials. Provide st.secrets['gcp_service_account'] or place google_auth.json in app root.")
    creds = Credentials.from_service_account_info(sa_info, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds, cache_discovery=False)


def sanitize_filename(name: str) -> str:
    """Make a filename safe for Drive by replacing problematic chars."""
    # Replace path separators and common unsafe chars
    safe = re.sub(r"[\\/\n\r\t]", "_", name)
    safe = re.sub(r"[^A-Za-z0-9._ -]", "_", safe)
    # Collapse repeated underscores/spaces
    safe = re.sub(r"[ _]+", " ", safe).strip()
    return safe or "uploaded_file"


def upload_to_drive(file, folder_id: str, filename: str | None = None):
    """Upload a single file-like object from st.file_uploader to Google Drive folder.

    Args:
        file: UploadedFile from Streamlit (has .name, .type, .getvalue())
        folder_id: Target Drive folder ID
        filename: Optional override for the stored filename

    Returns:
        dict with 'id' and 'webViewLink' on success
    """
    if not folder_id:
        raise RuntimeError("Missing Drive folder ID. Set 'GDRIVE_FOLDER_ID' in secrets.")

    service = get_drive_service()
    file_bytes = file.getvalue()
    mimetype = getattr(file, 'type', None) or 'application/octet-stream'
    name = sanitize_filename(filename or getattr(file, 'name', 'uploaded_file'))

    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mimetype, resumable=False)
    body = {'name': name, 'parents': [folder_id]}
    created = service.files().create(
        body=body,
        media_body=media,
        fields='id, webViewLink',
        supportsAllDrives=True  # Required for shared drives
    ).execute()
    return created


def _get_or_create_folder(service, parent_id: str, name: str) -> str:
    """Return the ID of a child folder with given name under parent, creating it if needed."""
    name_safe = sanitize_filename(name)
    q = (
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"name = '{name_safe}' and '{parent_id}' in parents and trashed = false"
    )
    res = service.files().list(
        q=q,
        fields='files(id, name)',
        pageSize=1,
        supportsAllDrives=True,  # Required for shared drives
        includeItemsFromAllDrives=True  # Required for shared drives
    ).execute()
    files = res.get('files', [])
    if files:
        return files[0]['id']
    # Create if not found
    body = {
        'name': name_safe,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id],
    }
    created = service.files().create(
        body=body,
        fields='id',
        supportsAllDrives=True  # Required for shared drives
    ).execute()
    return created['id']


def upload_to_drive_in_subfolders(file, base_folder_id: str, subfolders: list[str], filename: str | None = None):
    """Upload a file into nested subfolders under a base Drive folder.

    Creates subfolders if they don't exist. Example: subfolders=[participant, issue_id]
    """
    service = get_drive_service()
    parent_id = base_folder_id
    for folder_name in subfolders or []:
        parent_id = _get_or_create_folder(service, parent_id, folder_name)

    file_bytes = file.getvalue()
    mimetype = getattr(file, 'type', None) or 'application/octet-stream'
    name = sanitize_filename(filename or getattr(file, 'name', 'uploaded_file'))

    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mimetype, resumable=False)
    body = {'name': name, 'parents': [parent_id]}
    created = service.files().create(
        body=body,
        media_body=media,
        fields='id, webViewLink',
        supportsAllDrives=True  # Required for shared drives
    ).execute()
    return created
