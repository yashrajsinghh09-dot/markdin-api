# database.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment")

# Create SQLAlchemy engine with Neon-friendly settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # check connections before using them
    pool_recycle=300,            # recycle connections every 5 minutes
    connect_args={"sslmode": "require"},  # required for Neon
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
