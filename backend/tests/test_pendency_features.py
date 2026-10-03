import pandas as pd

from app.ml.pendency.features import build_matrix, clean_training_frame, fit_encoders


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"cnr": "A", "filing_date": "2010-01-05", "decision_date": "2011-03-01", "first_hearing": "2010-02-01", "criminal": True, "state": "Maharashtra", "district": "Nandurbar", "court": "1-1-5", "case_type": "cri.m.a.", "sections": ["IPC-379", "IPC-34"]},
            {"cnr": "B", "filing_date": "2010-06-10", "decision_date": "2010-06-01", "first_hearing": None, "criminal": False, "state": "Bihar", "district": "Patna", "court": "8-3-2", "case_type": "civil", "sections": []},
            {"cnr": "C", "filing_date": "2010-06-10", "decision_date": "2012-06-01", "first_hearing": "2010-09-01", "criminal": True, "state": "Bihar", "district": "Patna", "court": "8-3-2", "case_type": "civil", "sections": ["CrPC-125"]},
            {"cnr": "D", "filing_date": None, "decision_date": "2012-06-01", "first_hearing": None, "criminal": False, "state": None, "district": None, "court": None, "case_type": None, "sections": []},
        ]
    )


def test_cleaning_drops_negative_durations_and_missing_dates():
    df = clean_training_frame(sample_frame())
    assert df["cnr"].tolist() == ["A", "C"]
    assert df["days"].tolist() == [420, 722]


def test_matrix_has_expected_columns_and_handles_unseen_categories():
    train = clean_training_frame(sample_frame())
    enc = fit_encoders(train, top_k_sections=2)
    x = build_matrix(train, enc)
    assert list(x.columns) == enc.feature_names
    assert x["has_ipc"].tolist() == [1.0, 0.0]
    assert x["has_crpc"].tolist() == [0.0, 1.0]
    assert x["first_hearing_gap_days"].tolist() == [27.0, 83.0]

    unseen = pd.DataFrame([{**train.iloc[0].to_dict(), "state": "Kerala", "court": "99-9-9", "sections": ["IPC-999"]}])
    xu = build_matrix(unseen, enc)
    assert xu["state"].isna().all()
    assert xu["court"].isna().all()
    assert xu["n_sections"].iloc[0] == 1.0
