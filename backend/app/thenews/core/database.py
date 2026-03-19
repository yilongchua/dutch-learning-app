from sqlmodel import SQLModel, create_engine, Session
from .config import settings
from backend.app.thenews.schema.news_item import NewsItem
from backend.app.thenews.schema.theme import Theme


# Create engine; echo=False for normal operation
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.DATABASE_URL else {}
)

def init_db() -> None:
    """Import models and create all tables."""
    tables = [NewsItem.__table__, Theme.__table__]
    SQLModel.metadata.create_all(engine, tables=tables)

def get_session():
    """FastAPI dependency that yields a database session. Usage: `session: Session = Depends(get_session)`
    """
    with Session(engine) as session:
        yield session