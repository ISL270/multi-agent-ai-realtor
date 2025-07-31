import os.path
from typing import Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Path to the service account key file you downloaded and renamed.
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "service_account.json")


def get_calendar_service() -> Optional[Resource]:
    """Initializes a Google Calendar service using a service account.

    This function uses a service account key file for authentication, which is
    suitable for server-to-server interactions and deployed applications.

    Returns:
        A Google Calendar service object if successful, otherwise None.
    """
    creds: Optional[Credentials] = None
    try:
        # Reason: Using a service account is the standard for backend applications.
        # It avoids the need for manual user authentication (browser flow) and allows
        # the application to have its own identity and permissions.
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    except FileNotFoundError:
        print(f"ERROR: The service account key file was not found at '{SERVICE_ACCOUNT_FILE}'")
        print(
            "Please follow the setup instructions to create a service account, download the key, and place it in the project root."
        )
        return None
    except Exception as e:
        print(f"An error occurred while loading service account credentials: {e}")
        return None

    try:
        service: Resource = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        # The HttpError will be caught and handled by the calling tool.
        print(f"An error occurred while building the calendar service: {error}")
        return None
