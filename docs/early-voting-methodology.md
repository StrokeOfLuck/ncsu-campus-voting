# Early-voting methodology

## 2022 source

North Carolina State Board of Elections, November 8, 2022 Absentee by County archive:

`https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/absentee_county_20221108.zip`

NCSBE treats one-stop early voting as absentee data for reporting purposes. The 2022 file uses legacy labels in some fields, so the script accepts both `EARLY VOTING` and one-stop variants and requires `ballot_rtn_status = ACCEPTED`.

## Site filter

For the NC State baseline, filter the accepted Wake County early-voting rows to the Talley / NCSU Student Center site name.

Wake County's published historical site report gives **10,390 ballots** at NCSU Talley Student Union for the 2022 general election. The script uses that figure as a validation check.

## Outputs

Stored under `data/processed/early_voting/`:

- `2022_summary.json`
- `2022_wake_early_voting_by_site.csv`
- `2022_talley_daily.csv`
- `2022_talley_by_precinct.csv`
- `2022_talley_demographics.csv`

The demographic file contains aggregate counts and percentages for age, party registration, race, ethnicity and gender fields available in the NCSBE source.

## Privacy

The source file can contain voter-level personal information. Raw files are downloaded into ignored `data/raw/early_voting/` storage and are not committed to this public repository.

## 2026 rule

Build the 2026 site data using the same filters and output structure before comparing years. Validate the 2026 site total against an official Wake County or NCSBE published total when available.
