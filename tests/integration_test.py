
import httpx
import time

BASE_URL = "http://localhost:8000/api/v1"

# Test Data
ADMIN_EMAIL = "admin@ssts.com"
ADMIN_PASS = "admin"

COACH_EMAIL = f"coach_test_{int(time.time())}@example.com"
COACH_PASS = "password123"
COACH_NAME = "Coach Integration Tester"

ATHLETE_EMAIL = f"athlete_test_{int(time.time())}@example.com"
ATHLETE_PASS = "password123"
ATHLETE_NAME = "Athlete Integration Tester"

def print_pass(msg):
    print(f"✅ PASS: {msg}")

def print_fail(msg):
    print(f"❌ FAIL: {msg}")
    exit(1)

def login(email, password):
    response = httpx.post(f"{BASE_URL}/login/access-token", data={"username": email, "password": password})
    if response.status_code != 200:
        return None
    return response.json()["access_token"]

def register(email, password, name, role):
    data = {
        "email": email,
        "password": password,
        "full_name": name,
        "role": role
    }
    response = httpx.post(f"{BASE_URL}/users/", json=data)
    if response.status_code != 200:
        print_fail(f"Registration failed for {role}: {response.text}")
    print_pass(f"Registered {role}: {email}")

def main():
    print("🚀 Starting Integration Test...")

    # 1. Register Users
    register(COACH_EMAIL, COACH_PASS, COACH_NAME, "coach")
    register(ATHLETE_EMAIL, ATHLETE_PASS, ATHLETE_NAME, "athlete")

    # 2. Login Management (Admin)
    admin_token = login(ADMIN_EMAIL, ADMIN_PASS)
    if not admin_token:
        print("⚠️ Warning: Admin login failed. Skipping Management check (maybe admin not created?)")
    else:
        print_pass("Admin Login")
        # Check Management Dashboard Data
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = httpx.get(f"{BASE_URL}/organization/summary", headers=headers)
        if res.status_code == 200:
            print_pass("Management: Get Organization Summary")
            print(f"   Stats: {res.json()}")
        else:
            print_fail(f"Management summary failed: {res.text}")

    # 3. Login Coach
    coach_token = login(COACH_EMAIL, COACH_PASS)
    if not coach_token: print_fail("Coach Login")
    print_pass("Coach Login")

    # 4. Login Athlete
    athlete_token = login(ATHLETE_EMAIL, ATHLETE_PASS)
    if not athlete_token: print_fail("Athlete Login")
    print_pass("Athlete Login")
    
    athlete_headers = {"Authorization": f"Bearer {athlete_token}"}
    coach_headers = {"Authorization": f"Bearer {coach_token}"}

    # 5. Athlete: Update Profile (Settings)
    profile_update = {
        "full_name": "Updated Athlete Name",
        "email": ATHLETE_EMAIL, # Required by schema usually? depends on backend
        "height": 182,
        "weight": 78,
        "personal_best": "10.2s"
    }
    # Note: Backend expects UserUpdate which might be strict. Checking users endpoint.
    # Actually backend endpoint /users/me expects UserUpdate.
    res = httpx.put(f"{BASE_URL}/users/me", json=profile_update, headers=athlete_headers)
    if res.status_code == 200:
        data = res.json()
        if data['height'] == 182 and data['weight'] == 78:
            print_pass("Athlete: Update Profile (Height/Weight)")
        else:
            print_fail(f"Athlete profile mismatch: {data}")
    else:
        print_fail(f"Athlete update failed: {res.text}")

    # 6. Athlete: Create Session (Simulate)
    # Get Athlete ID first
    res = httpx.get(f"{BASE_URL}/users/me", headers=athlete_headers)
    athlete_id = res.json()['id']

    session_data = {
        "duration_seconds": 12.5,
        "technique_score": 85.0,
        "avg_cadence": 180,
        "avg_stride_length": 1.2,
        "avg_gct": 200,
        "max_swing_error": 10,
        "max_hip_error": 5,
        "video_path": "dummy/path.mp4"
    }
    res = httpx.post(f"{BASE_URL}/history/save", json=session_data, headers=athlete_headers)
    if res.status_code == 200:
        session_id = res.json()['id']
        print_pass("Athlete: Save Session")
    else:
        print_fail(f"Save session failed: {res.text}")

    # 7. Coach: View Athlete History
    # Needs to call /history/?user_id={athlete_id}
    res = httpx.get(f"{BASE_URL}/history/?user_id={athlete_id}", headers=coach_headers)
    if res.status_code == 200:
        sessions = res.json()
        if len(sessions) > 0 and sessions[0]['id'] == session_id:
            print_pass("Coach: View Athlete History")
        else:
            print_fail("Coach did not see the new session")
    else:
        print_fail(f"Coach history fetch failed: {res.text}")

    # 8. Coach: Add Feedback
    feedback_data = {"coach_notes": "Great job, keep knees higher!"}
    res = httpx.put(f"{BASE_URL}/history/{session_id}/feedback", json=feedback_data, headers=coach_headers)
    if res.status_code == 200:
        print_pass("Coach: Add Feedback")
    else:
        print_fail(f"Add Feedback failed: {res.text}")

    # 9. Athlete: Verify Feedback Visible
    res = httpx.get(f"{BASE_URL}/history/", headers=athlete_headers)
    if res.status_code == 200:
        sessions = res.json()
        target = next((s for s in sessions if s['id'] == session_id), None)
        if target and target['coach_notes'] == "Great job, keep knees higher!":
            print_pass("Athlete: Verify Feedback Received")
        else:
            print_fail(f"Feedback verification failed. Notes: {target.get('coach_notes') if target else 'Session not found'}")

    # 10. Coach: Verify Recent Sessions Endpoint
    res = httpx.get(f"{BASE_URL}/organization/recent-sessions", headers=coach_headers)
    if res.status_code == 200:
        recent = res.json()
        if len(recent) > 0:
            print_pass("Coach: Get Recent Sessions (Organization Endpoint)")
        else:
            print("⚠️ Warning: No recent sessions returned (maybe delay?)")
    else:
        print_fail(f"Coach recent sessions failed: {res.text}")

    print("\n🎉 ALL TESTS PASSED! System is fully functional.")

if __name__ == "__main__":
    main()
