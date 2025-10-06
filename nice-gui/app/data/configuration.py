"""Demo configuration data grouped for dashboard presentation."""

from __future__ import annotations

from typing import Sequence

from ..models.configuration import ConfigurationSection


def build_demo_configuration() -> tuple[
    Sequence[ConfigurationSection],
    Sequence[ConfigurationSection],
    Sequence[ConfigurationSection],
]:
    """Return configuration sections grouped by profile, settings, and connections."""

    profile_sections: Sequence[ConfigurationSection] = (
        ConfigurationSection(
            title="Notifications & Alerts",
            description="Email relay details and escalation contacts for the workspace.",
            items=(
                ("SMTP_SERVER", "smtp.gmail.com"),
                ("SMTP_PORT", "587"),
                ("SMTP_USERNAME", "your-email@gmail.com"),
                ("SMTP_PASSWORD", "your-app-password"),
                ("ADMIN_NOTIFICATION_EMAILS", "admin@yourdomain.com"),
            ),
        ),
        ConfigurationSection(
            title="Notification Webhooks",
            description="Outbound webhook destination for real-time alerts.",
            items=(("NOTIFICATION_WEBHOOK_URL", ""),),
        ),
        ConfigurationSection(
            title="AI Credentials",
            description="Primary key used for AI-powered automation across the tenant.",
            items=(("AI_API_KEY", "your_ai_api_key"),),
        ),
    )

    settings_sections: Sequence[ConfigurationSection] = (
        ConfigurationSection(
            title="Database",
            description="Connection target for persistent bot data and audit logs.",
            items=(("DATABASE_URL", "sqlite+aiosqlite:///./groupme_bots.db"),),
        ),
        ConfigurationSection(
            title="Platform Settings",
            description="Automation defaults that govern platform-specific behaviour.",
            items=(
                ("GROUPME_AUTO_JOIN_GROUPS", "true"),
                ("GROUPME_MESSAGE_COOLDOWN", "5"),
                ("DISCORD_AUTO_JOIN_GUILDS", "true"),
                ("DISCORD_COMMAND_PREFIX", "!"),
                ("TELEGRAM_AUTO_JOIN_GROUPS", "true"),
                ("TELEGRAM_MESSAGE_COOLDOWN", "3"),
                ("SIGNAL_AUTO_REGISTER", "true"),
                ("SIGNAL_MESSAGE_COOLDOWN", "2"),
            ),
        ),
        ConfigurationSection(
            title="Advanced Features",
            description="Feature flags that tune AI, moderation, and content pipelines.",
            items=(
                ("AI_ENABLED", "false"),
                ("AI_PROVIDER", "openai"),
                ("AI_MODEL", "gpt-3.5-turbo"),
                ("NLP_ENABLED", "false"),
                ("NLP_LANGUAGE", "en"),
                ("AUTO_MODERATION_ENABLED", "false"),
                ("TOXICITY_THRESHOLD", "0.8"),
                ("SPAM_DETECTION_ENABLED", "true"),
                ("CONTENT_FILTER_ENABLED", "false"),
                ("PROFANITY_FILTER", "true"),
                ("LINK_PREVIEW_ENABLED", "true"),
            ),
        ),
        ConfigurationSection(
            title="Monitoring & Analytics",
            description="Operational monitoring toggles and collection intervals.",
            items=(
                ("ANALYTICS_ENABLED", "false"),
                ("ANALYTICS_TRACKING_ID", ""),
                ("HEALTH_CHECK_ENABLED", "true"),
                ("HEALTH_CHECK_PATH", "/health"),
                ("METRICS_ENABLED", "false"),
                ("METRICS_COLLECTION_INTERVAL", "60"),
            ),
        ),
        ConfigurationSection(
            title="Backup & Migration",
            description="Disaster recovery configuration and migration readiness.",
            items=(
                ("BACKUP_ENABLED", "true"),
                ("BACKUP_INTERVAL_HOURS", "24"),
                ("BACKUP_RETENTION_DAYS", "7"),
                ("BACKUP_DESTINATION", "./backups"),
                ("MIGRATION_ENABLED", "false"),
                ("MIGRATION_SOURCE_PLATFORM", ""),
                ("MIGRATION_TARGET_PLATFORM", ""),
            ),
        ),
    )

    connection_sections: Sequence[ConfigurationSection] = (
        ConfigurationSection(
            title="Discord",
            description="Tokens and OAuth configuration for Discord automations.",
            items=(
                ("DISCORD_BOT_TOKEN", "your_discord_bot_token_here"),
                ("DISCORD_CLIENT_ID", "your_discord_client_id"),
                ("DISCORD_CLIENT_SECRET", "your_discord_client_secret"),
                ("DISCORD_MAIN_GUILD_ID", "your_main_discord_server_id"),
                ("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/your-webhook-id/your-webhook-token"),
            ),
        ),
        ConfigurationSection(
            title="Telegram",
            description="Bot credentials and webhook endpoints for Telegram.",
            items=(
                ("TELEGRAM_BOT_TOKEN", "your_telegram_bot_token_here"),
                ("TELEGRAM_WEBHOOK_URL", "https://your-domain.com/api/v1/telegram/webhook"),
                ("TELEGRAM_ADMIN_IDS", "123456789,987654321"),
            ),
        ),
        ConfigurationSection(
            title="Signal",
            description="Signal numbers and optional API keys for messaging bridges.",
            items=(
                ("SIGNAL_PHONE_NUMBER_1", "+1234567890"),
                ("SIGNAL_PHONE_NUMBER_2", "+1987654321"),
                ("SIGNAL_API_KEY", "your_signal_api_key_if_needed"),
            ),
        ),
        ConfigurationSection(
            title="E-Commerce Integrations",
            description="Commerce platform tokens for synchronized storefront workflows.",
            items=(
                ("SHOPIFY_ACCESS_TOKEN", "your_shopify_access_token"),
                ("SHOPIFY_STORE_URL", "your-store.myshopify.com"),
                ("WOOCOMMERCE_URL", "https://your-store.com"),
                ("WOOCOMMERCE_CONSUMER_KEY", "your_woocommerce_consumer_key"),
                ("WOOCOMMERCE_CONSUMER_SECRET", "your_woocommerce_consumer_secret"),
            ),
        ),
        ConfigurationSection(
            title="Payment Processing",
            description="Payment gateway keys for billing automation across channels.",
            items=(
                ("STRIPE_PUBLIC_KEY", "pk_test_your_stripe_public_key"),
                ("STRIPE_SECRET_KEY", "sk_test_your_stripe_secret_key"),
                ("STRIPE_WEBHOOK_SECRET", "whsec_your_stripe_webhook_secret"),
                ("PAYPAL_CLIENT_ID", "your_paypal_client_id"),
                ("PAYPAL_CLIENT_SECRET", "your_paypal_client_secret"),
                ("PAYPAL_MODE", "sandbox"),
            ),
        ),
        ConfigurationSection(
            title="AWS & External Services",
            description="Cloud credentials and third-party service tokens used by bots.",
            items=(
                ("AWS_ACCESS_KEY_ID", "your_aws_access_key_id"),
                ("AWS_SECRET_ACCESS_KEY", "your_aws_secret_access_key"),
                ("AWS_REGION", "us-east-1"),
                ("AWS_S3_BUCKET", "your-s3-bucket-name"),
                ("AWS_SES_SOURCE_EMAIL", "noreply@yourdomain.com"),
                ("REDDIT_CLIENT_ID", "your_reddit_client_id"),
                ("REDDIT_CLIENT_SECRET", "your_reddit_client_secret"),
                ("PUSHBULLET_API_KEY", "your_pushbullet_api_key"),
                ("TWITTER_API_KEY", "your_twitter_api_key"),
                ("TWITTER_API_SECRET", "your_twitter_api_secret"),
                ("TWITTER_ACCESS_TOKEN", "your_twitter_access_token"),
                ("TWITTER_ACCESS_SECRET", "your_twitter_access_token_secret"),
            ),
        ),
        ConfigurationSection(
            title="Webhooks & Integrations",
            description="Generic integration endpoints for event forwarding.",
            items=(
                ("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/your-slack-webhook"),
                ("GENERIC_WEBHOOK_URL", "https://your-service.com/webhook"),
            ),
        ),
    )

    return profile_sections, settings_sections, connection_sections
