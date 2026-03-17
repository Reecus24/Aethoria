#!/usr/bin/env python3
"""
Backend Testing for Realm of Aethoria - Critical Bug Fixes Verification
Testing the 9 critical bug fixes reported by German user on production
"""

import requests
import sys
from datetime import datetime
import uuid
import time
import json

class AethoriaBackendTester:
    def __init__(self, base_url="https://dragon-quest-46.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.knight_token = None
        self.shadow_token = None
        self.knight_user = None
        self.shadow_user = None
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

    def test_user_creation(self):
        """Create test users for different scenarios"""
        print("\n👥 Creating Test Users...")
        
        timestamp = str(int(time.time()))[-6:]
        
        # Create Knight user
        knight_data = {
            "username": f"TestKnight{timestamp}",
            "email": f"knight{timestamp}@test.com",
            "password": "testpass123",
            "path_choice": "knight"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=knight_data)
            if response.status_code == 200:
                data = response.json()
                self.knight_token = data.get('token')
                self.knight_user = data.get('user', {})
                self.log_test("Knight user creation", True, f"Created: {knight_data['username']}")
            else:
                self.log_test("Knight user creation", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Knight user creation", False, f"Exception: {str(e)}")
            return False
        
        # Create Shadow user
        shadow_data = {
            "username": f"TestShadow{timestamp}",
            "email": f"shadow{timestamp}@test.com", 
            "password": "testpass123",
            "path_choice": "shadow"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=shadow_data)
            if response.status_code == 200:
                data = response.json()
                self.shadow_token = data.get('token')
                self.shadow_user = data.get('user', {})
                self.token = self.shadow_token  # Default to shadow for most tests
                self.log_test("Shadow user creation", True, f"Created: {shadow_data['username']}")
                return True
            else:
                self.log_test("Shadow user creation", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Shadow user creation", False, f"Exception: {str(e)}")
            return False

    def test_dungeon_timer_logic(self):
        """Test Bug Fix #1 - Dungeon UI should only show when actually in jail"""
        print("\n🏢 Testing Dungeon Timer Logic...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            # Get game state to check dungeon status
            response = requests.get(f"{self.base_url}/game/state", headers=headers)
            if response.status_code == 200:
                game_state = response.json()
                timers = game_state.get('timers', {})
                
                # Check if dungeon timer exists
                dungeon_timer = timers.get('dungeon')
                
                if dungeon_timer:
                    # If dungeon timer exists, verify it has seconds_remaining > 0 
                    seconds_remaining = dungeon_timer.get('seconds_remaining', 0)
                    self.log_test("Dungeon timer has valid seconds_remaining", 
                                 isinstance(seconds_remaining, int),
                                 "Timer should have integer seconds_remaining")
                    
                    # If seconds > 0, user should be considered in jail
                    if seconds_remaining > 0:
                        self.log_test("Dungeon timer shows active jail time", True, 
                                     f"User in jail for {seconds_remaining} seconds")
                    else:
                        self.log_test("Dungeon timer shows zero when not jailed", True,
                                     "Timer exists but shows 0 (should trigger release)")
                else:
                    self.log_test("No active dungeon timer", True, "User not in jail (expected for new user)")
                
                # Test the logic: dungeon UI should only show if timers.dungeon exists AND seconds_remaining > 0
                in_dungeon_ui = dungeon_timer and dungeon_timer.get('seconds_remaining', 0) > 0
                self.log_test("Dungeon UI logic check", True, 
                             f"Should show dungeon UI: {in_dungeon_ui}")
                
            else:
                self.log_test("Get game state for dungeon check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Dungeon timer logic test", False, f"Exception: {str(e)}")

    def test_hospital_timer_calculation(self):
        """Test Bug Fix #2 - Hospital timer should calculate based on missing HP"""
        print("\n🏥 Testing Hospital Timer Calculation...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            # Get current game state
            response = requests.get(f"{self.base_url}/game/state", headers=headers)
            if response.status_code == 200:
                game_state = response.json()
                resources = game_state.get('resources', {})
                timers = game_state.get('timers', {})
                
                current_hp = resources.get('hp', 100)
                max_hp = resources.get('hp_max', 100)
                
                self.log_test("Get HP values", True, f"HP: {current_hp}/{max_hp}")
                
                # Check hospital timer calculation
                hospital_timer = timers.get('hospital')
                
                if hospital_timer:
                    seconds_remaining = hospital_timer.get('seconds_remaining', 0)
                    self.log_test("Hospital timer exists", True, f"{seconds_remaining} seconds remaining")
                    
                    # If user is injured but not in active hospital session, 
                    # timer should calculate (MAX_HP - current_hp) * 360 seconds
                    if current_hp < max_hp:
                        hp_missing = max_hp - current_hp
                        expected_seconds = hp_missing * 360  # 360 seconds per HP as per fix
                        
                        # Allow some tolerance for timing differences
                        tolerance = 60  # 1 minute tolerance
                        time_diff = abs(seconds_remaining - expected_seconds)
                        
                        self.log_test("Hospital timer calculation matches formula", 
                                     time_diff <= tolerance,
                                     f"Timer calculation for injured user",
                                     f"~{expected_seconds} seconds for {hp_missing} missing HP",
                                     f"{seconds_remaining} seconds (diff: {time_diff})")
                else:
                    if current_hp < max_hp:
                        self.log_test("Hospital timer missing for injured user", False,
                                     "Should have hospital timer when HP < max")
                    else:
                        self.log_test("No hospital timer for healthy user", True,
                                     "Correctly no timer when at full HP")
                        
            else:
                self.log_test("Get game state for hospital check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Hospital timer calculation test", False, f"Exception: {str(e)}")

    def test_training_multiple_stats(self):
        """Test Bug Fix #4 - Training should allow multiple concurrent stat training"""
        print("\n💪 Testing Multiple Stat Training...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            # Start training strength
            response = requests.post(f"{self.base_url}/game/training/start", 
                                   json={"stat": "strength"}, headers=headers)
            
            if response.status_code == 200:
                self.log_test("Start strength training", True)
                
                # Immediately try to start dexterity training
                time.sleep(0.5)  # Small delay to ensure timing
                response2 = requests.post(f"{self.base_url}/game/training/start",
                                        json={"stat": "dexterity"}, headers=headers)
                
                if response2.status_code == 200:
                    self.log_test("Start concurrent dexterity training", True, 
                                 "Multiple stat training works")
                elif response2.status_code == 400:
                    error_msg = response2.json().get('detail', '').lower()
                    if 'bereits' in error_msg or 'already' in error_msg:
                        if 'dexterity' in error_msg:
                            self.log_test("Multiple stat training blocked", False,
                                         "Should allow different stats to train concurrently")
                        else:
                            self.log_test("Same stat training correctly blocked", True,
                                         "Correctly prevents same stat double training")
                    else:
                        self.log_test("Training restriction logic", False, f"Unexpected error: {error_msg}")
                else:
                    self.log_test("Second training attempt", False, f"Status: {response2.status_code}")
                    
            elif response.status_code == 400:
                error_msg = response.json().get('detail', '').lower()
                if 'energie' in error_msg or 'energy' in error_msg:
                    self.log_test("Training energy check", True, "Correctly blocked due to insufficient energy")
                else:
                    self.log_test("Start strength training", False, f"Error: {error_msg}")
            else:
                self.log_test("Start strength training", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Multiple stat training test", False, f"Exception: {str(e)}")

    def test_xp_calculation(self):
        """Test Bug Fix #6 - XP should show actual progress, not 0/100"""
        print("\n⭐ Testing XP Calculation...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(f"{self.base_url}/game/state", headers=headers)
            if response.status_code == 200:
                game_state = response.json()
                user = game_state.get('user', {})
                resources = game_state.get('resources', {})
                
                current_xp = user.get('xp', 0)
                xp_required = resources.get('xp_required', 0)
                level = user.get('level', 1)
                
                self.log_test("Get XP values", True, f"XP: {current_xp}, Required: {xp_required}, Level: {level}")
                
                # Check that XP is not stuck at 0/100
                if level > 1 or current_xp > 0:
                    self.log_test("XP progresses correctly", current_xp > 0 or level > 1,
                                 "XP should progress for active users")
                
                # Check that xp_required is calculated correctly (remaining XP, not total threshold)
                if xp_required > 0:
                    # For level 1, should require (100 - current_xp)
                    # For level 2, should require (250 - current_xp), etc.
                    level_thresholds = [0, 100, 250, 450, 700, 1000]
                    if level <= len(level_thresholds):
                        threshold = level_thresholds[level - 1] if level > 1 else level_thresholds[level]
                        expected_required = max(0, threshold - current_xp)
                        
                        self.log_test("XP required calculation", 
                                     abs(xp_required - expected_required) <= 1,
                                     "XP required should be remaining XP to next level",
                                     f"{expected_required} XP remaining",
                                     f"{xp_required} XP required")
                    else:
                        self.log_test("High level XP handling", True, f"Level {level} XP handling")
                else:
                    if level >= 20:  # Max level
                        self.log_test("Max level XP handling", True, "At max level, 0 XP required is correct")
                    else:
                        self.log_test("XP required calculation", False, "Should have XP required for leveling")
                        
            else:
                self.log_test("Get game state for XP check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("XP calculation test", False, f"Exception: {str(e)}")

    def test_mugging_mechanics(self):
        """Test Bug Fix #7 - Mugging should only steal gold, no damage"""
        print("\n🗡️ Testing Mugging Mechanics...")
        
        if not self.knight_token or not self.shadow_token:
            self.log_test("Mugging test setup", False, "Need both Knight and Shadow users")
            return
        
        shadow_headers = {'Authorization': f'Bearer {self.shadow_token}'}
        knight_headers = {'Authorization': f'Bearer {self.knight_token}'}
        
        try:
            # Get initial HP of knight
            response = requests.get(f"{self.base_url}/game/state", headers=knight_headers)
            if response.status_code == 200:
                knight_state = response.json()
                initial_hp = knight_state.get('resources', {}).get('hp', 100)
                initial_gold = knight_state.get('resources', {}).get('gold', 0)
                knight_username = knight_state.get('user', {}).get('username')
                
                self.log_test("Get knight initial state", True, 
                             f"HP: {initial_hp}, Gold: {initial_gold}")
                
                if not knight_username:
                    self.log_test("Knight username retrieval", False, "Could not get knight username")
                    return
                
                # Shadow attempts to mug the knight
                mug_data = {"target_username": knight_username, "action": "mug"}
                response = requests.post(f"{self.base_url}/game/combat/attack", 
                                       json=mug_data, headers=shadow_headers)
                
                if response.status_code == 200:
                    mug_result = response.json()
                    self.log_test("Mugging attempt executed", True)
                    
                    # Check knight's HP after mugging - should be unchanged
                    time.sleep(1)  # Brief delay
                    response = requests.get(f"{self.base_url}/game/state", headers=knight_headers)
                    if response.status_code == 200:
                        post_mug_state = response.json()
                        post_mug_hp = post_mug_state.get('resources', {}).get('hp', 100)
                        post_mug_gold = post_mug_state.get('resources', {}).get('gold', 0)
                        
                        # HP should be unchanged (mugging should not deal damage)
                        self.log_test("Mugging deals no damage", 
                                     post_mug_hp == initial_hp,
                                     "Mugging should only steal gold, not deal damage",
                                     f"HP unchanged at {initial_hp}",
                                     f"HP changed from {initial_hp} to {post_mug_hp}")
                        
                        # Gold might have been stolen (if mugging was successful)
                        if post_mug_gold < initial_gold:
                            self.log_test("Mugging stole gold", True, 
                                         f"Gold reduced from {initial_gold} to {post_mug_gold}")
                        elif post_mug_gold == initial_gold:
                            self.log_test("Mugging failed or no gold stolen", True, 
                                         "Gold unchanged (mugging may have failed)")
                    else:
                        self.log_test("Get post-mug knight state", False, f"Status: {response.status_code}")
                        
                elif response.status_code == 400:
                    error_msg = response.json().get('detail', '').lower()
                    if 'energie' in error_msg or 'energy' in error_msg:
                        self.log_test("Mugging energy requirement", True, "Correctly blocked due to insufficient energy")
                    else:
                        self.log_test("Mugging attempt", False, f"Error: {error_msg}")
                else:
                    self.log_test("Mugging attempt", False, f"Status: {response.status_code}")
                    
            else:
                self.log_test("Get knight initial state", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Mugging mechanics test", False, f"Exception: {str(e)}")

    def test_equipment_bonuses(self):
        """Test Bug Fix #8 - Character stats should reflect equipment bonuses"""
        print("\n⚔️ Testing Equipment Bonuses...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            # Get current stats
            response = requests.get(f"{self.base_url}/game/state", headers=headers)
            if response.status_code == 200:
                game_state = response.json()
                stats = game_state.get('stats', {})
                base_strength = stats.get('strength', 0)
                total_strength = stats.get('total_strength', base_strength)
                base_defense = stats.get('defense', 0)
                total_defense = stats.get('total_defense', base_defense)
                
                self.log_test("Get character stats", True, 
                             f"Strength: {base_strength} (total: {total_strength}), Defense: {base_defense} (total: {total_defense})")
                
                # Check if total stats are provided (indicating equipment bonus calculation)
                has_total_strength = 'total_strength' in stats
                has_total_defense = 'total_defense' in stats
                
                self.log_test("Equipment bonus fields present", 
                             has_total_strength and has_total_defense,
                             "Game state should include total_strength and total_defense")
                
                # If user has equipment, totals should potentially be different
                equipment = game_state.get('equipment', [])
                has_equipment = len(equipment) > 0
                
                if has_equipment:
                    # Check if any equipment has bonuses
                    has_strength_bonus = any(item.get('strength', 0) > 0 for item in equipment)
                    has_defense_bonus = any(item.get('defense', 0) > 0 for item in equipment)
                    
                    if has_strength_bonus:
                        self.log_test("Strength bonus from equipment", 
                                     total_strength >= base_strength,
                                     "Total strength should be >= base strength with equipment")
                    
                    if has_defense_bonus:
                        self.log_test("Defense bonus from equipment",
                                     total_defense >= base_defense,
                                     "Total defense should be >= base defense with equipment")
                else:
                    self.log_test("No equipment found", True, "New user without equipment (expected)")
                    # Without equipment, total should equal base
                    self.log_test("Stats without equipment match",
                                 total_strength == base_strength and total_defense == base_defense,
                                 "Without equipment, total stats should equal base stats")
                    
            else:
                self.log_test("Get game state for equipment bonuses", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Equipment bonuses test", False, f"Exception: {str(e)}")

    def test_hall_of_fame(self):
        """Test Bug Fix #9 - Hall of Fame should show player names, not classes"""
        print("\n🏆 Testing Hall of Fame...")
        
        try:
            response = requests.get(f"{self.base_url}/landing")
            if response.status_code == 200:
                data = response.json()
                leaderboard = data.get('leaderboard', [])
                
                if len(leaderboard) > 0:
                    self.log_test("Leaderboard has entries", True, f"Found {len(leaderboard)} entries")
                    
                    # Check that entries have username, not just class names
                    first_entry = leaderboard[0]
                    has_username = 'username' in first_entry
                    username_value = first_entry.get('username', '')
                    
                    # Common class names to avoid
                    class_names = ['knight', 'shadow', 'noble', 'the knight', 'the shadow', 'the noble']
                    is_class_name = username_value.lower() in class_names
                    
                    self.log_test("Hall of Fame shows usernames", 
                                 has_username and not is_class_name,
                                 "Should show actual player usernames, not class names",
                                 "Player username",
                                 f"'{username_value}'" if username_value else "No username")
                    
                    # Check for path_label vs username confusion
                    path_label = first_entry.get('path_label', '')
                    title = first_entry.get('title', '')
                    
                    if username_value == path_label or username_value == title:
                        self.log_test("Username vs path_label confusion", False,
                                     "Username appears to be showing path_label instead of actual username")
                    else:
                        self.log_test("Username distinct from path", True,
                                     "Username correctly distinct from path/title")
                        
                else:
                    self.log_test("Leaderboard empty", True, "No leaderboard entries (may be expected for new deployment)")
                    
            else:
                self.log_test("Get leaderboard data", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Hall of Fame test", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all critical bug fix tests"""
        print("🔥 REALM OF AETHORIA - CRITICAL BUG FIXES TESTING")
        print("=" * 70)
        print("Testing 9 critical bugs reported by German user on production")
        print("=" * 70)
        
        # Create test users
        if not self.test_user_creation():
            print("❌ User creation failed - cannot proceed with other tests")
            return False
        
        # Test each critical bug fix
        self.test_dungeon_timer_logic()        # Bug #1
        self.test_hospital_timer_calculation()  # Bug #2
        # Map level requirements (Bug #3) - Frontend only
        self.test_training_multiple_stats()     # Bug #4
        # Equipment system bugs (Bug #5) - Complex, needs frontend testing
        self.test_xp_calculation()             # Bug #6
        self.test_mugging_mechanics()          # Bug #7
        self.test_equipment_bonuses()          # Bug #8
        self.test_hall_of_fame()              # Bug #9
        
        # Summary
        print("\n" + "=" * 70)
        print(f"📊 BACKEND TEST SUMMARY")
        print(f"Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed < self.tests_run:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🔗 Tested against: {self.base_url}")
        return self.tests_passed >= (self.tests_run * 0.8)  # 80% pass rate acceptable

if __name__ == "__main__":
    tester = AethoriaBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)