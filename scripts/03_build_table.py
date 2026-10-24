"""Stage 3: build one row per report with yes/no flags (all four quarters of 2024)."""
from pathlib import Path
import pandas as pd

QUARTERS = ["2024q1", "2024q2", "2024q3", "2024q4"]
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)


def load(name, cols):
    """Read one FAERS table from every quarter and stack them together."""
    parts = []
    for q in QUARTERS:
        yyq = q[2:].upper()  # "2024q1" -> "24Q1"
        path = Path(f"data/raw/faers_ascii_{q}/ASCII/{name}{yyq}.txt")
        parts.append(pd.read_csv(path, sep="$", dtype=str, quoting=3,
                                 encoding="latin-1", low_memory=False,
                                 usecols=cols))
    return pd.concat(parts, ignore_index=True)


def load_deleted():
    """Case IDs the FDA has withdrawn, from every quarter's Deleted file."""
    ids = set()
    for q in QUARTERS:
        yyq = q[2:].upper()
        path = Path(f"data/raw/faers_ascii_{q}/Deleted/DELETE{yyq}.txt")
        s = pd.read_csv(path, header=None, dtype=str, names=["caseid"])["caseid"].str.strip()
        ids |= set(s[s.str.isdigit()])
    return ids


demo = load("DEMO", ["primaryid", "caseid", "caseversion"])
drug = load("DRUG", ["primaryid", "role_cod", "drugname", "prod_ai"])
reac = load("REAC", ["primaryid", "pt"])

# One version per case: drop deleted cases, then keep the latest version
print("Reports before cleaning:", len(demo))
demo = demo[~demo["caseid"].isin(load_deleted())].copy()
demo["caseversion"] = demo["caseversion"].astype(int)
demo = demo.sort_values("caseversion").drop_duplicates("caseid", keep="last")
print("Reports after removing deleted cases and old versions:", len(demo))
keep = set(demo["primaryid"])
drug = drug[drug["primaryid"].isin(keep)]
reac = reac[reac["primaryid"].isin(keep)]

ai = drug["prod_ai"].fillna("").str.upper().str.strip()
name = drug["drugname"].fillna("").str.upper().str.strip()

# Rule 1: the drug counts only if it is a suspect drug (PS or SS)
suspect = drug["role_cod"].isin(["PS", "SS"])
# Rule 2: exact active ingredient, or blank ingredient with a known name
gaba = (ai == "GABAPENTIN") | ((ai == "") & name.isin(["GABAPENTIN", "NEURONTIN"]))
preg = (ai == "PREGABALIN") | ((ai == "") & name.isin(["PREGABALIN", "LYRICA"]))
print("Gabapentin rows kept:", int((gaba & suspect).sum()),
      "| pregabalin rows kept:", int((preg & suspect).sum()))

OPIOIDS = ["OXYCODONE", "HYDROCODONE", "MORPHINE", "FENTANYL", "TRAMADOL",
           "CODEINE", "METHADONE", "BUPRENORPHINE", "HYDROMORPHONE",
           "OXYMORPHONE", "TAPENTADOL"]
opioid = ai.str.contains("|".join(OPIOIDS))  # any role counts

pt = reac["pt"].fillna("").str.upper().str.strip()
print("Reaction terms containing RESPIRAT (top 12):")
print(pt[pt.str.contains("RESPIRAT")].value_counts().head(12).to_string())

# Main outcome and the stricter outcome used for the sensitivity analysis
RESP = ["RESPIRATORY DEPRESSION", "RESPIRATORY FAILURE",
        "RESPIRATORY ARREST", "HYPOVENTILATION", "ACUTE RESPIRATORY FAILURE"]
RESP_STRICT = ["RESPIRATORY DEPRESSION", "RESPIRATORY ARREST", "HYPOVENTILATION"]

table = pd.DataFrame({"primaryid": demo["primaryid"]}).set_index("primaryid")
table["gabapentin"] = drug["primaryid"][gaba & suspect].drop_duplicates() \
    .to_frame().assign(v=1).set_index("primaryid")["v"]
table["pregabalin"] = drug["primaryid"][preg & suspect].drop_duplicates() \
    .to_frame().assign(v=1).set_index("primaryid")["v"]
table["opioid"] = drug["primaryid"][opioid].drop_duplicates() \
    .to_frame().assign(v=1).set_index("primaryid")["v"]
table["resp_dep"] = reac["primaryid"][pt.isin(RESP)].drop_duplicates() \
    .to_frame().assign(v=1).set_index("primaryid")["v"]
table["resp_strict"] = reac["primaryid"][pt.isin(RESP_STRICT)].drop_duplicates() \
    .to_frame().assign(v=1).set_index("primaryid")["v"]
table = table.fillna(0).astype(int).reset_index()

table.to_csv(OUT / "analysis_table.csv", index=False)
print("\nReports:", len(table))
for c in ["gabapentin", "pregabalin", "opioid", "resp_dep", "resp_strict"]:
    print(c, int(table[c].sum()))
print("Both drugs on one report:",
      int(((table.gabapentin == 1) & (table.pregabalin == 1)).sum()))