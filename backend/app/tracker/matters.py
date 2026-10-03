import hashlib
import json
import uuid
from datetime import UTC, datetime

from app.graph.client import graph


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def case_snapshot(cnr: str) -> dict | None:
    return graph.run_one(
        """
        MATCH (c:Case {cnr: $cnr})
        OPTIONAL MATCH (c)-[:FILED_IN]->(court:Court)
        OPTIONAL MATCH (c)-[:OF_TYPE]->(t:CaseType)
        RETURN c {.cnr, .filing_date, .decision_date, .status, .purpose, .disposition, .year} AS case,
               court.name AS court, t.name AS case_type
        """,
        cnr=cnr,
    )


def snapshot_hash(snapshot: dict | None) -> str:
    payload = json.dumps(snapshot or {}, sort_keys=True, default=str)
    return hashlib.sha1(payload.encode()).hexdigest()


def create_matter(cnr: str, title: str, owner: str = "demo") -> dict:
    snap = case_snapshot(cnr)
    matter_id = str(uuid.uuid4())
    graph.run(
        """
        MERGE (m:Matter {cnr: $cnr, owner: $owner})
        ON CREATE SET m.id = $id, m.title = $title, m.created_at = $now, m.last_hash = $hash, m.last_snapshot = $snapshot, m.last_checked = $now
        WITH m
        OPTIONAL MATCH (c:Case {cnr: $cnr})
        FOREACH (_ IN CASE WHEN c IS NULL THEN [] ELSE [1] END | MERGE (m)-[:TRACKS]->(c))
        """,
        cnr=cnr,
        owner=owner,
        id=matter_id,
        title=title,
        now=now_iso(),
        hash=snapshot_hash(snap),
        snapshot=json.dumps(snap or {}, default=str),
    )
    return get_matter_by_cnr(cnr, owner)


def get_matter_by_cnr(cnr: str, owner: str = "demo") -> dict:
    row = graph.run_one(
        """
        MATCH (m:Matter {cnr: $cnr, owner: $owner})
        OPTIONAL MATCH (m)-[:TRACKS]->(c:Case)
        OPTIONAL MATCH (c)-[:FILED_IN]->(court:Court)
        OPTIONAL MATCH (c)-[:OF_TYPE]->(t:CaseType)
        OPTIONAL MATCH (a:Alert)-[:ABOUT]->(m) WHERE a.read = false
        RETURN m {.id, .cnr, .title, .owner, .created_at, .last_checked} AS matter,
               c {.filing_date, .decision_date, .status, .purpose, .disposition} AS case,
               court.name AS court, t.name AS case_type, count(a) AS unread_alerts
        """,
        cnr=cnr,
        owner=owner,
    )
    return row or {}


def list_matters(owner: str = "demo") -> list[dict]:
    return graph.run(
        """
        MATCH (m:Matter {owner: $owner})
        OPTIONAL MATCH (m)-[:TRACKS]->(c:Case)
        OPTIONAL MATCH (c)-[:FILED_IN]->(court:Court)
        OPTIONAL MATCH (c)-[:OF_TYPE]->(t:CaseType)
        OPTIONAL MATCH (a:Alert)-[:ABOUT]->(m) WHERE a.read = false
        RETURN m {.id, .cnr, .title, .owner, .created_at, .last_checked} AS matter,
               c {.filing_date, .decision_date, .status, .purpose, .disposition} AS case,
               court.name AS court, t.name AS case_type, count(a) AS unread_alerts
        ORDER BY matter.created_at DESC
        """,
        owner=owner,
    )


def delete_matter(matter_id: str) -> None:
    graph.run("MATCH (m:Matter {id: $id}) OPTIONAL MATCH (a:Alert)-[:ABOUT]->(m) DETACH DELETE a, m", id=matter_id)


def raise_alert(matter_id: str, kind: str, text: str) -> dict:
    alert_id = str(uuid.uuid4())
    graph.run(
        """
        MATCH (m:Matter {id: $matter_id})
        CREATE (a:Alert {id: $id, kind: $kind, text: $text, created_at: $now, read: false})-[:ABOUT]->(m)
        """,
        matter_id=matter_id,
        id=alert_id,
        kind=kind,
        text=text,
        now=now_iso(),
    )
    return {"id": alert_id, "kind": kind, "text": text}


def list_alerts(owner: str = "demo", unread_only: bool = False) -> list[dict]:
    return graph.run(
        """
        MATCH (a:Alert)-[:ABOUT]->(m:Matter {owner: $owner})
        WHERE NOT $unread_only OR a.read = false
        RETURN a {.id, .kind, .text, .created_at, .read} AS alert, m {.id, .cnr, .title} AS matter
        ORDER BY a.created_at DESC LIMIT 100
        """,
        owner=owner,
        unread_only=unread_only,
    )


def mark_alert_read(alert_id: str) -> None:
    graph.run("MATCH (a:Alert {id: $id}) SET a.read = true", id=alert_id)


def describe_change(old: dict | None, new: dict | None) -> list[tuple[str, str]]:
    changes: list[tuple[str, str]] = []
    o = (old or {}).get("case") or {}
    n = (new or {}).get("case") or {}
    if o.get("status") != n.get("status"):
        changes.append(("status", f"Status changed from {o.get('status')} to {n.get('status')}."))
    if o.get("purpose") != n.get("purpose"):
        changes.append(("stage", f"Stage moved from {o.get('purpose')} to {n.get('purpose')}."))
    if o.get("decision_date") != n.get("decision_date") and n.get("decision_date"):
        changes.append(("disposal", f"Case disposed on {n.get('decision_date')} ({n.get('disposition')})."))
    return changes


def refresh_matter(matter: dict, source) -> list[dict]:
    m = matter["matter"]
    stored = graph.run_one("MATCH (m:Matter {id: $id}) RETURN m.last_hash AS h, m.last_snapshot AS s", id=m["id"]) or {}
    previous = json.loads(stored.get("s") or "{}") or {"case": matter.get("case")}
    latest_case = source.fetch_case(m["cnr"])
    if latest_case:
        source.upsert_case(latest_case)
    current = case_snapshot(m["cnr"])
    new_hash = snapshot_hash(current)
    raised: list[dict] = []
    if stored.get("h") != new_hash:
        for kind, text in describe_change(previous, current) or [("update", "Case record changed on refresh.")]:
            raised.append(raise_alert(m["id"], kind, text))
    graph.run(
        "MATCH (m:Matter {id: $id}) SET m.last_hash = $h, m.last_snapshot = $s, m.last_checked = $now",
        id=m["id"],
        h=new_hash,
        s=json.dumps(current or {}, default=str),
        now=now_iso(),
    )
    return raised
