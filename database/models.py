"""
Database Schema Models & Constants.

IEEE Mapping: Section IV-F (Persistence Tier)
"""

CREATE_DOCTORS_TABLE = """
CREATE TABLE IF NOT EXISTS doctors (
    doctorId TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_PATIENT_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS patientRecords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patientId TEXT NOT NULL,
    patientName TEXT NOT NULL,
    cipherText TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
