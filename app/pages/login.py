import reflex as rx
from app.states.auth import AuthState
from app.components.layout import auth_layout


def teacher_login_page() -> rx.Component:
    return auth_layout(
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Email Address",
                    class_name="block text-sm font-medium text-gray-700 mb-1.5",
                ),
                rx.el.input(
                    placeholder="teacher@school.com",
                    on_change=AuthState.set_email_input,
                    class_name="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none transition-all",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Password",
                    class_name="block text-sm font-medium text-gray-700 mb-1.5",
                ),
                rx.el.input(
                    type="password",
                    placeholder="••••••••",
                    on_change=AuthState.set_password_input,
                    class_name="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none transition-all",
                ),
                class_name="mb-6",
            ),
            rx.el.button(
                "Sign In as Teacher",
                on_click=AuthState.login_teacher,
                class_name="w-full bg-violet-600 text-white font-medium py-2.5 rounded-lg hover:bg-violet-700 transition-colors shadow-sm hover:shadow-md",
            ),
            rx.el.div(
                "Don't have an account? ",
                rx.el.a(
                    "Create one",
                    href="/register/teacher",
                    class_name="text-violet-600 hover:text-violet-700 font-medium hover:underline",
                ),
                class_name="text-center mt-4 text-sm text-gray-600",
            ),
            class_name="flex flex-col",
        ),
        title="Teacher Login",
    )


def student_login_page() -> rx.Component:
    return auth_layout(
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Student ID",
                    class_name="block text-sm font-medium text-gray-700 mb-1.5",
                ),
                rx.el.input(
                    placeholder="S12345",
                    on_change=AuthState.set_student_id_input,
                    class_name="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none transition-all",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Password",
                    class_name="block text-sm font-medium text-gray-700 mb-1.5",
                ),
                rx.el.input(
                    type="password",
                    placeholder="••••••••",
                    on_change=AuthState.set_password_input,
                    class_name="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none transition-all",
                ),
                class_name="mb-6",
            ),
            rx.el.button(
                "Sign In as Student",
                on_click=AuthState.login_student,
                class_name="w-full bg-emerald-600 text-white font-medium py-2.5 rounded-lg hover:bg-emerald-700 transition-colors shadow-sm hover:shadow-md",
            ),
            rx.el.div(
                "Don't have an account? ",
                rx.el.a(
                    "Create one",
                    href="/register/student",
                    class_name="text-emerald-600 hover:text-emerald-700 font-medium hover:underline",
                ),
                class_name="text-center mt-4 text-sm text-gray-600",
            ),
            class_name="flex flex-col",
        ),
        title="Student Login",
    )