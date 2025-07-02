from typing import Optional

from googleapiclient.discovery import Resource
from langchain_core.tools import tool

from real_estate_ai.utils.google_calendar import get_calendar_service


@tool(parse_docstring=True)
def schedule_viewing(
    property_title: str,
    user_name: str,
    user_phone_number: str,
    start_time: str,
    end_time: str,
    timezone: str,
) -> str:
    """Schedules a property viewing in Google Calendar.

    Args:
        property_title: The title of the property to view.
        user_name: The name of the user.
        user_phone_number: The phone number of the user.
        start_time: The start time for the viewing in ISO format (YYYY-MM-DDTHH:MM:SS).
        end_time: The end time for the viewing in ISO format (YYYY-MM-DDTHH:MM:SS).
        timezone: The timezone for the event (e.g., 'America/Los_Angeles').

    Returns:
        A confirmation message with the event link or an error message.
    """
    if not user_phone_number:
        return "Error: The user's phone number is required to schedule a viewing. Please ask the user for their phone number."

    service: Optional[Resource] = get_calendar_service()
    if not service:
        return "Failed to connect to Google Calendar."

    summary = f"Property Viewing: {property_title} for {user_name}"
    description = f"Contact: {user_phone_number}"

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time,
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_time,
            "timeZone": timezone,
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 60},
            ],
        },
    }

    try:
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return f"Viewing confirmed! Event created: {created_event.get('htmlLink')}"
    except Exception as e:
        return f"An error occurred while creating the event: {e}"
