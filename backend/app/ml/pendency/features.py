from dataclasses import dataclass, field

import numpy as np
import pandas as pd

CATEGORICAL = ["state", "district", "court", "case_type", "judge_position"]
NUMERIC = [
    "filing_year",
    "filing_month",
    "filing_dow",
    "first_hearing_gap_days",
    "criminal",
    "n_sections",
    "has_ipc",
    "has_crpc",
    "pet_adv_present",
    "def_adv_present",
    "pet_state_party",
    "def_state_party",
    "bailable_ipc",
    "number_sections_ipc",
]
BOOL_COLUMNS = ["criminal", "pet_adv_present", "def_adv_present", "pet_state_party", "def_state_party", "bailable_ipc"]

MIN_DAYS = 0
MAX_DAYS = 6000


@dataclass
class Encoders:
    categories: dict[str, list[str]] = field(default_factory=dict)
    top_sections: list[str] = field(default_factory=list)

    @property
    def feature_names(self) -> list[str]:
        return NUMERIC + CATEGORICAL + [f"sec_{s}" for s in self.top_sections]


def target_days(df: pd.DataFrame) -> pd.Series:
    filing = pd.to_datetime(df["filing_date"], errors="coerce")
    decision = pd.to_datetime(df["decision_date"], errors="coerce")
    return (decision - filing).dt.days


def clean_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["days"] = target_days(df)
    mask = df["days"].between(MIN_DAYS, MAX_DAYS) & df["filing_date"].notna()
    return df.loc[mask].reset_index(drop=True)


def column(df: pd.DataFrame, name: str) -> pd.Series:
    if name in df.columns:
        return df[name]
    return pd.Series([None] * len(df), index=df.index, dtype="object")


def fit_encoders(df: pd.DataFrame, top_k_sections: int = 40) -> Encoders:
    enc = Encoders()
    for col in CATEGORICAL:
        enc.categories[col] = sorted(column(df, col).dropna().astype(str).unique().tolist())
    counts = pd.Series([s for secs in column(df, "sections") for s in (secs or [])]).value_counts()
    enc.top_sections = counts.head(top_k_sections).index.tolist()
    return enc


def as_flag(series: pd.Series) -> pd.Series:
    return series.map({True: 1.0, False: 0.0, 1: 1.0, 0: 0.0}).astype("float32")


def build_matrix(df: pd.DataFrame, enc: Encoders) -> pd.DataFrame:
    filing = pd.to_datetime(column(df, "filing_date"), errors="coerce")
    first = pd.to_datetime(column(df, "first_hearing"), errors="coerce")
    sections = column(df, "sections").apply(lambda s: set(s or []))

    out = pd.DataFrame(index=df.index)
    out["filing_year"] = filing.dt.year.astype("float32")
    out["filing_month"] = filing.dt.month.astype("float32")
    out["filing_dow"] = filing.dt.dayofweek.astype("float32")
    gap = (first - filing).dt.days.astype("float32")
    out["first_hearing_gap_days"] = gap.where(gap.between(0, 3650))
    for col in BOOL_COLUMNS:
        out[col] = as_flag(column(df, col))
    out["n_sections"] = sections.apply(len).astype("float32")
    out["has_ipc"] = sections.apply(lambda s: float(any(k.startswith("IPC-") for k in s))).astype("float32")
    out["has_crpc"] = sections.apply(lambda s: float(any(k.startswith("CrPC-") for k in s))).astype("float32")
    out["number_sections_ipc"] = pd.to_numeric(column(df, "number_sections_ipc"), errors="coerce").astype("float32")

    for col in CATEGORICAL:
        out[col] = pd.Categorical(column(df, col).astype("string"), categories=enc.categories[col])

    for key in enc.top_sections:
        out[f"sec_{key}"] = sections.apply(lambda s, k=key: float(k in s)).astype("float32")

    return out[enc.feature_names]


def log_target(days: pd.Series) -> np.ndarray:
    return np.log1p(days.to_numpy(dtype="float64"))


def unlog(pred: np.ndarray) -> np.ndarray:
    return np.expm1(pred)
