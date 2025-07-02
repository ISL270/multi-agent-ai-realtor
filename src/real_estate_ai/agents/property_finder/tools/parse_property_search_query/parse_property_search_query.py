from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

from .property_search_filters import PropertySearchFilters


@tool(parse_docstring=True)
def parse_property_search_query(user_query: str) -> PropertySearchFilters:
    """
    Parses a natural language property search query and returns structured filters.

    Args:
        user_query (str): The user's search request in natural language.
    """
    system_prompt = (
        "You are a helpful assistant that extracts structured search filters from real estate search queries. "
        "Given a user request, return a `PropertySearchFilters` object with as many of these fields as possible: "
        "city (str), max_price (float), min_price (float), bedrooms (int), bathrooms (int), "
        "property_type (str), amenities (list of str), min_area (float), max_area (float), listing_date (str), "
        "sort_by (str: 'price' or 'area'), sort_order (str: 'asc' or 'desc'). "
        "If the user query requests sorting (e.g., 'from cheapest', 'largest area', 'order by price'), extract the appropriate sort_by and sort_order. "
        "If the user query implies sorting (e.g., 'best', 'most expensive', 'biggest', 'cheapest'), infer the most appropriate sorting. "
        "If a field is missing, omit it from the output."
    )
    llm = init_chat_model(
        "openai:gpt-4.1",
        temperature=0,
    )
    structured_llm = llm.with_structured_output(PropertySearchFilters)
    return structured_llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query),
        ]
    )
