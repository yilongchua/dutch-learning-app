from sqlmodel import SQLModel, create_engine, Session
from backend.config.config import settings

# Create engine; echo=False for normal operation
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.DATABASE_URL else {}
)

def init_db() -> None:
    """Import models and create all tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """FastAPI dependency that yields a database session. Usage: `session: Session = Depends(get_session)`
    """
    with Session(engine) as session:
        yield session