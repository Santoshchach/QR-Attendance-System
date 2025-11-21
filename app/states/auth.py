import reflex as rx
import bcrypt
from sqlmodel import select
from app.models import User


class AuthState(rx.State):
    """Handle authentication and session management."""

    user_id: int = -1
    user_name: str = ""
    user_role: str = ""
    is_authenticated: bool = False
    email_input: str = ""
    student_id_input: str = ""
    password_input: str = ""
    reg_full_name: str = ""
    reg_email: str = ""
    reg_student_id: str = ""
    reg_password: str = ""
    reg_confirm_password: str = ""

    @rx.var
    def is_teacher(self) -> bool:
        return self.user_role == "teacher"

    @rx.var
    def is_student(self) -> bool:
        return self.user_role == "student"

    def _verify_password(self, plain_password, hashed_password):
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def _get_hash(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @rx.event
    def login_teacher(self):
        with rx.session() as session:
            user = session.exec(
                select(User).where(User.email == self.email_input)
            ).first()
            if (
                user
                and user.role == "teacher"
                and self._verify_password(self.password_input, user.password_hash)
            ):
                self.user_id = user.id
                self.user_name = user.full_name
                self.user_role = user.role
                self.is_authenticated = True
                return rx.redirect("/dashboard")
            return rx.window_alert("Invalid email or password")

    @rx.event
    def login_student(self):
        with rx.session() as session:
            user = session.exec(
                select(User).where(User.student_id == self.student_id_input)
            ).first()
            if (
                user
                and user.role == "student"
                and self._verify_password(self.password_input, user.password_hash)
            ):
                self.user_id = user.id
                self.user_name = user.full_name
                self.user_role = user.role
                self.is_authenticated = True
                return rx.redirect("/dashboard")
            return rx.window_alert("Invalid student ID or password")

    @rx.event
    def logout(self):
        self.user_id = -1
        self.user_name = ""
        self.user_role = ""
        self.is_authenticated = False
        return rx.redirect("/")

    @rx.event
    def check_login(self):
        if not self.is_authenticated:
            return rx.redirect("/")

    @rx.event
    def seed_test_users(self):
        """Create test users if none exist."""
        with rx.session() as session:
            if session.exec(select(User)).first():
                return
            teacher = User(
                full_name="Prof. Smith",
                password_hash=self._get_hash("teacher123"),
                role="teacher",
                email="teacher@school.com",
            )
            session.add(teacher)
            student = User(
                full_name="John Doe",
                password_hash=self._get_hash("student123"),
                role="student",
                student_id="S12345",
            )
            session.add(student)
            session.commit()

    @rx.event
    def set_reg_full_name(self, value: str):
        self.reg_full_name = value

    @rx.event
    def set_reg_email(self, value: str):
        self.reg_email = value

    @rx.event
    def set_reg_student_id(self, value: str):
        self.reg_student_id = value

    @rx.event
    def set_reg_password(self, value: str):
        self.reg_password = value

    @rx.event
    def set_reg_confirm_password(self, value: str):
        self.reg_confirm_password = value

    @rx.event
    def register_teacher(self):
        if not self.reg_full_name or not self.reg_email or (not self.reg_password):
            return rx.window_alert("Please fill in all fields")
        if self.reg_password != self.reg_confirm_password:
            return rx.window_alert("Passwords do not match")
        with rx.session() as session:
            existing = session.exec(
                select(User).where(User.email == self.reg_email)
            ).first()
            if existing:
                return rx.window_alert("Email already registered")
            teacher = User(
                full_name=self.reg_full_name,
                email=self.reg_email,
                password_hash=self._get_hash(self.reg_password),
                role="teacher",
            )
            session.add(teacher)
            session.commit()
        return [
            rx.window_alert("Registration successful! Please login."),
            rx.redirect("/login/teacher"),
        ]

    @rx.event
    def register_student(self):
        if not self.reg_full_name or not self.reg_student_id or (not self.reg_password):
            return rx.window_alert("Please fill in all fields")
        if self.reg_password != self.reg_confirm_password:
            return rx.window_alert("Passwords do not match")
        with rx.session() as session:
            existing = session.exec(
                select(User).where(User.student_id == self.reg_student_id)
            ).first()
            if existing:
                return rx.window_alert("Student ID already registered")
            student = User(
                full_name=self.reg_full_name,
                student_id=self.reg_student_id,
                password_hash=self._get_hash(self.reg_password),
                role="student",
            )
            session.add(student)
            session.commit()
        return [
            rx.window_alert("Registration successful! Please login."),
            rx.redirect("/login/student"),
        ]