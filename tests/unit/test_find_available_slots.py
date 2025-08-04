"""
Unit tests for find_available_slots tool.
Includes both LangChain Standard Tests and custom unit tests.
"""

from unittest.mock import MagicMock, patch

from langchain_tests.unit_tests import ToolsUnitTests

from src.agents.calendar_manager.tools.find_available_slots import find_available_slots


class TestFindAvailableSlotsUnit(ToolsUnitTests):
    """
    Standard unit tests for find_available_slots tool.

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
        Since find_available_slots is a simple function tool, return empty dict.
        """
        return {}

    @property
    def tool_constructor(self):
        """Return the tool constructor."""
        return lambda **kwargs: find_available_slots

    @property
    def tool_invoke_params_example(self):
        """
        Example parameters to pass to tool.invoke().
        These parameters must match the tool's input schema.
        """
        return {"date": "2024-03-15"}


class TestFindAvailableSlotsCustom:
    """Custom unit tests for find_available_slots tool logic."""

    @patch("src.agents.calendar_manager.tools.find_available_slots.get_calendar_service")
    def test_successful_slot_finding_with_available_slots(self, mock_get_calendar_service):
        """Test successful slot finding with some available slots."""
        # Mock Google Calendar service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        # Setup the mock chain
        mock_service.events.return_value = mock_events
        mock_events.list.return_value = mock_list
        mock_list.execute.return_value = mock_execute

        # Mock calendar response with one busy slot (10-11 AM)
        mock_execute.get.return_value = [
            {
                "start": {"dateTime": "2024-03-15T10:00:00+02:00"},
                "end": {"dateTime": "2024-03-15T11:00:00+02:00"},
            }
        ]

        mock_get_calendar_service.return_value = mock_service

        # Call the tool
        result = find_available_slots.invoke({"date": "2024-03-15"})

        # Verify the result structure
        assert isinstance(result, list)
        assert len(result) > 1  # Should have header, slots, and footer

        # Check for header message
        assert any("Available viewing slots for" in str(item) for item in result)

        # Check for footer message
        assert any("Please choose your preferred time" in str(item) for item in result)

        # Verify Google Calendar API was called correctly
        mock_service.events.assert_called_once()
        mock_events.list.assert_called_once()
        call_args = mock_events.list.call_args[1]
        assert call_args["calendarId"] == "primary"
        assert call_args["singleEvents"] is True
        assert call_args["orderBy"] == "startTime"

    @patch("src.agents.calendar_manager.tools.find_available_slots.get_calendar_service")
    def test_no_available_slots(self, mock_get_calendar_service):
        """Test when all slots are busy."""
        # Mock Google Calendar service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        # Setup the mock chain
        mock_service.events.return_value = mock_events
        mock_events.list.return_value = mock_list
        mock_list.execute.return_value = mock_execute

        # Mock calendar response with all day busy (9 AM - 5 PM)
        mock_execute.get.return_value = [
            {
                "start": {"dateTime": "2024-03-15T09:00:00+02:00"},
                "end": {"dateTime": "2024-03-15T17:00:00+02:00"},
            }
        ]

        mock_get_calendar_service.return_value = mock_service

        # Call the tool
        result = find_available_slots.invoke({"date": "2024-03-15"})

        # Verify no available slots message
        assert isinstance(result, list)
        assert len(result) == 1
        assert "No available slots found" in result[0]["message"]

    @patch("src.agents.calendar_manager.tools.find_available_slots.get_calendar_service")
    def test_calendar_service_error(self, mock_get_calendar_service):
        """Test error handling when calendar service fails."""
        # Mock calendar service to raise an exception
        mock_get_calendar_service.side_effect = ValueError("Calendar service unavailable")

        # Call the tool
        result = find_available_slots.invoke({"date": "2024-03-15"})

        # Verify error handling
        assert isinstance(result, list)
        assert len(result) == 1
        assert "error" in result[0]
        assert "Failed to connect to Google Calendar" in result[0]["error"]
        assert "Calendar service unavailable" in result[0]["error"]

    def test_invalid_date_format(self):
        """Test error handling for invalid date format."""
        # Test various invalid date formats
        invalid_dates = [
            "2024-13-01",  # Invalid month
            "2024-02-30",  # Invalid day
            "invalid-date",  # Non-date string
            "2024/03/15",  # Wrong format
            "15-03-2024",  # Wrong order
        ]

        for invalid_date in invalid_dates:
            result = find_available_slots.invoke({"date": invalid_date})
            assert isinstance(result, list)
            assert len(result) == 1
            assert "error" in result[0]
            assert "Invalid date format" in result[0]["error"]

    @patch("src.agents.calendar_manager.tools.find_available_slots.get_calendar_service")
    def test_timezone_handling(self, mock_get_calendar_service):
        """Test that timezone is handled correctly."""
        # Mock Google Calendar service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_list = MagicMock()

        # Setup the mock chain
        mock_service.events.return_value = mock_events
        mock_events.list.return_value = mock_list

        # Mock empty calendar response - execute() should return the events dict directly
        mock_list.execute.return_value = {"items": []}

        mock_get_calendar_service.return_value = mock_service

        # Call the tool
        result = find_available_slots.invoke({"date": "2024-03-15"})

        # Verify timezone is included in API call
        call_args = mock_events.list.call_args[1]
        time_min = call_args["timeMin"]
        time_max = call_args["timeMax"]

        # Verify times are in Egyptian timezone (UTC+2)
        assert "+02:00" in time_min or "+03:00" in time_min  # Account for DST
        assert "+02:00" in time_max or "+03:00" in time_max

        # Verify business hours (9 AM - 5 PM)
        assert "T09:00:00" in time_min
        assert "T17:00:00" in time_max

        # Verify the tool returns available slots for empty calendar (no conflicts)
        assert isinstance(result, list)
        assert len(result) > 1  # Should have header + slots + footer

        # First item should be the header message
        assert "message" in result[0]
        assert "Available viewing slots for March 15, 2024" in result[0]["message"]

        # Should have actual slot data (8 business hours = 8 slots)
        slot_items = [item for item in result if "slot" in item]
        assert len(slot_items) == 8  # 9 AM - 5 PM = 8 one-hour slots

    @patch("src.agents.calendar_manager.tools.find_available_slots.get_calendar_service")
    def test_slot_overlap_detection(self, mock_get_calendar_service):
        """Test that overlapping events are correctly detected."""
        # Mock Google Calendar service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        # Setup the mock chain
        mock_service.events.return_value = mock_events
        mock_events.list.return_value = mock_list
        mock_list.execute.return_value = mock_execute

        # Mock calendar response with overlapping event (10:30 AM - 11:30 AM)
        # This should block both 10-11 AM and 11-12 PM slots
        mock_execute.get.return_value = [
            {
                "start": {"dateTime": "2024-03-15T10:30:00+02:00"},
                "end": {"dateTime": "2024-03-15T11:30:00+02:00"},
            }
        ]

        mock_get_calendar_service.return_value = mock_service

        # Call the tool
        result = find_available_slots.invoke({"date": "2024-03-15"})

        # Verify that slots containing the overlapping event are not available
        slot_data = [item for item in result if "data" in item]

        # Check that 10-11 AM and 11-12 PM slots are not in available slots
        available_times = [slot["data"]["time_display"] for slot in slot_data]

        # These times should not be available due to overlap
        assert not any("10:00 AM - 11:00 AM" in time for time in available_times)
        assert not any("11:00 AM - 12:00 PM" in time for time in available_times)

    @patch("src.agents.calendar_manager.tools.find_available_slots.get_calendar_service")
    def test_business_hours_enforcement(self, mock_get_calendar_service):
        """Test that only business hours (9 AM - 5 PM) are considered."""
        # Mock Google Calendar service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        # Setup the mock chain
        mock_service.events.return_value = mock_events
        mock_events.list.return_value = mock_list
        mock_list.execute.return_value = mock_execute

        # Mock empty calendar response
        mock_execute.get.return_value = []

        mock_get_calendar_service.return_value = mock_service

        # Call the tool
        result = find_available_slots.invoke({"date": "2024-03-15"})

        # Extract slot data
        slot_data = [item for item in result if "data" in item]

        if slot_data:  # If there are available slots
            available_times = [slot["data"]["time_display"] for slot in slot_data]

            # Verify all slots are within business hours
            for time_display in available_times:
                # Extract start time
                start_time_str = time_display.split(" - ")[0]

                # Verify no slots before 9 AM or after 4 PM (since last slot is 4-5 PM)
                assert not any(early_time in start_time_str for early_time in ["6:00 AM", "7:00 AM", "8:00 AM"])
                assert not any(late_time in start_time_str for late_time in ["5:00 PM", "6:00 PM", "7:00 PM"])

    def test_tool_metadata(self):
        """Test that the tool has correct metadata."""
        tool = find_available_slots

        # Check tool name
        assert tool.name == "find_available_slots"

        # Check tool description
        assert "Finds available 1-hour appointment slots" in tool.description

        # Check tool has input schema
        schema = tool.get_input_schema()
        assert schema is not None

        # Check required fields in schema
        schema_fields = schema.model_fields
        assert "date" in schema_fields

        # Verify date field is required
        date_field = schema_fields["date"]
        assert date_field.annotation is str
