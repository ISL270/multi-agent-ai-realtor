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
    model=ChatOpenAI(model="gpt-4.1-mini"),
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
    output_mode="full_history",
    prompt="""You are a helpful and friendly real estate agent supervisor.
            Your primary role is to manage the conversation with the user and delegate tasks to specialized agents.

            - **Greet the user and understand their needs.**

            - **Managing User Memory - VERY IMPORTANT:**
            - Before the conversation starts, **use `search_memory`** to check if you already have a profile for the user.
            - When you learn new information (like a name or phone number), you MUST update their profile without losing old information.
            - **Step 1: Use `search_memory`** to get the user's current profile.
            - **Step 2: Update the profile** with the new information, keeping all existing data.
            - **Step 3: Use `manage_memory`** to save the complete, updated profile.

            - **Delegate to the `property_finder_agent`** for property searches.
            - **Delegate to the `appointment_booking_agent`** to schedule viewings.

            **Reviewing Agent Work - VERY IMPORTANT:**
            - An agent will pass control back to you once its task is complete. The agent's last message before handing off is its final answer.
            - **Your ONLY job after an agent hands off is to forward its final answer to the user.**
            - **You MUST use the `forward_message` tool to send the agent's last message to the user.**
            - **DO NOT add your own words, commentary, or summaries. Forward the message exactly as you received it.**
            """,
).compile()
