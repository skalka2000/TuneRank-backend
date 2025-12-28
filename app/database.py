from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite file-based DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./music.db"

# This is the actual engine that talks to SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
)

# Session factory — used in FastAPI to get DB access
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for model definitions (models.py will use this)
Base = declarative_base()
