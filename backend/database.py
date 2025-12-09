# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.environ.get("CYBERNOW_DB", f"sqlite:///{os.path.join(BASE_DIR, 'cybernow.db')}")

engine = create_engine(SQLITE_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    # Import models here so they are registered on Base.metadata before create_all
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")