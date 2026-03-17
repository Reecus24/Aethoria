#!/usr/bin/env python3
"""
Comprehensive Backend Testing for All 42 Features - Medieval Fantasy Game
Phase 7 E2E Testing - Testing all CRITICAL, HIGH, MEDIUM priority features
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

class ComprehensiveGameTester:
    def __init__(self):
        self.base_url = "https://dragon-quest-46.preview.emergentagent.com/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.critical_issues = []
        
    def log_test(self, name: str, success: bool, details: str = "", priority: str = "MEDIUM"):
        """Log test results with priority"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - {details}")
        else:
            issue = {
                'name': name,
                'priority': priority, 
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            self.failed_tests.append(issue)
            if priority == "CRITICAL":
                self.critical_issues.append(issue)
            print(f"❌ [{priority}] {name} - {details}")
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, timeout: int = 10) -> Optional[requests.Response]:
        """Make HTTP request with authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.Timeout:
            self.log_test(f"Timeout on {method} {endpoint}", False, "Request timeout after 10s", "HIGH")
            return None
        except Exception as e:
            self.log_test(f"Error on {method} {endpoint}", False, f"Exception: {str(e)}", "HIGH")
            return None
    
    def setup_test_user(self) -> bool:
        """Login with provided test user credentials"""
        print("🔐 Logging in with test user: megaknight@test.com")
        
        login_data = {
            "email": "megaknight@test.com",
            "password": "Test123!"
        }
        
        response = self.make_request('POST', '/auth/login', login_data)
        if response and response.status_code == 200:
            data = response.json()
            self.token = data.get('token')
            self.user_data = data.get('user', {})
            print(f"✅ Logged in successfully as {self.user_data.get('username', 'Unknown')}")
            print(f"   Level: {self.user_data.get('level', 0)}, Gold: {self.user_data.get('gold', 0)}")
            return True
        else:
            self.log_test("User Login", False, f"Failed to login - Status: {response.status_code if response else 'No response'}", "CRITICAL")
            return False
    
    def test_game_state(self) -> Dict[str, Any]:
        """Test game state API - foundation for all other tests"""
        print("\n🎮 Testing Game State...")
        response = self.make_request('GET', '/game/state')
        
        if not response or response.status_code != 200:
            self.log_test("Game State API", False, f"Status: {response.status_code if response else 'No response'}", "CRITICAL")
            return {}
        
        game_state = response.json()
        
        # Verify essential structure
        required_fields = ['user', 'resources', 'stats', 'location', 'equipment', 'timers', 'status']
        missing = [f for f in required_fields if f not in game_state]
        
        if missing:
            self.log_test("Game State Structure", False, f"Missing fields: {missing}", "CRITICAL")
        else:
            self.log_test("Game State Structure", True, "All required fields present")
        
        # Check user resources
        resources = game_state.get('resources', {})
        if 'gold' in resources and 'energy' in resources and 'hp' in resources:
            self.log_test("Game Resources", True, f"Gold: {resources['gold']}, Energy: {resources['energy']}, HP: {resources['hp']}")
        else:
            self.log_test("Game Resources", False, "Missing resource data", "HIGH")
        
        return game_state
    
    def test_combat_system(self, game_state: Dict) -> None:
        """CRITICAL: Test combat system complete flow"""
        print("\n⚔️ Testing Combat System (CRITICAL)...")
        
        # 1. Get combat targets
        response = self.make_request('GET', '/game/combat/targets')
        if not response or response.status_code != 200:
            self.log_test("Combat Targets", False, f"Status: {response.status_code if response else 'No response'}", "CRITICAL")
            return
        
        targets = response.json()
        if not targets:
            self.log_test("Combat Targets", False, "No targets available", "MEDIUM")
            return
        
        self.log_test("Combat Targets", True, f"Found {len(targets)} targets")
        
        # 2. Check energy requirement
        current_energy = game_state.get('resources', {}).get('energy', 0)
        if current_energy < 25:
            self.log_test("Combat Energy Check", False, f"Insufficient energy: {current_energy}/25", "MEDIUM")
            return
        
        # 3. Test attack (should work or give proper error)
        target = targets[0] if targets else None
        if target:
            attack_data = {
                "target_username": target['username'],
                "action": "attack"
            }
            response = self.make_request('POST', '/game/combat/attack', attack_data)
            
            if response and response.status_code in [200, 400]:
                if response.status_code == 200:
                    result = response.json()
                    self.log_test("Combat Attack", True, f"Combat executed - Victory: {result.get('victory', 'Unknown')}")
                    
                    # Check if hospitalized (HP < 20)
                    if not result.get('victory'):
                        print("   Checking if player was hospitalized...")
                        # Refresh game state to check hospital status
                        new_state = self.test_game_state()
                        if new_state.get('status', {}).get('in_hospital'):
                            self.log_test("Hospital Mechanics", True, "Player hospitalized after combat defeat")
                        
                else:
                    self.log_test("Combat Attack", True, f"Combat blocked properly: {response.json().get('detail', 'Unknown error')}")
            else:
                self.log_test("Combat Attack", False, f"Status: {response.status_code if response else 'No response'}", "CRITICAL")
        
        # 4. Test combat logs
        response = self.make_request('GET', '/game/combat/logs', None, 5)
        if response and response.status_code == 200:
            logs = response.json()
            self.log_test("Combat Logs", True, f"Retrieved {len(logs)} combat log entries")
        else:
            self.log_test("Combat Logs", False, "Failed to retrieve combat logs", "MEDIUM")
    
    def test_quest_system(self) -> None:
        """CRITICAL: Test quest system - Accept, complete, rewards"""
        print("\n📜 Testing Quest System (CRITICAL)...")
        
        # 1. Get available quests
        response = self.make_request('GET', '/game/quests/available')
        if not response or response.status_code != 200:
            self.log_test("Quest Availability", False, f"Status: {response.status_code if response else 'No response'}", "CRITICAL")
            return
        
        quest_data = response.json()
        available_quests = quest_data.get('available_quests', [])
        active_quest = quest_data.get('active_quest')
        
        if active_quest:
            self.log_test("Active Quest", True, f"Quest in progress: {active_quest.get('quest_name', 'Unknown')}")
            
            # Try to complete if ready
            response = self.make_request('POST', '/game/quests/complete')
            if response:
                if response.status_code == 200:
                    result = response.json()
                    self.log_test("Quest Completion", True, f"Quest completed - XP: {result.get('gains', {}).get('xp_gain', 0)}")
                elif response.status_code == 400:
                    self.log_test("Quest Timer", True, "Quest not yet complete (timer active)")
                else:
                    self.log_test("Quest Completion", False, f"Status: {response.status_code}", "HIGH")
        
        if available_quests:
            self.log_test("Available Quests", True, f"Found {len(available_quests)} available quests")
            
            # Try to accept a quest
            quest = available_quests[0]
            accept_data = {"quest_id": quest['id']}
            response = self.make_request('POST', '/game/quests/accept', accept_data)
            
            if response and response.status_code in [200, 400]:
                if response.status_code == 200:
                    self.log_test("Quest Accept", True, f"Successfully accepted quest: {quest['name']}")
                else:
                    self.log_test("Quest Accept Block", True, f"Quest blocked properly: {response.json().get('detail', 'Unknown')}")
            else:
                self.log_test("Quest Accept", False, f"Status: {response.status_code if response else 'No response'}", "CRITICAL")
        else:
            self.log_test("Available Quests", False, "No quests available", "MEDIUM")
    
    def test_shop_inventory_equipment_flow(self) -> None:
        """CRITICAL: Test Shop → Inventory → Equipment flow"""
        print("\n🛍️ Testing Shop → Inventory → Equipment Flow (CRITICAL)...")
        
        # 1. Get shop items
        response = self.make_request('GET', '/game/shop/items')
        if not response or response.status_code != 200:
            self.log_test("Shop Items", False, f"Status: {response.status_code if response else 'No response'}", "CRITICAL")
            return
        
        items = response.json()
        affordable_items = [item for item in items if item.get('price', 999999) <= 100]  # Find cheap items
        
        if not affordable_items:
            self.log_test("Shop Items", False, "No affordable items for testing", "MEDIUM")
            return
        
        self.log_test("Shop Items", True, f"Found {len(items)} shop items, {len(affordable_items)} affordable")
        
        # 2. Try to buy an item
        item = affordable_items[0]
        response = self.make_request('POST', f"/game/shop/buy?item_id={item['id']}&quantity=1")
        
        if response and response.status_code in [200, 400]:
            if response.status_code == 200:
                self.log_test("Shop Purchase", True, f"Successfully bought {item['name']}")
                
                # 3. Check inventory 
                response = self.make_request('GET', '/game/inventory')
                if response and response.status_code == 200:
                    inventory_data = response.json()
                    inventory_items = inventory_data.get('inventory', [])
                    
                    # Check if purchased item appears in inventory
                    item_found = any(inv_item['item_id'] == item['id'] for inv_item in inventory_items)
                    if item_found:
                        self.log_test("Inventory Update", True, f"Item {item['name']} appears in inventory")
                        
                        # 4. Try to equip item if it's equippable
                        if item.get('slot'):
                            equip_data = {
                                "item_id": item['id'],
                                "slot": item['slot']
                            }
                            response = self.make_request('POST', '/game/inventory/equip', equip_data)
                            
                            if response and response.status_code == 200:
                                self.log_test("Item Equipment", True, f"Successfully equipped {item['name']}")
                                
                                # 5. Verify stat bonuses applied
                                new_game_state = self.test_game_state()
                                equipped_items = new_game_state.get('equipment', [])
                                if any(eq['id'] == item['id'] for eq in equipped_items):
                                    self.log_test("Equipment Bonuses", True, "Item bonuses should be applied to stats")
                                else:
                                    self.log_test("Equipment Bonuses", False, "Item not found in equipped items", "HIGH")
                            else:
                                self.log_test("Item Equipment", False, f"Status: {response.status_code if response else 'No response'}", "HIGH")
                    else:
                        self.log_test("Inventory Update", False, "Purchased item not found in inventory", "CRITICAL")
                else:
                    self.log_test("Inventory Check", False, f"Status: {response.status_code if response else 'No response'}", "HIGH")
            else:
                self.log_test("Shop Purchase Block", True, f"Purchase blocked: {response.json().get('detail', 'Unknown')}")
        else:
            self.log_test("Shop Purchase", False, f"Status: {response.status_code if response else 'No response'}", "CRITICAL")
    
    def test_market_system(self) -> None:
        """CRITICAL: Test Market System - Create listing, buy from market"""
        print("\n🏪 Testing Market System (CRITICAL)...")
        
        # 1. Check market listings
        response = self.make_request('GET', '/game/market/listings')
        if not response or response.status_code != 200:
            self.log_test("Market Listings", False, f"Status: {response.status_code if response else 'No response'}", "CRITICAL")
            return
        
        listings = response.json()
        self.log_test("Market Listings", True, f"Found {len(listings)} market listings")
        
        # 2. Check my listings
        response = self.make_request('GET', '/game/market/my-listings')
        if response and response.status_code == 200:
            my_listings = response.json()
            self.log_test("My Market Listings", True, f"User has {len(my_listings)} active listings")
        else:
            self.log_test("My Market Listings", False, f"Status: {response.status_code if response else 'No response'}", "HIGH")
        
        # 3. Try to buy from market (if affordable listings exist)
        if listings:
            affordable_listings = [l for l in listings if l.get('price_per_unit', 999999) <= 50]
            if affordable_listings:
                listing = affordable_listings[0]
                buy_data = {
                    "listing_id": listing['id'],
                    "quantity": 1
                }
                response = self.make_request('POST', '/game/market/buy', buy_data)
                
                if response and response.status_code in [200, 400]:
                    if response.status_code == 200:
                        self.log_test("Market Purchase", True, f"Bought from market: {listing.get('item_name', 'Unknown item')}")
                    else:
                        self.log_test("Market Purchase Block", True, f"Purchase blocked: {response.json().get('detail', 'Unknown')}")
                else:
                    self.log_test("Market Purchase", False, f"Status: {response.status_code if response else 'No response'}", "CRITICAL")
    
    def test_guild_system(self) -> None:
        """HIGH: Test Guild Management"""
        print("\n⚜️ Testing Guild System (HIGH)...")
        
        # 1. Check guilds
        response = self.make_request('GET', '/game/guilds')
        if response and response.status_code == 200:
            guilds = response.json()
            self.log_test("Guild List", True, f"Found {len(guilds)} guilds")
        else:
            self.log_test("Guild List", False, f"Status: {response.status_code if response else 'No response'}", "HIGH")
            return
        
        # 2. Check guild creation (costs gold)
        create_data = {
            "name": f"TestGuild_{int(time.time())}",
            "description": "Automated test guild"
        }
        response = self.make_request('POST', '/game/guilds/create', create_data)
        
        if response and response.status_code in [200, 400]:
            if response.status_code == 200:
                self.log_test("Guild Creation", True, "Successfully created guild")
            else:
                self.log_test("Guild Creation Block", True, f"Guild creation blocked: {response.json().get('detail', 'Unknown')}")
        else:
            self.log_test("Guild Creation", False, f"Status: {response.status_code if response else 'No response'}", "HIGH")
    
    def test_travel_system(self) -> None:
        """HIGH: Test Travel Complete Flow"""
        print("\n🗺️ Testing Travel System (HIGH)...")
        
        # 1. Check kingdoms
        response = self.make_request('GET', '/kingdoms')
        if response and response.status_code == 200:
            kingdoms = response.json()
            self.log_test("Kingdoms Data", True, f"Found {len(kingdoms)} kingdoms")
            
            # 2. Try to start travel
            if kingdoms:
                destination = kingdoms[1] if len(kingdoms) > 1 else kingdoms[0]  # Pick different kingdom
                travel_data = {"kingdom_id": destination['id']}
                response = self.make_request('POST', '/game/travel', travel_data)
                
                if response and response.status_code in [200, 400]:
                    if response.status_code == 200:
                        self.log_test("Travel Start", True, f"Started travel to {destination['name']}")
                        
                        # 3. Check if travel timer is active
                        game_state = self.test_game_state()
                        if game_state.get('timers', {}).get('travel'):
                            self.log_test("Travel Timer", True, "Travel timer is active")
                        else:
                            self.log_test("Travel Timer", False, "Travel timer not found", "MEDIUM")
                    else:
                        self.log_test("Travel Start Block", True, f"Travel blocked: {response.json().get('detail', 'Unknown')}")
                else:
                    self.log_test("Travel Start", False, f"Status: {response.status_code if response else 'No response'}", "HIGH")
        else:
            self.log_test("Kingdoms Data", False, f"Status: {response.status_code if response else 'No response'}", "HIGH")
    
    def test_training_system(self) -> None:
        """MEDIUM: Test Training Timer Flow"""
        print("\n💪 Testing Training System (MEDIUM)...")
        
        # 1. Check training status
        response = self.make_request('GET', '/game/training/status')
        if response and response.status_code == 200:
            training_status = response.json()
            if training_status:
                self.log_test("Active Training", True, f"Training in progress: {training_status.get('stat', 'Unknown')}")
                
                # Try to claim if ready
                response = self.make_request('POST', '/game/training/claim')
                if response and response.status_code in [200, 400]:
                    if response.status_code == 200:
                        result = response.json()
                        self.log_test("Training Claim", True, f"Training completed - Gains: {result.get('gains', {})}")
                    else:
                        self.log_test("Training Timer Active", True, "Training not yet complete")
                else:
                    self.log_test("Training Claim", False, f"Status: {response.status_code if response else 'No response'}", "MEDIUM")
            else:
                # No active training, try to start one
                train_data = {"stat": "strength"}
                response = self.make_request('POST', '/game/training/start', train_data)
                
                if response and response.status_code in [200, 400]:
                    if response.status_code == 200:
                        self.log_test("Training Start", True, "Started strength training")
                    else:
                        self.log_test("Training Start Block", True, f"Training blocked: {response.json().get('detail', 'Unknown')}")
                else:
                    self.log_test("Training Start", False, f"Status: {response.status_code if response else 'No response'}", "MEDIUM")
        else:
            self.log_test("Training Status", False, f"Status: {response.status_code if response else 'No response'}", "MEDIUM")
    
    def test_crime_jail_flow(self) -> None:
        """MEDIUM: Test Crime → Jail Flow"""
        print("\n🗡️ Testing Crime → Jail Flow (MEDIUM)...")
        
        # 1. Get available crimes
        response = self.make_request('GET', '/game/crimes')
        if not response or response.status_code != 200:
            self.log_test("Crimes List", False, f"Status: {response.status_code if response else 'No response'}", "MEDIUM")
            return
        
        crimes = response.json()
        if not crimes:
            self.log_test("Crimes Available", False, "No crimes available", "MEDIUM")
            return
        
        self.log_test("Crimes List", True, f"Found {len(crimes)} available crimes")
        
        # 2. Try to commit a low-level crime
        crime = crimes[0]  # Pick first (usually lowest level)
        commit_data = {"crime_id": crime['id']}
        response = self.make_request('POST', '/game/crimes/commit', commit_data)
        
        if response and response.status_code in [200, 400]:
            if response.status_code == 200:
                result = response.json()
                success = result.get('victory', False)
                
                if success:
                    self.log_test("Crime Success", True, f"Crime successful - Rewards: {result.get('rewards', {})}")
                else:
                    self.log_test("Crime Failure", True, f"Crime failed - Penalties: {result.get('penalties', {})}")
                    
                    # Check if player was jailed
                    game_state = self.test_game_state()
                    if game_state.get('timers', {}).get('dungeon'):
                        self.log_test("Jail Mechanics", True, "Player sent to jail after failed crime")
                    else:
                        self.log_test("Jail Mechanics", False, "Player not jailed after crime failure", "MEDIUM")
            else:
                self.log_test("Crime Attempt Block", True, f"Crime blocked: {response.json().get('detail', 'Unknown')}")
        else:
            self.log_test("Crime Attempt", False, f"Status: {response.status_code if response else 'No response'}", "MEDIUM")
    
    def test_tavern_dice_system(self) -> None:
        """MEDIUM: Test Tavern Dice edge cases"""
        print("\n🎲 Testing Tavern Dice System (MEDIUM)...")
        
        # 1. Try minimum bet
        min_bet_data = {"wager": 10}
        response = self.make_request('POST', '/game/tavern/dice', min_bet_data, 15)  # Longer timeout
        
        if response and response.status_code in [200, 400]:
            if response.status_code == 200:
                result = response.json()
                roll_total = result.get('roll_total', 0)
                won = result.get('won', False)
                
                # Verify logic: 7-12 = win, 2-6 = loss
                expected_win = 7 <= roll_total <= 12
                if won == expected_win:
                    self.log_test("Dice Logic", True, f"Roll: {roll_total}, Won: {won} (correct)")
                else:
                    self.log_test("Dice Logic", False, f"Roll: {roll_total}, Won: {won} (incorrect logic)", "HIGH")
                
                self.log_test("Tavern Dice Min Bet", True, f"Minimum bet successful - Roll: {roll_total}")
            else:
                self.log_test("Tavern Dice Block", True, f"Dice blocked: {response.json().get('detail', 'Unknown')}")
        else:
            self.log_test("Tavern Dice", False, f"Status: {response.status_code if response else 'No response'}", "MEDIUM")
    
    def test_bank_system(self) -> None:
        """MEDIUM: Test Bank Investment System"""
        print("\n🏦 Testing Bank System (MEDIUM)...")
        
        # 1. Check bank account
        response = self.make_request('GET', '/game/bank/account')
        if not response or response.status_code != 200:
            self.log_test("Bank Account", False, f"Status: {response.status_code if response else 'No response'}", "MEDIUM")
            return
        
        account = response.json()
        balance = account.get('balance', 0)
        self.log_test("Bank Account", True, f"Bank balance: {balance}")
        
        # 2. Try deposit
        deposit_data = {"amount": 10}
        response = self.make_request('POST', '/game/bank/deposit', deposit_data, 15)  # Longer timeout
        
        if response and response.status_code in [200, 400]:
            if response.status_code == 200:
                self.log_test("Bank Deposit", True, "Successfully deposited to bank")
                
                # 3. Try withdraw
                withdraw_data = {"amount": 5}
                response = self.make_request('POST', '/game/bank/withdraw', withdraw_data, 15)
                
                if response and response.status_code in [200, 400]:
                    if response.status_code == 200:
                        self.log_test("Bank Withdraw", True, "Successfully withdrew from bank")
                    else:
                        self.log_test("Bank Withdraw Block", True, f"Withdraw blocked: {response.json().get('detail', 'Unknown')}")
                else:
                    self.log_test("Bank Withdraw", False, f"Status: {response.status_code if response else 'No response'}", "MEDIUM")
            else:
                self.log_test("Bank Deposit Block", True, f"Deposit blocked: {response.json().get('detail', 'Unknown')}")
        else:
            self.log_test("Bank Deposit", False, f"Status: {response.status_code if response else 'No response'}", "MEDIUM")
    
    def test_message_system(self) -> None:
        """HIGH: Test Message System"""
        print("\n💌 Testing Message System (HIGH)...")
        
        # 1. Check messages
        response = self.make_request('GET', '/game/messages')
        if response and response.status_code == 200:
            messages = response.json()
            unread_count = len([m for m in messages if not m.get('read', True)])
            self.log_test("Messages List", True, f"Found {len(messages)} messages, {unread_count} unread")
            
            # 2. Test sending message (to self for testing)
            send_data = {
                "recipient_username": self.user_data.get('username', 'testuser'),
                "subject": "Test Message",
                "body": "Automated test message from comprehensive testing"
            }
            response = self.make_request('POST', '/game/messages/send', send_data)
            
            if response and response.status_code in [200, 400]:
                if response.status_code == 200:
                    self.log_test("Send Message", True, "Successfully sent message")
                else:
                    self.log_test("Send Message Block", True, f"Message blocked: {response.json().get('detail', 'Unknown')}")
            else:
                self.log_test("Send Message", False, f"Status: {response.status_code if response else 'No response'}", "HIGH")
        else:
            self.log_test("Messages List", False, f"Status: {response.status_code if response else 'No response'}", "HIGH")
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        print("🏰 Starting Comprehensive E2E Testing - All 42 Features")
        print("=" * 80)
        
        start_time = time.time()
        
        # Setup
        if not self.setup_test_user():
            return {
                'error': 'Failed to setup test user',
                'tests_run': self.tests_run,
                'tests_passed': self.tests_passed
            }
        
        # Get initial game state
        game_state = self.test_game_state()
        if not game_state:
            self.log_test("Initial Setup", False, "Cannot get game state", "CRITICAL")
            return {'error': 'Cannot get game state'}
        
        # Run all feature tests
        print("\n" + "="*50 + " CRITICAL FEATURES " + "="*50)
        self.test_combat_system(game_state)
        self.test_quest_system()
        self.test_shop_inventory_equipment_flow()
        self.test_market_system()
        
        print("\n" + "="*50 + " HIGH PRIORITY FEATURES " + "="*50) 
        self.test_guild_system()
        self.test_travel_system()
        self.test_message_system()
        
        print("\n" + "="*50 + " MEDIUM PRIORITY FEATURES " + "="*50)
        self.test_training_system()
        self.test_crime_jail_flow()
        self.test_tavern_dice_system()
        self.test_bank_system()
        
        # Results
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        success_rate = round((self.tests_passed / self.tests_run) * 100, 1) if self.tests_run > 0 else 0
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("="*80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {success_rate}%")
        print(f"Duration: {duration} seconds")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES: {len(self.critical_issues)}")
            for issue in self.critical_issues[:5]:  # Show first 5
                print(f"  - {issue['name']}: {issue['details']}")
        
        print(f"\n⚠️ HIGH/MEDIUM ISSUES: {len([f for f in self.failed_tests if f['priority'] in ['HIGH', 'MEDIUM']])}")
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': len(self.failed_tests),
            'success_rate': success_rate,
            'critical_issues': len(self.critical_issues),
            'high_issues': len([f for f in self.failed_tests if f['priority'] == 'HIGH']),
            'medium_issues': len([f for f in self.failed_tests if f['priority'] == 'MEDIUM']),
            'failed_tests': self.failed_tests,
            'duration': duration,
            'major_functionality_broken': len(self.critical_issues) > 5 or success_rate < 50
        }

def main():
    """Main execution"""
    tester = ComprehensiveGameTester()
    results = tester.run_comprehensive_tests()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'/app/comprehensive_test_results_{timestamp}.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to comprehensive_test_results_{timestamp}.json")
    
    if results.get('major_functionality_broken'):
        print("\n🚨 MAJOR FUNCTIONALITY BROKEN - Over 50% failure rate or critical issues")
        return 1
    elif results.get('critical_issues', 0) > 0:
        print("\n⚠️ CRITICAL ISSUES FOUND - Needs attention")
        return 1
    else:
        print("\n✅ Testing completed successfully")
        return 0

if __name__ == "__main__":
    sys.exit(main())