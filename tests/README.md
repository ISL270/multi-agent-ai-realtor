# Tests

This directory contains the test suite for the Real Estate AI project.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_parse_property_search_query.py           # Basic standard tests
│   └── test_parse_property_search_query_comprehensive.py  # Standard + custom tests
├── integration/             # Integration tests (to be added)
├── e2e/                    # End-to-end tests (to be added)
└── fixtures/               # Test data and mocks (to be added)
```

## Test Types

### 1. LangChain Standard Tests
Uses `langchain-tests` to automatically validate:
- ✅ Tool has proper name and schema
- ✅ Tool initialization works correctly  
- ✅ Input parameters match declared schema
- ✅ Tool handles invocation properly

### 2. Custom Unit Tests
Tests specific business logic:
- ✅ Successful query parsing
- ✅ Error handling
- ✅ Various query patterns
- ✅ Tool metadata validation

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Unit Tests Only
```bash
pytest tests/unit/
```

### Run Specific Test File
```bash
pytest tests/unit/test_parse_property_search_query.py -v
```

### Run Tests with Coverage
```bash
pytest --cov=src tests/
```

### Run Tests by Marker
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m "not slow"    # Skip slow tests
```

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests

## Writing New Tests

### For Tools (using Standard Tests)
```python
from langchain_tests.unit_tests import ToolsUnitTests

class TestYourToolUnit(ToolsUnitTests):
    @property
    def tool_constructor(self):
        return your_tool
    
    @property
    def tool_invoke_params_example(self):
        return {"param": "value", "tool_call_id": "test_123"}
```

### Custom Unit Tests
```python
import pytest
from unittest.mock import patch, MagicMock

class TestYourToolCustom:
    @patch('your.module.dependency')
    def test_your_functionality(self, mock_dependency):
        # Test implementation
        pass
```

## Dependencies

- `pytest` - Test framework
- `langchain-tests` - LangChain standard tests
- `pytest-mock` - Mocking utilities
- `pytest-asyncio` - Async test support
