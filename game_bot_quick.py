#!/usr/bin/env python3
"""
Realm of Aethoria - Game Bot (Quick Start Version)
Simulates 5 AI players performing realistic game actions.
"""
import requests
import time
import random

BASE_URL = 'https://dragon-quest-46.preview.emergentagent.com/api'

# Bot character names (medieval fantasy themed with random suffix)
import random
rand_suffix = random.randint(1000, 9999)
BOT_CHARACTERS = [
    {'username': f'Aldric{rand_suffix}', 'email': f'aldric{rand_suffix}@realm.de', 'password': 'Bot123', 'path': 'knight'},
    {'username': f'Selene{rand_suffix}', 'email': f'selene{rand_suffix}@realm.de', 'password': 'Bot123', 'path': 'shadow'},
    {'username': f'Theron{rand_suffix}', 'email': f'theron{rand_suffix}@realm.de', 'password': 'Bot123', 'path': 'noble'},
    {'username': f'Lyra{rand_suffix}', 'email': f'lyra{rand_suffix}@realm.de', 'password': 'Bot123', 'path': 'shadow'},
    {'username': f'Magnus{rand_suffix}', 'email': f'magnus{rand_suffix}@realm.de', 'password': 'Bot123', 'path': 'knight'},
]

def register_bot(char):
    """Register a bot character"""
    try:
        res = requests.post(f'{BASE_URL}/auth/register', json={
            'username': char['username'],
            'email': char['email'],
            'password': char['password'],
            'path_choice': char['path']
        }, timeout=15)  # Increased timeout
        
        if res.status_code == 200:
            token = res.json()['token']
            print(f"✓ {char['username']} registered as {char['path'].upper()}")
            return {'name': char['username'], 'token': token, 'headers': {'Authorization': f'Bearer {token}'}}
        else:
            print(f"✗ {char['username']} failed: {res.status_code} - {res.text[:100]}")
            return None
    except Exception as e:
        print(f"✗ {char['username']} error: {e}")
        return None

def bot_action(bot, action_type):
    """Perform a single action"""
    try:
        if action_type == 'crime':
            crime_id = random.choice(['steal_bread', 'rob_drunk', 'pickpocket'])
            res = requests.post(f'{BASE_URL}/game/crimes/commit', 
                              headers=bot['headers'], 
                              json={'crime_id': crime_id},
                              timeout=10)
            if res.status_code == 200 and res.json().get('success'):
                print(f"   ✓ {bot['name']}: Crime successful (+{res.json()['rewards']['gold']}g)")
            return True
            
        elif action_type == 'training':
            stat = random.choice(['strength', 'dexterity', 'speed', 'defense'])
            res = requests.post(f'{BASE_URL}/game/training/start',
                              headers=bot['headers'],
                              json={'stat': stat},
                              timeout=10)
            if res.status_code == 200:
                print(f"   ✓ {bot['name']}: Training {stat}")
            return True
            
        elif action_type == 'shop':
            item = random.choice(['bread', 'potion_minor'])
            res = requests.post(f'{BASE_URL}/game/shop/buy?item_id={item}&quantity=1',
                              headers=bot['headers'],
                              timeout=10)
            if res.status_code == 200:
                print(f"   ✓ {bot['name']}: Bought {item}")
            return True
            
    except:
        pass
    return False

def main():
    print("=" * 60)
    print("🎮 REALM OF AETHORIA - GAME BOT (Quick Start)")
    print("=" * 60)
    
    # Register bots
    bots = []
    for char in BOT_CHARACTERS:
        bot = register_bot(char)
        if bot:
            bots.append(bot)
        time.sleep(1)
    
    print(f"\n✅ {len(bots)} bots active!\n")
    
    # Run 3 rounds of actions
    for round_num in range(1, 4):
        print(f"\n🔄 Round {round_num}:")
        for bot in bots:
            action = random.choice(['crime', 'crime', 'training', 'shop'])  # Crimes more likely
            bot_action(bot, action)
            time.sleep(random.randint(2, 4))
        
        if round_num < 3:
            print(f"\n⏳ Waiting 15 seconds...")
            time.sleep(15)
    
    print(f"\n✅ Bot session complete! Check the event ticker on the landing page.")

if __name__ == '__main__':
    main()
