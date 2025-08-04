"""
Comprehensive unit tests for parse_property_search_query tool.
Includes both LangChain Standard Tests and custom unit tests.
"""

from unittest.mock import MagicMock, patch

import pytest
from langchain_tests.unit_tests import ToolsUnitTests

from src.agents.property_finder.tools.parse_property_search_query.parse_property_search_query import (
    parse_property_search_query,
)
from src.agents.property_finder.tools.parse_property_search_query.property_search_filters import (
    PropertySearchFilters,
)


class TestParsePropertySearchQueryUnit(ToolsUnitTests):
    """
    Standard unit tests for parse_property_search_query tool.

    This class automatically tests:
    - Tool has a name attribute
    - Tool has proper input schema (args_schema)
    - Tool can be initialized correctly
    - Input parameters match the declared schema
    """

    @property
    def tool_constructor(self):
        """Returns the tool class/function to be tested."""
        return parse_property_search_query

    @property
    def tool_invoke_params_example(self):
        """
        Returns example parameters for invoking the tool.
        These parameters must match the tool's input schema.
        """
        return {
            "user_query": "Find me a 3 bedroom apartment in Cairo under $500,000 with a pool",
            "tool_call_id": "test_call_id_123",
        }


class TestParsePropertySearchQueryCustom:
    """Custom unit tests for parse_property_search_query tool logic."""

    @patch("src.agents.property_finder.tools.parse_property_search_query.parse_property_search_query.init_chat_model")
    def test_successful_parsing(self, mock_init_chat_model):
        """Test successful parsing of a property search query."""
        # Mock the LLM response
        mock_filters = PropertySearchFilters(city="Cairo", bedrooms=3, max_price=500000.0, amenities=["pool"])

        mock_llm = MagicMock()
        mock_structured_llm = MagicMock()
        mock_structured_llm.invoke.return_value = mock_filters
        mock_llm.with_structured_output.return_value = mock_structured_llm
        mock_init_chat_model.return_value = mock_llm

        # Call the tool
        result = parse_property_search_query.invoke(
            {
                "user_query": "Find me a 3 bedroom apartment in Cairo under $500,000 with a pool",
                "tool_call_id": "test_call_123",
            }
        )

        # Verify the result
        assert hasattr(result, "update")
        assert "filters" in result.update
        assert "messages" in result.update

        # Verify the filters
        filters = result.update["filters"]
        assert filters.city == "Cairo"
        assert filters.bedrooms == 3
        assert filters.max_price == 500000.0
        assert filters.amenities == ["pool"]

        # Verify LLM was called correctly
        mock_init_chat_model.assert_called_once_with("openai:gpt-4o", temperature=0)
        mock_llm.with_structured_output.assert_called_once_with(PropertySearchFilters)
        mock_structured_llm.invoke.assert_called_once()

    @patch("src.agents.property_finder.tools.parse_property_search_query.parse_property_search_query.init_chat_model")
    def test_error_handling(self, mock_init_chat_model):
        """Test error handling when LLM call fails."""
        # Mock LLM to raise an exception
        mock_llm = MagicMock()
        mock_llm.with_structured_output.side_effect = Exception("API Error")
        mock_init_chat_model.return_value = mock_llm

        # Call the tool
        result = parse_property_search_query.invoke(
            {"user_query": "Find me a property", "tool_call_id": "test_call_123"}
        )

        # Verify error handling
        assert hasattr(result, "update")
        assert "messages" in result.update

        # Check that error message is included
        messages = result.update["messages"]
        assert len(messages) == 1
        assert "Error parsing search query" in messages[0].content

    @pytest.mark.parametrize(
        "user_query,expected_fields",
        [
            ("2 bedroom apartment in Alexandria", {"bedrooms": 2, "city": "Alexandria"}),
            ("villa under $1,000,000", {"property_type": "villa", "max_price": 1000000}),
            ("property with gym and parking", {"amenities": ["gym", "parking"]}),
        ],
    )
    @patch("src.agents.property_finder.tools.parse_property_search_query.parse_property_search_query.init_chat_model")
    def test_various_query_patterns(self, mock_init_chat_model, user_query, expected_fields):
        """Test parsing of various query patterns."""
        # Create mock filters with expected fields
        mock_filters = PropertySearchFilters(**expected_fields)

        mock_llm = MagicMock()
        mock_structured_llm = MagicMock()
        mock_structured_llm.invoke.return_value = mock_filters
        mock_llm.with_structured_output.return_value = mock_structured_llm
        mock_init_chat_model.return_value = mock_llm

        # Call the tool
        result = parse_property_search_query.invoke({"user_query": user_query, "tool_call_id": "test_call_123"})

        # Verify the result contains expected fields
        assert hasattr(result, "update")
        filters = result.update["filters"]

        for field, expected_value in expected_fields.items():
            assert getattr(filters, field) == expected_value

    def test_tool_metadata(self):
        """Test that the tool has correct metadata."""
        tool = parse_property_search_query

        # Check tool name
        assert tool.name == "parse_property_search_query"

        # Check tool description
        assert "Parses a natural language property search query" in tool.description

        # Check tool has input schema
        schema = tool.get_input_schema()
        assert schema is not None

        # Check required fields in schema
        schema_fields = schema.model_fields
        assert "user_query" in schema_fields
        assert "tool_call_id" in schema_fields
