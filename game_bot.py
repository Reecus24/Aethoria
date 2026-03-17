#!/usr/bin/env python3
"""
Realm of Aethoria - Persistent Game Bot
Runs 5 AI players continuously in the background.
"""
import requests
import time
import random
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('/tmp/game_bot.log'),
        logging.StreamHandler()
    ]
)

BASE_URL = 'https://dragon-quest-46.preview.emergentagent.com/api'

# Generate unique bot names each run
rand = random.randint(1000, 9999)
BOT_CHARACTERS = [
    {'username': f'Aldric{rand}', 'email': f'aldric{rand}@realm.de', 'password': 'Bot123', 'path': 'knight'},
    {'username': f'Selene{rand}', 'email': f'selene{rand}@realm.de', 'password': 'Bot123', 'path': 'shadow'},
    {'username': f'Theron{rand}', 'email': f'theron{rand}@realm.de', 'password': 'Bot123', 'path': 'noble'},
    {'username': f'Lyra{rand}', 'email': f'lyra{rand}@realm.de', 'password': 'Bot123', 'path': 'shadow'},
    {'username': f'Magnus{rand}', 'email': f'magnus{rand}@realm.de', 'password': 'Bot123', 'path': 'knight'},
]

class Bot:
    def __init__(self, char):
        self.char = char
        self.name = char['username']
        self.token = None
        self.headers = {}
        self.logger = logging.getLogger(self.name)
        self.action_count = 0
    
    def register(self):
        """Register bot"""
        try:
            res = requests.post(f'{BASE_URL}/auth/register', json={
                'username': self.char['username'],
                'email': self.char['email'],
                'password': self.char['password'],
                'path_choice': self.char['path']
            }, timeout=15)
            
            if res.status_code == 200:
                self.token = res.json()['token']
                self.headers = {'Authorization': f'Bearer {self.token}'}
                self.logger.info(f"Registered as {self.char['path'].upper()}")
                return True
            else:
                self.logger.error(f"Registration failed: {res.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return False
    
    def get_state(self):
        """Get game state"""
        try:
            res = requests.get(f'{BASE_URL}/game/state', headers=self.headers, timeout=10)
            if res.status_code == 200:
                return res.json()
            return None
        except:
            return None
    
    def do_action(self):
        """Perform a random game action"""
        state = self.get_state()
        if not state:
            return False
        
        energy = state['resources']['energy']
        can_act = state['status']['can_act']
        level = state['level']
        gold = state['resources']['gold']
        
        if not can_act:
            self.logger.info("Cannot act - timer active")
            return False
        
        if energy < 5:
            self.logger.info(f"Low energy: {energy}/100 - resting")
            return False
        
        # Choose action (weighted random)
        actions = []
        if energy >= 3:
            actions.extend(['crime'] * 5)  # 50% chance
        if energy >= 6:
            actions.extend(['training'] * 3)  # 30% chance
        if gold >= 10:
            actions.extend(['shop'] * 1)  # 10% chance
        if energy >= 10:
            actions.extend(['quest'] * 1)  # 10% chance
        
        if not actions:
            return False
        
        action = random.choice(actions)
        
        # Execute action
        if action == 'crime':
            return self.do_crime(level, energy)
        elif action == 'training':
            return self.do_training()
        elif action == 'shop':
            return self.do_shop(gold)
        elif action == 'quest':
            return self.do_quest(level, energy)
        
        return False
    
    def do_crime(self, level, energy):
        """Commit appropriate crime"""
        crimes = ['steal_bread']
        if level >= 2:
            crimes.extend(['rob_drunk', 'pickpocket'])
        if level >= 4 and energy >= 8:
            crimes.append('burglary')
        
        crime_id = random.choice(crimes)
        
        try:
            res = requests.post(f'{BASE_URL}/game/crimes/commit',
                              headers=self.headers,
                              json={'crime_id': crime_id},
                              timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                if data.get('success'):
                    rewards = data.get('rewards', {})
                    self.logger.info(f"Crime success: {crime_id} | +{rewards.get('gold')}g")
                    self.action_count += 1
                    return True
                else:
                    self.logger.info(f"Crime failed: {crime_id} - caught!")
                    return True
        except:
            pass
        return False
    
    def do_training(self):
        """Start training"""
        stat = random.choice(['strength', 'dexterity', 'speed', 'defense'])
        try:
            res = requests.post(f'{BASE_URL}/game/training/start',
                              headers=self.headers,
                              json={'stat': stat},
                              timeout=10)
            if res.status_code == 200:
                self.logger.info(f"Training: {stat}")
                self.action_count += 1
                return True
        except:
            pass
        return False
    
    def do_shop(self, gold):
        """Buy from shop"""
        if gold < 10:
            return False
        
        items = ['bread'] if gold < 20 else ['bread', 'potion_minor']
        item = random.choice(items)
        
        try:
            res = requests.post(f'{BASE_URL}/game/shop/buy?item_id={item}&quantity=1',
                              headers=self.headers,
                              timeout=10)
            if res.status_code == 200:
                self.logger.info(f"Shop: bought {item}")
                self.action_count += 1
                return True
        except:
            pass
        return False
    
    def do_quest(self, level, energy):
        """Accept a quest"""
        try:
            res = requests.get(f'{BASE_URL}/game/quests/available', headers=self.headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                available = data.get('available_quests', [])
                suitable = [q for q in available if q['min_level'] <= level and q['energy_cost'] <= energy]
                
                if suitable:
                    quest = random.choice(suitable)
                    res2 = requests.post(f'{BASE_URL}/game/quests/accept',
                                       headers=self.headers,
                                       json={'quest_id': quest['id']},
                                       timeout=10)
                    if res2.status_code == 200:
                        self.logger.info(f"Quest: {quest['name']}")
                        self.action_count += 1
                        return True
        except:
            pass
        return False


def main():
    print("=" * 70)
    print("🎮 REALM OF AETHORIA - PERSISTENT GAME BOT")
    print("=" * 70)
    print(f"🤖 Registering 5 AI players...\n")
    
    # Register bots
    bots = []
    for char in BOT_CHARACTERS:
        bot = Bot(char)
        if bot.register():
            bots.append(bot)
            time.sleep(1.5)
    
    print(f"\n✅ {len(bots)} bots active: {', '.join([b.name for b in bots])}")
    print(f"🎯 Starting infinite gameplay loop...")
    print(f"   ⏱️  Actions every 8-15 seconds per bot")
    print(f"   💾 Logs: /tmp/game_bot.log\n")
    
    round_num = 0
    try:
        while True:
            round_num += 1
            
            if round_num % 10 == 0:
                total_actions = sum(b.action_count for b in bots)
                print(f"\n📊 Stats after {round_num} rounds: {total_actions} total actions")
            
            # Each bot takes a turn
            for bot in bots:
                try:
                    bot.do_action()
                    time.sleep(random.randint(8, 15))  # Realistic pacing
                except Exception as e:
                    bot.logger.error(f"Action error: {e}")
            
            # Brief pause between rounds
            time.sleep(random.randint(20, 40))
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Bot stopped")
        print(f"   Rounds: {round_num}")
        print(f"   Actions: {sum(b.action_count for b in bots)}")

if __name__ == '__main__':
    main()
