#!/usr/bin/env python3
"""
Aethoria Game Bot - Automated Testing
3 Bots spielen automatisch das Spiel durch und suchen nach Bugs
"""
import requests
import time
import random
import json
from datetime import datetime
from typing import List, Dict

class AethoriaBot:
    def __init__(self, path_choice: str, bot_name: str, base_url="https://dragon-quest-46.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.path = path_choice
        self.bot_name = bot_name
        self.token = None
        self.user_id = None
        self.bugs_found = []
        self.actions_performed = []
        self.current_level = 1
        
    def log_action(self, action: str, success: bool, details: str = ""):
        """Log bot action"""
        self.actions_performed.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'success': success,
            'details': details,
            'level': self.current_level
        })
        status = "✅" if success else "❌"
        print(f"{status} [{self.bot_name}] {action}: {details}")
    
    def log_bug(self, category: str, description: str, severity: str, evidence: dict):
        """Log discovered bug"""
        bug = {
            'timestamp': datetime.now().isoformat(),
            'bot': self.bot_name,
            'path': self.path,
            'category': category,
            'severity': severity,
            'description': description,
            'evidence': evidence,
            'level_when_found': self.current_level
        }
        self.bugs_found.append(bug)
        print(f"🐛 [{self.bot_name}] BUG FOUND ({severity}): {description}")
    
    def register(self):
        """Register new bot user"""
        timestamp = str(int(time.time() * 1000))[-8:]
        bot_prefix = self.bot_name[:3].lower()  # Just first 3 chars
        username = f"bot{bot_prefix}{timestamp}"
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json={
                'username': username,
                'email': f'{bot_prefix}{timestamp}@gamebot.com',
                'password': 'botpass123',
                'path_choice': self.path
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.user_id = data['user']['id']
                self.log_action("Register", True, f"Created {username} as {self.path}")
                return True
            else:
                self.log_action("Register", False, f"Status {response.status_code}: {response.text[:100]}")
                return False
        except Exception as e:
            self.log_action("Register", False, str(e))
            return False
    
    def get_state(self) -> dict:
        """Get current game state"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{self.base_url}/game/state", headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}
    
    def test_training_system(self):
        """Test training multiple stats"""
        print(f"\n🏋️ [{self.bot_name}] Testing Training System...")
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Try training 2 different stats
        stats_to_train = ['strength', 'dexterity']
        trained_count = 0
        
        for stat in stats_to_train:
            try:
                response = requests.post(
                    f"{self.base_url}/game/training/start",
                    headers=headers,
                    json={'stat': stat, 'duration_hours': 1},
                    timeout=10
                )
                
                if response.status_code == 200:
                    trained_count += 1
                    self.log_action(f"Train {stat}", True, "Started training")
                elif response.status_code == 400 and trained_count == 0:
                    # First training failed - that's a bug
                    self.log_bug(
                        'Training', 
                        f'Cannot start training {stat}: {response.json().get("detail")}',
                        'HIGH',
                        {'stat': stat, 'response': response.json()}
                    )
            except Exception as e:
                self.log_bug('Training', f'Training API error: {str(e)}', 'CRITICAL', {})
        
        if trained_count < 2:
            self.log_bug(
                'Training',
                f'Only able to train {trained_count}/2 stats simultaneously',
                'HIGH',
                {'trained_count': trained_count}
            )
    
    def test_equipment_system(self):
        """Test buying and equipping items"""
        print(f"\n⚔️ [{self.bot_name}] Testing Equipment System...")
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Get shop items
        try:
            shop_response = requests.get(f"{self.base_url}/game/shop/items", headers=headers, timeout=10)
            items = shop_response.json()
            
            if not items:
                self.log_bug('Shop', 'Shop is empty', 'CRITICAL', {})
                return
            
            # Try to buy a weapon
            weapon = next((i for i in items if i.get('slot') == 'weapon'), None)
            if weapon:
                buy_response = requests.post(
                    f"{self.base_url}/game/shop/buy?item_id={weapon['id']}&quantity=1",
                    headers=headers,
                    timeout=10
                )
                
                if buy_response.status_code == 200:
                    self.log_action("Buy weapon", True, weapon['name'])
                    
                    # Try to equip it
                    time.sleep(0.5)
                    equip_response = requests.post(
                        f"{self.base_url}/game/inventory/equip",
                        headers=headers,
                        json={'item_id': weapon['id'], 'slot': 'weapon'},
                        timeout=10
                    )
                    
                    if equip_response.status_code == 200:
                        self.log_action("Equip weapon", True, weapon['name'])
                        
                        # Check if still in inventory
                        time.sleep(0.5)
                        inv_response = requests.get(f"{self.base_url}/game/inventory", headers=headers, timeout=10)
                        inventory = inv_response.json().get('inventory', [])
                        
                        weapon_in_inv = any(i['item_id'] == weapon['id'] for i in inventory)
                        if not weapon_in_inv:
                            self.log_bug(
                                'Equipment',
                                f'Equipped item {weapon["name"]} disappeared from inventory',
                                'HIGH',
                                {'weapon_id': weapon['id']}
                            )
                        else:
                            self.log_action("Verify inventory", True, "Equipped item still in inventory")
                    else:
                        self.log_bug(
                            'Equipment',
                            f'Cannot equip {weapon["name"]}: {equip_response.json().get("detail")}',
                            'HIGH',
                            {'response': equip_response.json()}
                        )
                else:
                    self.log_action("Buy weapon", False, f"Status {buy_response.status_code}")
                    
        except Exception as e:
            self.log_bug('Equipment', f'Equipment test error: {str(e)}', 'MEDIUM', {})
    
    def test_combat_system(self, target_username: str = None):
        """Test combat and mugging"""
        print(f"\n⚔️ [{self.bot_name}] Testing Combat System...")
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Get online players
        try:
            players_response = requests.get(f"{self.base_url}/game/players/online", headers=headers, timeout=10)
            players = players_response.json()
            
            if len(players) < 2:
                self.log_action("Combat test", False, "Not enough players online")
                return
            
            # Find a target (not self)
            target = next((p for p in players if p['username'] != self.bot_name.split('Bot')[0]), None)
            if not target:
                self.log_action("Combat test", False, "No valid target found")
                return
            
            # Get initial HP
            initial_state = self.get_state()
            initial_hp = initial_state.get('resources', {}).get('hp', 100)
            
            # Test mugging (for Shadow class)
            if self.path == 'shadow':
                mug_response = requests.post(
                    f"{self.base_url}/game/combat",
                    headers=headers,
                    json={'target_id': target['id'], 'action': 'mug'},
                    timeout=10
                )
                
                if mug_response.status_code == 200:
                    result = mug_response.json()
                    damage_taken = result.get('damage', 0)
                    
                    # Check if we took damage on failed mug
                    if not result.get('victory') and damage_taken > 0:
                        self.log_bug(
                            'Combat',
                            f'Mugging failure caused {damage_taken} damage (should be 0)',
                            'HIGH',
                            {'result': result, 'initial_hp': initial_hp}
                        )
                    elif result.get('victory'):
                        self.log_action("Mug success", True, f"Stole {result.get('gold_stolen', 0)} gold")
                    else:
                        self.log_action("Mug failed", True, f"No damage taken (correct!)")
                        
        except Exception as e:
            self.log_bug('Combat', f'Combat test error: {str(e)}', 'MEDIUM', {})
    
    def test_xp_and_leveling(self):
        """Test XP display and leveling"""
        print(f"\n⭐ [{self.bot_name}] Testing XP System...")
        state = self.get_state()
        
        xp_current = state.get('resources', {}).get('xp', 0)
        xp_required = state.get('resources', {}).get('xp_required', 0)
        level = state.get('user', {}).get('level', 1)
        
        # Check if XP display makes sense
        if xp_required == 0 and level < 20:
            self.log_bug(
                'XP System',
                f'XP required is 0 at level {level} (should show next level requirement)',
                'MEDIUM',
                {'xp_current': xp_current, 'xp_required': xp_required, 'level': level}
            )
        elif xp_required == 100 and xp_current == 0 and level > 1:
            self.log_bug(
                'XP System',
                f'XP still shows 0/100 at level {level}',
                'HIGH',
                {'xp_current': xp_current, 'xp_required': xp_required}
            )
        else:
            self.log_action("XP display", True, f"{xp_current}/{xp_current + xp_required} at level {level}")
            self.current_level = level
    
    def play_game_loop(self, iterations: int = 5):
        """Main game loop - perform random actions"""
        print(f"\n🎮 [{self.bot_name}] Starting game loop for {iterations} iterations...")
        
        for i in range(iterations):
            print(f"\n--- Iteration {i+1}/{iterations} ---")
            
            # Simple actions without full implementation
            try:
                state = self.get_state()
                self.log_action("Game loop iteration", True, f"Level {state.get('user', {}).get('level', 1)}")
            except:
                pass
            
            time.sleep(random.uniform(0.5, 1.5))
    
    def attempt_crime(self):
        """Attempt a crime"""
        headers = {'Authorization': f'Bearer {self.token}'}
        crimes = ['pickpocket', 'burglary', 'robbery']
        crime_id = random.choice(crimes)
        
        try:
            response = requests.post(
                f"{self.base_url}/game/crimes/attempt",
                headers=headers,
                json={'crime_id': crime_id},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                self.log_action("Crime", result.get('success', False), crime_id)
        except:
            pass
    
    def attempt_training(self):
        """Start training a random stat"""
        headers = {'Authorization': f'Bearer {self.token}'}
        stat = random.choice(['strength', 'dexterity', 'speed', 'defense'])
        
        try:
            response = requests.post(
                f"{self.base_url}/game/training/start",
                headers=headers,
                json={'stat': stat, 'duration_hours': 1},
                timeout=10
            )
            if response.status_code == 200:
                self.log_action("Training", True, f"Started {stat}")
        except:
            pass
    
    def attempt_shop(self):
        """Try to buy something from shop"""
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            state = self.get_state()
            gold = state.get('resources', {}).get('gold', 0)
            
            if gold < 50:
                return
            
            shop = requests.get(f"{self.base_url}/game/shop/items", headers=headers, timeout=10)
            items = shop.json()
            
            affordable = [i for i in items if i['price'] <= gold]
            if affordable:
                item = random.choice(affordable)
                response = requests.post(
                    f"{self.base_url}/game/shop/buy?item_id={item['id']}&quantity=1",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    self.log_action("Shop purchase", True, item['name'])
        except:
            pass

    
    def test_travel_system(self):
        """Test travel to different kingdoms"""
        print(f"\n🗺️ [{self.bot_name}] Testing Travel System...")
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            # Get current state
            state = self.get_state()
            current_level = state.get('user', {}).get('level', 1)
            current_location = state.get('location', {}).get('kingdom_id', 'aethoria_capital')
            gold = state.get('resources', {}).get('gold', 0)
            
            # Get all kingdoms
            kingdoms = [
                {'id': 'aethoria_capital', 'name': 'Aethoria Prime', 'min_level': 1, 'travel_cost': 0},
                {'id': 'shadowfen', 'name': 'Shadowfen', 'min_level': 2, 'travel_cost': 50},
                {'id': 'ironhold', 'name': 'Ironhold', 'min_level': 3, 'travel_cost': 50},
            ]
            
            # Find kingdoms we SHOULD be able to travel to
            accessible = [k for k in kingdoms if k['min_level'] <= current_level and k['id'] != current_location and k['travel_cost'] <= gold]
            
            if accessible:
                target = accessible[0]
                print(f"  Trying to travel to {target['name']} (Level {target['min_level']} required, we are Level {current_level})")
                
                travel = requests.post(
                    f"{self.base_url}/game/travel",
                    headers=headers,
                    json={'kingdom_id': target['id']},
                    timeout=10
                )
                
                if travel.status_code == 200:
                    self.log_action("Travel", True, f"Started travel to {target['name']}")
                elif travel.status_code == 400:
                    error = travel.json().get('detail', '')
                    if 'Level' in error:
                        # We have the level but can't travel - BUG!
                        self.log_bug(
                            'Travel',
                            f"Cannot travel despite meeting requirements: Level {current_level}, Target requires Level {target['min_level']}. Error: {error}",
                            'HIGH',
                            {'current_level': current_level, 'target': target, 'error': error}
                        )
                    else:
                        self.log_action("Travel", False, error)
            else:
                self.log_action("Travel test", False, f"No accessible kingdoms at level {current_level} with {gold} gold")
                
        except Exception as e:
            self.log_bug('Travel', f'Travel test error: {str(e)}', 'MEDIUM', {})
        """Try to buy something from shop"""
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            state = self.get_state()
            gold = state.get('resources', {}).get('gold', 0)
            
            if gold < 50:
                return
            
            shop = requests.get(f"{self.base_url}/game/shop/items", headers=headers, timeout=10)
            items = shop.json()
            
            affordable = [i for i in items if i['price'] <= gold]
            if affordable:
                item = random.choice(affordable)
                response = requests.post(
                    f"{self.base_url}/game/shop/buy?item_id={item['id']}&quantity=1",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    self.log_action("Shop purchase", True, item['name'])
        except:
            pass

def run_bot_testing():
    """Run all 3 bots and collect bugs"""
    print("=" * 70)
    print("🤖 AETHORIA AUTOMATED BOT TESTING")
    print("=" * 70)
    print("Starting 3 bots (Knight, Shadow, Noble) to test the game...\n")
    
    # Create bots
    knight_bot = AethoriaBot('knight', 'KnightBot')
    shadow_bot = AethoriaBot('shadow', 'ShadowBot')
    noble_bot = AethoriaBot('noble', 'NobleBot')
    
    bots = [knight_bot, shadow_bot, noble_bot]
    
    # Phase 1: Register all bots
    print("\n📝 PHASE 1: Registration")
    print("-" * 70)
    for bot in bots:
        if not bot.register():
            print(f"❌ Failed to register {bot.bot_name}")
            return
        time.sleep(0.5)
    
    # Phase 2: Core systems testing
    print("\n🧪 PHASE 2: Core Systems Testing")
    print("-" * 70)
    
    for bot in bots:
        bot.test_xp_and_leveling()
        time.sleep(0.5)
        bot.test_training_system()
        time.sleep(0.5)
        bot.test_equipment_system()
        time.sleep(0.5)
        bot.test_travel_system()
        time.sleep(1)
    
    # Phase 3: Combat testing (Shadow vs Knight)
    print("\n⚔️ PHASE 3: Combat Testing")
    print("-" * 70)
    shadow_bot.test_combat_system()
    
    # Phase 4: Game loop simulation
    print("\n🎮 PHASE 4: Game Loop Simulation")
    print("-" * 70)
    for bot in bots:
        bot.play_game_loop(iterations=5)
        time.sleep(1)
    
    # Collect all bugs
    all_bugs = []
    all_actions = []
    
    for bot in bots:
        all_bugs.extend(bot.bugs_found)
        all_actions.extend(bot.actions_performed)
    
    # Generate report
    print("\n" + "=" * 70)
    print("📊 TESTING COMPLETE - GENERATING REPORT")
    print("=" * 70)
    
    report = {
        'test_date': datetime.now().isoformat(),
        'bots_run': len(bots),
        'total_actions': len(all_actions),
        'bugs_found': len(all_bugs),
        'bugs_by_severity': {
            'CRITICAL': [b for b in all_bugs if b['severity'] == 'CRITICAL'],
            'HIGH': [b for b in all_bugs if b['severity'] == 'HIGH'],
            'MEDIUM': [b for b in all_bugs if b['severity'] == 'MEDIUM'],
            'LOW': [b for b in all_bugs if b['severity'] == 'LOW']
        },
        'all_bugs': all_bugs,
        'bot_summaries': [
            {
                'bot': bot.bot_name,
                'path': bot.path,
                'actions': len(bot.actions_performed),
                'bugs': len(bot.bugs_found)
            }
            for bot in bots
        ]
    }
    
    # Save report
    report_path = '/app/bot_test_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report saved: {report_path}")
    print(f"\n📋 SUMMARY:")
    print(f"  - Bots run: {len(bots)}")
    print(f"  - Total actions: {len(all_actions)}")
    print(f"  - Bugs found: {len(all_bugs)}")
    print(f"    • CRITICAL: {len(report['bugs_by_severity']['CRITICAL'])}")
    print(f"    • HIGH: {len(report['bugs_by_severity']['HIGH'])}")
    print(f"    • MEDIUM: {len(report['bugs_by_severity']['MEDIUM'])}")
    print(f"    • LOW: {len(report['bugs_by_severity']['LOW'])}")
    
    if all_bugs:
        print(f"\n🐛 BUG DETAILS:")
        for bug in all_bugs:
            print(f"  [{bug['severity']}] {bug['category']}: {bug['description']}")
    
    return report

if __name__ == "__main__":
    try:
        report = run_bot_testing()
        print("\n" + "=" * 70)
        print("✅ Bot testing completed successfully")
        print("=" * 70)
    except KeyboardInterrupt:
        print("\n⚠️  Bot testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Bot testing failed: {str(e)}")
        import traceback
        traceback.print_exc()
