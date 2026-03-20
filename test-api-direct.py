import sys
import asyncio
from fastapi.testclient import TestClient
from production.api.main import app

client = TestClient(app)

def test_login():
    try:
        response = client.post(
            "/api/auth/login",
            json={"email": "admin@techcorp.com", "password": "admin123"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✓ Login successful!")
            data = response.json()
            print(f"Token: {data['access_token'][:50]}...")
            print(f"User: {data['user']['name']}")
        else:
            print(f"\n✗ Login failed")
            try:
                print(f"Error JSON: {response.json()}")
            except:
                print(f"Raw: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login()
