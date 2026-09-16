# Election Day methodology

## 2022 sources

NCSBE historical voter-history statistics for the November 8, 2022 general election:

`https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/history_stats_20221108.zip`

NCSBE 2022 Election Day polling-place file:

`https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/polling_place_20221108.csv`

The historical voter-history statistics are aggregate counts, not individual voter records. NCSBE documents fields including county, precinct, age range, party, race, ethnicity, sex, total voters and voting method.

## Election Day filter and validation

The 2022 historical statistics file stores `voting_method` as legacy one-character codes. The current NCSBE layout describes the field but does not provide a legend for those legacy values, so this project does **not** guess what each individual letter means.

Instead, the script totals each code statewide and finds the unique combination of codes whose count exactly reproduces NCSBE's published **1,578,545 in-person Election Day voters statewide**. For the archived 2022 file, that validated combination is `A`, `C`, `T`, and `V` together. The individual letters are left unlabeled.

Using that validated grouping, the baseline contains **196,547 Wake County Election Day voters**.

The script then aggregates:

- statewide Election Day total for validation
- Wake County Election Day total
- Wake County totals by precinct
- Wake County demographic distributions

If the statewide total ever fails to match the official NCSBE figure, the script stops rather than silently producing a baseline.

## Polling places

The polling-place file identifies official Election Day locations by county and precinct. The script saves the Wake County rows under the Election Day output folder. The 2022 file contains 208 Wake County polling-place rows.

Election Day polling places are assigned by a voter's residential address. This is different from early voting, where a voter may use any early-voting site in the county.

## Outputs

Stored under `data/processed/election_day/`:

- `2022_election_day_summary.json`
- `2022_wake_election_day_by_precinct.csv`
- `2022_wake_election_day_demographics.csv`
- `2022_wake_polling_places.csv`

The summary JSON records the source URLs, official validation figure, selected legacy-code grouping, statewide method-code totals and validation difference so the filtering decision is auditable later.

## Campus-area precinct rule

Do not automatically call a precinct a "student precinct." If the story later focuses on precincts surrounding NC State, create and document a separate list of included precincts and the geographic reason for including each one.

## 2026 rule

Use the finalized 2026 voter-history statistics for the final Election Day comparison. NCSBE notes that voter history may take multiple weeks after an election to be finalized across all counties.
