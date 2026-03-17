from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient, ASCENDING, DESCENDING
import os
import jwt
import bcrypt
import uuid
import random
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'aethoria-realm-secret-key-change-in-production')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_DAYS = 30

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ.get('DB_NAME', 'aethoria_db')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
users_col = db['users']
events_col = db['events']
reviews_col = db['reviews']
items_col = db['items']
inventories_col = db['inventories']
training_sessions_col = db['training_sessions']
crimes_col = db['crimes']
crime_logs_col = db['crime_logs']
combat_logs_col = db['combat_logs']
quests_col = db['quests']
user_quests_col = db['user_quests']
market_listings_col = db['market_listings']
bank_accounts_col = db['bank_accounts']
guilds_col = db['guilds']
guild_members_col = db['guild_members']
messages_col = db['messages']
hospital_sessions_col = db['hospital_sessions']
dungeon_sessions_col = db['dungeon_sessions']
bounties_col = db['bounties']
properties_col = db['properties']
user_properties_col = db['user_properties']
achievements_col = db['achievements']
user_achievements_col = db['user_achievements']

# Create indexes
users_col.create_index([('email', ASCENDING)], unique=True)
users_col.create_index([('username', ASCENDING)], unique=True)
users_col.create_index([('level', DESCENDING), ('xp', DESCENDING)])
market_listings_col.create_index([('item_id', ASCENDING), ('active', ASCENDING)])
combat_logs_col.create_index([('timestamp', DESCENDING)])

app = FastAPI(title="Realm of Aethoria API")
security = HTTPBearer()

# ============================================================================
# GAME CONSTANTS
# ============================================================================

MAX_ENERGY = 100
ENERGY_REGEN_PER_HOUR = 10
MAX_HP = 100
HP_REGEN_PER_HOUR = 5

TRAINING_COSTS = {
    'strength': {'energy': 10, 'duration_minutes': 5, 'xp': 2},
    'dexterity': {'energy': 10, 'duration_minutes': 5, 'xp': 2},
    'speed': {'energy': 10, 'duration_minutes': 5, 'xp': 2},
    'defense': {'energy': 10, 'duration_minutes': 5, 'xp': 2},
}

LEVEL_XP_REQUIREMENTS = [
    0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200,  # 1-10
    4000, 5000, 6200, 7600, 9200, 11000, 13000, 15200, 17600, 20200,  # 11-20
]

# Path stats bonuses
PATH_BONUSES = {
    'knight': {'strength': 5, 'defense': 5},
    'shadow': {'dexterity': 5, 'speed': 5},
    'noble': {'strength': 2, 'dexterity': 2, 'speed': 2, 'defense': 2},
}

# ============================================================================
# MASTER DATA (Items, Crimes, Quests)
# ============================================================================

MASTER_ITEMS = [
    # Weapons
    {'id': 'sword_iron', 'name': 'Eisenschwert', 'type': 'weapon', 'subtype': 'melee', 'price': 100, 'damage': 15, 'required_level': 1},
    {'id': 'sword_steel', 'name': 'Stahlschwert', 'type': 'weapon', 'subtype': 'melee', 'price': 500, 'damage': 35, 'required_level': 5},
    {'id': 'sword_dragon', 'name': 'Drachenklingenschwert', 'type': 'weapon', 'subtype': 'melee', 'price': 5000, 'damage': 80, 'required_level': 15},
    {'id': 'dagger_rusty', 'name': 'Rostiger Dolch', 'type': 'weapon', 'subtype': 'melee', 'price': 50, 'damage': 10, 'required_level': 1},
    {'id': 'bow_short', 'name': 'Kurzbogen', 'type': 'weapon', 'subtype': 'ranged', 'price': 150, 'damage': 20, 'required_level': 3},
    {'id': 'bow_long', 'name': 'Langbogen', 'type': 'weapon', 'subtype': 'ranged', 'price': 800, 'damage': 45, 'required_level': 8},
    
    # Armor
    {'id': 'armor_leather', 'name': 'Lederrüstung', 'type': 'armor', 'subtype': 'body', 'price': 80, 'defense': 10, 'required_level': 1},
    {'id': 'armor_chain', 'name': 'Kettenhemd', 'type': 'armor', 'subtype': 'body', 'price': 400, 'defense': 25, 'required_level': 5},
    {'id': 'armor_plate', 'name': 'Plattenrüstung', 'type': 'armor', 'subtype': 'body', 'price': 3000, 'defense': 60, 'required_level': 12},
    {'id': 'helmet_iron', 'name': 'Eisenhelm', 'type': 'armor', 'subtype': 'head', 'price': 50, 'defense': 5, 'required_level': 1},
    {'id': 'shield_wooden', 'name': 'Holzschild', 'type': 'armor', 'subtype': 'shield', 'price': 60, 'defense': 8, 'required_level': 1},
    {'id': 'shield_steel', 'name': 'Stahlschild', 'type': 'armor', 'subtype': 'shield', 'price': 600, 'defense': 30, 'required_level': 7},
    
    # Potions
    {'id': 'potion_health_small', 'name': 'Kleiner Heiltrank', 'type': 'consumable', 'subtype': 'potion', 'price': 20, 'effect': {'hp': 25}, 'required_level': 1},
    {'id': 'potion_health_medium', 'name': 'Mittlerer Heiltrank', 'type': 'consumable', 'subtype': 'potion', 'price': 50, 'effect': {'hp': 50}, 'required_level': 5},
    {'id': 'potion_energy', 'name': 'Energietrank', 'type': 'consumable', 'subtype': 'potion', 'price': 30, 'effect': {'energy': 25}, 'required_level': 1},
    {'id': 'potion_strength', 'name': 'Stärketrank', 'type': 'consumable', 'subtype': 'buff', 'price': 100, 'effect': {'strength_boost': 10, 'duration_hours': 1}, 'required_level': 8},
    
    # Relics
    {'id': 'relic_ancient_coin', 'name': 'Uralte Münze', 'type': 'relic', 'subtype': 'luck', 'price': 1000, 'effect': {'crime_success_boost': 5}, 'required_level': 10},
    {'id': 'relic_dragon_tooth', 'name': 'Drachenzahn', 'type': 'relic', 'subtype': 'combat', 'price': 8000, 'effect': {'damage_boost': 15}, 'required_level': 18},
    
    # Resources
    {'id': 'bread', 'name': 'Brot', 'type': 'resource', 'subtype': 'food', 'price': 5, 'effect': {'hp': 5}, 'required_level': 1},
    {'id': 'meat', 'name': 'Fleisch', 'type': 'resource', 'subtype': 'food', 'price': 15, 'effect': {'hp': 15}, 'required_level': 1},
]

