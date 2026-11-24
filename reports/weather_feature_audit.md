# Weather feature audit

- Forecast date: 1 September. Weather observation cutoff: 31 July.
- NASA POWER variables: daily `T2M` (°C) and `PRECTOTCORR` (mm/day).
- Coverage: 38 districts mapped to 33 weather cells, January 1998–July 2022.
- Quality checks: 296,274 daily rows, with no missing readings for either
  variable. All 6,650 January–July district-month aggregates were complete.
- Joined features: 950 district-year rows. Weather cutoff violations:
  0. Yield history cutoff violations: 0.
- The India district boundary release `IND-ADM2-76128533` represents 2021.
  Its metadata lists 736 features. Both downloaded files contained 735.
  All 38 project district names matched distinct boundary IDs after five
  explicit spelling aliases. Historical district boundaries may differ.
- Each district uses the weather cell nearest its representative point.
  The Thanjavur center and point series matched across all 8,978 days.
  Thiruvarur matched the same cell in a seven-day sample.
- Historical NASA records may include later revisions. Historical DES
  publication dates remain unverified. The primary evaluation assumes
  a two-crop-year yield reporting delay and checks a three-year alternative.

Sources: [NASA POWER](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
and [geoBoundaries India ADM2 metadata](https://www.geoboundaries.org/api/current/gbOpen/IND/ADM2/).
