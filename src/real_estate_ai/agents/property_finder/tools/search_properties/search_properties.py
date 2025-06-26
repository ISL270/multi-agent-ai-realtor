import logging
from typing import Any, Dict, List

from langchain.tools import tool

from real_estate_ai.supabase import supabase

from ..parse_property_search_query.property_search_filters import PropertySearchFilters
from .property import Property

logger = logging.getLogger(__name__)


def _get_property_images(property_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch images for multiple properties in a single query."""
    if not property_ids:
        return {}

    try:
        response = (
            supabase.table("property_images")
            .select("property_id, url, is_primary")
            .in_("property_id", property_ids)
            .limit(500)
            .execute()
        )

        images = {}
        data = response.data or []

        for img in data:
            images.setdefault(img["property_id"], []).append(
                {"url": img["url"], "is_primary": img.get("is_primary", False)}
            )
        return images
    except Exception as e:
        logger.error(f"Error fetching property images: {str(e)}", exc_info=True)
        return {}


def _map_to_property(prop: Dict[str, Any], images: List[Dict[str, Any]], amenities: List[str]) -> Property:
    """Map database property to Property model, including amenities."""
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
        images=images or [],
        amenities=amenities or [],
    )


@tool(parse_docstring=True)
def search_properties(filters: PropertySearchFilters) -> List[Property]:
    """
    Searches for properties in the database using location, price, area, room count, property type, and amenities.

    This function uses a database-side RPC function for efficient filtering, especially for amenities.

    Args:
        filters: An instance of PropertySearchFilters containing the search criteria.

    Returns:
        List of Property objects matching the search criteria.
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
            return []

        # Fetch images for returned properties
        property_ids = [prop["id"] for prop in response.data]
        property_images = _get_property_images(property_ids)

        # Map DB rows to models, using amenities directly from the RPC result
        return [
            _map_to_property(prop, property_images.get(prop["id"], []), prop.get("amenities", []))
            for prop in response.data
        ]
    except Exception as e:
        logger.error(f"Error searching properties: {str(e)}", exc_info=True)
        return []


# Allowed sort fields and orders to avoid unsafe queries
ALLOWED_SORT_FIELDS = {"price", "area_sqm"}
ALLOWED_SORT_ORDERS = {"asc", "desc"}