MASTER_CRIMES = [
    # Level 1-5 crimes
    {'id': 'steal_bread', 'name': 'Brot stehlen', 'description': 'Stehle Brot vom Marktstand', 'energy_cost': 5, 'min_level': 1, 'base_success': 80, 'rewards': {'gold': (5, 15), 'xp': 1}, 'failure': {'jail_minutes': 15}},
    {'id': 'pickpocket', 'name': 'Taschendiebstahl', 'description': 'Stehle die Börse eines Bürgers', 'energy_cost': 8, 'min_level': 2, 'base_success': 65, 'rewards': {'gold': (20, 50), 'xp': 3}, 'failure': {'jail_minutes': 30}},
    {'id': 'burglary', 'name': 'Einbruch', 'description': 'Breche in ein Haus ein', 'energy_cost': 12, 'min_level': 4, 'base_success': 50, 'rewards': {'gold': (50, 150), 'xp': 8}, 'failure': {'jail_minutes': 60, 'gold_fine': 30}},
    {'id': 'rob_merchant', 'name': 'Händler überfallen', 'description': 'Überfalle einen reisenden Händler', 'energy_cost': 15, 'min_level': 6, 'base_success': 45, 'rewards': {'gold': (100, 300), 'xp': 15}, 'failure': {'jail_minutes': 120, 'gold_fine': 80}},
    {'id': 'rob_treasury', 'name': 'Schatzkammer ausrauben', 'description': 'Wage einen Überfall auf die königliche Schatzkammer', 'energy_cost': 25, 'min_level': 10, 'base_success': 30, 'rewards': {'gold': (500, 1500), 'xp': 40}, 'failure': {'jail_minutes': 360, 'gold_fine': 300, 'injury': 20}},
]

MASTER_QUESTS = [
    {'id': 'quest_rats', 'name': 'Rattenplage', 'description': 'Töte 10 Ratten in den Stadtkanälen', 'min_level': 1, 'energy_cost': 15, 'duration_minutes': 20, 'rewards': {'gold': 50, 'xp': 10}},
    {'id': 'quest_escort', 'name': 'Händler-Eskorte', 'description': 'Eskortiere einen Händler sicher durch den Wald', 'min_level': 3, 'energy_cost': 20, 'duration_minutes': 30, 'rewards': {'gold': 100, 'xp': 25}},
    {'id': 'quest_bandit_camp', 'name': 'Banditenlager', 'description': 'Zerstöre ein Banditenlager außerhalb der Stadt', 'min_level': 5, 'energy_cost': 30, 'duration_minutes': 60, 'rewards': {'gold': 250, 'xp': 50, 'item': 'sword_steel'}},
    {'id': 'quest_dragon', 'name': 'Drachen-Bedrohung', 'description': 'Vertreibe einen jungen Drachen aus den Bergen', 'min_level': 15, 'energy_cost': 50, 'duration_minutes': 120, 'rewards': {'gold': 2000, 'xp': 200, 'item': 'relic_dragon_tooth'}},
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_token(user_id: str, username: str) -> str:
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get('user_id')
    user = users_col.find_one({'id': user_id}, {'_id': 0, 'hashed_password': 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Update last_seen
    users_col.update_one({'id': user_id}, {'$set': {'last_seen': datetime.now(timezone.utc)}})
    return user

def calculate_level(xp: int) -> int:
    level = 1
    for threshold in LEVEL_XP_REQUIREMENTS:
        if xp >= threshold:
            level += 1
        else:
            break
    return min(level, len(LEVEL_XP_REQUIREMENTS))

def calculate_xp_for_next_level(current_xp: int, current_level: int) -> int:
    if current_level >= len(LEVEL_XP_REQUIREMENTS):
        return 0
    return LEVEL_XP_REQUIREMENTS[current_level] - current_xp

def regenerate_energy(user: dict) -> int:
    """Calculate current energy based on last regen time"""
    last_energy_regen = user.get('last_energy_regen')
    current_energy = user.get('energy', MAX_ENERGY)
    
    if not last_energy_regen or current_energy >= MAX_ENERGY:
        return min(current_energy, MAX_ENERGY)
    
    now = datetime.now(timezone.utc)
    hours_passed = (now - last_energy_regen).total_seconds() / 3600
    energy_gain = int(hours_passed * ENERGY_REGEN_PER_HOUR)
    
    new_energy = min(current_energy + energy_gain, MAX_ENERGY)
    
    if energy_gain > 0:
        users_col.update_one(
            {'id': user['id']},
            {
                '$set': {
                    'energy': new_energy,
                    'last_energy_regen': now
                }
            }
        )
    
    return new_energy

def regenerate_hp(user: dict) -> int:
    """Calculate current HP based on last regen time or hospital"""
    # Check if in hospital
    hospital_session = hospital_sessions_col.find_one({'user_id': user['id'], 'released': False})
    if hospital_session:
        release_time = hospital_session['release_time']
        if datetime.now(timezone.utc) >= release_time:
            # Release from hospital
            hospital_sessions_col.update_one(
                {'user_id': user['id'], 'released': False},
                {'$set': {'released': True, 'release_time': datetime.now(timezone.utc)}}
            )
            users_col.update_one({'id': user['id']}, {'$set': {'hp': MAX_HP}})
            return MAX_HP
        else:
            # Still in hospital
            return user.get('hp', 0)
    
    last_hp_regen = user.get('last_hp_regen')
    current_hp = user.get('hp', MAX_HP)
    
    if not last_hp_regen or current_hp >= MAX_HP:
        return min(current_hp, MAX_HP)
    
    now = datetime.now(timezone.utc)
    hours_passed = (now - last_hp_regen).total_seconds() / 3600
    hp_gain = int(hours_passed * HP_REGEN_PER_HOUR)
    
    new_hp = min(current_hp + hp_gain, MAX_HP)
    
    if hp_gain > 0:
        users_col.update_one(
            {'id': user['id']},
            {
                '$set': {
                    'hp': new_hp,
                    'last_hp_regen': now
                }
            }
        )
    
    return new_hp

def check_dungeon_status(user: dict) -> Optional[dict]:
    """Check if user is in dungeon"""
    dungeon_session = dungeon_sessions_col.find_one({'user_id': user['id'], 'released': False})
    if dungeon_session:
        release_time = dungeon_session['release_time']
        if datetime.now(timezone.utc) >= release_time:
            # Release from dungeon
            dungeon_sessions_col.update_one(
                {'user_id': user['id'], 'released': False},
                {'$set': {'released': True, 'actual_release': datetime.now(timezone.utc)}}
            )
            return None
        else:
            minutes_remaining = int((release_time - datetime.now(timezone.utc)).total_seconds() / 60)
            return {'in_dungeon': True, 'release_time': release_time, 'minutes_remaining': minutes_remaining}
    return None

def log_event(category: str, message: str, user_id: Optional[str] = None):
    """Log an event to the events collection"""
    event = {
        'id': str(uuid.uuid4()),
        'type': category,
        'event': message,
        'timestamp': datetime.now(timezone.utc),
        'user_id': user_id
    }
    events_col.insert_one(event)
    
    # Keep only last 100 events
    count = events_col.count_documents({})
    if count > 100:
        oldest = list(events_col.find({}, {'_id': 1}).sort('timestamp', ASCENDING).limit(count - 100))
        events_col.delete_many({'_id': {'$in': [doc['_id'] for doc in oldest]}})

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)
    path_choice: Literal['knight', 'shadow', 'noble']

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TrainRequest(BaseModel):
    stat: Literal['strength', 'dexterity', 'speed', 'defense']

class CrimeRequest(BaseModel):
    crime_id: str

class CombatRequest(BaseModel):
    target_username: str
    action: Literal['attack', 'mug', 'hospitalize'] = 'attack'

class QuestRequest(BaseModel):
    quest_id: str

class ReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=10)

class MarketListingCreate(BaseModel):
    item_id: str
    quantity: int = Field(..., ge=1)
    price_per_unit: int = Field(..., ge=1)

class MarketBuyRequest(BaseModel):
    listing_id: str
    quantity: int = Field(..., ge=1)

class BankDepositRequest(BaseModel):
    amount: int = Field(..., ge=1)

class BankWithdrawRequest(BaseModel):
    amount: int = Field(..., ge=1)

class GuildCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., max_length=500)

