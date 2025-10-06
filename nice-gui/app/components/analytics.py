"""Analytics dashboard with real-time charts and channel monitoring."""

from __future__ import annotations

import random

import plotly.graph_objects as go
from nicegui import ui

from ..state import DashboardState


def render_analytics(state: DashboardState) -> None:
    """Render comprehensive analytics dashboard with nested tabs for each channel."""

    with ui.card().classes("w-full border border-gray-200 shadow-sm"):
        with ui.column().classes("gap-4"):
            ui.label("Analytics Dashboard").classes("text-lg font-semibold")
            ui.label("Real-time monitoring and insights across all platforms").classes("text-sm text-gray-600")

            # Create nested tabs for each platform
            with ui.tabs().classes("w-full") as platform_tabs:
                ui.tab("groupme", "GroupMe").classes("px-4 py-2")
                ui.tab("discord", "Discord").classes("px-4 py-2")
                ui.tab("telegram", "Telegram").classes("px-4 py-2")
                ui.tab("signal", "Signal").classes("px-4 py-2")

            with ui.tab_panels(platform_tabs, value="groupme").classes("w-full"):
                with ui.tab_panel("groupme"):
                    _render_groupme_analytics()

                with ui.tab_panel("discord"):
                    _render_discord_analytics()

                with ui.tab_panel("telegram"):
                    _render_telegram_analytics()

                with ui.tab_panel("signal"):
                    _render_signal_analytics()


def _render_groupme_analytics() -> None:
    """Render GroupMe analytics with real-time charts."""

    # Channel tabs for GroupMe
    channels = ["Tally Main", "Tally Subleasing", "Tally TRVP House", "Tally BLMA"]

    with ui.tabs().classes("w-full mb-4") as channel_tabs:
        for channel in channels:
            ui.tab(channel.lower().replace(" ", "_"), channel).classes("px-3 py-2")

    with ui.tab_panels(channel_tabs, value="tally_main").classes("w-full"):
        for channel in channels:
            channel_id = channel.lower().replace(" ", "_")
            with ui.tab_panel(channel_id):
                _render_channel_analytics(channel, "GroupMe")


def _render_discord_analytics() -> None:
    """Render Discord analytics with real-time charts."""

    channels = ["Main Server", "Development Server", "Test Server"]

    with ui.tabs().classes("w-full mb-4") as channel_tabs:
        for channel in channels:
            ui.tab(channel.lower().replace(" ", "_"), channel).classes("px-3 py-2")

    with ui.tab_panels(channel_tabs, value="main_server").classes("w-full"):
        for channel in channels:
            channel_id = channel.lower().replace(" ", "_")
            with ui.tab_panel(channel_id):
                _render_channel_analytics(channel, "Discord")


def _render_telegram_analytics() -> None:
    """Render Telegram analytics with real-time charts."""

    channels = ["Main Group", "Support Group", "Announcements"]

    with ui.tabs().classes("w-full mb-4") as channel_tabs:
        for channel in channels:
            ui.tab(channel.lower().replace(" ", "_"), channel).classes("px-3 py-2")

    with ui.tab_panels(channel_tabs, value="main_group").classes("w-full"):
        for channel in channels:
            channel_id = channel.lower().replace(" ", "_")
            with ui.tab_panel(channel_id):
                _render_channel_analytics(channel, "Telegram")


def _render_signal_analytics() -> None:
    """Render Signal analytics with real-time charts."""

    channels = ["Phone 1", "Phone 2", "Backup Phone"]

    with ui.tabs().classes("w-full mb-4") as channel_tabs:
        for channel in channels:
            ui.tab(channel.lower().replace(" ", "_"), channel).classes("px-3 py-2")

    with ui.tab_panels(channel_tabs, value="phone_1").classes("w-full"):
        for channel in channels:
            channel_id = channel.lower().replace(" ", "_")
            with ui.tab_panel(channel_id):
                _render_channel_analytics(channel, "Signal")


def _render_channel_analytics(channel: str, platform: str) -> None:
    """Render analytics charts for a specific channel using organized dropdown sections."""

    with ui.column().classes("gap-4 w-full"):
        ui.label(f"{platform}: {channel} Analytics").classes("text-md font-semibold mb-4")

        # Real-time metrics cards (always visible)
        _render_metrics_cards(channel, platform)

        # Message Volume Chart - Full Width Dropdown
        with ui.expansion("📊 Message Volume Analytics", value=False).classes("w-full"):
            with ui.column().classes("gap-4 w-full"):
                ui.label("Detailed message volume tracking over the last 24 hours").classes("text-sm text-gray-600")
                _render_message_volume_chart(channel, platform)

        # User Activity Section
        with ui.expansion("👥 User Activity Analysis", value=False).classes("w-full"):
            with ui.column().classes("gap-4 w-full"):
                ui.label("User engagement patterns and activity heatmap").classes("text-sm text-gray-600")
                _render_user_activity_chart(channel, platform)

        # Bot Performance Section
        with ui.expansion("🤖 Bot Performance Metrics", value=False).classes("w-full"):
            with ui.column().classes("gap-4 w-full"):
                ui.label("Bot response times and success rates").classes("text-sm text-gray-600")
                _render_bot_performance_chart(channel, platform)

        # Workflow Analytics Section
        with ui.expansion("⚙️ Workflow Execution Analytics", value=False).classes("w-full"):
            with ui.column().classes("gap-4 w-full"):
                ui.label("Automated workflow performance and execution statistics").classes("text-sm text-gray-600")
                _render_workflow_chart(channel, platform)


