from encrypt import encryptRecord
from decrypt import decryptRecord

patientData = "P001|Ravi|22|Fever"

password = "hospital123"

cipher = encryptRecord(patientData, password)

print("Cipher Text")
print(cipher)

print()

plain = decryptRecord(cipher, password)

print("Original Data")
print(plain)