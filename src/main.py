import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph_supervisor.handoff import create_forward_message_tool
from langmem import create_manage_memory_tool, create_search_memory_tool

from agents.appointment_booking.appointment_booking_agent import (
    appointment_booking_agent,
)
from agents.property_finder.property_finder_agent import property_finder_agent
from standard_state import StandardState
from tools.create_property_ui import create_property_ui
from user_profile import UserProfile

# Explicitly load .env from project root (ensures environment variables are available for local/dev runs)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

forward_message = create_forward_message_tool("supervisor")

supervisor = create_supervisor(
    model=ChatOpenAI(model="gpt-4.1-mini"),
    supervisor_name="supervisor",
    state_schema=StandardState,
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
        create_property_ui,
    ],
    output_mode="full_history",
    prompt="""You are a helpful and friendly real estate agent supervisor.
            Your primary role is to manage the conversation with the user and delegate tasks to specialized agents.

            - **Greet the user and understand their needs.**

            - **Managing User Memory - VERY IMPORTANT:**
            - Before the conversation starts, **use `search_memory`** to check if you already have a profile for the user.
            - When you learn new information (like a name or phone number), you MUST update their profile without losing old information.
            - **If no existing profile is found:** Use `manage_memory` to CREATE a new profile with all the information you've learned.
            - **If an existing profile is found:** Use `manage_memory` to UPDATE the existing profile by providing the memory ID from the search results and including both old and new information in the updated profile.

            - **Delegate to the `property_finder_agent`** for property searches.
            - **Delegate to the `appointment_booking_agent`** to schedule viewings.

            **Handling Property Search Results - VERY IMPORTANT:**
            - When the `property_finder_agent` successfully finds properties and updates the state, you MUST:
              1. Use the `create_property_ui` tool to generate the property carousel UI and AI response message
              2. This tool will automatically create the UI display and generate an appropriate response message
              3. The tool ensures proper UI-message linking by using `push_ui_message()` in the correct context
            - **DO NOT manually create property summaries or descriptions - let the `create_property_ui` tool handle this.**
            - **Simply use `create_property_ui` after the property_finder_agent has populated the state with properties.**

            **Reviewing Agent Work - VERY IMPORTANT:**
            - When the `appointment_booking_agent` passes control back to you, its task is complete. The agent's last message before handing off is its final answer.
            - **Your ONLY job after the `appointment_booking_agent` hands off is to forward its final answer to the user.**
            - **You MUST use the `forward_message` tool to send the `appointment_booking_agent`'s last message to the user.**
            - **DO NOT add your own words, commentary, or summaries. Forward the message exactly as you received it.**
            """,
).compile()
