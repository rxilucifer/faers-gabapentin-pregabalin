# Gabapentin vs pregabalin: respiratory depression in FAERS

A pharmacovigilance signal-detection project on public FDA data, written in Python. This is a one-quarter pilot (January to March 2024). Every result is checked a second way.

## Question

Are reports of respiratory depression more common with gabapentin or pregabalin, and does it change when an opioid is on the same report?

## Data

FDA Adverse Event Reporting System (FAERS), quarterly ASCII files for 2024 Q1, downloaded on 22 October 2026. The raw files are not stored in this repository because of their size. Download them from the FDA FAERS quarterly data extract files page and place them in `data/raw/`.

## Definitions

- **Drug:** gabapentin or pregabalin listed as primary or secondary suspect (PS or SS). Gabapentin enacarbil and compounded creams are excluded.
- **Opioid on the report:** any listed opioid (oxycodone, hydrocodone, morphine, fentanyl, tramadol, codeine, methadone, buprenorphine, hydromorphone, oxymorphone, tapentadol), in any role.
- **Outcome:** any of these reaction terms: respiratory depression, respiratory failure, acute respiratory failure, respiratory arrest, hypoventilation.
- **Reports listing both drugs** (99) are left out of all comparisons.
- **PRR and ROR:** two standard measures that compare how often an outcome is reported with a drug against how often it is reported otherwise. ROR is given with a 95% confidence interval.

## Results (2024 Q1)

| Comparison | Reports with outcome / without | ROR (95% CI) |
|---|---|---|
| Gabapentin vs neither drug | 43 / 1588 | 6.22 (4.58 to 8.45) |
| Pregabalin vs neither drug | 31 / 1870 | 3.81 (2.66 to 5.45) |
| Gabapentin vs pregabalin, all reports | 43 / 1588 vs 31 / 1870 | 1.63 (1.02 to 2.60) |
| Gabapentin vs pregabalin, opioid on report | 29 / 627 vs 22 / 884 | 1.86 (1.06 to 3.27) |
| Gabapentin vs pregabalin, no opioid | 14 / 961 vs 9 / 986 | 1.60 (0.69 to 3.70) |

Full table: `results/signal_table.csv`.

## What this shows

- Both drugs show a reporting signal for respiratory depression.
- Gabapentin is reported somewhat more often than pregabalin, but the interval only just excludes 1.
- The opioid and no-opioid results have overlapping intervals, so this analysis cannot say whether an opioid changes the difference between the two drugs.

## Limits

- FAERS holds spontaneous reports. They show an association, not proof that a drug is related to a reaction, and they cannot give how often it happens.
- Reporting depends on many things: media attention, how long a drug has been on the market, and who reports.
- The outcome groups several terms, and respiratory failure has many causes.
- Only one quarter is used. The no-opioid groups are small (14 and 9 reports).
- Patients are not adjusted for age, sex, dose or other illnesses.

## How to run

    python -m venv .venv
    source .venv/bin/activate
    pip install pandas
    python scripts/03_build_table.py
    python scripts/04_signal.py
    python scripts/05_checks.py

Scripts 01 and 02 only look at the raw data. Script 05 runs 8 checks, including a second independent count and a re-run that must give an identical results file.

## Plan

Add more quarters, then adjust for age and sex.