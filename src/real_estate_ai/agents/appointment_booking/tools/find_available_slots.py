import datetime
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from googleapiclient.discovery import Resource
from langchain_core.tools import tool

from real_estate_ai.utils.google_calendar import get_calendar_service


@tool(parse_docstring=True)
def find_available_slots(date: str) -> List[Dict[str, str]]:
    """Finds available 30-minute appointment slots for a given date in Google Calendar.

    Args:
        date (str): The date to check for available slots, in 'YYYY-MM-DD' format.

    Returns:
        A list of available slots, where each slot is a dictionary with 'start' and 'end' times.
    """
    service: Optional[Resource] = get_calendar_service()
    if not service:
        return [{"error": "Failed to connect to Google Calendar."}]

    try:
        day = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return [{"error": "Invalid date format. Please use YYYY-MM-DD."}]

    try:
        # Per user request, all operations are in the Egyptian timezone.
        tz_str = "Africa/Cairo"
        tz = ZoneInfo(tz_str)
    except ZoneInfoNotFoundError:
        return [{"error": f"Invalid timezone specified: {tz_str}"}]

    # Define business hours (9 AM to 5 PM) in the calendar's timezone
    time_min = datetime.datetime.combine(day, datetime.time(9, 0), tzinfo=tz)
    time_max = datetime.datetime.combine(day, datetime.time(17, 0), tzinfo=tz)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    busy_slots = events_result.get("items", [])

    available_slots = []
    slot_start = time_min

    while slot_start < time_max:
        slot_end = slot_start + datetime.timedelta(minutes=30)
        is_busy = False
        for event in busy_slots:
            # Google API returns timezone-aware ISO strings, so fromisoformat works directly
            event_start = datetime.datetime.fromisoformat(event["start"]["dateTime"])
            event_end = datetime.datetime.fromisoformat(event["end"]["dateTime"])

            # Check for overlap between timezone-aware objects
            if max(slot_start, event_start) < min(slot_end, event_end):
                is_busy = True
                break

        if not is_busy:
            available_slots.append({"start": slot_start.isoformat(), "end": slot_end.isoformat(), "timezone": tz_str})

        slot_start = slot_end

    if not available_slots:
        return [{"message": "No available slots found for the selected date."}]

    return available_slots
