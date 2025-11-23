import reflex as rx
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_timezone(dt: datetime | None) -> datetime | None:
    """Ensure a datetime object has timezone information (UTC)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class User(SQLModel, table=True):
    """User model for both teachers and students."""

    id: int | None = Field(default=None, primary_key=True)
    full_name: str
    password_hash: str
    role: str
    email: str | None = None
    student_id: str | None = None
    created_at: datetime = Field(default_factory=get_utc_now)


class Session(SQLModel, table=True):
    """Class session created by a teacher."""

    id: int | None = Field(default=None, primary_key=True)
    teacher_id: int
    course_name: str
    created_at: datetime = Field(default_factory=get_utc_now)
    expires_at: datetime
    is_active: bool = True


class Attendance(SQLModel, table=True):
    """Attendance record for a student in a session."""

    id: int | None = Field(default=None, primary_key=True)
    session_id: int
    student_id: int
    scanned_at: datetime = Field(default_factory=get_utc_now)
    status: str = "present"