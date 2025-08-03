from typing import Annotated, Any, Dict, List

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command

from utils.supabase import supabase

from ..parse_property_search_query.property_search_filters import PropertySearchFilters
from .property import Property


@tool(parse_docstring=True)
def search_properties(
    filters: PropertySearchFilters,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Searches for properties based on the provided filters and updates the state.

    This tool executes a search query against the Supabase database using the
    structured filters provided. It then updates the shared graph state with the
    retrieved properties and the filters used for the search.

    Args:
        filters: A Pydantic model containing the structured search criteria.
        tool_call_id: The ID of the tool call, injected by LangGraph.

    Returns:
        A Command object to update the graph's state with the new properties and filters.
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

        # Remove None values to use DB defaults, but always keep at least one parameter
        # to disambiguate between multiple RPC function signatures
        params = {k: v for k, v in params.items() if v is not None}

        # Ensure we always have at least one parameter to avoid function ambiguity
        if not params:
            params["p_city"] = None

        # Call the RPC function
        response = supabase.rpc("search_properties_rpc", params).execute()

        if not response.data:
            success_message = "No properties found matching your criteria."
            return Command(
                update={
                    "properties": [],
                    "filters": filters,
                    "messages": [ToolMessage(content=success_message, tool_call_id=tool_call_id)],
                }
            )

        # Map DB rows to models, using amenities directly from the RPC result
        properties = [_map_to_property(prop, prop.get("amenities", [])) for prop in response.data]

        # Update state with found properties and filters
        success_message = f"Found {len(properties)} properties matching your criteria."

        return Command(
            update={
                "properties": properties,
                "filters": filters,
                "messages": [ToolMessage(content=success_message, tool_call_id=tool_call_id)],
            }
        )
    except Exception as e:
        error_message = f"An error occurred while searching for properties: {e}"
        return Command(
            update={
                "properties": [],
                "filters": filters,
                "messages": [ToolMessage(content=error_message, tool_call_id=tool_call_id)],
            }
        )


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
