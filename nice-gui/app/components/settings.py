"""Interactive settings controls."""

from __future__ import annotations

from typing import Iterable
import os

from nicegui import ui

from _schema.schemas.users import NotificationType

from ..state import DashboardState


def render_settings_panel(state: DashboardState) -> None:
    """Render comprehensive settings organized into tabs."""

    with ui.card().classes("w-full border border-gray-200 shadow-sm"):
        with ui.column().classes("gap-4"):
            ui.label("Settings Center").classes("text-lg font-semibold")
            ui.label(
                "Manage your profile, application settings, and external connections."
            ).classes("text-sm text-gray-600")

            # Create tabs for different settings categories
            tabs = ui.tabs().classes("w-full")

            with ui.tab_panels(tabs, value="profile").classes("w-full"):
                with ui.tab_panel("profile"):
                    _render_user_profile_settings(state)

                with ui.tab_panel("settings"):
                    _render_user_settings(state)

                with ui.tab_panel("connections"):
                    _render_connections_settings(state)


def _render_user_profile_settings(state: DashboardState) -> None:
    """Render user profile and basic settings."""

    with ui.expansion("Basic Information", value=True).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-3 w-full"):
            ui.label("Personal Details").classes("text-sm font-medium")

            # Project name and version
            ui.input("Project Name",
                    value=os.getenv("PROJECT_NAME", "Group_Me_Bots"),
                    placeholder="Enter project name").classes("w-full")

            ui.input("Version",
                    value=os.getenv("VERSION", "0.1.0"),
                    placeholder="Enter version").classes("w-full")

            # Contact information
            ui.input("Contact Phone",
                    value=os.getenv("CONTACT_PHONE", ""),
                    placeholder="Enter contact phone").classes("w-full")

            ui.input("Contact Email",
                    value=os.getenv("CONTACT_EMAIL", ""),
                    placeholder="Enter contact email").classes("w-full")

            # Website links
            ui.input("Main Website",
                    value=os.getenv("MAIN_WEBSITE", ""),
                    placeholder="Enter main website URL").classes("w-full")

            ui.input("Telegram Group",
                    value=os.getenv("TELEGRAM_GROUP", ""),
                    placeholder="Enter Telegram group URL").classes("w-full")

    with ui.expansion("Security Settings", value=True).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-3 w-full"):
            ui.label("Authentication & Security").classes("text-sm font-medium")

            # JWT settings
            ui.input("JWT Secret Key",
                    value=os.getenv("JWT_SECRET_KEY", ""),
                    placeholder="Enter JWT secret key").classes("w-full")

            ui.number("Access Token Expiry (minutes)",
                     value=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "11520")),
                     min=1, max=525600).classes("w-full")

            # Two-factor authentication toggle
            two_factor_switch = ui.switch(
                "Two-factor authentication",
                value=state.user.two_factor_enabled
            )
            two_factor_switch.on_value_change(
                lambda event: state.set_two_factor(bool(event.value))
            )