class MessageSendRequest(BaseModel):
    recipient_username: str
    subject: str = Field(..., max_length=100)
    body: str = Field(..., max_length=2000)

# Response models
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    path: str
    level: int
    xp: int
    gold: int
    energy: int
    hp: int
    stats: dict
    equipment: dict
    location: str
    title: str
    days_in_realm: int
    created_at: datetime

class GameStateResponse(BaseModel):
    user: UserResponse
    timers: dict
    notifications: dict
    in_dungeon: bool
    in_hospital: bool

# ============================================================================
# SEED DATA
# ============================================================================

def seed_initial_data():
    """Seed master data on startup"""
    # Seed items if empty
    if items_col.count_documents({}) == 0:
        items_col.insert_many([{**item, 'id': item['id']} for item in MASTER_ITEMS])
        print("✓ Seeded items collection")
    
    # Seed quests if empty
    if quests_col.count_documents({}) == 0:
        quests_col.insert_many([{**quest, 'id': quest['id']} for quest in MASTER_QUESTS])
        print("✓ Seeded quests collection")
    
    # Seed achievements
    if achievements_col.count_documents({}) == 0:
        default_achievements = [
            {'id': 'first_crime', 'name': 'Erstes Verbrechen', 'description': 'Begehe dein erstes Verbrechen', 'icon': '🗡️'},
            {'id': 'first_level_up', 'name': 'Aufstieg', 'description': 'Erreiche Level 2', 'icon': '⬆️'},
            {'id': 'first_kill', 'name': 'Erster Sieg', 'description': 'Besiege einen Gegner im Kampf', 'icon': '⚔️'},
            {'id': 'merchant', 'name': 'Händler', 'description': 'Verdiene 1000 Gold durch Handel', 'icon': '💰'},
            {'id': 'legend', 'name': 'Legende', 'description': 'Erreiche Level 20', 'icon': '👑'},
        ]
        achievements_col.insert_many(default_achievements)
        print("✓ Seeded achievements collection")

