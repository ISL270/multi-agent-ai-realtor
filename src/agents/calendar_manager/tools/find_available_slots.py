import datetime
from typing import Dict, List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from googleapiclient.discovery import Resource
from langchain_core.tools import tool

from utils.google_calendar import get_calendar_service


@tool(parse_docstring=True)
def find_available_slots(date: str) -> List[Dict[str, str]]:
    """Finds available 1-hour appointment slots for a given date in Google Calendar.

    Args:
        date (str): The date to check for available slots, in 'YYYY-MM-DD' format.

    Returns:
        A formatted list of available time slots for property viewings.
    """
    try:
        service: Resource = get_calendar_service()
    except (ValueError, RuntimeError) as e:
        return [{"error": f"Failed to connect to Google Calendar: {str(e)}"}]

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

    # Generate 1-hour slots
    while slot_start < time_max:
        slot_end = slot_start + datetime.timedelta(hours=1)
        
        # Skip if slot would extend beyond business hours
        if slot_end > time_max:
            break
            
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
            # Format time for display (e.g., "10:00 AM - 11:00 AM")
            start_time = slot_start.strftime("%I:%M %p").lstrip('0')
            end_time = slot_end.strftime("%I:%M %p").lstrip('0')
            time_display = f"{start_time} - {end_time}"
            
            available_slots.append({
                "time_display": time_display,
                "start": slot_start.isoformat(), 
                "end": slot_end.isoformat(), 
                "timezone": tz_str
            })

        slot_start = slot_start + datetime.timedelta(hours=1)

    if not available_slots:
        return [{"message": "❌ No available slots found for the selected date."}]

    # Format the response more appealingly
    formatted_slots = []
    formatted_slots.append({"message": f"📅 **Available viewing slots for {day.strftime('%B %d, %Y')}:**"})
    
    for i, slot in enumerate(available_slots, 1):
        formatted_slots.append({"slot": f"🕐 **{i}.** {slot['time_display']}", "data": slot})
    
    formatted_slots.append({"message": "\n💡 **Please choose your preferred time and provide your name and phone number to book.**"})
    
    return formatted_slots