def _render_user_settings(state: DashboardState) -> None:
    """Render application and platform settings."""

    with ui.expansion("Platform Settings", value=True).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-4 w-full"):
            ui.label("Platform-Specific Configuration").classes("text-sm font-medium")

            # GroupMe settings
            with ui.row().classes("gap-4 w-full"):
                with ui.column().classes("flex-1"):
                    ui.label("GroupMe").classes("text-xs font-semibold text-gray-600")
                    ui.switch("Auto Join Groups",
                             value=os.getenv("GROUPME_AUTO_JOIN_GROUPS", "true").lower() == "true")
                    ui.number("Message Cooldown (seconds)",
                             value=int(os.getenv("GROUPME_MESSAGE_COOLDOWN", "5")),
                             min=1, max=60)

            # Discord settings
            with ui.row().classes("gap-4 w-full"):
                with ui.column().classes("flex-1"):
                    ui.label("Discord").classes("text-xs font-semibold text-gray-600")
                    ui.switch("Auto Join Guilds",
                             value=os.getenv("DISCORD_AUTO_JOIN_GUILDS", "true").lower() == "true")
                    ui.input("Command Prefix",
                            value=os.getenv("DISCORD_COMMAND_PREFIX", "!"),
                            placeholder="!")

            # Telegram settings
            with ui.row().classes("gap-4 w-full"):
                with ui.column().classes("flex-1"):
                    ui.label("Telegram").classes("text-xs font-semibold text-gray-600")
                    ui.switch("Auto Join Groups",
                             value=os.getenv("TELEGRAM_AUTO_JOIN_GROUPS", "true").lower() == "true")
                    ui.number("Message Cooldown (seconds)",
                             value=int(os.getenv("TELEGRAM_MESSAGE_COOLDOWN", "3")),
                             min=1, max=60)

            # Signal settings
            with ui.row().classes("gap-4 w-full"):
                with ui.column().classes("flex-1"):
                    ui.label("Signal").classes("text-xs font-semibold text-gray-600")
                    ui.switch("Auto Register",
                             value=os.getenv("SIGNAL_AUTO_REGISTER", "true").lower() == "true")
                    ui.number("Message Cooldown (seconds)",
                             value=int(os.getenv("SIGNAL_MESSAGE_COOLDOWN", "2")),
                             min=1, max=60)

    with ui.expansion("Advanced Features", value=False).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-3 w-full"):
            ui.label("AI & Advanced Features").classes("text-sm font-medium")

            ui.switch("AI Enabled",
                     value=os.getenv("AI_ENABLED", "false").lower() == "true")
            ui.input("AI Provider",
                    value=os.getenv("AI_PROVIDER", "openai"),
                    placeholder="openai").classes("w-full")
            ui.input("AI Model",
                    value=os.getenv("AI_MODEL", "gpt-3.5-turbo"),
                    placeholder="gpt-3.5-turbo").classes("w-full")

            ui.switch("NLP Enabled",
                     value=os.getenv("NLP_ENABLED", "false").lower() == "true")
            ui.input("NLP Language",
                    value=os.getenv("NLP_LANGUAGE", "en"),
                    placeholder="en").classes("w-full")

            ui.switch("Auto Moderation",
                     value=os.getenv("AUTO_MODERATION_ENABLED", "false").lower() == "true")
            ui.number("Toxicity Threshold",
                     value=float(os.getenv("TOXICITY_THRESHOLD", "0.8")),
                     min=0.1, max=1.0, step=0.1)

    with ui.expansion("Performance & Monitoring", value=False).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-3 w-full"):
            ui.label("System Configuration").classes("text-sm font-medium")

            ui.switch("Debug Mode",
                     value=os.getenv("DEBUG", "true").lower() == "true")
            ui.switch("Health Check Enabled",
                     value=os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true")
            ui.switch("Metrics Enabled",
                     value=os.getenv("METRICS_ENABLED", "false").lower() == "true")

            ui.number("Metrics Collection Interval (seconds)",
                     value=int(os.getenv("METRICS_COLLECTION_INTERVAL", "60")),
                     min=10, max=3600)


def _render_connections_settings(state: DashboardState) -> None:
    """Render external service connections."""

    with ui.expansion("Messaging Platforms", value=True).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-4 w-full"):
            ui.label("Bot Tokens & API Keys").classes("text-sm font-medium")

            # Discord connection
            with ui.card().classes("p-4 border border-gray-200"):
                ui.label("Discord Bot").classes("text-sm font-semibold")
                ui.input("Bot Token",
                        value=os.getenv("DISCORD_BOT_TOKEN", ""),
                        placeholder="Discord bot token",
                        password=True).classes("w-full")
                ui.input("Client ID",
                        value=os.getenv("DISCORD_CLIENT_ID", ""),
                        placeholder="Discord client ID").classes("w-full")
                ui.input("Client Secret",
                        value=os.getenv("DISCORD_CLIENT_SECRET", ""),
                        placeholder="Discord client secret",
                        password=True).classes("w-full")

            # Telegram connection
            with ui.card().classes("p-4 border border-gray-200"):
                ui.label("Telegram Bot").classes("text-sm font-semibold")
                ui.input("Bot Token",
                        value=os.getenv("TELEGRAM_BOT_TOKEN", ""),
                        placeholder="Telegram bot token",
                        password=True).classes("w-full")
                ui.input("Webhook URL",
                        value=os.getenv("TELEGRAM_WEBHOOK_URL", ""),
                        placeholder="https://your-domain.com/webhook").classes("w-full")
                ui.input("API ID",
                        value=os.getenv("TELEGRAM_API_ID", ""),
                        placeholder="Telegram API ID").classes("w-full")
                ui.input("API Hash",
                        value=os.getenv("TELEGRAM_API_HASH", ""),
                        placeholder="Telegram API hash").classes("w-full")

            # Signal connection
            with ui.card().classes("p-4 border border-gray-200"):
                ui.label("Signal").classes("text-sm font-semibold")
                ui.input("Phone Number 1",
                        value=os.getenv("SIGNAL_PHONE_NUMBER_1", ""),
                        placeholder="+1234567890").classes("w-full")
                ui.input("Phone Number 2",
                        value=os.getenv("SIGNAL_PHONE_NUMBER_2", ""),
                        placeholder="+1987654321").classes("w-full")

    with ui.expansion("Cloud & External Services", value=False).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-4 w-full"):
            ui.label("AWS & Cloud Services").classes("text-sm font-medium")

            # AWS settings
            with ui.card().classes("p-4 border border-gray-200"):
                ui.label("AWS Configuration").classes("text-sm font-semibold")
                ui.input("Access Key ID",
                        value=os.getenv("AWS_ACCESS_KEY_ID", ""),
                        placeholder="AWS access key ID").classes("w-full")
                ui.input("Secret Access Key",
                        value=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
                        placeholder="AWS secret access key",
                        password=True).classes("w-full")
                ui.input("Region",
                        value=os.getenv("AWS_REGION", "us-east-1"),
                        placeholder="us-east-1").classes("w-full")
                ui.input("S3 Bucket",
                        value=os.getenv("AWS_S3_BUCKET", ""),
                        placeholder="S3 bucket name").classes("w-full")

            # Payment processors
            with ui.card().classes("p-4 border border-gray-200"):
                ui.label("Payment Processing").classes("text-sm font-semibold")
                ui.input("Stripe Public Key",
                        value=os.getenv("STRIPE_PUBLIC_KEY", ""),
                        placeholder="Stripe public key").classes("w-full")
                ui.input("Stripe Secret Key",
                        value=os.getenv("STRIPE_SECRET_KEY", ""),
                        placeholder="Stripe secret key",
                        password=True).classes("w-full")
                ui.input("PayPal Client ID",
                        value=os.getenv("PAYPAL_CLIENT_ID", ""),
                        placeholder="PayPal client ID").classes("w-full")
                ui.input("PayPal Client Secret",
                        value=os.getenv("PAYPAL_CLIENT_SECRET", ""),
                        placeholder="PayPal client secret",
                        password=True).classes("w-full")

    with ui.expansion("Webhooks & Integrations", value=False).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-3 w-full"):
            ui.label("Webhook URLs").classes("text-sm font-medium")

            ui.input("Discord Webhook",
                    value=os.getenv("DISCORD_WEBHOOK_URL", ""),
                    placeholder="Discord webhook URL").classes("w-full")
            ui.input("Slack Webhook",
                    value=os.getenv("SLACK_WEBHOOK_URL", ""),
                    placeholder="Slack webhook URL").classes("w-full")
            ui.input("Generic Webhook",
                    value=os.getenv("GENERIC_WEBHOOK_URL", ""),
                    placeholder="Generic webhook URL").classes("w-full")
            ui.input("Notification Webhook",
                    value=os.getenv("NOTIFICATION_WEBHOOK_URL", ""),
                    placeholder="Notification webhook URL").classes("w-full")

    with ui.expansion("Database & Storage", value=False).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-3 w-full"):
            ui.label("Data Configuration").classes("text-sm font-medium")

            ui.input("Database URL",
                    value=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./groupme_bots.db"),
                    placeholder="Database connection URL").classes("w-full")
            ui.input("Redis URL",
                    value=os.getenv("REDIS_URL", "redis://localhost:6379"),
                    placeholder="Redis connection URL").classes("w-full")


def _render_notification_switches(state: DashboardState) -> None:
    """Legacy notification switches - kept for compatibility."""
    preferences = state.user.notification_preferences
    ui.label("Channels").classes("text-sm font-medium")
    for notification in _sorted_notifications(preferences.keys()):
        switch = ui.switch(
            state.notification_label(notification),
            value=bool(preferences.get(notification, False)),
        )
        switch.on_value_change(
            lambda event, item=notification: state.update_notification(
                item, bool(event.value)
            )
        )


def _render_security_controls(state: DashboardState) -> None:
    """Legacy security controls - kept for compatibility."""
    ui.label("Authentication").classes("text-sm font-medium")
    two_factor_switch = ui.switch(
        "Two-factor authentication", value=state.user.two_factor_enabled
    )
    two_factor_switch.on_value_change(
        lambda event: state.set_two_factor(bool(event.value))
    )


def _sorted_notifications(notifications: Iterable[NotificationType]) -> Iterable[NotificationType]:
    """Return notifications sorted for deterministic rendering."""

    return sorted(notifications, key=lambda item: item.value)
