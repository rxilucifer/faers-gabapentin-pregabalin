"""Stage 1: look at the raw FAERS tables. Changes nothing."""
from pathlib import Path
import pandas as pd

BASE = Path("data/raw/faers_ascii_2024q1")
ASC = BASE / "ASCII"


def load(name):
    # FAERS files are separated by $ and may contain stray quote marks
    return pd.read_csv(ASC / f"{name}24Q1.txt", sep="$", dtype=str,
                       quoting=3, encoding="latin-1", low_memory=False)


demo, drug, reac = load("DEMO"), load("DRUG"), load("REAC")
print("Rows: DEMO", len(demo), "DRUG", len(drug), "REAC", len(reac))
print("Unique reports (primaryid):", demo["primaryid"].nunique())
print("Unique cases (caseid):", demo["caseid"].nunique())

multi = demo.groupby("caseid")["primaryid"].nunique()
print("Cases with more than one report version:", int((multi > 1).sum()))

deleted = pd.read_csv(BASE / "Deleted" / "DELETE24Q1.txt", header=None,
                      dtype=str, names=["caseid"])["caseid"].str.strip()
deleted = set(deleted[deleted.str.isdigit()])
print("Deleted case IDs listed:", len(deleted))
print("Deleted IDs present in DEMO:", demo["caseid"].isin(deleted).sum())

for word in ["GABAPENTIN", "PREGABALIN"]:
    a = drug["drugname"].fillna("").str.upper().str.contains(word)
    b = drug["prod_ai"].fillna("").str.upper().str.contains(word)
    print(word, "| in drugname:", int(a.sum()), "| in prod_ai:", int(b.sum()),
          "| either:", int((a | b).sum()))

print("Role codes:", drug["role_cod"].value_counts().to_dict())