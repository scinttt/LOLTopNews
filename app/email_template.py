"""
Email template for patch analysis notifications.
"""
import html


def render_patch_email(
    version: str,
    summary: str,
    tier_highlights: list[str],
    app_base_url: str,
    unsubscribe_url: str,
) -> dict:
    """
    Render a patch notification email.

    Returns {"subject": str, "html": str, "text": str, "headers": dict}.
    """
    safe_version = html.escape(version)
    safe_summary = html.escape(summary)
    safe_highlights = [html.escape(h) for h in tier_highlights]

    highlights_html = "".join(f"<li>{h}</li>" for h in safe_highlights)
    highlights_text = "\n".join(f"  - {h}" for h in tier_highlights)

    view_url = f"{app_base_url}?version={version}"

    subject = f"LOL {version} Top Lane Patch Analysis"

    email_html = f"""<!doctype html>
<html lang="en">
  <body style="margin:0;padding:24px;background:#010a13;font-family:Georgia,serif;color:#c4b998;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
      <tr><td align="center">
        <table role="presentation" width="100%" style="max-width:640px;background:#091428;border:1px solid #5b462a;">
          <tr><td style="padding:32px;">
            <p style="margin:0 0 12px;font-size:12px;letter-spacing:0.14em;text-transform:uppercase;color:#a09476;">
              LOL Top Lane Guide
            </p>
            <h1 style="margin:0 0 16px;font-size:28px;color:#f0e6d2;">
              Patch {safe_version} Analysis
            </h1>
            <p style="margin:0 0 20px;font-size:15px;line-height:1.7;color:#c4b998;">
              {safe_summary}
            </p>
            <h3 style="margin:0 0 8px;font-size:14px;color:#c89b3c;">Key Changes</h3>
            <ul style="margin:0 0 24px;padding-left:20px;color:#c4b998;">
              {highlights_html}
            </ul>
            <p style="margin:0 0 24px;">
              <a href="{html.escape(view_url)}"
                 style="display:inline-block;padding:12px 18px;background:#c89b3c;color:#010a13;
                        text-decoration:none;font-weight:bold;">
                View Full Analysis
              </a>
            </p>
            <p style="margin:24px 0 0;font-size:12px;color:#5b462a;">
              <a href="{html.escape(unsubscribe_url)}" style="color:#5b462a;">Unsubscribe</a>
            </p>
          </td></tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>"""

    email_text = f"""LOL Top Lane Guide - Patch {version}

{summary}

Key Changes:
{highlights_text}

View full analysis: {view_url}

Unsubscribe: {unsubscribe_url}"""

    return {
        "subject": subject,
        "html": email_html,
        "text": email_text,
        "headers": {
            "List-Unsubscribe": f"<{unsubscribe_url}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        },
    }
