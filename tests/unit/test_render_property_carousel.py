"""
Unit tests for render_property_carousel tool.
Includes both LangChain Standard Tests and custom unit tests.
"""

from unittest.mock import MagicMock, patch

from langchain_tests.unit_tests import ToolsUnitTests
from langchain_core.messages import AIMessage, ToolMessage

from src.agents.supervisor.tools.render_property_carousel import render_property_carousel
from src.agents.property_finder.tools.search_properties.property import Property
from src.agents.property_finder.tools.parse_property_search_query.property_search_filters import PropertySearchFilters


class TestRenderPropertyCarouselUnit(ToolsUnitTests):
    """
    Standard unit tests for render_property_carousel tool.

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
        Since render_property_carousel is a simple function tool, return empty dict.
        """
        return {}

    @property
    def tool_constructor(self):
        """Return the tool constructor."""
        return lambda **kwargs: render_property_carousel

    @property
    def tool_invoke_params_example(self):
        """
        Example parameters to pass to tool.invoke().
        These parameters must match the tool's input schema.
        Since this tool uses injected parameters, we provide minimal params.
        """
        return {
            "state": {
                "properties": [], 
                "filters": None,
                "messages": [],
                "is_last_step": False,
                "remaining_steps": 5,
                "ui": []
            },
            "tool_call_id": "test_call_123",
        }


