"""
Pytest configuration and fixtures for the test suite.
"""

import os
import sys
from unittest.mock import MagicMock

# Set mock environment variables before any imports
os.environ.setdefault('SUPABASE_URL', 'https://mock.supabase.co')
os.environ.setdefault('SUPABASE_KEY', 'mock_key_12345678901234567890123456789012')

# Mock the Supabase client at import time
mock_supabase_client = MagicMock()

# Patch the utils.supabase module before it gets imported
if 'utils.supabase' not in sys.modules:
    import utils.supabase
    utils.supabase.supabase = mock_supabase_client
