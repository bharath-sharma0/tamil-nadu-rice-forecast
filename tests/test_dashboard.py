import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class DashboardTest(unittest.TestCase):
    def test_forecast_and_insufficient_history(self):
        app = AppTest.from_file(
            ROOT / "app" / "streamlit_app.py", default_timeout=20
        ).run()

        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox[0].value, "Ramanathapuram")
        self.assertEqual(app.selectbox[1].value, 2020)
        self.assertEqual(app.metric[0].value, "242.33 kg/ha")
        self.assertEqual(len(app.dataframe[0].value), 5)

        app.selectbox[0].set_value("Chengalpattu").run()

        self.assertFalse(app.exception)
        self.assertFalse(app.metric)
        self.assertIn("Insufficient history for a forecast", app.warning[0].value)
        self.assertEqual(len(app.dataframe[0].value), 5)
