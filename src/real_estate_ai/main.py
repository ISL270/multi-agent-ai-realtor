import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph_supervisor.handoff import create_forward_message_tool
from langmem import create_manage_memory_tool, create_search_memory_tool

from real_estate_ai.models import UserProfile
from real_estate_ai.tools import parse_property_search_query, search_properties

# Explicitly load .env from project root (ensures environment variables are available for local/dev runs)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

model = ChatOpenAI(model="gpt-4.1")


def scheduleViewing():
    """
    Schedule a viewing for a property.
    """
    return "Your Viewing is scheduled successfully tomorrow at 10 AM"


calender_agent = create_react_agent(
    model=model,
    tools=[scheduleViewing],
    prompt="""You are a specialized real estate calender assistant.""",
    name="calender_agent",
)


property_search_agent = create_react_agent(
    model=model,
    prompt="""You are a specialized real estate property search assistant.

            Your primary goal is to help users find properties that match their criteria.

            Given a user's request, you must follow these steps strictly:
            1. Use the `parse_property_search_query` tool to extract structured search criteria from the user's message.
            2. Use the `search_properties` tool with the extracted criteria to find matching properties.
            3. **Present the search results clearly and concisely in a user-friendly format.** Your response should be complete and ready to be sent directly to the user.

            Do not ask for clarification. Complete the full sequence of actions before concluding your turn.
            """,
    tools=[parse_property_search_query, search_properties],
    name="property_search_agent",
)


forward_message = create_forward_message_tool("supervisor")

supervisor = create_supervisor(
    model=model,
    supervisor_name="supervisor",
    agents=[
        property_search_agent,
        calender_agent,
    ],
    tools=[
        create_manage_memory_tool(
            schema=UserProfile,
            namespace=("memories"),
            instructions="Extract user profile information",
        ),
        create_search_memory_tool(namespace=("memories")),
        forward_message,
    ],
    output_mode="last_message",
    prompt="""You are a helpful and friendly real estate agent supervisor.
            Your primary role is to manage the conversation with the user and delegate tasks to specialized agents.
            - **Greet the user and understand their needs.**
            - **Use the `search_memory` tool** to see if you already know the user.
            - **Delegate to the `property_search_agent`** for property searches.
            - **Review the agent's work.** The agent will return its results in the message history. The last message from the agent before it transfers back to you is its final answer.
            - **If the agent's final answer is a complete, user-ready response, you MUST use the `forward_message` tool to send it directly to the user. Do not add any commentary or additional text. Only one message should be sent to the user.**
            - **Use the `manage_memory` tool to save new user details.**
            - **Delegate to the `calender_agent`** to schedule viewings.
            """,
).compile()
