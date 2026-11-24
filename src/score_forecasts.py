import csv
from collections import defaultdict
from random import Random
from statistics import mean, quantiles

from src.forecast_metrics import forecast_metrics


def mae_interval(keys, actuals, predictions):
    errors = defaultdict(list)
    for key in keys:
        errors[key[1]].append(abs(actuals[key] - predictions[key]))

    years = sorted(errors)
    if len(years) < 2:
        return None, None

    rng = Random(42)
    samples = [
        mean(error for year in rng.choices(years, k=len(years))
             for error in errors[year])
        for _ in range(5_000)
    ]
    bounds = quantiles(samples, n=1000, method="inclusive")
    return bounds[24], bounds[974]


def write_test_reports(output_dir, plan, district_names, actuals, forecasts):
    methods = plan["comparison_methods"]
    groups = plan["district_groups"]
    shared = set(actuals).intersection(*(forecasts[method] for method in methods))
    if not shared:
        raise ValueError("No observed rows with predictions from all methods")

    selected = forecasts[plan["selected_method"]]
    width = plan["prediction_interval"]["half_width_kg_per_ha"]
    metrics_rows = []
    interval_rows = []

    for group in ("Overall", *sorted(set(groups.values()))):
        observed = {key for key in actuals
                    if group == "Overall" or groups[district_names[key[0]]] == group}
        keys = sorted(observed & shared)

        for method in methods:
            predictions = forecasts[method]
            scores = forecast_metrics(
                [actuals[key] for key in keys],
                [predictions[key] for key in keys],
            ) if keys else {}
            low, high = mae_interval(keys, actuals, predictions)
            metrics_rows.append({
                "group": group,
                "method": method,
                "observed_rows": len(observed),
                "forecast_rows": len(observed & predictions.keys()),
                "shared_rows": len(keys),
                "scored_years": len({year for _, year in keys}),
                "mae_kg_per_ha": scores.get("mae"),
                "mae_ci_95_lower": low,
                "mae_ci_95_upper": high,
                "rmse_kg_per_ha": scores.get("rmse"),
                "mape_percent": scores.get("mape"),
                "mape_rows": scores.get("mape_rows", 0),
            })

        eligible = observed & selected.keys()
        hits = sum(
            max(0, selected[key] - width) <= actuals[key] <= selected[key] + width
            for key in eligible
        )
        interval_rows.append((group, len(eligible), hits))

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "final_test_metrics.csv").open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(metrics_rows[0]))
        writer.writeheader()
        writer.writerows(metrics_rows)
    with (output_dir / "final_test_interval_coverage.csv").open("w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["district_group", "scored_intervals", "inside_interval"])
        writer.writerows(interval_rows)

    return len(metrics_rows), len(interval_rows)
