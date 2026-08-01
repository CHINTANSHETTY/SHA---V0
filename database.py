import sqlite3


def createDatabase():
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    # Doctor Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors(
        doctorId TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    # Patient Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patientRecords(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patientId TEXT,
        patientName TEXT,
        cipherText TEXT
    )
    """)

    conn.commit()
    conn.close()


def createDefaultDoctor():
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO doctors
    VALUES(?,?)
    """, ("doctor01", "hospital123"))

    conn.commit()
    conn.close()


def validateDoctor(doctorId, password):
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM doctors
    WHERE doctorId=? AND password=?
    """, (doctorId, password))

    doctor = cursor.fetchone()

    conn.close()

    return doctor is not None


def saveRecord(patientId, patientName, cipherText):
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patientRecords
    (patientId,patientName,cipherText)
    VALUES(?,?,?)
    """, (patientId, patientName, cipherText))

    conn.commit()
    conn.close()


def showAllRecords():
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM patientRecords
    """)

    records = cursor.fetchall()

    conn.close()

    return records


def getRecord(recordId):
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM patientRecords
    WHERE id=?
    """, (recordId,))

    record = cursor.fetchone()

    conn.close()

    return record


# -----------------------------
# UPDATE RECORD
# -----------------------------
def updateRecord(recordId, patientName, cipherText):

    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE patientRecords
    SET patientName = ?, cipherText = ?
    WHERE id = ?
    """, (patientName, cipherText, recordId))

    conn.commit()
    conn.close()
    
    # -----------------------------
# DELETE RECORD
# -----------------------------
def deleteRecord(recordId):

    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM patientRecords
        WHERE id = ?
    """, (recordId,))

    conn.commit()
    conn.close()