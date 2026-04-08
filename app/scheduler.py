"""
Scheduled version check — periodically polls for new LOL patch notes,
runs the analysis pipeline when a new version is detected, and saves results.
"""
import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from crawlers.lol_official import LOLOfficialCrawler

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None

CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "3600"))


async def check_for_new_version() -> dict:
    """
    Check the LOL official site for a new patch version.
    If a new version is detected, run the full analysis pipeline.

    Returns a dict describing what happened:
      {"status": "new", "version": "26.5"} or {"status": "unchanged"}
    """
    # Import here to avoid circular import (api imports workflow, scheduler imports api)
    from agents.workflow import run_workflow
    from api import load_versions_index, save_analysis_to_cache

    logger.info("🔍 Checking for new patch version...")

    try:
        crawler = LOLOfficialCrawler()
        raw_content, detected_version = await crawler.fetch_latest_patch_notes()

        index = load_versions_index()
        current_latest = index.get("latest")

        if detected_version == current_latest:
            logger.info(f"✅ No new version (current: {current_latest})")
            return {"status": "unchanged", "version": current_latest}

        logger.info(f"🆕 New version detected: {detected_version} (was: {current_latest})")

        # Run full analysis pipeline (lesson: do NOT hold file locks during this)
        result = await run_workflow(raw_content, version=detected_version)

        # Save to cache + update version index (short file I/O only)
        save_analysis_to_cache(detected_version, result)

        # Send email notifications to subscribers
        await _send_patch_notifications(detected_version, result)

        logger.info(f"✅ New version {detected_version} analyzed and cached")
        return {"status": "new", "version": detected_version}

    except Exception as e:
        logger.error(f"❌ Version check failed: {e}")
        return {"status": "error", "error": str(e)}


async def _send_patch_notifications(version: str, result: dict) -> None:
    """Send email notifications to all active subscribers."""
    resend_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("EMAIL_FROM")
    app_base_url = os.getenv("APP_BASE_URL")

    if not all([resend_key, from_email, app_base_url]):
        logger.info("Email not configured, skipping notifications")
        return

    from email_client import ResendEmailClient
    from email_template import render_patch_email
    from subscribers import list_active

    active = list_active()
    if not active:
        logger.info("No active subscribers, skipping notifications")
        return

    # Extract summary and tier highlights from result
    summary_report = result.get("summary_report") or {}
    summary_text = summary_report.get("executive_summary", f"Patch {version} analysis is ready.")
    tier_list = summary_report.get("tier_list", {})
    highlights = []
    for tier in ["S", "A"]:
        for champ in tier_list.get(tier, [])[:3]:
            name = champ.get("champion", champ) if isinstance(champ, dict) else str(champ)
            highlights.append(f"{tier}-tier: {name}")
    if not highlights:
        highlights = ["View the full analysis for details"]

    client = ResendEmailClient(resend_key)
    sent_count = 0
    for sub in active:
        try:
            unsub_url = f"{app_base_url}/api/unsubscribe?token={sub['unsubscribe_token']}"
            email = render_patch_email(version, summary_text, highlights, app_base_url, unsub_url)
            await client.send_email(
                from_addr=from_email,
                to=sub["email"],
                subject=email["subject"],
                html=email["html"],
                text=email["text"],
                headers=email.get("headers"),
            )
            sent_count += 1
        except Exception as e:
            logger.warning(f"Failed to send email to {sub['email']}: {e}")

    logger.info(f"📧 Sent {sent_count}/{len(active)} notification emails for v{version}")


def start_scheduler() -> None:
    """Start the background scheduler."""
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        check_for_new_version,
        "interval",
        seconds=CHECK_INTERVAL_SECONDS,
        id="check_new_version",
        name="Check for new LOL patch version",
    )
    _scheduler.start()
    logger.info(f"📅 Scheduler started: checking every {CHECK_INTERVAL_SECONDS}s")


def stop_scheduler() -> None:
    """Shut down the scheduler."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("📅 Scheduler stopped")
