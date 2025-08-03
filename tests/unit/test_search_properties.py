"""
Comprehensive unit tests for search_properties tool.
Includes both LangChain Standard Tests and custom unit tests.
"""

import pytest
from unittest.mock import patch, MagicMock
from langchain_tests.unit_tests import ToolsUnitTests

from src.agents.property_finder.tools.search_properties.search_properties import (
    search_properties,
    _map_to_property,
)
from src.agents.property_finder.tools.parse_property_search_query.property_search_filters import (
    PropertySearchFilters,
)
from src.agents.property_finder.tools.search_properties.property import Property


class TestSearchPropertiesUnit(ToolsUnitTests):
    """
    Standard unit tests for search_properties tool.
    
    This class automatically tests:
    - Tool has a name attribute
    - Tool has proper input schema (args_schema)
    - Tool can be initialized correctly
    - Input parameters match the declared schema
    """

    @property
    def tool_constructor(self):
        """Returns the tool class/function to be tested."""
        return search_properties

    @property
    def tool_invoke_params_example(self):
        """
        Returns example parameters for invoking the tool.
        These parameters must match the tool's input schema.
        """
        # Create a sample PropertySearchFilters object
        sample_filters = PropertySearchFilters(
            city="Cairo",
            bedrooms=3,
            max_price=500000.0,
            amenities=["pool", "gym"]
        )
        
        return {
            "filters": sample_filters,
            "tool_call_id": "test_call_id_123"
        }


