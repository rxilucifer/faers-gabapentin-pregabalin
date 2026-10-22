"""Stage 4: compare reporting of respiratory depression (PRR and ROR)."""
from math import exp, log, sqrt
from pathlib import Path
import pandas as pd

t = pd.read_csv("data/processed/analysis_table.csv")
t = t[~((t.gabapentin == 1) & (t.pregabalin == 1))]  # drop reports with both


def stats(exposed, outcome):
    a = int((exposed & outcome).sum())
    b = int((exposed & ~outcome).sum())
    c = int((~exposed & outcome).sum())
    d = int((~exposed & ~outcome).sum())
    if min(a, b, c, d) == 0:
        return dict(a=a, b=b, c=c, d=d, PRR=None, ROR=None, low=None, high=None)
    ror = (a * d) / (b * c)
    se = sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    prr = (a / (a + b)) / (c / (c + d))
    return dict(a=a, b=b, c=c, d=d, PRR=round(prr, 2), ROR=round(ror, 2),
                low=round(exp(log(ror) - 1.96 * se), 2),
                high=round(exp(log(ror) + 1.96 * se), 2))


rows = []
groups = {"all": t.opioid >= 0, "opioid": t.opioid == 1, "no opioid": t.opioid == 0}
for gname, g in groups.items():
    s = t[g]
    out = s.resp_dep == 1
    gab, pre = s.gabapentin == 1, s.pregabalin == 1
    neither = ~gab & ~pre
    for label, sub, exp_ in [
        ("gabapentin vs neither", gab | neither, gab),
        ("pregabalin vs neither", pre | neither, pre),
        ("gabapentin vs pregabalin", gab | pre, gab),
    ]:
        r = stats(exp_[sub], out[sub])
        rows.append(dict(reports=gname, comparison=label, **r))

res = pd.DataFrame(rows)
Path("results").mkdir(exist_ok=True)
res.to_csv("results/signal_table.csv", index=False)
print(res.to_string(index=False))