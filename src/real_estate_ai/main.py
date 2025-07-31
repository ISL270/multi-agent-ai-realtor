import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph_supervisor.handoff import create_forward_message_tool
from langmem import create_manage_memory_tool, create_search_memory_tool

from .agents.appointment_booking.appointment_booking_agent import (
    appointment_booking_agent,
)
from .agents.property_finder.property_finder import property_finder
from .standard_state import StandardState
from .user_profile import UserProfile

# Explicitly load .env from project root (ensures environment variables are available for local/dev runs)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

forward_message = create_forward_message_tool("supervisor")

supervisor = create_supervisor(
    model=ChatOpenAI(model="gpt-4.1-mini"),
    supervisor_name="supervisor",
    state_schema=StandardState,
    agents=[
        property_finder,
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

            - **Managing User Memory - VERY IMPORTANT:**
            - Before the conversation starts, **use `search_memory`** to check if you already have a profile for the user.
            - When you learn new information (like a name or phone number), you MUST update their profile without losing old information.
            - **If no existing profile is found:** Use `manage_memory` to CREATE a new profile with all the information you've learned.
            - **If an existing profile is found:** Use `manage_memory` to UPDATE the existing profile by providing the memory ID from the search results and including both old and new information in the updated profile.

            - **Delegate to the `property_finder`** for property searches. Messages from this agent are handled automatically. You can continue the conversation naturally after it finishes.
            - **Delegate to the `appointment_booking_agent`** to schedule viewings.

            **Reviewing Agent Work - VERY IMPORTANT:**
            - When the `appointment_booking_agent` passes control back to you, its task is complete. The agent's last message before handing off is its final answer.
            - **Your ONLY job after the `appointment_booking_agent` hands off is to forward its final answer to the user.**
            - **You MUST use the `forward_message` tool to send the `appointment_booking_agent`'s last message to the user.**
            - **DO NOT add your own words, commentary, or summaries. Forward the message exactly as you received it.**
            """,
).compile()