class TestSearchPropertiesCustom:
    """Custom unit tests for search_properties tool logic."""

    @patch('src.agents.property_finder.tools.search_properties.search_properties.supabase')
    def test_successful_search_with_results(self, mock_supabase):
        """Test successful property search with results."""
        # Mock database response
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "prop-123",
                "title": "Luxury Villa",
                "description": "Beautiful villa in Cairo",
                "price": 450000.0,
                "property_type": "villa",
                "bedrooms": 3,
                "bathrooms": 2,
                "city": "Cairo",
                "area_sqm": 200.0,
                "image_url": "https://example.com/villa.jpg",
                "amenities": ["pool", "gym"]
            },
            {
                "id": "prop-456",
                "title": "Modern Apartment",
                "description": "Modern apartment with amenities",
                "price": 300000.0,
                "property_type": "apartment",
                "bedrooms": 2,
                "bathrooms": 1,
                "city": "Cairo",
                "area_sqm": 120.0,
                "image_url": "https://example.com/apartment.jpg",
                "amenities": ["gym"]
            }
        ]
        
        mock_supabase.rpc.return_value.execute.return_value = mock_response

        # Create test filters
        filters = PropertySearchFilters(
            city="Cairo",
            bedrooms=3,
            max_price=500000.0,
            amenities=["gym"]
        )

        # Call the tool
        result = search_properties.invoke({
            "filters": filters,
            "tool_call_id": "test_call_123"
        })

        # Verify the result
        assert hasattr(result, 'update')
        assert 'properties' in result.update
        assert 'filters' in result.update
        assert 'messages' in result.update
        
        # Verify properties
        properties = result.update['properties']
        assert len(properties) == 2
        assert all(isinstance(prop, Property) for prop in properties)
        assert properties[0].id == "prop-123"
        assert properties[0].title == "Luxury Villa"
        assert properties[0].amenities == ["pool", "gym"]

        # Verify filters are preserved
        assert result.update['filters'] == filters

        # Verify success message
        messages = result.update['messages']
        assert len(messages) == 1
        assert "Found 2 properties" in messages[0].content

        # Verify database call
        mock_supabase.rpc.assert_called_once_with("search_properties_rpc", {
            "p_amenities": ["gym"],
            "p_city": "Cairo",
            "p_max_price": 500000.0,
            "p_bedrooms": 3,
            "p_sort_by": "price",
            "p_sort_order": "desc"
        })

    @patch('src.agents.property_finder.tools.search_properties.search_properties.supabase')
    def test_search_with_no_results(self, mock_supabase):
        """Test search that returns no results."""
        # Mock empty database response
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.rpc.return_value.execute.return_value = mock_response

        # Create test filters
        filters = PropertySearchFilters(city="Alexandria", bedrooms=5)

        # Call the tool
        result = search_properties.invoke({
            "filters": filters,
            "tool_call_id": "test_call_123"
        })

        # Verify the result
        assert hasattr(result, 'update')
        properties = result.update['properties']
        assert len(properties) == 0

        # Verify message
        messages = result.update['messages']
        assert "No properties found" in messages[0].content

    @patch('src.agents.property_finder.tools.search_properties.search_properties.supabase')
    def test_search_with_database_error(self, mock_supabase):
        """Test error handling when database call fails."""
        # Mock database error
        mock_supabase.rpc.return_value.execute.side_effect = Exception("Database connection failed")

        # Create test filters
        filters = PropertySearchFilters(city="Cairo")

        # Call the tool
        result = search_properties.invoke({
            "filters": filters,
            "tool_call_id": "test_call_123"
        })

        # Verify error handling
        assert hasattr(result, 'update')
        properties = result.update['properties']
        assert len(properties) == 0

        # Verify error message
        messages = result.update['messages']
        assert "An error occurred while searching" in messages[0].content
        assert "Database connection failed" in messages[0].content

    @pytest.mark.parametrize("filters_data,expected_params", [
        (
            {"city": "Cairo", "bedrooms": 2},
            {"p_city": "Cairo", "p_bedrooms": 2, "p_sort_by": "price", "p_sort_order": "desc"}
        ),
        (
            {"max_price": 1000000, "property_type": "villa"},
            {"p_max_price": 1000000, "p_property_type": "villa", "p_sort_by": "price", "p_sort_order": "desc"}
        ),
        (
            {"amenities": ["Pool", " GYM ", "parking "]},
            {"p_amenities": ["pool", "gym", "parking"], "p_sort_by": "price", "p_sort_order": "desc"}
        ),
        (
            {"sort_by": "area", "sort_order": "asc"},
            {"p_sort_by": "area_sqm", "p_sort_order": "asc"}  # "area" maps to "area_sqm"
        ),
    ])
    @patch('src.agents.property_finder.tools.search_properties.search_properties.supabase')
    def test_parameter_mapping(self, mock_supabase, filters_data, expected_params):
        """Test that filters are correctly mapped to database parameters."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.rpc.return_value.execute.return_value = mock_response

        # Create filters
        filters = PropertySearchFilters(**filters_data)

        # Call the tool
        search_properties.invoke({
            "filters": filters,
            "tool_call_id": "test_call_123"
        })

        # Verify database call parameters
        mock_supabase.rpc.assert_called_once_with("search_properties_rpc", expected_params)

    @patch('src.agents.property_finder.tools.search_properties.search_properties.supabase')
    def test_empty_filters_handling(self, mock_supabase):
        """Test handling of completely empty filters."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.rpc.return_value.execute.return_value = mock_response

        # Create empty filters
        filters = PropertySearchFilters()

        # Call the tool
        search_properties.invoke({
            "filters": filters,
            "tool_call_id": "test_call_123"
        })

        # Verify that default sort parameters are always included
        call_args = mock_supabase.rpc.call_args[0][1]
        assert "p_sort_by" in call_args  # Should have default sort_by
        assert "p_sort_order" in call_args  # Should have default sort_order
        assert call_args["p_sort_by"] == "price"  # Default sort field
        assert call_args["p_sort_order"] == "desc"  # Default sort order

    def test_map_to_property_function(self):
        """Test the _map_to_property helper function."""
        # Test data
        prop_data = {
            "id": "prop-789",
            "title": "Test Property",
            "description": "A test property",
            "price": 250000.0,
            "property_type": "apartment",
            "bedrooms": 2,
            "bathrooms": 1,
            "city": "Alexandria",
            "area_sqm": 100.0,
            "image_url": "https://example.com/test.jpg"
        }
        amenities = ["balcony", "parking"]

        # Call the function
        property_obj = _map_to_property(prop_data, amenities)

        # Verify the result
        assert isinstance(property_obj, Property)
        assert property_obj.id == "prop-789"
        assert property_obj.title == "Test Property"
        assert property_obj.price == 250000.0
        assert property_obj.amenities == ["balcony", "parking"]

    def test_tool_metadata(self):
        """Test that the tool has correct metadata."""
        tool = search_properties
        
        # Check tool name
        assert tool.name == "search_properties"
        
        # Check tool description
        assert "Searches for properties based on the provided filters" in tool.description
        
        # Check tool has input schema
        schema = tool.get_input_schema()
        assert schema is not None
        
        # Check required fields in schema
        schema_fields = schema.model_fields
        assert "filters" in schema_fields
        assert "tool_call_id" in schema_fields
