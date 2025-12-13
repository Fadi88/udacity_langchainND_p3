# CultPass Support Agent

A Multi-Agent AI Support System built with **LangChain** and **LangGraph**. It routes customer queries to specialized agents, manages persistent state, and integrates with product and knowledge databases.

## Features
- **Smart Routing**: Triage agent directs user queries to `Billing`, `Booking`, or `Tech Support`.
- **RAG Powered**: Tech support agent answers from a Knowledge Base (`udahub.db`).
- **Tool Use**: Agents can look up users, check subscriptions, book classes, and cancel reservations.
- **Persistence**: Remembers user context across chat sessions using `SqliteSaver`.
- **Audit Logging**: All interactions are logged to `TicketMessage` in the DB.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Variables**:
   Create a `.env` file with your OpenAI API key:
   ```env
   OPENAI_API_KEY="sk-..."
   # If using Vocareum/Udacity key:
   # OPENAI_API_BASE="https://openai.vocareum.com/v1"
   ```
3. **Initialize Database**:
   (Optional) If you want to reset the data, run the population script (if available) or use the existing `cultpass.db` and `udahub.db`.

## Usage

Run the agent interface:
```python
from starter.utils import chat_interface
from starter.agentic.workflow import orchestrator

chat_interface(orchestrator, ticket_id="session-123")
```

## Architecture
- **Triage**: Supervisor node using GPT-4o-mini.
- **Billing Agent**: Has access to `Subscription` and `User` tables.
- **Booking Agent**: Can modify `Reservation` and `Experience` slots.
- **Tech Agent**: Vector/Keyword search on `Knowledge` table.
