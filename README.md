# NC State Campus Voting

Data and reporting workspace for a Technician follow-up on voting at NC State.

The project is designed to compare campus voting across election years and voting methods, including early voting and Election Day voting. The immediate baseline is the November 8, 2022 general election, when NCSU Talley Student Union was a Wake County early-voting site.

## Main research questions

- How many people used the NC State campus voting site?
- Who used it by age, party registration, race, ethnicity and gender?
- How did campus-site voters differ from Wake County early voters overall?
- In 2026, how does use of the NC State-area early-voting site compare with Talley in 2022?
- Did voting method or location patterns change, including Election Day voting?

## Project structure

- `references.html` — reporting source sheet with direct links and notes
- `methodology.md` — analysis plan and comparison rules
- `scripts/download_2022.py` — downloads the official 2022 NCSBE absentee/early-voting file and creates aggregate outputs
- `data/processed/` — aggregate, publication-safe outputs
- `data/raw/` — intentionally ignored by Git because the official voter-level file can contain personal information

## 2022 source

North Carolina State Board of Elections, November 8, 2022 Absentee by County file:

https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/absentee_county_20221108.zip

NCSBE instructs users to identify early voters by filtering `abs_req_type` to `EARLY VOTING` and `ballot_rtn_status` to `ACCEPTED`.

## Reproducibility

Run:

```bash
python scripts/download_2022.py
```

The script downloads the official NCSBE archive into `data/raw/`, identifies Wake County records, filters accepted early votes and creates aggregate CSV files. Raw voter-level data are not committed to this public repository.
