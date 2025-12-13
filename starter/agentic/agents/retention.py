from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from agentic.tools.cultpass_tools import get_retention_policy, lookup_user

# Define the retention agent
# It has access to user lookup and retention policy
tools = [
    lookup_user,
    get_retention_policy,
]

model = ChatOpenAI(model="gpt-4o-mini")

# System prompt to guide the agent to be empathetic and try to retain the user
# properly we would use a system_message arg in create_react_agent if supported or wrap the model
# For simple react agent, we rely on the tool description and generic behavior, OR we can pass state_modifier.

retention_instructions = """You are a Retention Specialist for CultPass. 
Your goal is to understand why a user wants to cancel and offer helpful alternatives (like pausing) or explain the policy.
1. Check the user's details first if not known.
2. Use 'get_retention_policy' to know what you can offer.
3. Be empathetic but firm on policy. Do NOT process the actual cancellation yourself (instruct them to do it in-app), 
   but try to convince them to stay or pause instead.
"""

retention_agent = create_react_agent(model, tools=tools, prompt=retention_instructions)
