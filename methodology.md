# Methodology index

This project keeps early voting and Election Day analysis separate because they use different data and different rules.

## Baseline

Use the **November 8, 2022 general election** as the historical baseline for the **November 3, 2026 general election**.

The project intentionally skips 2024 for the main comparison so the reporting stays focused on two midterm general elections.

## Early voting

See [`docs/early-voting-methodology.md`](docs/early-voting-methodology.md).

Early voting is site-choice data: eligible voters may use any early-voting site in their county. The 2022 NC State baseline is Talley Student Union, where Wake County reports 10,390 ballots cast during early voting.

Processed data live in:

`data/processed/early_voting/`

## Election Day

See [`docs/election-day-methodology.md`](docs/election-day-methodology.md).

Election Day is precinct-assigned voting based on residential address. The analysis uses NCSBE historical voter-history statistics plus the official polling-place file.

Processed data live in:

`data/processed/election_day/`

## Story plan

See [`docs/story-plan.md`](docs/story-plan.md) for the exact 2022-to-2026 comparison plan, November workflow and possible graphics.

## Publication and privacy

Keep official source URLs and reproducible scripts in Git. Raw voter-level files belong in ignored `data/raw/` storage. Publish aggregate counts and percentages rather than names, addresses, NCIDs or other voter-level identifiers.
