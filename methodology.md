# Methodology notes

## Baseline election

Use the November 8, 2022 general election as the primary historical baseline for a 2026 midterm comparison.

Talley Student Union served as a Wake County one-stop early-voting site in 2022. Wake County reports 10,390 ballots cast at the NCSU Talley Student Union early-voting site in that election.

## Early-voting records

Primary source: North Carolina State Board of Elections `Absentee by County` file for the November 8, 2022 election.

NCSBE's published instructions for early-voting lists are:

1. Download the Absentee by County ZIP.
2. Filter `abs_req_type` to `EARLY VOTING`.
3. Filter `ballot_rtn_status` to `ACCEPTED`.

For site-specific analysis, additionally filter `site_name` for the Talley/NC State early-voting location.

## Measures to build

For Talley and Wake County overall:

- total accepted early votes
- daily ballots cast
- age distribution
- voter party registration
- race
- ethnicity
- gender
- precinct of registration
- same-day registration count, when available

For publication, use aggregate counts and percentages rather than publishing voter names, addresses, NCIDs or other voter-level identifiers.

## 2026 comparison

The primary comparison should be 2022 general election versus 2026 general election because both are non-presidential federal general elections. Any 2024 presidential-election comparison should be clearly labeled as contextual rather than treated as a like-for-like turnout comparison.

Useful denominators include:

- campus-site ballots
- all Wake County early votes
- campus-site share of Wake early voting
- age-group share within each site
- voting-method share when Election Day data are added

## Election Day

Election Day voting is precinct-based rather than countywide site choice. Use NCSBE historical polling-place data and voter-history data to identify voting method and precinct-level participation. Do not assume all voters in an NC State-area precinct are students.

## Reproducibility

Keep official source URLs and scripts in Git. Do not commit raw voter-level files to this public repository. Save aggregate outputs sufficient to reproduce published charts and reported figures.