# Run seed on startup
seed_initial_data()

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    # Check existing
    if users_col.find_one({'email': req.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    if users_col.find_one({'username': req.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash password
    hashed = bcrypt.hashpw(req.password.encode('utf-8'), bcrypt.gensalt())
    
    # Path stats
    base_stats = {'strength': 10, 'dexterity': 10, 'speed': 10, 'defense': 10}
    path_bonus = PATH_BONUSES.get(req.path_choice, {})
    for stat, bonus in path_bonus.items():
        base_stats[stat] += bonus
    
    # Path labels
    path_labels = {
        'knight': 'The Knight',
        'shadow': 'The Shadow',
        'noble': 'The Noble'
    }
    
    now = datetime.now(timezone.utc)
    user_id = str(uuid.uuid4())
    
    user = {
        'id': user_id,
        'username': req.username,
        'email': req.email,
        'hashed_password': hashed.decode('utf-8'),
        'path': req.path_choice,
        'path_label': path_labels[req.path_choice],
        'level': 1,
        'xp': 0,
        'gold': 100,  # Starting gold
        'energy': MAX_ENERGY,
        'hp': MAX_HP,
        'stats': base_stats,
        'equipment': {
            'weapon': None,
            'armor': None,
            'helmet': None,
            'shield': None,
        },
        'location': 'aethoria_capital',  # Starting kingdom
        'title': path_labels[req.path_choice],
        'created_at': now,
        'last_seen': now,
        'last_energy_regen': now,
        'last_hp_regen': now,
        'days_in_realm': 0,
    }
    
    users_col.insert_one(user)
    
    # Log event
    log_event('quest', f'{req.username} joined the Realm as {path_labels[req.path_choice]}', user_id)
    
    # Create token
    token = create_token(user_id, req.username)
    
    # Remove sensitive data
    del user['hashed_password']
    del user['_id']
    
    return {
        'success': True,
        'message': f'Welcome to the Realm, {req.username}! Your legend begins now.',
        'token': token,
        'user': user
    }

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    user = users_col.find_one({'email': req.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.checkpw(req.password.encode('utf-8'), user['hashed_password'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last_seen
    users_col.update_one({'id': user['id']}, {'$set': {'last_seen': datetime.now(timezone.utc)}})
    
    # Log event
    log_event('quest', f'{user["username"]} returned to the Realm', user['id'])
    
    token = create_token(user['id'], user['username'])
    
    del user['hashed_password']
    del user['_id']
    
    return {
        'success': True,
        'message': f'Welcome back, {user["username"]}!',
        'token': token,
        'user': user
    }

@app.get("/api/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# ============================================================================
# GAME STATE ENDPOINT
# ============================================================================

@app.get("/api/game/state")
async def get_game_state(current_user: dict = Depends(get_current_user)):
    """Get current game state for HUD/topbar"""
    user_id = current_user['id']
    
    # Regenerate resources
    energy = regenerate_energy(current_user)
    hp = regenerate_hp(current_user)
    
    # Check timers
    training_session = training_sessions_col.find_one({'user_id': user_id, 'completed': False})
    dungeon_status = check_dungeon_status(current_user)
    hospital_session = hospital_sessions_col.find_one({'user_id': user_id, 'released': False})
    
    active_quest = user_quests_col.find_one({'user_id': user_id, 'status': 'active'})
    
    timers = {}
    if training_session:
        complete_time = training_session['complete_time']
        if datetime.now(timezone.utc) < complete_time:
            timers['training'] = {
                'stat': training_session['stat'],
                'complete_time': complete_time,
                'seconds_remaining': int((complete_time - datetime.now(timezone.utc)).total_seconds())
            }
    
    if dungeon_status and dungeon_status.get('in_dungeon'):
        timers['dungeon'] = dungeon_status
    
    if hospital_session:
        release_time = hospital_session['release_time']
        if datetime.now(timezone.utc) < release_time:
            timers['hospital'] = {
                'release_time': release_time,
                'seconds_remaining': int((release_time - datetime.now(timezone.utc)).total_seconds())
            }
    
    if active_quest:
        complete_time = active_quest['complete_time']
        if datetime.now(timezone.utc) < complete_time:
            timers['quest'] = {
                'quest_name': active_quest['quest_name'],
                'complete_time': complete_time,
                'seconds_remaining': int((complete_time - datetime.now(timezone.utc)).total_seconds())
            }
    
    # Unread messages
    unread_count = messages_col.count_documents({'recipient_id': user_id, 'read': False})
    
    return {
        'gold': current_user['gold'],
        'energy': energy,
        'hp': hp,
        'level': current_user['level'],
        'xp': current_user['xp'],
        'xp_next': calculate_xp_for_next_level(current_user['xp'], current_user['level']),
        'location': current_user['location'],
        'timers': timers,
        'notifications': {
            'unread_messages': unread_count
        },
        'in_dungeon': bool(dungeon_status and dungeon_status.get('in_dungeon')),
        'in_hospital': bool(hospital_session and datetime.now(timezone.utc) < hospital_session['release_time'])
    }

# ============================================================================
# TRAINING SYSTEM
# ============================================================================

@app.post("/api/game/training/start")
async def start_training(req: TrainRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check if already training
    existing = training_sessions_col.find_one({'user_id': user_id, 'completed': False})
    if existing:
        raise HTTPException(status_code=400, detail="Du trainierst bereits einen anderen Stat")
    
    # Check dungeon
    if check_dungeon_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst nicht trainieren während du im Kerker bist")
    
    # Check energy
    cost = TRAINING_COSTS[req.stat]
    current_energy = regenerate_energy(current_user)
    
    if current_energy < cost['energy']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Energie (benötigt: {cost['energy']}, aktuell: {current_energy})")
    
    # Deduct energy
    users_col.update_one(
        {'id': user_id},
        {
            '$inc': {'energy': -cost['energy']},
            '$set': {'last_energy_regen': datetime.now(timezone.utc)}
        }
    )
    
    # Create training session
    complete_time = datetime.now(timezone.utc) + timedelta(minutes=cost['duration_minutes'])
    session = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'stat': req.stat,
        'start_time': datetime.now(timezone.utc),
        'complete_time': complete_time,
        'completed': False,
        'claimed': False
    }
    training_sessions_col.insert_one(session)
    
    return {
        'success': True,
        'message': f'Training für {req.stat.upper()} gestartet',
        'complete_time': complete_time,
        'duration_minutes': cost['duration_minutes']
    }

@app.post("/api/game/training/claim")
async def claim_training(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Find completed training
    session = training_sessions_col.find_one({'user_id': user_id, 'completed': False})
    if not session:
        raise HTTPException(status_code=404, detail="Keine aktive Trainingseinheit gefunden")
    
    if datetime.now(timezone.utc) < session['complete_time']:
        raise HTTPException(status_code=400, detail="Training noch nicht abgeschlossen")
    
    # Claim rewards
    stat = session['stat']
    stat_gain = random.randint(1, 3)  # Random gain 1-3
    xp_gain = TRAINING_COSTS[stat]['xp']
    
    result = users_col.update_one(
        {'id': user_id},
        {
            '$inc': {
                f'stats.{stat}': stat_gain,
                'xp': xp_gain
            }
        }
    )
    
    # Mark session as claimed
    training_sessions_col.update_one(
        {'id': session['id']},
        {'$set': {'completed': True, 'claimed': True, 'claimed_at': datetime.now(timezone.utc)}}
    )
    
    # Check for level up
    updated_user = users_col.find_one({'id': user_id})
    new_level = calculate_level(updated_user['xp'])
    if new_level > updated_user['level']:
        users_col.update_one({'id': user_id}, {'$set': {'level': new_level}})
        log_event('quest', f'{current_user["username"]} reached level {new_level}!', user_id)
        
        return {
            'success': True,
            'message': f'Training abgeschlossen! +{stat_gain} {stat.upper()}, +{xp_gain} XP',
            'level_up': True,
            'new_level': new_level,
            'stat_gain': stat_gain,
            'xp_gain': xp_gain
        }
    
    return {
        'success': True,
        'message': f'Training abgeschlossen! +{stat_gain} {stat.upper()}, +{xp_gain} XP',
        'level_up': False,
        'stat_gain': stat_gain,
        'xp_gain': xp_gain
    }

# ============================================================================
# CRIMES SYSTEM
# ============================================================================

@app.get("/api/game/crimes")
async def get_crimes(current_user: dict = Depends(get_current_user)):
    """Get available crimes"""
    crimes = []
    for crime in MASTER_CRIMES:
        if current_user['level'] >= crime['min_level']:
            crimes.append(crime)
    return crimes

@app.post("/api/game/crimes/commit")
async def commit_crime(req: CrimeRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check dungeon
    dungeon_status = check_dungeon_status(current_user)
    if dungeon_status:
        raise HTTPException(status_code=400, detail="Du kannst keine Verbrechen begehen während du im Kerker sitzt")
    
    # Find crime
    crime = next((c for c in MASTER_CRIMES if c['id'] == req.crime_id), None)
    if not crime:
        raise HTTPException(status_code=404, detail="Verbrechen nicht gefunden")
    
    if current_user['level'] < crime['min_level']:
        raise HTTPException(status_code=400, detail=f"Level {crime['min_level']} erforderlich")
    
    # Check energy
    current_energy = regenerate_energy(current_user)
    if current_energy < crime['energy_cost']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Energie (benötigt: {crime['energy_cost']})")
    
    # Deduct energy
    users_col.update_one(
        {'id': user_id},
        {
            '$inc': {'energy': -crime['energy_cost']},
            '$set': {'last_energy_regen': datetime.now(timezone.utc)}
        }
    )
    
    # Calculate success (base + dexterity bonus)
    dex_bonus = current_user['stats']['dexterity'] * 0.5
    success_chance = min(95, crime['base_success'] + dex_bonus)
    roll = random.randint(1, 100)
    success = roll <= success_chance
    
    log_entry = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'crime_id': req.crime_id,
        'crime_name': crime['name'],
        'success': success,
        'timestamp': datetime.now(timezone.utc)
    }
    
    if success:
        # Success rewards
        gold_reward = random.randint(*crime['rewards']['gold'])
        xp_reward = crime['rewards']['xp']
        
        users_col.update_one(
            {'id': user_id},
            {'$inc': {'gold': gold_reward, 'xp': xp_reward}}
        )
        
        log_entry['gold_gained'] = gold_reward
        log_entry['xp_gained'] = xp_reward
        crime_logs_col.insert_one(log_entry)
        
        # Check level up
        updated_user = users_col.find_one({'id': user_id})
        new_level = calculate_level(updated_user['xp'])
        level_up = False
        if new_level > updated_user['level']:
            users_col.update_one({'id': user_id}, {'$set': {'level': new_level}})
            log_event('quest', f'{current_user["username"]} reached level {new_level}!', user_id)
            level_up = True
        
        log_event('crime', f'{current_user["username"]} successfully committed: {crime["name"]}', user_id)
        
        return {
            'success': True,
            'message': f'Erfolg! Du hast {gold_reward} Gold und {xp_reward} XP verdient.',
            'gold_gained': gold_reward,
            'xp_gained': xp_reward,
            'level_up': level_up,
            'new_level': new_level if level_up else None
        }
    else:
        # Failure consequences
        failure = crime['failure']
        
        # Jail time
        if 'jail_minutes' in failure:
            release_time = datetime.now(timezone.utc) + timedelta(minutes=failure['jail_minutes'])
            dungeon_sessions_col.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'crime_id': req.crime_id,
                'arrest_time': datetime.now(timezone.utc),
                'release_time': release_time,
                'released': False
            })
            log_entry['jail_minutes'] = failure['jail_minutes']
        
        # Gold fine
        if 'gold_fine' in failure:
            users_col.update_one({'id': user_id}, {'$inc': {'gold': -failure['gold_fine']}})
            log_entry['gold_lost'] = failure['gold_fine']
        
        # Injury (HP loss)
        if 'injury' in failure:
            new_hp = max(0, current_user['hp'] - failure['injury'])
            users_col.update_one({'id': user_id}, {'$set': {'hp': new_hp}})
            log_entry['hp_lost'] = failure['injury']
            
            # If HP drops to 0, send to hospital
            if new_hp == 0:
                hospital_time = 30  # 30 minutes base
                release_time = datetime.now(timezone.utc) + timedelta(minutes=hospital_time)
                hospital_sessions_col.insert_one({
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'reason': 'crime_injury',
                    'admit_time': datetime.now(timezone.utc),
                    'release_time': release_time,
                    'released': False
                })
                log_entry['hospitalized'] = True
        
        crime_logs_col.insert_one(log_entry)
        log_event('crime', f'{current_user["username"]} failed at: {crime["name"]} and was caught!', user_id)
        
        penalty_msg = []
        if 'jail_minutes' in failure:
            penalty_msg.append(f'{failure["jail_minutes"]} Minuten Kerker')
        if 'gold_fine' in failure:
            penalty_msg.append(f'{failure["gold_fine"]} Gold Strafe')
        if 'injury' in failure:
            penalty_msg.append(f'{failure["injury"]} HP Verlust')
        
        return {
            'success': False,
            'message': f'Gescheitert! Du wurdest erwischt. Strafe: {", ".join(penalty_msg)}',
            'penalties': failure
        }

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

@app.get("/api/game/combat/targets")
async def get_combat_targets(current_user: dict = Depends(get_current_user)):
    """Get list of potential targets"""
    # Find other players (exclude self, those in dungeon/hospital with privacy)
    targets = list(users_col.find(
        {
            'id': {'$ne': current_user['id']},
            'hp': {'$gt': 0}  # Only those not in hospital
        },
        {
            '_id': 0,
            'username': 1,
            'level': 1,
            'path_label': 1,
            'stats': 1,
            'location': 1
        }
    ).limit(50))
    
    return targets

@app.post("/api/game/combat/attack")
async def attack_player(req: CombatRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check if in dungeon/hospital
    if check_dungeon_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst nicht angreifen während du im Kerker bist")
    
    hospital_session = hospital_sessions_col.find_one({'user_id': user_id, 'released': False})
    if hospital_session and datetime.now(timezone.utc) < hospital_session['release_time']:
        raise HTTPException(status_code=400, detail="Du kannst nicht angreifen während du im Lazarett bist")
    
    # Check energy (25 energy per attack like torn.com)
    current_energy = regenerate_energy(current_user)
    if current_energy < 25:
        raise HTTPException(status_code=400, detail="Nicht genug Energie (benötigt: 25)")
    
    # Find target
    target = users_col.find_one({'username': req.target_username})
    if not target:
        raise HTTPException(status_code=404, detail="Ziel nicht gefunden")
    
    if target['id'] == user_id:
        raise HTTPException(status_code=400, detail="Du kannst dich nicht selbst angreifen")
    
    # Check target HP
    target_hp = regenerate_hp(target)
    if target_hp == 0:
        raise HTTPException(status_code=400, detail="Ziel ist bereits im Lazarett")
    
    # Deduct energy
    users_col.update_one(
        {'id': user_id},
        {
            '$inc': {'energy': -25},
            '$set': {'last_energy_regen': datetime.now(timezone.utc)}
        }
    )
    
    # Combat calculation (simplified)
    attacker_power = (
        current_user['stats']['strength'] * 2 +
        current_user['stats']['dexterity'] +
        current_user['stats']['speed']
    ) + random.randint(-10, 20)
    
    defender_power = (
        target['stats']['defense'] * 2 +
        target['stats']['speed'] +
        target['stats']['strength']
    ) + random.randint(-10, 20)
    
    attacker_wins = attacker_power > defender_power
    
    if attacker_wins:
        # Calculate damage
        damage = random.randint(15, 40)
        new_target_hp = max(0, target_hp - damage)
        
        # Gold steal for mug action
        gold_stolen = 0
        if req.action == 'mug':
            gold_stolen = min(target['gold'], random.randint(10, 50))
            users_col.update_one({'id': target['id']}, {'$inc': {'gold': -gold_stolen}})
            users_col.update_one({'id': user_id}, {'$inc': {'gold': gold_stolen}})
        
        # Update target HP
        users_col.update_one(
            {'id': target['id']},
            {
                '$set': {'hp': new_target_hp, 'last_hp_regen': datetime.now(timezone.utc)}
            }
        )
        
        # If hospitalize or HP = 0, send to hospital
        hospital_minutes = 0
        if req.action == 'hospitalize' or new_target_hp == 0:
            hospital_minutes = 60 if req.action == 'hospitalize' else 30
            hospital_sessions_col.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': target['id'],
                'reason': 'combat_loss',
                'attacker_id': user_id,
                'admit_time': datetime.now(timezone.utc),
                'release_time': datetime.now(timezone.utc) + timedelta(minutes=hospital_minutes),
                'released': False
            })
        
        # Log combat
        combat_log = {
            'id': str(uuid.uuid4()),
            'attacker_id': user_id,
            'attacker_name': current_user['username'],
            'defender_id': target['id'],
            'defender_name': target['username'],
            'action': req.action,
            'winner': 'attacker',
            'damage': damage,
            'gold_stolen': gold_stolen,
            'hospital_minutes': hospital_minutes,
            'timestamp': datetime.now(timezone.utc)
        }
        combat_logs_col.insert_one(combat_log)
        
        # XP gain for attacker
        xp_gain = 10
        users_col.update_one({'id': user_id}, {'$inc': {'xp': xp_gain}})
        
        # Event log
        action_text = 'angegriffen' if req.action == 'attack' else 'ausgeraubt' if req.action == 'mug' else 'ins Lazarett geschickt'
        log_event('combat', f'{current_user["username"]} hat {target["username"]} {action_text}!', user_id)
        
        return {
            'success': True,
            'victory': True,
            'message': f'Sieg! Du hast {damage} Schaden verursacht.',
            'damage': damage,
            'gold_stolen': gold_stolen,
            'xp_gained': xp_gain,
            'target_hospitalized': hospital_minutes > 0
        }
    else:
        # Defender wins
        damage = random.randint(10, 25)
        new_attacker_hp = max(0, regenerate_hp(current_user) - damage)
        
        users_col.update_one(
            {'id': user_id},
            {
                '$set': {'hp': new_attacker_hp, 'last_hp_regen': datetime.now(timezone.utc)}
            }
        )
        
        # If attacker HP = 0, hospital
        hospital_minutes = 0
        if new_attacker_hp == 0:
            hospital_minutes = 45
            hospital_sessions_col.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'reason': 'combat_loss',
                'defender_id': target['id'],
                'admit_time': datetime.now(timezone.utc),
                'release_time': datetime.now(timezone.utc) + timedelta(minutes=hospital_minutes),
                'released': False
            })
        
        # Log combat
        combat_log = {
            'id': str(uuid.uuid4()),
            'attacker_id': user_id,
            'attacker_name': current_user['username'],
            'defender_id': target['id'],
            'defender_name': target['username'],
            'action': req.action,
            'winner': 'defender',
            'damage': damage,
            'gold_stolen': 0,
            'hospital_minutes': hospital_minutes,
            'timestamp': datetime.now(timezone.utc)
        }
        combat_logs_col.insert_one(combat_log)
        
        log_event('combat', f'{target["username"]} hat {current_user["username"]} im Kampf besiegt!', target['id'])
        
        return {
            'success': True,
            'victory': False,
            'message': f'Niederlage! Du hast {damage} Schaden erlitten.',
            'damage': damage,
            'attacker_hospitalized': hospital_minutes > 0
        }

@app.get("/api/game/combat/logs")
async def get_combat_logs(current_user: dict = Depends(get_current_user), limit: int = 20):
    """Get recent combat logs for user"""
    logs = list(combat_logs_col.find(
        {
            '$or': [
                {'attacker_id': current_user['id']},
                {'defender_id': current_user['id']}
            ]
        },
        {'_id': 0}
    ).sort('timestamp', DESCENDING).limit(limit))
    
    return logs

# ============================================================================
# QUESTS SYSTEM
# ============================================================================

@app.get("/api/game/quests/available")
async def get_available_quests(current_user: dict = Depends(get_current_user)):
    """Get available quests for user level"""
    # Check if already on a quest
    active = user_quests_col.find_one({'user_id': current_user['id'], 'status': 'active'})
    if active:
        return {'active_quest': active, 'available_quests': []}
    
    # Get completed quest IDs
    completed_ids = [uq['quest_id'] for uq in user_quests_col.find({'user_id': current_user['id'], 'status': 'completed'})]
    
    # Find available quests
    available = []
    for quest in MASTER_QUESTS:
        if current_user['level'] >= quest['min_level'] and quest['id'] not in completed_ids:
            available.append(quest)
    
    return {'active_quest': None, 'available_quests': available}

@app.post("/api/game/quests/accept")
async def accept_quest(req: QuestRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check if already on a quest
    active = user_quests_col.find_one({'user_id': user_id, 'status': 'active'})
    if active:
        raise HTTPException(status_code=400, detail="Du hast bereits eine aktive Quest")
    
    # Find quest
    quest = next((q for q in MASTER_QUESTS if q['id'] == req.quest_id), None)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest nicht gefunden")
    
    if current_user['level'] < quest['min_level']:
        raise HTTPException(status_code=400, detail=f"Level {quest['min_level']} erforderlich")
    
    # Check if already completed
    completed = user_quests_col.find_one({'user_id': user_id, 'quest_id': req.quest_id, 'status': 'completed'})
    if completed:
        raise HTTPException(status_code=400, detail="Diese Quest wurde bereits abgeschlossen")
    
    # Check energy
    current_energy = regenerate_energy(current_user)
    if current_energy < quest['energy_cost']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Energie (benötigt: {quest['energy_cost']})")
    
    # Deduct energy
    users_col.update_one(
        {'id': user_id},
        {
            '$inc': {'energy': -quest['energy_cost']},
            '$set': {'last_energy_regen': datetime.now(timezone.utc)}
        }
    )
    
    # Create user quest
    complete_time = datetime.now(timezone.utc) + timedelta(minutes=quest['duration_minutes'])
    user_quest = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'quest_id': req.quest_id,
        'quest_name': quest['name'],
        'start_time': datetime.now(timezone.utc),
        'complete_time': complete_time,
        'status': 'active',
        'claimed': False
    }
    user_quests_col.insert_one(user_quest)
    
    return {
        'success': True,
        'message': f'Quest "{quest["name"]}" akzeptiert!',
        'complete_time': complete_time,
        'duration_minutes': quest['duration_minutes']
    }

@app.post("/api/game/quests/complete")
async def complete_quest(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Find active quest
    user_quest = user_quests_col.find_one({'user_id': user_id, 'status': 'active'})
    if not user_quest:
        raise HTTPException(status_code=404, detail="Keine aktive Quest gefunden")
    
    if datetime.now(timezone.utc) < user_quest['complete_time']:
        raise HTTPException(status_code=400, detail="Quest noch nicht abgeschlossen")
    
    # Find quest details
    quest = next((q for q in MASTER_QUESTS if q['id'] == user_quest['quest_id']), None)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest Daten nicht gefunden")
    
    # Claim rewards
    gold_reward = quest['rewards']['gold']
    xp_reward = quest['rewards']['xp']
    
    users_col.update_one(
        {'id': user_id},
        {'$inc': {'gold': gold_reward, 'xp': xp_reward}}
    )
    
    # Mark quest as completed
    user_quests_col.update_one(
        {'id': user_quest['id']},
        {
            '$set': {
                'status': 'completed',
                'claimed': True,
                'claimed_at': datetime.now(timezone.utc)
            }
        }
    )
    
    # Item reward if any
    item_reward = None
    if 'item' in quest['rewards']:
        item_id = quest['rewards']['item']
        # Add to inventory
        existing = inventories_col.find_one({'user_id': user_id, 'item_id': item_id})
        if existing:
            inventories_col.update_one(
                {'user_id': user_id, 'item_id': item_id},
                {'$inc': {'quantity': 1}}
            )
        else:
            inventories_col.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'item_id': item_id,
                'quantity': 1,
                'acquired_at': datetime.now(timezone.utc)
            })
        
        item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
        item_reward = item_data['name'] if item_data else item_id
    
    # Check level up
    updated_user = users_col.find_one({'id': user_id})
    new_level = calculate_level(updated_user['xp'])
    level_up = False
    if new_level > updated_user['level']:
        users_col.update_one({'id': user_id}, {'$set': {'level': new_level}})
        log_event('quest', f'{current_user["username"]} reached level {new_level}!', user_id)
        level_up = True
    
    log_event('quest', f'{current_user["username"]} completed quest: {quest["name"]}', user_id)
    
    message = f'Quest abgeschlossen! +{gold_reward} Gold, +{xp_reward} XP'
    if item_reward:
        message += f', +1 {item_reward}'
    
    return {
        'success': True,
        'message': message,
        'rewards': {
            'gold': gold_reward,
            'xp': xp_reward,
            'item': item_reward
        },
        'level_up': level_up,
        'new_level': new_level if level_up else None
    }

# ============================================================================
# INVENTORY & ITEMS
# ============================================================================

@app.get("/api/game/inventory")
async def get_inventory(current_user: dict = Depends(get_current_user)):
    """Get user's inventory"""
    user_id = current_user['id']
    
    inventory_items = list(inventories_col.find({'user_id': user_id}, {'_id': 0}))
    
    # Enrich with item details
    enriched = []
    for inv_item in inventory_items:
        item_data = next((i for i in MASTER_ITEMS if i['id'] == inv_item['item_id']), None)
        if item_data:
            enriched.append({
                **inv_item,
                'item_details': item_data
            })
    
    return {
        'inventory': enriched,
        'equipped': current_user.get('equipment', {})
    }

@app.post("/api/game/inventory/use")
async def use_item(item_id: str, current_user: dict = Depends(get_current_user)):
    """Use a consumable item"""
    user_id = current_user['id']
    
    # Check inventory
    inv_item = inventories_col.find_one({'user_id': user_id, 'item_id': item_id})
    if not inv_item or inv_item['quantity'] < 1:
        raise HTTPException(status_code=404, detail="Item nicht im Inventar")
    
    # Get item details
    item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
    if not item_data or item_data['type'] != 'consumable':
        raise HTTPException(status_code=400, detail="Dieser Gegenstand kann nicht benutzt werden")
    
    # Apply effect
    effect = item_data.get('effect', {})
    updates = {}
    messages = []
    
    if 'hp' in effect:
        current_hp = regenerate_hp(current_user)
        new_hp = min(MAX_HP, current_hp + effect['hp'])
        updates['hp'] = new_hp
        messages.append(f"+{effect['hp']} HP")
    
    if 'energy' in effect:
        current_energy = regenerate_energy(current_user)
        new_energy = min(MAX_ENERGY, current_energy + effect['energy'])
        updates['energy'] = new_energy
        messages.append(f"+{effect['energy']} Energie")
    
    # Update user
    if updates:
        users_col.update_one({'id': user_id}, {'$set': updates})
    
    # Remove item from inventory
    if inv_item['quantity'] == 1:
        inventories_col.delete_one({'id': inv_item['id']})
    else:
        inventories_col.update_one({'id': inv_item['id']}, {'$inc': {'quantity': -1}})
    
    return {
        'success': True,
        'message': f'{item_data["name"]} benutzt: {", ".join(messages)}',
        'effects': effect
    }

# ============================================================================
# ARMOUR SHOP
# ============================================================================

@app.get("/api/game/shop/items")
async def get_shop_items(current_user: dict = Depends(get_current_user)):
    """Get items available in shop"""
    # Filter by user level
    available = [item for item in MASTER_ITEMS if item['required_level'] <= current_user['level']]
    return available

@app.post("/api/game/shop/buy")
async def buy_item(item_id: str, quantity: int = 1, current_user: dict = Depends(get_current_user)):
    """Buy item from shop"""
    user_id = current_user['id']
    
    # Find item
    item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
    if not item_data:
        raise HTTPException(status_code=404, detail="Gegenstand nicht gefunden")
    
    if current_user['level'] < item_data['required_level']:
        raise HTTPException(status_code=400, detail=f"Level {item_data['required_level']} erforderlich")
    
    total_cost = item_data['price'] * quantity
    if current_user['gold'] < total_cost:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {total_cost})")
    
    # Deduct gold
    users_col.update_one({'id': user_id}, {'$inc': {'gold': -total_cost}})
    
    # Add to inventory
    existing = inventories_col.find_one({'user_id': user_id, 'item_id': item_id})
    if existing:
        inventories_col.update_one(
            {'user_id': user_id, 'item_id': item_id},
            {'$inc': {'quantity': quantity}}
        )
    else:
        inventories_col.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'item_id': item_id,
            'quantity': quantity,
            'acquired_at': datetime.now(timezone.utc)
        })
    
    return {
        'success': True,
        'message': f'{quantity}x {item_data["name"]} gekauft für {total_cost} Gold',
        'cost': total_cost
    }

# ============================================================================
# MARKET SYSTEM
# ============================================================================

@app.get("/api/game/market/listings")
async def get_market_listings(item_type: Optional[str] = None, limit: int = 50):
    """Get active market listings"""
    query = {'active': True}
    if item_type:
        query['item_type'] = item_type
    
    listings = list(market_listings_col.find(query, {'_id': 0}).sort('created_at', DESCENDING).limit(limit))
    
    # Enrich with item details and seller info
    enriched = []
    for listing in listings:
        item_data = next((i for i in MASTER_ITEMS if i['id'] == listing['item_id']), None)
        seller = users_col.find_one({'id': listing['seller_id']}, {'username': 1, 'level': 1})
        
        enriched.append({
            **listing,
            'item_details': item_data,
            'seller_name': seller['username'] if seller else 'Unknown',
            'seller_level': seller['level'] if seller else 1
        })
    
    return enriched

@app.post("/api/game/market/create")
async def create_market_listing(req: MarketListingCreate, current_user: dict = Depends(get_current_user)):
    """Create a new market listing"""
    user_id = current_user['id']
    
    # Check inventory
    inv_item = inventories_col.find_one({'user_id': user_id, 'item_id': req.item_id})
    if not inv_item or inv_item['quantity'] < req.quantity:
        raise HTTPException(status_code=400, detail="Nicht genug Gegenstände im Inventar")
    
    # Get item details
    item_data = next((i for i in MASTER_ITEMS if i['id'] == req.item_id), None)
    if not item_data:
        raise HTTPException(status_code=404, detail="Gegenstand nicht gefunden")
    
    # Remove from inventory
    if inv_item['quantity'] == req.quantity:
        inventories_col.delete_one({'id': inv_item['id']})
    else:
        inventories_col.update_one(
            {'id': inv_item['id']},
            {'$inc': {'quantity': -req.quantity}}
        )
    
    # Create listing
    listing = {
        'id': str(uuid.uuid4()),
        'seller_id': user_id,
        'item_id': req.item_id,
        'item_name': item_data['name'],
        'item_type': item_data['type'],
        'quantity': req.quantity,
        'price_per_unit': req.price_per_unit,
        'total_price': req.price_per_unit * req.quantity,
        'active': True,
        'created_at': datetime.now(timezone.utc)
    }
    market_listings_col.insert_one(listing)
    
    return {
        'success': True,
        'message': f'Angebot erstellt: {req.quantity}x {item_data["name"]} für {listing["total_price"]} Gold',
        'listing_id': listing['id']
    }

@app.post("/api/game/market/buy")
async def buy_from_market(req: MarketBuyRequest, current_user: dict = Depends(get_current_user)):
    """Buy from market listing"""
    user_id = current_user['id']
    
    # Find listing
    listing = market_listings_col.find_one({'id': req.listing_id, 'active': True})
    if not listing:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden oder nicht mehr aktiv")
    
    if listing['seller_id'] == user_id:
        raise HTTPException(status_code=400, detail="Du kannst nicht von deinem eigenen Angebot kaufen")
    
    if req.quantity > listing['quantity']:
        raise HTTPException(status_code=400, detail="Nicht genug Gegenstände verfügbar")
    
    total_cost = req.quantity * listing['price_per_unit']
    if current_user['gold'] < total_cost:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {total_cost})")
    
    # Transfer gold
    users_col.update_one({'id': user_id}, {'$inc': {'gold': -total_cost}})
    users_col.update_one({'id': listing['seller_id']}, {'$inc': {'gold': total_cost}})
    
    # Add to buyer inventory
    existing = inventories_col.find_one({'user_id': user_id, 'item_id': listing['item_id']})
    if existing:
        inventories_col.update_one(
            {'user_id': user_id, 'item_id': listing['item_id']},
            {'$inc': {'quantity': req.quantity}}
        )
    else:
        inventories_col.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'item_id': listing['item_id'],
            'quantity': req.quantity,
            'acquired_at': datetime.now(timezone.utc)
        })
    
    # Update or remove listing
    if req.quantity == listing['quantity']:
        market_listings_col.update_one({'id': req.listing_id}, {'$set': {'active': False}})
    else:
        market_listings_col.update_one(
            {'id': req.listing_id},
            {
                '$inc': {'quantity': -req.quantity},
                '$set': {'total_price': (listing['quantity'] - req.quantity) * listing['price_per_unit']}
            }
        )
    
    return {
        'success': True,
        'message': f'{req.quantity}x {listing["item_name"]} gekauft für {total_cost} Gold',
        'cost': total_cost
    }

