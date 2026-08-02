"""
Database Manager & Argon2id Authentication Interface.

IEEE Mapping: Section IV-F (Persistence & Credential Protection)
"""

import sqlite3
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from database.models import CREATE_DOCTORS_TABLE, CREATE_PATIENT_RECORDS_TABLE

DB_FILE = "records.db"
_ph = PasswordHasher()


def get_db_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    """Returns a SQLite connection object with row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def createDatabase(db_path: str = DB_FILE) -> None:
    """Creates SQLite database tables if they do not exist and migrates legacy schemas."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_DOCTORS_TABLE)
        cursor.execute(CREATE_PATIENT_RECORDS_TABLE)

        # Legacy database schema migration check
        cursor.execute("PRAGMA table_info(doctors)")
        columns = [col["name"] for col in cursor.fetchall()]
        if "password" in columns and "password_hash" not in columns:
            cursor.execute("ALTER TABLE doctors RENAME COLUMN password TO password_hash")

        conn.commit()


def hash_password(password: str) -> str:
    """Hashes password using Argon2id with random salt."""
    return _ph.hash(password)


def verify_password(hash_str: str, password: str) -> bool:
    """Verifies password against Argon2id hash in constant time."""
    try:
        return _ph.verify(hash_str, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def createDefaultDoctor(db_path: str = DB_FILE) -> None:
    """Creates default doctor credential (doctor01 / hospital123) hashed with Argon2id."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM doctors WHERE doctorId = ?", ("doctor01",))
        existing = cursor.fetchone()

        if not existing:
            pwd_hash = hash_password("hospital123")
            cursor.execute(
                "INSERT INTO doctors (doctorId, password_hash) VALUES (?, ?)",
                ("doctor01", pwd_hash)
            )
            conn.commit()


def validateDoctor(doctorId: str, password: str, db_path: str = DB_FILE) -> bool:
    """Validates doctor credentials using Argon2id password verification."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash FROM doctors WHERE doctorId = ?",
            (doctorId,)
        )
        row = cursor.fetchone()

        if not row:
            return False

        # Support both legacy plaintext (for seamless migration) and Argon2id hash
        stored_hash = row["password_hash"]
        if stored_hash.startswith("$argon2id$"):
            valid = verify_password(stored_hash, password)
            if valid and _ph.check_needs_rehash(stored_hash):
                new_hash = hash_password(password)
                cursor.execute(
                    "UPDATE doctors SET password_hash = ? WHERE doctorId = ?",
                    (new_hash, doctorId)
                )
                conn.commit()
            return valid
        elif stored_hash == password:
            # Re-hash legacy plaintext password automatically to Argon2id
            new_hash = hash_password(password)
            cursor.execute(
                "UPDATE doctors SET password_hash = ? WHERE doctorId = ?",
                (new_hash, doctorId)
            )
            conn.commit()
            return True

        return False


def saveRecord(patientId: str, patientName: str, cipherText: str, db_path: str = DB_FILE) -> int:
    """Saves encrypted patient record into SQLite database."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO patientRecords (patientId, patientName, cipherText)
            VALUES (?, ?, ?)
            """,
            (patientId, patientName, cipherText)
        )
        conn.commit()
        return cursor.lastrowid


def showAllRecords(db_path: str = DB_FILE) -> list[tuple]:
    """Retrieves all patient records as list of tuples (id, patientId, patientName, cipherText)."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, patientId, patientName, cipherText FROM patientRecords")
        rows = cursor.fetchall()
        return [(r["id"], r["patientId"], r["patientName"], r["cipherText"]) for r in rows]


def getRecord(recordId: int, db_path: str = DB_FILE) -> tuple | None:
    """Retrieves a single patient record by recordId."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, patientId, patientName, cipherText FROM patientRecords WHERE id = ?",
            (recordId,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return (row["id"], row["patientId"], row["patientName"], row["cipherText"])


def updateRecord(recordId: int, patientName: str, cipherText: str, db_path: str = DB_FILE) -> bool:
    """Updates patient record by recordId."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE patientRecords
            SET patientName = ?, cipherText = ?
            WHERE id = ?
            """,
            (patientName, cipherText, recordId)
        )
        conn.commit()
        return cursor.rowcount > 0


def deleteRecord(recordId: int, db_path: str = DB_FILE) -> bool:
    """Deletes patient record by recordId."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patientRecords WHERE id = ?", (recordId,))
        conn.commit()
        return cursor.rowcount > 0
