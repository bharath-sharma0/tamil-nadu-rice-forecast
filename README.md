# Tamil Nadu Kharif Rice Yield Forecast

This project aims to forecast district-level Kharif rice yield to support
procurement planning in Tamil Nadu. The current milestone covers data loading
and quality checks.

## Data source

[Directorate of Economics and Statistics APY Query Report](https://data.desagri.gov.in/website/apy-query-report-web)

To reproduce the export, select Tamil Nadu, All Districts, Rice, Kharif,
1998–99 through 2022–23, and All Type. Save the exported file as
`data/raw/apy_query_report.xls`. The export contains an HTML table.

Redistribution terms for this DES query export are still unverified.
The raw file and local SQLite database are excluded from Git.

## Cleaning and coverage

- The source has 950 district-year slots across 38 district names and 25 years.
- The SQL pipeline derives yield in kg/ha as production in tonnes × 1,000
  divided by area in hectares. The original reported yield remains in staging.
- Of the 950 slots, 767 have a derived yield. The 179 blank slots and four
  incomplete slots retain missing yields.
- Chennai in 2020 retains its reported zero production and derived zero yield.
  Its interpretation still needs source verification.
- Ramanathapuram in 2016 has positive production and a reported yield of zero.
  The derived yield uses the source area and production.
- District names match within the export. Historical boundary comparability
  still needs verification.

The SQL files are in `sql/`. Counts from the cleaning audit are in
[`reports/yield_quality_summary.csv`](reports/yield_quality_summary.csv).