@app.get("/api/game/market/my-listings")
async def get_my_listings(current_user: dict = Depends(get_current_user)):
    """Get user's active listings"""
    listings = list(market_listings_col.find(
        {'seller_id': current_user['id'], 'active': True},
        {'_id': 0}
    ))
    
    # Enrich with item details
    enriched = []
    for listing in listings:
        item_data = next((i for i in MASTER_ITEMS if i['id'] == listing['item_id']), None)
        enriched.append({
            **listing,
            'item_details': item_data
        })
    
    return enriched

@app.delete("/api/game/market/cancel/{listing_id}")
async def cancel_listing(listing_id: str, current_user: dict = Depends(get_current_user)):
    """Cancel a listing and return items"""
    listing = market_listings_col.find_one({'id': listing_id, 'seller_id': current_user['id'], 'active': True})
    if not listing:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    
    # Return items to inventory
    existing = inventories_col.find_one({'user_id': current_user['id'], 'item_id': listing['item_id']})
    if existing:
        inventories_col.update_one(
            {'user_id': current_user['id'], 'item_id': listing['item_id']},
            {'$inc': {'quantity': listing['quantity']}}
        )
    else:
        inventories_col.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': current_user['id'],
            'item_id': listing['item_id'],
            'quantity': listing['quantity'],
            'acquired_at': datetime.now(timezone.utc)
        })
    
    # Deactivate listing
    market_listings_col.update_one({'id': listing_id}, {'$set': {'active': False}})
    
    return {
        'success': True,
        'message': f'Angebot storniert. {listing["quantity"]}x {listing["item_name"]} zurück im Inventar'
    }

