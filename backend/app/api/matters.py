from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.graph.client import graph
from app.ingest.sources import active_source
from app.tracker import scheduler
from app.tracker.matters import create_matter, delete_matter, list_alerts, list_matters, mark_alert_read, refresh_matter

router = APIRouter(prefix="/matters", tags=["matters"])


class NewMatter(BaseModel):
    cnr: str
    title: str
    owner: str = "demo"


@router.get("")
def matters(owner: str = "demo"):
    return list_matters(owner)


@router.post("", status_code=201)
def add_matter(body: NewMatter):
    if not graph.run_one("MATCH (c:Case {cnr: $cnr}) RETURN c.cnr AS cnr", cnr=body.cnr):
        raise HTTPException(404, f"No case with CNR {body.cnr} in the graph yet. Live eCourts lookup arrives in a later feature.")
    return create_matter(body.cnr, body.title, body.owner)


@router.delete("/{matter_id}", status_code=204)
def remove_matter(matter_id: str):
    delete_matter(matter_id)


@router.post("/refresh")
def refresh_now():
    return scheduler.refresh_all_matters()


@router.post("/{matter_id}/refresh")
def refresh_one(matter_id: str):
    row = graph.run_one("MATCH (m:Matter {id: $id}) RETURN m.cnr AS cnr, m.owner AS owner", id=matter_id)
    if not row:
        raise HTTPException(404, "matter not found")
    matter = next((m for m in list_matters(row["owner"]) if m["matter"]["id"] == matter_id), None)
    return {"alerts": refresh_matter(matter, active_source())}


@router.get("/schedule")
def schedule():
    return {"running": scheduler.scheduler.running, "jobs": scheduler.jobs()}


alerts_router = APIRouter(prefix="/alerts", tags=["alerts"])


@alerts_router.get("")
def alerts(owner: str = "demo", unread_only: bool = False):
    return list_alerts(owner, unread_only)


@alerts_router.post("/{alert_id}/read", status_code=204)
def read_alert(alert_id: str):
    mark_alert_read(alert_id)
