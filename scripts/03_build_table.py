"""Stage 3: build one row per report with four yes/no flags."""
from pathlib import Path
import pandas as pd

ASC = Path("data/raw/faers_ascii_2024q1/ASCII")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)


def load(name):
    return pd.read_csv(ASC / f"{name}24Q1.txt", sep="$", dtype=str,
                       quoting=3, encoding="latin-1", low_memory=False)


demo, drug, reac = load("DEMO"), load("DRUG"), load("REAC")
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
RESP = ["RESPIRATORY DEPRESSION", "RESPIRATORY FAILURE",
           "RESPIRATORY ARREST", "HYPOVENTILATION", "ACUTE RESPIRATORY FAILURE"]

table = pd.DataFrame({"primaryid": demo["primaryid"]}).set_index("primaryid")
table["gabapentin"] = drug["primaryid"][gaba & suspect].drop_duplicates() \
    .to_frame().assign(v=1).set_index("primaryid")["v"]
table["pregabalin"] = drug["primaryid"][preg & suspect].drop_duplicates() \
    .to_frame().assign(v=1).set_index("primaryid")["v"]
table["opioid"] = drug["primaryid"][opioid].drop_duplicates() \
    .to_frame().assign(v=1).set_index("primaryid")["v"]
table["resp_dep"] = reac["primaryid"][pt.isin(RESP)].drop_duplicates() \
    .to_frame().assign(v=1).set_index("primaryid")["v"]
table = table.fillna(0).astype(int).reset_index()

table.to_csv(OUT / "analysis_table.csv", index=False)
print("\nReports:", len(table))
for c in ["gabapentin", "pregabalin", "opioid", "resp_dep"]:
    print(c, int(table[c].sum()))
print("Both drugs on one report:",
      int(((table.gabapentin == 1) & (table.pregabalin == 1)).sum()))