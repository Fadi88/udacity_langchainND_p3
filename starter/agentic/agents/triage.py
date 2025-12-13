from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# Define the routing model
class RouteQuery(BaseModel):
    """Route user query to the most relevant agent."""

    destination: Literal[
        "billing_agent", "booking_agent", "tech_agent", "retention_agent"
    ] = Field(
        ...,
        description="The agent to route the query to. Options: 'billing_agent' for payment/subscription status, 'booking_agent' for reservations, 'tech_agent' for technical/how-to, 'retention_agent' for cancellation/pause requests.",
    )
    sentiment: Literal["Positive", "Neutral", "Negative", "Frustrated"] = Field(
        "Neutral", description="The tone of the user's message."
    )
    urgency: Literal["Low", "Medium", "High", "Critical"] = Field(
        "Low", description="The urgency level of the request."
    )


system_prompt = """You are a Triage Agent for CultPass.
Your job is to classify the incoming user query and route it to the appropriate specialist agent.
- Billing Agent: For subscription status, upgrades, payment issues (NOT cancellations).
- Booking Agent: For booking classes, checking schedules, cancelling ONE reservation.
- Tech Agent: For technical issues (login, app crash), general how-to questions.
- Retention Agent: For subscription CANCELLATION or PAUSE requests.

Also determine the user's Sentiment and Urgency.
- Sentiment: Look for keywords like "angry", "thanks", "broken", "love".
- Urgency: Look for time-sensitive words like "now", "immediately", "today".

Select the best destination based on the user's latest message.
"""

prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("human", "{messages}")]
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
triage_chain = prompt | llm.with_structured_output(RouteQuery)
