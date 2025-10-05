"""Integration tests for the modular NiceGUI operations dashboard."""

from __future__ import annotations

from nicegui.testing import User


async def test_admin_can_toggle_bots(user: User) -> None:
    """Administrators can activate automations and see usage updates."""

    await user.open("/")
    await user.should_see("Operations Control Center")
    await user.should_see("Current role: User")
    await user.should_see("Bot controls are locked while in user mode.")

    user.find("View as Admin").click()
    await user.should_see("Current role: Admin")
    await user.should_see("Bot controls are unlocked for administrators.")

    user.find("Toggle Announcements automation").click()
    await user.should_see("Announcements automation status: Active")
    await user.should_see("Active automations: 1 of 3")
    await user.should_see("Credits used: 200 / 320")
    await user.should_see("Announcements automation activated")

    user.find("Toggle Announcements automation").click()
    await user.should_see("Announcements automation status: Paused")
    await user.should_see("Credits used: 160 / 320")
    await user.should_see("Announcements automation paused")


async def test_user_mode_keeps_automations_locked(user: User) -> None:
    """Standard users view automation status without making changes."""

    await user.open("/")
    await user.should_see("Current role: User")
    await user.should_see("Support automation status: Paused")

    user.find("Toggle Support automation").click()
    await user.should_see("Support automation status: Paused")
    await user.should_see("Bot controls are locked while in user mode.")

    user.find("View as Admin").click()
    await user.should_see("Current role: Admin")
    user.find("Toggle Support automation").click()
    await user.should_see("Support automation status: Active")

    user.find("View as User").click()
    await user.should_see("Bot controls are locked while in user mode.")
    user.find("Toggle Support automation").click()
    await user.should_see("Support automation status: Active")


async def test_profile_settings_updates_log_activity(user: User) -> None:
    """Profile settings interactions appear in the activity log."""

    await user.open("/")
    await user.should_see("Profile Management")

    user.find("Security alerts").click()
    await user.should_see("Security alerts notifications disabled")

    user.find("Two-factor authentication").click()
    await user.should_see("Two-factor authentication disabled")
