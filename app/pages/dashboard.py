import reflex as rx
from app.components.layout import dashboard_layout
from app.states.auth import AuthState
from app.states.session import SessionState
from app.states.attendance import AttendanceState
from app.models import Session
from app.components.qr_modal import qr_modal
from app.components.scanner_modal import scanner_modal


def session_card(session: Session) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    session.course_name,
                    class_name="font-semibold text-gray-900 text-lg",
                ),
                rx.el.p(
                    "Created ",
                    rx.moment(session.created_at, from_now=True),
                    class_name="text-xs text-gray-400",
                ),
                class_name="flex flex-col",
            ),
            rx.el.span(
                "Active",
                class_name="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full h-fit",
            ),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("clock", class_name="w-4 h-4 text-gray-400 mr-2"),
                rx.el.span(
                    "Expires ",
                    rx.moment(session.expires_at, from_now=True),
                    class_name="text-sm text-gray-600",
                ),
                class_name="flex items-center mb-2",
            ),
            rx.el.div(
                rx.icon("users", class_name="w-4 h-4 text-gray-400 mr-2"),
                rx.el.span(
                    f"{SessionState.attendee_counts.get(session.id, 0)} Attendees",
                    class_name="text-sm text-gray-600",
                ),
                class_name="flex items-center mb-4",
            ),
            class_name="flex flex-col",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("qr-code", class_name="w-4 h-4 mr-2"),
                "Show QR",
                on_click=SessionState.show_qr_code(
                    session.id, session.course_name, session.expires_at.to_string()
                ),
                class_name="flex items-center justify-center flex-1 bg-violet-100 text-violet-700 py-2 rounded-lg hover:bg-violet-200 transition-colors font-medium text-sm",
            ),
            rx.el.button(
                rx.icon("square-x", class_name="w-4 h-4 mr-2"),
                "End",
                on_click=SessionState.end_session(session.id),
                class_name="flex items-center justify-center flex-1 bg-red-50 text-red-600 py-2 rounded-lg hover:bg-red-100 transition-colors font-medium text-sm",
            ),
            class_name="flex gap-2 mt-auto pt-4 border-t border-gray-50",
        ),
        class_name="bg-white p-5 rounded-xl border border-gray-100 shadow-sm flex flex-col h-full",
    )


def teacher_dashboard() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Create New Session", class_name="text-lg font-bold text-gray-800 mb-4"
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Course Name",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.input(
                        placeholder="e.g. CS101 - Intro to Computer Science",
                        on_change=SessionState.set_course_name,
                        class_name="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 focus:border-violet-500",
                        default_value=SessionState.course_name,
                    ),
                    class_name="flex-1",
                ),
                rx.el.div(
                    rx.el.label(
                        "Duration (Minutes)",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.select(
                        rx.el.option("15 Minutes", value="15"),
                        rx.el.option("30 Minutes", value="30"),
                        rx.el.option("45 Minutes", value="45"),
                        rx.el.option("60 Minutes", value="60"),
                        rx.el.option("90 Minutes", value="90"),
                        rx.el.option("120 Minutes", value="120"),
                        value=SessionState.duration.to_string(),
                        on_change=SessionState.set_duration,
                        class_name="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 focus:border-violet-500",
                    ),
                    class_name="w-48",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="w-5 h-5 mr-2"),
                    "Create & Start",
                    on_click=SessionState.create_session,
                    class_name="bg-violet-600 text-white px-6 py-2 rounded-lg hover:bg-violet-700 transition-all flex items-center font-semibold shadow-sm h-[42px] mt-6",
                ),
                class_name="flex flex-col md:flex-row gap-4 items-start",
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-100 shadow-sm mb-8",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Active Sessions", class_name="text-lg font-bold text-gray-800"
                ),
                rx.el.button(
                    rx.icon("refresh-ccw", class_name="w-4 h-4"),
                    on_click=SessionState.load_active_sessions,
                    class_name="p-2 text-gray-500 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-colors",
                ),
                class_name="flex justify-between items-center mb-4",
            ),
            rx.cond(
                SessionState.active_sessions,
                rx.el.div(
                    rx.foreach(SessionState.active_sessions, session_card),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                ),
                rx.el.div(
                    rx.icon("inbox", class_name="w-12 h-12 text-gray-300 mb-3"),
                    rx.el.p(
                        "No active sessions", class_name="text-gray-500 font-medium"
                    ),
                    rx.el.p(
                        "Create a new session above to get started.",
                        class_name="text-sm text-gray-400",
                    ),
                    class_name="flex flex-col items-center justify-center py-12 bg-white rounded-xl border border-dashed border-gray-200",
                ),
            ),
            class_name="w-full",
        ),
        qr_modal(),
        class_name="w-full",
    )


def history_item(item: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.p(item["course_name"], class_name="font-medium text-gray-900"),
                rx.el.p(
                    f"Session #{item['session_id']}", class_name="text-xs text-gray-500"
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            item["scanned_at"],
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            rx.el.span(
                item["status"],
                class_name="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 capitalize",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
    )


def student_dashboard() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Total Sessions Attended",
                        class_name="text-sm font-medium text-gray-500",
                    ),
                    rx.el.p(
                        AttendanceState.total_attended.to_string(),
                        class_name="text-3xl font-bold text-gray-900 mt-1",
                    ),
                ),
                rx.el.div(
                    rx.icon(
                        "check_check",
                        class_name="w-10 h-10 text-emerald-500 opacity-20",
                    )
                ),
                class_name="flex justify-between items-center bg-white p-6 rounded-xl border border-gray-100 shadow-sm mb-8",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("scan", class_name="w-6 h-6 text-violet-600 mb-2"),
                    rx.el.h3("Scan QR Code", class_name="font-semibold text-gray-900"),
                    rx.el.p(
                        "Mark your attendance now", class_name="text-sm text-gray-500"
                    ),
                    on_click=AttendanceState.toggle_scanner(True),
                    class_name="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow cursor-pointer text-left",
                ),
                class_name="grid grid-cols-1 gap-6 mb-8",
            ),
            rx.el.div(
                rx.el.h3(
                    "Attendance History",
                    class_name="text-lg font-bold text-gray-800 mb-4",
                ),
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Course",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Date & Time",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Status",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                            ),
                            class_name="bg-gray-50",
                        ),
                        rx.el.tbody(
                            rx.foreach(AttendanceState.history, history_item),
                            class_name="bg-white divide-y divide-gray-200",
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="overflow-hidden rounded-lg shadow-sm border border-gray-200 overflow-x-auto",
                ),
                class_name="w-full",
            ),
            class_name="flex flex-col",
        ),
        scanner_modal(),
        class_name="w-full",
    )


def dashboard_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("Dashboard", class_name="text-2xl font-bold text-gray-900"),
            rx.el.p(
                f"Welcome back, {AuthState.user_name}!", class_name="text-gray-500 mt-1"
            ),
            class_name="mb-8",
        ),
        rx.cond(AuthState.is_teacher, teacher_dashboard(), student_dashboard()),
        class_name="p-8 max-w-6xl mx-auto",
    )


def dashboard_page() -> rx.Component:
    return dashboard_layout(dashboard_content())