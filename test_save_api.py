
import httpx
import time

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@ssts.com"
PASSWORD = "admin"

def test_save():
    print("Logging in...")
    try:
        resp = httpx.post(f"{BASE_URL}/login/access-token", data={"username": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        token = resp.json()["access_token"]
        
        print("Saving session...")
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "duration_seconds": 5.0,
            "technique_score": 90.0,
            "avg_cadence": 170,
            "avg_stride_length": 1.1,
            "avg_gct": 200,
            "max_swing_error": 0,
            "max_hip_error": 0,
            "video_path": "api_test.mp4"
        }
        resp = httpx.post(f"{BASE_URL}/history/save", json=data, headers=headers)
        if resp.status_code == 200:
            print(f"✅ API Save SUCCESS: ID {resp.json()['id']}")
        else:
            print(f"❌ API Save FAILED: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_save()
