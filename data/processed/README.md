# Processed Data

- **`survey_clean.csv`** — the analysis dataset (n = 107), cleaned and coded from
  `data/raw/responses_final.csv` by `src/preprocessing.py`. This is what
  `notebooks/01_analysis.ipynb`. See
  `docs/codebook.md` for the full raw→clean column mapping.

## Reproducing from raw

```python
from src.preprocessing import load_google_form_export, clean_and_code
raw = load_google_form_export("data/raw/responses_final.csv")
clean = clean_and_code(raw)
clean.to_csv("data/processed/survey_clean.csv", index=False)
```
