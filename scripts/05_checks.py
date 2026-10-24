"""Stage 5: check the results a second, independent way (all four quarters)."""
import csv
import hashlib
import subprocess
import sys
from pathlib import Path
import pandas as pd

QUARTERS = ["2024q1", "2024q2", "2024q3", "2024q4"]
fails = []


def check(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        fails.append(name)


def rows(prefix):
    """Read one FAERS table from every quarter, one row at a time."""
    for q in QUARTERS:
        yyq = q[2:].upper()
        path = Path(f"data/raw/faers_ascii_{q}/ASCII/{prefix}{yyq}.txt")
        with open(path, encoding="latin-1", newline="") as fh:
            yield from csv.DictReader(fh, delimiter="$", quoting=csv.QUOTE_NONE)


# Second way to clean: plain Python, no pandas
deleted = set()
for q in QUARTERS:
    yyq = q[2:].upper()
    path = Path(f"data/raw/faers_ascii_{q}/Deleted/DELETE{yyq}.txt")
    with open(path, encoding="latin-1") as fh:
        deleted |= {line.strip() for line in fh if line.strip().isdigit()}

latest = {}  # caseid -> (highest version, its primaryid)
for r in rows("DEMO"):
    cid = r["caseid"]
    if cid in deleted:
        continue
    v = int(r["caseversion"])
    if cid not in latest or v > latest[cid][0]:
        latest[cid] = (v, r["primaryid"])
ids = {pid for _, pid in latest.values()}

table = pd.read_csv("data/processed/analysis_table.csv")
sig = pd.read_csv("results/signal_table.csv")
check("one table row per kept case (latest version, not deleted)", len(table) == len(ids))
check("no report ID appears twice", table.primaryid.is_unique)
check("table report IDs are exactly the kept IDs",
      set(table.primaryid.astype(str)) == ids)

g = (table.gabapentin == 1) & (table.pregabalin == 0)
p = (table.pregabalin == 1) & (table.gabapentin == 0)
both = (table.gabapentin == 1) & (table.pregabalin == 1)
neither = (table.gabapentin == 0) & (table.pregabalin == 0)
check("gabapentin + pregabalin + both + neither = all reports",
      g.sum() + p.sum() + both.sum() + neither.sum() == len(table))

gab, pre = set(), set()
for r in rows("DRUG"):
    if r["primaryid"] not in ids or r["role_cod"] not in ("PS", "SS"):
        continue
    ai, nm = r["prod_ai"].upper().strip(), r["drugname"].upper().strip()
    if ai == "GABAPENTIN" or (ai == "" and nm in ("GABAPENTIN", "NEURONTIN")):
        gab.add(r["primaryid"])
    if ai == "PREGABALIN" or (ai == "" and nm in ("PREGABALIN", "LYRICA")):
        pre.add(r["primaryid"])
allrow = sig[(sig.reports == "all") & (sig.comparison == "gabapentin vs neither")].iloc[0]
check("gabapentin-only count matches a second count",
      allrow.a + allrow.b == len(gab - pre))
allrow = sig[(sig.reports == "all") & (sig.comparison == "pregabalin vs neither")].iloc[0]
check("pregabalin-only count matches a second count",
      allrow.a + allrow.b == len(pre - gab))

RESP = {"RESPIRATORY DEPRESSION", "RESPIRATORY FAILURE", "RESPIRATORY ARREST",
        "HYPOVENTILATION", "ACUTE RESPIRATORY FAILURE"}
resp = {r["primaryid"] for r in rows("REAC")
        if r["pt"].upper().strip() in RESP} & ids
check("respiratory report count matches a second count",
      table.resp_dep.sum() == len(resp))

a, b, c, d = 20, 80, 100, 900
check("ROR formula gives 2.25 on a hand example", round(a * d / (b * c), 2) == 2.25)


def digest():
    return hashlib.sha256(Path("results/signal_table.csv").read_bytes()).hexdigest()


before = digest()
for s in ("scripts/03_build_table.py", "scripts/04_signal.py"):
    subprocess.run([sys.executable, s], capture_output=True, check=True)
check("re-running everything gives an identical results file", before == digest())

print("\nALL CHECKS PASS" if not fails else f"\n{len(fails)} CHECK(S) FAILED")
sys.exit(1 if fails else 0)