import reflex as rx
from app.states.session import SessionState


def qr_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    SessionState.current_session_title,
                    class_name="text-2xl font-semibold text-gray-800 mb-2",
                ),
                rx.radix.primitives.dialog.description(
                    "Scan this QR code to mark attendance.",
                    class_name="text-sm text-gray-600 mb-6",
                ),
                rx.el.div(
                    rx.image(
                        src=SessionState.qr_code_image,
                        class_name="w-64 h-64 mx-auto border-4 border-white shadow-lg rounded-lg",
                    ),
                    class_name="bg-gray-100 p-4 rounded-xl mb-4 flex justify-center",
                ),
                rx.el.div(
                    rx.el.p(
                        "Expires ",
                        rx.moment(SessionState.current_session_expiry, from_now=True),
                        class_name="text-center font-medium text-red-500",
                    ),
                    class_name="mb-6",
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Close",
                            on_click=SessionState.close_qr_modal,
                            class_name="bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300 transition duration-200 w-full",
                        )
                    ),
                    class_name="flex justify-end",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-2xl p-6 w-full max-w-md z-50",
            ),
        ),
        open=SessionState.show_qr,
        on_open_change=SessionState.close_qr_modal,
    )