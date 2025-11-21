import reflex as rx
import qrcode
import io
import base64
from datetime import datetime, timedelta, timezone
from sqlmodel import select, func, desc
from app.models import Session, Attendance
from app.states.auth import AuthState


class SessionState(rx.State):
    """Handle class sessions and QR code generation."""

    course_name: str = ""
    duration: int = 60
    active_sessions: list[Session] = []
    attendee_counts: dict[int, int] = {}
    show_qr: bool = False
    qr_code_image: str = ""
    current_session_title: str = ""
    current_session_expiry: str = ""

    @rx.event
    async def load_active_sessions(self):
        """Load all active sessions for the current teacher."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated or auth_state.user_role != "teacher":
            return
        with rx.session() as session:
            statement = (
                select(Session)
                .where(Session.teacher_id == auth_state.user_id)
                .where(Session.is_active == True)
                .order_by(desc(Session.created_at))
            )
            self.active_sessions = session.exec(statement).all()
            self.attendee_counts = {}
            for s in self.active_sessions:
                count_stmt = select(func.count()).where(Attendance.session_id == s.id)
                count = session.exec(count_stmt).one()
                self.attendee_counts[s.id] = count

    @rx.event
    async def create_session(self):
        """Create a new class session."""
        auth_state = await self.get_state(AuthState)
        if not self.course_name:
            return rx.window_alert("Please enter a course name")
        with rx.session() as session:
            now = datetime.now(timezone.utc)
            expires = now + timedelta(minutes=self.duration)
            new_session = Session(
                teacher_id=auth_state.user_id,
                course_name=self.course_name,
                expires_at=expires,
                is_active=True,
            )
            session.add(new_session)
            session.commit()
            session.refresh(new_session)
        self.course_name = ""
        self.show_qr_code(
            new_session.id, new_session.course_name, new_session.expires_at.isoformat()
        )
        return SessionState.load_active_sessions

    @rx.event
    async def end_session(self, session_id: int):
        """End a session manually."""
        with rx.session() as session:
            s = session.get(Session, session_id)
            if s:
                s.is_active = False
                session.add(s)
                session.commit()
        return SessionState.load_active_sessions

    @rx.event
    def show_qr_code(self, session_id: int, course_name: str, expires_at: str):
        """Generate and show QR code for a session."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"ATTENDQR_SESSION_{session_id}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        self.qr_code_image = f"data:image/png;base64,{img_str}"
        self.current_session_title = course_name
        self.current_session_expiry = expires_at
        self.show_qr = True

    @rx.event
    def close_qr_modal(self):
        """Close the QR code modal."""
        self.show_qr = False

    @rx.event
    def set_course_name(self, value: str):
        self.course_name = value

    @rx.event
    def set_duration(self, value: str):
        if value.isdigit():
            self.duration = int(value)