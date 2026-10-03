import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.ingest.sources import active_source
from app.tracker.matters import list_matters, refresh_matter

log = logging.getLogger("casegraph.scheduler")

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def refresh_all_matters() -> dict:
    source = active_source()
    matters = list_matters()
    total_alerts = 0
    for m in matters:
        try:
            total_alerts += len(refresh_matter(m, source))
        except Exception as exc:
            log.warning("refresh failed for %s: %s", m["matter"]["cnr"], exc)
    log.info("refreshed %d matters, %d alerts", len(matters), total_alerts)
    return {"matters": len(matters), "alerts": total_alerts, "source": source.name}


def start() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        refresh_all_matters,
        "interval",
        minutes=settings.refresh_interval_minutes,
        id="refresh_matters",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.start()


def stop() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


def jobs() -> list[dict]:
    return [
        {"id": j.id, "next_run": j.next_run_time.isoformat() if j.next_run_time else None, "interval_minutes": settings.refresh_interval_minutes}
        for j in scheduler.get_jobs()
    ]
