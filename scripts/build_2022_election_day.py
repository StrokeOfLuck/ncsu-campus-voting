#!/usr/bin/env python3
"""Build the 2022 Wake County Election Day baseline from official NCSBE files.

The historical voter-history statistics file is already aggregate. This script
also downloads the official 2022 polling-place file and keeps only Wake County
polling places for reference. Outputs are kept separate from early voting under
`data/processed/election_day/`.
"""

from __future__ import annotations

import csv
import json
import shutil
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HISTORY_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/history_stats_20221108.zip"
POLLING_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/polling_place_20221108.csv"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "election_day"
PROCESSED = ROOT / "data" / "processed" / "election_day"
HISTORY_ZIP = RAW / "history_stats_20221108.zip"
HISTORY_DIR = RAW / "history_stats_20221108"
POLLING_FILE = RAW / "polling_place_20221108.csv"
NCSBE_STATEWIDE_ELECTION_DAY_TOTAL = 1578545


def norm(value: str | None) -> str:
    return (value or "").strip()


def upper(value: str | None) -> str:
    return norm(value).upper()


def download(url: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"Using existing {path}")
        return
    print(f"Downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "ncsu-campus-voting reporting project"})
    with urllib.request.urlopen(req) as response, path.open("wb") as out:
        shutil.copyfileobj(response, out)
    print(f"Saved {path}")


def extract_history():
    if HISTORY_DIR.exists() and any(HISTORY_DIR.rglob("*")):
        return
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(HISTORY_ZIP) as zf:
        zf.extractall(HISTORY_DIR)


def text_encoding(path: Path) -> str:
    with path.open("rb") as f:
        start = f.read(4)
    if start.startswith(b"\xff\xfe") or start.startswith(b"\xfe\xff"):
        return "utf-16"
    return "utf-8-sig"


def detect_dialect(path: Path):
    encoding = text_encoding(path)
    with path.open("r", encoding=encoding, errors="replace", newline="") as f:
        sample = f.read(32768)
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t|")
    except csv.Error:
        return csv.excel_tab if "\t" in sample else csv.excel


def row_reader(path: Path):
    dialect = detect_dialect(path)
    encoding = text_encoding(path)
    f = path.open("r", encoding=encoding, errors="replace", newline="")
    return f, csv.DictReader(f, dialect=dialect)


def find_col(fields, *choices):
    lookup = {str(f).strip().lower(): f for f in (fields or [])}
    for choice in choices:
        if choice.lower() in lookup:
            return lookup[choice.lower()]
    return None


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def locate_history_file() -> Path:
    candidates = [p for p in HISTORY_DIR.rglob("*") if p.is_file() and p.suffix.lower() in {".txt", ".csv"}]
    if not candidates:
        raise RuntimeError("No text/CSV history file found in the NCSBE archive.")
    for path in candidates:
        try:
            f, reader = row_reader(path)
            with f:
                fields = {str(x).strip().lower() for x in (reader.fieldnames or [])}
            if {"county_desc", "precinct_abbrv", "total_voters", "voting_method"}.issubset(fields):
                return path
        except Exception:
            pass
    raise RuntimeError("Could not identify the NCSBE history statistics file.")


def detect_election_day_method(history_file: Path):
    """Identify the historical-file method code by matching NCSBE's published total.

    The old history-stats file uses one-character method codes rather than the
    current descriptive labels. Instead of guessing a code, match each method's
    statewide voter total to NCSBE's published 2022 Election Day total.
    """
    f, reader = row_reader(history_file)
    fields = reader.fieldnames or []
    method_col = find_col(fields, "voting_method")
    total_col = find_col(fields, "total_voters")
    if not method_col or not total_col:
        raise RuntimeError(f"Missing voting_method/total_voters fields. Found: {fields}")

    method_totals = Counter()
    with f:
        for row in reader:
            try:
                count = int(float(norm(row.get(total_col)) or 0))
            except ValueError:
                continue
            method_totals[norm(row.get(method_col)) or "Unknown"] += count

    matches = [method for method, total in method_totals.items() if total == NCSBE_STATEWIDE_ELECTION_DAY_TOTAL]
    if len(matches) != 1:
        raise RuntimeError(
            "Could not uniquely identify the Election Day method code by NCSBE's published total. "
            f"Method totals: {dict(method_totals)}"
        )
    return matches[0], dict(method_totals)


def build_history_outputs(history_file: Path, election_day_method: str):
    f, reader = row_reader(history_file)
    fields = reader.fieldnames or []

    county_col = find_col(fields, "county_desc")
    precinct_col = find_col(fields, "precinct_abbrv", "precinct_desc", "precinct")
    age_col = find_col(fields, "age")
    party_col = find_col(fields, "party_cd")
    race_col = find_col(fields, "race_code", "race")
    ethnic_col = find_col(fields, "ethnic_code", "ethnicity")
    sex_col = find_col(fields, "sex_code", "gender")
    total_col = find_col(fields, "total_voters")
    method_col = find_col(fields, "voting_method")

    required = [county_col, precinct_col, total_col, method_col]
    if any(col is None for col in required):
        raise RuntimeError(f"Missing expected history columns. Found: {fields}")

    statewide_total = 0
    wake_total = 0
    precinct_counts = Counter()
    dimension_counts = defaultdict(Counter)

    with f:
        for row in reader:
            if norm(row.get(method_col)) != election_day_method:
                continue
            try:
                count = int(float(norm(row.get(total_col)) or 0))
            except ValueError:
                continue

            statewide_total += count
            if upper(row.get(county_col)) != "WAKE":
                continue

            wake_total += count
            precinct = norm(row.get(precinct_col)) or "Unknown"
            precinct_counts[precinct] += count

            for dimension, col in (
                ("age", age_col),
                ("party", party_col),
                ("race", race_col),
                ("ethnicity", ethnic_col),
                ("sex", sex_col),
            ):
                if col:
                    dimension_counts[dimension][norm(row.get(col)) or "Unknown"] += count

    write_csv(
        PROCESSED / "2022_wake_election_day_by_precinct.csv",
        ["precinct", "election_day_voters"],
        [{"precinct": precinct, "election_day_voters": count} for precinct, count in precinct_counts.most_common()],
    )

    demo_rows = []
    for dimension, counts in dimension_counts.items():
        for value, count in counts.most_common():
            demo_rows.append({
                "dimension": dimension,
                "value": value,
                "count": count,
                "percent": round((count / wake_total * 100), 3) if wake_total else 0,
            })
    write_csv(
        PROCESSED / "2022_wake_election_day_demographics.csv",
        ["dimension", "value", "count", "percent"],
        demo_rows,
    )

    return statewide_total, wake_total


def build_polling_place_output():
    f, reader = row_reader(POLLING_FILE)
    fields = reader.fieldnames or []
    county_col = find_col(fields, "county_desc", "county_name", "county")
    if not county_col:
        raise RuntimeError(f"Could not find county field in polling-place file. Found: {fields}")

    wake_rows = []
    with f:
        for row in reader:
            if upper(row.get(county_col)) == "WAKE":
                wake_rows.append({field: norm(row.get(field)) for field in fields})

    if not wake_rows:
        raise RuntimeError("No Wake County polling places found in the 2022 polling-place file.")
    write_csv(PROCESSED / "2022_wake_polling_places.csv", fields, wake_rows)
    return len(wake_rows)


def main():
    download(HISTORY_URL, HISTORY_ZIP)
    extract_history()
    download(POLLING_URL, POLLING_FILE)

    history_file = locate_history_file()
    print(f"History source: {history_file}")
    election_day_method, method_totals = detect_election_day_method(history_file)
    print(f"Election Day voting_method code identified by official total: {election_day_method}")

    statewide_total, wake_total = build_history_outputs(history_file, election_day_method)
    summary = {
        "statewide_election_day_voters_from_history_stats": statewide_total,
        "ncsbe_published_statewide_election_day_voters": NCSBE_STATEWIDE_ELECTION_DAY_TOTAL,
        "statewide_validation_difference": statewide_total - NCSBE_STATEWIDE_ELECTION_DAY_TOTAL,
        "wake_election_day_voters": wake_total,
        "selected_election_day_method_code": election_day_method,
        "statewide_voters_by_history_method_code": method_totals,
        "history_source_url": HISTORY_URL,
        "polling_place_source_url": POLLING_URL,
        "wake_polling_place_rows": build_polling_place_output(),
        "raw_data_committed": False,
    }

    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "2022_election_day_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

    if summary["statewide_validation_difference"] != 0:
        raise RuntimeError("Election Day validation failed against NCSBE's published statewide total.")


if __name__ == "__main__":
    main()
