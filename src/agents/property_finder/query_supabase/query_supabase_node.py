import logging
import uuid
from typing import Any, Dict, List

from langchain_core.messages import AIMessage
from langgraph.graph.ui import push_ui_message

from agents.property_finder.query_supabase.property import Property
from standard_state import StandardState
from utils.supabase import supabase

logger = logging.getLogger(__name__)


def query_supabase_node(state: StandardState):
    """
    Searches for properties in the database using location, price, area, room count, property type, and amenities.

    This function uses a database-side RPC function for efficient filtering, especially for amenities.

    Args:
        state: The current graph state, containing the search filters.
    """
    filters = state.get("filters")
    if not filters:
        logger.warning("No filters found in state, returning empty list.")
        return {"properties": []}

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

        # Remove None values to use DB defaults, but always keep at least one parameter
        # to disambiguate between multiple RPC function signatures
        params = {k: v for k, v in params.items() if v is not None}

        # Ensure we always have at least one parameter to avoid function ambiguity
        if not params:
            params = {"p_city": None}

        # Call the RPC function
        response = supabase.rpc("search_properties_rpc", params).execute()

        if not response.data:
            return {"properties": []}

        # Map DB rows to models, using amenities directly from the RPC result
        properties = [_map_to_property(prop, prop.get("amenities", [])) for prop in response.data]

        # Convert Pydantic models to dicts for JSON serialization to the frontend.
        # Note: .dict() is for Pydantic v1. If using v2, this would be .model_dump().
        properties_as_dicts = [p.dict() for p in properties]

        message_content = f"I found {len(properties)} properties matching your criteria."
        if len(properties) == 1:
            message_content = "I found 1 property matching your criteria."

        message = AIMessage(
            id=str(uuid.uuid4()),
            content=message_content,
        )

        # Try to push UI message, but don't fail if it's not in a runnable context
        try:
            push_ui_message(
                "property_carousel",
                {"properties": properties_as_dicts},
                message=message,
            )
        except Exception as ui_error:
            logger.warning(f"Failed to push UI message: {str(ui_error)}")

        return {"properties": properties, "messages": [message]}
    except Exception as e:
        logger.error(f"Error searching properties: {str(e)}", exc_info=True)
        return {"properties": []}


def _map_to_property(prop: Dict[str, Any], amenities: List[str]) -> Property:
    """
    Map a database property row to the Property model, including amenities.
    Expects prop to already have an 'image_url' field (non-optional).
    # Reason: The schema now guarantees a single image_url per property.
    """
    return Property(
        id=prop["id"],
        title=prop.get("title", "Untitled Property"),
        description=prop.get("description"),
        price=float(prop.get("price", 0)),
        property_type=prop.get("property_type"),
        bedrooms=prop.get("bedrooms"),
        bathrooms=prop.get("bathrooms"),
        city=prop.get("city"),
        area_sqm=float(prop.get("area_sqm", 0)) if prop.get("area_sqm") is not None else None,
        image_url=prop["image_url"],
        amenities=amenities or [],
    )


# Allowed sort fields and orders to avoid unsafe queries
ALLOWED_SORT_FIELDS = {"price", "area_sqm"}
ALLOWED_SORT_ORDERS = {"asc", "desc"}
