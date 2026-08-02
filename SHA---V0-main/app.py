from flask import Flask, render_template, request, redirect, url_for, session

from database import (
    createDatabase,
    createDefaultDoctor,
    validateDoctor,
    saveRecord,
    showAllRecords,
    getRecord,
    updateRecord,
    deleteRecord,
)

from crypto.engine.encrypt import encrypt_payload
from crypto.engine.decrypt import decrypt_payload
from crypto.models.package import EncryptedPackage
from crypto.models.exceptions import CryptoError, AuthenticationError
from decrypt import decryptRecord as legacy_decryptRecord


# =========================================================
# FLASK APPLICATION SETUP
# =========================================================

app = Flask(__name__)
app.secret_key = "sha_healthcare_secret_key"


# =========================================================
# DATABASE SETUP
# =========================================================

createDatabase()
createDefaultDoctor()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    if "doctor" in session:
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():
    doctorId = request.form.get("doctorId", "").strip()
    password = request.form.get("password", "")

    if not doctorId or not password:
        return "Please enter Doctor ID and Password."

    if validateDoctor(doctorId, password):
        session["doctor"] = doctorId
        return redirect(url_for("dashboard"))

    return "Invalid Doctor ID or Password"


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():
    if "doctor" not in session:
        return redirect(url_for("home"))

    records = showAllRecords()
    totalRecords = len(records)

    return render_template(
        "dashboard.html",
        doctor=session["doctor"],
        totalRecords=totalRecords
    )


# =========================================================
# ENCRYPT PATIENT RECORD
# =========================================================

@app.route("/encrypt", methods=["GET", "POST"])
def encryptPage():
    if "doctor" not in session:
        return redirect(url_for("home"))

    cipherText = None
    message = None

    if request.method == "POST":
        patientId = request.form.get("patientId", "").strip()
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        disease = request.form.get("disease", "").strip()
        diagnosis = request.form.get("diagnosis", "").strip()
        prescription = request.form.get("prescription", "").strip()
        password = request.form.get("password", "")

        if not all([
            patientId,
            name,
            age,
            gender,
            disease,
            diagnosis,
            prescription,
            password
        ]):
            return render_template(
                "encrypt.html",
                cipherText=None,
                message="Please fill in all fields."
            )

        try:
            ageNumber = int(age)
            if ageNumber <= 0 or ageNumber > 150:
                raise ValueError
        except ValueError:
            return render_template(
                "encrypt.html",
                cipherText=None,
                message="Please enter a valid age."
            )

        patientData = (
            patientId + "|" +
            name + "|" +
            age + "|" +
            gender + "|" +
            disease + "|" +
            diagnosis + "|" +
            prescription
        )

        try:
            # Encrypt using KDR-CA-AEAD Authenticated Cipher
            pkg = encrypt_payload(patientData, password)
            cipherText = pkg.to_json()

            saveRecord(
                patientId,
                name,
                cipherText
            )

            message = "Patient record encrypted and saved successfully with KDR-CA-AEAD."

        except Exception as error:
            print("Encryption Error:", error)
            message = "Unable to encrypt the patient record."

    return render_template(
        "encrypt.html",
        cipherText=cipherText,
        message=message
    )


# =========================================================
# VIEW ALL RECORDS
# =========================================================

@app.route("/records")
def recordsPage():
    if "doctor" not in session:
        return redirect(url_for("home"))

    records = showAllRecords()
    return render_template(
        "records.html",
        records=records
    )


# =========================================================
# VIEW SINGLE RECORD
# =========================================================

@app.route("/record/<int:recordId>")
def patientPage(recordId):
    if "doctor" not in session:
        return redirect(url_for("home"))

    record = getRecord(recordId)

    if record is None:
        return "Patient Record Not Found", 404

    return render_template(
        "patient.html",
        record=record
    )


# =========================================================
# DECRYPT PATIENT RECORD
# =========================================================

@app.route("/decrypt/<int:recordId>", methods=["POST"])
def decryptPage(recordId):
    if "doctor" not in session:
        return redirect(url_for("home"))

    record = getRecord(recordId)

    if record is None:
        return "Patient Record Not Found", 404

    password = request.form.get("password", "")

    if not password:
        return render_template(
            "patient.html",
            record=record,
            error="Please enter the decryption password."
        )

    try:
        cipherText = record[3]

        if cipherText.startswith("{") and "KDR-CA-AEAD" in cipherText:
            pkg = EncryptedPackage.from_json(cipherText)
            originalData = decrypt_payload(pkg, password)
        else:
            # Fallback for legacy V0 unauthenticated records
            originalData = legacy_decryptRecord(cipherText, password)

        data = originalData.split("|")

        if len(data) != 7:
            return render_template(
                "patient.html",
                record=record,
                error="Invalid password or corrupted patient record."
            )

        if data[0] != str(record[1]):
            return render_template(
                "patient.html",
                record=record,
                error="Invalid decryption password."
            )

        return render_template(
            "decrypt.html",
            patientId=data[0],
            name=data[1],
            age=data[2],
            gender=data[3],
            disease=data[4],
            diagnosis=data[5],
            prescription=data[6]
        )

    except AuthenticationError:
        return render_template(
            "patient.html",
            record=record,
            error="Authentication failed: Invalid password or payload tampered with."
        )
    except Exception as error:
        print("Decryption Error:", error)
        return render_template(
            "patient.html",
            record=record,
            error="Unable to decrypt the record. Check the password."
        )


