from core.settings import get_settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

settings = get_settings()

engine = create_engine(
    url=settings.database_url.unicode_string(),
    echo=False,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
