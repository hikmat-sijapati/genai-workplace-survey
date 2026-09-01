"""
preprocessing.py

This replaces the earlier placeholder assumption that raw exports already
arrived pre-coded as prod_1..5 / anx_1..5 / numeric ordinals. Google
Form exports use the full question text as column headers and "<n> <Label>"
text (e.g. "4 Agree") for Likert/grid answers, so this module does the
renaming + text-to-code parsing.

Usage:
    from src.preprocessing import load_google_form_export, clean_and_code
    raw = load_google_form_export("data/raw/responses_final.csv")
    clean = clean_and_code(raw)
"""

import re
import pandas as pd
import numpy as np

# --- Exact raw column headers (must match the live Google Form export) ---
COL_CONSENT = "Do you consent to participate?"
COL_A1 = "A1. What is your age group?"
COL_A2 = "A2. What is your gender?"
COL_A3 = "A3. What is your current employment sector?"
COL_A4 = "A4. What is your current job level?"
COL_A5 = "A5. How many years of work experience do you have?"
COL_B1 = "B1. How frequently do you use generative AI tools (e.g., ChatGPT, Copilot, Gemini, Claude) for work-related tasks?"
COL_B2 = "B2. Which of the following best describes how you primarily use generative AI at work? (select the closest match)"
COL_B3 = "B3. How would you rate your own proficiency/literacy with generative AI tools?"

COL_PROD = [
    " [Generative AI tools help me complete tasks faster.]",
    " [Generative AI improves the overall quality of my work output.]",
    " [I feel more creative when using generative AI tools.]",
    " [Generative AI reduces the amount of repetitive/manual work I do.]",
    " [Overall, generative AI has increased my productivity at work.]",
]
COL_ANX = [
    " [I am concerned that generative AI could eventually replace parts of my job.]",
    " [My organization's growing use of AI tools makes me feel less secure in my role.]",
    " [I feel pressure to constantly upskill to keep pace with AI developments.]",
    " [I trust my organization to manage AI adoption fairly and transparently.]",
    " [Overall, generative AI increases my anxiety about my long-term career prospects.]",
]
COL_E1 = "E1. What is your biggest concern (if any) about the use of generative AI in your workplace?"
COL_E2 = "E2. What is the most valuable benefit (if any) you have experienced from using generative AI at work?"

CONSENT_TEXT = "I have read the above and voluntarily agree to participate."

# Rename map: raw header -> codebook variable name
RENAME_MAP = {
    COL_CONSENT: "consent",
    COL_A1: "age_group",
    COL_A2: "gender",
    COL_A3: "sector",
    COL_A4: "job_level_text",
    COL_A5: "experience_years_text",
    COL_B1: "ai_usage_freq_text",
    COL_B2: "ai_primary_use",
    COL_B3: "ai_literacy_text",
    COL_PROD[0]: "prod_1",
    COL_PROD[1]: "prod_2",
    COL_PROD[2]: "prod_3",
    COL_PROD[3]: "prod_4",
    COL_PROD[4]: "prod_5",
    COL_ANX[0]: "anx_1",
    COL_ANX[1]: "anx_2",
    COL_ANX[2]: "anx_3",
    COL_ANX[3]: "anx_4",  # reverse-coded trust item
    COL_ANX[4]: "anx_5",
    COL_E1: "concern_text",
    COL_E2: "benefit_text",
}

# Ordinal text -> numeric code maps (order = ordinal rank, 1 = lowest)
JOB_LEVEL_MAP = {
    "Entry-level / Junior": 1, "Mid-level / Associate": 2, "Senior / Specialist": 3,
    "Managerial": 4, "Executive / C-level": 5,
}
EXPERIENCE_MAP = {
    "Less than 1 year": 1, "1–3 years": 2, "4–7 years": 3,
    "8–15 years": 4, "More than 15 years": 5,
}
USAGE_FREQ_MAP = {
    "Never": 1, "Rarely (a few times a month)": 2, "Occasionally (a few times a week)": 3,
    "Frequently (daily)": 4, "Constantly (multiple times per day)": 5,
}
LITERACY_MAP = {
    "Beginner": 1, "Basic": 2, "Intermediate": 3, "Advanced": 4, "Expert": 5,
}


def load_google_form_export(path: str) -> pd.DataFrame:
    """Load a raw Google Form export, CSV or XLSX, by file extension."""
    if str(path).lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    return pd.read_csv(path)


