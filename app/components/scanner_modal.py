import reflex as rx
from app.states.attendance import AttendanceState

SCANNER_SCRIPT = """
window.qrScanner = {
    stream: null,
    reqId: null,
    facingMode: "environment",

    init: function() {
        const video = document.getElementById("qr-video");
        const canvasElement = document.getElementById("qr-canvas");
        const statusMsg = document.getElementById("qr-status");
        const overlay = document.getElementById("qr-overlay");

        if (!video || !canvasElement) return;

        // Reset UI
        if(statusMsg) {
            statusMsg.innerText = "Requesting camera access...";
            statusMsg.className = "text-xs text-gray-500 mb-2 text-center font-mono h-auto transition-colors duration-300";
        }
        if(overlay) {
            overlay.style.borderColor = "rgba(255,255,255,0.5)";
            overlay.style.boxShadow = "none";
        }

        // Check browser support
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            if(statusMsg) {
                statusMsg.innerText = "Error: Camera API not supported in this browser. Please use a modern mobile browser (Chrome, Safari).";
                statusMsg.className = "text-xs text-red-500 mb-2 text-center font-bold";
            }
            return;
        }

        // Stop any existing stream
        this.stop();

        const constraints = { 
            video: { 
                facingMode: this.facingMode,
                width: { ideal: 1280 },
                height: { ideal: 720 }
            } 
        };

        navigator.mediaDevices.getUserMedia(constraints)
            .then(stream => {
                this.stream = stream;
                video.srcObject = stream;
                video.setAttribute("playsinline", true);
                video.play().catch(e => console.error("Play error:", e));

                requestAnimationFrame(this.tick.bind(this));

                if(statusMsg) statusMsg.innerText = "Camera active. Align QR code within frame.";
            })
            .catch(err => {
                console.error("Camera access error:", err);
                let msg = "Error accessing camera: " + err.message;

                if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                    msg = "Permission denied. Please allow camera access in your browser settings.";
                } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                    msg = "No camera found.";
                } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
                    msg = "Camera is already in use by another app.";
                } else if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
                    msg = "Camera access requires HTTPS.";
                }

                if(statusMsg) {
                    statusMsg.innerText = msg;
                    statusMsg.className = "text-xs text-red-600 mb-2 text-center font-bold bg-red-50 p-2 rounded border border-red-100";
                }
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

        if (!video || !canvasElement) {
            // If elements are gone (modal closed), stop processing
            this.stop();
            return;
        }

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
                    this.drawLine(canvas, code.location.topLeftCorner, code.location.topRightCorner, "#10b981");
                    this.drawLine(canvas, code.location.topRightCorner, code.location.bottomRightCorner, "#10b981");
                    this.drawLine(canvas, code.location.bottomRightCorner, code.location.bottomLeftCorner, "#10b981");
                    this.drawLine(canvas, code.location.bottomLeftCorner, code.location.topLeftCorner, "#10b981");

                    const overlay = document.getElementById("qr-overlay");
                    if(overlay) {
                        overlay.style.borderColor = "#10b981";
                        overlay.style.boxShadow = "0 0 20px rgba(16,185,129,0.5)";
                    }

                    let input = document.getElementById("qr-input");
                    if (input && input.value !== code.data) {
                        const statusMsg = document.getElementById("qr-status");
                        if(statusMsg) {
                            statusMsg.innerText = "QR Code detected!";
                            statusMsg.className = "text-xs text-emerald-600 mb-2 text-center font-bold";
                        }

                        // Vibrate for feedback if supported
                        if (navigator.vibrate) navigator.vibrate(100);

                        let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        nativeInputValueSetter.call(input, code.data);
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                } else {
                    const overlay = document.getElementById("qr-overlay");
                    if(overlay) {
                         overlay.style.borderColor = "rgba(255,255,255,0.5)";
                         overlay.style.boxShadow = "none";
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
                                class_name="absolute inset-0 border-4 border-white/50 z-10 transition-all duration-300 m-8 rounded-lg",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    rx.icon(
                                        "rotate-cw", class_name="w-5 h-5 text-white"
                                    ),
                                    on_click=rx.call_script(
                                        "window.qrScanner.switchCamera()"
                                    ),
                                    class_name="bg-black/50 p-2 rounded-full hover:bg-black/70 transition-colors",
                                    title="Switch Camera",
                                ),
                                rx.el.button(
                                    rx.icon(
                                        "refresh-ccw", class_name="w-5 h-5 text-white"
                                    ),
                                    on_click=rx.call_script("window.qrScanner.init()"),
                                    class_name="bg-black/50 p-2 rounded-full hover:bg-black/70 transition-colors",
                                    title="Reload Camera",
                                ),
                                class_name="absolute top-2 right-2 flex gap-2 z-20",
                            ),
                            class_name="w-full h-64 bg-black rounded-lg mb-4 relative overflow-hidden",
                        ),
                        rx.el.p(
                            "Initializing camera...",
                            id="qr-status",
                            class_name="text-xs text-gray-500 mb-2 text-center font-mono h-auto",
                        ),
                        rx.el.input(
                            id="qr-input",
                            placeholder="Enter code manually if scan fails",
                            on_change=AttendanceState.set_scan_code,
                            class_name="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 font-mono text-center mb-4",
                            default_value=AttendanceState.scan_code,
                        ),
                        rx.el.details(
                            rx.el.summary(
                                "Troubleshooting",
                                class_name="text-xs text-gray-500 cursor-pointer hover:text-violet-600 mb-2 font-medium",
                            ),
                            rx.el.ul(
                                rx.el.li("Ensure you have granted camera permissions."),
                                rx.el.li("Make sure no other app is using the camera."),
                                rx.el.li(
                                    "Try refreshing the page or switching cameras."
                                ),
                                rx.el.li("Ensure you are on HTTPS or localhost."),
                                class_name="text-xs text-gray-500 list-disc pl-4 space-y-1 bg-gray-50 p-3 rounded-lg mb-4",
                            ),
                            class_name="mb-2 w-full",
                        ),
                        class_name="mb-4",
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