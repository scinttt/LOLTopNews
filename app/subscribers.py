"""
Subscriber management — JSON file-based storage for MVP.
"""
import json
import logging
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SUBSCRIBERS_FILE = Path("data/subscribers.json")


def _load() -> list[dict]:
    if SUBSCRIBERS_FILE.exists():
        try:
            with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("subscribers", [])
        except Exception as e:
            logger.warning(f"Failed to load subscribers: {e}")
    return []


def _save(subscribers: list[dict]) -> None:
    SUBSCRIBERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"subscribers": subscribers}, f, ensure_ascii=False, indent=2)


def upsert_active(email: str) -> tuple[dict, str]:
    """
    Subscribe or reactivate an email.
    Returns (subscriber_dict, action) where action is "created"|"reactivated"|"already_active".
    """
    subscribers = _load()

    for sub in subscribers:
        if sub["email"] == email:
            if sub["status"] == "active":
                return sub, "already_active"
            sub["status"] = "active"
            sub["updated_at"] = datetime.now(timezone.utc).isoformat()
            _save(subscribers)
            return sub, "reactivated"

    new_sub = {
        "email": email,
        "status": "active",
        "unsubscribe_token": secrets.token_urlsafe(32),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    subscribers.append(new_sub)
    _save(subscribers)
    return new_sub, "created"


def unsubscribe_by_token(token: str) -> Optional[dict]:
    """Unsubscribe by token. Returns the subscriber or None if not found."""
    subscribers = _load()
    for sub in subscribers:
        if sub["unsubscribe_token"] == token:
            sub["status"] = "unsubscribed"
            sub["updated_at"] = datetime.now(timezone.utc).isoformat()
            _save(subscribers)
            return sub
    return None


def list_active() -> list[dict]:
    """Return all active subscribers."""
    return [s for s in _load() if s["status"] == "active"]
