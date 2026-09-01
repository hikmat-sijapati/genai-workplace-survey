"""
stats.py

Statistical analysis helpers that operate on an already-cleaned dataframe
(output of src.preprocessing.clean_and_code). Kept separate from
preprocessing.py so raw-schema parsing and statistical modeling can evolve
independently.

Usage:
    from src.stats import descriptive_summary, run_correlations, run_group_anova, run_regression
"""

import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf


def descriptive_summary(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Return mean, sd, min, max for a list of numeric columns."""
    return df[cols].agg(["mean", "std", "min", "max"]).T


def run_correlations(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Pearson correlation matrix for the given numeric columns."""
    return df[cols].corr(method="pearson")


def run_group_anova(df: pd.DataFrame, value_col: str, group_col: str) -> dict:
    """One-way ANOVA of value_col across levels of group_col."""
    groups = [g[value_col].dropna().values for _, g in df.groupby(group_col)]
    f_stat, p_val = stats.f_oneway(*groups)
    return {"f_stat": f_stat, "p_value": p_val}


def run_regression(df: pd.DataFrame, formula: str):
    """
    Run an OLS regression using a statsmodels formula string, e.g.:
        "productivity_index ~ ai_usage_freq + ai_literacy + C(job_level)"
    Returns the fitted statsmodels results object.
    """
    return smf.ols(formula=formula, data=df).fit()
