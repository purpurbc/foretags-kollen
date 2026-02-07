#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import ast
import re
from pathlib import Path

INPUT_FILE = "cccc.csv"             # <-- change if needed
UNIQUE_OUT = "sni_codes_unique.csv"  # code, description (deduped)
MAP_OUT    = "company_sni.csv"       # org_number, legal_name, code, description

# Regex fallback to capture entries like "24100 Framställning av ..." inside the list text
SNI_ITEM_RE = re.compile(r"(\d{5})\s+([^\]]+?)(?=(?:',|\",|\])|$)")

def parse_sni_list(cell):
    """
    Parse a cell that should contain something like:
      "['24100 Text', '24310 Text']"
    Returns a list of strings like "24100 Text".
    """
    if cell is None:
        return []
    s = str(cell).strip()
    if not s or s.lower() == "nan":
        return []

    # Some CSVs may double-quote the whole list; others not.
    # 1) Try a safe literal_eval first.
    try:
        val = ast.literal_eval(s)
        if isinstance(val, (list, tuple)):
            # Ensure each item is a flat string
            items = []
            for it in val:
                if it is None:
                    continue
                items.append(str(it))
            return items
    except Exception:
        pass

    # 2) Fallback: try to extract via regex "##### description"
    #    First, drop leading/trailing brackets if present
    s2 = s.strip()
    if s2.startswith("[") and s2.endswith("]"):
        s2 = s2[1:-1]

    # Normalize quotes to help the lookahead in regex
    s2 = s2.replace("’", "'").replace("”", '"').replace("“", '"')

    items = []
    for m in SNI_ITEM_RE.finditer(s2):
        code = m.group(1)
        desc = m.group(2).strip().strip("'").strip('"').strip()
        items.append(f"{code} {desc}")
    return items

def split_code_desc(text):
    """
    Split "24100 Framställning av järn ..." → ("24100", "Framställning av järn ...")
    """
    text = text.strip()
    m = re.match(r"^(\d{5})\s+(.*)$", text)
    if m:
        return m.group(1), m.group(2).strip()
    return None, text  # fallback; shouldn't happen if upstream parsed correctly

def main():
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {INPUT_FILE}")

    # Collect unique SNI pairs and mapping rows
    unique_pairs = set()  # (code, desc)
    mapping_rows = []     # dicts with org_number, legal_name, code, desc

    with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        # Expect column names as provided by you. We only require:
        # - 'sni_codes'
        # - 'org_number'
        # - 'legal_name'
        # If the header differs slightly, adjust here.
        for row in reader:
            sni_raw = row.get("sni_codes")
            org_number = (row.get("org_number") or "").strip()
            legal_name = (row.get("legal_name") or "").strip()

            items = parse_sni_list(sni_raw)
            if not items:
                continue

            for item in items:
                code, desc = split_code_desc(item)
                if not code or not desc:
                    continue
                pair = (code, desc)
                if pair not in unique_pairs:
                    unique_pairs.add(pair)
                # Add mapping (no dedup within same company+code unless you want to)
                mapping_rows.append({
                    "org_number": org_number,
                    "legal_name": legal_name,
                    "sni_code": code,
                    "sni_description": desc
                })

    # Write unique SNI list
    with open(UNIQUE_OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sni_code", "sni_description"])
        for code, desc in sorted(unique_pairs, key=lambda x: (x[0], x[1])):
            w.writerow([code, desc])

    # Write company → SNI mapping
    with open(MAP_OUT, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["org_number", "legal_name", "sni_code", "sni_description"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        # Optional: dedup rows at (org_number, sni_code) level to avoid repeats per company
        seen_map = set()
        for r in mapping_rows:
            key = (r["org_number"], r["sni_code"])
            if key in seen_map:
                continue
            seen_map.add(key)
            w.writerow(r)

    print(f"✅ Wrote {len(unique_pairs)} unique SNI codes to {UNIQUE_OUT}")
    print(f"✅ Wrote company→SNI mapping to {MAP_OUT}")

if __name__ == "__main__":
    main()
