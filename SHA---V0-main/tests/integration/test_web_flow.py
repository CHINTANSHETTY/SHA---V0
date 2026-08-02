"""
End-to-End Flask Web Integration Tests.
"""

import unittest
from app import app


class TestWebFlow(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_login_and_dashboard_access(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Login with Argon2id-validated doctor credentials
        login_res = self.client.post(
            "/login",
            data={"doctorId": "doctor01", "password": "hospital123"},
            follow_redirects=True
        )
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Dashboard", login_res.data)

    def test_encrypt_patient_record_web_flow(self):
        # Login
        self.client.post("/login", data={"doctorId": "doctor01", "password": "hospital123"})

        # Submit encryption form
        encrypt_res = self.client.post(
            "/encrypt",
            data={
                "patientId": "P999",
                "name": "Integration Test Patient",
                "age": "30",
                "gender": "Male",
                "disease": "Testing",
                "diagnosis": "Automated Test",
                "prescription": "Pass Test",
                "password": "test_password_123"
            },
            follow_redirects=True
        )
        self.assertEqual(encrypt_res.status_code, 200)
        self.assertIn(b"encrypted and saved successfully", encrypt_res.data)


if __name__ == "__main__":
    unittest.main()
