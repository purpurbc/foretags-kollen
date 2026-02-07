import re
import pandas as pd
from pathlib import Path
from src.utils.helpers import str_to_list


_ORG_DIGITS = re.compile(r"\D+")


def _norm_orgnr(x: str) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    if not s or s.lower() == "nan":
        return ""
    # keep digits only so 556123-4567 == 5561234567 (also removes NBSP etc.)
    return _ORG_DIGITS.sub("", s)


def _has_value(x) -> bool:
    if x is None:
        return False
    s = str(x).strip()
    return s != "" and s.lower() != "nan"


def _emails_to_list(x) -> list[str]:
    """
    Uses your str_to_list, but also handles the common case where the cell is
    quoted twice and literal_eval returns a STRING that looks like a list.
    """
    v = x
    for _ in range(3):  # unwrap a couple of times if needed
        if isinstance(v, list):
            break
        v = str_to_list(v)
        # str_to_list may return [ "<list-as-string>" ] if it parsed a quoted list-string
        if isinstance(v, list) and len(v) == 1 and isinstance(v[0], str):
            inner = v[0].strip()
            if inner.startswith("[") and inner.endswith("]"):
                v = inner
                continue
    return v if isinstance(v, list) else []


def _dedupe_emails(seq: list[str]) -> list[str]:
    seen = set()
    out = []
    for e in seq or []:
        if e is None:
            continue
        s = str(e).strip().strip('"').strip("'")
        if not s:
            continue
        k = s.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(s)
    return out


def merge_contacts_into_main(
    main_csv: str,
    other_csv: str,
    out_csv: str | None = None,
    *,
    key: str = "org_number",
    website_col: str = "website",
    emails_col: str = "emails",
):
    main = pd.read_csv(main_csv, dtype=str)
    other = pd.read_csv(other_csv, dtype=str)

    # Ensure cols exist
    if website_col not in main.columns:
        main[website_col] = ""
    if emails_col not in main.columns:
        main[emails_col] = "[]"
    if website_col not in other.columns:
        other[website_col] = ""
    if emails_col not in other.columns:
        other[emails_col] = "[]"

    # Normalize keys
    main["_k"] = main[key].apply(_norm_orgnr)
    other["_k"] = other[key].apply(_norm_orgnr)

    # Normalize payload columns
    main[website_col] = main[website_col].fillna("").astype(str).str.strip()
    other[website_col] = other[website_col].fillna("").astype(str).str.strip()

    main[emails_col] = main[emails_col].apply(_emails_to_list)
    other[emails_col] = other[emails_col].apply(_emails_to_list)

    # Build lookup from other by key
    other_map: dict[str, dict[str, object]] = {}
    for _, r in other.iterrows():
        k = r["_k"]
        if not k:
            continue

        w = r[website_col]
        e = _dedupe_emails(r[emails_col])

        if k not in other_map:
            other_map[k] = {"website": w, "emails": e}
        else:
            # first non-empty website wins
            if not _has_value(other_map[k]["website"]) and _has_value(w):
                other_map[k]["website"] = w
            # extend emails
            other_map[k]["emails"] = _dedupe_emails(list(other_map[k]["emails"]) + e)

    # Merge into main
    for i, r in main.iterrows():
        k = r["_k"]
        if not k or k not in other_map:
            main.at[i, emails_col] = _dedupe_emails(r[emails_col])
            continue

        src = other_map[k]

        if not _has_value(r[website_col]) and _has_value(src["website"]):
            main.at[i, website_col] = src["website"]

        merged = _dedupe_emails(r[emails_col] + list(src["emails"]))
        main.at[i, emails_col] = merged

    main = main.drop(columns="_k")

    if out_csv:
        Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
        main.to_csv(out_csv, index=False, encoding="utf-8")

    return main


merge_contacts_into_main(
    main_csv="data\details\details_rev-2000-2000000_nump-2000_sort-revenueDesc.csv",
    other_csv="data\old\cccc.csv",
    out_csv="data\out\out.csv",
)
