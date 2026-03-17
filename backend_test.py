import requests
import sys
import uuid
from datetime import datetime

class AethoriaAPITester:
    def __init__(self, base_url="https://dragon-quest-46.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failures = []

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Validate response content for key endpoints
                if endpoint == "landing":
                    data = response.json()
                    required_fields = ['ticker', 'features', 'leaderboard', 'reviews', 'news', 'paths', 'online']
                    for field in required_fields:
                        if field not in data:
                            print(f"⚠️  Warning: Missing {field} in landing data")
                        else:
                            print(f"✓ {field} present in response")
                    
                    # Check if features count is 42
                    if 'features' in data and len(data['features']) == 42:
                        print("✓ Correct number of features (42)")
                    else:
                        print(f"⚠️  Expected 42 features, got {len(data.get('features', []))}")
                        
                elif endpoint == "features":
                    features = response.json()
                    if len(features) == 42:
                        print("✓ Correct number of features (42)")
                    else:
                        print(f"⚠️  Expected 42 features, got {len(features)}")
                        
                elif endpoint == "leaderboard":
                    leaderboard = response.json()
                    if len(leaderboard) == 10:
                        print("✓ Correct number of leaderboard entries (10)")
                    else:
                        print(f"⚠️  Expected 10 leaderboard entries, got {len(leaderboard)}")
                        
                return True, response.json() if response.content else {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                print(f"❌ Failed - {error_msg}")
                self.failures.append(f"{name}: {error_msg}")
                return False, {}

        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            print(f"❌ Failed - {error_msg}")
            self.failures.append(f"{name}: {error_msg}")
            return False, {}
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"❌ Failed - {error_msg}")
            self.failures.append(f"{name}: {error_msg}")
            return False, {}

    def test_register_user(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_user = {
            "username": f"test_knight_{timestamp}",
            "email": f"test_{timestamp}@aethoria.realm",
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_user
        )
        
        if success and response.get('success'):
            print(f"✓ Registration successful for {test_user['username']}")
            return test_user
        else:
            print(f"❌ Registration failed")
            return None

    def test_register_with_path(self):
        """Test user registration with path selection"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_user = {
            "username": f"test_shadow_{timestamp}",
            "email": f"testshadow_{timestamp}@aethoria.realm", 
            "password": "TestPass123!",
            "path_choice": "shadow"
        }
        
        success, response = self.run_test(
            "User Registration with Path Selection",
            "POST",
            "auth/register",
            200,
            data=test_user
        )
        
        if success and response.get('success'):
            print(f"✓ Registration with shadow path successful for {test_user['username']}")
            # Validate that user has correct path stats
            user_data = response.get('user', {})
            if user_data.get('path_choice') == 'shadow':
                print(f"✓ Path choice correctly set to shadow")
            if user_data.get('dexterity', 0) == 14:  # Shadow path starts with 14 dexterity
                print(f"✓ Path stats correctly applied (dexterity: 14)")
            return test_user
        else:
            print(f"❌ Registration with path failed")
            return None

    def test_login_user(self, user_credentials):
        """Test user login"""
        if not user_credentials:
            return False
            
        login_data = {
            "email": user_credentials["email"],
            "password": user_credentials["password"]
        }
        
        success, response = self.run_test(
            "User Login",
            "POST", 
            "auth/login",
            200,
            data=login_data
        )
        
        if success and response.get('success'):
            print(f"✓ Login successful for {user_credentials['username']}")
            return True
        else:
            print(f"❌ Login failed")
            return False

    def run_all_tests(self):
        """Run complete backend test suite"""
        print("🏰 Starting Realm of Aethoria Backend Tests...")
        
        # Test main aggregated endpoint
        self.run_test("Landing Data", "GET", "landing", 200)
        
        # Test individual endpoints
        self.run_test("Event Ticker", "GET", "ticker", 200)
        self.run_test("Features List", "GET", "features", 200)
        self.run_test("Leaderboard", "GET", "leaderboard", 200)
        self.run_test("Reviews", "GET", "reviews", 200)
        self.run_test("News", "GET", "news", 200)
        self.run_test("Paths", "GET", "paths", 200)
        self.run_test("Kingdoms", "GET", "kingdoms", 200)
        self.run_test("Online Stats", "GET", "stats/online", 200)
        
        # Test authentication
        test_user = self.test_register_user()
        if test_user:
            self.test_login_user(test_user)
        
        # Test registration with path selection
        test_shadow_user = self.test_register_with_path()
        
        # Test duplicate registration (should fail)
        if test_user:
            success, response = self.run_test(
                "Duplicate Registration (Expected Failure)",
                "POST",
                "auth/register", 
                400,
                data=test_user
            )
        
        # Test login with wrong credentials (should fail) 
        wrong_creds = {
            "email": "nonexistent@aethoria.realm",
            "password": "wrongpass"
        }
        self.run_test(
            "Invalid Login (Expected Failure)",
            "POST",
            "auth/login",
            401,
            data=wrong_creds
        )
        
        # Test JWT /me endpoint with valid token
        if test_user:
            success, login_response = self.run_test(
                "Get Valid JWT Token",
                "POST",
                "auth/login",
                200,
                data={
                    "email": test_user["email"],
                    "password": test_user["password"]
                }
            )
            
            if success and 'token' in login_response:
                token = login_response['token']
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
                
                # Test protected /me endpoint
                url = f"{self.base_url}/api/me"
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        self.tests_passed += 1
                        print(f"✅ JWT /me endpoint - Status: 200")
                        me_data = response.json()
                        if 'user' in me_data and me_data['user']['username'] == test_user['username']:
                            print(f"✓ JWT authentication working - user data correct")
                        else:
                            print(f"⚠️  JWT user data mismatch")
                    else:
                        print(f"❌ JWT /me endpoint failed - Status: {response.status_code}")
                        self.failures.append(f"JWT /me endpoint: Expected 200, got {response.status_code}")
                    self.tests_run += 1
                except Exception as e:
                    print(f"❌ JWT /me endpoint failed - Error: {str(e)}")
                    self.failures.append(f"JWT /me endpoint: {str(e)}")
                    self.tests_run += 1
        
        # Print results
        print(f"\n📊 Backend Test Results:")
        print(f"Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.failures:
            print("\n❌ Failed Tests:")
            for failure in self.failures:
                print(f"  - {failure}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AethoriaAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())