def _parse_likert(series: pd.Series) -> pd.Series:
    """Extract the leading integer from Google Forms grid answers like '4 Agree'."""
    return series.astype(str).str.extract(r"^(\d)")[0].astype(float)


def clean_and_code(df_raw: pd.DataFrame, require_consent: bool = True) -> pd.DataFrame:
    """
    Rename raw Google Form columns to codebook variable names, parse ordinal
    text fields to numeric codes, reverse-code anx_4, and compute
    productivity_index / anxiety_index.

    Rows without the exact consent string are dropped by default (defensive
    check — the live form's branching logic should already guarantee this).

    """
    df = df_raw.rename(columns=RENAME_MAP).copy()

    required_cols = list(RENAME_MAP.values())
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Expected columns missing after rename — raw schema may have "
                          f"changed: {missing}")

    if require_consent:
        before = len(df)
        df = df[df["consent"].astype(str).str.strip() == CONSENT_TEXT].copy()
        dropped = before - len(df)
        if dropped:
            print(f"Dropped {dropped} row(s) without valid consent.")

    df["job_level"] = df["job_level_text"].map(JOB_LEVEL_MAP)
    df["experience_years_code"] = df["experience_years_text"].map(EXPERIENCE_MAP)
    df["ai_usage_freq"] = df["ai_usage_freq_text"].map(USAGE_FREQ_MAP)
    df["ai_literacy"] = df["ai_literacy_text"].map(LITERACY_MAP)

    prod_cols = ["prod_1", "prod_2", "prod_3", "prod_4", "prod_5"]
    anx_cols = ["anx_1", "anx_2", "anx_3", "anx_4", "anx_5"]
    for c in prod_cols + anx_cols:
        df[c] = _parse_likert(df[c])

    # sanity check: all parsed Likert values must be 1-5
    for c in prod_cols + anx_cols + ["job_level", "experience_years_code", "ai_usage_freq", "ai_literacy"]:
        bad = df[df[c].isna() | ~df[c].between(1, 5)]
        if len(bad):
            raise ValueError(f"{len(bad)} unparseable/out-of-range value(s) in column '{c}'. "
                              f"Check for unexpected free-text or option-wording changes in the form.")

    df["productivity_index"] = df[prod_cols].mean(axis=1).round(2)
    df["anx_4_rev"] = 6 - df["anx_4"]
    anx_final_cols = ["anx_1", "anx_2", "anx_3", "anx_4_rev", "anx_5"]
    df["anxiety_index"] = df[anx_final_cols].mean(axis=1).round(2)

    df.insert(0, "respondent_id", [f"R{1000+i}" for i in range(len(df))])

    keep_cols = [
        "respondent_id",
        "age_group", "gender", "sector",
        "job_level_text", "job_level", "experience_years_text", "experience_years_code",
        "ai_usage_freq_text", "ai_usage_freq", "ai_primary_use",
        "ai_literacy_text", "ai_literacy",
        *prod_cols, "productivity_index",
        *anx_cols, "anx_4_rev", "anxiety_index",
        "concern_text", "benefit_text",
    ]
    return df[keep_cols].reset_index(drop=True)


def validation_summary(df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> dict:
    """Return a dict of basic data-quality checks for reporting."""
    return {
        "raw_rows": len(df_raw),
        "clean_rows": len(df_clean),
        "rows_dropped_consent_or_parse": len(df_raw) - len(df_clean),
        "missing_concern_text_pct": round(100 * (df_clean["concern_text"].isna() | (df_clean["concern_text"].astype(str).str.strip() == "")).mean(), 1),
        "missing_benefit_text_pct": round(100 * (df_clean["benefit_text"].isna() | (df_clean["benefit_text"].astype(str).str.strip() == "")).mean(), 1),
        "productivity_index_range": (df_clean["productivity_index"].min(), df_clean["productivity_index"].max()),
        "anxiety_index_range": (df_clean["anxiety_index"].min(), df_clean["anxiety_index"].max()),
    }


if __name__ == "__main__":
    raw = load_google_form_export("data/raw/responses_final.csv")
    clean = clean_and_code(raw)
    print(validation_summary(raw, clean))
    clean.to_csv("data/processed/survey_clean.csv", index=False)
    print(f"Saved {len(clean)} cleaned rows to data/processed/survey_clean.csv")
