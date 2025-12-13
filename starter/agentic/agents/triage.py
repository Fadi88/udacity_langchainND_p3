from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# Define the routing model
class RouteQuery(BaseModel):
    """Route user query to the most relevant agent."""

    destination: Literal["billing_agent", "booking_agent", "tech_agent"] = Field(
        ...,
        description="The agent to route the query to. Options: 'billing_agent' for subscription/payment, 'booking_agent' for reservations/classes, 'tech_agent' for technical/how-to/app issues.",
    )


system_prompt = """You are a Triage Agent for CultPass.
Your job is to classify the incoming user query and route it to the appropriate specialist agent.
- Billing Agent: For subscription status, upgrades, cancellations, refunds, payment issues.
- Booking Agent: For booking classes, checking schedules, cancelling reservations, waitlists.
- Tech Agent: For technical issues (login, app crash), general how-to questions, and knowledge base inquiries.

Select the best destination based on the user's latest message.
"""

prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("human", "{messages}")]
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
triage_chain = prompt | llm.with_structured_output(RouteQuery)
