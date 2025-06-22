"""
Supabase client initialization and utilities.

This module provides a pre-configured Supabase client instance
that can be imported and used throughout the application.
"""

import logging
import os
from urllib.parse import urlparse

from supabase import Client, create_client

# Configure logging
logger = logging.getLogger(__name__)


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
    if not (url.startswith(("http://", "https://"))):
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

    # Log basic info (key is masked for security)
    logger.debug("Initializing Supabase client")
    logger.debug(f"SUPABASE_URL: {supabase_url}")
    logger.debug(f"SUPABASE_KEY present: {'Yes' if supabase_key else 'No'}")

    # Validate environment variables
    if not supabase_url or not supabase_key:
        error_msg = "Missing Supabase credentials. " "Please set SUPABASE_URL and SUPABASE_KEY in your .env file."
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        # Validate and normalize the URL
        supabase_url = validate_supabase_url(supabase_url)

        # Initialize Supabase client
        logger.debug(f"Creating Supabase client for URL: {supabase_url}")
        client: Client = create_client(supabase_url, supabase_key)

        # Test the connection with a simple query
        test_connection(client)

        logger.info("Supabase client initialized successfully")
        return client

    except Exception as e:
        error_msg = f"Failed to initialize Supabase client: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


def test_connection(client: Client) -> None:
    """
    Test the Supabase connection with a simple query.

    Args:
        client: Initialized Supabase client

    Raises:
        RuntimeError: If the test query fails
    """
    try:
        logger.debug("Testing Supabase connection...")
        # Use try/except to handle different response formats
        try:
            # Try the modern response format first (tuple with data and count)
            response = client.table("properties").select("*").limit(1).execute()

            # Check for different response formats
            if isinstance(response, dict):
                # Newer versions return a dict with 'data' and 'count' keys
                if "data" not in response:
                    logger.warning("Supabase response missing 'data' key")
            elif isinstance(response, tuple) and len(response) > 0:
                # Older versions return a tuple of (data, count)
                if not isinstance(response[0], (list, dict)):
                    logger.warning("Unexpected data format in Supabase response")
            else:
                logger.warning(f"Unexpected Supabase response format: {type(response)}")

            logger.debug("Supabase connection test successful")

        except Exception as query_error:
            logger.warning(f"Supabase query test failed: {str(query_error)}")
            # Try a different approach if the first one fails
            try:
                # Try a simpler query to just check connection
                client.table("properties").select("count", count="exact").execute()
                logger.debug("Supabase connection test successful with count query")
            except Exception as count_error:
                logger.error(f"Supabase count query also failed: {str(count_error)}")
                raise RuntimeError(f"Supabase connection test failed: {str(count_error)}") from count_error

    except Exception as e:
        error_msg = f"Supabase connection test failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


# Initialize the global Supabase client
try:
    supabase: Client = initialize_supabase()
except Exception as e:
    logger.critical("Failed to initialize Supabase client. Application may not function correctly.")
    raise
    error_msg = f"Failed to initialize Supabase client: {str(e)}"
    logger.error(error_msg, exc_info=True)
    raise RuntimeError(error_msg) from e
