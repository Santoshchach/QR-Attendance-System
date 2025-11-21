import reflex as rx
from app.states.auth import AuthState


def sidebar_link(text: str, icon_name: str, url: str) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.icon(icon_name, class_name="w-5 h-5"),
            rx.el.span(text, class_name="font-medium"),
            class_name="flex items-center space-x-3 px-4 py-3 text-gray-600 hover:bg-violet-50 hover:text-violet-600 rounded-lg transition-colors",
        ),
        href=url,
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("qr-code", class_name="w-8 h-8 text-violet-600"),
                rx.el.h1("AttendQR", class_name="text-xl font-bold text-gray-800"),
                class_name="flex items-center space-x-2 px-4 py-6 mb-4 border-b border-gray-100",
            ),
            rx.el.nav(
                rx.cond(
                    AuthState.is_teacher,
                    rx.el.div(
                        rx.el.p(
                            "TEACHER",
                            class_name="px-4 text-xs font-semibold text-gray-400 mb-2",
                        ),
                        sidebar_link("Dashboard", "layout-dashboard", "/dashboard"),
                        sidebar_link("Analytics", "bar-chart-3", "/analytics"),
                        class_name="flex flex-col space-y-1",
                    ),
                ),
                rx.cond(
                    AuthState.is_student,
                    rx.el.div(
                        rx.el.p(
                            "STUDENT",
                            class_name="px-4 text-xs font-semibold text-gray-400 mb-2 mt-6",
                        ),
                        sidebar_link("My Dashboard", "layout-dashboard", "/dashboard"),
                        sidebar_link("Scan QR", "scan", "/dashboard"),
                        sidebar_link("History", "history", "/dashboard"),
                        class_name="flex flex-col space-y-1",
                    ),
                ),
                class_name="flex-1 px-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            AuthState.user_name,
                            class_name="text-sm font-medium text-gray-700",
                        ),
                        rx.el.p(
                            AuthState.user_role,
                            class_name="text-xs text-gray-500 capitalize",
                        ),
                    ),
                    rx.el.button(
                        rx.icon(
                            "log-out",
                            class_name="w-5 h-5 text-gray-500 hover:text-red-500 transition-colors",
                        ),
                        on_click=AuthState.logout,
                        title="Logout",
                    ),
                    class_name="flex items-center justify-between w-full",
                ),
                class_name="p-4 border-t border-gray-100",
            ),
            class_name="flex flex-col h-full",
        ),
        class_name="w-64 bg-white border-r border-gray-200 hidden md:block h-screen sticky top-0",
    )


def dashboard_layout(content: rx.Component) -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            content, class_name="flex-1 bg-gray-50 min-h-screen overflow-y-auto"
        ),
        class_name="flex w-full",
    )


def auth_layout(content: rx.Component, title: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("qr-code", class_name="w-12 h-12 text-violet-600 mx-auto mb-4"),
                rx.el.h1(
                    "AttendQR",
                    class_name="text-2xl font-bold text-center text-gray-900 mb-8",
                ),
                class_name="w-full",
            ),
            rx.el.div(
                rx.el.h2(title, class_name="text-xl font-semibold text-gray-800 mb-6"),
                content,
                class_name="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 w-full max-w-md",
            ),
            rx.el.div(
                rx.el.a(
                    "Back to Home",
                    href="/",
                    class_name="text-sm text-gray-500 hover:text-violet-600 mt-8 block text-center",
                )
            ),
            class_name="flex flex-col items-center justify-center min-h-screen p-4",
        ),
        class_name="min-h-screen bg-gray-50 font-['Inter']",
    )