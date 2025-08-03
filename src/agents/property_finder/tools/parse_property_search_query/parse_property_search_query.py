from typing import Annotated

from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import InjectedToolCallId
from langgraph.types import Command

from .property_search_filters import PropertySearchFilters


@tool(parse_docstring=True)
def parse_property_search_query(
    user_query: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    """
    Parses a natural language property search query and returns structured filters.
    Updates the state with the parsed filters.

    Args:
        user_query (str): The user's search request in natural language.
        tool_call_id: The tool call ID (injected automatically).
    """
    system_prompt = (
        "You are a helpful assistant that extracts structured search filters from real estate search queries. "
        "Given a user request, return a JSON object with as many of these fields as possible: "
        "city (str), max_price (float), min_price (float), bedrooms (int), bathrooms (int), "
        "property_type (str), amenities (list of str), min_area (float), max_area (float), listing_date (str), "
        "sort_by (str: 'price' or 'area'), sort_order (str: 'asc' or 'desc'). "
        "If the user query requests sorting (e.g., 'from cheapest', 'largest area', 'order by price'), extract the appropriate sort_by and sort_order. "
        "If the user query implies sorting (e.g., 'best', 'most expensive', 'biggest', 'cheapest'), infer the most appropriate sorting. "
        "If a field is missing, omit it from the output."
    )
    try:
        llm = init_chat_model("openai:gpt-4o", temperature=0)
        structured_llm = llm.with_structured_output(PropertySearchFilters)

        filters = structured_llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query),
            ]
        )

        # Create success message
        success_message = f"Successfully parsed search query: {user_query}"

        return Command(
            update={
                "filters": filters,
                "messages": [ToolMessage(content=success_message, tool_call_id=tool_call_id)],
            }
        )
    except Exception as e:
        error_message = f"Error parsing search query: {str(e)}"
        return Command(update={"messages": [ToolMessage(content=error_message, tool_call_id=tool_call_id)]})
