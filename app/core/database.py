from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG, 
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

def init_db():
    # Import models here to register them with SQLModel.metadata
    from app.db.models import ContractRequest, ToolCall, ObservabilityLog
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
