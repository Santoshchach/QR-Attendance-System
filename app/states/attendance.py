import reflex as rx
import logging
from sqlmodel import select, desc
from datetime import datetime, timezone
from app.models import Session, Attendance
from app.states.auth import AuthState


class AttendanceState(rx.State):
    """Handle attendance scanning and history."""

    show_scanner: bool = False
    scan_code: str = ""
    history: list[dict] = []
    total_attended: int = 0

    @rx.event
    def toggle_scanner(self, open_status: bool):
        """Toggle the scanner modal visibility."""
        self.show_scanner = open_status
        if not open_status:
            self.scan_code = ""

    @rx.event
    def set_scan_code(self, value: str):
        self.scan_code = value

    @rx.event
    async def process_scan(self):
        """Process the scanned QR code."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated or auth_state.user_role != "student":
            yield rx.window_alert("You must be logged in as a student.")
            return
        if not self.scan_code.startswith("ATTENDQR_SESSION_"):
            yield rx.toast.error("Invalid QR Code format.")
            return
        try:
            session_id = int(self.scan_code.replace("ATTENDQR_SESSION_", ""))
        except ValueError as e:
            logging.exception(f"Error: {e}")
            yield rx.toast.error("Invalid Session ID in QR Code.")
            return
        with rx.session() as db_session:
            session_obj = db_session.get(Session, session_id)
            if not session_obj:
                yield rx.toast.error("Session not found.")
                return
            if not session_obj.is_active:
                yield rx.toast.error("This session has ended.")
                return
            now = datetime.now(timezone.utc)
            expires_at = session_obj.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if now > expires_at:
                yield rx.toast.error("This session has expired.")
                return
            existing = db_session.exec(
                select(Attendance)
                .where(Attendance.session_id == session_id)
                .where(Attendance.student_id == auth_state.user_id)
            ).first()
            if existing:
                self.show_scanner = False
                yield rx.toast.warning(
                    "You have already marked attendance for this session."
                )
                return
            attendance = Attendance(
                session_id=session_id, student_id=auth_state.user_id, status="present"
            )
            db_session.add(attendance)
            db_session.commit()
            self.show_scanner = False
            yield rx.toast.success(f"Attendance marked for {session_obj.course_name}!")
            yield AttendanceState.load_history

    @rx.event
    async def load_history(self):
        """Load attendance history for the current student."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            return
        with rx.session() as db_session:
            results = db_session.exec(
                select(Attendance, Session)
                .where(Attendance.session_id == Session.id)
                .where(Attendance.student_id == auth_state.user_id)
                .order_by(desc(Attendance.scanned_at))
            ).all()
            self.history = []
            for att, sess in results:
                self.history.append(
                    {
                        "course_name": sess.course_name,
                        "scanned_at": att.scanned_at.strftime("%Y-%m-%d %H:%M"),
                        "status": att.status,
                        "session_id": sess.id,
                    }
                )
            self.total_attended = len(self.history)