"""HTML rendering helpers for the NiceGUI stub server."""

from __future__ import annotations

from typing import Any, Iterable, Iterator, List, Sequence, Tuple

import textwrap


def _tabbed_html(title: str, tabs: Iterable[str], active: str) -> str:
    buttons = "".join(
        f'<button class="tab-button{ " active" if name == active else "" }" '
        f'data-tab="{name}">{name}</button>'
        for name in tabs
    )
    return textwrap.dedent(
        f"""
        <header class="header">
          <h1>{title}</h1>
          <div class="tab-bar">{buttons}</div>
        </header>
        """
    )


def _definition_list(items: Iterable[Tuple[str, Any]]) -> str:
    def render(value: Any) -> str:
        if value in (None, ""):
            return "Not configured"
        return str(value)

    return "".join(f"<dt>{key}</dt><dd>{render(value)}</dd>" for key, value in items)


def _section_cards(sections: Sequence) -> str:
    cards: List[str] = []
    for section in sections:
        description = (
            f"<p class=\"muted\">{section.description}</p>"
            if getattr(section, "description", None)
            else ""
        )
        cards.append(
            textwrap.dedent(
                f"""
                <article class="card">
                  <h3>{section.title}</h3>
                  {description}
                  <dl>{_definition_list(section.items)}</dl>
                </article>
                """
            )
        )
    return "".join(cards)


def render_static_dashboard() -> str:
    """Return a static HTML representation of the dashboard."""

    from app.state import DashboardState

    state = DashboardState.demo()
    role_helper = (
        "Bot controls are unlocked for administrators."
        if state.role == "Admin"
        else "Bot controls are locked while in user mode."
    )
    bots = "".join(
        f"<li><strong>{bot.bot_name}</strong>: "
        f"{'Active' if state.bot_controller.get_status(bot.bot_name) else 'Paused'}</li>"
        for bot in state.bots
    )
    automation_card = (
        f"<section class=\"card\"><h2>Bot Management</h2>"
        f"<p class=\"muted\">{role_helper}</p><ul class=\"list\">{bots}</ul></section>"
    )
    activity = "".join(f"<li>{entry}</li>" for entry in state.activity_log)
    activity_card = (
        "<section class=\"card\"><h2>Recent Activity</h2>"
        f"<ul class=\"list\">{activity}</ul></section>"
    )
    profile = textwrap.dedent(
        f"""
        <section class="card">
          <h2>Profile Management</h2>
          <p>{state.user.nickname} ({state.user.email})</p>
          <p>Timezone: {state.user.timezone}</p>
          <p>Preferred contact: {state.user.preferred_contact_method.value.replace('_', ' ').title()}</p>
        </section>
        """
    )
    auth_states = [state.auth.status_text()]
    auth_states.append(
        "Two-factor authentication is enabled"
        if state.user.two_factor_enabled
        else "Two-factor authentication is disabled"
    )
    auth = textwrap.dedent(
        f"""
        <section class="card">
          <h2>Authentication</h2>
          <ul class="list">{''.join(f'<li>{line}</li>' for line in auth_states)}</ul>
        </section>
        """
    )
    assistants: List[str] = []
    for bot in state.bots:
        capabilities = ", ".join(cap.replace("_", " ").title() for cap in bot.capabilities)
        assistants.append(
            textwrap.dedent(
                f"""
                <article class="card">
                  <h3>{bot.bot_name} ({bot.bot_model})</h3>
                  <p class="muted">Focus: {bot.function.replace('_', ' ').title()}</p>
                  <p>Capabilities: {capabilities}</p>
                  <dl>{_definition_list(bot.settings.items())}</dl>
                </article>
                """
            )
        )
    assistants_grid = "".join(assistants)
    billing = textwrap.dedent(
        f"""
        <section class="card">
          <h2>Credits &amp; Billing</h2>
          <p>{state.credit_summary()}</p>
          <p class="muted">Selected package: 25 credits</p>
        </section>
        """
    )

    tabs = [
        ("Bots & Automations", automation_card + activity_card),
        ("User Profile", profile + auth + _section_cards(state.profile_sections)),
        ("User Settings", textwrap.dedent(
            f"""
            <section class="card">
              <h2>Settings</h2>
              <p class="muted">Workspace notifications and preferences.</p>
              {_section_cards(state.settings_sections)}
            </section>
            """
        )),
        ("Connections", textwrap.dedent(
            f"""
            <section class="card">
              <h2>Connections</h2>
              {_section_cards(state.connection_sections)}
            </section>
            """
        )),
        ("AI Assistants & Billing", assistants_grid + billing),
    ]

    def tab_names() -> Iterator[str]:
        for name, _ in tabs:
            yield name

    content = "".join(
        textwrap.dedent(
            f"""
            <section class="tab-content{' active' if index == 0 else ''}" data-tab="{name}">
              {panel}
            </section>
            """
        )
        for index, (name, panel) in enumerate(tabs)
    )

    return textwrap.dedent(
        f"""
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Operations Control Center (Stub)</title>
            <style>
              body {{ font-family: 'Inter', system-ui, sans-serif; margin: 0; background: #f5f5f7; color: #111827; }}
              .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }}
              .header h1 {{ margin: 0 0 0.5rem; font-size: 2rem; }}
              .muted {{ color: #6b7280; }}
              .tab-bar {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.5rem; }}
              .tab-button {{ border: none; background: #e5e7eb; padding: 0.5rem 0.9rem; border-radius: 999px; cursor: pointer; font-size: 0.95rem; transition: background 0.2s ease; }}
              .tab-button.active {{ background: #2563eb; color: #fff; }}
              .tab-content {{ display: none; gap: 1rem; }}
              .tab-content.active {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; }}
              .card {{ background: #fff; border-radius: 1rem; padding: 1.2rem 1.5rem; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); }}
              .card h2 {{ margin-top: 0; font-size: 1.25rem; }}
              .card h3 {{ margin-top: 0; font-size: 1.1rem; }}
              .list {{ list-style: none; padding: 0; margin: 0; }}
              .list li {{ margin-bottom: 0.5rem; }}
              dl {{ display: grid; grid-template-columns: max-content 1fr; column-gap: 0.75rem; row-gap: 0.35rem; margin: 0; }}
              dt {{ font-weight: 600; }}
              footer {{ margin-top: 2rem; font-size: 0.85rem; color: #9ca3af; text-align: center; }}
            </style>
          </head>
          <body>
            <div class="container">
              {_tabbed_html('Operations Control Center', tab_names(), tabs[0][0])}
              <section class="card">
                <h2>Role Summary</h2>
                <p><strong>Current role:</strong> {state.role}</p>
                <p><strong>{state.bot_summary()}</strong></p>
                <p class="muted">Switch roles and interact with bots in the full NiceGUI build.</p>
              </section>
              {content}
              <footer>Stub renderer active. Install NiceGUI for the interactive experience.</footer>
            </div>
            <script>
              const buttons = document.querySelectorAll('.tab-button');
              const sections = document.querySelectorAll('.tab-content');
              buttons.forEach((button) => {{
                button.addEventListener('click', () => {{
                  buttons.forEach((btn) => btn.classList.remove('active'));
                  sections.forEach((section) => section.classList.remove('active'));
                  button.classList.add('active');
                  const target = button.dataset.tab;
                  const selector = '.tab-content[data-tab="' + target + '"]';
                  const match = document.querySelector(selector);
                  if (match) {{ match.classList.add('active'); }}
                }});
              }});
            </script>
          </body>
        </html>
        """
    )
