import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.database = Path(temporary.name) / "tasks.sqlite3"
        self.app = create_app(self.database)
        self.client = self.enterContext(TestClient(self.app))

    def create_task(self):
        response = self.client.post("/api/tasks", json={"question": "  比较两种数据库  "})
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_health(self):
        self.assertEqual(self.client.get("/api/health").json(), {"status": "ok"})

    def test_create_read_and_list(self):
        task = self.create_task()
        self.assertEqual(task["question"], "比较两种数据库")
        self.assertEqual(task["status"], "draft")
        self.assertIsNone(task["report"])
        self.assertEqual(self.client.get(f'/api/tasks/{task["id"]}').json(), task)
        self.assertEqual(self.client.get("/api/tasks").json(), [task])

    def test_update_draft(self):
        task = self.create_task()
        response = self.client.patch(f'/api/tasks/{task["id"]}', json={"question": "新的问题"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["question"], "新的问题")

    def test_delete_task(self):
        task = self.create_task()
        self.assertEqual(self.client.delete(f'/api/tasks/{task["id"]}').status_code, 204)
        self.assertEqual(self.client.get(f'/api/tasks/{task["id"]}').status_code, 404)

    def test_invalid_question_is_rejected(self):
        for question in ["", "  ", "x" * 2001, [], None]:
            with self.subTest(question=str(question)[:20]):
                response = self.client.post("/api/tasks", json={"question": question})
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["error"]["code"], "invalid_input")

    def test_unknown_task_is_404(self):
        for suffix in ["", "/run", "/cancel"]:
            response = self.client.get("/api/tasks/missing") if not suffix else self.client.post("/api/tasks/missing" + suffix)
            self.assertEqual(response.status_code, 404)

    def test_tasks_survive_app_restart(self):
        task = self.create_task()
        with TestClient(create_app(self.database)) as restarted:
            self.assertEqual(restarted.get(f'/api/tasks/{task["id"]}').json(), task)

    def test_active_task_cannot_be_edited_or_deleted(self):
        data = self.create_task()
        task = self.app.state.store.get(data["id"])
        task.status = "running"
        self.app.state.store.save(task)
        self.assertEqual(self.client.patch(f'/api/tasks/{task.id}', json={"question": "change"}).status_code, 409)
        self.assertEqual(self.client.delete(f'/api/tasks/{task.id}').status_code, 409)


if __name__ == "__main__":
    unittest.main()
