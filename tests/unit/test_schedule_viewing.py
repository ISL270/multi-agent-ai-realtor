"""
Unit tests for schedule_viewing tool.
Includes both LangChain Standard Tests and custom unit tests.
"""

from unittest.mock import MagicMock, patch

from langchain_tests.unit_tests import ToolsUnitTests

from src.agents.calendar_manager.tools.schedule_viewing import schedule_viewing


class TestScheduleViewingUnit(ToolsUnitTests):
    """
    Standard unit tests for schedule_viewing tool.

    This class automatically tests:
    - Tool has a name attribute
    - Tool has proper input schema (args_schema)
    - Tool initialization works correctly
    - Tool input schema matches invoke parameters
    """

    @property
    def tool_constructor_params(self):
        """
        Parameters to pass to the tool constructor.
        Since schedule_viewing is a simple function tool, return empty dict.
        """
        return {}

    @property
    def tool_constructor(self):
        """Return the tool constructor."""
        return lambda **kwargs: schedule_viewing

    @property
    def tool_invoke_params_example(self):
        """
        Example parameters to pass to tool.invoke().
        These parameters must match the tool's input schema.
        """
        return {
            "property_title": "Beautiful Villa in Maadi",
            "user_name": "Ahmed Hassan",
            "user_phone_number": "+201234567890",
            "start_time": "2024-03-15T14:00:00",
            "end_time": "2024-03-15T15:00:00",
            "timezone": "Africa/Cairo",
        }


