#!/usr/bin/env python3
"""Build the 2022 NC State / Wake County early-voting baseline.

Downloads the official NCSBE absentee-by-county archive into ignored local raw
storage and commits only aggregate, publication-safe outputs under
`data/processed/early_voting/`.
"""

from __future__ import annotations

import csv
import json
import shutil
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

URL = "https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/absentee_county_20221108.zip"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "early_voting"
PROCESSED = ROOT / "data" / "processed" / "early_voting"
ZIP_PATH = RAW / "absentee_county_20221108.zip"
EXTRACTED = RAW / "absentee_county_20221108"
PUBLISHED_TALLEY_TOTAL = 10390


def norm(value: str | None) -> str:
    return (value or "").strip()


def upper(value: str | None) -> str:
    return norm(value).upper()


def detect_dialect(path: Path):
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        sample = f.read(32768)
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t|")
    except csv.Error:
        return csv.excel_tab if "\t" in sample else csv.excel


def row_reader(path: Path):
    dialect = detect_dialect(path)
    f = path.open("r", encoding="utf-8-sig", errors="replace", newline="")
    return f, csv.DictReader(f, dialect=dialect)


def find_col(fields, *choices):
    lookup = {str(f).strip().lower(): f for f in (fields or [])}
    for choice in choices:
        if choice.lower() in lookup:
            return lookup[choice.lower()]
    return None


def looks_like_wake(path: Path) -> bool:
    try:
        f, reader = row_reader(path)
        with f:
            county_col = find_col(reader.fieldnames, "county_desc", "county")
            if not county_col:
                return False
            for i, row in enumerate(reader):
                if upper(row.get(county_col)) == "WAKE":
                    return True
                if i >= 500:
                    break
    except Exception:
        return False
    return False


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


def extract():
    if EXTRACTED.exists() and any(EXTRACTED.rglob("*")):
        return
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        zf.extractall(EXTRACTED)


def locate_wake_file() -> Path:
    candidates = [p for p in EXTRACTED.rglob("*") if p.is_file() and p.suffix.lower() in {".csv", ".txt"}]
    name_hits = [p for p in candidates if "wake" in p.name.lower()]
    for path in name_hits + candidates:
        if looks_like_wake(path):
            return path
    raise RuntimeError("Could not identify the Wake County absentee file inside the archive.")


def clean_age(value: str) -> str:
    value = norm(value)
    try:
        return str(int(float(value)))
    except (ValueError, TypeError):
        return value or "Unknown"


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    download(URL, ZIP_PATH)
    extract()
    wake_file = locate_wake_file()
    print(f"Wake County source: {wake_file}")

    f, reader = row_reader(wake_file)
    fields = reader.fieldnames or []

    county_col = find_col(fields, "county_desc", "county")
    req_col = find_col(fields, "abs_req_type", "ballot_req_type")
    status_col = find_col(fields, "ballot_rtn_status")
    site_col = find_col(fields, "site_name")
    date_col = find_col(fields, "ballot_rtn_dt")
    party_col = find_col(fields, "voter_party_code", "party_cd")
    race_col = find_col(fields, "race")
    ethnicity_col = find_col(fields, "ethnicity")
    gender_col = find_col(fields, "gender")
    age_col = find_col(fields, "age")
    precinct_col = find_col(fields, "precinct_desc", "precinct_abbrv", "precinct")
    sdr_col = find_col(fields, "sdr")

    required = {"early-voting type": req_col, "return status": status_col, "site name": site_col}
    missing = [label for label, col in required.items() if not col]
    if missing:
        raise RuntimeError(f"Missing expected columns: {', '.join(missing)}. Found: {fields}")

    site_counts = Counter()
    daily_counts = Counter()
    precinct_counts = Counter()
    dimension_counts = defaultdict(Counter)
    talley_total = 0
    wake_early_total = 0
    talley_sdr = 0

    with f:
        for row in reader:
            if county_col and upper(row.get(county_col)) != "WAKE":
                continue

            request_type = upper(row.get(req_col))
            if request_type not in {"EARLY VOTING", "ONE-STOP", "ONE STOP"} and "EARLY" not in request_type and "ONE-STOP" not in request_type:
                continue
            if upper(row.get(status_col)) != "ACCEPTED":
                continue

            wake_early_total += 1
            site = norm(row.get(site_col)) or "Unknown"
            site_counts[site] += 1

            is_talley = "TALLEY" in site.upper() or ("NCSU" in site.upper() and "STUDENT" in site.upper())
            if not is_talley:
                continue

            talley_total += 1
            if date_col:
                daily_counts[norm(row.get(date_col)) or "Unknown"] += 1
            if precinct_col:
                precinct_counts[norm(row.get(precinct_col)) or "Unknown"] += 1
            if party_col:
                dimension_counts["party"][norm(row.get(party_col)) or "Unknown"] += 1
            if race_col:
                dimension_counts["race"][norm(row.get(race_col)) or "Unknown"] += 1
            if ethnicity_col:
                dimension_counts["ethnicity"][norm(row.get(ethnicity_col)) or "Unknown"] += 1
            if gender_col:
                dimension_counts["gender"][norm(row.get(gender_col)) or "Unknown"] += 1
            if age_col:
                dimension_counts["age"][clean_age(row.get(age_col))] += 1
            if sdr_col and upper(row.get(sdr_col)) in {"Y", "YES"}:
                talley_sdr += 1

    write_csv(
        PROCESSED / "2022_wake_early_voting_by_site.csv",
        ["site_name", "accepted_early_votes"],
        [{"site_name": site, "accepted_early_votes": count} for site, count in site_counts.most_common()],
    )
    write_csv(
        PROCESSED / "2022_talley_daily.csv",
        ["date", "accepted_early_votes"],
        [{"date": date, "accepted_early_votes": count} for date, count in sorted(daily_counts.items())],
    )
    write_csv(
        PROCESSED / "2022_talley_by_precinct.csv",
        ["precinct", "accepted_early_votes"],
        [{"precinct": precinct, "accepted_early_votes": count} for precinct, count in precinct_counts.most_common()],
    )

    demo_rows = []
    for dimension, counts in dimension_counts.items():
        for value, count in counts.most_common():
            demo_rows.append({
                "dimension": dimension,
                "value": value,
                "count": count,
                "percent": round((count / talley_total * 100), 3) if talley_total else 0,
            })
    write_csv(PROCESSED / "2022_talley_demographics.csv", ["dimension", "value", "count", "percent"], demo_rows)

    summary = {
        "election": "2022-11-08 General Election",
        "source_url": URL,
        "wake_accepted_early_votes_from_file": wake_early_total,
        "talley_accepted_early_votes_from_file": talley_total,
        "talley_same_day_registration_records": talley_sdr if sdr_col else None,
        "wake_county_published_talley_total": PUBLISHED_TALLEY_TOTAL,
        "validation_difference": talley_total - PUBLISHED_TALLEY_TOTAL,
        "raw_data_committed": False,
    }
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "2022_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    if talley_total != PUBLISHED_TALLEY_TOTAL:
        print("WARNING: Talley total does not match Wake County's published 10,390.")


if __name__ == "__main__":
    main()
