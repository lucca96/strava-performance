import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

import main
from src.analysis import classify_activity, render_report, upsert_history
from src.ai_ready_report import ai_ready_filename, write_ai_ready_report
from src.client import ApiBudgetExceeded, StravaClient
from src.weekly_report import weekly_filename, write_all_weekly_reports, write_weekly_report


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="OK", headers=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text
        self.headers = headers or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.text)


class FakeSession:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if not self.responses:
            return FakeResponse(200, {})
        return self.responses.pop(0)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        scratch_root = Path.cwd() / "data" / "test_tmp"
        scratch_root.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch_root)
        self.data_dir = Path(self.tmp.name)
        main.DATA_DIR = self.data_dir
        main.INDEX_PATH = self.data_dir / "cache" / "activity_index.json"
        main.HISTORY_PATH = self.data_dir / "performance_history.csv"
        main.REPORTS_DIR = self.data_dir / "reports"
        main.WEEKLY_REPORTS_DIR = self.data_dir / "weekly_reports"
        main.AI_REPORTS_DIR = self.data_dir / "ai_reports"

    def tearDown(self):
        self.tmp.cleanup()

    def write_json(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def seed_activity_cache(self):
        activity = {
            "id": 1,
            "name": "Run cached",
            "type": "Run",
            "start_date_local": "2024-01-01T07:00:00Z",
            "has_heartrate": True,
            "distance": 2000,
            "moving_time": 600,
            "max_heartrate": 180,
        }
        self.write_json(main.INDEX_PATH, {"complete": True, "cached_pages": [1], "activities": [activity]})
        base = self.data_dir / "cache" / "activities" / "1"
        self.write_json(
            base / "details.json",
            {
                "id": 1,
                "name": "Run cached",
                "type": "Run",
                "start_date_local": "2024-01-01T07:00:00Z",
                "distance": 2000,
                "moving_time": 600,
                "average_heartrate": 150,
                "max_heartrate": 180,
            },
        )
        self.write_json(
            base / "streams.json",
            {
                "time": {"data": [0, 1, 2, 3]},
                "heartrate": {"data": [140, 150, 160, 170]},
                "distance": {"data": [0, 500, 1000, 2000]},
            },
        )
        self.write_json(
            base / "laps.json",
            [
                {"distance": 1000, "moving_time": 300},
                {"distance": 1000, "moving_time": 300},
            ],
        )

    def test_analyze_uses_cache_without_api_calls(self):
        self.seed_activity_cache()
        session = FakeSession()
        client = StravaClient(data_dir=self.data_dir, max_calls=10, session=session)

        record = main.cmd_analyze(client, "1")

        self.assertEqual(client.calls_made, 0)
        self.assertEqual(len(session.calls), 0)
        self.assertEqual(record["analysis_status"], "complete")
        self.assertTrue((self.data_dir / "performance_history.csv").exists())
        self.assertTrue((self.data_dir / "reports" / "1.md").exists())

    def test_budget_is_not_exceeded(self):
        session = FakeSession(
            [
                FakeResponse(200, {"access_token": "abc", "expires_at": 9999999999}),
            ]
        )
        client = StravaClient(data_dir=self.data_dir, max_calls=1, session=session)

        with self.assertRaises(ApiBudgetExceeded):
            client.get_activity_details(1)

        self.assertEqual(client.calls_made, 1)
        self.assertEqual(len(session.calls), 1)

    def test_history_upsert_does_not_duplicate_activity(self):
        record = {
            "activity_id": 1,
            "name": "first",
            "type": "Run",
            "start_date_local": "2024-01-01T00:00:00Z",
        }
        upsert_history(record, main.HISTORY_PATH)
        record["name"] = "updated"
        upsert_history(record, main.HISTORY_PATH)

        df = pd.read_csv(main.HISTORY_PATH)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.loc[0, "name"], "updated")

    def test_report_omits_status_and_classifies_activity(self):
        report = render_report(
            {
                "activity_id": 1,
                "name": "NoGi + Wrestling",
                "type": "Workout",
                "start_date_local": "2024-01-01T00:00:00Z",
                "moving_time_min": 60,
                "perceived_exertion": 8,
            }
        )

        self.assertIn("- Categoria: grappling", report)
        self.assertNotIn("## Status", report)
        self.assertNotIn("- Status:", report)

    def test_report_accepts_csv_string_numbers(self):
        report = render_report(
            {
                "activity_id": "2",
                "name": "Pedalada",
                "type": "Ride",
                "start_date_local": "2024-01-01T00:00:00Z",
                "distance_km": "10.0",
                "moving_time_min": "60.0",
                "pace_summary_sec_km": "360.0",
                "perceived_exertion": "",
            }
        )

        self.assertIn("- Pace medio: 6:00/km", report)

    def test_activity_classification_rules(self):
        self.assertEqual(classify_activity("Gi na Toca"), "grappling")
        self.assertEqual(classify_activity("Preparação Física CDPD"), "preparacao_fisica")
        self.assertEqual(classify_activity("PreparaÃ§Ã£o FÃ­sica CDPD"), "preparacao_fisica")
        self.assertEqual(classify_activity("Pedalada na 040"), "outros")

    def test_weekly_report_uses_iso_week_filename(self):
        self.assertEqual(weekly_filename(2025, 2), "2025_semana_02.md")

    def test_ai_ready_report_uses_iso_week_filename(self):
        self.assertEqual(ai_ready_filename(2025, 2), "2025_semana_02_ai.md")

    def test_weekly_report_generation(self):
        rows = [
            {
                "activity_id": 1,
                "name": "NoGi",
                "type": "Workout",
                "activity_category": "grappling",
                "start_date_local": "2025-01-06T20:00:00Z",
                "moving_time_min": 60,
                "perceived_exertion": 8,
                "session_rpe_load": 480,
                "average_heartrate": 140,
                "max_heartrate": 175,
                "cardiac_drift_pct": 5,
                "z1_min": 10,
                "z2_min": 20,
                "z3_min": 20,
                "z4_min": 10,
                "z5_min": 0,
            },
            {
                "activity_id": 2,
                "name": "Preparacao Fisica CDPD",
                "type": "Workout",
                "activity_category": "preparacao_fisica",
                "start_date_local": "2025-01-08T20:00:00Z",
                "moving_time_min": 45,
                "perceived_exertion": 7,
                "session_rpe_load": 315,
                "average_heartrate": 120,
                "max_heartrate": 160,
                "cardiac_drift_pct": 3,
                "z1_min": 30,
                "z2_min": 10,
                "z3_min": 5,
                "z4_min": 0,
                "z5_min": 0,
            },
        ]
        pd.DataFrame(rows).to_csv(main.HISTORY_PATH, index=False)

        path = write_weekly_report(main.HISTORY_PATH, main.WEEKLY_REPORTS_DIR, 2025, 2)
        report = path.read_text(encoding="utf-8")

        self.assertEqual(path.name, "2025_semana_02.md")
        self.assertIn("# Relatorio semanal 2025-W02", report)
        self.assertIn("- Sessoes: 2", report)
        self.assertIn("- grappling: 1 sessoes", report)
        self.assertIn("## Prompt para AI", report)

    def test_ai_ready_report_generation(self):
        rows = [
            {
                "activity_id": 1,
                "name": "NoGi",
                "type": "Workout",
                "activity_category": "grappling",
                "start_date_local": "2025-01-06T20:00:00Z",
                "moving_time_min": 60,
                "perceived_exertion": 8,
                "session_rpe_load": 480,
            }
        ]
        pd.DataFrame(rows).to_csv(main.HISTORY_PATH, index=False)

        path = write_ai_ready_report(main.HISTORY_PATH, main.AI_REPORTS_DIR, 2025, 2)
        report = path.read_text(encoding="utf-8")

        self.assertEqual(path.name, "2025_semana_02_ai.md")
        self.assertIn("## Contexto fixo", report)
        self.assertIn("## Tarefa para AI", report)
        self.assertIn("## Dados estruturados da semana", report)
        self.assertIn("Analise os dados abaixo", report)

    def test_write_all_weekly_reports(self):
        rows = [
            {
                "activity_id": 1,
                "name": "Gi",
                "type": "Workout",
                "activity_category": "grappling",
                "start_date_local": "2025-01-06T20:00:00Z",
            },
            {
                "activity_id": 2,
                "name": "Gi",
                "type": "Workout",
                "activity_category": "grappling",
                "start_date_local": "2025-01-13T20:00:00Z",
            },
        ]
        pd.DataFrame(rows).to_csv(main.HISTORY_PATH, index=False)

        paths = write_all_weekly_reports(main.HISTORY_PATH, main.WEEKLY_REPORTS_DIR)

        self.assertEqual([path.name for path in paths], ["2025_semana_02.md", "2025_semana_03.md"])

    def test_weekly_report_handles_missing_load(self):
        rows = [
            {
                "activity_id": 1,
                "name": "Gi",
                "type": "Workout",
                "activity_category": "grappling",
                "start_date_local": "2025-01-06T20:00:00Z",
            }
        ]
        pd.DataFrame(rows).to_csv(main.HISTORY_PATH, index=False)

        path = write_weekly_report(main.HISTORY_PATH, main.WEEKLY_REPORTS_DIR, 2025, 2)

        self.assertTrue(path.exists())

    def test_sync_refreshes_latest_page_and_generates_weekly(self):
        session = FakeSession(
            [
                FakeResponse(200, {"access_token": "abc", "expires_at": 9999999999}),
                FakeResponse(
                    200,
                    [
                        {
                            "id": 10,
                            "name": "NoGi",
                            "type": "Workout",
                            "start_date_local": "2025-01-06T20:00:00Z",
                            "has_heartrate": True,
                            "distance": 0,
                            "moving_time": 3600,
                            "max_heartrate": 180,
                        }
                    ],
                ),
                FakeResponse(
                    200,
                    {
                        "id": 10,
                        "name": "NoGi",
                        "type": "Workout",
                        "start_date_local": "2025-01-06T20:00:00Z",
                        "distance": 0,
                        "moving_time": 3600,
                        "average_heartrate": 145,
                        "max_heartrate": 180,
                        "perceived_exertion": 8,
                    },
                ),
                FakeResponse(
                    200,
                    {
                        "time": {"data": [0, 1, 2, 3]},
                        "heartrate": {"data": [140, 145, 150, 155]},
                    },
                ),
            ]
        )
        client = StravaClient(data_dir=self.data_dir, max_calls=10, session=session)

        record = main.cmd_sync(client)

        self.assertEqual(record["activity_id"], 10)
        self.assertEqual(client.calls_made, 4)
        self.assertTrue((main.WEEKLY_REPORTS_DIR / "2025_semana_02.md").exists())

    def test_backfill_stops_after_index_budget(self):
        session = FakeSession(
            [
                FakeResponse(200, {"access_token": "abc", "expires_at": 9999999999}),
                FakeResponse(
                    200,
                    [
                        {
                            "id": 1,
                            "name": "Run",
                            "type": "Run",
                            "start_date_local": "2024-01-01T00:00:00Z",
                            "has_heartrate": True,
                        }
                    ],
                ),
            ]
        )
        client = StravaClient(data_dir=self.data_dir, max_calls=2, session=session)

        result = main.cmd_backfill(client)

        self.assertIsNone(result)
        self.assertEqual(client.calls_made, 2)
        self.assertFalse(main.HISTORY_PATH.exists())


if __name__ == "__main__":
    unittest.main()
