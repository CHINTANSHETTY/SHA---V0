"""
Flask Web Application Endpoint Integration Tests.
"""

import unittest
from app import app
from database import createDatabase, createDefaultDoctor


class TestWebAppEndpoints(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test_secret_key"
        self.client = app.test_client()

        # Initialize temporary DB and doctor
        createDatabase("test_app_records.db")
        createDefaultDoctor("test_app_records.db")

    def tearDown(self):
        import os
        if os.path.exists("test_app_records.db"):
            try:
                os.remove("test_app_records.db")
            except PermissionError:
                pass

    def test_home_page_renders_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Doctor Login", response.data)

    def test_login_and_dashboard_flow(self):
        # Login with default doctor credentials
        response = self.client.post(
            "/login",
            data={"doctorId": "doctor01", "password": "hospital123"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dashboard", response.data)

        # Access dashboard
        response_dash = self.client.get("/dashboard")
        self.assertEqual(response_dash.status_code, 200)
        self.assertIn(b"Welcome Doctor", response_dash.data)

    def test_encrypt_and_decrypt_web_flow(self):
        # Authenticate session
        with self.client.session_transaction() as sess:
            sess["doctor"] = "doctor01"

        # Submit encryption form
        enc_res = self.client.post(
            "/encrypt",
            data={
                "patientId": "P999",
                "name": "Ananya Sharma",
                "age": "34",
                "gender": "Female",
                "disease": "Hypertension",
                "diagnosis": "Essential Hypertension",
                "prescription": "Lisinopril 10mg",
                "password": "doctor_encrypt_pwd_123"
            },
            follow_redirects=True
        )
        self.assertEqual(enc_res.status_code, 200)
        self.assertIn(b"encrypted and saved successfully", enc_res.data)

    def test_logout_flow(self):
        with self.client.session_transaction() as sess:
            sess["doctor"] = "doctor01"

        res = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Doctor Login", res.data)


if __name__ == "__main__":
    unittest.main()