# ============================================================================
# BANKING SYSTEM
# ============================================================================

@app.get("/api/game/bank/account")
async def get_bank_account(current_user: dict = Depends(get_current_user)):
    """Get bank account info"""
    account = bank_accounts_col.find_one({'user_id': current_user['id']}, {'_id': 0})
    if not account:
        # Create account
        account = {
            'id': str(uuid.uuid4()),
            'user_id': current_user['id'],
            'balance': 0,
            'created_at': datetime.now(timezone.utc)
        }
        bank_accounts_col.insert_one(account)
    
    return account

@app.post("/api/game/bank/deposit")
async def bank_deposit(req: BankDepositRequest, current_user: dict = Depends(get_current_user)):
    """Deposit gold to bank"""
    user_id = current_user['id']
    
    if current_user['gold'] < req.amount:
        raise HTTPException(status_code=400, detail="Nicht genug Gold")
    
    # Transfer gold
    users_col.update_one({'id': user_id}, {'$inc': {'gold': -req.amount}})
    
    # Update or create bank account
    account = bank_accounts_col.find_one({'user_id': user_id})
    if account:
        bank_accounts_col.update_one(
            {'user_id': user_id},
            {'$inc': {'balance': req.amount}}
        )
    else:
        bank_accounts_col.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'balance': req.amount,
            'created_at': datetime.now(timezone.utc)
        })
    
    return {
        'success': True,
        'message': f'{req.amount} Gold eingezahlt',
        'deposited': req.amount
    }

