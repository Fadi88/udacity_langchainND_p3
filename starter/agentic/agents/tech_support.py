from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from agentic.tools.rag_tools import search_knowledge_base

# Define the tech support agent
# It has access to the Knowledge Base
tools = [search_knowledge_base]

model = ChatOpenAI(model="gpt-4o-mini")

tech_agent = create_react_agent(model, tools=tools)
