from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from agentic.tools.rag_tools import search_knowledge_base

# Define the tech support agent
# It has access to the Knowledge Base
tools = [search_knowledge_base]

model = ChatOpenAI(model="gpt-4o-mini")

tech_instructions = """You are a Tech Support Assistant.
Use the 'search_knowledge_base' tool to find answers.
If the tool returns no relevant results or you cannot answer the question based on the tool output,
you MUST respond with "[ESCALATION_REQUIRED] I cannot find an answer to your question in my knowledge base. Connecting you to a human agent..."
Do not make up functionality that isn't in the context.
"""

tech_agent = create_react_agent(model, tools=tools, prompt=tech_instructions)