@app.post("/api/game/bank/withdraw")
async def bank_withdraw(req: BankWithdrawRequest, current_user: dict = Depends(get_current_user)):
    """Withdraw gold from bank"""
    user_id = current_user['id']
    
    account = bank_accounts_col.find_one({'user_id': user_id})
    if not account or account['balance'] < req.amount:
        raise HTTPException(status_code=400, detail="Nicht genug Gold auf dem Bankkonto")
    
    # Transfer gold
    bank_accounts_col.update_one({'user_id': user_id}, {'$inc': {'balance': -req.amount}})
    users_col.update_one({'id': user_id}, {'$inc': {'gold': req.amount}})
    
    return {
        'success': True,
        'message': f'{req.amount} Gold abgehoben',
        'withdrawn': req.amount
    }

# ============================================================================
# REVIEWS (from landing page)
# ============================================================================

@app.get("/api/reviews")
async def get_reviews():
    reviews = list(reviews_col.find({}, {'_id': 0}).sort('created_at', DESCENDING))
    
    enriched = []
    for review in reviews:
        days_ago = (datetime.now(timezone.utc) - review['created_at']).days
        if days_ago == 0:
            date_str = "Today"
        elif days_ago == 1:
            date_str = "Yesterday"
        elif days_ago < 30:
            date_str = f"{days_ago} days ago"
        else:
            date_str = review['created_at'].strftime("%B %d, %Y")
        
        enriched.append({
            'id': review['id'],
            'author': review['author'],
            'rating': review['rating'],
            'text': review['text'],
            'verified': True,
            'date': date_str
        })
    
    return enriched

@app.post("/api/reviews")
async def create_review(req: ReviewRequest, current_user: dict = Depends(get_current_user)):
    # Check if already reviewed
    existing = reviews_col.find_one({'user_id': current_user['id']})
    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted a review for the Realm")
    
    review = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'author': current_user['username'],
        'rating': req.rating,
        'text': req.text,
        'verified': True,
        'created_at': datetime.now(timezone.utc)
    }
    reviews_col.insert_one(review)
    
    return {
        'success': True,
        'message': 'Vielen Dank für deine Bewertung!'
    }

# ============================================================================
# LANDING PAGE DATA (existing)
# ============================================================================

# Features, News, Paths, Kingdoms data (keeping existing from original server.py)
FEATURES = [item for item in MASTER_ITEMS[:10]]  # Just use first 10 items as feature showcase

# ... (I'll continue with the rest in the next file to keep this manageable)
