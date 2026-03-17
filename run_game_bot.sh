#!/bin/bash
# Game Bot Runner - Keeps 5 AI players active
# Runs in a loop, executing bot actions every 2-3 minutes

cd /app

while true; do
    echo "$(date '+%H:%M:%S') - Starting bot round..."
    
    python3 -c "
import requests, time, random

BASE = 'https://dragon-quest-46.preview.emergentagent.com/api'

# Use existing bots (already registered)
bots = [
    ('Aldric8883', 'aldric8883@bot.de'),
    ('Selene8883', 'selene8883@bot.de'),
    ('Theron8883', 'theron8883@bot.de'),
    ('Lyra8883', 'lyra8883@bot.de'),
    ('Magnus8883', 'magnus8883@bot.de'),
]

active_bots = []
for name, email in bots:
    try:
        # Login
        res = requests.post(f'{BASE}/auth/login', json={'email': email, 'password': 'Bot123'}, timeout=10)
        if res.status_code == 200:
            token = res.json()['token']
            active_bots.append({'name': name, 'headers': {'Authorization': f'Bearer {token}'}})
    except:
        # If login fails, try to register
        try:
            path = 'knight' if 'Aldric' in name or 'Magnus' in name else 'shadow' if 'Selene' in name or 'Lyra' in name else 'noble'
            res = requests.post(f'{BASE}/auth/register', json={
                'username': name,
                'email': email,
                'password': 'Bot123',
                'path_choice': path
            }, timeout=10)
            if res.status_code == 200:
                token = res.json()['token']
                active_bots.append({'name': name, 'headers': {'Authorization': f'Bearer {token}'}})
        except:
            pass

print(f'{len(active_bots)}/5 bots active')

# Each bot does 1-2 actions
for bot in active_bots:
    try:
        # Get state
        state = requests.get(f'{BASE}/game/state', headers=bot['headers'], timeout=10).json()
        energy = state.get('resources', {}).get('energy', 0)
        can_act = state.get('status', {}).get('can_act', False)
        
        if not can_act or energy < 5:
            continue
        
        # Random action
        action = random.choices(['crime', 'training', 'shop'], weights=[60, 30, 10])[0]
        
        if action == 'crime' and energy >= 3:
            requests.post(f'{BASE}/game/crimes/commit', headers=bot['headers'], json={'crime_id': random.choice(['steal_bread', 'rob_drunk'])}, timeout=10)
        elif action == 'training' and energy >= 6:
            requests.post(f'{BASE}/game/training/start', headers=bot['headers'], json={'stat': random.choice(['strength', 'speed', 'defense'])}, timeout=10)
        elif action == 'shop':
            requests.post(f'{BASE}/game/shop/buy?item_id=bread&quantity=1', headers=bot['headers'], timeout=10)
        
        time.sleep(random.randint(2, 4))
    except:
        pass

print('Bot round complete')
" >> /tmp/game_bot_daemon.log 2>&1
    
    # Wait 2-3 minutes between rounds
    sleep $((120 + RANDOM % 60))
done
