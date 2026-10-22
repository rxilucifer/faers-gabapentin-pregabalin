"""Stage 2: see how gabapentin and pregabalin are written. Changes nothing."""
from pathlib import Path
import pandas as pd

ASC = Path("data/raw/faers_ascii_2024q1/ASCII")
drug = pd.read_csv(ASC / "DRUG24Q1.txt", sep="$", dtype=str, quoting=3,
                   encoding="latin-1", low_memory=False)
name = drug["drugname"].fillna("").str.upper().str.strip()
ai = drug["prod_ai"].fillna("").str.upper().str.strip()

for word in ["GABAPENTIN", "PREGABALIN"]:
    in_ai = ai.str.contains(word)
    in_name = name.str.contains(word)
    print("\n==", word)
    print("Rows matched by active ingredient:", int(in_ai.sum()))
    print("Rows matched by name only (not ingredient):", int((in_name & ~in_ai).sum()))
    print("Top 12 drug names where ingredient matches:")
    print(name[in_ai].value_counts().head(12).to_string())
    print("Active ingredient spellings:")
    print(ai[in_ai].value_counts().head(6).to_string())