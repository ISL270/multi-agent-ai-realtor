# Tests

This directory contains the comprehensive test suite for the Real Estate AI project with **86 tests total** - **ALL PASSING** ✅

## Test Structure

```
tests/
├── conftest.py              # Global test configuration and mocking
├── unit/                    # Unit tests for individual tools (70 tests)
│   ├── test_parse_property_search_query.py    # 12 tests
│   ├── test_search_properties.py              # 16 tests
│   ├── test_find_available_slots.py           # 14 tests
│   ├── test_schedule_viewing.py               # 14 tests
│   └── test_render_property_carousel.py       # 14 tests
└── integration/             # Integration tests for end-to-end workflows (16 tests)
    ├── test_property_search_flow_integration.py    # 5 tests
    ├── test_calendar_flow_integration.py           # 5 tests
    └── test_render_carousel_integration.py         # 6 tests
```

## Test Types

### 1. Unit Tests (70 tests)
**LangChain Standard Tests** - Uses `langchain-tests` to automatically validate:
- ✅ Tool has proper name and schema
- ✅ Tool initialization works correctly  
- ✅ Input parameters match declared schema
- ✅ Tool handles invocation properly

**Custom Unit Tests** - Tests specific business logic:
- ✅ Successful operations and data processing
- ✅ Error handling and edge cases
- ✅ API integration (Supabase, Google Calendar, OpenAI)
- ✅ Input validation and parameter mapping
- ✅ Tool metadata and schema validation

### 2. Integration Tests (16 tests)
**End-to-End Workflow Testing**:
- ✅ **Property Search Flow**: Natural language query → parsing → database search
- ✅ **Calendar Flow**: Slot finding → viewing scheduling → event creation
- ✅ **Render Carousel**: Property data → UI rendering → user interaction
- ✅ Realistic data scenarios with proper external dependency mocking
- ✅ Error handling across multiple tool interactions

## Running Tests

### Run All Tests (86 tests)
```bash
pytest tests/ -v
```

### Run Unit Tests Only (70 tests)
```bash
pytest tests/unit/ -v
```

### Run Integration Tests Only (16 tests)
```bash
pytest tests/integration/ -v
```

### Run Specific Test File
```bash
pytest tests/unit/test_search_properties.py -v
pytest tests/integration/test_property_search_flow_integration.py -v
```

## Testing Infrastructure

- **Global Mocking**: Supabase client, Google Calendar API, and OpenAI LLM calls properly mocked in `conftest.py`
- **LangChain Standard Tests**: Automated schema validation and tool initialization testing
- **Custom Unit Tests**: Business logic, error handling, and API integration testing
- **Integration Tests**: End-to-end workflows testing realistic tool interactions
- **Direct Function Testing**: Innovative approach for testing tools with `InjectedState` parameters

## Writing New Tests

### Unit Tests for LangGraph Tools
```python
from langchain_tests.unit_tests import ToolsUnitTests
from unittest.mock import patch, MagicMock

# LangChain Standard Tests
class TestYourToolUnit(ToolsUnitTests):
    @property
    def tool_constructor(self):
        return your_tool
    
    @property
    def tool_invoke_params_example(self):
        return {"param": "value", "tool_call_id": "test_123"}

# Custom Unit Tests
class TestYourToolCustom:
    @patch('src.agents.your_agent.tools.your_tool.external_dependency')
    def test_successful_operation(self, mock_dependency):
        # Mock external dependencies
        mock_dependency.return_value = expected_result
        
        # Test the tool functionality
        result = your_tool.invoke({"param": "value", "tool_call_id": "test"})
        
        # Assert expected behavior
        assert result.content == "expected output"
        mock_dependency.assert_called_once()
```

### Integration Tests for Workflows
```python
from unittest.mock import patch, MagicMock

class TestYourWorkflowIntegration:
    @patch('src.agents.agent1.tools.tool1.external_service')
    @patch('src.agents.agent2.tools.tool2.external_service')
    def test_complete_workflow(self, mock_service1, mock_service2):
        # Mock all external dependencies
        mock_service1.return_value = step1_result
        mock_service2.return_value = step2_result
        
        # Test the complete workflow
        step1_result = tool1.func(input_data, "test_call_id")
        step2_result = tool2.func(step1_result.update["key"], "test_call_id")
        
        # Assert end-to-end behavior
        assert step2_result.update["final_key"] == expected_final_result
```

## Dependencies

- `pytest` - Test framework
- `langchain-tests` - LangChain standard tests
- `unittest.mock` - Built-in mocking utilities
- Standard Python testing libraries
