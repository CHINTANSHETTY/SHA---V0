"""
Unit tests for Database Manager & Argon2id Password Hashing.
"""

import unittest
import os
import tempfile
from database.db_manager import (
    createDatabase,
    createDefaultDoctor,
    validateDoctor,
    saveRecord,
    showAllRecords,
    getRecord,
    updateRecord,
    deleteRecord,
    hash_password,
    verify_password,
)


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_path = self.temp_db.name
        self.temp_db.close()
        createDatabase(self.db_path)

    def tearDown(self):
        import gc
        gc.collect()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

    def test_argon2id_hashing(self):
        pwd = "secure_password_123"
        hashed = hash_password(pwd)
        self.assertTrue(hashed.startswith("$argon2id$"))
        self.assertTrue(verify_password(hashed, pwd))
        self.assertFalse(verify_password(hashed, "wrong_password"))

    def test_doctor_creation_and_validation(self):
        createDefaultDoctor(self.db_path)
        self.assertTrue(validateDoctor("doctor01", "hospital123", self.db_path))
        self.assertFalse(validateDoctor("doctor01", "wrong_password", self.db_path))
        self.assertFalse(validateDoctor("non_existent", "hospital123", self.db_path))

    def test_patient_record_crud(self):
        rec_id = saveRecord("P001", "Rahul", "cipher_bytes_hex", self.db_path)
        self.assertGreater(rec_id, 0)

        record = getRecord(rec_id, self.db_path)
        self.assertIsNotNone(record)
        self.assertEqual(record[1], "P001")
        self.assertEqual(record[2], "Rahul")
        self.assertEqual(record[3], "cipher_bytes_hex")

        all_records = showAllRecords(self.db_path)
        self.assertEqual(len(all_records), 1)

        updated = updateRecord(rec_id, "Rahul Kumar", "new_cipher_hex", self.db_path)
        self.assertTrue(updated)
        updated_rec = getRecord(rec_id, self.db_path)
        self.assertEqual(updated_rec[2], "Rahul Kumar")

        deleted = deleteRecord(rec_id, self.db_path)
        self.assertTrue(deleted)
        self.assertIsNone(getRecord(rec_id, self.db_path))


if __name__ == "__main__":
    unittest.main()
