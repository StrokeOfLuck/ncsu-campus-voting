# Election Day methodology

## 2022 sources

NCSBE historical voter-history statistics for the November 8, 2022 general election:

`https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/history_stats_20221108.zip`

NCSBE 2022 Election Day polling-place file:

`https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/polling_place_20221108.csv`

The historical voter-history statistics are aggregate counts, not individual voter records. NCSBE documents fields including county, precinct, age range, party, race, ethnicity, sex, total voters and voting method.

## Election Day filter

Filter voter-history statistics to Election Day voting method, then aggregate:

- statewide total for validation
- Wake County total
- Wake County totals by precinct
- Wake County demographic distributions

NCSBE's published 2022 turnout page reports **1,578,545 in-person Election Day voters statewide**. The script checks its statewide aggregation against that number.

## Polling places

The polling-place file identifies official Election Day locations by county and precinct. The script saves the Wake County rows under the Election Day output folder.

Election Day polling places are assigned by a voter's residential address. This is different from early voting, where a voter may use any early-voting site in the county.

## Outputs

Stored under `data/processed/election_day/`:

- `2022_election_day_summary.json`
- `2022_wake_election_day_by_precinct.csv`
- `2022_wake_election_day_demographics.csv`
- `2022_wake_polling_places.csv`

## Campus-area precinct rule

Do not automatically call a precinct a "student precinct." If the story later focuses on precincts surrounding NC State, create and document a separate list of included precincts and the geographic reason for including each one.

## 2026 rule

Use the finalized 2026 voter-history statistics for the final Election Day comparison. NCSBE notes that voter history may take multiple weeks after an election to be finalized across all counties.
