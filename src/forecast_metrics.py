from math import sqrt
from statistics import mean


def forecast_metrics(actuals, forecasts):
    if len(actuals) != len(forecasts) or len(actuals) == 0:
        raise ValueError("Expected equal, nonempty actual and forecast sequences")

    errors = [forecast - actual for actual, forecast in zip(actuals, forecasts)]
    percentages = [
        abs(error) / actual * 100
        for actual, error in zip(actuals, errors)
        if actual > 0
    ]
    return {
        "mae": mean(abs(error) for error in errors),
        "rmse": sqrt(mean(error ** 2 for error in errors)),
        "mape": mean(percentages) if percentages else None,
        "mape_rows": len(percentages),
    }
