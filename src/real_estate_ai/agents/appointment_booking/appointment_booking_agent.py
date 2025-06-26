from langgraph.prebuilt import create_react_agent


def scheduleViewing():
    """
    Schedule a viewing for a property.
    """
    return "Your Viewing is scheduled successfully tomorrow at 10 AM"


appointment_booking_agent = create_react_agent(
    model="openai:gpt-4.1",
    prompt="""You are a specialized real estate calender assistant.""",
    name="appointment_booking_agent",
    tools=[scheduleViewing],
)
