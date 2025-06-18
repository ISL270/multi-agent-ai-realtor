import os

from dotenv import load_dotenv
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import create_react_agent

# Explicitly load .env from project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not set in environment or .env file.")


def search_properties(location: str, max_price: float = 500000) -> str:
    """Search for properties in a specific location within a price range.

    Args:
        location: The city or area to search in
        max_price: Maximum price for the properties

    Returns:
        A string with mock search results
    """
    return f"Showing 5 properties in {location} under ${max_price:,}. All properties are amazing with great views!"


class CustomState(MessagesState):
    pass


graph_builder = StateGraph(CustomState)

agent = create_react_agent(
    model="gpt-4.1",
    prompt="I'm an AI assistant for real estate agents. I can help you search for properties and answer questions about them. Please give me a command to search for properties or ask a question about a specific property.",
    tools=[search_properties],
)

graph_builder.add_node("agent", agent)
graph_builder.set_entry_point("agent")
graph = graph_builder.compile()
