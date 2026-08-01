from flask import Flask, render_template, request, redirect, url_for, session

from database import (
    createDatabase,
    createDefaultDoctor,
    validateDoctor,
    saveRecord,
    showAllRecords,
    getRecord,
    updateRecord,
    deleteRecord
)

from encrypt import encryptRecord
from decrypt import decryptRecord


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

            cipherText = encryptRecord(
                patientData,
                password
            )

            saveRecord(
                patientId,
                name,
                cipherText
            )

            message = "Patient record encrypted and saved successfully."

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

        originalData = decryptRecord(
            cipherText,
            password
        )

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

    # -----------------------------------------------------
    # User entered password
    # -----------------------------------------------------

    if request.method == "POST":

        password = request.form.get("password", "")

        if not password:

            error = "Please enter the encryption password."

        else:

            try:

                originalData = decryptRecord(
                    record[3],
                    password
                )

                data = originalData.split("|")

                if len(data) != 7:

                    error = "Invalid password or unsupported patient record."

                elif data[0] != str(record[1]):

                    error = "Invalid password."

                else:

                    # Password was correct.
                    # Save temporarily so we can re-encrypt
                    # after editing.

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

            except Exception as errorMessage:

                print(
                    "Edit Decryption Error:",
                    errorMessage
                )

                error = "Invalid password or unable to decrypt record."

    # GET request shows password page

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

    # Make sure this is the record that was unlocked
    if session.get("editRecordId") != recordId:

        return redirect(
            url_for("recordsPage")
        )

    password = session.get("editPassword")

    if not password:

        return redirect(
            url_for(
                "editPage",
                recordId=recordId
            )
        )

    record = getRecord(recordId)

    if record is None:
        return "Patient Record Not Found", 404

    # -----------------------------------------------------
    # Get updated values
    # -----------------------------------------------------

    patientId = request.form.get(
        "patientId",
        ""
    ).strip()

    name = request.form.get(
        "name",
        ""
    ).strip()

    age = request.form.get(
        "age",
        ""
    ).strip()

    gender = request.form.get(
        "gender",
        ""
    ).strip()

    disease = request.form.get(
        "disease",
        ""
    ).strip()

    diagnosis = request.form.get(
        "diagnosis",
        ""
    ).strip()

    prescription = request.form.get(
        "prescription",
        ""
    ).strip()

    # -----------------------------------------------------
    # Validate fields
    # -----------------------------------------------------

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

    # Do not allow Patient ID to be changed
    if patientId != str(record[1]):

        return "Patient ID cannot be changed."

    try:

        ageNumber = int(age)

        if ageNumber <= 0 or ageNumber > 150:
            raise ValueError

    except ValueError:

        return "Please enter a valid age."

    # -----------------------------------------------------
    # Build updated patient data
    # -----------------------------------------------------

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

        # Encrypt updated information
        newCipherText = encryptRecord(
            patientData,
            password
        )

        # Update SAME database row
        updateRecord(
            recordId,
            name,
            newCipherText
        )

        # Remove password from session
        session.pop(
            "editPassword",
            None
        )

        session.pop(
            "editRecordId",
            None
        )

        return redirect(
            url_for("recordsPage")
        )

    except Exception as error:

        print(
            "Update Error:",
            error
        )

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

        # Remove edit session if this record was unlocked
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

    return redirect(
        url_for("home")
    )


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