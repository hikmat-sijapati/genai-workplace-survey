# Codebook — Survey Variables

This codebook documents the mapping from the **raw Google Form export**
(column headers = full question text) to the **analysis-ready variable
names** used in the notebook and `src/preprocessing.py`.

## Raw → Clean column mapping

| Raw Google Form column (exact header) | Clean variable | Type |
|---|---|---|
| `Do you consent to participate?` | `consent` | text (filtered, dropped after use) |
| `A1. What is your age group?` | `age_group` | categorical |
| `A2. What is your gender?` | `gender` | categorical |
| `A3. What is your current employment sector?` | `sector` | categorical |
| `A4. What is your current job level?` | `job_level_text` / `job_level` | ordinal text / 1–5 code |
| `A5. How many years of work experience do you have?` | `experience_years_text` / `experience_years_code` | ordinal text / 1–5 code |
| `B1. How frequently do you use generative AI tools...?` | `ai_usage_freq_text` / `ai_usage_freq` | ordinal text / 1–5 code |
| `B2. Which of the following best describes...?` | `ai_primary_use` | categorical |
| `B3. How would you rate your own proficiency...?` | `ai_literacy_text` / `ai_literacy` | ordinal text / 1–5 code |
| ` [Generative AI tools help me complete tasks faster.]` | `prod_1` | Likert 1–5 |
| ` [Generative AI improves the overall quality...]` | `prod_2` | Likert 1–5 |
| ` [I feel more creative when using generative AI tools.]` | `prod_3` | Likert 1–5 |
| ` [Generative AI reduces the amount of repetitive/manual work I do.]` | `prod_4` | Likert 1–5 |
| ` [Overall, generative AI has increased my productivity at work.]` | `prod_5` | Likert 1–5 |
| ` [I am concerned that generative AI could eventually replace...]` | `anx_1` | Likert 1–5 |
| ` [My organization's growing use of AI tools makes me feel less secure...]` | `anx_2` | Likert 1–5 |
| ` [I feel pressure to constantly upskill...]` | `anx_3` | Likert 1–5 |
| ` [I trust my organization to manage AI adoption fairly...]` | `anx_4` (+ `anx_4_rev`) | Likert 1–5, **reverse-coded** |
| ` [Overall, generative AI increases my anxiety...]` | `anx_5` | Likert 1–5 |
| `E1. What is your biggest concern...?` | `concern_text` | open text |
| `E2. What is the most valuable benefit...?` | `benefit_text` | open text |

Derived columns: `productivity_index` = mean(`prod_1`..`prod_5`);
`anxiety_index` = mean(`anx_1`, `anx_2`, `anx_3`, `anx_4_rev`, `anx_5`).

## Raw response format notes

- Likert/grid answers are exported as text in the form `"<n> <Label>"`, e.g.
  `"4 Agree"`, `"3 Neutral"`, `"1 Strongly Disagree"`. `src/preprocessing.py`
  extracts the leading digit via regex — do not assume the raw value is
  already numeric.
- Ordinal demographic/usage fields (job level, experience, usage frequency,
  literacy) are exported as their **option text**, not a number. These are
  mapped to 1–5 codes via explicit dictionaries in `src/preprocessing.py`
  (`JOB_LEVEL_MAP`, `EXPERIENCE_MAP`, `USAGE_FREQ_MAP`, `LITERACY_MAP`).
- `age_group` and `experience_years_text` use an en dash (`–`, U+2013), not a
  hyphen — copy option text exactly if extending the maps.

## Value encodings

| Variable | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| `job_level` | Entry-level / Junior | Mid-level / Associate | Senior / Specialist | Managerial | Executive / C-level |
| `experience_years_code` | Less than 1 year | 1–3 years | 4–7 years | 8–15 years | More than 15 years |
| `ai_usage_freq` | Never | Rarely (a few times a month) | Occasionally (a few times a week) | Frequently (daily) | Constantly (multiple times per day) |
| `ai_literacy` | Beginner | Basic | Intermediate | Advanced | Expert |

## Reverse Coding Note

`anx_4` ("I trust my organization to manage AI adoption fairly and
transparently") is positively worded relative to the anxiety construct and
is reverse-scored as `anx_4_rev = 6 - anx_4` before being averaged into
`anxiety_index`.

## Consent filtering

Rows are only retained if `consent` exactly equals *"I have read the above
and voluntarily agree to participate."* This is a defensive check —
the live form's branching logic should already prevent non-consenting
submissions from reaching later questions, but the check guards against
partial/edited exports.
