import reflex as rx
from app.pages.login import teacher_login_page, student_login_page
from app.pages.register import teacher_registration_page, student_registration_page
from app.pages.dashboard import dashboard_page
from app.states.auth import AuthState
from app.database import initialize_db

initialize_db()


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.icon("qr-code", class_name="w-20 h-20 text-violet-600 mb-6"),
            rx.el.h1(
                "AttendQR System", class_name="text-4xl font-bold text-gray-900 mb-4"
            ),
            rx.el.p(
                "Seamless attendance management for modern classrooms.",
                class_name="text-xl text-gray-600 mb-12 max-w-lg",
            ),
            rx.el.div(
                rx.el.a(
                    rx.el.button(
                        "Teacher Login",
                        rx.icon("arrow-right", class_name="ml-2", size=16),
                        class_name="bg-violet-600 text-white px-8 py-4 rounded-xl hover:bg-violet-700 transition-all flex items-center font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1",
                    ),
                    href="/login/teacher",
                ),
                rx.el.a(
                    rx.el.button(
                        "Student Login",
                        rx.icon("arrow-right", class_name="ml-2", size=16),
                        class_name="bg-white text-gray-700 border border-gray-200 px-8 py-4 rounded-xl hover:bg-gray-50 transition-all flex items-center font-semibold shadow-md hover:shadow-lg transform hover:-translate-y-1",
                    ),
                    href="/login/student",
                ),
                class_name="flex flex-col sm:flex-row gap-4",
            ),
            rx.el.div(
                rx.el.p("Development Mode: ", class_name="text-gray-400 mr-2"),
                rx.el.button(
                    "Seed Test Data",
                    on_click=AuthState.seed_test_users,
                    class_name="text-violet-500 hover:underline font-medium",
                ),
                class_name="mt-16 flex items-center text-sm",
            ),
            class_name="flex flex-col items-center justify-center text-center min-h-screen p-4",
        ),
        class_name="font-['Inter'] bg-white min-h-screen",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
        rx.el.script(src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js"),
    ],
)
from app.states.session import SessionState
from app.states.attendance import AttendanceState
from app.pages.analytics import analytics_page
from app.states.analytics import AnalyticsState

app.add_page(index, route="/")
app.add_page(teacher_login_page, route="/login/teacher")
app.add_page(student_login_page, route="/login/student")
app.add_page(teacher_registration_page, route="/register/teacher")
app.add_page(student_registration_page, route="/register/student")
app.add_page(
    dashboard_page,
    route="/dashboard",
    on_load=[
        AuthState.check_login,
        SessionState.load_active_sessions,
        AttendanceState.load_history,
    ],
)
app.add_page(
    analytics_page,
    route="/analytics",
    on_load=[AuthState.check_login, AnalyticsState.load_stats],
)