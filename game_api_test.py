#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Realm of Aethoria
Focuses on game endpoints that frontend expects vs backend reality
"""

import requests
import json
import time
from datetime import datetime

class GameAPITester:
    def __init__(self):
        self.base_url = "https://dragon-quest-46.preview.emergentagent.com/api"
        self.token = None
        self.user_id = None
        self.username = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.api_mismatches = []

    def log_test(self, name, method, endpoint, expected_status, actual_status, success, details=None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - {method} {endpoint} - Status: {actual_status}")
        else:
            self.failed_tests.append({
                'name': name,
                'method': method,
                'endpoint': endpoint,
                'expected_status': expected_status,
                'actual_status': actual_status,
                'details': details
            })
            print(f"❌ {name} - {method} {endpoint} - Expected {expected_status}, got {actual_status}")
            if details:
                print(f"   Details: {details}")

    def log_api_mismatch(self, feature, frontend_expectation, backend_reality, impact):
        """Log API mismatches found"""
        mismatch = {
            'feature': feature,
            'frontend_expectation': frontend_expectation,
            'backend_reality': backend_reality,
            'impact': impact
        }
        self.api_mismatches.append(mismatch)
        print(f"🔥 API MISMATCH - {feature}:")
        print(f"   Frontend expects: {frontend_expectation}")
        print(f"   Backend provides: {backend_reality}")
        print(f"   Impact: {impact}")

    def make_request(self, method, endpoint, data=None):
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return None

    def setup_test_user(self):
        """Create test user for authenticated endpoints"""
        print("\n🔐 Setting up test user...")
        
        timestamp = str(int(time.time()))
        self.username = f"test_user_{timestamp}"
        test_email = f"test_{timestamp}@example.com"
        test_password = "TestPass123!"

        # Register user
        register_data = {
            "username": self.username,
            "email": test_email,
            "password": test_password,
            "path_choice": "knight"
        }
        
        response = self.make_request('POST', '/auth/register', register_data)
        if response and response.status_code == 200:
            self.token = response.json().get('token')
            self.user_id = response.json().get('user', {}).get('id')
            print(f"✅ Test user created: {self.username}")
            return True
        else:
            print(f"❌ Failed to create test user: {response.status_code if response else 'No response'}")
            return False

    def test_training_system(self):
        """Test training system - CRITICAL API MISMATCH"""
        print("\n💪 Testing Training System (CRITICAL)...")
        
        # Test what TrainingPage.jsx expects - direct stat endpoints
        for stat in ['strength', 'dexterity', 'speed', 'defense']:
            response = self.make_request('POST', f'/game/training/{stat}')
            if response:
                if response.status_code == 404:
                    self.log_api_mismatch(
                        f"Training {stat}",
                        f"Direct POST /api/game/training/{stat} endpoint",
                        "No such endpoint exists",
                        "CRITICAL - Training page cannot train stats directly"
                    )
                self.log_test(f"Direct {stat} Training (Frontend Expected)", "POST", 
                             f"/game/training/{stat}", 200, response.status_code, False)

        # Test what backend actually provides - timer system
        start_data = {"stat": "strength"}
        response = self.make_request('POST', '/game/training/start', start_data)
        success = response and response.status_code == 200
        self.log_test("Training Start (Backend Reality)", "POST", "/game/training/start", 
                     200, response.status_code if response else 0, success)

        response = self.make_request('GET', '/game/training/status')
        success = response and response.status_code == 200
        self.log_test("Training Status", "GET", "/game/training/status", 
                     200, response.status_code if response else 0, success)

        response = self.make_request('POST', '/game/training/claim')
        # Should fail due to timer, but endpoint should exist
        if response and response.status_code == 400:
            self.log_test("Training Claim", "POST", "/game/training/claim", 
                         400, response.status_code, True)

    def test_game_state(self):
        """Test game state structure"""
        print("\n🎮 Testing Game State...")
        
        response = self.make_request('GET', '/game/state')
        if response and response.status_code == 200:
            game_data = response.json()
            self.log_test("Game State", "GET", "/game/state", 200, response.status_code, True)
            
            # Check structure for frontend compatibility
            expected_fields = ['user', 'resources', 'stats', 'location', 'equipment', 'timers']
            missing_fields = []
            for field in expected_fields:
                if field not in game_data:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_api_mismatch("Game State Structure",
                                    f"Fields {expected_fields} in gameState",
                                    f"Missing fields: {missing_fields}",
                                    "HIGH - Frontend may break")
                                    
            # Check if character field exists (mentioned in review)
            if 'character' in game_data:
                print("⚠️  gameState.character field found - should be gameState.user")
                self.log_api_mismatch("Game State Character Field",
                                    "gameState.user for user data",
                                    "gameState.character present",
                                    "MEDIUM - Code should use gameState.user")
        else:
            self.log_test("Game State", "GET", "/game/state", 200, 
                         response.status_code if response else 0, False)

    def test_crimes_system(self):
        """Test crimes system"""
        print("\n🗡️ Testing Crimes System...")
        
        response = self.make_request('GET', '/game/crimes')
        success = response and response.status_code == 200
        self.log_test("Get Crimes", "GET", "/game/crimes", 
                     200, response.status_code if response else 0, success)

        # Test specific crime endpoint that might be expected
        crime_id = "steal_bread"
        response = self.make_request('GET', f'/game/crimes/{crime_id}')
        if response and response.status_code == 404:
            self.log_api_mismatch("Individual Crime Info",
                                f"GET /api/game/crimes/{crime_id} endpoint",
                                "No individual crime endpoint",
                                "LOW - Can get from list")
        
        # Test committing crime (actual endpoint)
        crime_data = {"crime_id": crime_id}
        response = self.make_request('POST', '/game/crimes/commit', crime_data)
        success = response and response.status_code == 200
        self.log_test("Commit Crime", "POST", "/game/crimes/commit", 
                     200, response.status_code if response else 0, success)

    def test_combat_system(self):
        """Test combat system"""
        print("\n⚔️ Testing Combat System...")
        
        # Test attack endpoint format
        target_username = "nonexistent_user"
        response = self.make_request('POST', f'/game/attack/{target_username}')
        if response and response.status_code == 404:
            self.log_api_mismatch("Combat Attack Format",
                                f"POST /api/game/attack/{{target_user_id}} endpoint",
                                "Different endpoint structure or missing",
                                "HIGH - Combat page may not work")
        
        # Check what combat endpoints exist
        response = self.make_request('GET', '/game/combat/logs')
        success = response and response.status_code == 200
        self.log_test("Combat Logs", "GET", "/game/combat/logs", 
                     200, response.status_code if response else 0, success)

    def test_shop_system(self):
        """Test shop system"""
        print("\n🛍️ Testing Shop System...")
        
        response = self.make_request('GET', '/game/shop/items')
        success = response and response.status_code == 200
        self.log_test("Shop Items", "GET", "/game/shop/items", 
                     200, response.status_code if response else 0, success)

        # Test buy endpoint format from frontend code
        item_id = "sword_iron"
        response = self.make_request('POST', f'/game/shop/buy?item_id={item_id}&quantity=1')
        if response and response.status_code == 404:
            # Check if it needs different format
            buy_data = {"item_id": item_id, "quantity": 1}
            response2 = self.make_request('POST', '/game/shop/buy', buy_data)
            if response2:
                self.log_test("Shop Buy (JSON body)", "POST", "/game/shop/buy", 
                             200, response2.status_code, response2.status_code in [200, 400])
            else:
                self.log_api_mismatch("Shop Buy Format",
                                    "POST /api/game/shop/buy with query params",
                                    "Different endpoint format required",
                                    "MEDIUM - Shop purchases may fail")

    def test_market_system(self):
        """Test market system"""
        print("\n🏪 Testing Market System...")
        
        # Check various market endpoints mentioned in review
        market_endpoints = [
            '/game/market/listings',
            '/game/market/my-listings',
            '/game/market/buy',
            '/game/market/sell'
        ]
        
        for endpoint in market_endpoints:
            response = self.make_request('GET', endpoint)
            success = response and response.status_code == 200
            self.log_test(f"Market {endpoint.split('/')[-1]}", "GET", endpoint, 
                         200, response.status_code if response else 0, success)

    def test_bank_system(self):
        """Test bank system"""
        print("\n🏦 Testing Bank System...")
        
        response = self.make_request('GET', '/game/bank/account')
        success = response and response.status_code == 200
        self.log_test("Bank Account", "GET", "/game/bank/account", 
                     200, response.status_code if response else 0, success)

        # Test deposit/withdraw
        deposit_data = {"amount": 10}
        response = self.make_request('POST', '/game/bank/deposit', deposit_data)
        success = response and response.status_code in [200, 400]
        self.log_test("Bank Deposit", "POST", "/game/bank/deposit", 
                     200, response.status_code if response else 0, 
                     response.status_code in [200, 400] if response else False)

        withdraw_data = {"amount": 5}
        response = self.make_request('POST', '/game/bank/withdraw', withdraw_data)
        success = response and response.status_code in [200, 400]
        self.log_test("Bank Withdraw", "POST", "/game/bank/withdraw", 
                     200, response.status_code if response else 0,
                     response.status_code in [200, 400] if response else False)

    def test_tavern_system(self):
        """Test tavern system"""
        print("\n🎲 Testing Tavern System...")
        
        dice_data = {"wager": 10}
        response = self.make_request('POST', '/game/tavern/dice', dice_data)
        success = response and response.status_code in [200, 400]
        self.log_test("Tavern Dice", "POST", "/game/tavern/dice", 
                     200, response.status_code if response else 0,
                     response.status_code in [200, 400] if response else False)

    def test_travel_system(self):
        """Test travel system"""
        print("\n🗺️ Testing Travel System...")
        
        travel_data = {"kingdom_id": "goldenveil"}
        response = self.make_request('POST', '/game/travel', travel_data)
        success = response and response.status_code in [200, 400]
        self.log_test("Start Travel", "POST", "/game/travel", 
                     200, response.status_code if response else 0,
                     response.status_code in [200, 400] if response else False)

        response = self.make_request('POST', '/game/travel/complete')
        # Endpoint should exist even if no active travel
        success = response is not None
        self.log_test("Complete Travel", "POST", "/game/travel/complete", 
                     200, response.status_code if response else 0, success)

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🏰 Starting Game API Mismatch Testing")
        print("=" * 60)
        
        start_time = time.time()
        
        # Setup user first
        if not self.setup_test_user():
            print("❌ Cannot continue without authenticated user")
            return None
        
        # Test all systems
        self.test_training_system()     # CRITICAL - mentioned in review
        self.test_game_state()          # Check structure issues
        self.test_crimes_system()
        self.test_combat_system()
        self.test_shop_system()
        self.test_market_system()
        self.test_bank_system()
        self.test_tavern_system()
        self.test_travel_system()
        
        # Results
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        print("\n" + "=" * 60)
        print("📊 GAME API TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        success_rate = round((self.tests_passed / self.tests_run) * 100, 1) if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate}%")
        print(f"Duration: {duration}s")
        
        if self.api_mismatches:
            print(f"\n🚨 CRITICAL: {len(self.api_mismatches)} API MISMATCHES FOUND:")
            for i, mismatch in enumerate(self.api_mismatches, 1):
                print(f"{i}. {mismatch['feature']} - {mismatch['impact']}")
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': len(self.failed_tests),
            'success_rate': success_rate,
            'api_mismatches': self.api_mismatches,
            'failed_tests': self.failed_tests[:10],  # First 10
            'duration': duration
        }

def main():
    """Main execution"""
    tester = GameAPITester()
    results = tester.run_all_tests()
    
    if results:
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f'/app/game_api_test_{timestamp}.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to game_api_test_{timestamp}.json")
        
        # Return appropriate exit code
        if results['api_mismatches']:
            print("🚨 CRITICAL API MISMATCHES - Frontend will break!")
            return 1
        elif results['success_rate'] < 70:
            print("⚠️ HIGH FAILURE RATE")
            return 1
        else:
            print("✅ Tests completed")
            return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())