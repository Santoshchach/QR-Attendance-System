import reflex as rx
from app.components.layout import dashboard_layout
from app.states.analytics import AnalyticsState


def stat_card(title: str, value: str, icon: str, color: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(title, class_name="text-sm font-medium text-gray-500"),
                rx.el.p(value, class_name="text-3xl font-bold text-gray-900 mt-1"),
                class_name="flex flex-col",
            ),
            rx.el.div(
                rx.icon(icon, class_name=f"w-8 h-8 text-{color}-600"),
                class_name=f"p-3 bg-{color}-100 rounded-xl",
            ),
            class_name="flex justify-between items-start",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-100 shadow-sm",
    )


def chart_card(title: str, content: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="text-lg font-bold text-gray-800 mb-6"),
        content,
        class_name="bg-white p-6 rounded-xl border border-gray-100 shadow-sm h-full",
    )


def analytics_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Analytics Dashboard", class_name="text-2xl font-bold text-gray-900"
                ),
                rx.el.p(
                    "Insights into attendance and class performance",
                    class_name="text-gray-500 mt-1",
                ),
                class_name="mb-4 md:mb-0",
            ),
            rx.el.div(
                rx.el.select(
                    rx.el.option("All Sessions", value="all"),
                    rx.foreach(
                        AnalyticsState.available_courses,
                        lambda c: rx.el.option(c["label"], value=c["value"]),
                    ),
                    value=AnalyticsState.selected_course_id,
                    on_change=AnalyticsState.set_course_filter,
                    class_name="px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 bg-white text-sm",
                ),
                rx.el.select(
                    rx.el.option("All Time", value="all"),
                    rx.el.option("Last Week", value="week"),
                    rx.el.option("Last Month", value="month"),
                    value=AnalyticsState.date_range,
                    on_change=AnalyticsState.set_date_range,
                    class_name="px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-violet-500 bg-white text-sm",
                ),
                rx.el.button(
                    rx.icon("file-text", class_name="w-4 h-4 mr-2"),
                    "Export PDF",
                    on_click=AnalyticsState.export_pdf,
                    class_name="flex items-center px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium transition-colors",
                ),
                rx.el.button(
                    rx.icon("table", class_name="w-4 h-4 mr-2"),
                    "Export Excel",
                    on_click=AnalyticsState.export_excel,
                    class_name="flex items-center px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium transition-colors",
                ),
                class_name="flex flex-wrap gap-3",
            ),
            class_name="flex flex-col md:flex-row md:justify-between md:items-center mb-8",
        ),
        rx.el.div(
            stat_card(
                "Total Sessions",
                AnalyticsState.total_sessions.to_string(),
                "presentation",
                "blue",
            ),
            stat_card(
                "Avg. Attendance",
                AnalyticsState.avg_attendance.to_string(),
                "users",
                "violet",
            ),
            stat_card(
                "Total Students",
                AnalyticsState.total_students.to_string(),
                "graduation-cap",
                "emerald",
            ),
            stat_card(
                "Active Sessions",
                AnalyticsState.active_sessions_count.to_string(),
                "radio",
                "amber",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8",
        ),
        rx.el.div(
            rx.el.div(
                chart_card(
                    "Attendance Trends",
                    rx.recharts.area_chart(
                        rx.recharts.cartesian_grid(
                            horizontal=True,
                            vertical=False,
                            stroke_dasharray="3 3",
                            class_name="opacity-50",
                        ),
                        rx.recharts.graphing_tooltip(
                            separator="",
                            content_style={
                                "backgroundColor": "white",
                                "borderRadius": "8px",
                                "border": "1px solid #e5e7eb",
                                "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                            },
                        ),
                        rx.recharts.x_axis(
                            data_key="date",
                            class_name="text-xs",
                            tick_line=False,
                            axis_line=False,
                            dy=10,
                        ),
                        rx.recharts.y_axis(
                            class_name="text-xs",
                            tick_line=False,
                            axis_line=False,
                            dx=-10,
                        ),
                        rx.recharts.area(
                            data_key="count",
                            type_="monotone",
                            stroke="#8b5cf6",
                            fill="#8b5cf6",
                            fill_opacity=0.2,
                            stroke_width=2,
                        ),
                        data=AnalyticsState.attendance_trends,
                        width="100%",
                        height=300,
                    ),
                ),
                class_name="col-span-1 lg:col-span-2",
            ),
            rx.el.div(
                chart_card(
                    "Participation Level",
                    rx.el.div(
                        rx.recharts.pie_chart(
                            rx.recharts.graphing_tooltip(),
                            rx.recharts.pie(
                                data=AnalyticsState.student_distribution,
                                data_key="value",
                                name_key="name",
                                cx="50%",
                                cy="50%",
                                inner_radius=60,
                                outer_radius=80,
                                padding_angle=5,
                                stroke="#fff",
                                stroke_width=2,
                            ),
                            width="100%",
                            height=300,
                        ),
                        rx.el.div(
                            rx.foreach(
                                AnalyticsState.student_distribution,
                                lambda item: rx.el.div(
                                    rx.el.div(
                                        class_name="w-3 h-3 rounded-full mr-2",
                                        bg=item["fill"],
                                    ),
                                    rx.el.span(
                                        item["name"], class_name="text-sm text-gray-600"
                                    ),
                                    class_name="flex items-center",
                                ),
                            ),
                            class_name="flex justify-center gap-4 mt-[-20px]",
                        ),
                        class_name="flex flex-col items-center",
                    ),
                ),
                class_name="col-span-1",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8",
        ),
        rx.el.div(
            chart_card(
                "Session Performance (Recent)",
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(
                        horizontal=True,
                        vertical=False,
                        stroke_dasharray="3 3",
                        class_name="opacity-50",
                    ),
                    rx.recharts.graphing_tooltip(
                        cursor={"fill": "#f3f4f6"},
                        content_style={
                            "backgroundColor": "white",
                            "borderRadius": "8px",
                            "border": "1px solid #e5e7eb",
                            "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                        },
                    ),
                    rx.recharts.x_axis(
                        data_key="name",
                        class_name="text-xs",
                        tick_line=False,
                        axis_line=False,
                        dy=10,
                        interval=0,
                    ),
                    rx.recharts.y_axis(
                        class_name="text-xs", tick_line=False, axis_line=False, dx=-10
                    ),
                    rx.recharts.bar(
                        data_key="attendees",
                        fill="#3b82f6",
                        radius=[4, 4, 0, 0],
                        bar_size=40,
                    ),
                    data=AnalyticsState.session_performance,
                    width="100%",
                    height=300,
                ),
            ),
            class_name="w-full mb-8",
        ),
        class_name="p-8 max-w-7xl mx-auto",
    )


def analytics_page() -> rx.Component:
    return dashboard_layout(analytics_content())