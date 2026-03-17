# ============================================================================
# REALM OF AETHORIA - COMPLETE GAME BACKEND
# Medieval Fantasy torn.com-inspired Browser RPG
# ============================================================================

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import jwt
import bcrypt
import uuid
import random
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

JWT_SECRET = os.environ.get('SECRET_KEY', 'aethoria-secret-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_DAYS = 30

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ.get('DB_NAME', 'aethoria_db')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

security = HTTPBearer()

# ============================================================================
# GAME CONSTANTS
# ============================================================================

MAX_ENERGY = 100
ENERGY_REGEN_PER_HOUR = 10
MAX_HP = 100
HP_REGEN_PER_HOUR = 5

TRAINING_COSTS = {
    'strength': {'energy': 10, 'duration_minutes': 5, 'xp': 2, 'gain': (1, 3)},
    'dexterity': {'energy': 10, 'duration_minutes': 5, 'xp': 2, 'gain': (1, 3)},
    'speed': {'energy': 10, 'duration_minutes': 5, 'xp': 2, 'gain': (1, 3)},
    'defense': {'energy': 10, 'duration_minutes': 5, 'xp': 2, 'gain': (1, 3)},
}

LEVEL_XP_REQUIREMENTS = [
    0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200,  # 1-10
    4000, 5000, 6200, 7600, 9200, 11000, 13000, 15200, 17600, 20200,  # 11-20
]

PATH_BONUSES = {
    'knight': {'strength': 5, 'defense': 5},
    'shadow': {'dexterity': 5, 'speed': 5},
    'noble': {'strength': 2, 'dexterity': 2, 'speed': 2, 'defense': 2},
}

PATH_LABELS = {
    'knight': 'The Knight',
    'shadow': 'The Shadow',
    'noble': 'The Noble'
}

PATH_ICONS = {
    'knight': '⚔️',
    'shadow': '🗡️',
    'noble': '👑'
}

# ============================================================================
# MASTER DATA - ITEMS
# ============================================================================

MASTER_ITEMS = [
    # === WEAPONS - MELEE ===
    {'id': 'sword_iron', 'name': 'Eisenschwert', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 100, 'damage': 15, 'required_level': 1, 'description': 'Ein einfaches, aber zuverlässiges Schwert aus Eisen'},
    {'id': 'sword_steel', 'name': 'Stahlschwert', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 500, 'damage': 35, 'required_level': 5, 'description': 'Geschmiedet aus bestem Stahl, scharf und tödlich'},
    {'id': 'sword_dragon', 'name': 'Drachenklingenschwert', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 5000, 'damage': 80, 'required_level': 15, 'description': 'Geschmiedet im Drachenfeuer, eine legendäre Waffe'},
    {'id': 'dagger_rusty', 'name': 'Rostiger Dolch', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 50, 'damage': 10, 'required_level': 1, 'description': 'Alt und rostig, aber immer noch gefährlich'},
    {'id': 'axe_battle', 'name': 'Streitaxt', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 800, 'damage': 45, 'required_level': 8, 'description': 'Schwere Axt für vernichtende Schläge'},
    {'id': 'mace_iron', 'name': 'Eisenstreitkolben', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 300, 'damage': 25, 'required_level': 4, 'description': 'Zerschmettert Rüstungen mit roher Kraft'},
    
    # === WEAPONS - RANGED ===
    {'id': 'bow_short', 'name': 'Kurzbogen', 'type': 'weapon', 'subtype': 'ranged', 'slot': 'weapon', 'price': 150, 'damage': 20, 'required_level': 3, 'description': 'Schnell und wendig für schnelle Schüsse'},
    {'id': 'bow_long', 'name': 'Langbogen', 'type': 'weapon', 'subtype': 'ranged', 'slot': 'weapon', 'price': 800, 'damage': 45, 'required_level': 8, 'description': 'Große Reichweite und tödliche Präzision'},
    {'id': 'crossbow', 'name': 'Armbrust', 'type': 'weapon', 'subtype': 'ranged', 'slot': 'weapon', 'price': 1200, 'damage': 55, 'required_level': 10, 'description': 'Durchschlägt selbst schwere Rüstungen'},
    
    # === ARMOR - BODY ===
    {'id': 'armor_leather', 'name': 'Lederrüstung', 'type': 'armor', 'subtype': 'body', 'slot': 'armor', 'price': 80, 'defense': 10, 'required_level': 1, 'description': 'Leichte Rüstung für Beweglichkeit'},
    {'id': 'armor_chain', 'name': 'Kettenhemd', 'type': 'armor', 'subtype': 'body', 'slot': 'armor', 'price': 400, 'defense': 25, 'required_level': 5, 'description': 'Kettengeflecht bietet soliden Schutz'},
    {'id': 'armor_plate', 'name': 'Plattenrüstung', 'type': 'armor', 'subtype': 'body', 'slot': 'armor', 'price': 3000, 'defense': 60, 'required_level': 12, 'description': 'Schwere Plattenpanzerung für maximalen Schutz'},
    
    # === ARMOR - HEAD ===
    {'id': 'helmet_iron', 'name': 'Eisenhelm', 'type': 'armor', 'subtype': 'head', 'slot': 'helmet', 'price': 50, 'defense': 5, 'required_level': 1, 'description': 'Schützt deinen Kopf vor Hieben'},
    {'id': 'helmet_steel', 'name': 'Stahlhelm', 'type': 'armor', 'subtype': 'head', 'slot': 'helmet', 'price': 300, 'defense': 15, 'required_level': 6, 'description': 'Verstärkter Helm aus Stahl'},
    
    # === ARMOR - SHIELD ===
    {'id': 'shield_wooden', 'name': 'Holzschild', 'type': 'armor', 'subtype': 'shield', 'slot': 'shield', 'price': 60, 'defense': 8, 'required_level': 1, 'description': 'Ein einfacher Holzschild'},
    {'id': 'shield_steel', 'name': 'Stahlschild', 'type': 'armor', 'subtype': 'shield', 'slot': 'shield', 'price': 600, 'defense': 30, 'required_level': 7, 'description': 'Massiver Schild aus reinem Stahl'},
    {'id': 'shield_dragon', 'name': 'Drachenschuppenschild', 'type': 'armor', 'subtype': 'shield', 'slot': 'shield', 'price': 4000, 'defense': 70, 'required_level': 16, 'description': 'Aus echten Drachenschuppen gefertigt'},
    
    # === POTIONS ===
    {'id': 'potion_health_small', 'name': 'Kleiner Heiltrank', 'type': 'consumable', 'subtype': 'potion', 'price': 20, 'effect': {'hp': 25}, 'required_level': 1, 'description': 'Stellt 25 HP wieder her'},
    {'id': 'potion_health_medium', 'name': 'Mittlerer Heiltrank', 'type': 'consumable', 'subtype': 'potion', 'price': 50, 'effect': {'hp': 50}, 'required_level': 5, 'description': 'Stellt 50 HP wieder her'},
    {'id': 'potion_health_large', 'name': 'Großer Heiltrank', 'type': 'consumable', 'subtype': 'potion', 'price': 150, 'effect': {'hp': 100}, 'required_level': 10, 'description': 'Stellt vollständig HP wieder her'},
    {'id': 'potion_energy', 'name': 'Energietrank', 'type': 'consumable', 'subtype': 'potion', 'price': 30, 'effect': {'energy': 25}, 'required_level': 1, 'description': 'Stellt 25 Energie wieder her'},
    {'id': 'potion_strength', 'name': 'Stärketrank', 'type': 'consumable', 'subtype': 'buff', 'price': 100, 'effect': {'strength_boost': 10, 'duration_hours': 1}, 'required_level': 8, 'description': 'Erhöht Stärke temporär um 10 für 1 Stunde'},
    {'id': 'potion_dexterity', 'name': 'Geschicklichkeitstrank', 'type': 'consumable', 'subtype': 'buff', 'price': 100, 'effect': {'dexterity_boost': 10, 'duration_hours': 1}, 'required_level': 8, 'description': 'Erhöht Geschicklichkeit temporär um 10'},
    
    # === RELICS ===
    {'id': 'relic_ancient_coin', 'name': 'Uralte Münze', 'type': 'relic', 'subtype': 'luck', 'price': 1000, 'effect': {'crime_success_boost': 5}, 'required_level': 10, 'description': 'Erhöht Erfolgschance bei Verbrechen um 5%'},
    {'id': 'relic_dragon_tooth', 'name': 'Drachenzahn', 'type': 'relic', 'subtype': 'combat', 'price': 8000, 'effect': {'damage_boost': 15}, 'required_level': 18, 'description': 'Erhöht Kampfschaden um 15'},
    {'id': 'relic_shadow_cloak', 'name': 'Schattenumhang', 'type': 'relic', 'subtype': 'stealth', 'price': 3000, 'effect': {'crime_success_boost': 10, 'dungeon_time_reduction': 20}, 'required_level': 12, 'description': 'Macht dich schwer zu fassen'},
    
    # === RESOURCES ===
    {'id': 'bread', 'name': 'Brot', 'type': 'resource', 'subtype': 'food', 'price': 5, 'effect': {'hp': 5}, 'required_level': 1, 'description': 'Ein einfaches Stück Brot'},
    {'id': 'meat', 'name': 'Fleisch', 'type': 'resource', 'subtype': 'food', 'price': 15, 'effect': {'hp': 15}, 'required_level': 1, 'description': 'Gebratenes Fleisch, nahrhaft'},
    {'id': 'wine', 'name': 'Wein', 'type': 'resource', 'subtype': 'drink', 'price': 25, 'effect': {'energy': 10}, 'required_level': 1, 'description': 'Feiner Wein zur Erfrischung'},
]

# ============================================================================
# MASTER DATA - CRIMES
# ============================================================================

MASTER_CRIMES = [
    # Level 1-3
    {'id': 'steal_bread', 'name': 'Brot stehlen', 'description': 'Stehle Brot vom Marktstand', 'energy_cost': 5, 'min_level': 1, 'base_success': 80, 'rewards': {'gold': (5, 15), 'xp': 1}, 'failure': {'jail_minutes': 15}, 'category': 'petty'},
    {'id': 'pickpocket', 'name': 'Taschendiebstahl', 'description': 'Stehle die Börse eines Bürgers', 'energy_cost': 8, 'min_level': 2, 'base_success': 65, 'rewards': {'gold': (20, 50), 'xp': 3}, 'failure': {'jail_minutes': 30}, 'category': 'theft'},
    {'id': 'rob_drunk', 'name': 'Betrunkenen ausrauben', 'description': 'Raube einen Betrunkenen vor der Taverne aus', 'energy_cost': 7, 'min_level': 2, 'base_success': 70, 'rewards': {'gold': (15, 40), 'xp': 2}, 'failure': {'jail_minutes': 20}, 'category': 'theft'},
    
    # Level 4-7
    {'id': 'burglary', 'name': 'Einbruch', 'description': 'Breche in ein Haus ein', 'energy_cost': 12, 'min_level': 4, 'base_success': 50, 'rewards': {'gold': (50, 150), 'xp': 8}, 'failure': {'jail_minutes': 60, 'gold_fine': 30}, 'category': 'burglary'},
    {'id': 'steal_horse', 'name': 'Pferd stehlen', 'description': 'Stehle ein Pferd vom Stall', 'energy_cost': 15, 'min_level': 5, 'base_success': 45, 'rewards': {'gold': (100, 200), 'xp': 12}, 'failure': {'jail_minutes': 90, 'gold_fine': 50}, 'category': 'theft'},
    {'id': 'rob_merchant', 'name': 'Händler überfallen', 'description': 'Überfalle einen reisenden Händler', 'energy_cost': 15, 'min_level': 6, 'base_success': 45, 'rewards': {'gold': (100, 300), 'xp': 15}, 'failure': {'jail_minutes': 120, 'gold_fine': 80}, 'category': 'robbery'},
    {'id': 'blackmail', 'name': 'Erpressung', 'description': 'Erpresse einen wohlhabenden Bürger', 'energy_cost': 18, 'min_level': 7, 'base_success': 40, 'rewards': {'gold': (200, 400), 'xp': 18}, 'failure': {'jail_minutes': 150, 'gold_fine': 150}, 'category': 'extortion'},
    
    # Level 8-12
    {'id': 'heist_shop', 'name': 'Laden ausrauben', 'description': 'Raube einen Waffenladen aus', 'energy_cost': 20, 'min_level': 8, 'base_success': 35, 'rewards': {'gold': (300, 600), 'xp': 25, 'item_chance': ('sword_steel', 10)}, 'failure': {'jail_minutes': 180, 'gold_fine': 200, 'injury': 15}, 'category': 'heist'},
    {'id': 'kidnapping', 'name': 'Entführung', 'description': 'Entführe ein Familienmitglied eines Adeligen', 'energy_cost': 25, 'min_level': 10, 'base_success': 30, 'rewards': {'gold': (500, 1000), 'xp': 35}, 'failure': {'jail_minutes': 240, 'gold_fine': 400, 'injury': 25}, 'category': 'major'},
    {'id': 'rob_treasury', 'name': 'Schatzkammer ausrauben', 'description': 'Wage einen Überfall auf die königliche Schatzkammer', 'energy_cost': 25, 'min_level': 10, 'base_success': 30, 'rewards': {'gold': (500, 1500), 'xp': 40}, 'failure': {'jail_minutes': 360, 'gold_fine': 300, 'injury': 20}, 'category': 'heist'},
    
    # Level 13+
    {'id': 'assassination', 'name': 'Attentat', 'description': 'Führe einen Auftragsmord aus', 'energy_cost': 30, 'min_level': 13, 'base_success': 25, 'rewards': {'gold': (1000, 2500), 'xp': 60}, 'failure': {'jail_minutes': 600, 'gold_fine': 800, 'injury': 40}, 'category': 'assassination'},
    {'id': 'dragon_egg_theft', 'name': 'Drachenei stehlen', 'description': 'Stehle ein Drachenei aus einer Höhle', 'energy_cost': 40, 'min_level': 18, 'base_success': 15, 'rewards': {'gold': (3000, 8000), 'xp': 150, 'item_chance': ('relic_dragon_tooth', 30)}, 'failure': {'jail_minutes': 720, 'gold_fine': 2000, 'injury': 60}, 'category': 'legendary'},
]

# ============================================================================
# MASTER DATA - QUESTS
# ============================================================================

MASTER_QUESTS = [
    {'id': 'quest_rats', 'name': 'Rattenplage', 'description': 'Töte 10 Ratten in den Stadtkanälen', 'min_level': 1, 'energy_cost': 15, 'duration_minutes': 20, 'rewards': {'gold': 50, 'xp': 10}, 'repeatable': True},
    {'id': 'quest_escort', 'name': 'Händler-Eskorte', 'description': 'Eskortiere einen Händler sicher durch den Wald', 'min_level': 3, 'energy_cost': 20, 'duration_minutes': 30, 'rewards': {'gold': 100, 'xp': 25}, 'repeatable': True},
    {'id': 'quest_wolves', 'name': 'Wolfsrudel', 'description': 'Eliminiere ein Wolfsrudel das Reisende bedroht', 'min_level': 5, 'energy_cost': 25, 'duration_minutes': 40, 'rewards': {'gold': 200, 'xp': 40}, 'repeatable': True},
    {'id': 'quest_bandit_camp', 'name': 'Banditenlager', 'description': 'Zerstöre ein Banditenlager außerhalb der Stadt', 'min_level': 5, 'energy_cost': 30, 'duration_minutes': 60, 'rewards': {'gold': 250, 'xp': 50, 'item': 'sword_steel'}, 'repeatable': False},
    {'id': 'quest_rescue', 'name': 'Rettungsmission', 'description': 'Rette einen verschleppten Bürger aus Feindeshand', 'min_level': 8, 'energy_cost': 35, 'duration_minutes': 90, 'rewards': {'gold': 500, 'xp': 80}, 'repeatable': True},
    {'id': 'quest_artifact', 'name': 'Verlorenes Artefakt', 'description': 'Finde ein verlorenes Artefakt in den Ruinen', 'min_level': 10, 'energy_cost': 40, 'duration_minutes': 120, 'rewards': {'gold': 800, 'xp': 120, 'item': 'relic_ancient_coin'}, 'repeatable': False},
    {'id': 'quest_dragon', 'name': 'Drachen-Bedrohung', 'description': 'Vertreibe einen jungen Drachen aus den Bergen', 'min_level': 15, 'energy_cost': 50, 'duration_minutes': 120, 'rewards': {'gold': 2000, 'xp': 200, 'item': 'relic_dragon_tooth'}, 'repeatable': False},
]

# ============================================================================
# MASTER DATA - CREATURES (for Hunting)
# ============================================================================

MASTER_CREATURES = [
    {'id': 'wolf', 'name': 'Wolf', 'hp': 30, 'power': 15, 'min_level': 5, 'energy_cost': 20, 'rewards': {'gold': (30, 80), 'xp': 15}},
    {'id': 'bear', 'name': 'Bär', 'hp': 60, 'power': 35, 'min_level': 10, 'energy_cost': 30, 'rewards': {'gold': (100, 200), 'xp': 40}},
    {'id': 'troll', 'name': 'Troll', 'hp': 100, 'power': 50, 'min_level': 15, 'energy_cost': 40, 'rewards': {'gold': (300, 600), 'xp': 100}},
    {'id': 'dragon_young', 'name': 'Junger Drache', 'hp': 200, 'power': 80, 'min_level': 20, 'energy_cost': 60, 'rewards': {'gold': (1000, 3000), 'xp': 300, 'item_chance': ('relic_dragon_tooth', 20)}},
]

# ============================================================================
# MASTER DATA - PROPERTIES
# ============================================================================

MASTER_PROPERTIES = [
    {'id': 'cottage', 'name': 'Kleine Hütte', 'type': 'residence', 'price': 5000, 'min_level': 8, 'daily_income': 50, 'description': 'Eine bescheidene Hütte am Stadtrand'},
    {'id': 'house', 'name': 'Stadthaus', 'type': 'residence', 'price': 15000, 'min_level': 12, 'daily_income': 150, 'description': 'Ein solides Haus in der Stadt'},
    {'id': 'manor', 'name': 'Herrenhaus', 'type': 'residence', 'price': 50000, 'min_level': 16, 'daily_income': 500, 'description': 'Ein prächtiges Anwesen mit Ländereien'},
    {'id': 'castle', 'name': 'Burg', 'type': 'fortress', 'price': 200000, 'min_level': 20, 'daily_income': 2000, 'description': 'Eine mächtige Festung mit Verteidigungsanlagen'},
]

# ============================================================================
# MASTER DATA - ACHIEVEMENTS
# ============================================================================

MASTER_ACHIEVEMENTS = [
    {'id': 'first_crime', 'name': 'Erstes Verbrechen', 'description': 'Begehe dein erstes Verbrechen', 'icon': '🗡️', 'xp_reward': 10},
    {'id': 'first_level_up', 'name': 'Aufstieg', 'description': 'Erreiche Level 2', 'icon': '⬆️', 'xp_reward': 20},
    {'id': 'first_kill', 'name': 'Erster Sieg', 'description': 'Besiege einen Gegner im Kampf', 'icon': '⚔️', 'xp_reward': 50},
    {'id': 'merchant', 'name': 'Händler', 'description': 'Verdiene 1000 Gold durch Handel', 'icon': '💰', 'xp_reward': 100},
    {'id': 'rich', 'name': 'Wohlhabend', 'description': 'Besitze 10.000 Gold gleichzeitig', 'icon': '💎', 'xp_reward': 200},
    {'id': 'legend', 'name': 'Legende', 'description': 'Erreiche Level 20', 'icon': '👑', 'xp_reward': 500},
    {'id': 'property_owner', 'name': 'Grundbesitzer', 'description': 'Kaufe deine erste Immobilie', 'icon': '🏰', 'xp_reward': 150},
    {'id': 'guild_master', 'name': 'Gildenmeister', 'description': 'Gründe eine Gilde', 'icon': '⚜️', 'xp_reward': 200},
]

# ============================================================================
# LANDING PAGE DATA
# ============================================================================

FEATURES = [
    {"title": "Merchant Exchange", "desc": "Invest in the Realm's bustling trade market and watch your gold multiply!", "icon": "📈"},
    {"title": "Open Realm", "desc": "Play your way. Be a knight, a rogue, a noble — limited only by your ambition!", "icon": "⚔️"},
    {"title": "Royal Contests", "desc": "Compete in grand tournaments and contests to win legendary prizes!", "icon": "🏆"},
    {"title": "Royal Council", "desc": "Need guidance? The Council of Elders will help new adventurers find their path!", "icon": "👑"},
    {"title": "Hunter's Contracts", "desc": "Collect bounties placed on wanted heads, or place your own on a rival!", "icon": "🎯"},
    {"title": "Royal Honours", "desc": "Earn distinguished honours for accomplishing legendary feats in the Realm!", "icon": "🎖️"},
    {"title": "One of a Kind", "desc": "Realm of Aethoria is like no other game in the world — built from the ground up!", "icon": "✨"},
    {"title": "Tavern Dice", "desc": "Six rolls, one skull — win a fortune or lose everything in a single throw!", "icon": "🎲"},
    {"title": "Quests", "desc": "Accept royal quests as you level up to earn credits for weapons, armour and relics!", "icon": "📜"},
    {"title": "Noble Bonds", "desc": "Find a partner and forge an alliance. Enjoy the benefits of shared strongholds!", "icon": "💍"},
    {"title": "Markets", "desc": "Become part of the Realm's economy — buy and sell goods at the Grand Market!", "icon": "🏪"},
    {"title": "Potions & Elixirs", "desc": "Feel the power and dangers of rare alchemical potions and elixirs!", "icon": "⚗️"},
    {"title": "Relics", "desc": "Collect and use ancient relics to enhance your combat and trade abilities!", "icon": "🔮"},
    {"title": "Armour Shops", "desc": "Browse the Realm's blacksmith quarter for weapons, armour, and rare artefacts!", "icon": "🛡️"},
    {"title": "Realm Exploration", "desc": "Travel to 11 distant kingdoms and experience their cultures and hidden riches!", "icon": "🗺️"},
    {"title": "Items & Artefacts", "desc": "Own hundreds of items — from common bread to legendary dragon-forged swords!", "icon": "💎"},
    {"title": "Tavern Poker", "desc": "Challenge up to 8 players in a high-stakes game of cards at the Tavern!", "icon": "🃏"},
    {"title": "The Dungeon", "desc": "Fail a deed and you'll end up in the Royal Dungeon — or help a friend escape!", "icon": "🔐"},
    {"title": "Guilds & Orders", "desc": "Create or join one of hundreds of guilds. War, trade, and scheme together!", "icon": "⚜️"},
    {"title": "Tournament Grounds", "desc": "Acquire and upgrade mighty steeds for jousting competitions against rivals!", "icon": "🐴"},
    {"title": "No Resets", "desc": "Your character is eternal — stats, rank, and legend will never be erased!", "icon": "♾️"},
    {"title": "Training Grounds", "desc": "Strengthen your Defence, Dexterity, Speed, and Might at the Royal Barracks!", "icon": "💪"},
    {"title": "Merchant Houses", "desc": "Found one of 39 merchant houses and hire other players to work under you!", "icon": "🏰"},
    {"title": "Realm Community", "desc": "Meet and socialise with thousands of adventurers in Aethoria's great halls!", "icon": "🤝"},
    {"title": "The Royal Gazette", "desc": "Read the Royal Gazette for the latest realm events and grand announcements!", "icon": "📰"},
    {"title": "Creature Hunting", "desc": "Journey to the Wildlands and hunt legendary beasts once you reach level 15!", "icon": "🐉"},
    {"title": "Arcane Studies", "desc": "Choose from dozens of arcane courses to unlock new skills and abilities!", "icon": "📚"},
    {"title": "Powerful Servers", "desc": "Aethoria runs on a fleet of enchanted server-stones for the fastest experience!", "icon": "⚡"},
    {"title": "Always Available", "desc": "Access the Realm from anywhere in the known world — 99.9% uptime guaranteed!", "icon": "🌐"},
    {"title": "Combat System", "desc": "Challenge rivals to duels — attack, mug, or hospitalise those who wrong you!", "icon": "⚔️"},
    {"title": "Dark Deeds", "desc": "Earn coin by committing over 50 dark deeds — each with hundreds of outcomes!", "icon": "🗡️"},
    {"title": "Royal Treasury", "desc": "Deposit your gold or seek a loan from the Royal Treasury's loan sharks!", "icon": "💰"},
    {"title": "Strongholds", "desc": "Invest your wealth into glorious keeps and castles — 14 properties to own!", "icon": "🏯"},
    {"title": "The Dragon's Den", "desc": "Try your luck at Aethoria's legendary casino — a dozen games of fortune!", "icon": "🎰"},
    {"title": "Arcane Curses", "desc": "Craft powerful hexes and sell them to players — or use them in shadow crimes!", "icon": "🌑"},
    {"title": "Royal Bank", "desc": "Grow your treasury through interest in the Royal Bank's investment vaults!", "icon": "🏦"},
    {"title": "Hall of Legends", "desc": "Rise to immortal fame and be enshrined in the Realm's Hall of Legends!", "icon": "🌟"},
    {"title": "Healer's Sanctuary", "desc": "View the fallen, tended to by healers — watch your back and guard your allies!", "icon": "❤️‍🩹"},
    {"title": "The Scavenger's Pit", "desc": "Rummage through the refuse of the wealthy — one man's trash is another's gold!", "icon": "🪙"},
    {"title": "Level Mastery", "desc": "Ascend through the levels to unlock hidden areas — experience is a mystery!", "icon": "⬆️"},
    {"title": "Guilds & Trades", "desc": "Try your hand at dozens of professions: healer, soldier, court scribe and more!", "icon": "⚒️"},
]

PATHS = {
    "knight": {"title": "The Knight", "subtitle": "Master of Combat & Honour", "description": "Forge yourself into an unstoppable warrior. Train daily at the Royal Barracks, master every weapon from the humble shortsword to the legendary dragon-forged blade. Win glory in the tournament grounds, defend your guild in faction wars, and rise to become the most feared combatant in all of Aethoria.", "highlights": ["Melee Weapons: axes, swords, maces, legendary enchanted blades", "Train Strength, Speed, Defence and Dexterity at the Barracks", "Compete in Grand Tournaments and Faction Wars", "Earn the rank of Champion and be enshrined in the Hall of Legends"], "icon": "⚔️", "color": "#C0392B"},
    "shadow": {"title": "The Shadow", "subtitle": "Master of Darkness & Cunning", "description": "Slip through the cracks of society, unseen and unstoppable. Master the art of dark deeds, pickpocketing, burglary and guild-organised crimes. Craft arcane curses. Place bounties and collect them. The shadows of Aethoria hold more power than any sword — if you dare to wield them.", "highlights": ["50+ Dark Deeds with hundreds of unique outcomes", "Craft and deploy Arcane Curses against enemies", "Place and collect Hunter's Contracts (Bounties)", "Master the art of Guild-organised shadow operations"], "icon": "🗡️", "color": "#8E44AD"},
    "noble":  {"title": "The Noble",  "subtitle": "Master of Gold & Power",    "description": "True power lies not in strength but in wealth and influence. Build your Merchant House, hire players as your retainers, dominate the trade markets, invest in the Royal Treasury, and acquire magnificent strongholds. The Realm's economy bends to the will of those with enough gold — and the cunning to use it.", "highlights": ["Found and manage one of 39 Merchant Houses", "Dominate the Merchant Exchange and drive prices", "Acquire Strongholds — from modest manors to grand castles", "Forge Noble Bonds and political alliances"], "icon": "👑", "color": "#D4AC0D"},
}

KINGDOMS = [
    {"id": "aethoria_capital", "name": "Aethoria Prime", "desc": "The capital of the Realm. Trade, power, and intrigue converge.", "image": "https://images.unsplash.com/photo-1533154683836-84ea7a0bc310?w=400&q=50", "type": "Capital", "danger": "Medium"},
    {"id": "ironhold", "name": "Ironhold", "desc": "A fortress city of steel and fire. Home to the greatest warriors.", "image": "https://images.unsplash.com/photo-1621947081720-86970823b77a?w=400&q=50", "type": "Military", "danger": "High"},
    {"id": "shadowfen", "name": "Shadowfen", "desc": "A city of fog and secrets, where rogues and thieves hold court.", "image": "https://images.unsplash.com/photo-1518709766631-a6a7f45921c3?w=400&q=50", "type": "Underworld", "danger": "Very High"},
    {"id": "goldenveil", "name": "Goldenveil", "desc": "The Realm's most prosperous trading city. Every merchant dreams of it.", "image": "https://images.unsplash.com/photo-1501183638710-841dd1904471?w=400&q=50", "type": "Commerce", "danger": "Low"},
    {"id": "stonecrest", "name": "Stonecrest", "desc": "Ancient mountains hiding powerful arcane secrets in their caves.", "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=50", "type": "Arcane", "danger": "High"},
    {"id": "crystalmere", "name": "Crystalmere", "desc": "A lakeside city of extraordinary beauty and political scheming.", "image": "https://images.unsplash.com/photo-1499678329028-101435549a4e?w=400&q=50", "type": "Noble", "danger": "Medium"},
    {"id": "embervast", "name": "Embervast", "desc": "The volcanic borderlands, rich in dragon-forged materials.", "image": "https://images.unsplash.com/photo-1527482797697-8795b05a13fe?w=400&q=50", "type": "Wilds", "danger": "Extreme"},
    {"id": "tidehaven", "name": "Tidehaven", "desc": "A port city where smugglers and merchants clash over sea routes.", "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=50", "type": "Maritime", "danger": "High"},
    {"id": "duskwood", "name": "Duskwood", "desc": "An ancient forest kingdom where shapeshifters and druids dwell.", "image": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=400&q=50", "type": "Forest", "danger": "Medium"},
    {"id": "frostholm", "name": "Frostholm", "desc": "The frozen north: hard people, rare pelts, and glacier-locked tombs.", "image": "https://images.unsplash.com/photo-1491555103944-7c647fd857e6?w=400&q=50", "type": "Frozen", "danger": "Very High"},
    {"id": "sunkeep", "name": "Sunkeep", "desc": "A desert kingdom where ruins of the First Empire still stand.", "image": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=400&q=50", "type": "Desert", "danger": "High"},
]

def make_initial_news():
    now = datetime.now(timezone.utc)
    entries = [
        {"title": "Realm of Aethoria opens its gates — welcome, adventurers!", "days_ago": 0},
        {"title": "Character Paths launched: Choose Knight, Shadow, or Noble", "days_ago": 1},
        {"title": "11 Kingdoms now available for exploration — travel system active", "days_ago": 3},
        {"title": "Hall of Legends now displays real registered adventurers", "days_ago": 5},
        {"title": "Review system launched — share your experience with the Realm", "days_ago": 7},
        {"title": "Online counter now tracks real active adventurers in real-time", "days_ago": 10},
        {"title": "Character Dashboard released — view your stats and path anytime", "days_ago": 14},
        {"title": "Realm Event Ticker now shows real activity from real adventurers", "days_ago": 18},
    ]
    result = []
    for e in entries:
        ts = now - timedelta(days=e["days_ago"])
        result.append({
            "id": str(uuid.uuid4()),
            "title": e["title"],
            "date": ts.strftime("%-d. %B %Y"),
            "date_iso": ts.isoformat(),
            "url": "#",
        })
    return result

# ============================================================================
# HELPER FUNCTIONS - AUTH
# ============================================================================

def create_access_token(user_id: str, username: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    payload = decode_access_token(credentials.credentials)
    user = await db.users.find_one({"id": payload["sub"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Update last_seen
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_seen": datetime.now(timezone.utc)}}
    )
    
    return user

# ============================================================================
# HELPER FUNCTIONS - GAME MECHANICS
# ============================================================================

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

async def regenerate_energy(user: dict) -> int:
    """Calculate and update current energy"""
    last_regen = user.get('last_energy_regen')
    current_energy = user.get('energy', MAX_ENERGY)
    
    if not last_regen or current_energy >= MAX_ENERGY:
        return min(current_energy, MAX_ENERGY)
    
    if isinstance(last_regen, str):
        last_regen = datetime.fromisoformat(last_regen.replace('Z', '+00:00'))
    
    now = datetime.now(timezone.utc)
    hours_passed = (now - last_regen).total_seconds() / 3600
    energy_gain = int(hours_passed * ENERGY_REGEN_PER_HOUR)
    
    new_energy = min(current_energy + energy_gain, MAX_ENERGY)
    
    if energy_gain > 0:
        await db.users.update_one(
            {'id': user['id']},
            {'$set': {'energy': new_energy, 'last_energy_regen': now}}
        )
    
    return new_energy

async def regenerate_hp(user: dict) -> int:
    """Calculate and update current HP"""
    # Check hospital first
    hospital_session = await db.hospital_sessions.find_one({'user_id': user['id'], 'released': False})
    if hospital_session:
        release_time = hospital_session['release_time']
        if isinstance(release_time, str):
            release_time = datetime.fromisoformat(release_time.replace('Z', '+00:00'))
        
        if datetime.now(timezone.utc) >= release_time:
            await db.hospital_sessions.update_one(
                {'user_id': user['id'], 'released': False},
                {'$set': {'released': True, 'actual_release': datetime.now(timezone.utc)}}
            )
            await db.users.update_one({'id': user['id']}, {'$set': {'hp': MAX_HP}})
            return MAX_HP
        else:
            return user.get('hp', 0)
    
    last_regen = user.get('last_hp_regen')
    current_hp = user.get('hp', MAX_HP)
    
    if not last_regen or current_hp >= MAX_HP:
        return min(current_hp, MAX_HP)
    
    if isinstance(last_regen, str):
        last_regen = datetime.fromisoformat(last_regen.replace('Z', '+00:00'))
    
    now = datetime.now(timezone.utc)
    hours_passed = (now - last_regen).total_seconds() / 3600
    hp_gain = int(hours_passed * HP_REGEN_PER_HOUR)
    
    new_hp = min(current_hp + hp_gain, MAX_HP)
    
    if hp_gain > 0:
        await db.users.update_one(
            {'id': user['id']},
            {'$set': {'hp': new_hp, 'last_hp_regen': now}}
        )
    
    return new_hp

async def check_dungeon_status(user: dict) -> Optional[dict]:
    """Check if user is in dungeon"""
    dungeon_session = await db.dungeon_sessions.find_one({'user_id': user['id'], 'released': False})
    if dungeon_session:
        release_time = dungeon_session['release_time']
        if isinstance(release_time, str):
            release_time = datetime.fromisoformat(release_time.replace('Z', '+00:00'))
        
        if datetime.now(timezone.utc) >= release_time:
            await db.dungeon_sessions.update_one(
                {'user_id': user['id'], 'released': False},
                {'$set': {'released': True, 'actual_release': datetime.now(timezone.utc)}}
            )
            return None
        else:
            minutes_remaining = int((release_time - datetime.now(timezone.utc)).total_seconds() / 60)
            return {
                'in_dungeon': True,
                'release_time': release_time,
                'minutes_remaining': minutes_remaining,
                'crime': dungeon_session.get('crime_name', 'Unknown')
            }
    return None

async def check_hospital_status(user: dict) -> Optional[dict]:
    """Check if user is in hospital"""
    hospital_session = await db.hospital_sessions.find_one({'user_id': user['id'], 'released': False})
    if hospital_session:
        release_time = hospital_session['release_time']
        if isinstance(release_time, str):
            release_time = datetime.fromisoformat(release_time.replace('Z', '+00:00'))
        
        if datetime.now(timezone.utc) >= release_time:
            await db.hospital_sessions.update_one(
                {'user_id': user['id'], 'released': False},
                {'$set': {'released': True, 'actual_release': datetime.now(timezone.utc)}}
            )
            await db.users.update_one({'id': user['id']}, {'$set': {'hp': MAX_HP}})
            return None
        else:
            minutes_remaining = int((release_time - datetime.now(timezone.utc)).total_seconds() / 60)
            return {
                'in_hospital': True,
                'release_time': release_time,
                'minutes_remaining': minutes_remaining,
                'reason': hospital_session.get('reason', 'Unknown')
            }
    return None

async def log_event(event_type: str, message: str, user_id: Optional[str] = None):
    """Log an event"""
    doc = {
        "id": str(uuid.uuid4()),
        "event": message,
        "type": event_type,
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc),
    }
    await db.events.insert_one(doc)
    
    # Keep only last 100
    count = await db.events.count_documents({})
    if count > 100:
        oldest = await db.events.find({}, {"_id": 1}).sort("created_at", 1).limit(count - 100).to_list(count - 100)
        if oldest:
            ids = [d["_id"] for d in oldest]
            await db.events.delete_many({"_id": {"$in": ids}})

def serialize_doc(doc):
    """Serialize MongoDB document"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        result = {}
        for k, v in doc.items():
            if k == "_id":
                continue
            result[k] = serialize_doc(v) if isinstance(v, (dict, list)) else (v.isoformat() if isinstance(v, datetime) else v)
        return result
    return doc

async def check_and_award_achievement(user_id: str, achievement_id: str):
    """Check and award achievement if not already earned"""
    existing = await db.user_achievements.find_one({'user_id': user_id, 'achievement_id': achievement_id})
    if not existing:
        achievement = next((a for a in MASTER_ACHIEVEMENTS if a['id'] == achievement_id), None)
        if achievement:
            await db.user_achievements.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'achievement_id': achievement_id,
                'earned_at': datetime.now(timezone.utc)
            })
            # Award XP
            await db.users.update_one({'id': user_id}, {'$inc': {'xp': achievement.get('xp_reward', 0)}})
            return achievement
    return None

# ============================================================================
# PYDANTIC MODELS - REQUESTS
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

class TravelRequest(BaseModel):
    kingdom_id: str

class HuntRequest(BaseModel):
    creature_id: str

class BountyCreateRequest(BaseModel):
    target_username: str
    reward_amount: int = Field(..., ge=100)

class PropertyBuyRequest(BaseModel):
    property_id: str

class DiceGameRequest(BaseModel):
    wager: int = Field(..., ge=10)

class UseItemRequest(BaseModel):
    item_id: str

class EquipItemRequest(BaseModel):
    item_id: str
    slot: Literal['weapon', 'armor', 'helmet', 'shield']

# ============================================================================
# SEED DATABASE
# ============================================================================

async def seed_database():
    """Seed master data on startup"""
    # Items
    if await db.items.count_documents({}) == 0:
        await db.items.insert_many([{**item} for item in MASTER_ITEMS])
        logger.info("✓ Seeded items collection")
    
    # Quests
    if await db.quests.count_documents({}) == 0:
        await db.quests.insert_many([{**quest} for quest in MASTER_QUESTS])
        logger.info("✓ Seeded quests collection")
    
    # Crimes
    if await db.crimes.count_documents({}) == 0:
        await db.crimes.insert_many([{**crime} for crime in MASTER_CRIMES])
        logger.info("✓ Seeded crimes collection")
    
    # Creatures
    if await db.creatures.count_documents({}) == 0:
        await db.creatures.insert_many([{**creature} for creature in MASTER_CREATURES])
        logger.info("✓ Seeded creatures collection")
    
    # Properties
    if await db.properties.count_documents({}) == 0:
        await db.properties.insert_many([{**prop} for prop in MASTER_PROPERTIES])
        logger.info("✓ Seeded properties collection")
    
    # Achievements
    if await db.achievements.count_documents({}) == 0:
        await db.achievements.insert_many([{**ach} for ach in MASTER_ACHIEVEMENTS])
        logger.info("✓ Seeded achievements collection")
    
    # Landing page data
    if await db.features.count_documents({}) == 0:
        await db.features.insert_many([{"id": str(uuid.uuid4()), "index": i, **f} for i, f in enumerate(FEATURES)])
        logger.info("✓ Seeded features collection")
    
    if await db.paths.count_documents({}) == 0:
        await db.paths.insert_many([{"id": str(uuid.uuid4()), "key": k, **v} for k, v in PATHS.items()])
        logger.info("✓ Seeded paths collection")
    
    if await db.kingdoms.count_documents({}) == 0:
        await db.kingdoms.insert_many([{**k} for k in KINGDOMS])
        logger.info("✓ Seeded kingdoms collection")
    
    # News (always refresh)
    await db.news.delete_many({})
    await db.news.insert_many(make_initial_news())
    logger.info("✓ Refreshed news collection")

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(title="Realm of Aethoria API")

@app.on_event("startup")
async def startup_event():
    await seed_database()
    logger.info("✓ Realm of Aethoria backend started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    client.close()

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    # Check existing
    if await db.users.find_one({'email': req.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await db.users.find_one({'username': req.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash password
    hashed = bcrypt.hashpw(req.password.encode('utf-8'), bcrypt.gensalt())
    
    # Path stats
    base_stats = {'strength': 10, 'dexterity': 10, 'speed': 10, 'defense': 10}
    path_bonus = PATH_BONUSES.get(req.path_choice, {})
    for stat, bonus in path_bonus.items():
        base_stats[stat] += bonus
    
    now = datetime.now(timezone.utc)
    user_id = str(uuid.uuid4())
    
    user = {
        'id': user_id,
        'username': req.username,
        'email': req.email,
        'password': hashed.decode('utf-8'),
        'path_choice': req.path_choice,
        'path_label': PATH_LABELS[req.path_choice],
        'level': 1,
        'xp': 0,
        'gold': 100,
        'energy': MAX_ENERGY,
        'hp': MAX_HP,
        'stats': base_stats,
        'equipment': {'weapon': None, 'armor': None, 'helmet': None, 'shield': None},
        'location': 'aethoria_capital',
        'title': PATH_LABELS[req.path_choice],
        'created_at': now,
        'last_seen': now,
        'last_energy_regen': now,
        'last_hp_regen': now,
        'days_in_realm': 0,
    }
    
    await db.users.insert_one(user)
    
    # Create bank account
    await db.bank_accounts.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'balance': 0,
        'created_at': now
    })
    
    # Log event
    await log_event('quest', f'{req.username} joined the Realm as {PATH_LABELS[req.path_choice]}', user_id)
    
    # Create token
    token = create_access_token(user_id, req.username)
    
    del user['password']
    del user['_id']
    
    return {
        'success': True,
        'message': f'Welcome to the Realm, {req.username}!',
        'token': token,
        'user': serialize_doc(user)
    }

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    user = await db.users.find_one({'email': req.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.checkpw(req.password.encode('utf-8'), user['password'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last_seen
    await db.users.update_one({'id': user['id']}, {'$set': {'last_seen': datetime.now(timezone.utc)}})
    
    # Log event
    await log_event('combat', f'{user["username"]} returned to the Realm', user['id'])
    
    token = create_access_token(user['id'], user['username'])
    
    del user['password']
    del user['_id']
    
    return {
        'success': True,
        'message': f'Welcome back, {user["username"]}!',
        'token': token,
        'user': serialize_doc(user)
    }

@app.get("/api/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    user = dict(current_user)
    if 'password' in user:
        del user['password']
    if '_id' in user:
        del user['_id']
    return serialize_doc(user)

# ============================================================================
# GAME STATE & HUD
# ============================================================================

@app.get("/api/game/state")
async def get_game_state(current_user: dict = Depends(get_current_user)):
    """Get complete game state for HUD"""
    user_id = current_user['id']
    
    # Regenerate resources
    energy = await regenerate_energy(current_user)
    hp = await regenerate_hp(current_user)
    
    # Check timers
    timers = {}
    
    # Training
    training_session = await db.training_sessions.find_one({'user_id': user_id, 'completed': False})
    if training_session:
        complete_time = training_session['complete_time']
        if isinstance(complete_time, str):
            complete_time = datetime.fromisoformat(complete_time.replace('Z', '+00:00'))
        
        if datetime.now(timezone.utc) < complete_time:
            timers['training'] = {
                'stat': training_session['stat'],
                'complete_time': complete_time.isoformat(),
                'seconds_remaining': int((complete_time - datetime.now(timezone.utc)).total_seconds())
            }
    
    # Quest
    active_quest = await db.user_quests.find_one({'user_id': user_id, 'status': 'active'})
    if active_quest:
        complete_time = active_quest['complete_time']
        if isinstance(complete_time, str):
            complete_time = datetime.fromisoformat(complete_time.replace('Z', '+00:00'))
        
        if datetime.now(timezone.utc) < complete_time:
            timers['quest'] = {
                'quest_name': active_quest['quest_name'],
                'complete_time': complete_time.isoformat(),
                'seconds_remaining': int((complete_time - datetime.now(timezone.utc)).total_seconds())
            }
    
    # Travel
    travel_session = await db.travel_sessions.find_one({'user_id': user_id, 'completed': False})
    if travel_session:
        arrival_time = travel_session['arrival_time']
        if isinstance(arrival_time, str):
            arrival_time = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
        
        if datetime.now(timezone.utc) < arrival_time:
            timers['travel'] = {
                'destination': travel_session['destination_name'],
                'arrival_time': arrival_time.isoformat(),
                'seconds_remaining': int((arrival_time - datetime.now(timezone.utc)).total_seconds())
            }
    
    # Status checks
    dungeon_status = await check_dungeon_status(current_user)
    hospital_status = await check_hospital_status(current_user)
    
    if dungeon_status:
        timers['dungeon'] = dungeon_status
    if hospital_status:
        timers['hospital'] = hospital_status
    
    # Notifications
    unread_messages = await db.messages.count_documents({'recipient_id': user_id, 'read': False})
    
    # Get kingdom name
    kingdom = next((k for k in KINGDOMS if k['id'] == current_user['location']), {'name': 'Unknown'})
    
    # Calculate equipment bonuses
    equipped_items = []
    total_defense_bonus = 0
    total_damage_bonus = 0
    
    for slot, item_id in current_user.get('equipment', {}).items():
        if item_id:
            item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
            if item_data:
                equipped_items.append({**item_data, 'slot': slot})
                if 'defense' in item_data:
                    total_defense_bonus += item_data['defense']
                if 'damage' in item_data:
                    total_damage_bonus += item_data['damage']
    
    return {
        'user': {
            'id': user_id,
            'username': current_user['username'],
            'level': current_user['level'],
            'xp': current_user['xp'],
            'xp_next': calculate_xp_for_next_level(current_user['xp'], current_user['level']),
            'title': current_user['title'],
            'path': current_user['path_choice'],
            'path_label': current_user['path_label'],
        },
        'resources': {
            'gold': current_user['gold'],
            'energy': energy,
            'energy_max': MAX_ENERGY,
            'hp': hp,
            'hp_max': MAX_HP,
        },
        'stats': {
            **current_user['stats'],
            'total_defense': current_user['stats']['defense'] + total_defense_bonus,
            'total_damage': current_user['stats']['strength'] + total_damage_bonus,
        },
        'location': {
            'kingdom_id': current_user['location'],
            'kingdom_name': kingdom['name']
        },
        'equipment': equipped_items,
        'timers': timers,
        'notifications': {
            'unread_messages': unread_messages,
        },
        'status': {
            'in_dungeon': bool(dungeon_status),
            'in_hospital': bool(hospital_status),
            'can_act': not bool(dungeon_status or hospital_status),
        }
    }

# ============================================================================
# TRAINING SYSTEM
# ============================================================================

@app.post("/api/game/training/start")
async def start_training(req: TrainRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check restrictions
    if await check_dungeon_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst nicht trainieren während du im Kerker bist")
    
    if await check_hospital_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst nicht trainieren während du verletzt bist")
    
    # Check if already training
    existing = await db.training_sessions.find_one({'user_id': user_id, 'completed': False})
    if existing:
        raise HTTPException(status_code=400, detail="Du trainierst bereits einen anderen Stat")
    
    # Check energy
    cost = TRAINING_COSTS[req.stat]
    current_energy = await regenerate_energy(current_user)
    
    if current_energy < cost['energy']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Energie (benötigt: {cost['energy']}, aktuell: {current_energy})")
    
    # Deduct energy
    await db.users.update_one(
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
    await db.training_sessions.insert_one(session)
    
    return {
        'success': True,
        'message': f'Training für {req.stat.upper()} gestartet',
        'complete_time': complete_time.isoformat(),
        'duration_minutes': cost['duration_minutes']
    }

@app.post("/api/game/training/claim")
async def claim_training(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    session = await db.training_sessions.find_one({'user_id': user_id, 'completed': False})
    if not session:
        raise HTTPException(status_code=404, detail="Keine aktive Trainingseinheit gefunden")
    
    complete_time = session['complete_time']
    if isinstance(complete_time, str):
        complete_time = datetime.fromisoformat(complete_time.replace('Z', '+00:00'))
    
    if datetime.now(timezone.utc) < complete_time:
        remaining = int((complete_time - datetime.now(timezone.utc)).total_seconds() / 60)
        raise HTTPException(status_code=400, detail=f"Training noch nicht abgeschlossen ({remaining} Minuten verbleibend)")
    
    # Calculate gains
    stat = session['stat']
    stat_gain = random.randint(*TRAINING_COSTS[stat]['gain'])
    xp_gain = TRAINING_COSTS[stat]['xp']
    
    await db.users.update_one(
        {'id': user_id},
        {'$inc': {f'stats.{stat}': stat_gain, 'xp': xp_gain}}
    )
    
    await db.training_sessions.update_one(
        {'id': session['id']},
        {'$set': {'completed': True, 'claimed': True, 'claimed_at': datetime.now(timezone.utc)}}
    )
    
    # Check level up
    updated_user = await db.users.find_one({'id': user_id})
    new_level = calculate_level(updated_user['xp'])
    level_up = False
    if new_level > updated_user['level']:
        await db.users.update_one({'id': user_id}, {'$set': {'level': new_level}})
        await log_event('quest', f'{current_user["username"]} reached level {new_level}!', user_id)
        await check_and_award_achievement(user_id, 'first_level_up')
        level_up = True
    
    return {
        'success': True,
        'message': f'Training abgeschlossen! +{stat_gain} {stat.upper()}, +{xp_gain} XP',
        'gains': {
            'stat': stat,
            'stat_gain': stat_gain,
            'xp_gain': xp_gain
        },
        'level_up': level_up,
        'new_level': new_level if level_up else None
    }

@app.get("/api/game/training/status")
async def get_training_status(current_user: dict = Depends(get_current_user)):
    """Get current training status"""
    session = await db.training_sessions.find_one(
        {'user_id': current_user['id'], 'completed': False},
        {'_id': 0}
    )
    return serialize_doc(session) if session else None

# ============================================================================
# CRIMES SYSTEM
# ============================================================================

@app.get("/api/game/crimes")
async def get_crimes(current_user: dict = Depends(get_current_user)):
    """Get available crimes for user level"""
    crimes = []
    for crime in MASTER_CRIMES:
        if current_user['level'] >= crime['min_level']:
            # Calculate adjusted success chance
            dex_bonus = current_user['stats']['dexterity'] * 0.5
            adjusted_success = min(95, crime['base_success'] + dex_bonus)
            
            crimes.append({
                **crime,
                'adjusted_success': round(adjusted_success, 1)
            })
    
    return crimes

@app.post("/api/game/crimes/commit")
async def commit_crime(req: CrimeRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check dungeon
    if await check_dungeon_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst keine Verbrechen begehen während du im Kerker sitzt")
    
    # Find crime
    crime = next((c for c in MASTER_CRIMES if c['id'] == req.crime_id), None)
    if not crime:
        raise HTTPException(status_code=404, detail="Verbrechen nicht gefunden")
    
    if current_user['level'] < crime['min_level']:
        raise HTTPException(status_code=400, detail=f"Level {crime['min_level']} erforderlich")
    
    # Check energy
    current_energy = await regenerate_energy(current_user)
    if current_energy < crime['energy_cost']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Energie (benötigt: {crime['energy_cost']})")
    
    # Deduct energy
    await db.users.update_one(
        {'id': user_id},
        {'$inc': {'energy': -crime['energy_cost']}, '$set': {'last_energy_regen': datetime.now(timezone.utc)}}
    )
    
    # Calculate success
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
        'roll': roll,
        'success_chance': success_chance,
        'timestamp': datetime.now(timezone.utc)
    }
    
    if success:
        # Success rewards
        gold_reward = random.randint(*crime['rewards']['gold'])
        xp_reward = crime['rewards']['xp']
        
        await db.users.update_one({'id': user_id}, {'$inc': {'gold': gold_reward, 'xp': xp_reward}})
        
        log_entry['gold_gained'] = gold_reward
        log_entry['xp_gained'] = xp_reward
        
        # Item chance
        item_gained = None
        if 'item_chance' in crime['rewards']:
            item_id, chance = crime['rewards']['item_chance']
            if random.randint(1, 100) <= chance:
                # Add to inventory
                existing = await db.inventories.find_one({'user_id': user_id, 'item_id': item_id})
                if existing:
                    await db.inventories.update_one(
                        {'user_id': user_id, 'item_id': item_id},
                        {'$inc': {'quantity': 1}}
                    )
                else:
                    await db.inventories.insert_one({
                        'id': str(uuid.uuid4()),
                        'user_id': user_id,
                        'item_id': item_id,
                        'quantity': 1,
                        'acquired_at': datetime.now(timezone.utc)
                    })
                
                item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
                item_gained = item_data['name'] if item_data else item_id
                log_entry['item_gained'] = item_id
        
        await db.crime_logs.insert_one(log_entry)
        
        # Check achievements
        crime_count = await db.crime_logs.count_documents({'user_id': user_id, 'success': True})
        if crime_count == 1:
            await check_and_award_achievement(user_id, 'first_crime')
        
        # Check level up
        updated_user = await db.users.find_one({'id': user_id})
        new_level = calculate_level(updated_user['xp'])
        level_up = False
        if new_level > updated_user['level']:
            await db.users.update_one({'id': user_id}, {'$set': {'level': new_level}})
            await log_event('quest', f'{current_user["username"]} reached level {new_level}!', user_id)
            level_up = True
        
        await log_event('crime', f'{current_user["username"]} successfully committed: {crime["name"]}', user_id)
        
        message = f'Erfolg! +{gold_reward} Gold, +{xp_reward} XP'
        if item_gained:
            message += f', +1 {item_gained}'
        
        return {
            'success': True,
            'victory': True,
            'message': message,
            'rewards': {
                'gold': gold_reward,
                'xp': xp_reward,
                'item': item_gained
            },
            'level_up': level_up,
            'new_level': new_level if level_up else None
        }
    else:
        # Failure consequences
        failure = crime['failure']
        penalties = []
        
        # Jail
        if 'jail_minutes' in failure:
            release_time = datetime.now(timezone.utc) + timedelta(minutes=failure['jail_minutes'])
            await db.dungeon_sessions.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'crime_id': req.crime_id,
                'crime_name': crime['name'],
                'arrest_time': datetime.now(timezone.utc),
                'release_time': release_time,
                'released': False
            })
            log_entry['jail_minutes'] = failure['jail_minutes']
            penalties.append(f'{failure["jail_minutes"]} Minuten Kerker')
        
        # Fine
        if 'gold_fine' in failure:
            current_gold = current_user['gold']
            fine_amount = min(current_gold, failure['gold_fine'])
            await db.users.update_one({'id': user_id}, {'$inc': {'gold': -fine_amount}})
            log_entry['gold_lost'] = fine_amount
            penalties.append(f'{fine_amount} Gold Strafe')
        
        # Injury
        if 'injury' in failure:
            current_hp = await regenerate_hp(current_user)
            new_hp = max(0, current_hp - failure['injury'])
            await db.users.update_one({'id': user_id}, {'$set': {'hp': new_hp, 'last_hp_regen': datetime.now(timezone.utc)}})
            log_entry['hp_lost'] = failure['injury']
            penalties.append(f'{failure["injury"]} HP Verlust')
            
            # Hospital if HP = 0
            if new_hp == 0:
                hospital_time = 30
                release_time = datetime.now(timezone.utc) + timedelta(minutes=hospital_time)
                await db.hospital_sessions.insert_one({
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'reason': 'crime_injury',
                    'admit_time': datetime.now(timezone.utc),
                    'release_time': release_time,
                    'released': False
                })
                log_entry['hospitalized'] = True
                penalties.append('Ins Lazarett eingeliefert')
        
        await db.crime_logs.insert_one(log_entry)
        await log_event('crime', f'{current_user["username"]} failed at: {crime["name"]} and was caught!', user_id)
        
        return {
            'success': True,
            'victory': False,
            'message': f'Gescheitert! Strafe: {", ".join(penalties)}',
            'penalties': failure
        }

@app.get("/api/game/crimes/logs")
async def get_crime_logs(current_user: dict = Depends(get_current_user), limit: int = 20):
    """Get user's crime history"""
    logs = await db.crime_logs.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).sort('timestamp', -1).limit(limit).to_list(limit)
    
    return serialize_doc(logs)

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

@app.get("/api/game/combat/targets")
async def get_combat_targets(current_user: dict = Depends(get_current_user)):
    """Get list of attackable players"""
    targets = await db.users.find(
        {
            'id': {'$ne': current_user['id']},
            'hp': {'$gt': 0}
        },
        {
            '_id': 0,
            'id': 1,
            'username': 1,
            'level': 1,
            'path_label': 1,
            'stats': 1,
            'location': 1,
            'last_seen': 1
        }
    ).sort('level', -1).limit(50).to_list(50)
    
    return serialize_doc(targets)

@app.post("/api/game/combat/attack")
async def attack_player(req: CombatRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check restrictions
    if await check_dungeon_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst nicht angreifen während du im Kerker bist")
    
    if await check_hospital_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst nicht angreifen während du verletzt bist")
    
    # Check energy (25 like torn.com)
    current_energy = await regenerate_energy(current_user)
    if current_energy < 25:
        raise HTTPException(status_code=400, detail="Nicht genug Energie (benötigt: 25)")
    
    # Find target
    target = await db.users.find_one({'username': req.target_username})
    if not target:
        raise HTTPException(status_code=404, detail="Ziel nicht gefunden")
    
    if target['id'] == user_id:
        raise HTTPException(status_code=400, detail="Du kannst dich nicht selbst angreifen")
    
    # Check target HP
    target_hp = await regenerate_hp(target)
    if target_hp == 0:
        raise HTTPException(status_code=400, detail="Ziel ist bereits im Lazarett")
    
    # Deduct energy
    await db.users.update_one(
        {'id': user_id},
        {'$inc': {'energy': -25}, '$set': {'last_energy_regen': datetime.now(timezone.utc)}}
    )
    
    # Combat calculation with equipment bonuses
    attacker_weapon_bonus = 0
    attacker_equipment = current_user.get('equipment', {})
    if attacker_equipment.get('weapon'):
        weapon = next((i for i in MASTER_ITEMS if i['id'] == attacker_equipment['weapon']), None)
        if weapon and 'damage' in weapon:
            attacker_weapon_bonus = weapon['damage']
    
    defender_armor_bonus = 0
    defender_equipment = target.get('equipment', {})
    for slot in ['armor', 'helmet', 'shield']:
        if defender_equipment.get(slot):
            armor = next((i for i in MASTER_ITEMS if i['id'] == defender_equipment[slot]), None)
            if armor and 'defense' in armor:
                defender_armor_bonus += armor['defense']
    
    attacker_power = (
        current_user['stats']['strength'] * 2 +
        current_user['stats']['dexterity'] +
        current_user['stats']['speed'] +
        attacker_weapon_bonus +
        random.randint(-10, 30)
    )
    
    defender_power = (
        target['stats']['defense'] * 2 +
        target['stats']['speed'] +
        target['stats']['strength'] +
        defender_armor_bonus +
        random.randint(-10, 30)
    )
    
    attacker_wins = attacker_power > defender_power
    
    if attacker_wins:
        # Calculate damage
        base_damage = random.randint(20, 50)
        damage = max(10, base_damage - defender_armor_bonus // 2)
        new_target_hp = max(0, target_hp - damage)
        
        # Gold steal for mug
        gold_stolen = 0
        if req.action == 'mug':
            max_steal = target['gold'] // 2
            gold_stolen = min(target['gold'], random.randint(10, max(50, max_steal)))
            await db.users.update_one({'id': target['id']}, {'$inc': {'gold': -gold_stolen}})
            await db.users.update_one({'id': user_id}, {'$inc': {'gold': gold_stolen}})
        
        # Update target HP
        await db.users.update_one(
            {'id': target['id']},
            {'$set': {'hp': new_target_hp, 'last_hp_regen': datetime.now(timezone.utc)}}
        )
        
        # Hospital
        hospital_minutes = 0
        if req.action == 'hospitalize' or new_target_hp == 0:
            hospital_minutes = 60 if req.action == 'hospitalize' else 30
            await db.hospital_sessions.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': target['id'],
                'reason': 'combat_loss',
                'attacker_id': user_id,
                'attacker_name': current_user['username'],
                'admit_time': datetime.now(timezone.utc),
                'release_time': datetime.now(timezone.utc) + timedelta(minutes=hospital_minutes),
                'released': False
            })
        
        # Log
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
        await db.combat_logs.insert_one(combat_log)
        
        # XP gain
        xp_gain = 10 + (target['level'] * 2)
        await db.users.update_one({'id': user_id}, {'$inc': {'xp': xp_gain}})
        
        # Check achievements
        kill_count = await db.combat_logs.count_documents({'attacker_id': user_id, 'winner': 'attacker'})
        if kill_count == 1:
            await check_and_award_achievement(user_id, 'first_kill')
        
        # Event
        action_text = 'angegriffen' if req.action == 'attack' else 'ausgeraubt' if req.action == 'mug' else 'ins Lazarett geschickt'
        await log_event('combat', f'{current_user["username"]} hat {target["username"]} {action_text}!', user_id)
        
        # Check level up
        updated_user = await db.users.find_one({'id': user_id})
        new_level = calculate_level(updated_user['xp'])
        level_up = new_level > updated_user['level']
        if level_up:
            await db.users.update_one({'id': user_id}, {'$set': {'level': new_level}})
            await log_event('quest', f'{current_user["username"]} reached level {new_level}!', user_id)
        
        return {
            'success': True,
            'victory': True,
            'message': f'Sieg! {damage} Schaden verursacht' + (f', {gold_stolen} Gold gestohlen' if gold_stolen > 0 else ''),
            'damage': damage,
            'gold_stolen': gold_stolen,
            'xp_gained': xp_gain,
            'target_hospitalized': hospital_minutes > 0,
            'level_up': level_up,
            'new_level': new_level if level_up else None
        }
    else:
        # Defender wins
        base_damage = random.randint(15, 35)
        damage = max(5, base_damage - current_user['stats']['defense'] // 2)
        current_hp = await regenerate_hp(current_user)
        new_attacker_hp = max(0, current_hp - damage)
        
        await db.users.update_one(
            {'id': user_id},
            {'$set': {'hp': new_attacker_hp, 'last_hp_regen': datetime.now(timezone.utc)}}
        )
        
        # Hospital
        hospital_minutes = 0
        if new_attacker_hp == 0:
            hospital_minutes = 45
            await db.hospital_sessions.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'reason': 'combat_loss',
                'defender_id': target['id'],
                'defender_name': target['username'],
                'admit_time': datetime.now(timezone.utc),
                'release_time': datetime.now(timezone.utc) + timedelta(minutes=hospital_minutes),
                'released': False
            })
        
        # Log
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
        await db.combat_logs.insert_one(combat_log)
        
        await log_event('combat', f'{target["username"]} hat {current_user["username"]} im Kampf besiegt!', target['id'])
        
        return {
            'success': True,
            'victory': False,
            'message': f'Niederlage! Du hast {damage} Schaden erlitten',
            'damage': damage,
            'attacker_hospitalized': hospital_minutes > 0
        }

@app.get("/api/game/combat/logs")
async def get_combat_logs(current_user: dict = Depends(get_current_user), limit: int = 30):
    """Get combat logs"""
    logs = await db.combat_logs.find(
        {
            '$or': [
                {'attacker_id': current_user['id']},
                {'defender_id': current_user['id']}
            ]
        },
        {'_id': 0}
    ).sort('timestamp', -1).limit(limit).to_list(limit)
    
    return serialize_doc(logs)

# Continue in next message due to length...
