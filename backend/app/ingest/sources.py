from typing import Protocol

from app.graph.client import graph

UPSERT_CASE = """
UNWIND $rows AS r
MERGE (c:Case {cnr: r.cnr})
SET c.filing_date = r.filing_date, c.decision_date = r.decision_date, c.status = r.status,
    c.purpose = r.purpose, c.disposition = r.disposition, c.year = r.year, c.source = r.source,
    c.updated_at = datetime()
WITH c, r
MERGE (court:Court {id: r.court_id}) ON CREATE SET court.name = r.court_name
MERGE (c)-[:FILED_IN]->(court)
WITH c, r
FOREACH (_ IN CASE WHEN r.district_id IS NULL THEN [] ELSE [1] END |
  MERGE (d:District {id: r.district_id}) ON CREATE SET d.name = r.district_name
  MERGE (court:Court {id: r.court_id})
  MERGE (court)-[:IN_DISTRICT]->(d)
  FOREACH (__ IN CASE WHEN r.state_id IS NULL THEN [] ELSE [1] END |
    MERGE (s:State {id: r.state_id}) ON CREATE SET s.name = r.state_name
    MERGE (d)-[:IN_STATE]->(s)))
WITH c, r
FOREACH (_ IN CASE WHEN r.type_id IS NULL THEN [] ELSE [1] END |
  MERGE (t:CaseType {id: r.type_id}) ON CREATE SET t.name = r.type_name
  MERGE (c)-[:OF_TYPE]->(t))
WITH c, r
UNWIND coalesce(r.section_keys, []) AS key
MERGE (s:Section {key: key})
MERGE (c)-[:UNDER]->(s)
"""


class CaseSource(Protocol):
    name: str

    def fetch_case(self, cnr: str) -> dict | None: ...

    def upsert_case(self, row: dict) -> None: ...


class GraphOnlySource:
    name = "graph"

    def fetch_case(self, cnr: str) -> dict | None:
        return None

    def upsert_case(self, row: dict) -> None:
        graph.write_batches(UPSERT_CASE, [row])


class LiveEcourtsSource:
    name = "ecourts-live"

    def fetch_case(self, cnr: str) -> dict | None:
        raise NotImplementedError("Live eCourts CNR lookup arrives in a later feature. The bulk dataset is the source for now.")

    def upsert_case(self, row: dict) -> None:
        graph.write_batches(UPSERT_CASE, [row])


def active_source() -> CaseSource:
    return GraphOnlySource()
