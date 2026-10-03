from app.graph.client import Graph

CONSTRAINTS = [
    "CREATE CONSTRAINT case_cnr IF NOT EXISTS FOR (c:Case) REQUIRE c.cnr IS UNIQUE",
    "CREATE CONSTRAINT court_id IF NOT EXISTS FOR (c:Court) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT district_id IF NOT EXISTS FOR (d:District) REQUIRE d.id IS UNIQUE",
    "CREATE CONSTRAINT state_id IF NOT EXISTS FOR (s:State) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT casetype_id IF NOT EXISTS FOR (t:CaseType) REQUIRE t.id IS UNIQUE",
    "CREATE CONSTRAINT judgment_id IF NOT EXISTS FOR (j:Judgment) REQUIRE j.id IS UNIQUE",
    "CREATE CONSTRAINT act_id IF NOT EXISTS FOR (a:Act) REQUIRE a.id IS UNIQUE",
    "CREATE CONSTRAINT section_key IF NOT EXISTS FOR (s:Section) REQUIRE s.key IS UNIQUE",
    "CREATE CONSTRAINT matter_id IF NOT EXISTS FOR (m:Matter) REQUIRE m.id IS UNIQUE",
    "CREATE CONSTRAINT alert_id IF NOT EXISTS FOR (a:Alert) REQUIRE a.id IS UNIQUE",
    "CREATE CONSTRAINT review_id IF NOT EXISTS FOR (r:ReviewItem) REQUIRE r.id IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX case_filing IF NOT EXISTS FOR (c:Case) ON (c.filing_date)",
    "CREATE INDEX case_status IF NOT EXISTS FOR (c:Case) ON (c.status)",
    "CREATE INDEX judgment_date IF NOT EXISTS FOR (j:Judgment) ON (j.date)",
    "CREATE INDEX judgment_citation IF NOT EXISTS FOR (j:Judgment) ON (j.citation)",
    "CREATE FULLTEXT INDEX judgment_text IF NOT EXISTS FOR (j:Judgment) ON EACH [j.title, j.headnote]",
    "CREATE FULLTEXT INDEX section_text IF NOT EXISTS FOR (s:Section) ON EACH [s.title, s.number]",
]

VECTOR_INDEX = """
CREATE VECTOR INDEX judgment_embedding IF NOT EXISTS
FOR (j:Judgment) ON (j.embedding)
OPTIONS {indexConfig: {`vector.dimensions`: $dims, `vector.similarity_function`: 'cosine'}}
"""


def ensure_schema(graph: Graph, embedding_dims: int = 1024) -> None:
    for stmt in CONSTRAINTS + INDEXES:
        graph.run(stmt)
    graph.run(VECTOR_INDEX, dims=embedding_dims)
