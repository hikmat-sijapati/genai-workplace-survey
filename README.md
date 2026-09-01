# Generative AI in the Workplace: Productivity vs. Job Security Anxiety

## Research Question

How does employees' use of generative AI tools (e.g., ChatGPT, Copilot, Gemini) relate to
their perceived productivity gains and job-security anxiety, and how do these relationships
vary by role, seniority, and AI literacy?

## Repository Structure

```
genai-workplace-survey/
├── data/
│   ├── raw/
│   │   ├── responses_final.csv                     # collected responses (n=107) — primary dataset
│   └── processed/
│       ├── survey_clean.csv                        # cleaned dataset (n=107) — used in the report
├── docs/
│   ├── questionnaire/   # Survey instrument (Word/PDF + screenshot for report appendix)
│   ├── ethics/          # Ethics statement / consent form
│   └── codebook.md      # Raw→clean column mapping and value encodings
├── notebooks/
│   └── 01_analysis.ipynb   # Load raw export → clean/validate → descriptives → correlation →
│                            # ANOVA → regression → visualizations → thematic coding
├── reports/
│   └── figures/         # Exported charts used in the research report
├── src/
│   ├── preprocessing.py            # Raw Google Form export → codebook variables (renaming,
│   │                                # ordinal/Likert text parsing, index computation, validation)
│   ├── stats.py                    # Descriptives, correlation, ANOVA, OLS regression helpers
├── requirements.txt
├── environment.yaml               # Conda environment export for reproducible setup
├── LICENSE
└── README.md
```

## Data

- **Type:** Primary data collected via an original online survey (Google Forms), distributed
  to working professionals.
- **Status:** Data collection is complete — **107 valid, consenting responses**
  (`data/raw/responses_final.csv`) are the dataset used throughout the analysis and
  research report.
- **Access:** Raw exports keep the exact Google Form column headers (question text) and
  Likert answers as text (e.g. `"4 Agree"`). `src/preprocessing.py` renames columns and parses
  these into the numeric codes defined in `docs/codebook.md`, producing the analysis-ready
  file in `data/processed/`.
- **Instrument:** See `docs/questionnaire/Survey_Questionnaire.docx` (also screenshotted in the
  report Appendix per assignment requirements).

## Methodology (summary)

1. Quantitative, cross-sectional survey design (5-point Likert scales + demographics + 2 open
   items).
2. Raw export cleaning and coding (`src/preprocessing.py`): column renaming, consent
   filtering, ordinal/Likert text-to-code parsing, reverse-coding of `anx_4`, and computation
   of `productivity_index` / `anxiety_index`.
3. Data validation checks (row counts, duplicate timestamps, missingness, value-range
   assertions) — Section 2 of the notebook.
4. Descriptive statistics (usage frequency, sector, seniority distribution).
5. Correlation analysis: AI usage frequency vs. AI literacy vs. productivity index vs.
   anxiety index.
6. Group comparisons (one-way ANOVA) by job level and sector.
7. Multiple regression: productivity/anxiety index ~ usage frequency + AI literacy + job
   level (`src/stats.py`).
8. Light thematic/keyword-frequency pass on the two open-ended questions for triangulation.

Full methodological justification is provided in the research report (Section: Methodology).

## Reproducing the Analysis

```bash
# create / restore the project environment
conda env create -f environment.yaml
conda activate genai-workplace-survey

# run the analysis notebook
jupyter notebook notebooks/01_analysis.ipynb
```

If you prefer not to create a new environment, you can also install the requirements directly:

```bash
pip install -r requirements.txt
jupyter notebook notebooks/01_analysis.ipynb
```

## Ethics

This study collects anonymous, voluntary survey responses from adult participants (18+).
No personally identifying information is collected. Participants provide informed consent
before starting the survey. See `docs/ethics/ethics_statement.md` for full details.

## Citation & References

All citations for the accompanying research report are managed in Mendeley

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).
