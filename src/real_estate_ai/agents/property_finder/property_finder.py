from langgraph.graph import StateGraph

from src.real_estate_ai.standard_state import StandardState

from .parse_query.parse_query_node import parse_query_node
from .query_supabase.query_supabase_node import query_supabase_node

workflow = StateGraph(StandardState).add_sequence(
    [
        parse_query_node,
        query_supabase_node,
    ]
)

workflow.set_entry_point("parse_query_node")

property_finder = workflow.compile(name="property_finder")
