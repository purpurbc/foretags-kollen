import pandas as pd
from pathlib import Path


def diff_csv_by_orgnr(
        left_csv: str,
        right_csv: str,
        out_csv: str | None = None,
    ):
    left  = pd.read_csv(left_csv, dtype=str)
    right = pd.read_csv(right_csv, dtype=str)

    # Normalize org_number
    left["_org"]  = left["org_number"].str.strip()
    right_orgs = set(right["org_number"].str.strip())

    # Rows in left but not in right
    diff = left[~left["_org"].isin(right_orgs)].drop(columns="_org")

    if out_csv:
        Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
        diff.to_csv(out_csv, index=False)

    return diff["org_number"]

print(diff_csv_by_orgnr("data\old\cccc.csv", "data\details\details_rev-2000-2000000_nump-2000_sort-revenueDesc.csv"))