class TestRenderPropertyCarouselCustom:
    """Custom unit tests for render_property_carousel tool logic."""

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    @patch("src.agents.supervisor.tools.render_property_carousel.uuid.uuid4")
    def test_successful_carousel_rendering_single_property(self, mock_uuid, mock_push_ui):
        """Test successful rendering of property carousel with single property."""
        # Mock UUID for consistent testing
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = lambda x: "test-uuid-123"

        # Create test property
        test_property = Property(
            id="prop-123",
            title="Beautiful Villa in Maadi",
            description="Spacious villa with modern amenities",
            price=750000.0,
            property_type="villa",
            bedrooms=4,
            bathrooms=3,
            city="Cairo",
            area_sqm=300.0,
            image_url="https://example.com/villa.jpg",
            amenities=["pool", "garden"]
        )

        # Create test filters
        test_filters = PropertySearchFilters(
            city="Cairo",
            bedrooms=4,
            max_price=800000.0
        )

        # Create test state - tool expects Property objects
        test_state = {
            "properties": [test_property],
            "filters": test_filters,
            "messages": [],
            "is_last_step": False,
            "remaining_steps": 5,
            "ui": []
        }

        # Call the tool function directly to bypass InjectedState validation
        result = render_property_carousel.func(
            state=test_state,
            tool_call_id="test_call_123"
        )

        # Verify the result structure
        assert hasattr(result, "update")
        assert "messages" in result.update
        messages = result.update["messages"]
        assert len(messages) == 2

        # Verify tool message
        tool_message = messages[0]
        assert isinstance(tool_message, ToolMessage)
        assert "Successfully created property carousel UI for 1 properties" in tool_message.content
        assert tool_message.tool_call_id == "test_call_123"

        # Verify AI message
        ai_message = messages[1]
        assert isinstance(ai_message, AIMessage)
        assert "I found 1 property that matches your criteria" in ai_message.content
        assert "in Cairo" in ai_message.content
        assert "4+ bedrooms" in ai_message.content
        assert "max $800,000" in ai_message.content

        # Verify push_ui_message was called correctly
        mock_push_ui.assert_called_once()
        call_args = mock_push_ui.call_args
        assert call_args[0][0] == "property_carousel"
        
        ui_data = call_args[0][1]
        assert "properties" in ui_data
        assert len(ui_data["properties"]) == 1
        
        # Verify property was converted to dict
        property_dict = ui_data["properties"][0]
        assert property_dict["id"] == "prop-123"
        assert property_dict["title"] == "Beautiful Villa in Maadi"
        assert property_dict["price"] == 750000.0

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    @patch("src.agents.supervisor.tools.render_property_carousel.uuid.uuid4")
    def test_successful_carousel_rendering_multiple_properties(self, mock_uuid, mock_push_ui):
        """Test successful rendering of property carousel with multiple properties."""
        # Mock UUID for consistent testing
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = lambda x: "test-uuid-456"

        # Create test properties
        property1 = Property(
            id="prop-456",
            title="Modern Apartment in New Cairo",
            description="Contemporary apartment with city views",
            price=500000.0,
            property_type="apartment",
            bedrooms=3,
            bathrooms=2,
            city="Cairo",
            area_sqm=150.0,
            image_url="https://example.com/apartment.jpg",
            amenities=["gym", "parking"]
        )

        property2 = Property(
            id="prop-789",
            title="Luxury Penthouse in Zamalek",
            description="Exclusive penthouse with premium finishes",
            price=1200000.0,
            property_type="penthouse",
            bedrooms=3,
            bathrooms=3,
            city="Cairo",
            area_sqm=200.0,
            image_url="https://example.com/penthouse.jpg",
            amenities=["pool", "gym", "parking"]
        )

        # Create test filters
        test_filters = PropertySearchFilters(
            city="Cairo",
            bedrooms=3,
            property_type="apartment"
        )

        # Create test state - tool expects dictionary with AppState structure
        test_state = {
            "properties": [property1, property2],
            "filters": test_filters,
            "messages": [],
            "is_last_step": False,
            "remaining_steps": 5,
            "ui": []
        }

        # Call the tool function directly to bypass InjectedState validation
        result = render_property_carousel.func(
            state=test_state,
            tool_call_id="test_call_456"
        )

        # Verify the result structure
        assert hasattr(result, "update")
        messages = result.update["messages"]
        assert len(messages) == 2

        # Verify tool message
        tool_message = messages[0]
        assert "Successfully created property carousel UI for 2 properties" in tool_message.content

        # Verify AI message
        ai_message = messages[1]
        assert "I found 2 properties that match your criteria" in ai_message.content
        assert "in Cairo" in ai_message.content
        assert "3+ bedrooms" in ai_message.content
        assert "type: apartment" in ai_message.content

        # Verify UI data contains both properties
        call_args = mock_push_ui.call_args
        ui_data = call_args[0][1]
        assert len(ui_data["properties"]) == 2
        
        property_ids = [prop["id"] for prop in ui_data["properties"]]
        assert "prop-456" in property_ids
        assert "prop-789" in property_ids

    def test_no_properties_available(self):
        """Test handling when no properties are available in state."""
        # Create empty state - tool expects dictionary with AppState structure
        test_state = {
            "properties": [],
            "filters": None,
            "messages": [],
            "is_last_step": False,
            "remaining_steps": 5,
            "ui": []
        }

        # Call the tool function directly to bypass InjectedState validation
        result = render_property_carousel.func(
            state=test_state,
            tool_call_id="test_empty_call"
        )

        # Verify error handling
        assert hasattr(result, "update")
        messages = result.update["messages"]
        assert len(messages) == 1

        # Verify error message
        error_message = messages[0]
        assert isinstance(error_message, ToolMessage)
        assert "No properties available to display" in error_message.content
        assert error_message.tool_call_id == "test_empty_call"

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    @patch("src.agents.supervisor.tools.render_property_carousel.uuid.uuid4")
    def test_rendering_without_filters(self, mock_uuid, mock_push_ui):
        """Test rendering when no filters are provided in state."""
        # Mock UUID
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = lambda x: "test-uuid-no-filters"

        # Create test property
        test_property = Property(
            id="prop-no-filters",
            title="Test Property",
            description="Test property description",
            price=600000.0,
            property_type="apartment",
            bedrooms=2,
            bathrooms=1,
            city="Alexandria",
            area_sqm=100.0,
            image_url="https://example.com/test.jpg",
            amenities=[]
        )

        # Create state without filters - tool expects dictionary with AppState structure
        test_state = {
            "properties": [test_property],
            "filters": None,
            "messages": [],
            "is_last_step": False,
            "remaining_steps": 5,
            "ui": []
        }

        # Call the tool function directly to bypass InjectedState validation
        result = render_property_carousel.func(
            state=test_state,
            tool_call_id="test_no_filters_call"
        )

        # Verify the result
        messages = result.update["messages"]
        ai_message = messages[1]
        
        # Should not contain filter information
        assert "I found 1 property that matches your criteria:" in ai_message.content
        assert "in Alexandria" not in ai_message.content  # No filter summary
        assert "bedrooms" not in ai_message.content
        assert "price range" not in ai_message.content

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    @patch("src.agents.supervisor.tools.render_property_carousel.uuid.uuid4")
    def test_price_range_formatting(self, mock_uuid, mock_push_ui):
        """Test proper formatting of price ranges in filter summary."""
        # Mock UUID
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = lambda x: "test-uuid-price"

        # Create test property
        test_property = Property(
            id="prop-price",
            title="Price Test Property",
            description="Property for price range testing",
            price=750000.0,
            property_type="apartment",
            bedrooms=3,
            bathrooms=2,
            city="Cairo",
            area_sqm=150.0,
            image_url="https://example.com/price.jpg",
            amenities=[]
        )

        # Test different price range scenarios
        test_cases = [
            # Min and max price
            {
                "filters": PropertySearchFilters(min_price=500000.0, max_price=1000000.0),
                "expected": "price range: min $500,000 - max $1,000,000"
            },
            # Only min price
            {
                "filters": PropertySearchFilters(min_price=300000.0),
                "expected": "price range: min $300,000"
            },
            # Only max price
            {
                "filters": PropertySearchFilters(max_price=800000.0),
                "expected": "price range: max $800,000"
            }
        ]

        for test_case in test_cases:
            test_state = {
                "properties": [test_property],
                "filters": test_case["filters"],
                "messages": [],
                "is_last_step": False,
                "remaining_steps": 5,
                "ui": []
            }

            result = render_property_carousel.func(
                state=test_state,
                tool_call_id="test_price_call"
            )

            ai_message = result.update["messages"][1]
            assert test_case["expected"] in ai_message.content

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    def test_exception_handling(self, mock_push_ui):
        """Test error handling when an exception occurs."""
        # Mock push_ui_message to raise an exception
        mock_push_ui.side_effect = Exception("UI rendering failed")

        # Create test state
        test_property = Property(
            id="prop-error",
            title="Error Test Property",
            description="Property for error testing",
            price=500000.0,
            property_type="apartment",
            bedrooms=2,
            bathrooms=1,
            city="Cairo",
            area_sqm=100.0,
            image_url="https://example.com/error.jpg",
            amenities=[]
        )

        test_state = {
            "properties": [test_property],
            "filters": None,
            "messages": [],
            "is_last_step": False,
            "remaining_steps": 5,
            "ui": []
        }

        # Call the tool function directly to bypass InjectedState validation
        result = render_property_carousel.func(
            state=test_state,
            tool_call_id="test_error_call"
        )

        # Verify error handling
        messages = result.update["messages"]
        assert len(messages) == 1

        error_message = messages[0]
        assert isinstance(error_message, ToolMessage)
        assert "Error creating property UI" in error_message.content
        assert "UI rendering failed" in error_message.content
        assert error_message.tool_call_id == "test_error_call"

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    @patch("src.agents.supervisor.tools.render_property_carousel.uuid.uuid4")
    def test_property_model_dump_conversion(self, mock_uuid, mock_push_ui):
        """Test that properties are properly converted to dictionaries."""
        # Mock UUID
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = lambda x: "test-uuid-conversion"

        # Create test property with all fields
        test_property = Property(
            id="prop-conversion",
            title="Conversion Test Villa",
            description="Luxurious villa for conversion testing",
            price=900000.0,
            property_type="villa",
            bedrooms=5,
            bathrooms=4,
            city="New Cairo",
            area_sqm=400.0,
            image_url="https://example.com/conversion.jpg",
            amenities=["pool", "gym", "garden", "parking"]
        )

        test_state = {
            "properties": [test_property],
            "filters": None,
            "messages": [],
            "is_last_step": False,
            "remaining_steps": 5,
            "ui": []
        }

        # Call the tool function directly to bypass InjectedState validation
        render_property_carousel.func(
            state=test_state,
            tool_call_id="test_conversion_call"
        )

        # Verify the property was converted to dict with all fields
        call_args = mock_push_ui.call_args
        ui_data = call_args[0][1]
        property_dict = ui_data["properties"][0]

        # Check all expected fields are present
        expected_fields = ["id", "title", "description", "price", "property_type", "bedrooms", "bathrooms", "city", "area_sqm", "image_url", "amenities"]
        for field in expected_fields:
            assert field in property_dict

        # Verify field values
        assert property_dict["id"] == "prop-conversion"
        assert property_dict["title"] == "Conversion Test Villa"
        assert property_dict["description"] == "Luxurious villa for conversion testing"
        assert property_dict["price"] == 900000.0
        assert property_dict["property_type"] == "villa"
        assert property_dict["bedrooms"] == 5
        assert property_dict["bathrooms"] == 4
        assert property_dict["city"] == "New Cairo"
        assert property_dict["area_sqm"] == 400.0
        assert property_dict["image_url"] == "https://example.com/conversion.jpg"
        assert property_dict["amenities"] == ["pool", "gym", "garden", "parking"]

    def test_tool_metadata(self):
        """Test that the tool has correct metadata."""
        tool = render_property_carousel

        # Check tool name
        assert tool.name == "render_property_carousel"

        # Check tool description
        assert "Renders a property carousel UI from properties in state" in tool.description

        # Check tool has input schema
        schema = tool.get_input_schema()
        assert schema is not None

        # Check that the tool uses injected parameters
        # The schema should be minimal since most parameters are injected
        # Should have injected state and tool_call_id parameters
        # These might not appear in the schema since they're injected
        # The important thing is that the tool can be invoked
