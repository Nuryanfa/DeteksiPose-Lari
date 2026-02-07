import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def login(email, password):
    resp = requests.post(f"{BASE_URL}/login/access-token", data={"username": email, "password": password})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    print(f"Login failed for {email}: {resp.text}")
    return None

def test_list_athletes(token, role_name):
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\n[TEST] {role_name} attempting to LIST ATHLETES:")
    resp = requests.get(f"{BASE_URL}/users/athletes", headers=headers)
    if resp.status_code == 200:
        print(f"✅ PASSED: {role_name} can view athletes.")
    elif resp.status_code == 403:
        print(f"🛡️ SECURED: {role_name} correctly BLOCKED from viewing athletes.")
    else:
        print(f"❌ FAIL: Unexpected status {resp.status_code}")

def test_view_history(token, role_name, target_user_id=1):
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\n[TEST] {role_name} attempting to VIEW OTHERS HISTORY (ID={target_user_id}):")
    resp = requests.get(f"{BASE_URL}/history/?user_id={target_user_id}", headers=headers)
    if resp.status_code == 200:
        # If athlete, this implies failure (unless viewing self)
        # If coach/mgmt, this implies success
        if role_name == "Athlete":
             print(f"❌ FAIL: {role_name} could view other's history!")
        else:
             print(f"✅ PASSED: {role_name} can view specific history.")
    elif resp.status_code == 403:
        if role_name == "Athlete":
            print(f"🛡️ SECURED: {role_name} correctly BLOCKED from other's history.")
        else:
            print(f"❌ FAIL: {role_name} was blocked but shouldn't be.")
    else:
        print(f"❓ INFO: Status {resp.status_code} (User might not exist or other error)")

def get_me(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if resp.status_code == 200:
        return resp.json()["id"]
    return None

def get_first_athlete_id(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/users/athletes", headers=headers)
    if resp.status_code == 200:
        users = resp.json()
        if users: return users[0]["id"]
    return 999 

def run_tests():
    print("=== STARTING RBAC VERIFICATION ===")
    
    # 1. Management Test
    print("\n--- Testing Management Role ---")
    token_mgmt = login("koni@ssts.com", "konipassword")
    mgmt_id = get_me(token_mgmt)
    print(f"Logged in as Management (ID: {mgmt_id})")
    
    if token_mgmt:
        test_list_athletes(token_mgmt, "Management") # Should Pass
        athlete_id = get_first_athlete_id(token_mgmt)
        print(f"Found Athlete ID: {athlete_id}")
        test_view_history(token_mgmt, "Management", target_user_id=athlete_id) # Should Pass

    # 2. Athlete Test
    print("\n--- Testing Athlete Role ---")
    token_athlete = login("atlet@ssts.com", "atletpassword")
    if token_athlete:
        test_list_athletes(token_athlete, "Athlete") # Should Fail
        test_view_history(token_athlete, "Athlete", target_user_id=mgmt_id) # Should Fail (Spying on Mgmt)

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"Test Error: {e}")
