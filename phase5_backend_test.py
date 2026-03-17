import requests
import sys
import uuid
import time
import json
from datetime import datetime

class Phase5DynamicDataTester:
    def __init__(self, base_url="https://dragon-quest-46.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failures = []
        self.test_token = None

    def log_result(self, test_name, success, message=""):
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: {message}")
        else:
            print(f"❌ {test_name}: {message}")
            self.failures.append(f"{test_name}: {message}")

    def make_request(self, method, endpoint, data=None, auth=False):
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if auth and self.test_token:
            headers['Authorization'] = f'Bearer {self.test_token}'
            
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def test_real_leaderboard_data(self):
        """Test that leaderboard returns real user data sorted correctly"""
        print(f"\n🏆 Testing Real Leaderboard Data...")
        
        response = self.make_request('GET', 'leaderboard')
        if not response or response.status_code != 200:
            self.log_result("Leaderboard API Call", False, f"Status: {response.status_code if response else 'No response'}")
            return False
            
        leaderboard = response.json()
        
        # Check if leaderboard has real users (should have some data since we registered users in backend test)
        has_real_users = len(leaderboard) > 0
        self.log_result("Leaderboard has real users", has_real_users, f"Found {len(leaderboard)} users")
        
        if has_real_users:
            # Check that users are sorted by level, then by XP
            for i in range(1, len(leaderboard)):
                current = leaderboard[i-1]
                next_user = leaderboard[i]
                
                level_order_correct = (current['level'] >= next_user['level'])
                if current['level'] == next_user['level']:
                    xp_order_correct = (current['xp'] >= next_user['xp'])
                else:
                    xp_order_correct = True
                    
                if not (level_order_correct and xp_order_correct):
                    self.log_result("Leaderboard sort order", False, f"User at rank {i} not properly sorted")
                    return False
                    
            self.log_result("Leaderboard sort order", True, "Users sorted correctly by level/XP")
            
            # Check that users have real data structure
            first_user = leaderboard[0]
            required_fields = ['rank', 'username', 'level', 'xp', 'path_choice', 'path_label']
            missing_fields = [field for field in required_fields if field not in first_user]
            
            if missing_fields:
                self.log_result("Leaderboard data structure", False, f"Missing fields: {missing_fields}")
                return False
            else:
                self.log_result("Leaderboard data structure", True, "All required fields present")
                
        return True

    def test_real_online_stats(self):
        """Test that online counter shows real activity"""
        print(f"\n🌐 Testing Real Online Stats...")
        
        response = self.make_request('GET', 'stats/online')
        if not response or response.status_code != 200:
            self.log_result("Online Stats API Call", False, f"Status: {response.status_code if response else 'No response'}")
            return False
            
        online_stats = response.json()
        
        # Check structure
        required_fields = ['now', 'last_hour', 'last_24h', 'total']
        missing_fields = [field for field in required_fields if field not in online_stats]
        
        if missing_fields:
            self.log_result("Online stats structure", False, f"Missing fields: {missing_fields}")
            return False
            
        self.log_result("Online stats structure", True, "All required fields present")
        
        # Check that we have some registered users
        total_users = online_stats['total']
        self.log_result("Has registered users", total_users > 0, f"Total users: {total_users}")
        
        # Logical consistency checks
        consistency_ok = (
            online_stats['now'] <= online_stats['last_hour'] and
            online_stats['last_hour'] <= online_stats['last_24h'] and 
            online_stats['last_24h'] <= online_stats['total']
        )
        
        self.log_result("Online stats logical consistency", consistency_ok, 
                       f"now:{online_stats['now']}, hour:{online_stats['last_hour']}, day:{online_stats['last_24h']}, total:{online_stats['total']}")
        
        return True

    def test_real_ticker_events(self):
        """Test that ticker shows real logged events"""
        print(f"\n📜 Testing Real Ticker Events...")
        
        response = self.make_request('GET', 'ticker')
        if not response or response.status_code != 200:
            self.log_result("Ticker API Call", False, f"Status: {response.status_code if response else 'No response'}")
            return False
            
        ticker = response.json()
        
        # Check if we have real events (should have some from user registrations)
        has_events = len(ticker) > 0
        self.log_result("Ticker has real events", has_events, f"Found {len(ticker)} events")
        
        if has_events:
            # Check event structure
            first_event = ticker[0]
            required_fields = ['event', 'type', 'created_at']
            missing_fields = [field for field in required_fields if field not in first_event]
            
            if missing_fields:
                self.log_result("Ticker event structure", False, f"Missing fields: {missing_fields}")
                return False
                
            self.log_result("Ticker event structure", True, "Events have correct structure")
            
            # Check for real registration/login events
            real_event_types = ['quest', 'combat']  # register = quest, login = combat
            has_real_event_types = any(event['type'] in real_event_types for event in ticker)
            self.log_result("Has real event types", has_real_event_types, "Found registration/login events")
            
        return True

    def test_user_registration_creates_events(self):
        """Test that registering a new user creates ticker events and updates leaderboard"""
        print(f"\n👤 Testing User Registration Impact...")
        
        # Get baseline data
        baseline_leaderboard = self.make_request('GET', 'leaderboard').json()
        baseline_ticker = self.make_request('GET', 'ticker').json()
        baseline_online = self.make_request('GET', 'stats/online').json()
        
        baseline_user_count = len(baseline_leaderboard)
        baseline_event_count = len(baseline_ticker)
        baseline_total_users = baseline_online['total']
        
        # Register a new user
        timestamp = datetime.now().strftime('%H%M%S')
        new_user = {
            "username": f"phase5_test_{timestamp}",
            "email": f"phase5test_{timestamp}@aethoria.realm",
            "password": "TestPass123!",
            "path_choice": "noble"
        }
        
        register_response = self.make_request('POST', 'auth/register', new_user)
        if not register_response or register_response.status_code != 200:
            self.log_result("New user registration", False, f"Registration failed: {register_response.status_code if register_response else 'No response'}")
            return False
            
        self.log_result("New user registration", True, f"User {new_user['username']} registered successfully")
        
        # Wait a moment for data to propagate
        time.sleep(2)
        
        # Check updated leaderboard
        new_leaderboard = self.make_request('GET', 'leaderboard').json()
        new_user_count = len(new_leaderboard)
        
        leaderboard_updated = new_user_count > baseline_user_count
        self.log_result("Leaderboard updated after registration", leaderboard_updated, 
                       f"User count: {baseline_user_count} -> {new_user_count}")
        
        # Check updated ticker
        new_ticker = self.make_request('GET', 'ticker').json()
        new_event_count = len(new_ticker)
        
        ticker_updated = new_event_count > baseline_event_count
        self.log_result("Ticker updated after registration", ticker_updated,
                       f"Event count: {baseline_event_count} -> {new_event_count}")
        
        # Check updated online count
        new_online = self.make_request('GET', 'stats/online').json()
        new_total_users = new_online['total']
        
        total_users_updated = new_total_users > baseline_total_users  
        self.log_result("Total user count updated", total_users_updated,
                       f"Total users: {baseline_total_users} -> {new_total_users}")
        
        # Store token for later tests
        if register_response:
            register_data = register_response.json()
            self.test_token = register_data.get('token')
            
        return True

    def test_reviews_system(self):
        """Test review submission and retrieval"""
        print(f"\n⭐ Testing Reviews System...")
        
        if not self.test_token:
            self.log_result("Review system test", False, "No authentication token available")
            return False
            
        # Get baseline reviews
        baseline_reviews = self.make_request('GET', 'reviews').json()
        baseline_count = len(baseline_reviews)
        
        # Submit a review
        review_data = {
            "rating": 5,
            "text": "This is a comprehensive Phase 5 test review to validate the real dynamic review system is working correctly!"
        }
        
        review_response = self.make_request('POST', 'reviews', review_data, auth=True)
        
        if not review_response or review_response.status_code != 200:
            self.log_result("Review submission", False, f"Status: {review_response.status_code if review_response else 'No response'}")
            return False
            
        self.log_result("Review submission", True, "Review submitted successfully")
        
        # Wait for data to propagate
        time.sleep(1)
        
        # Check updated reviews
        new_reviews = self.make_request('GET', 'reviews').json()
        new_count = len(new_reviews)
        
        reviews_updated = new_count > baseline_count
        self.log_result("Reviews list updated", reviews_updated, f"Review count: {baseline_count} -> {new_count}")
        
        if reviews_updated:
            # Check review structure
            latest_review = new_reviews[0]  # Should be sorted by created_at desc
            required_fields = ['author', 'rating', 'text', 'date']
            missing_fields = [field for field in required_fields if field not in latest_review]
            
            if missing_fields:
                self.log_result("Review data structure", False, f"Missing fields: {missing_fields}")
                return False
                
            self.log_result("Review data structure", True, "Review has correct structure")
            
            # Test duplicate review prevention
            duplicate_response = self.make_request('POST', 'reviews', review_data, auth=True)
            duplicate_prevented = duplicate_response and duplicate_response.status_code == 400
            self.log_result("Duplicate review prevention", duplicate_prevented, "Duplicate review correctly rejected")
            
        return True

    def test_empty_states_behavior(self):
        """Test that API returns appropriate empty states when no data exists"""
        print(f"\n🔄 Testing Empty States...")
        
        # For Phase 5, all mock data has been removed, so we should test the behavior
        # when collections are empty vs when they have real data
        
        # Test that endpoints return valid empty arrays/objects rather than errors
        response = self.make_request('GET', 'landing')
        if not response or response.status_code != 200:
            self.log_result("Landing page with real data", False, "Landing endpoint failed")
            return False
            
        landing_data = response.json()
        
        # Verify all sections exist even if empty
        required_sections = ['ticker', 'features', 'leaderboard', 'reviews', 'news', 'paths', 'kingdoms', 'online']
        missing_sections = [section for section in required_sections if section not in landing_data]
        
        if missing_sections:
            self.log_result("Landing data completeness", False, f"Missing sections: {missing_sections}")
            return False
            
        self.log_result("Landing data completeness", True, "All sections present in landing data")
        
        # Test that arrays are proper arrays (not null)
        array_sections = ['ticker', 'features', 'leaderboard', 'reviews', 'news', 'paths', 'kingdoms']
        for section in array_sections:
            if not isinstance(landing_data[section], list):
                self.log_result(f"{section} data type", False, f"{section} is not an array")
                return False
                
        self.log_result("Data type consistency", True, "All array sections are proper arrays")
        
        return True

    def run_phase5_tests(self):
        """Run all Phase 5 specific tests"""
        print("🌟 Starting Phase 5 Dynamic Data Tests...")
        print("Testing conversion from placeholder to real dynamic data...")
        
        # Test real data systems
        self.test_real_leaderboard_data()
        self.test_real_online_stats() 
        self.test_real_ticker_events()
        self.test_user_registration_creates_events()
        self.test_reviews_system()
        self.test_empty_states_behavior()
        
        # Summary
        print(f"\n📊 Phase 5 Test Results:")
        print(f"Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.failures:
            print("\n❌ Failed Tests:")
            for failure in self.failures:
                print(f"  - {failure}")
        else:
            print("\n🎉 All Phase 5 dynamic data features working correctly!")
        
        return self.tests_passed == self.tests_run

def main():
    tester = Phase5DynamicDataTester()
    success = tester.run_phase5_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())