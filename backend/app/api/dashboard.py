from fastapi import APIRouter, Query

from app.graph.client import graph

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary():
    row = graph.run_one(
        """
        MATCH (c:Case)
        WITH count(c) AS total,
             sum(CASE WHEN c.status = 'pending' THEN 1 ELSE 0 END) AS pending,
             sum(CASE WHEN c.status = 'disposed' THEN 1 ELSE 0 END) AS disposed,
             collect(CASE WHEN c.status = 'disposed' AND c.filing_date IS NOT NULL AND c.decision_date IS NOT NULL
                          THEN duration.inDays(date(c.filing_date), date(c.decision_date)).days END) AS durations
        WITH total, pending, disposed, [d IN durations WHERE d IS NOT NULL] AS ds
        RETURN total, pending, disposed,
               CASE WHEN size(ds) = 0 THEN null ELSE apoc.coll.avg(ds) END AS mean_days_to_disposal,
               CASE WHEN size(ds) = 0 THEN null ELSE apoc.coll.sort(ds)[toInteger(size(ds) / 2)] END AS median_days_to_disposal
        """
    )
    counts = graph.run_one(
        """
        OPTIONAL MATCH (j:Judgment) WITH count(j) AS judgments
        OPTIONAL MATCH ()-[c:CITES]->() WITH judgments, count(c) AS cites
        OPTIONAL MATCH (s:Section) WITH judgments, cites, count(s) AS sections
        OPTIONAL MATCH (m:Matter) WITH judgments, cites, sections, count(m) AS matters
        OPTIONAL MATCH (r:ReviewItem {status: 'pending'})
        RETURN judgments, cites, sections, matters, count(r) AS pending_reviews
        """
    )
    return {**(row or {}), **(counts or {})}


@router.get("/pendency-by-age")
def pendency_by_age(as_of: str | None = Query(None, description="ISO date; defaults to the latest decision or hearing date in the data")):
    return graph.run(
        """
        MATCH (c:Case) WHERE c.decision_date IS NOT NULL OR c.last_hearing IS NOT NULL
        WITH date(coalesce(c.decision_date, c.last_hearing)) AS d
        WHERE d <= date()
        WITH max(d) AS latest
        WITH CASE WHEN $as_of IS NULL THEN latest ELSE date($as_of) END AS ref
        MATCH (c:Case {status: 'pending'}) WHERE c.filing_date IS NOT NULL
        WITH ref, duration.inDays(date(c.filing_date), ref).days / 365.25 AS years
        WITH ref,
             CASE WHEN years < 1 THEN 'Under 1 year' WHEN years < 3 THEN '1 to 3 years' WHEN years < 5 THEN '3 to 5 years'
                  WHEN years < 10 THEN '5 to 10 years' ELSE 'Over 10 years' END AS band,
             CASE WHEN years < 1 THEN 0 WHEN years < 3 THEN 1 WHEN years < 5 THEN 2 WHEN years < 10 THEN 3 ELSE 4 END AS ord
        WITH ref, band, ord, count(*) AS n
        WITH ref, collect({band: band, ord: ord, n: n}) AS rows, sum(n) AS total
        UNWIND rows AS r
        RETURN r.band AS band, r.n AS count, round(100.0 * r.n / total, 1) AS share, toString(ref) AS as_of
        ORDER BY r.ord
        """,
        as_of=as_of,
    )


@router.get("/pendency")
def pendency(group_by: str = Query("state", pattern="^(state|district|court|case_type|year)$"), limit: int = 50):
    match = {
        "state": "MATCH (c:Case)-[:FILED_IN]->(:Court)-[:IN_DISTRICT]->(:District)-[:IN_STATE]->(g:State)",
        "district": "MATCH (c:Case)-[:FILED_IN]->(:Court)-[:IN_DISTRICT]->(g:District)",
        "court": "MATCH (c:Case)-[:FILED_IN]->(g:Court)",
        "case_type": "MATCH (c:Case)-[:OF_TYPE]->(g:CaseType)",
        "year": "MATCH (c:Case) WITH c, {name: toString(c.year), id: toString(c.year)} AS g",
    }[group_by]
    return graph.run(
        f"""
        {match}
        WITH g, count(c) AS total,
             sum(CASE WHEN c.status = 'pending' THEN 1 ELSE 0 END) AS pending,
             sum(CASE WHEN c.status = 'disposed' THEN 1 ELSE 0 END) AS disposed,
             [x IN collect(CASE WHEN c.status = 'disposed' AND c.filing_date IS NOT NULL AND c.decision_date IS NOT NULL
                   THEN duration.inDays(date(c.filing_date), date(c.decision_date)).days END) WHERE x IS NOT NULL] AS ds
        RETURN g.name AS name, g.id AS id, total, pending, disposed,
               round(100.0 * pending / total, 1) AS pending_share,
               CASE WHEN size(ds) = 0 THEN null ELSE round(apoc.coll.avg(ds)) END AS mean_days_to_disposal
        ORDER BY pending DESC LIMIT $limit
        """,
        limit=limit,
    )


@router.get("/stages")
def stages(limit: int = 20):
    return graph.run(
        """
        MATCH (c:Case {status: 'pending'}) WHERE c.purpose IS NOT NULL
        RETURN c.purpose AS stage, count(*) AS pending ORDER BY pending DESC LIMIT $limit
        """,
        limit=limit,
    )
