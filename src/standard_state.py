from typing import Annotated, List, Optional

from langgraph.graph.ui import AnyUIMessage, ui_message_reducer
from langgraph.prebuilt.chat_agent_executor import AgentState

from agents.property_finder.parse_query.property_search_filters import (
    PropertySearchFilters,
)
from agents.property_finder.query_supabase.property import Property


class StandardState(AgentState):
    properties: List[Property]
    filters: Optional[PropertySearchFilters] = None
    ui: Annotated[List[AnyUIMessage], ui_message_reducer]
