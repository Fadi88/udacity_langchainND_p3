from typing import TypedDict, Annotated, Union
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from agentic.agents.billing import billing_agent
from agentic.agents.booking import booking_agent
from agentic.agents.tech_support import tech_agent
from agentic.agents.triage import triage_chain


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# Wrapper nodes for the sub-agents
def billing_node(state: AgentState):
    result = billing_agent.invoke(state)
    return {"messages": result["messages"][-1]}  # Return the last message (response)


def booking_node(state: AgentState):
    result = booking_agent.invoke(state)
    return {"messages": result["messages"][-1]}


def tech_node(state: AgentState):
    result = tech_agent.invoke(state)
    return {"messages": result["messages"][-1]}


def triage_node(state: AgentState):
    # Triage doesn't add messages, just routes.
    # Logic is in the conditional edge.
    # But we need a node to start or we use START.
    # We'll rely on the conditional edge from START or a dedicated node.
    # Let's have a dedicated node to ensure we route correctly.
    # Actually, we can just return state.
    return state


def route_logic(state: AgentState):
    # Run the triage chain on the messages
    classification = triage_chain.invoke({"messages": state["messages"]})
    return classification.destination


# Define the graph
builder = StateGraph(AgentState)

builder.add_node("triage", triage_node)
builder.add_node("billing_agent", billing_node)
builder.add_node("booking_agent", booking_node)
builder.add_node("tech_agent", tech_node)

# Start ---> Triage ---> [Conditional] ---> Agents ---> End
builder.add_edge(START, "triage")

builder.add_conditional_edges(
    "triage",
    route_logic,
    {
        "billing_agent": "billing_agent",
        "booking_agent": "booking_agent",
        "tech_agent": "tech_agent",
    },
)

# After agent speaks, we end the turn
builder.add_edge("billing_agent", END)
builder.add_edge("booking_agent", END)
builder.add_edge("tech_agent", END)

from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# Use SqliteSaver for persistence
# We need to create a connection. check_same_thread=False is needed if shared,
# but for this simple app it's fine.
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

orchestrator = builder.compile(checkpointer=checkpointer)
