import reflex as rx
from sqlmodel import SQLModel, create_engine
import logging
from app.models import User, Session, Attendance


def initialize_db():
    """Initialize the database and create tables if they don't exist."""
    try:
        db_url = "sqlite:///reflex.db"
        engine = create_engine(db_url)
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        logging.exception(f"Error initializing database: {e}")