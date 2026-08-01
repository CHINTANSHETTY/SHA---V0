from encrypt import encryptRecord
from decrypt import decryptRecord


patientData = (
    "05|Rahul|21|Male|Fever|"
    "Viral Fever|Paracetamol"
)

password = "1234"


print("ORIGINAL:")
print(patientData)


cipherText = encryptRecord(
    patientData,
    password
)

print("\nENCRYPTED:")
print(cipherText)


decryptedText = decryptRecord(
    cipherText,
    password
)

print("\nDECRYPTED:")
print(decryptedText)


print("\nMATCH:")
print(patientData == decryptedText)