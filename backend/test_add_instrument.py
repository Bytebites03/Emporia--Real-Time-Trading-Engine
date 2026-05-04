# test_add_instrument.py
import requests
import json

# First login as admin
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "admin123"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit()

token = login_response.json()['access_token']
print(f"✅ Logged in, token: {token[:50]}...")

# Add an instrument
headers = {"Authorization": f"Bearer {token}"}
params = {
    "ticker_symbol": "TEST/USD",
    "instrument_name": "Test Coin",
    "instrument_type": "crypto",
    "exchange": "TestEx",
    "initial_price": 100
}

response = requests.post(
    "http://localhost:8000/instrument/add",
    params=params,
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")