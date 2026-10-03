import json
import uuid
from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.graph.client import graph
from app.retrieval.embeddings import chat_model
from app.tracker.matters import now_iso
from app.verify.citations import verify_text

DraftKind = Literal["memo", "bail_application", "consumer_complaint", "generic"]

SYSTEM_PROMPTS: dict[str, str] = {
    "memo": "You draft concise legal research memos for Indian lawyers. Use only the facts and authorities provided. Never invent citations.",
    "bail_application": "You draft bail applications for Indian criminal courts under BNSS. Use only the facts provided. Never invent case law.",
    "consumer_complaint": "You draft consumer complaints under the Consumer Protection Act 2019 for Indian consumer commissions. Use only the facts provided.",
    "generic": "You draft legal documents for Indian courts. Use only the facts provided. Never invent citations.",
}


class ReviewState(TypedDict, total=False):
    review_id: str
    kind: DraftKind
    instructions: str
    facts: str
    draft: str
    citation_report: dict
    decision: str
    reviewer: str
    reviewer_note: str
    final: str


def draft_node(state: ReviewState) -> ReviewState:
    prompt = SYSTEM_PROMPTS.get(state["kind"], SYSTEM_PROMPTS["generic"])
    response = chat_model().invoke(
        [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Instructions:\n{state['instructions']}\n\nFacts and authorities:\n{state['facts']}"),
        ]
    )
    return {"draft": response.content}


def verify_node(state: ReviewState) -> ReviewState:
    return {"citation_report": verify_text(state["draft"])}


def human_review_node(state: ReviewState) -> ReviewState:
    save_review(state, status="pending")
    decision = interrupt(
        {
            "review_id": state["review_id"],
            "kind": state["kind"],
            "draft": state["draft"],
            "citation_report": state["citation_report"],
            "message": "A person must approve or reject this draft before it is released.",
        }
    )
    return {
        "decision": decision.get("decision", "rejected"),
        "reviewer": decision.get("reviewer", "unknown"),
        "reviewer_note": decision.get("note", ""),
    }


def route_after_review(state: ReviewState) -> str:
    return "release" if state.get("decision") == "approved" else "discard"


def release_node(state: ReviewState) -> ReviewState:
    save_review(state, status="approved", final=state["draft"])
    return {"final": state["draft"]}


def discard_node(state: ReviewState) -> ReviewState:
    save_review(state, status="rejected")
    return {"final": ""}


def build_graph():
    g = StateGraph(ReviewState)
    g.add_node("draft", draft_node)
    g.add_node("verify", verify_node)
    g.add_node("human_review", human_review_node)
    g.add_node("release", release_node)
    g.add_node("discard", discard_node)
    g.add_edge(START, "draft")
    g.add_edge("draft", "verify")
    g.add_edge("verify", "human_review")
    g.add_conditional_edges("human_review", route_after_review, {"release": "release", "discard": "discard"})
    g.add_edge("release", END)
    g.add_edge("discard", END)
    return g.compile(checkpointer=InMemorySaver())


review_graph = build_graph()


def save_review(state: ReviewState, status: str, final: str | None = None) -> None:
    graph.run(
        """
        MERGE (r:ReviewItem {id: $id})
        ON CREATE SET r.created_at = $now, r.kind = $kind, r.instructions = $instructions
        SET r.status = $status, r.draft = $draft, r.citation_report = $report,
            r.reviewer = $reviewer, r.reviewer_note = $note, r.final = $final,
            r.decided_at = CASE WHEN $status IN ['approved', 'rejected'] THEN $now ELSE r.decided_at END
        """,
        id=state["review_id"],
        now=now_iso(),
        kind=state.get("kind", "generic"),
        instructions=state.get("instructions", ""),
        status=status,
        draft=state.get("draft", ""),
        report=json.dumps(state.get("citation_report", {})),
        reviewer=state.get("reviewer"),
        note=state.get("reviewer_note"),
        final=final,
    )


def start_review(kind: DraftKind, instructions: str, facts: str) -> dict:
    review_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": review_id}}
    result = review_graph.invoke(
        {"review_id": review_id, "kind": kind, "instructions": instructions, "facts": facts},
        config=config,
    )
    interrupts = result.get("__interrupt__", [])
    payload = interrupts[0].value if interrupts else {}
    return {"review_id": review_id, "status": "pending", **payload}


def decide_review(review_id: str, decision: str, reviewer: str, note: str = "") -> dict:
    config = {"configurable": {"thread_id": review_id}}
    state = review_graph.get_state(config)
    if not state.next:
        stored = get_review(review_id)
        if stored:
            return stored
        raise KeyError(review_id)
    result = review_graph.invoke(Command(resume={"decision": decision, "reviewer": reviewer, "note": note}), config=config)
    return {"review_id": review_id, "status": "approved" if result.get("final") else "rejected", "final": result.get("final", "")}


def get_review(review_id: str) -> dict | None:
    row = graph.run_one(
        "MATCH (r:ReviewItem {id: $id}) RETURN r {.id, .kind, .status, .draft, .citation_report, .reviewer, .reviewer_note, .final, .created_at, .decided_at} AS r",
        id=review_id,
    )
    if not row:
        return None
    r = row["r"]
    r["citation_report"] = json.loads(r.get("citation_report") or "{}")
    return r


def list_reviews(status: str | None = None) -> list[dict]:
    rows = graph.run(
        """
        MATCH (r:ReviewItem)
        WHERE $status IS NULL OR r.status = $status
        RETURN r {.id, .kind, .status, .created_at, .decided_at, .reviewer} AS r
        ORDER BY r.created_at DESC LIMIT 200
        """,
        status=status,
    )
    return [row["r"] for row in rows]
