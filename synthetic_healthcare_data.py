"""
Module: synthetic_healthcare_data.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Generates deterministic synthetic healthcare records and datasets (100, 500, 1000 records).
         No real patient data is used.
"""

import csv
import random
from typing import List, Dict, Tuple

DISEASES = [
    "Hypertension", "Type 2 Diabetes", "Asthma", "Arrhythmia", "COVID-19",
    "Influenza A", "Pneumonia", "Hyperlipidemia", "Migraine", "Osteoarthritis"
]

MEDICATIONS = [
    "Amlodipine 5mg", "Metformin 500mg", "Albuterol 90mcg", "Metoprolol 25mg", "Paxlovid",
    "Oseltamivir 75mg", "Amoxicillin 500mg", "Atorvastatin 20mg", "Sumatriptan 50mg", "Ibuprofen 400mg"
]

GENDERS = ["Male", "Female", "Other"]


def generate_synthetic_record(record_idx: int, rng: random.Random) -> Dict[str, str]:
    """Generates a single synthetic patient record dictionary."""
    patient_id = f"P{record_idx + 1000:05d}"
    age = str(rng.randint(18, 92))
    gender = rng.choice(GENDERS)
    sys_bp = rng.randint(95, 160)
    dia_bp = rng.randint(60, 100)
    bp = f"{sys_bp}/{dia_bp}"
    hr = str(rng.randint(58, 105))
    disease = rng.choice(DISEASES)
    medication = rng.choice(MEDICATIONS)
    glucose = str(rng.randint(70, 195))
    temp = f"{rng.uniform(97.2, 101.5):.1f}"
    doctor_id = f"D{rng.randint(10, 99):03d}"
    date = f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"

    return {
        "PatientID": patient_id,
        "Age": age,
        "Gender": gender,
        "BloodPressure": bp,
        "HeartRate": hr,
        "Diagnosis": disease,
        "Medication": medication,
        "Glucose": glucose,
        "Temperature": temp,
        "DoctorID": doctor_id,
        "Date": date,
    }


def record_to_string(record: Dict[str, str]) -> str:
    """Formats synthetic patient record dictionary into pipe-delimited string."""
    return (
        f"{record['PatientID']}|{record['Age']}|{record['Gender']}|{record['BloodPressure']}|"
        f"{record['HeartRate']}|{record['Diagnosis']}|{record['Medication']}|{record['Glucose']}|"
        f"{record['Temperature']}|{record['DoctorID']}|{record['Date']}"
    )


def generate_synthetic_dataset(count: int, seed: int = 20260923) -> List[Dict[str, str]]:
    """Generates a list of count synthetic healthcare record dictionaries."""
    rng = random.Random(seed)
    return [generate_synthetic_record(i, rng) for i in range(count)]


def save_dataset_to_csv(filename: str, records: List[Dict[str, str]]) -> None:
    """Saves synthetic dataset to a CSV file."""
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def create_all_synthetic_datasets(seed: int = 20260923) -> Tuple[str, str, str]:
    """Generates and saves 100, 500, and 1000 synthetic record CSV files."""
    f100 = "synthetic_healthcare_100.csv"
    f500 = "synthetic_healthcare_500.csv"
    f1000 = "synthetic_healthcare_1000.csv"

    save_dataset_to_csv(f100, generate_synthetic_dataset(100, seed))
    save_dataset_to_csv(f500, generate_synthetic_dataset(500, seed))
    save_dataset_to_csv(f1000, generate_synthetic_dataset(1000, seed))

    return f100, f500, f1000


if __name__ == "__main__":
    f100, f500, f1000 = create_all_synthetic_datasets()
    print(f"Generated synthetic datasets: {f100}, {f500}, {f1000}")
