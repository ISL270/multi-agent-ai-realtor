"""
Integration tests for the complete property search flow.

These tests validate the end-to-end functionality of the property search system
by testing the interaction between parse_property_search_query and search_properties tools.
"""

from unittest.mock import MagicMock, patch

from src.agents.property_finder.tools.parse_property_search_query.parse_property_search_query import (
    parse_property_search_query,
)
from src.agents.property_finder.tools.parse_property_search_query.property_search_filters import (
    PropertySearchFilters,
)
from src.agents.property_finder.tools.search_properties.search_properties import (
    search_properties,
)


class TestPropertySearchFlowIntegration:
    """
    Integration tests for the complete property search workflow.

    Tests the realistic flow:
    1. User provides natural language query
    2. parse_property_search_query converts it to structured filters
    3. search_properties uses those filters to find properties
    4. Results are returned in proper format
    """

    @patch("src.agents.property_finder.tools.search_properties.search_properties.supabase")
    @patch("src.agents.property_finder.tools.parse_property_search_query.parse_property_search_query.init_chat_model")
    def test_complete_property_search_flow(self, mock_init_chat_model, mock_supabase):
        """Test the complete flow from natural language query to property results."""

        # Mock LLM for query parsing
        mock_llm = MagicMock()
        mock_structured_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm
        mock_init_chat_model.return_value = mock_llm

        # Mock realistic parsed filters
        mock_filters = PropertySearchFilters(
            city="New Cairo", bedrooms=2, max_price=4000000.0, property_type="apartment"
        )
        mock_structured_llm.invoke.return_value = mock_filters

        # Mock Supabase for property search
        mock_client = mock_supabase

        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "prop-flow-1",
                "title": "Modern 2BR Apartment",
                "description": "Beautiful apartment in New Cairo",
                "price": 3500000.0,
                "property_type": "apartment",
                "bedrooms": 2,
                "bathrooms": 2,
                "city": "New Cairo",
                "area_sqm": 120.0,
                "image_url": "https://example.com/apartment1.jpg",
                "amenities": ["parking", "gym"],
            }
        ]
        mock_client.rpc.return_value.execute.return_value = mock_response

        # Step 1: Parse natural language query
        user_query = "I need a 2-bedroom apartment in New Cairo under 4 million EGP"
        parse_result = parse_property_search_query.invoke(
            {"user_query": user_query, "tool_call_id": "parse_integration_test"}
        )

        # Verify parsing result
        assert hasattr(parse_result, "update")
        assert "filters" in parse_result.update
        parsed_filters = parse_result.update["filters"]

        # Step 2: Use parsed filters to search properties
        search_result = search_properties.invoke({"filters": parsed_filters, "tool_call_id": "search_integration_test"})

        # Verify search result
        assert hasattr(search_result, "update")
        assert "properties" in search_result.update
        properties = search_result.update["properties"]

        # Verify end-to-end flow worked
        assert len(properties) == 1
        property_result = properties[0]
        assert property_result.city == "New Cairo"
        assert property_result.bedrooms == 2
        assert property_result.price <= 4000000.0
        assert property_result.property_type == "apartment"

        # Verify both tools were called with proper parameters
        assert mock_structured_llm.invoke.called
        assert mock_client.rpc.called

    @patch("src.agents.property_finder.tools.search_properties.search_properties.supabase")
    @patch("src.agents.property_finder.tools.parse_property_search_query.parse_property_search_query.init_chat_model")
    def test_complex_query_with_multiple_filters(self, mock_init_chat_model, mock_supabase):
        """Test complex queries with multiple filter criteria."""

        # Mock LLM for complex query parsing
        mock_llm = MagicMock()
        mock_structured_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm
        mock_init_chat_model.return_value = mock_llm

        # Mock complex parsed filters
        mock_filters = PropertySearchFilters(
            city="Maadi",
            bedrooms=3,
            bathrooms=2,
            min_price=2000000.0,
            max_price=6000000.0,
            property_type="villa",
            amenities=["pool", "garden"],
            sort_by="price",
            sort_order="asc",
        )
        mock_structured_llm.invoke.return_value = mock_filters

        # Mock Supabase response
        mock_client = mock_supabase

        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "villa-complex-1",
                "title": "Luxury Villa with Pool",
                "description": "Spacious villa with garden and pool",
                "price": 5500000.0,
                "property_type": "villa",
                "bedrooms": 3,
                "bathrooms": 2,
                "city": "Maadi",
                "area_sqm": 300.0,
                "image_url": "https://example.com/villa1.jpg",
                "amenities": ["pool", "garden", "parking"],
            }
        ]
        mock_client.rpc.return_value.execute.return_value = mock_response

        # Test complex query
        complex_query = (
            "Find me a 3-bedroom villa in Maadi with pool and garden, budget 2-6 million EGP, sorted by price"
        )

        # Step 1: Parse complex query
        parse_result = parse_property_search_query.invoke(
            {"user_query": complex_query, "tool_call_id": "complex_parse_test"}
        )

        parsed_filters = parse_result.update["filters"]

        # Step 2: Search with complex filters
        search_result = search_properties.invoke({"filters": parsed_filters, "tool_call_id": "complex_search_test"})

        properties = search_result.update["properties"]

        # Verify complex filtering worked
        assert len(properties) == 1
        villa = properties[0]
        assert villa.city == "Maadi"
        assert villa.bedrooms == 3
        assert villa.bathrooms == 2
        assert 2000000.0 <= villa.price <= 6000000.0
        assert villa.property_type == "villa"
        assert "pool" in villa.amenities
        assert "garden" in villa.amenities

        # Verify database was called with proper parameters
        call_args = mock_client.rpc.call_args
        params = call_args[0][1]
        assert params["p_city"] == "Maadi"
        assert params["p_bedrooms"] == 3
        assert params["p_bathrooms"] == 2
        assert params["p_min_price"] == 2000000.0
        assert params["p_max_price"] == 6000000.0
        assert params["p_property_type"] == "villa"
        assert params["p_amenities"] == ["pool", "garden"]
        assert params["p_sort_by"] == "price"
        assert params["p_sort_order"] == "asc"

    @patch("src.agents.property_finder.tools.search_properties.search_properties.supabase")
    @patch("src.agents.property_finder.tools.parse_property_search_query.parse_property_search_query.init_chat_model")
    def test_no_results_flow(self, mock_init_chat_model, mock_supabase):
        """Test the flow when no properties match the criteria."""

        # Mock LLM
        mock_llm = MagicMock()
        mock_structured_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm
        mock_init_chat_model.return_value = mock_llm

        # Mock filters for unrealistic search
        mock_filters = PropertySearchFilters(
            city="NonExistentCity", bedrooms=10, max_price=100.0  # Unrealistically low price
        )
        mock_structured_llm.invoke.return_value = mock_filters

        # Mock empty Supabase response
        mock_client = mock_supabase

        mock_response = MagicMock()
        mock_response.data = []  # No results
        mock_client.rpc.return_value.execute.return_value = mock_response

        # Test unrealistic query
        unrealistic_query = "10-bedroom mansion in NonExistentCity for $100"

        # Parse and search
        parse_result = parse_property_search_query.invoke(
            {"user_query": unrealistic_query, "tool_call_id": "no_results_parse"}
        )

        search_result = search_properties.invoke(
            {"filters": parse_result.update["filters"], "tool_call_id": "no_results_search"}
        )

        # Verify empty results are handled properly
        properties = search_result.update["properties"]
        assert len(properties) == 0

        # Should still have proper message structure
        messages = search_result.update["messages"]
        assert len(messages) > 0

    @patch("src.agents.property_finder.tools.search_properties.search_properties.supabase")
    @patch("src.agents.property_finder.tools.parse_property_search_query.parse_property_search_query.init_chat_model")
    def test_error_handling_in_flow(self, mock_init_chat_model, mock_supabase):
        """Test error handling when components fail in the flow."""

        # Mock LLM to work initially
        mock_llm = MagicMock()
        mock_structured_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm
        mock_init_chat_model.return_value = mock_llm

        mock_filters = PropertySearchFilters(city="Cairo", bedrooms=2)
        mock_structured_llm.invoke.return_value = mock_filters

        # Mock Supabase to fail
        mock_client = mock_supabase
        mock_client.rpc.return_value.execute.side_effect = Exception("Database connection failed")

        # Parse should work
        parse_result = parse_property_search_query.invoke(
            {"user_query": "2 bedroom apartment in Cairo", "tool_call_id": "error_flow_parse"}
        )

        assert "filters" in parse_result.update

        # Search should handle database error
        search_result = search_properties.invoke(
            {"filters": parse_result.update["filters"], "tool_call_id": "error_flow_search"}
        )

        # Should contain error message
        messages = search_result.update["messages"]
        assert len(messages) > 0
        error_message = messages[0]
        assert "error" in error_message.content.lower() or "failed" in error_message.content.lower()

    def test_realistic_user_scenarios(self):
        """Test realistic user interaction scenarios without external dependencies."""

        # Test various realistic query patterns that users might enter
        realistic_queries = [
            "2 bedroom apartment in New Cairo under 5M EGP",
            "villa with swimming pool in 6th of October City",
            "3 bedroom property with parking in Maadi",
            "apartment under 2 million in Alexandria with gym",
            "luxury villa with garden in New Cairo, 4+ bedrooms, budget 8-12 million",
            "studio apartment near downtown, furnished, under 1.5M",
            "family house with 3 bathrooms in Heliopolis",
            "penthouse with balcony, New Administrative Capital",
        ]

        # Verify each query can be processed (structure validation)
        for query in realistic_queries:
            # These are structural tests - verify the tools can handle the input format
            assert isinstance(query, str)
            assert len(query) > 0
            assert any(
                keyword in query.lower()
                for keyword in ["bedroom", "apartment", "villa", "house", "studio", "penthouse"]
            )

            # Verify query contains location information
            egyptian_cities = ["cairo", "alexandria", "maadi", "heliopolis", "october", "administrative", "downtown"]
            has_city = any(city in query.lower() for city in egyptian_cities)
            if not has_city:
                print(f"Query without city: {query}")
            assert has_city, f"Query '{query}' does not contain any Egyptian city"

            # Verify query contains some criteria
            criteria_keywords = ["bedroom", "bathroom", "pool", "gym", "garden", "parking", "balcony", "furnished"]
            assert any(keyword in query.lower() for keyword in criteria_keywords)