# =========================================================
# EDIT PATIENT - PASSWORD PAGE
# =========================================================

@app.route("/edit/<int:recordId>", methods=["GET", "POST"])
def editPage(recordId):
    if "doctor" not in session:
        return redirect(url_for("home"))

    record = getRecord(recordId)

    if record is None:
        return "Patient Record Not Found", 404

    error = None

    if request.method == "POST":
        password = request.form.get("password", "")

        if not password:
            error = "Please enter the encryption password."
        else:
            try:
                cipherText = record[3]

                if cipherText.startswith("{") and "KDR-CA-AEAD" in cipherText:
                    pkg = EncryptedPackage.from_json(cipherText)
                    originalData = decrypt_payload(pkg, password)
                else:
                    originalData = legacy_decryptRecord(cipherText, password)

                data = originalData.split("|")

                if len(data) != 7:
                    error = "Invalid password or unsupported patient record."
                elif data[0] != str(record[1]):
                    error = "Invalid password."
                else:
                    session["editPassword"] = password
                    session["editRecordId"] = recordId

                    return render_template(
                        "editPatient.html",
                        recordId=recordId,
                        patientId=data[0],
                        name=data[1],
                        age=data[2],
                        gender=data[3],
                        disease=data[4],
                        diagnosis=data[5],
                        prescription=data[6]
                    )

            except AuthenticationError:
                error = "Invalid password or payload tag mismatch."
            except Exception as errorMessage:
                print("Edit Decryption Error:", errorMessage)
                error = "Invalid password or unable to decrypt record."

    return render_template(
        "editPassword.html",
        record=record,
        error=error
    )


# =========================================================
# UPDATE PATIENT RECORD
# =========================================================

@app.route("/update/<int:recordId>", methods=["POST"])
def updatePatient(recordId):
    if "doctor" not in session:
        return redirect(url_for("home"))

    if session.get("editRecordId") != recordId:
        return redirect(url_for("recordsPage"))

    password = session.get("editPassword")

    if not password:
        return redirect(url_for("editPage", recordId=recordId))

    record = getRecord(recordId)

    if record is None:
        return "Patient Record Not Found", 404

    patientId = request.form.get("patientId", "").strip()
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    gender = request.form.get("gender", "").strip()
    disease = request.form.get("disease", "").strip()
    diagnosis = request.form.get("diagnosis", "").strip()
    prescription = request.form.get("prescription", "").strip()

    if not all([
        patientId,
        name,
        age,
        gender,
        disease,
        diagnosis,
        prescription
    ]):
        return "Please fill in all patient fields."

    if patientId != str(record[1]):
        return "Patient ID cannot be changed."

    try:
        ageNumber = int(age)
        if ageNumber <= 0 or ageNumber > 150:
            raise ValueError
    except ValueError:
        return "Please enter a valid age."

    patientData = (
        patientId + "|" +
        name + "|" +
        age + "|" +
        gender + "|" +
        disease + "|" +
        diagnosis + "|" +
        prescription
    )

    try:
        pkg = encrypt_payload(patientData, password)
        newCipherText = pkg.to_json()

        updateRecord(recordId, name, newCipherText)

        session.pop("editPassword", None)
        session.pop("editRecordId", None)

        return redirect(url_for("recordsPage"))

    except Exception as error:
        print("Update Error:", error)
        return "Unable to update patient record."


# =========================================================
# DELETE PATIENT RECORD
# =========================================================

@app.route("/delete/<int:recordId>", methods=["POST"])
def deletePatient(recordId):
    if "doctor" not in session:
        return redirect(url_for("home"))

    record = getRecord(recordId)

    if record is None:
        return "Patient Record Not Found", 404

    try:
        deleteRecord(recordId)

        if session.get("editRecordId") == recordId:
            session.pop("editRecordId", None)
            session.pop("editPassword", None)

        return redirect(url_for("recordsPage"))

    except Exception as error:
        print("Delete Error:", error)
        return "Unable to delete patient record."


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )