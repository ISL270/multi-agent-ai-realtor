"""
Unit tests for parse_property_search_query tool using LangChain Standard Tests.
"""

from langchain_tests.unit_tests import ToolsUnitTests

from src.agents.property_finder.tools.parse_property_search_query.parse_property_search_query import (
    parse_property_search_query,
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
            "tool_call_id": "test_call_id_123"
        }
