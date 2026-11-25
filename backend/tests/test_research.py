"""Offline contract fixtures; these are not evidence of a live research run."""
import os
from unittest.mock import patch

from app.research import parse_response, ResearchError
from app.schemas import Source
from test_api import ApiTests
from datetime import datetime, timezone


class ResearchTests(ApiTests):
    def test_missing_credentials_preserves_draft(self):
        task = self.create_task()
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            result = self.client.post(f'/api/tasks/{task["id"]}/run')
        self.assertEqual(result.status_code, 503)
        self.assertEqual(self.app.state.store.get(task["id"]).status, "draft")

    def test_success_persists_report_and_prevents_rerun(self):
        task = self.create_task()
        source = Source(id="1", title="Fixture", url="https://example.com", excerpt="",
                        fetched_at=datetime.now(timezone.utc))
        with patch("app.main.configured", return_value=True), patch("app.main.research", return_value=("结论 [1]", [source])):
            self.assertEqual(self.client.post(f'/api/tasks/{task["id"]}/run').status_code, 202)
            result = self.client.get(f'/api/tasks/{task["id"]}').json()
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["report"], "结论 [1]")
            self.assertEqual(len(result["sources"]), 1)
            self.assertEqual(self.client.post(f'/api/tasks/{task["id"]}/run').status_code, 409)

    def test_failure_and_retry(self):
        task = self.create_task()
        with patch("app.main.configured", return_value=True), patch("app.main.research", side_effect=ResearchError("provider_error", "配额不足")):
            for _ in range(2):
                self.assertEqual(self.client.post(f'/api/tasks/{task["id"]}/run').status_code, 202)
                result = self.client.get(f'/api/tasks/{task["id"]}').json()
                self.assertEqual(result["status"], "failed")
                self.assertIsNone(result["report"])
                self.assertEqual(result["error"]["code"], "provider_error")

    def test_citation_normalization(self):
        data = {"status": "completed", "output": [
            {"type": "web_search_call", "status": "completed"},
            {"type": "message", "content": [{"type": "output_text", "text": "事实 citation",
                "annotations": [{"type": "url_citation", "url": "https://example.com", "title": "来源", "start_index": 3, "end_index": 11}]}]}]}
        report, sources = parse_response(data)
        self.assertEqual(report, "事实 [1]")
        self.assertEqual(sources[0].url, "https://example.com")
        data["output"][1]["content"][0]["annotations"][0]["url"] = "javascript:alert(1)"
        with self.assertRaises(ResearchError):
            parse_response(data)

    def test_no_search_or_partial_report_rejected(self):
        for data in [{"status": "incomplete"}, {"status": "completed", "output": []}]:
            with self.assertRaises(ResearchError):
                parse_response(data)

    def test_restart_recovers_inflight_task(self):
        from app.main import create_app
        task = self.create_task()
        stored = self.app.state.store.get(task["id"])
        stored.status = "running"
        self.app.state.store.save(stored)
        restarted = create_app(self.database)
        self.assertEqual(restarted.state.store.get(stored.id).error.code, "interrupted")
