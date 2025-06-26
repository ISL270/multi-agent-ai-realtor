import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph_supervisor.handoff import create_forward_message_tool
from langmem import create_manage_memory_tool, create_search_memory_tool

from real_estate_ai.agents.appointment_booking.appointment_booking_agent import (
    appointment_booking_agent,
)
from real_estate_ai.agents.property_finder.property_finder_agent import (
    property_finder_agent,
)
from real_estate_ai.user_profile import UserProfile

# Explicitly load .env from project root (ensures environment variables are available for local/dev runs)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

forward_message = create_forward_message_tool("supervisor")

supervisor = create_supervisor(
    model=ChatOpenAI(model="gpt-4.1"),
    supervisor_name="supervisor",
    agents=[
        property_finder_agent,
        appointment_booking_agent,
    ],
    tools=[
        create_manage_memory_tool(
            schema=UserProfile,
            namespace=("memories"),
            instructions="Extract user profile details (name, job, city, etc.) from the conversation and save them to the UserProfile. Be proactive: if the user mentions a piece of personal information, your job is to capture it.",
        ),
        create_search_memory_tool(namespace=("memories")),
        forward_message,
    ],
    output_mode="last_message",
    prompt="""You are a helpful and friendly real estate agent supervisor.
            Your primary role is to manage the conversation with the user and delegate tasks to specialized agents.
            - **Greet the user and understand their needs.**
            - **Use the `search_memory` tool** to see if you already know the user. If you don't, and you've learned new details like their name, **use the `manage_memory` tool to save them.**
            - **Delegate to the `property_search_agent`** for property searches.
            - **Review the agent's work.** The agent will return its results in the message history. The last message from the agent before it transfers back to you is its final answer.
            - **If the agent's final answer is a complete, user-ready response, you MUST use the `forward_message` tool to send it directly to the user. Do not add any commentary or additional text. Only one message should be sent to the user.**
            - **Delegate to the `calender_agent`** to schedule viewings.
            """,
).compile()
