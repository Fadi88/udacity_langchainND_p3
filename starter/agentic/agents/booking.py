from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from agentic.tools.cultpass_tools import (
    lookup_user,
    get_user_reservations,
    cancel_reservation,
    book_reservation,
)

# Define the booking agent
# It has access to reservation tools and user lookup
tools = [lookup_user, get_user_reservations, cancel_reservation, book_reservation]

model = ChatOpenAI(model="gpt-4o-mini")

booking_agent = create_react_agent(model, tools=tools)
