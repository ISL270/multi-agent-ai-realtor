import logging
from typing import Any, Dict

from langchain.tools import tool
import uuid
from langgraph.graph.ui import UIMessage

from postgrest import APIError

from real_estate_ai.supabase import supabase

from ..parse_property_search_query.property_search_filters import PropertySearchFilters
from .property import Property

logger = logging.getLogger(__name__)


def _map_to_property(prop: Dict[str, Any]) -> Property | None:
    """
    Safely map a database property row to the Property model.
    Returns None if essential fields like 'id' or 'image_url' are missing.
    """
    # Reason: The RPC function might return incomplete data. Using .get() for all fields
    # and checking for essential ones makes the mapping more robust and prevents crashes.
    prop_id = prop.get("id")
    image_url = prop.get("image_url")

    if not prop_id or not image_url:
        logger.warning(f"Skipping property due to missing 'id' or 'image_url'. Data: {prop}")
        return None

    try:
        return Property(
            id=prop_id,
            title=prop.get("title", "Untitled Property"),
            description=prop.get("description"),
            price=float(prop.get("price", 0)),
            property_type=prop.get("property_type"),
            bedrooms=prop.get("bedrooms"),
            bathrooms=prop.get("bathrooms"),
            city=prop.get("city"),
            area_sqm=float(prop.get("area_sqm", 0)) if prop.get("area_sqm") is not None else None,
            image_url=image_url,
            amenities=prop.get("amenities", []),
        )
    except (ValueError, TypeError) as e:
        logger.error(f"Could not parse property data. Error: {e}. Data: {prop}", exc_info=True)
        return None


@tool(parse_docstring=True)
def search_properties(filters: PropertySearchFilters) -> UIMessage:
    """
    Searches for properties in the database using location, price, area, room count, property type, and amenities.

    This function uses a database-side RPC function for efficient filtering, especially for amenities.

    Args:
        filters: An instance of PropertySearchFilters containing the search criteria.

    Returns:
        A UIMessage containing a list of Property objects to be rendered by the frontend.
    """
    try:
        # Validate and normalize input
        amenities = [a.strip().lower() for a in (filters.amenities or []) if a and a.strip()] or None

        sort_by = filters.sort_by if filters.sort_by in ALLOWED_SORT_FIELDS else "price"
        sort_order = filters.sort_order if filters.sort_order in ALLOWED_SORT_ORDERS else "desc"

        params = {
            "p_amenities": amenities,
            "p_city": filters.city,
            "p_min_price": filters.min_price,
            "p_max_price": filters.max_price,
            "p_property_type": filters.property_type,
            "p_bedrooms": filters.bedrooms,
            "p_bathrooms": filters.bathrooms,
            "p_min_area": filters.min_area,
            "p_max_area": filters.max_area,
            "p_sort_by": sort_by,
            "p_sort_order": sort_order,
        }

        # Remove None values to use DB defaults
        params = {k: v for k, v in params.items() if v is not None}

        # Call the RPC function
        response = supabase.rpc("search_properties_rpc", params).execute()

        if not response.data:
            # Return a UIMessage indicating no properties were found
            return {
                "type": "ui",
                "id": str(uuid.uuid4()),
                "name": "Text",
                "props": {"content": "I couldn't find any properties matching your criteria. Would you like to try a different search?"},
                "metadata": {},
            }

        # Map DB rows to Pydantic models, using amenities directly from the RPC result
        properties = [p for p in (_map_to_property(prop) for prop in response.data) if p is not None]

        # Convert Pydantic models to dictionaries for the frontend
        property_dicts = [prop.dict() for prop in properties]

        # Return a dictionary conforming to the UIMessage TypedDict structure
        return {
            "type": "ui",
            "id": str(uuid.uuid4()),
            "name": "PropertyList",
            "props": {"properties": property_dicts},
            "metadata": {},
        }

    except APIError as e:
        logger.error(f"Supabase API Error: {e.message}", exc_info=True)
        return {
            "type": "ui",
            "id": str(uuid.uuid4()),
            "name": "Text",
            "props": {"content": f"I encountered a database error: {e.message}. Please check the system logs."},
            "metadata": {},
        }
    except Exception as e:
        logger.error(f"Error searching properties: {str(e)}", exc_info=True)
        # Return a dictionary conforming to the UIMessage TypedDict structure
        return {
            "type": "ui",
            "id": str(uuid.uuid4()),
            "name": "Text",
            "props": {"content": "Sorry, I encountered an error while searching for properties. Please try again later."},
            "metadata": {},
        }


# Allowed sort fields and orders to avoid unsafe queries
ALLOWED_SORT_FIELDS = {"price", "area_sqm"}
ALLOWED_SORT_ORDERS = {"asc", "desc"}
