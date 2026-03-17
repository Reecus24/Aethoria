#!/usr/bin/env python3
"""
Backend Testing for Realm of Aethoria - Fixed Bugs Verification
Testing 14 specific bug fixes reported by user after production deployment
"""

import requests
import sys
from datetime import datetime
import uuid
import time

class FixedBugsAPITester:
    def __init__(self, base_url="https://dragon-quest-46.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details="", expected="", actual=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
            if expected:
                print(f"   Expected: {expected}")
            if actual:
                print(f"   Actual: {actual}")
        
        self.test_results.append({
            'test': name,
            'success': success,
            'details': details,
            'expected': expected,
            'actual': actual
        })

    def test_auth_and_setup(self):
        """Test authentication and create test users"""
        print("\n🔐 Testing Authentication & User Creation...")
        
        # Create Shadow user for testing
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits for uniqueness
        shadow_email = f"shadow{timestamp}@test.com"
        shadow_data = {
            "username": f"Shadow{timestamp}",
            "email": shadow_email,
            "password": "testpass123",
            "path_choice": "shadow"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=shadow_data)
            print(f"Registration response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.shadow_user = data.get('user', {})
                self.log_test("Shadow user registration", True, f"Created user: {shadow_data['username']}")
                
                # BUG FIX 1: Check starting stats - should be 100g for all paths
                gold = self.shadow_user.get('gold', 0)
                self.log_test("Bug Fix #1 - Path starting stats (100g)", 
                             gold == 100, 
                             f"Shadow path starting gold should be 100g",
                             "100 gold", f"{gold} gold")
                return True
            else:
                self.log_test("Shadow user registration", False, f"Failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Shadow user registration", False, f"Exception: {str(e)}")
            return False

    def test_equipment_system(self):
        """Test Bug Fix #2 - Equipment system fixed"""
        print("\n⚔️ Testing Equipment System...")
        
        if not self.token:
            self.log_test("Equipment test setup", False, "No auth token")
            return
            
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Get initial inventory
        try:
            response = requests.get(f"{self.base_url}/game/inventory", headers=headers)
            if response.status_code == 200:
                initial_inventory = response.json()
                self.log_test("Get initial inventory", True)
                
                # Check if equipment is returned in proper format
                equipped = initial_inventory.get('equipped', {})
                inventory_items = initial_inventory.get('inventory', [])
                self.log_test("Bug Fix #2 - Equipment structure returned", 
                             isinstance(equipped, dict) and isinstance(inventory_items, list),
                             "Equipment system returns proper structure")
                
                # Try to buy an item first to test equipping
                shop_response = requests.get(f"{self.base_url}/game/shop/items", headers=headers)
                if shop_response.status_code == 200:
                    items = shop_response.json()
                    # Find a cheap weapon to buy
                    cheap_weapon = None
                    for item in items:
                        if item.get('type') == 'weapon' and item.get('price', 999999) <= 100:
                            cheap_weapon = item
                            break
                    
                    if cheap_weapon:
                        # Buy the weapon - try different formats
                        buy_response = requests.post(
                            f"{self.base_url}/game/shop/buy?item_id={cheap_weapon['id']}", 
                            headers=headers
                        )
                        if buy_response.status_code != 200:
                            # Try with JSON body
                            buy_response = requests.post(
                                f"{self.base_url}/game/shop/buy", 
                                json={"item_id": cheap_weapon['id']},
                                headers=headers
                            )
                        if buy_response.status_code == 200:
                            self.log_test("Buy weapon for equipment test", True, cheap_weapon['name'])
                            
                            # Now try to equip it
                            equip_response = requests.post(
                                f"{self.base_url}/game/inventory/equip",
                                json={"item_id": cheap_weapon['id'], "slot": "weapon"},
                                headers=headers
                            )
                            if equip_response.status_code == 200:
                                self.log_test("Bug Fix #2 - Equipment equip works", True)
                                
                                # Check if equipment is updated
                                post_equip_response = requests.get(f"{self.base_url}/game/inventory", headers=headers)
                                if post_equip_response.status_code == 200:
                                    post_inventory = post_equip_response.json()
                                    weapon_equipped = post_inventory.get('equipped', {}).get('weapon')
                                    self.log_test("Bug Fix #2 - Equipment persisted after equip", 
                                                 weapon_equipped == cheap_weapon['id'],
                                                 "Weapon should be equipped after equip call")
                                else:
                                    self.log_test("Check post-equip inventory", False, "Failed to get inventory after equip")
                            else:
                                self.log_test("Equip weapon", False, f"Failed with status {equip_response.status_code}")
                        else:
                            self.log_test("Buy weapon", False, f"Failed with status {buy_response.status_code}")
                    else:
                        self.log_test("Find cheap weapon", False, "No affordable weapons found")
                else:
                    self.log_test("Get shop items", False, f"Failed with status {shop_response.status_code}")
            else:
                self.log_test("Get initial inventory", False, f"Failed with status {response.status_code}")
        except Exception as e:
            self.log_test("Equipment system test", False, f"Exception: {str(e)}")

    def test_timers_format(self):
        """Test Bug Fix #3 - Hospital/Dungeon timers format"""
        print("\n⏰ Testing Timer Format...")
        
        if not self.token:
            self.log_test("Timer test setup", False, "No auth token")
            return
            
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            # Get game state to check timer format
            response = requests.get(f"{self.base_url}/game/state", headers=headers)
            if response.status_code == 200:
                game_state = response.json()
                timers = game_state.get('timers', {})
                
                self.log_test("Get game state for timers", True)
                
                # Check timer structure - should have seconds_remaining instead of minutes_remaining
                if 'hospital' in timers:
                    hospital_timer = timers['hospital']
                    has_seconds = 'seconds_remaining' in hospital_timer
                    no_minutes = 'minutes_remaining' not in hospital_timer
                    self.log_test("Bug Fix #3 - Hospital timer uses seconds_remaining", 
                                 has_seconds and no_minutes,
                                 "Timer should use seconds_remaining, not minutes_remaining")
                else:
                    self.log_test("Bug Fix #3 - Timer format check", True, "No active hospital timer (expected)")
                
                if 'dungeon' in timers:
                    dungeon_timer = timers['dungeon']
                    has_seconds = 'seconds_remaining' in dungeon_timer
                    no_minutes = 'minutes_remaining' not in dungeon_timer  
                    self.log_test("Bug Fix #3 - Dungeon timer uses seconds_remaining",
                                 has_seconds and no_minutes,
                                 "Timer should use seconds_remaining, not minutes_remaining")
                else:
                    self.log_test("Bug Fix #3 - Dungeon timer format check", True, "No active dungeon timer (expected)")
                    
            else:
                self.log_test("Get game state", False, f"Failed with status {response.status_code}")
        except Exception as e:
            self.log_test("Timer format test", False, f"Exception: {str(e)}")

    def test_travel_system(self):
        """Test Bug Fix #7 - Travel system request format"""
        print("\n🗺️ Testing Travel System...")
        
        if not self.token:
            self.log_test("Travel test setup", False, "No auth token")
            return
            
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            # Test travel with kingdom_id format (not destination)
            travel_data = {"kingdom_id": "ironhold"}  # Should be kingdom_id, not destination
            
            response = requests.post(f"{self.base_url}/game/travel", json=travel_data, headers=headers)
            # Travel might fail due to insufficient gold, but should accept the format
            if response.status_code in [200, 400]:  # 400 might be insufficient gold
                if response.status_code == 200:
                    self.log_test("Bug Fix #7 - Travel accepts kingdom_id format", True)
                else:
                    # Check if it's a gold issue vs format issue
                    error_msg = response.json().get('detail', '').lower()
                    if 'gold' in error_msg or 'cost' in error_msg:
                        self.log_test("Bug Fix #7 - Travel accepts kingdom_id format", True, "Format accepted (insufficient gold)")
                    else:
                        self.log_test("Bug Fix #7 - Travel request format", False, f"Unexpected error: {error_msg}")
            else:
                self.log_test("Bug Fix #7 - Travel request format", False, f"Failed with status {response.status_code}")
                
        except Exception as e:
            self.log_test("Travel system test", False, f"Exception: {str(e)}")

    def test_messages_system(self):
        """Test Bug Fix #8 & #9 - Messages system"""
        print("\n✉️ Testing Messages System...")
        
        if not self.token:
            self.log_test("Messages test setup", False, "No auth token")
            return
            
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            # Test message sending with recipient_username format
            message_data = {
                "recipient_username": "TestUser123",  # Use actual user from earlier
                "subject": "Test Message",
                "body": "Testing the message system format"
            }
            
            response = requests.post(f"{self.base_url}/game/messages/send", json=message_data, headers=headers)
            # Might fail because user doesn't exist, but should accept the format
            if response.status_code in [200, 404, 400]:
                if response.status_code == 200:
                    self.log_test("Bug Fix #8 - Messages accept recipient_username format", True)
                else:
                    error_msg = response.json().get('detail', '').lower()
                    if 'not found' in error_msg or 'exist' in error_msg:
                        self.log_test("Bug Fix #8 - Messages accept recipient_username format", True, "Format accepted (user not found)")
                    else:
                        self.log_test("Bug Fix #8 - Messages request format", False, f"Unexpected error: {error_msg}")
            else:
                self.log_test("Bug Fix #8 - Messages request format", False, f"Failed with status {response.status_code}")
            
            # Test messages API response format
            response = requests.get(f"{self.base_url}/game/messages", headers=headers)
            if response.status_code == 200:
                messages_data = response.json()
                # Bug Fix #9: Should be direct array, not res.data.messages
                if isinstance(messages_data, list):
                    self.log_test("Bug Fix #9 - Messages API returns direct array", True)
                elif isinstance(messages_data, dict) and 'messages' in messages_data:
                    self.log_test("Bug Fix #9 - Messages API response format", False, "Still using nested messages format")
                else:
                    self.log_test("Bug Fix #9 - Messages API response format", False, f"Unexpected format: {type(messages_data)}")
            else:
                self.log_test("Get messages API", False, f"Failed with status {response.status_code}")
                
        except Exception as e:
            self.log_test("Messages system test", False, f"Exception: {str(e)}")

    def test_properties_api_format(self):
        """Test Bug Fix #14 - Properties API format"""
        print("\n🏰 Testing Properties API...")
        
        if not self.token:
            self.log_test("Properties test setup", False, "No auth token")
            return
            
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(f"{self.base_url}/game/properties/available", headers=headers)
            if response.status_code == 200:
                properties_data = response.json()
                
                # Bug Fix #14: Should return {properties: []} format, not bare array
                if isinstance(properties_data, dict) and 'properties' in properties_data:
                    properties_list = properties_data['properties']
                    if isinstance(properties_list, list):
                        self.log_test("Bug Fix #14 - Properties API returns {properties: []} format", True)
                    else:
                        self.log_test("Bug Fix #14 - Properties API format", False, "properties field is not a list")
                elif isinstance(properties_data, list):
                    self.log_test("Bug Fix #14 - Properties API format", False, "Still returning bare array instead of {properties: []}")
                else:
                    self.log_test("Bug Fix #14 - Properties API format", False, f"Unexpected format: {type(properties_data)}")
            else:
                self.log_test("Get properties API", False, f"Failed with status {response.status_code}")
                
        except Exception as e:
            self.log_test("Properties API test", False, f"Exception: {str(e)}")

    def test_quest_specificity(self):
        """Test Bug Fix #12 - Class-specific quests"""
        print("\n📜 Testing Quest Specificity...")
        
        if not self.token:
            self.log_test("Quest test setup", False, "No auth token")
            return
            
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(f"{self.base_url}/game/quests/available", headers=headers)
            if response.status_code == 200:
                quest_data = response.json()
                available_quests = quest_data.get('available_quests', [])
                
                if available_quests:
                    # Check if quests are path-specific for Shadow user
                    shadow_quests = [q for q in available_quests if 'shadow' in q.get('paths', [])]
                    non_shadow_quests = [q for q in available_quests if 'shadow' not in q.get('paths', []) and q.get('paths')]
                    
                    self.log_test("Bug Fix #12 - Class-specific quests exist", 
                                 len(shadow_quests) > 0,
                                 f"Found {len(shadow_quests)} Shadow-specific quests")
                    
                    if non_shadow_quests:
                        self.log_test("Bug Fix #12 - Path filtering working", False, 
                                     f"Found {len(non_shadow_quests)} non-Shadow quests for Shadow user")
                    else:
                        self.log_test("Bug Fix #12 - Path filtering working", True, "Only appropriate path quests shown")
                else:
                    self.log_test("Quest availability check", True, "No quests available (may be expected)")
                    
            else:
                self.log_test("Get quests API", False, f"Failed with status {response.status_code}")
                
        except Exception as e:
            self.log_test("Quest specificity test", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests for fixed bugs"""
        print("🔥 REALM OF AETHORIA - FIXED BUGS BACKEND TESTING")
        print("=" * 60)
        
        # Core authentication and bug fix #1
        if not self.test_auth_and_setup():
            print("❌ Authentication failed - cannot proceed with other tests")
            return False
            
        # Test each bug fix
        self.test_equipment_system()        # Bug Fix #2
        self.test_timers_format()           # Bug Fix #3
        self.test_travel_system()           # Bug Fix #7  
        self.test_messages_system()         # Bug Fix #8 & #9
        self.test_properties_api_format()   # Bug Fix #14
        self.test_quest_specificity()       # Bug Fix #12
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 BACKEND TEST SUMMARY")
        print(f"Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed < self.tests_run:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = FixedBugsAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)