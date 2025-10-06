"""Integration tests for the modular NiceGUI operations dashboard."""

from __future__ import annotations

from nicegui.testing import User


def test_admin_can_toggle_bots(user: User) -> None:
    """Administrators can activate automations and see usage updates."""

    user.open("/")
    user.should_see("Operations Control Center")
    user.should_see("Current role: User")
    user.should_see("Bot controls are locked while in user mode.")

    user.find("View as Admin").click()
    user.should_see("Current role: Admin")
    user.should_see("Bot controls are unlocked for administrators.")

    user.find("Toggle Announcements automation").click()
    user.should_see("Announcements automation status: Active")
    user.should_see("Active automations: 1 of 3")
    user.should_see("Credits used: 200 / 320")
    user.should_see("Announcements automation activated")

    user.find("Toggle Announcements automation").click()
    user.should_see("Announcements automation status: Paused")
    user.should_see("Credits used: 160 / 320")
    user.should_see("Announcements automation paused")


def test_user_mode_keeps_automations_locked(user: User) -> None:
    """Standard users view automation status without making changes."""

    user.open("/")
    user.should_see("Current role: User")
    user.should_see("Support automation status: Paused")

    user.find("Toggle Support automation").click()
    user.should_see("Support automation status: Paused")
    user.should_see("Bot controls are locked while in user mode.")

    user.find("View as Admin").click()
    user.should_see("Current role: Admin")
    user.find("Toggle Support automation").click()
    user.should_see("Support automation status: Active")

    user.find("View as User").click()
    user.should_see("Bot controls are locked while in user mode.")
    user.find("Toggle Support automation").click()
    user.should_see("Support automation status: Active")


def test_profile_settings_updates_log_activity(user: User) -> None:
    """Profile settings interactions appear in the activity log."""

    user.open("/")
    user.should_see("Profile Management")

    user.find("Security alerts").click()
    user.should_see("Security alerts notifications disabled")

    user.find("Two-factor authentication").click()
    user.should_see("Two-factor authentication disabled")


def test_local_login_updates_authentication_status(user: User) -> None:
    """Dice login form authenticates the dashboard session."""

    user.open("/")
    user.should_see("Authentication")

    user.find("Log out").click()
    user.should_see("Not signed in.")

    user.find("Dice Email").type("pilot@example.com")
    user.find("Password").type("hunter2!")
    user.find("Sign in").click()

    user.should_see("Signed in as pilot@example.com via Dice")
    user.should_see("Signed in as pilot@example.com via Dice")


def test_credit_purchase_flow_adds_addon_credits(user: User) -> None:
    """Simulated checkout allocates add-on credits."""

    user.open("/")
    user.should_see("Credits & Billing")

    user.find("25 Credits ($25)").click()
    user.find("Create checkout session").click()
    user.should_see("Checkout ready for 25 credits")
    user.should_see("Complete Purchase")

    user.find("Confirm payment").click()
    user.should_see("Payment successful! 25 credits added to your account.")
    user.should_see("Add-on credits: 25")
