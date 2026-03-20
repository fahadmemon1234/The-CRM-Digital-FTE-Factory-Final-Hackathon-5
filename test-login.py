import requests
import json

url = "http://localhost:8000/api/auth/login"
data = {
    "email": "admin@techcorp.com",
    "password": "admin123"
}

try:
    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ Login successful!")
        print(f"Token: {result['access_token'][:50]}...")
        print(f"User: {result['user']['name']} ({result['user']['email']})")
    else:
        print(f"\n✗ Login failed with status {response.status_code}")
        try:
            error = response.json()
            print(f"Error: {error}")
        except:
            print(f"Raw error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
