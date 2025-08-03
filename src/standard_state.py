from typing import Annotated, List, Optional

from langgraph.graph.ui import AnyUIMessage, ui_message_reducer
from langgraph.prebuilt.chat_agent_executor import AgentState
from pydantic import Field

from agents.property_finder.tools.parse_property_search_query.property_search_filters import (
    PropertySearchFilters,
)
from agents.property_finder.tools.search_properties.property import Property


class StandardState(AgentState):
    properties: List[Property] = Field(default_factory=list)
    filters: Optional[PropertySearchFilters] = Field(default=None)
    ui: Annotated[List[AnyUIMessage], ui_message_reducer] = Field(default_factory=list)
