from langchain_core.tools import tool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.models.udahub import Knowledge
import json

UDA_DB_PATH = "sqlite:///udahub.db"
engine = create_engine(UDA_DB_PATH)
Session = sessionmaker(bind=engine)


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the knowledge base for articles matching the query.
    Returns a JSON string of matching articles (title and content snippet).
    """
    session = Session()
    try:
        # Basic keyword search using SQL LIKE
        formatted_query = f"%{query}%"
        results = (
            session.query(Knowledge)
            .filter(
                (Knowledge.title.ilike(formatted_query))
                | (Knowledge.content.ilike(formatted_query))
                | (Knowledge.tags.ilike(formatted_query))
            )
            .limit(3)
            .all()
        )

        if not results:
            return json.dumps(
                {"message": "No relevant articles found in knowledge base."}
            )

        articles = []
        for r in results:
            articles.append({"title": r.title, "content": r.content, "tags": r.tags})
        return json.dumps(articles)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        session.close()
