from collections import defaultdict
from math import isfinite

import lightgbm as lgb
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing


def trailing_history(history):
    start = len(history) - 1
    while start > 0 and history[start][0] - history[start - 1][0] == 1:
        start -= 1
    return history[start:] if history else []


def predict_lightgbm(conn, year, cutoff, features, plan):
    columns = ", ".join(features)
    train = conn.execute(
        f"""SELECT target_yield_kg_per_ha, {columns}
            FROM evaluation_features
            WHERE crop_year_start <= ? AND target_yield_kg_per_ha IS NOT NULL
            ORDER BY crop_year_start, district_id""",
        (cutoff,),
    ).fetchall()
    future = conn.execute(
        f"""SELECT district_id, {columns}
            FROM evaluation_features WHERE crop_year_start = ?
            ORDER BY district_id""",
        (year,),
    ).fetchall()

    X = np.asarray([row[1:] for row in train], dtype=float)
    y = np.asarray([row[0] for row in train], dtype=float)
    X_next = np.asarray([row[1:] for row in future], dtype=float)
    model = lgb.train(
        plan["lightgbm_parameters"],
        lgb.Dataset(X, label=y, feature_name=features),
        num_boost_round=plan["lightgbm_rounds"],
    )
    predictions = model.predict(X_next, num_threads=1)
    if not np.isfinite(predictions).all():
        raise ValueError(f"Nonfinite LightGBM forecast in {year}")
    return {(row[0], year): float(value) for row, value in zip(future, predictions)}


def generate_frozen_forecasts(conn, plan):
    years = plan["final_test_years"]
    limit = plan["latest_training_label_year"]
    delay = plan["yield_feature_delay_years"]
    features = plan["lightgbm_features"]
    columns = ", ".join(features)

    conn.execute("DROP TABLE IF EXISTS temp.evaluation_features")
    conn.execute(
        f"""CREATE TEMP TABLE evaluation_features AS
            SELECT district_id, crop_year_start,
                   CASE WHEN crop_year_start <= ? THEN target_yield_kg_per_ha END
                       AS target_yield_kg_per_ha,
                   {columns}
            FROM main.rice_forecast_features
            WHERE crop_year_start <= ?""",
        (limit, max(years)),
    )
    forecasts = {method: {} for method in plan["comparison_methods"]}

    for year in years:
        cutoff = min(year - delay, limit)
        for district, last, average in conn.execute(
            """SELECT district_id, yield_last_available, yield_trailing_avg_3
               FROM evaluation_features WHERE crop_year_start = ?""",
            (year,),
        ):
            if last is not None:
                forecasts["Last available"][district, year] = last
            if average is not None:
                forecasts["Trailing average"][district, year] = average

        histories = defaultdict(list)
        for district, source_year, value in conn.execute(
            """SELECT district_id, crop_year_start, target_yield_kg_per_ha
               FROM evaluation_features
               WHERE crop_year_start <= ? AND target_yield_kg_per_ha IS NOT NULL
               ORDER BY district_id, crop_year_start""",
            (cutoff,),
        ):
            histories[district].append((source_year, value))

        for district, history in histories.items():
            eligible = trailing_history(history)
            if len(eligible) < plan["ses_min_consecutive_observations"]:
                continue
            fit = SimpleExpSmoothing(
                [value for _, value in eligible], initialization_method="estimated"
            ).fit(optimized=True)
            value = float(fit.forecast(year - eligible[-1][0])[-1])
            if not isfinite(value):
                raise ValueError(f"Nonfinite smoothing forecast: {district}, {year}")
            forecasts["Exponential smoothing"][district, year] = value

        for method, inputs in (
            ("LightGBM history only", features[:2]),
            ("LightGBM history + weather", features),
        ):
            forecasts[method].update(predict_lightgbm(conn, year, cutoff, inputs, plan))

    return forecasts
