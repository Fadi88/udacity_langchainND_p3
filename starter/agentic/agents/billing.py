from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from agentic.tools.cultpass_tools import (
    lookup_user,
    get_subscription_status,
    update_subscription,
    get_user_reservations,
)

# Define the billing agent
# It has access to subscription tools and user lookup
tools = [
    lookup_user,
    get_subscription_status,
    update_subscription,
    get_user_reservations,
]

model = ChatOpenAI(model="gpt-4o-mini")

billing_agent = create_react_agent(model, tools=tools)
