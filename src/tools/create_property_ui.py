import uuid
from typing import Annotated

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.graph.ui import push_ui_message
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from standard_state import StandardState


@tool(parse_docstring=True)
def create_property_ui(
    state: Annotated[StandardState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Creates a property carousel UI from properties in state and returns an AI message.
    
    This tool should be called after properties have been found and populated in the state.
    It creates a PropertyCarousel UI component and generates an appropriate AI response message.
    
    Args:
        state: The current graph state containing properties (injected automatically).
        tool_call_id: The tool call ID (injected automatically).
    """
    try:
        properties = state.get("properties", [])
        filters = state.get("filters")
        
        if not properties:
            error_message = "No properties available to display."
            return Command(
                update={
                    "messages": [ToolMessage(content=error_message, tool_call_id=tool_call_id)]
                }
            )
        
        # Convert properties to dictionaries for UI component
        properties_as_dicts = [prop.model_dump() for prop in properties]
        
        # Create AI message
        property_count = len(properties)
        if property_count == 1:
            ai_content = f"I found {property_count} property that matches your criteria:"
        else:
            ai_content = f"I found {property_count} properties that match your criteria:"
            
        # Add filter summary if available
        if filters:
            filter_parts = []
            if filters.city:
                filter_parts.append(f"in {filters.city}")
            if filters.min_price or filters.max_price:
                price_range = []
                if filters.min_price:
                    price_range.append(f"min ${filters.min_price:,.0f}")
                if filters.max_price:
                    price_range.append(f"max ${filters.max_price:,.0f}")
                filter_parts.append(f"price range: {' - '.join(price_range)}")
            if filters.bedrooms:
                filter_parts.append(f"{filters.bedrooms}+ bedrooms")
            if filters.property_type:
                filter_parts.append(f"type: {filters.property_type}")
                
            if filter_parts:
                ai_content += f" ({', '.join(filter_parts)})"
        
        ai_message = AIMessage(
            id=str(uuid.uuid4()),
            content=ai_content,
        )
        
        # Push UI message linked to the AI message
        push_ui_message(
            "property_carousel",
            {"properties": properties_as_dicts},
            message=ai_message
        )
        
        # Create success tool message
        success_message = f"Successfully created property carousel UI for {property_count} properties."
        
        return Command(
            update={
                "messages": [
                    ToolMessage(content=success_message, tool_call_id=tool_call_id),
                    ai_message
                ]
            }
        )
        
    except Exception as e:
        error_message = f"Error creating property UI: {str(e)}"
        return Command(
            update={
                "messages": [ToolMessage(content=error_message, tool_call_id=tool_call_id)]
            }
        )
