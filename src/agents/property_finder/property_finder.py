from langgraph.graph import StateGraph

from agents.property_finder.parse_query.parse_query_node import parse_query_node
from agents.property_finder.query_supabase.query_supabase_node import (
    query_supabase_node,
)
from standard_state import StandardState

workflow = StateGraph(StandardState).add_sequence(
    [
        parse_query_node,
        query_supabase_node,
    ]
)

workflow.set_entry_point("parse_query_node")

property_finder = workflow.compile(name="property_finder")
