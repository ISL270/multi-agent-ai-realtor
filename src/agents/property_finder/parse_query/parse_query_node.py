"""Graph node: parse the latest user message into structured filters."""

import logging

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from standard_state import StandardState

from agents.property_finder.parse_query.property_search_filters import PropertySearchFilters

logger = logging.getLogger(__name__)


def parse_query_node(state: StandardState):
    # Get the latest human message (not just the latest message)
    human_messages = [msg for msg in state["messages"] if msg.type == "human"]
    if not human_messages:
        logger.warning("No human messages found in conversation history")
        return {"filters": None}

    property_query = human_messages[-1].content

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

    llm = init_chat_model("openai:gpt-4.1", temperature=0)
    structured_llm = llm.with_structured_output(PropertySearchFilters)

    filters: PropertySearchFilters = structured_llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=property_query),
        ]
    )

    return {"filters": filters}
