from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.review_gate import DraftKind, decide_review, get_review, list_reviews, start_review

router = APIRouter(prefix="/review", tags=["review"])


class DraftRequest(BaseModel):
    kind: DraftKind = "generic"
    instructions: str
    facts: str


class Decision(BaseModel):
    decision: str
    reviewer: str = "demo"
    note: str = ""


@router.post("/drafts", status_code=202)
def create_draft(body: DraftRequest):
    return start_review(body.kind, body.instructions, body.facts)


@router.get("/queue")
def queue(status: str | None = "pending"):
    return list_reviews(status)


@router.get("/{review_id}")
def review(review_id: str):
    item = get_review(review_id)
    if not item:
        raise HTTPException(404, "review not found")
    return item


@router.post("/{review_id}/decision")
def decide(review_id: str, body: Decision):
    if body.decision not in {"approved", "rejected"}:
        raise HTTPException(422, "decision must be approved or rejected")
    try:
        return decide_review(review_id, body.decision, body.reviewer, body.note)
    except KeyError:
        raise HTTPException(404, "review not found")
