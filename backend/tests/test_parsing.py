from app.verify.citations import extract_citations, normalise_citation
from app.verify.statutes import normalise_act, parse_section_refs, section_key


def test_reporter_citations_are_extracted():
    text = "As held in AIR 1999 SC 123 and (2014) 8 SCC 273, and later in 2020 SCC OnLine SC 571."
    found = dict(extract_citations(text))
    assert "AIR 1999 SC 123" in found
    assert "(2014) 8 SCC 273" in found
    assert "2020 SCC OnLine SC 571" in found
    assert all(kind == "reporter" for kind in found.values())


def test_dotted_and_bracket_reporters_normalise_to_metadata_form():
    text = "See [1950] 1 S.C.R. 1008 and A.I.R. 1950 S.C. 27 and (1975) 2 S.C.C. 159."
    raws = [raw for raw, kind in extract_citations(text) if kind == "reporter"]
    norms = {normalise_citation(r) for r in raws}
    assert normalise_citation("[1950] 1 S.C.R. 1008") in norms
    assert normalise_citation("AIR 1950 SC 27") in norms
    assert normalise_citation("(1975) 2 SCC 159") in norms


def test_case_names_are_extracted():
    text = "Reliance was placed on Arnesh Kumar v. State of Bihar, (2014) 8 SCC 273."
    kinds = dict(extract_citations(text))
    assert any(k == "case_name" and raw.startswith("Arnesh Kumar v. State of Bihar") for raw, k in kinds.items())


def test_case_name_does_not_swallow_the_preceding_sentence():
    text = "I am entitled to bail as per the ratio laid down in the judgment of ASHOK DHANKAD versus STATE OF NCT OF DELHI, and so on."
    names = [raw for raw, k in extract_citations(text) if k == "case_name"]
    assert names == ["ASHOK DHANKAD versus STATE OF NCT OF DELHI"]


def test_citation_normalisation_ignores_spacing_and_dots():
    assert normalise_citation("A.I.R. 1999 S.C. 123") == normalise_citation("AIR 1999 SC 123")
    assert normalise_citation("(2014) 8 SCC 273") == "(2014)8SCC273"


def test_act_aliases():
    assert normalise_act("Indian Penal Code") == "IPC"
    assert normalise_act("I.P.C.") is None
    assert normalise_act("CrPC") == "CrPC"
    assert normalise_act("Bharatiya Nagarik Suraksha Sanhita") == "BNSS"
    assert normalise_act("Arms Act") is None


def test_section_refs_from_prose():
    text = "charged under Section 302 of the Indian Penal Code and Section 25 of the Arms Act, released u/s 436A CrPC, see Sec. 498A IPC."
    assert parse_section_refs(text) == ["CrPC-436A", "IPC-302", "IPC-498A"]


def test_section_key_is_uppercase_without_spaces():
    assert section_key("ipc", "498 a") == "ipc-498A"
