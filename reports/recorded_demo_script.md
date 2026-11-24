# Recorded dashboard demo

Before recording, open the local dashboard and select Chengalpattu, 2020–21.
Keep this district selected for the entire recording.

| Time | On screen | What to say |
|---|---|---|
| 0–15 sec | District and crop-year selectors | I built a SQL-backed system that forecasts district-level Kharif rice yield for procurement planning in Tamil Nadu. Each historical forecast is issued on 1 September. |
| 15–30 sec | Insufficient-history message | The selected model averages three consecutive eligible seasons. Here, history is incomplete, so the dashboard asks the procurement officer to obtain a current district estimate before setting a volume target. |
| 30–50 sec | Held-out model comparison | I selected the trailing average on earlier years. On 93 shared test rows it scored 483.91 kilograms per hectare MAE. LightGBM with weather scored 357.46 on those same rows. I reported the reversal and kept the original model selection. |
| 50–60 sec | Coverage column and confidence intervals | I report forecast coverage separately from error. The trailing average forecast 93 of 113 observed test outcomes. Confidence intervals are exploratory because the test covers only three years. |

## Screenshot checklist

1. Capture the insufficient-history message and procurement action.
2. Scroll down and capture the five-model comparison, including the coverage column.