def _render_metrics_cards(channel: str, platform: str) -> None:
    """Render real-time metrics cards."""

    # Mock data - in real app this would come from API
    metrics = {
        "Messages Today": "1,247",
        "Active Users": "89",
        "Bot Responses": "342",
        "Avg Response Time": "1.2s"
    }

    with ui.row().classes("gap-4 w-full mb-6"):
        for label, value in metrics.items():
            with ui.card().classes("p-4 border border-gray-200 flex-1"):
                ui.label(value).classes("text-2xl font-bold text-blue-600")
                ui.label(label).classes("text-sm text-gray-600")


def _render_message_volume_chart(channel: str, platform: str) -> None:
    """Render message volume chart with real-time updates."""

    # Generate sample data
    hours = list(range(24))
    messages = [random.randint(50, 200) for _ in hours]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours,
        y=messages,
        mode='lines+markers',
        name='Messages',
        line=dict(color='#3B82F6', width=2),
        marker=dict(size=4)
    ))

    fig.update_layout(
        title="Message Volume - Last 24 Hours",
        xaxis_title="Hour",
        yaxis_title="Messages",
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        plot_bgcolor='#F8FAFC',
        paper_bgcolor='white'
    )

    # Create the plot element
    plot = ui.plotly(fig).classes('w-full')

    # Update function for real-time data
    def update_chart():
        new_messages = [random.randint(50, 200) for _ in hours]
        fig.data[0].y = new_messages
        plot.update()

    # Auto-update every 5 seconds
    ui.timer(5.0, update_chart)


def _render_user_activity_chart(channel: str, platform: str) -> None:
    """Render user activity heatmap."""

    # Generate sample hourly activity data
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hours = list(range(24))

    # Create activity matrix (days x hours)
    activity_data = [[random.randint(0, 100) for _ in hours] for _ in days]

    fig = go.Figure(data=go.Heatmap(
        z=activity_data,
        x=hours,
        y=days,
        colorscale='Blues',
        showscale=True,
        colorbar=dict(title="Activity Level")
    ))

    fig.update_layout(
        title="User Activity Heatmap - Last 7 Days",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        margin=dict(l=40, r=40, t=40, b=40),
        height=300
    )

    ui.plotly(fig).classes('w-full')


def _render_bot_performance_chart(channel: str, platform: str) -> None:
    """Render bot performance metrics."""

    # Sample bot performance data
    bots = ["Zort Pro", "Support Bot", "Moderator Bot"]
    response_times = [random.uniform(0.8, 2.5) for _ in bots]
    success_rates = [random.uniform(85, 98) for _ in bots]

    fig = go.Figure()

    # Response time bars
    fig.add_trace(go.Bar(
        name='Avg Response Time (s)',
        x=bots,
        y=response_times,
        marker_color='#EF4444'
    ))

    # Success rate line
    fig.add_trace(go.Scatter(
        name='Success Rate (%)',
        x=bots,
        y=success_rates,
        mode='lines+markers',
        line=dict(color='#10B981', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))

    fig.update_layout(
        title="Bot Performance Metrics",
        yaxis=dict(title="Response Time (s)", side="left"),
        yaxis2=dict(title="Success Rate (%)", side="right", overlaying="y"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )

    ui.plotly(fig).classes('w-full')


def _render_workflow_chart(channel: str, platform: str) -> None:
    """Render workflow execution analytics."""

    # Sample workflow data
    workflows = ["Message Processing", "User Verification", "Content Moderation", "Analytics Pipeline"]
    executions = [random.randint(100, 500) for _ in workflows]
    success_rates = [random.uniform(92, 99) for _ in workflows]

    fig = go.Figure()

    # Execution count bars
    colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']

    for i, workflow in enumerate(workflows):
        fig.add_trace(go.Bar(
            name=workflow,
            x=[workflow],
            y=[executions[i]],
            marker_color=colors[i],
            showlegend=False
        ))

    fig.update_layout(
        title="Workflow Executions - Last 24h",
        xaxis_title="Workflow",
        yaxis_title="Executions",
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        xaxis_tickangle=-45
    )

    # Add success rate annotations
    for i, (workflow, success_rate) in enumerate(zip(workflows, success_rates)):
        fig.add_annotation(
            x=workflow,
            y=executions[i] + 20,
            text=f"{success_rate:.1f}%",
            showarrow=False,
            font=dict(size=10, color="white"),
            bgcolor=colors[i]
        )

    ui.plotly(fig).classes('w-full')
