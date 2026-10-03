import pandas as pd

from app.graph.client import graph

TRAINING_QUERY = """
MATCH (s:State {id: $state_id})<-[:IN_STATE]-(d:District)<-[:IN_DISTRICT]-(court:Court)<-[:FILED_IN]-(c:Case {status: 'disposed'})
WHERE c.filing_date IS NOT NULL AND c.decision_date IS NOT NULL
OPTIONAL MATCH (c)-[:OF_TYPE]->(t:CaseType)
OPTIONAL MATCH (c)-[:UNDER]->(sec:Section)
RETURN c.cnr AS cnr, c.filing_date AS filing_date, c.decision_date AS decision_date, c.first_hearing AS first_hearing,
       c.criminal AS criminal, s.name AS state, d.name AS district, court.id AS court, t.name AS case_type,
       c.pet_adv_present AS pet_adv_present, c.def_adv_present AS def_adv_present,
       c.pet_state_party AS pet_state_party, c.def_state_party AS def_state_party,
       c.bailable_ipc AS bailable_ipc, c.number_sections_ipc AS number_sections_ipc, c.judge_position AS judge_position,
       collect(DISTINCT sec.key) AS sections
LIMIT $limit
"""

CASE_QUERY = """
MATCH (c:Case {cnr: $cnr})
OPTIONAL MATCH (c)-[:FILED_IN]->(court:Court)
OPTIONAL MATCH (court)-[:IN_DISTRICT]->(d:District)-[:IN_STATE]->(s:State)
OPTIONAL MATCH (c)-[:OF_TYPE]->(t:CaseType)
OPTIONAL MATCH (c)-[:UNDER]->(sec:Section)
RETURN c.cnr AS cnr, c.filing_date AS filing_date, c.decision_date AS decision_date, c.first_hearing AS first_hearing,
       c.status AS status, c.purpose AS purpose, c.criminal AS criminal, s.name AS state, d.name AS district,
       court.id AS court, court.name AS court_name, t.name AS case_type,
       c.pet_adv_present AS pet_adv_present, c.def_adv_present AS def_adv_present,
       c.pet_state_party AS pet_state_party, c.def_state_party AS def_state_party,
       c.bailable_ipc AS bailable_ipc, c.number_sections_ipc AS number_sections_ipc, c.judge_position AS judge_position,
       collect(DISTINCT sec.key) AS sections
"""

SIMILAR_QUERY = """
MATCH (c:Case {status: 'disposed'})-[:FILED_IN]->(court:Court {id: $court})
WHERE c.filing_date IS NOT NULL AND c.decision_date IS NOT NULL
OPTIONAL MATCH (c)-[:OF_TYPE]->(t:CaseType)
WITH c, t WHERE $case_type IS NULL OR t.name = $case_type
WITH duration.inDays(date(c.filing_date), date(c.decision_date)).days AS days
WHERE days >= 0
RETURN count(days) AS n, percentileCont(days, 0.5) AS median_days, percentileCont(days, 0.1) AS p10_days, percentileCont(days, 0.9) AS p90_days
"""


def fetch_training_frame(limit: int = 200000) -> pd.DataFrame:
    states = graph.run("MATCH (s:State)<-[:IN_STATE]-()<-[:IN_DISTRICT]-()<-[:FILED_IN]-(c:Case {status: 'disposed'}) RETURN s.id AS id, count(c) AS n ORDER BY n DESC")
    total = sum(r["n"] for r in states) or 1
    frames = []
    for r in states:
        share = max(1, round(limit * r["n"] / total))
        rows = graph.run(TRAINING_QUERY, state_id=r["id"], limit=share)
        if rows:
            frames.append(pd.DataFrame(rows))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def fetch_case(cnr: str) -> dict | None:
    return graph.run_one(CASE_QUERY, cnr=cnr)


def similar_cases_benchmark(court: str | None, case_type: str | None) -> dict | None:
    if not court:
        return None
    row = graph.run_one(SIMILAR_QUERY, court=court, case_type=case_type)
    if not row or not row["n"]:
        return None
    return row
