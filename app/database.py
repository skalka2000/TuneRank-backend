import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # load from .env file if it exists

# Check if DATABASE_URL is set (for PostgreSQL)
db_url = os.getenv("DATABASE_URL")

if db_url is None or db_url == "":
    # Default to SQLite for local dev
    db_url = "sqlite:///./music.db"
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
else:
    # Use PostgreSQL for production
    engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
