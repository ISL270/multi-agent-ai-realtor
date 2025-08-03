import os
from typing import Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import Resource, build

# Calendar API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Global service instance for lazy initialization
_service: Optional[Resource] = None


def get_service_account_file_path() -> str:
    """
    Get the path to the Google service account file.

    Returns:
        str: Path to the service account file

    Raises:
        ValueError: If the service account file path is not configured
    """
    # Try environment variable first
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")

    if service_account_file:
        return service_account_file

    # Fallback to default location in project root
    default_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "service_account.json")

    if os.path.exists(default_path):
        return default_path

    raise ValueError(
        "Google service account file not found. "
        "Set GOOGLE_SERVICE_ACCOUNT_FILE environment variable or place service_account.json in project root."
    )


def initialize_calendar_service() -> Resource:
    """
    Initialize and return a Google Calendar service.

    Returns:
        Resource: Initialized Google Calendar service

    Raises:
        ValueError: If service account file is not found or invalid
        RuntimeError: If service initialization fails
    """
    try:
        # Get service account file path
        service_account_file = get_service_account_file_path()

        # Load credentials from service account file
        creds = Credentials.from_service_account_file(service_account_file, scopes=SCOPES)

        # Build and return the service
        service: Resource = build("calendar", "v3", credentials=creds)
        return service

    except FileNotFoundError as e:
        raise ValueError(f"Service account file not found: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Google Calendar service: {str(e)}") from e


def get_calendar_service() -> Resource:
    """
    Get the Google Calendar service instance using lazy initialization.

    Returns:
        Resource: Initialized Google Calendar service

    Raises:
        ValueError: If service account file is not found or invalid
        RuntimeError: If service initialization fails
    """
    global _service
    if _service is None:
        _service = initialize_calendar_service()
    return _service


# For backward compatibility, expose additional functions if needed
def reset_calendar_service() -> None:
    """
    Reset the cached calendar service instance.
    Useful for testing or when credentials change.
    """
    global _service
    _service = None
