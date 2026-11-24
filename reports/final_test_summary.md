# Final test results

Crop years 2020–21 through 2022–23. Error metrics use the 93 observed district-years where all five methods issued forecasts.

| Method | Forecasts / observed | MAE (kg/ha) | Exploratory 95% MAE CI | RMSE (kg/ha) | MAPE (positive actuals) |
|---|---:|---:|---:|---:|---:|
| Last available | 100/113 | 482.10 | 355.15–551.15 | 653.53 | 15.62% (n=93) |
| Trailing average | 93/113 | 483.91 | 425.20–525.77 | 621.78 | 15.02% (n=93) |
| Exponential smoothing | 93/113 | 409.77 | 375.43–432.56 | 500.36 | 12.33% (n=93) |
| LightGBM history only | 113/113 | 397.19 | 337.78–446.84 | 497.86 | 12.68% (n=93) |
| LightGBM history + weather | 113/113 | 357.46 | 330.68–376.30 | 437.19 | 10.93% (n=93) |

The frozen model was **Trailing average**. **LightGBM history + weather** had the lowest MAE on this test. The test ranking was reported after model selection.

The selected model's nominal 90% prediction interval covered **91/93 (97.8%)** of its observed forecasts. Both misses were above the upper bound in 2020–21, in Ramanathapuram and Sivaganga.

The selected model issued forecasts for only 6 of 26 observed district-years in the limited-history group. The MAE intervals resample just three test years and should be interpreted cautiously. Exponential smoothing emitted two convergence warnings during test fitting.

See [district-group metrics](final_test_metrics.csv) and [interval coverage counts](final_test_interval_coverage.csv).
