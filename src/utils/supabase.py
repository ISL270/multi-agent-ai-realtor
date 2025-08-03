"""
Supabase client initialization and utilities.

This module provides a pre-configured Supabase client instance
that can be imported and used throughout the application.
"""

import os
from typing import Optional
from urllib.parse import urlparse

from supabase import Client, create_client

# Global client instance for lazy initialization
_client: Optional[Client] = None


def validate_supabase_url(url: str) -> str:
    """
    Validate and normalize the Supabase URL.

    Args:
        url: The Supabase URL to validate

    Returns:
        str: The normalized URL with protocol and without trailing slashes

    Raises:
        ValueError: If the URL is empty or invalid
    """
    if not url:
        raise ValueError("Supabase URL cannot be empty")

    # Ensure URL has a protocol
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # Parse the URL to validate it
    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        raise ValueError(f"Invalid Supabase URL: {url}")

    # Normalize the URL (remove trailing slashes)
    return url.rstrip("/")


def initialize_supabase() -> Client:
    """
    Initialize and return a Supabase client.

    Returns:
        Client: Initialized Supabase client

    Raises:
        ValueError: If required environment variables are missing
        RuntimeError: If client initialization fails
    """
    # Load environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    # Validate environment variables
    if not supabase_url or not supabase_key:
        raise ValueError(
            "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY in your .env file."
        )

    try:
        # Validate and normalize the URL
        supabase_url = validate_supabase_url(supabase_url)

        # Initialize Supabase client
        client: Client = create_client(supabase_url, supabase_key)

        # Test the connection with a simple query
        test_connection(client)

        return client

    except Exception as e:
        raise RuntimeError(f"Failed to initialize Supabase client: {str(e)}") from e


def test_connection(client: Client) -> None:
    """
    Test the Supabase connection with a simple query.

    Args:
        client: Initialized Supabase client

    Raises:
        RuntimeError: If the test query fails
    """
    try:
        # Simple connection test with minimal query
        client.table("properties").select("*").limit(1).execute()
    except Exception as e:
        raise RuntimeError(f"Supabase connection test failed: {str(e)}") from e


def get_supabase_client() -> Client:
    """
    Get the Supabase client instance using lazy initialization.

    Returns:
        Client: Initialized Supabase client

    Raises:
        ValueError: If required environment variables are missing
        RuntimeError: If client initialization fails
    """
    global _client
    if _client is None:
        _client = initialize_supabase()
    return _client


# For backward compatibility, expose the client as 'supabase'
# This will be initialized on first access
def __getattr__(name: str) -> Client:
    """Module-level attribute access for backward compatibility."""
    if name == "supabase":
        return get_supabase_client()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
