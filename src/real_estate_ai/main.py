import os

from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

from real_estate_ai.tools import parse_property_search_query, search_properties

# Explicitly load .env from project root (ensures environment variables are available for local/dev runs)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

# Validate that the OpenAI API key is available (required for model access)
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not set in environment or .env file.")


class State(AgentState):
    pass


# Build the agent graph using LangGraph's StateGraph
# The agent node is created with a custom prompt and attached tools for property search and query parsing
graph_builder = StateGraph(State)

agent = create_react_agent(
    model="gpt-4.1",
    prompt="You are a helpful real estate agent assistant. You can help users search for properties and answer questions about them.",
    tools=[parse_property_search_query, search_properties],
)

graph_builder.add_node("agent", agent)
graph_builder.set_entry_point("agent")

graph = graph_builder.compile()
