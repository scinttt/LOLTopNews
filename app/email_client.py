"""
Email client using Resend API.
"""
import logging
import os

import httpx

logger = logging.getLogger(__name__)


class ResendEmailClient:
    """Send emails via Resend (https://resend.com)."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("RESEND_API_KEY", "")

    async def send_email(
        self,
        *,
        from_addr: str,
        to: str,
        subject: str,
        html: str,
        text: str,
        headers: dict[str, str] | None = None,
        reply_to: str | None = None,
    ) -> str:
        """Send a single email. Returns the Resend message ID."""
        payload: dict = {
            "from": from_addr,
            "to": [to],
            "subject": subject,
            "html": html,
            "text": text,
        }
        if headers:
            payload["headers"] = headers
        if reply_to:
            payload["reply_to"] = [reply_to]

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )

        data = resp.json()
        if not resp.is_success or "id" not in data:
            raise RuntimeError(data.get("message", f"Resend failed: {resp.status_code}"))

        logger.info(f"Email sent to {to}: {data['id']}")
        return data["id"]
