# reset_udahub.py
import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)
from langgraph.graph.state import CompiledStateGraph


Base = declarative_base()


def reset_db(db_path: str, echo: bool = True):
    """Drops the existing udahub.db file and recreates all tables."""

    # Remove the file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Removed existing {db_path}")

    # Create a new engine and recreate tables
    engine = create_engine(f"sqlite:///{db_path}", echo=echo)
    Base.metadata.create_all(engine)
    print(f"✅ Recreated {db_path} with fresh schema")


@contextmanager
def get_session(engine: Engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def model_to_dict(instance):
    """Convert a SQLAlchemy model instance to a dictionary."""
    return {
        column.name: getattr(instance, column.name)
        for column in instance.__table__.columns
    }


def chat_interface(agent: CompiledStateGraph, ticket_id: str):
    from data.models.udahub import Ticket, TicketMessage, RoleEnum
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import uuid

    # Setup DB for logging
    engine = create_engine("sqlite:///udahub.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create ticket if not exists (simplified)
    # properly we assume ticket exists, but let's ensure it for the demo
    # We won't create it here to avoid complex dependency, we assume ID is passed.

    print(f"--- Chat Session Started (Ticket ID: {ticket_id}) ---")

    is_first_iteration = False  # Handled by the loop
    # messages = [SystemMessage(content = f"ThreadId: {ticket_id}")] # Graph handles persistence

    while True:
        user_input = input("User: ")
        # print("User:", user_input) # Input already echos?
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Assistant: Goodbye!")
            break

        # Log User Message
        user_msg = TicketMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            ticket_id=ticket_id,
            role=RoleEnum.user,
            content=user_input,
        )
        session.add(user_msg)
        session.commit()

        messages = [HumanMessage(content=user_input)]

        trigger = {"messages": messages}
        config = {
            "configurable": {
                "thread_id": ticket_id,
            }
        }

        try:
            result = agent.invoke(input=trigger, config=config)

            # The agent might return multiple messages, but usually the last one is the AI response.
            # result["messages"] contains the full history if we used memory, or just the new ones?
            # With langgraph state, it returns the final state.
            # We want the LAST AI message.

            last_msg = result["messages"][-1]
            response_content = last_msg.content

            print(f"Assistant: {response_content}")

            # Log Assistant Message
            ai_msg = TicketMessage(
                message_id=f"msg-{uuid.uuid4().hex[:8]}",
                ticket_id=ticket_id,
                role=RoleEnum.ai,  # or agent
                content=str(response_content),
            )
            session.add(ai_msg)
            session.commit()

        except Exception as e:
            print(f"Error: {e}")
            session.rollback()

    session.close()
