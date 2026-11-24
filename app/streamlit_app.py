import csv
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "processed" / "rice_forecast.sqlite"
PLAN = ROOT / "reports" / "frozen_evaluation_plan.json"
HISTORY_SQL = ROOT / "sql" / "23_dashboard_eligible_history.sql"

st.set_page_config(page_title="Kharif Rice Yield Forecast", layout="wide")
st.title("Tamil Nadu Kharif Rice Yield")
st.caption("Historical procurement scenarios · Forecast issued 1 September")

if not DATABASE.is_file():
    st.error("The local SQLite database is missing. Build the data pipeline first.")
    st.stop()

plan = json.loads(PLAN.read_text(encoding="utf-8"))
districts = sorted(plan["district_groups"])

picker, year_picker = st.columns(2)
district = picker.selectbox("District", districts, index=districts.index("Ramanathapuram"))
year = year_picker.selectbox(
    "Crop year", plan["final_test_years"],
    format_func=lambda value: f"{value}–{str(value + 1)[-2:]}",
)

with closing(sqlite3.connect(DATABASE.as_uri() + "?mode=ro", uri=True)) as conn:
    drivers = conn.execute(
        HISTORY_SQL.read_text(encoding="utf-8"),
        {"district": district, "forecast_year": year},
    ).fetchall()

if len(drivers) != 3 or any(value is None for _, value in drivers):
    st.warning("Insufficient history for a forecast. Three consecutive eligible yields are required.")
    st.write("Procurement action: request a current district estimate before setting a volume target.")
else:
    forecast = mean(value for _, value in drivers)
    half_width = plan["prediction_interval"]["half_width_kg_per_ha"]
    lower, upper = max(0, forecast - half_width), forecast + half_width

    st.metric("Forecast yield", f"{forecast:,.2f} kg/ha")
    st.markdown(f"**Nominal 90% prediction range** · {lower:,.2f}–{upper:,.2f} kg/ha")

    with closing(sqlite3.connect(DATABASE.as_uri() + "?mode=ro", uri=True)) as conn:
        chart_rows = conn.execute(
            """
            SELECT y.crop_year_start, y.yield_kg_per_ha
            FROM fact_kharif_rice_yield AS y
            JOIN dim_district AS d USING (district_id)
            WHERE d.district_name = ?
              AND (y.crop_year_start BETWEEN ? AND ? OR y.crop_year_start = ?)
            ORDER BY y.crop_year_start
            """,
            (district, year - 12, year - 2, year),
        ).fetchall()

    history = [(source_year, float("nan") if value is None else value)
               for source_year, value in chart_rows if source_year <= year - 2]
    actual = next((value for source_year, value in chart_rows if source_year == year), None)

    fig, ax = plt.subplots(figsize=(8, 3.2), layout="constrained")
    ax.plot(*zip(*history), marker="o", color="#16705A", label="Eligible history")
    ax.errorbar(
        year, forecast, yerr=[[forecast - lower], [upper - forecast]],
        fmt="D", capsize=6, color="#365CC0", label="Forecast and interval",
    )
    if actual is not None:
        ax.scatter(year, actual, marker="x", s=65, color="#B65347", label="Observed later")
    ax.set(xlabel="Crop-year start", ylabel="Yield (kg/ha)")
    ax.set_xticks(range(year - 12, year + 1, 2))
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Seasons behind the forecast")
    st.table([
        {"Crop year": f"{source_year}–{str(source_year + 1)[-2:]}",
         "Yield (kg/ha)": round(value, 2)}
        for source_year, value in drivers
    ])
    st.write("Procurement action: use the range for scenario planning and confirm local supply before committing to volumes.")


def show_test_comparison():
    st.subheader("Held-out model comparison")
    st.caption("2020–21 to 2022–23 · Errors use the same 93 observed forecasts for all five methods.")

    results_path = ROOT / "reports" / "final_test_metrics.csv"
    with results_path.open(encoding="utf-8", newline="") as source:
        results = [row for row in csv.DictReader(source) if row["group"] == "Overall"]

    table = []
    for row in sorted(results, key=lambda item: float(item["mae_kg_per_ha"])):
        method = row["method"]
        if method == plan["selected_method"]:
            method += " (selected before test)"
        table.append({
            "Method": method,
            "MAE (kg/ha)": f"{float(row['mae_kg_per_ha']):.2f}",
            "Exploratory 95% MAE CI": (
                f"{float(row['mae_ci_95_lower']):.2f}–"
                f"{float(row['mae_ci_95_upper']):.2f}"
            ),
            "Observed rows forecast": f"{row['forecast_rows']}/{row['observed_rows']}",
        })
    st.dataframe(table, hide_index=True)


show_test_comparison()
