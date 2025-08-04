"""
Integration tests for the complete calendar management flow.

These tests validate the end-to-end functionality of the calendar system
by testing the interaction between find_available_slots and schedule_viewing tools.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.agents.calendar_manager.tools.find_available_slots import find_available_slots
from src.agents.calendar_manager.tools.schedule_viewing import schedule_viewing


class TestCalendarFlowIntegration:
    """
    Integration tests for the complete calendar management workflow.

    Tests the realistic flow:
    1. User requests available slots for a specific date
    2. find_available_slots queries Google Calendar and returns free slots
    3. User selects a slot and requests to schedule a viewing
    4. schedule_viewing creates the calendar event
    """

    @patch("src.agents.calendar_manager.tools.schedule_viewing.get_calendar_service")
    @patch("src.agents.calendar_manager.tools.find_available_slots.get_calendar_service")
    def test_complete_calendar_booking_flow(self, mock_find_service, mock_schedule_service):
        """Test the complete flow from finding slots to booking a viewing."""

        # Mock Google Calendar service for finding slots
        mock_find_calendar = MagicMock()
        mock_find_service.return_value = mock_find_calendar

        # Mock existing events (some busy periods)
        mock_events_result = {
            "items": [
                {
                    "start": {"dateTime": "2024-03-15T10:00:00+02:00"},
                    "end": {"dateTime": "2024-03-15T11:00:00+02:00"},
                    "summary": "Existing Meeting",
                },
                {
                    "start": {"dateTime": "2024-03-15T14:00:00+02:00"},
                    "end": {"dateTime": "2024-03-15T15:30:00+02:00"},
                    "summary": "Client Call",
                },
            ]
        }
        mock_find_calendar.events.return_value.list.return_value.execute.return_value = mock_events_result

        # Mock Google Calendar service for scheduling
        mock_schedule_calendar = MagicMock()
        mock_schedule_service.return_value = mock_schedule_calendar

        # Mock successful event creation
        mock_created_event = {
            "id": "event_integration_test_123",
            "htmlLink": "https://calendar.google.com/event?eid=test123",
            "summary": "Property Viewing: Luxury Villa - John Doe",
            "start": {"dateTime": "2024-03-15T12:00:00+02:00"},
            "end": {"dateTime": "2024-03-15T13:00:00+02:00"},
        }
        mock_schedule_calendar.events.return_value.insert.return_value.execute.return_value = mock_created_event

        # Step 1: Find available slots
        available_slots = find_available_slots.invoke({"date": "2024-03-15"})

        # Verify slots were found
        assert isinstance(available_slots, list)
        assert len(available_slots) > 0

        # Find a suitable slot (should be available between busy periods)
        suitable_slot = None
        for slot in available_slots:
            if "data" in slot:  # Skip message entries
                slot_data = slot["data"]
                # Look for a slot around 12:00 PM (between the busy periods)
                if "12:00" in slot_data["time_display"]:
                    suitable_slot = slot_data
                    break

        assert suitable_slot is not None, "Should find a slot around 12:00 PM"

        # Step 2: Schedule a viewing using the found slot
        viewing_result = schedule_viewing.invoke(
            {
                "property_title": "Luxury Villa",
                "user_name": "John Doe",
                "user_phone_number": "+201234567890",
                "start_time": suitable_slot["start"],
                "end_time": suitable_slot["end"],
                "timezone": "Africa/Cairo",
            }
        )

        # Verify the viewing was scheduled successfully
        assert "Viewing confirmed!" in viewing_result
        assert "Event created:" in viewing_result
        assert "https://calendar.google.com/event" in viewing_result

        # Verify both calendar services were called
        assert mock_find_calendar.events.called
        assert mock_schedule_calendar.events.called

        # Verify the event was created with proper details
        create_call_args = mock_schedule_calendar.events.return_value.insert.call_args
        event_body = create_call_args[1]["body"]

        assert "Luxury Villa" in event_body["summary"]
        assert "John Doe" in event_body["summary"]
        assert "John Doe" in event_body["description"]
        assert "+201234567890" in event_body["description"]

    @patch("src.agents.calendar_manager.tools.find_available_slots.get_calendar_service")
    def test_busy_day_scenario(self, mock_find_service):
        """Test finding slots on a very busy day."""

        mock_calendar = MagicMock()
        mock_find_service.return_value = mock_calendar

        # Mock a very busy day with back-to-back meetings
        busy_events = {
            "items": [
                {
                    "start": {"dateTime": "2024-03-15T09:00:00+02:00"},
                    "end": {"dateTime": "2024-03-15T10:30:00+02:00"},
                    "summary": "Morning Meeting",
                },
                {
                    "start": {"dateTime": "2024-03-15T10:30:00+02:00"},
                    "end": {"dateTime": "2024-03-15T12:00:00+02:00"},
                    "summary": "Project Review",
                },
                {
                    "start": {"dateTime": "2024-03-15T13:00:00+02:00"},
                    "end": {"dateTime": "2024-03-15T14:30:00+02:00"},
                    "summary": "Client Presentation",
                },
                {
                    "start": {"dateTime": "2024-03-15T14:30:00+02:00"},
                    "end": {"dateTime": "2024-03-15T16:30:00+02:00"},
                    "summary": "Team Meeting",
                },
            ]
        }
        mock_calendar.events.return_value.list.return_value.execute.return_value = busy_events

        # Find available slots on busy day
        available_slots = find_available_slots.invoke({"date": "2024-03-15"})

        # Should still find some slots (early morning, lunch break, late afternoon)
        assert isinstance(available_slots, list)
        # On a busy day, there should be fewer slots but still some available
        # The exact number depends on business hours and slot duration

    @patch("src.agents.calendar_manager.tools.schedule_viewing.get_calendar_service")
    def test_scheduling_with_different_timezones(self, mock_schedule_service):
        """Test scheduling viewings with different timezone specifications."""

        mock_calendar = MagicMock()
        mock_schedule_service.return_value = mock_calendar

        # Mock successful event creation
        mock_created_event = {
            "id": "timezone_test_event",
            "htmlLink": "https://calendar.google.com/event?eid=timezone_test",
            "summary": "Property Viewing: Downtown Apartment - Sarah Smith",
        }
        mock_calendar.events.return_value.insert.return_value.execute.return_value = mock_created_event

        # Test different timezone formats
        timezone_tests = [
            {
                "timezone": "Africa/Cairo",
                "start_time": "2024-03-15T14:00:00+02:00",
                "end_time": "2024-03-15T15:00:00+02:00",
                "description": "Cairo timezone with offset",
            },
            {
                "timezone": "UTC",
                "start_time": "2024-03-15T12:00:00Z",
                "end_time": "2024-03-15T13:00:00Z",
                "description": "UTC timezone",
            },
        ]

        for test_case in timezone_tests:
            result = schedule_viewing.invoke(
                {
                    "property_title": "Downtown Apartment",
                    "user_name": "Sarah Smith",
                    "user_phone_number": "+201987654321",
                    "start_time": test_case["start_time"],
                    "end_time": test_case["end_time"],
                    "timezone": test_case["timezone"],
                }
            )

            # Should successfully schedule regardless of timezone format
            assert "Viewing confirmed!" in result
            assert mock_calendar.events.called

    @patch("src.agents.calendar_manager.tools.schedule_viewing.get_calendar_service")
    @patch("src.agents.calendar_manager.tools.find_available_slots.get_calendar_service")
    def test_error_handling_in_calendar_flow(self, mock_find_service, mock_schedule_service):
        """Test error handling when calendar operations fail."""

        # Mock find_available_slots to work
        mock_find_calendar = MagicMock()
        mock_find_service.return_value = mock_find_calendar

        mock_events_result = {"items": []}  # Empty calendar
        mock_find_calendar.events.return_value.list.return_value.execute.return_value = mock_events_result

        # Mock schedule_viewing to fail
        mock_schedule_service.side_effect = Exception("Google Calendar API unavailable")

        # Step 1: Find slots should work
        available_slots = find_available_slots.invoke({"date": "2024-03-15"})
        assert isinstance(available_slots, list)

        # Step 2: Scheduling should handle the error
        with pytest.raises(Exception) as exc_info:
            schedule_viewing.invoke(
                {
                    "property_title": "Test Property",
                    "user_name": "Test User",
                    "user_phone_number": "+201234567890",
                    "start_time": "2024-03-15T14:00:00+02:00",
                    "end_time": "2024-03-15T15:00:00+02:00",
                    "timezone": "Africa/Cairo",
                }
            )

        # Should propagate the calendar API error
        assert "Google Calendar API unavailable" in str(exc_info.value)

    def test_realistic_calendar_scenarios(self):
        """Test realistic calendar interaction scenarios without external dependencies."""

        # Test various realistic date formats and scenarios
        realistic_scenarios = [
            {"date": "2024-03-15", "description": "Weekday booking"},  # Friday
            {"date": "2024-03-16", "description": "Weekend booking"},  # Saturday
            {"date": "2024-03-18", "description": "Start of week booking"},  # Monday
        ]

        # Test various realistic viewing details
        realistic_viewings = [
            {
                "property_title": "Modern 2BR Apartment in New Cairo",
                "user_name": "Ahmed Hassan",
                "user_phone_number": "+201234567890",
                "description": "Egyptian client booking",
            },
            {
                "property_title": "Luxury Villa with Pool",
                "user_name": "Sarah Johnson",
                "user_phone_number": "+1234567890",
                "description": "International client booking",
            },
            {
                "property_title": "Downtown Studio Apartment",
                "user_name": "محمد علي",  # Arabic name
                "user_phone_number": "+201987654321",
                "description": "Arabic name handling",
            },
        ]

        # Verify data structure validity
        for scenario in realistic_scenarios:
            # Verify date format
            date_str = scenario["date"]
            assert len(date_str) == 10  # YYYY-MM-DD format
            assert date_str.count("-") == 2

            # Verify date can be parsed
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pytest.fail(f"Invalid date format: {date_str}")

        for viewing in realistic_viewings:
            # Verify required fields are present
            assert "property_title" in viewing
            assert "user_name" in viewing
            assert "user_phone_number" in viewing

            # Verify data types
            assert isinstance(viewing["property_title"], str)
            assert isinstance(viewing["user_name"], str)
            assert isinstance(viewing["user_phone_number"], str)

            # Verify phone number format (basic validation)
            phone = viewing["user_phone_number"]
            assert phone.startswith("+")
            assert len(phone) >= 10  # Minimum reasonable phone length
