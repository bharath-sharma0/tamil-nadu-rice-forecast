import unittest
from math import sqrt

from src.forecast_metrics import forecast_metrics


class ForecastMetricsTest(unittest.TestCase):
    def test_known_errors_with_zero_actual(self):
        scores = forecast_metrics([0, 100, 200], [10, 80, 240])
        self.assertAlmostEqual(scores["mae"], 70 / 3)
        self.assertAlmostEqual(scores["rmse"], sqrt(700))
        self.assertAlmostEqual(scores["mape"], 20)
        self.assertEqual(scores["mape_rows"], 2)

    def test_no_positive_actuals(self):
        scores = forecast_metrics([0], [10])
        self.assertIsNone(scores["mape"])
        self.assertEqual(scores["mape_rows"], 0)
        self.assertEqual(scores["mae"], 10)
