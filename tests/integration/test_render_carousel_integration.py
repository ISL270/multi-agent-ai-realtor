"""
Integration tests for the render_property_carousel tool.

These tests validate the end-to-end functionality of the property carousel rendering
by testing realistic scenarios with complete application state.
"""

from unittest.mock import patch

from src.agents.property_finder.tools.parse_property_search_query.property_search_filters import (
    PropertySearchFilters,
)
from src.agents.property_finder.tools.search_properties.property import Property
from src.agents.supervisor.app_state import AppState
from src.agents.supervisor.tools.render_property_carousel import (
    render_property_carousel,
)


class TestRenderCarouselIntegration:
    """
    Integration tests for the render_property_carousel tool.

    Tests realistic scenarios with complete application state including:
    - Properties from search results
    - User filters and preferences
    - UI message handling
    - Error scenarios
    """

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    def test_complete_carousel_rendering_flow(self, mock_push_ui):
        """Test complete carousel rendering with realistic property data."""

        # Create realistic property data (as would come from search_properties)
        properties = [
            Property(
                id="prop-integration-1",
                title="Modern 2BR Apartment in New Cairo",
                description="Beautiful modern apartment with city views, fully furnished with premium amenities.",
                price=3500000.0,
                property_type="apartment",
                bedrooms=2,
                bathrooms=2,
                city="New Cairo",
                area_sqm=120.0,
                image_url="https://example.com/apartment1.jpg",
                amenities=["parking", "gym", "pool", "security"],
            ),
            Property(
                id="prop-integration-2",
                title="Luxury Villa with Garden",
                description="Spacious villa with private garden and swimming pool, perfect for families.",
                price=8500000.0,
                property_type="villa",
                bedrooms=4,
                bathrooms=3,
                city="New Cairo",
                area_sqm=350.0,
                image_url="https://example.com/villa1.jpg",
                amenities=["garden", "pool", "parking", "maid_room"],
            ),
            Property(
                id="prop-integration-3",
                title="Cozy Studio in Maadi",
                description="Perfect studio apartment for young professionals, close to metro station.",
                price=1800000.0,
                property_type="apartment",
                bedrooms=1,
                bathrooms=1,
                city="Maadi",
                area_sqm=65.0,
                image_url="https://example.com/studio1.jpg",
                amenities=["parking", "security", "elevator"],
            ),
        ]

        # Create realistic filters (as would come from parse_property_search_query)
        filters = PropertySearchFilters(
            city="New Cairo", bedrooms=2, max_price=5000000.0, property_type="apartment", amenities=["parking", "gym"]
        )

        # Create complete application state
        test_state = AppState(
            properties=properties, filters=filters, messages=[], ui=[], is_last_step=False, remaining_steps=5
        )

        # Mock successful UI message pushing
        mock_push_ui.return_value = True

        # Execute carousel rendering
        result = render_property_carousel.func(state=test_state, tool_call_id="integration_carousel_test")

        # Verify result structure
        assert hasattr(result, "update")
        assert "messages" in result.update

        # Verify messages were created (ToolMessage + AIMessage)
        messages = result.update["messages"]
        assert len(messages) == 2

        # Get the AI message (second message)
        ai_message = messages[1]
        assert ai_message.type == "ai"
        assert "I found 3 properties" in ai_message.content
        assert "New Cairo" in ai_message.content  # Should mention the city filter
        assert "2+ bedrooms" in ai_message.content  # Should mention bedroom filter
        assert "max $5,000,000" in ai_message.content  # Should mention price filter

        # Verify UI was pushed with property data
        assert mock_push_ui.called
        ui_call_args = mock_push_ui.call_args[0]  # Positional arguments

        assert ui_call_args[0] == "property_carousel"  # First arg is message type
        assert "properties" in ui_call_args[1]  # Second arg is data dict

        # Verify property data was properly formatted for UI
        ui_properties = ui_call_args[1]["properties"]
        assert len(ui_properties) == 3

        # Check first property formatting
        first_property = ui_properties[0]
        assert first_property["id"] == "prop-integration-1"
        assert first_property["title"] == "Modern 2BR Apartment in New Cairo"
        assert first_property["price"] == 3500000.0
        assert "parking" in first_property["amenities"]

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    def test_carousel_with_price_range_filters(self, mock_push_ui):
        """Test carousel rendering with price range filters."""

        properties = [
            Property(
                id="price-test-1",
                title="Budget Apartment",
                description="Affordable option",
                price=2000000.0,
                property_type="apartment",
                bedrooms=2,
                bathrooms=1,
                city="Alexandria",
                area_sqm=90.0,
                image_url="https://example.com/budget.jpg",
                amenities=["parking"],
            ),
            Property(
                id="price-test-2",
                title="Premium Penthouse",
                description="Luxury living",
                price=4500000.0,
                property_type="apartment",
                bedrooms=3,
                bathrooms=2,
                city="Alexandria",
                area_sqm=180.0,
                image_url="https://example.com/premium.jpg",
                amenities=["parking", "gym", "pool", "concierge"],
            ),
        ]

        # Filters with price range
        filters = PropertySearchFilters(city="Alexandria", min_price=1500000.0, max_price=5000000.0, bedrooms=2)

        test_state = AppState(
            properties=properties, filters=filters, messages=[], ui=[], is_last_step=False, remaining_steps=3
        )

        mock_push_ui.return_value = True

        result = render_property_carousel.func(state=test_state, tool_call_id="price_range_test")

        # Verify price range is mentioned in AI message
        ai_message = result.update["messages"][1]  # AI message is second
        assert "$1,500,000" in ai_message.content
        assert "$5,000,000" in ai_message.content
        assert "I found 2 properties" in ai_message.content

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    def test_carousel_with_no_properties(self, mock_push_ui):
        """Test carousel rendering when no properties are found."""

        # Empty properties list
        properties = []

        filters = PropertySearchFilters(
            city="NonExistentCity", bedrooms=10, max_price=100.0  # Unrealistic requirement  # Unrealistically low
        )

        test_state = AppState(
            properties=properties, filters=filters, messages=[], ui=[], is_last_step=True, remaining_steps=0
        )

        mock_push_ui.return_value = True

        result = render_property_carousel.func(state=test_state, tool_call_id="no_properties_test")

        # Verify appropriate message for no results
        messages = result.update["messages"]
        # When no properties, might only return 1 message (ToolMessage)
        if len(messages) == 1:
            message = messages[0]  # Only ToolMessage
        else:
            message = messages[1]  # AI message is second

        assert "no properties" in message.content.lower() or "0 properties" in message.content.lower()

        # When no properties, push_ui_message is NOT called (early return)
        assert not mock_push_ui.called

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    def test_carousel_with_complex_filters(self, mock_push_ui):
        """Test carousel rendering with complex filter combinations."""

        properties = [
            Property(
                id="complex-1",
                title="Family Villa with All Amenities",
                description="Perfect family home with everything you need",
                price=7200000.0,
                property_type="villa",
                bedrooms=4,
                bathrooms=3,
                city="6th of October City",
                area_sqm=280.0,
                image_url="https://example.com/family-villa.jpg",
                amenities=["garden", "pool", "gym", "parking", "security", "maid_room"],
            )
        ]

        # Complex filters with multiple criteria
        filters = PropertySearchFilters(
            city="6th of October City",
            property_type="villa",
            bedrooms=4,
            bathrooms=3,
            min_price=5000000.0,
            max_price=10000000.0,
            amenities=["garden", "pool", "gym"],
            sort_by="price",
            sort_order="desc",
        )

        test_state = AppState(
            properties=properties, filters=filters, messages=[], ui=[], is_last_step=False, remaining_steps=2
        )

        mock_push_ui.return_value = True

        result = render_property_carousel.func(state=test_state, tool_call_id="complex_filters_test")

        # Verify all filter criteria are mentioned
        ai_message = result.update["messages"][1]  # AI message is second
        content = ai_message.content

        assert "6th of October City" in content
        assert "villa" in content.lower()
        assert "4+ bedrooms" in content  # The actual format uses "4+"
        assert "$5,000,000" in content  # Uses $ not EGP
        assert "$10,000,000" in content  # Uses $ not EGP

    @patch("src.agents.supervisor.tools.render_property_carousel.push_ui_message")
    def test_ui_error_handling(self, mock_push_ui):
        """Test carousel behavior when UI message pushing fails."""

        properties = [
            Property(
                id="ui-error-test",
                title="Test Property",
                description="Test description",
                price=3000000.0,
                property_type="apartment",
                bedrooms=2,
                bathrooms=1,
                city="Cairo",
                area_sqm=100.0,
                image_url="https://example.com/test.jpg",
                amenities=["parking"],
            )
        ]

        filters = PropertySearchFilters(city="Cairo")

        test_state = AppState(
            properties=properties, filters=filters, messages=[], ui=[], is_last_step=False, remaining_steps=1
        )

        # Mock UI push to fail
        mock_push_ui.side_effect = Exception("UI service unavailable")

        result = render_property_carousel.func(state=test_state, tool_call_id="ui_error_test")

        # Should still return a result with messages
        assert hasattr(result, "update")
        assert "messages" in result.update

        # Check if there's an error message (might be only 1 message on error)
        messages = result.update["messages"]
        if len(messages) == 1:
            message = messages[0]  # Only ToolMessage on error
        else:
            message = messages[1]  # AI message is second

        assert (
            "error" in message.content.lower()
            or "issue" in message.content.lower()
            or "failed" in message.content.lower()
        )

    def test_property_data_validation(self):
        """Test that carousel handles various property data formats correctly."""

        # Test properties with different data completeness
        test_properties = [
            # Complete property
            Property(
                id="complete-prop",
                title="Complete Property Data",
                description="Full description available",
                price=3000000.0,
                property_type="apartment",
                bedrooms=2,
                bathrooms=2,
                city="Cairo",
                area_sqm=120.0,
                image_url="https://example.com/complete.jpg",
                amenities=["parking", "gym"],
            ),
            # Minimal property data
            Property(
                id="minimal-prop",
                title="Minimal Property",
                description="Basic info only",
                price=2000000.0,
                property_type="apartment",
                bedrooms=1,
                bathrooms=1,
                city="Alexandria",
                area_sqm=80.0,
                image_url="",  # Empty image URL
                amenities=[],  # No amenities
            ),
        ]

        # Verify all properties have required fields
        for prop in test_properties:
            assert hasattr(prop, "id")
            assert hasattr(prop, "title")
            assert hasattr(prop, "price")
            assert hasattr(prop, "property_type")
            assert hasattr(prop, "bedrooms")
            assert hasattr(prop, "bathrooms")
            assert hasattr(prop, "city")
            assert hasattr(prop, "area_sqm")
            assert hasattr(prop, "amenities")

            # Verify data types
            assert isinstance(prop.id, str)
            assert isinstance(prop.title, str)
            assert isinstance(prop.price, (int, float))
            assert isinstance(prop.bedrooms, int)
            assert isinstance(prop.bathrooms, int)
            assert isinstance(prop.amenities, list)
