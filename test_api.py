#!/usr/bin/env python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Test 1: Get Doctor Token
print("\n=== Test 1: Get Doctor Token ===")
token_response = requests.post(
    f"{BASE_URL}/token/",
    json={"email": "doctor1@test.com", "password": "password123"}
)
print(f"Status: {token_response.status_code}")
doctor_token = token_response.json().get("access")
print(f"Doctor Token: {doctor_token[:50]}...")

# Test 2: Get Patient Token
print("\n=== Test 2: Get Patient Token ===")
token_response = requests.post(
    f"{BASE_URL}/token/",
    json={"email": "patient1@test.com", "password": "password123"}
)
print(f"Status: {token_response.status_code}")
patient_token = token_response.json().get("access")
print(f"Patient Token: {patient_token[:50]}...")

# Test 3: Doctor views their patients (my-patients endpoint)
print("\n=== Test 3: Doctor GET /appointments/my-patients/ ===")
headers = {"Authorization": f"Bearer {doctor_token}"}
response = requests.get(f"{BASE_URL}/appointments/my-patients/", headers=headers)
print(f"Status: {response.status_code}")
patients_data = response.json()
print(f"Response: {json.dumps(patients_data, indent=2)[:500]}...")

# Test 4: Patient views their medical records (my-medical-records endpoint)
print("\n=== Test 4: Patient GET /appointments/my-medical-records/ ===")
headers = {"Authorization": f"Bearer {patient_token}"}
response = requests.get(f"{BASE_URL}/appointments/my-medical-records/", headers=headers)
print(f"Status: {response.status_code}")
records_data = response.json()
print(f"Response: {json.dumps(records_data, indent=2)[:500]}...")

print("\n=== All Tests Complete ===")