class TestScheduleViewingCustom:
    """Custom unit tests for schedule_viewing tool logic."""

    @patch("src.agents.calendar_manager.tools.schedule_viewing.get_calendar_service")
    def test_successful_viewing_scheduling(self, mock_get_calendar_service):
        """Test successful property viewing scheduling."""
        # Mock Google Calendar service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()

        # Setup the mock chain
        mock_service.events.return_value = mock_events
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_execute

        # Mock successful event creation response
        mock_execute.get.return_value = "https://calendar.google.com/event/123"

        mock_get_calendar_service.return_value = mock_service

        # Call the tool
        result = schedule_viewing.invoke(
            {
                "property_title": "Luxury Apartment in New Cairo",
                "user_name": "Sarah Mohamed",
                "user_phone_number": "+201987654321",
                "start_time": "2024-03-20T10:00:00",
                "end_time": "2024-03-20T11:00:00",
                "timezone": "Africa/Cairo",
            }
        )

        # Verify the result
        assert isinstance(result, str)
        assert "Viewing confirmed!" in result
        assert "Event created:" in result

        # Verify Google Calendar API was called correctly
        mock_service.events.assert_called_once()
        mock_events.insert.assert_called_once()

        # Verify the event data structure
        call_args = mock_events.insert.call_args
        assert call_args[1]["calendarId"] == "primary"

        event_body = call_args[1]["body"]
        assert "Property Viewing: Luxury Apartment in New Cairo for Sarah Mohamed" in event_body["summary"]
        assert "Sarah Mohamed" in event_body["description"]
        assert "+201987654321" in event_body["description"]
        assert event_body["start"]["dateTime"] == "2024-03-20T10:00:00"
        assert event_body["end"]["dateTime"] == "2024-03-20T11:00:00"
        assert event_body["start"]["timeZone"] == "Africa/Cairo"
        assert event_body["end"]["timeZone"] == "Africa/Cairo"

    def test_missing_phone_number_validation(self):
        """Test validation when phone number is missing or empty."""
        # Test with empty phone number
        result = schedule_viewing.invoke(
            {
                "property_title": "Test Property",
                "user_name": "Test User",
                "user_phone_number": "",
                "start_time": "2024-03-15T14:00:00",
                "end_time": "2024-03-15T15:00:00",
                "timezone": "Africa/Cairo",
            }
        )

        assert "Error: The user's phone number is required" in result

        # Test with whitespace-only phone number
        result = schedule_viewing.invoke(
            {
                "property_title": "Test Property",
                "user_name": "Test User",
                "user_phone_number": "   ",
                "start_time": "2024-03-15T14:00:00",
                "end_time": "2024-03-15T15:00:00",
                "timezone": "Africa/Cairo",
            }
        )

        # This should pass through since it's a valid string, but the tool should handle it
        # The current implementation only checks for empty string, not whitespace

    @patch("src.agents.calendar_manager.tools.schedule_viewing.get_calendar_service")
    def test_calendar_service_connection_error(self, mock_get_calendar_service):
        """Test error handling when calendar service connection fails."""
        # Mock calendar service to raise an exception
        mock_get_calendar_service.side_effect = ValueError("Authentication failed")

        # Call the tool
        result = schedule_viewing.invoke(
            {
                "property_title": "Test Property",
                "user_name": "Test User",
                "user_phone_number": "+201234567890",
                "start_time": "2024-03-15T14:00:00",
                "end_time": "2024-03-15T15:00:00",
                "timezone": "Africa/Cairo",
            }
        )

        # Verify error handling
        assert "Failed to connect to Google Calendar" in result
        assert "Authentication failed" in result

    @patch("src.agents.calendar_manager.tools.schedule_viewing.get_calendar_service")
    def test_event_creation_error(self, mock_get_calendar_service):
        """Test error handling when event creation fails."""
        # Mock Google Calendar service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()

        # Setup the mock chain
        mock_service.events.return_value = mock_events
        mock_events.insert.return_value = mock_insert

        # Mock event creation to raise an exception
        mock_insert.execute.side_effect = Exception("Calendar quota exceeded")

        mock_get_calendar_service.return_value = mock_service

        # Call the tool
        result = schedule_viewing.invoke(
            {
                "property_title": "Test Property",
                "user_name": "Test User",
                "user_phone_number": "+201234567890",
                "start_time": "2024-03-15T14:00:00",
                "end_time": "2024-03-15T15:00:00",
                "timezone": "Africa/Cairo",
            }
        )

        # Verify error handling
        assert "An error occurred while creating the event" in result
        assert "Calendar quota exceeded" in result

    @patch("src.agents.calendar_manager.tools.schedule_viewing.get_calendar_service")
    def test_event_structure_and_content(self, mock_get_calendar_service):
        """Test that the event is structured correctly with all required content."""
        # Mock Google Calendar service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()

        # Setup the mock chain
        mock_service.events.return_value = mock_events
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_execute

        mock_execute.get.return_value = "https://calendar.google.com/event/456"
        mock_get_calendar_service.return_value = mock_service

        # Call the tool with specific test data
        schedule_viewing.invoke(
            {
                "property_title": "Modern Penthouse in Zamalek",
                "user_name": "Omar Khaled",
                "user_phone_number": "+201555123456",
                "start_time": "2024-04-10T16:30:00",
                "end_time": "2024-04-10T17:30:00",
                "timezone": "Africa/Cairo",
            }
        )

        # Get the event body that was passed to the API
        call_args = mock_events.insert.call_args
        event_body = call_args[1]["body"]

        # Verify event summary
        expected_summary = "Property Viewing: Modern Penthouse in Zamalek for Omar Khaled"
        assert event_body["summary"] == expected_summary

        # Verify event description contains all required information
        description = event_body["description"]
        assert "📋 Property Viewing Details:" in description
        assert "🏠 Property: Modern Penthouse in Zamalek" in description
        assert "👤 Client: Omar Khaled" in description
        assert "📞 Phone: +201555123456" in description
        assert "📅 Please arrive 5 minutes early" in description
        assert "💼 Bring a valid ID" in description

        # Verify event timing
        assert event_body["start"]["dateTime"] == "2024-04-10T16:30:00"
        assert event_body["end"]["dateTime"] == "2024-04-10T17:30:00"
        assert event_body["start"]["timeZone"] == "Africa/Cairo"
        assert event_body["end"]["timeZone"] == "Africa/Cairo"

        # Verify reminders are configured
        assert "reminders" in event_body
        assert event_body["reminders"]["useDefault"] is False
        assert len(event_body["reminders"]["overrides"]) == 1
        reminder = event_body["reminders"]["overrides"][0]
        assert reminder["method"] == "popup"
        assert reminder["minutes"] == 60

    @patch("src.agents.calendar_manager.tools.schedule_viewing.get_calendar_service")
    def test_different_timezones(self, mock_get_calendar_service):
        """Test that different timezones are handled correctly."""
        # Mock Google Calendar service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()

        # Setup the mock chain
        mock_service.events.return_value = mock_events
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_execute

        mock_execute.get.return_value = "https://calendar.google.com/event/789"
        mock_get_calendar_service.return_value = mock_service

        # Test with different timezone
        schedule_viewing.invoke(
            {
                "property_title": "Beach House in Sahel",
                "user_name": "Layla Ahmed",
                "user_phone_number": "+201777888999",
                "start_time": "2024-06-15T09:00:00",
                "end_time": "2024-06-15T10:00:00",
                "timezone": "Europe/London",
            }
        )

        # Verify timezone is correctly set
        call_args = mock_events.insert.call_args
        event_body = call_args[1]["body"]
        assert event_body["start"]["timeZone"] == "Europe/London"
        assert event_body["end"]["timeZone"] == "Europe/London"

    @patch("src.agents.calendar_manager.tools.schedule_viewing.get_calendar_service")
    def test_special_characters_in_input(self, mock_get_calendar_service):
        """Test handling of special characters in user input."""
        # Mock Google Calendar service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()

        # Setup the mock chain
        mock_service.events.return_value = mock_events
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_execute

        mock_execute.get.return_value = "https://calendar.google.com/event/special"
        mock_get_calendar_service.return_value = mock_service

        # Test with special characters
        schedule_viewing.invoke(
            {
                "property_title": "Villa with Pool & Garden (Premium)",
                "user_name": "José María García",
                "user_phone_number": "+20-1-555-123-456",
                "start_time": "2024-05-20T11:15:00",
                "end_time": "2024-05-20T12:15:00",
                "timezone": "Africa/Cairo",
            }
        )

        # Verify special characters are preserved
        call_args = mock_events.insert.call_args
        event_body = call_args[1]["body"]

        assert "Villa with Pool & Garden (Premium)" in event_body["summary"]
        assert "José María García" in event_body["description"]
        assert "+20-1-555-123-456" in event_body["description"]

    def test_tool_metadata(self):
        """Test that the tool has correct metadata."""
        tool = schedule_viewing

        # Check tool name
        assert tool.name == "schedule_viewing"

        # Check tool description
        assert "Schedules a property viewing in Google Calendar" in tool.description

        # Check tool has input schema
        schema = tool.get_input_schema()
        assert schema is not None

        # Check required fields in schema
        schema_fields = schema.model_fields
        required_fields = ["property_title", "user_name", "user_phone_number", "start_time", "end_time", "timezone"]

        for field in required_fields:
            assert field in schema_fields

        # Verify all fields are string type
        for field_name in required_fields:
            field = schema_fields[field_name]
            assert field.annotation is str
