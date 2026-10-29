import unittest

from app import create_app


class FakeBrain:
    def chat(self, message):
        if message == "fail":
            raise RuntimeError("brain failed")
        return f"Reply: {message}"


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(FakeBrain())
        self.app.testing = True
        self.client = self.app.test_client()

    def test_ui_assets_are_served(self):
        for path, mimetype in (
            ("/", "text/html"),
            ("/styles.css", "text/css"),
            ("/script.js", "application/javascript"),
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, mimetype)
                response.close()

    def test_chat_validates_json_and_message(self):
        self.assertEqual(self.client.post("/api/chat", json=[]).status_code, 400)
        self.assertEqual(
            self.client.post("/api/chat", json={"message": 12}).status_code,
            400,
        )
        self.assertEqual(
            self.client.post("/api/chat", json={"message": " "}).status_code,
            400,
        )
        self.assertEqual(
            self.client.post("/api/chat", json={"message": "x" * 4001}).status_code,
            400,
        )

    def test_chat_returns_brain_response_and_surfaces_failures(self):
        response = self.client.post("/api/chat", json={"message": "hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["response"], "Reply: hello")
        self.assertTrue(response.json["timestamp"].endswith("+00:00"))

        failure = self.client.post("/api/chat", json={"message": "fail"})
        self.assertEqual(failure.status_code, 502)
        self.assertFalse(failure.json["success"])

    def test_health_returns_live_metrics_on_current_platform(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["success"], True)
        self.assertIn("cpu_usage", response.json["data"])
        self.assertIn("memory_usage", response.json["data"])
        self.assertIn("disk_usage", response.json["data"])

    def test_monitor_returns_processes_and_uptime(self):
        response = self.client.get("/api/monitor")
        self.assertEqual(response.status_code, 200)
        data = response.json["data"]
        self.assertGreaterEqual(data["process_count"], len(data["processes"]))
        self.assertIsInstance(data["uptime_seconds"], int)

    def test_encryption_returns_recoverable_ciphertext_and_key(self):
        invalid = self.client.post("/api/encrypt", json={"text": ""})
        self.assertEqual(invalid.status_code, 400)

        response = self.client.post("/api/encrypt", json={"text": "private"})
        self.assertEqual(response.status_code, 200)
        encrypted = response.json["data"]
        manager = self.app.config["ENCRYPTION_MANAGER"]
        manager_with_key = type(manager)(encrypted["key"].encode("ascii"))
        self.assertEqual(
            manager_with_key.decrypt_data(encrypted["encrypted"].encode("ascii")),
            "private",
        )

    def test_hash_uses_salted_password_hashing(self):
        invalid = self.client.post("/api/hash", json={"password": ""})
        self.assertEqual(invalid.status_code, 400)

        response = self.client.post("/api/hash", json={"password": "correct horse"})
        self.assertEqual(response.status_code, 200)
        result = response.json["data"]
        hasher = self.app.config["PASSWORD_HASHER"]
        self.assertEqual(result["algorithm"], "PBKDF2-HMAC-SHA256")
        self.assertTrue(hasher.verify_password(
            "correct horse", result["hash"], result["salt"]
        ))
        self.assertFalse(hasher.verify_password(
            "wrong password", result["hash"], result["salt"]
        ))

    def test_audit_reports_scope_and_configuration(self):
        response = self.client.post("/api/audit")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not a malware or vulnerability scan", response.json["data"]["scope"])

        self.app.config["OMNI_HOST"] = "0.0.0.0"
        warning = self.client.post("/api/audit")
        checks = warning.json["data"]["checks"]
        binding_check = next(check for check in checks if check["name"] == "Loopback-only binding")
        self.assertEqual(binding_check["status"], "warning")


if __name__ == "__main__":
    unittest.main()
