import reflex as rx
from app.states.session import SessionState
from app.states.attendance import AttendanceState


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


SCANNER_SCRIPT = """
window.qrScanner = {
    stream: null,
    reqId: null,
    facingMode: "environment",

    init: function() {
        const video = document.getElementById("qr-video");
        const canvasElement = document.getElementById("qr-canvas");
        if (!video || !canvasElement) return;

        const statusMsg = document.getElementById("qr-status");

        if (this.stream) {
            this.stream.getTracks().forEach(t => t.stop());
        }

        navigator.mediaDevices.getUserMedia({ video: { facingMode: this.facingMode } })
            .then(stream => {
                this.stream = stream;
                video.srcObject = stream;
                video.setAttribute("playsinline", true);
                video.play();
                requestAnimationFrame(this.tick.bind(this));
                if(statusMsg) statusMsg.innerText = "Camera active. Scanning...";
            })
            .catch(err => {
                console.error(err);
                if(statusMsg) statusMsg.innerText = "Error accessing camera: " + err.message + ". Please check permissions.";
            });
    },

    stop: function() {
        if (this.stream) {
            this.stream.getTracks().forEach(t => t.stop());
            this.stream = null;
        }
        if (this.reqId) {
            cancelAnimationFrame(this.reqId);
            this.reqId = null;
        }
    },

    switchCamera: function() {
        this.facingMode = (this.facingMode === "user") ? "environment" : "user";
        this.init();
    },

    tick: function() {
        const video = document.getElementById("qr-video");
        const canvasElement = document.getElementById("qr-canvas");
        if (!video || !canvasElement) return;

        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            const canvas = canvasElement.getContext("2d", { willReadFrequently: true });
            canvasElement.height = video.videoHeight;
            canvasElement.width = video.videoWidth;
            canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

            if (typeof jsQR !== 'undefined') {
                const imageData = canvas.getImageData(0, 0, canvasElement.width, canvasElement.height);
                const code = jsQR(imageData.data, imageData.width, imageData.height, {
                    inversionAttempts: "dontInvert",
                });

                if (code) {
                    this.drawLine(canvas, code.location.topLeftCorner, code.location.topRightCorner, "#FF3B58");
                    this.drawLine(canvas, code.location.topRightCorner, code.location.bottomRightCorner, "#FF3B58");
                    this.drawLine(canvas, code.location.bottomRightCorner, code.location.bottomLeftCorner, "#FF3B58");
                    this.drawLine(canvas, code.location.bottomLeftCorner, code.location.topLeftCorner, "#FF3B58");

                    let input = document.getElementById("qr-input");
                    if (input && input.value !== code.data) {
                        let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        nativeInputValueSetter.call(input, code.data);
                        input.dispatchEvent(new Event('input', { bubbles: true }));

                        const overlay = document.getElementById("qr-overlay");
                        const statusMsg = document.getElementById("qr-status");
                        if(overlay) {
                            overlay.style.borderColor = "#10b981";
                            setTimeout(() => overlay.style.borderColor = "rgba(255,255,255,0.5)", 500);
                        }
                        if(statusMsg) statusMsg.innerText = "QR Code detected!";
                    }
                }
            }
        }
        this.reqId = requestAnimationFrame(this.tick.bind(this));
    },

    drawLine: function(canvas, begin, end, color) {
        canvas.beginPath();
        canvas.moveTo(begin.x, begin.y);
        canvas.lineTo(end.x, end.y);
        canvas.lineWidth = 4;
        canvas.strokeStyle = color;
        canvas.stroke();
    }
};
"""


def scanner_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.el.div(
                    rx.script(SCANNER_SCRIPT),
                    rx.radix.primitives.dialog.title(
                        "Scan QR Code",
                        class_name="text-2xl font-semibold text-gray-800 mb-2",
                    ),
                    rx.radix.primitives.dialog.description(
                        "Align the QR code within the frame.",
                        class_name="text-sm text-gray-600 mb-6",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.video(
                                id="qr-video",
                                class_name="absolute inset-0 w-full h-full object-cover",
                            ),
                            rx.el.canvas(
                                id="qr-canvas",
                                class_name="absolute inset-0 w-full h-full object-cover opacity-90",
                            ),
                            rx.el.div(
                                id="qr-overlay",
                                class_name="absolute inset-0 border-4 border-white/50 z-10 transition-colors duration-300 m-8 rounded-lg",
                            ),
                            rx.el.button(
                                rx.icon("camera", class_name="w-5 h-5 text-white"),
                                on_click=rx.call_script(
                                    "window.qrScanner.switchCamera()"
                                ),
                                class_name="absolute top-2 right-2 bg-black/50 p-2 rounded-full hover:bg-black/70 transition-colors z-20",
                                title="Switch Camera",
                            ),
                            class_name="w-full h-64 bg-black rounded-lg mb-4 relative overflow-hidden",
                        ),
                        rx.el.p(
                            "Initializing camera...",
                            id="qr-status",
                            class_name="text-xs text-gray-500 mb-2 text-center font-mono h-4",
                        ),
                        rx.el.input(
                            id="qr-input",
                            placeholder="Enter code manually if scan fails",
                            on_change=AttendanceState.set_scan_code,
                            class_name="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 font-mono text-center mb-2",
                            default_value=AttendanceState.scan_code,
                        ),
                        class_name="mb-6",
                    ),
                    rx.el.div(
                        rx.radix.primitives.dialog.close(
                            rx.el.button(
                                "Cancel",
                                class_name="bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300 transition duration-200",
                            )
                        ),
                        rx.el.button(
                            "Mark Attendance",
                            on_click=AttendanceState.process_scan,
                            class_name="bg-violet-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-violet-700 transition duration-200 ml-2",
                        ),
                        class_name="flex justify-end",
                    ),
                    on_mount=rx.call_script("window.qrScanner.init()"),
                    on_unmount=rx.call_script("window.qrScanner.stop()"),
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-2xl p-6 w-full max-w-md z-50",
            ),
        ),
        open=AttendanceState.show_scanner,
        on_open_change=AttendanceState.toggle_scanner,
    )