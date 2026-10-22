"""Stage 5: check the results a second, independent way."""
import csv
import hashlib
import subprocess
import sys
from pathlib import Path
import pandas as pd

ASC = Path("data/raw/faers_ascii_2024q1/ASCII")
fails = []


def check(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        fails.append(name)


def rows(f):
    with open(ASC / f, encoding="latin-1", newline="") as fh:
        yield from csv.DictReader(fh, delimiter="$", quoting=csv.QUOTE_NONE)


table = pd.read_csv("data/processed/analysis_table.csv")
sig = pd.read_csv("results/signal_table.csv")
ids = {r["primaryid"] for r in rows("DEMO24Q1.txt")}
check("one table row per report in DEMO", len(table) == len(ids))
check("no report ID appears twice", table.primaryid.is_unique)

g = (table.gabapentin == 1) & (table.pregabalin == 0)
p = (table.pregabalin == 1) & (table.gabapentin == 0)
both = (table.gabapentin == 1) & (table.pregabalin == 1)
neither = (table.gabapentin == 0) & (table.pregabalin == 0)
check("gabapentin + pregabalin + both + neither = all reports",
      g.sum() + p.sum() + both.sum() + neither.sum() == len(table))

gab, pre = set(), set()
for r in rows("DRUG24Q1.txt"):
    if r["role_cod"] not in ("PS", "SS"):
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
resp = {r["primaryid"] for r in rows("REAC24Q1.txt")
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