"""
Reproducible analysis for the July-September 2026 student job-board applications.
Run: python analysis.py job-board-applications.csv
Requires: pandas, matplotlib.
Outputs are written to the same directory as the input CSV.
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("job-board-applications.csv")
out = input_path.resolve().parent
df = pd.read_csv(input_path)

df["applied_on"] = pd.to_datetime(df["applied_on"], errors="coerce")
for col in ["role_category", "work_mode", "source", "shortlisted", "interviewed", "hired"]:
    df[col] = df[col].astype("string").str.strip()
df["work_mode"] = df["work_mode"].str.lower().replace({"on-site": "on_site", "onsite": "on_site"})
for col in ["shortlisted", "interviewed", "hired"]:
    df[col] = df[col].str.lower()
df["source"] = df["source"].replace({"": pd.NA, "nan": pd.NA})

duplicates = df[df["application_id"].duplicated(keep=False)]
if not duplicates.empty:
    variation = duplicates.groupby("application_id", dropna=False).nunique(dropna=False).max(axis=1)
    if (variation > 1).any():
        raise ValueError("Conflicting duplicate application IDs: inspect before deduplicating.")
clean = df.drop_duplicates("application_id", keep="first").copy()
clean.to_csv(out / "cleaned_applications.csv", index=False)

source = clean.groupby("source", dropna=False).agg(
    applications=("application_id", "size"),
    hires=("hired", lambda x: (x == "yes").sum())
)
source["hires_per_100"] = source["hires"] / source["applications"] * 100
source.reset_index().to_csv(out / "source_hire_rates.csv", index=False)

role = clean[clean.source.notna()].groupby(["role_category", "source"]).agg(
    applications=("application_id", "size"),
    hires=("hired", lambda x: (x == "yes").sum())
).reset_index()
role["hires_per_100"] = role.hires / role.applications * 100
role.to_csv(out / "role_source_hire_rates.csv", index=False)

steps = clean.assign(all_four=clean.steps_done.eq(4)).groupby("all_four").agg(
    applications=("application_id", "size"),
    shortlisted=("shortlisted", lambda x: (x == "yes").sum())
)
steps["shortlist_rate_pct"] = steps.shortlisted / steps.applications * 100
steps.reset_index().to_csv(out / "step_completion_shortlisting.csv", index=False)

paid = clean.assign(paid=clean.stipend_inr_month.gt(0)).groupby("paid").agg(
    applications=("application_id", "size"),
    no_reply=("days_to_first_reply", lambda x: x.isna().sum()),
    median_reply_days=("days_to_first_reply", "median"),
    mean_reply_days=("days_to_first_reply", "mean"),
    replied=("days_to_first_reply", lambda x: x.notna().sum())
)
paid["never_heard_back_pct"] = paid.no_reply / paid.applications * 100
paid.reset_index().to_csv(out / "paid_vs_unpaid_response.csv", index=False)

known = source[source.index.notna()].sort_values("hires_per_100")
fig, ax = plt.subplots(figsize=(8.5, 5.2))
bars = ax.barh(known.index.astype(str), known.hires_per_100)
ax.set(title="Hires per 100 applications by acquisition source",
       xlabel="Hires per 100 applications", ylabel="Application source")
ax.grid(axis="x", alpha=.25)
ax.set_axisbelow(True)
for bar, value in zip(bars, known.hires_per_100):
    ax.text(value + .12, bar.get_y() + bar.get_height()/2, f"{value:.1f}", va="center")
ax.set_xlim(0, max(known.hires_per_100) * 1.25)
fig.tight_layout()
fig.savefig(out / "hire_rate_by_source.png", dpi=180)
print("Analysis complete. See CSV result tables and hire_rate_by_source.png.")
