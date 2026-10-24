# Gabapentin vs pregabalin: respiratory depression in FAERS
 
A pharmacovigilance signal-detection project on public FDA data, written in Python. It covers all four quarters of 2024. Every result is checked a second way.
 
## Question
 
Are reports of respiratory depression more common with gabapentin or pregabalin, and does it change when an opioid is on the same report?
 
## Data
 
FDA Adverse Event Reporting System (FAERS), quarterly ASCII files for 2024 Q1 to Q4, downloaded on 22 and 24 October 2026. The raw files are not stored in this repository because of their size. Download them from the FDA FAERS quarterly data extract files page and place each quarter in its own folder: `data/raw/faers_ascii_2024q1`, `faers_ascii_2024q2`, `faers_ascii_2024q3` and `faers_ascii_2024q4`.
 
## Definitions
 
- **Case cleaning:** cases on the FDA deleted-case lists are removed, and only the latest version of each case is kept. This takes 1,619,665 reports down to 1,480,549.
- **Drug:** gabapentin or pregabalin listed as primary or secondary suspect (PS or SS). Gabapentin enacarbil and compounded creams are excluded.
- **Opioid on the report:** any listed opioid (oxycodone, hydrocodone, morphine, fentanyl, tramadol, codeine, methadone, buprenorphine, hydromorphone, oxymorphone, tapentadol), in any role.
- **Outcome:** any of these reaction terms: respiratory depression, respiratory failure, acute respiratory failure, respiratory arrest, hypoventilation.
- **Reports listing both drugs** (391) are left out of all comparisons.
- **PRR and ROR:** two standard measures that compare how often an outcome is reported with a drug against how often it is reported otherwise. ROR is given with a 95% confidence interval.
## Results (2024 Q1 to Q4)
 
| Comparison | Reports with outcome / without | ROR (95% CI) |
|---|---|---|
| Gabapentin vs neither drug | 123 / 5145 | 4.78 (3.99 to 5.73) |
| Pregabalin vs neither drug | 85 / 6431 | 2.64 (2.13 to 3.28) |
| Gabapentin vs pregabalin, all reports | 123 / 5145 vs 85 / 6431 | 1.81 (1.37 to 2.39) |
| Gabapentin vs pregabalin, opioid on report | 77 / 1853 vs 62 / 3136 | 2.10 (1.50 to 2.95) |
| Gabapentin vs pregabalin, no opioid | 46 / 3292 vs 23 / 3295 | 2.00 (1.21 to 3.31) |
 
Full table: `results/signal_table.csv`. The earlier one-quarter pilot (2024 Q1 only) is kept in `results/signal_table_2024q1_pilot.csv`.
 
## What this shows
 
- Both drugs show a reporting signal for respiratory depression.
- Gabapentin is reported disproportionately more often than pregabalin, and the interval excludes 1.
- The opioid and no-opioid results have overlapping intervals, so this analysis cannot say whether an opioid changes the difference between the two drugs.
- The pilot (Q1 only) pointed the same way, with a wider interval.
## Sensitivity analysis
 
To test whether the result depends on the broad term "respiratory failure", the comparison was repeated with a stricter outcome: respiratory depression, respiratory arrest and hypoventilation only (`scripts/06_sensitivity.py`, results in `results/sensitivity_table.csv`).
 
| Comparison | Reports with outcome / without | ROR (95% CI) |
|---|---|---|
| Gabapentin vs pregabalin, all reports | 105 / 5163 vs 72 / 6444 | 1.82 (1.35 to 2.46) |
| Gabapentin vs pregabalin, opioid on report | 73 / 1857 vs 52 / 3146 | 2.38 (1.66 to 3.41) |
| Gabapentin vs pregabalin, no opioid | 32 / 3306 vs 20 / 3298 | 1.60 (0.91 to 2.80) |
 
The overall result is almost unchanged. The opioid and no-opioid intervals still overlap, and the no-opioid groups are small. Ratios against "neither drug" are much larger with the stricter outcome because it is rarer, so they should not be compared with the main table.
 
## Limits
 
- FAERS holds spontaneous reports. They show an association, not proof that a drug is related to a reaction, and they cannot give how often it happens.
- Reporting depends on many things: media attention, how long a drug has been on the market, and who reports.
- The outcome groups several terms, and respiratory failure has many causes.
- In the opioid group, the comparison reports also contain opioids, which themselves can cause respiratory depression. This raises the background rate and can hide a signal.
- Only 2024 is used. Cases can also be reported twice under different case IDs, which this analysis cannot detect.
- Patients are not adjusted for age, sex, dose or other illnesses.
## How to run
 
    python -m venv .venv
    source .venv/bin/activate
    pip install pandas
    python scripts/03_build_table.py
    python scripts/04_signal.py
    python scripts/05_checks.py
    python scripts/06_sensitivity.py
 
Scripts 01 and 02 only look at the raw data (01 covers 2024 Q1 only). Script 05 runs 9 checks, including a second independent count and a re-run that must give an identical results file.
 
## Plan
 
Add more years, then adjust for age and sex.