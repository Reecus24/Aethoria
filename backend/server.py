# ============================================================================
# REALM OF AETHORIA - COMPLETE GAME BACKEND
# Medieval Fantasy torn.com-inspired Browser RPG
# ============================================================================

from fastapi import FastAPI, HTTPException, Depends, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
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
ENERGY_REGEN_PER_HOUR = 25  # Increased from 10 → 25 (4x faster, full regen in 4 hours instead of 10)
MAX_HP = 100
HP_REGEN_PER_HOUR = 10  # Increased from 5 → 10 (2x faster)

TRAINING_COSTS = {
    'strength': {'energy': 6, 'duration_minutes': 3, 'xp': 3, 'gain': (1, 3)},  # Reduced energy 10→6, time 5→3, xp 2→3
    'dexterity': {'energy': 6, 'duration_minutes': 3, 'xp': 3, 'gain': (1, 3)},
    'speed': {'energy': 6, 'duration_minutes': 3, 'xp': 3, 'gain': (1, 3)},
    'defense': {'energy': 6, 'duration_minutes': 3, 'xp': 3, 'gain': (1, 3)},
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
    {'id': 'sword_iron', 'name': 'Eisenschwert', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 100, 'damage': 15, 'strength': 3, 'required_level': 1, 'description': 'Ein einfaches, aber zuverlässiges Schwert aus Eisen'},
    {'id': 'sword_steel', 'name': 'Stahlschwert', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 500, 'damage': 35, 'strength': 7, 'required_level': 5, 'description': 'Geschmiedet aus bestem Stahl, scharf und tödlich'},
    {'id': 'sword_dragon', 'name': 'Drachenklingenschwert', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 5000, 'damage': 80, 'strength': 16, 'required_level': 15, 'description': 'Geschmiedet im Drachenfeuer, eine legendäre Waffe'},
    {'id': 'dagger_rusty', 'name': 'Rostiger Dolch', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 50, 'damage': 10, 'strength': 2, 'required_level': 1, 'description': 'Alt und rostig, aber immer noch gefährlich'},
    {'id': 'axe_battle', 'name': 'Streitaxt', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 800, 'damage': 45, 'strength': 9, 'required_level': 8, 'description': 'Schwere Axt für vernichtende Schläge'},
    {'id': 'mace_iron', 'name': 'Eisenstreitkolben', 'type': 'weapon', 'subtype': 'melee', 'slot': 'weapon', 'price': 300, 'damage': 25, 'strength': 5, 'required_level': 4, 'description': 'Zerschmettert Rüstungen mit roher Kraft'},
    
    # === WEAPONS - RANGED ===
    {'id': 'bow_short', 'name': 'Kurzbogen', 'type': 'weapon', 'subtype': 'ranged', 'slot': 'weapon', 'price': 150, 'damage': 20, 'strength': 4, 'required_level': 3, 'description': 'Schnell und wendig für schnelle Schüsse'},
    {'id': 'bow_long', 'name': 'Langbogen', 'type': 'weapon', 'subtype': 'ranged', 'slot': 'weapon', 'price': 800, 'damage': 45, 'strength': 9, 'required_level': 8, 'description': 'Große Reichweite und tödliche Präzision'},
    {'id': 'crossbow', 'name': 'Armbrust', 'type': 'weapon', 'subtype': 'ranged', 'slot': 'weapon', 'price': 1200, 'damage': 55, 'strength': 11, 'required_level': 10, 'description': 'Durchschlägt selbst schwere Rüstungen'},
    
    # === ARMOR - BODY ===
    {'id': 'armor_leather', 'name': 'Lederrüstung', 'type': 'armor', 'subtype': 'body', 'slot': 'armor', 'price': 80, 'defense': 10, 'required_level': 1, 'description': 'Leichte Rüstung für Beweglichkeit'},
    {'id': 'armor_chain', 'name': 'Kettenhemd', 'type': 'armor', 'subtype': 'body', 'slot': 'armor', 'price': 400, 'defense': 25, 'required_level': 5, 'description': 'Kettengeflecht bietet soliden Schutz'},
    {'id': 'armor_plate', 'name': 'Plattenrüstung', 'type': 'armor', 'subtype': 'body', 'slot': 'armor', 'price': 3000, 'defense': 60, 'required_level': 12, 'description': 'Schwere Plattenpanzerung für maximalen Schutz'},
    
    # === ARMOR - HEAD ===
    {'id': 'helmet_iron', 'name': 'Eisenhelm', 'type': 'armor', 'subtype': 'head', 'slot': 'helmet', 'price': 50, 'defense': 5, 'required_level': 1, 'description': 'Schützt deinen Kopf vor Hieben'},
    {'id': 'helmet_steel', 'name': 'Stahlhelm', 'type': 'armor', 'subtype': 'head', 'slot': 'helmet', 'price': 300, 'defense': 15, 'required_level': 6, 'description': 'Verstärkter Helm aus Stahl'},
    
    # === ARMOR - SHIELD (OFFHAND) ===
    {'id': 'shield_wooden', 'name': 'Holzschild', 'type': 'armor', 'subtype': 'offhand', 'slot': 'offhand', 'price': 60, 'defense': 8, 'required_level': 1, 'description': 'Ein einfacher Holzschild'},
    {'id': 'shield_steel', 'name': 'Stahlschild', 'type': 'armor', 'subtype': 'offhand', 'slot': 'offhand', 'price': 600, 'defense': 30, 'required_level': 7, 'description': 'Massiver Schild aus reinem Stahl'},
    {'id': 'shield_dragon', 'name': 'Drachenschuppenschild', 'type': 'armor', 'subtype': 'offhand', 'slot': 'offhand', 'price': 4000, 'defense': 70, 'required_level': 16, 'description': 'Aus echten Drachenschuppen gefertigt'},
    
    # === OFFHAND - DUAL WIELD ===
    {'id': 'dagger_offhand', 'name': 'Zweitdolch', 'type': 'weapon', 'subtype': 'dual', 'slot': 'offhand', 'price': 200, 'damage': 12, 'strength': 2, 'dexterity': 3, 'required_level': 4, 'description': 'Für die freie Hand - perfekt für schnelle Angriffe'},
    {'id': 'knife_throwing', 'name': 'Wurfmesser', 'type': 'weapon', 'subtype': 'dual', 'slot': 'offhand', 'price': 150, 'damage': 10, 'dexterity': 4, 'required_level': 3, 'description': 'Leicht und tödlich'},
    
    # === BOOTS ===
    {'id': 'boots_leather', 'name': 'Lederstiefel', 'type': 'armor', 'subtype': 'boots', 'slot': 'boots', 'price': 40, 'speed': 2, 'required_level': 1, 'description': 'Leichte Stiefel für schnelle Bewegungen'},
    {'id': 'boots_steel', 'name': 'Stahlstiefel', 'type': 'armor', 'subtype': 'boots', 'slot': 'boots', 'price': 300, 'defense': 8, 'speed': 3, 'required_level': 6, 'description': 'Gepanzerte Stiefel mit verstärkten Sohlen'},
    {'id': 'boots_shadow', 'name': 'Schattenstiefel', 'type': 'armor', 'subtype': 'boots', 'slot': 'boots', 'price': 800, 'speed': 8, 'dexterity': 5, 'required_level': 10, 'description': 'Lautlos wie der Wind'},
    {'id': 'boots_dragon', 'name': 'Drachenschuppenstiefel', 'type': 'armor', 'subtype': 'boots', 'slot': 'boots', 'price': 3500, 'defense': 15, 'speed': 12, 'required_level': 15, 'description': 'Unvergleichliche Beweglichkeit und Schutz'},
    
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
    # Level 1-3 (Early crimes - reduced energy costs for better progression)
    {'id': 'steal_bread', 'name': 'Brot stehlen', 'description': 'Stehle Brot vom Marktstand', 'energy_cost': 3, 'min_level': 1, 'base_success': 85, 'rewards': {'gold': (6, 18), 'xp': 2}, 'failure': {'jail_minutes': 10}, 'category': 'petty'},
    {'id': 'pickpocket', 'name': 'Taschendiebstahl', 'description': 'Stehle die Börse eines Bürgers', 'energy_cost': 5, 'min_level': 2, 'base_success': 70, 'rewards': {'gold': (24, 60), 'xp': 4}, 'failure': {'jail_minutes': 20}, 'category': 'theft'},
    {'id': 'rob_drunk', 'name': 'Betrunkenen ausrauben', 'description': 'Raube einen Betrunkenen vor der Taverne aus', 'energy_cost': 4, 'min_level': 2, 'base_success': 75, 'rewards': {'gold': (18, 48), 'xp': 3}, 'failure': {'jail_minutes': 15}, 'category': 'theft'},
    
    # Level 4-7 (Mid-game - balanced energy/reward)
    {'id': 'burglary', 'name': 'Einbruch', 'description': 'Breche in ein Haus ein', 'energy_cost': 8, 'min_level': 4, 'base_success': 55, 'rewards': {'gold': (60, 180), 'xp': 10}, 'failure': {'jail_minutes': 40, 'gold_fine': 30}, 'category': 'burglary'},
    {'id': 'steal_horse', 'name': 'Pferd stehlen', 'description': 'Stehle ein Pferd vom Stall', 'energy_cost': 10, 'min_level': 5, 'base_success': 50, 'rewards': {'gold': (120, 240), 'xp': 15}, 'failure': {'jail_minutes': 60, 'gold_fine': 50}, 'category': 'theft'},
    {'id': 'rob_merchant', 'name': 'Händler überfallen', 'description': 'Überfalle einen reisenden Händler', 'energy_cost': 10, 'min_level': 6, 'base_success': 50, 'rewards': {'gold': (120, 360), 'xp': 18}, 'failure': {'jail_minutes': 80, 'gold_fine': 80}, 'category': 'robbery'},
    {'id': 'blackmail', 'name': 'Erpressung', 'description': 'Erpresse einen wohlhabenden Bürger', 'energy_cost': 12, 'min_level': 7, 'base_success': 45, 'rewards': {'gold': (240, 480), 'xp': 22}, 'failure': {'jail_minutes': 100, 'gold_fine': 150}, 'category': 'extortion'},
    
    # Level 8-12 (High risk/reward)
    {'id': 'heist_shop', 'name': 'Laden ausrauben', 'description': 'Raube einen Waffenladen aus', 'energy_cost': 15, 'min_level': 8, 'base_success': 40, 'rewards': {'gold': (360, 720), 'xp': 30, 'item_chance': ('sword_steel', 15)}, 'failure': {'jail_minutes': 120, 'gold_fine': 200, 'injury': 15}, 'category': 'heist'},
    {'id': 'kidnapping', 'name': 'Entführung', 'description': 'Entführe ein Familienmitglied eines Adeligen', 'energy_cost': 18, 'min_level': 10, 'base_success': 35, 'rewards': {'gold': (600, 1200), 'xp': 42}, 'failure': {'jail_minutes': 180, 'gold_fine': 400, 'injury': 25}, 'category': 'major'},
    {'id': 'rob_treasury', 'name': 'Schatzkammer ausrauben', 'description': 'Wage einen Überfall auf die königliche Schatzkammer', 'energy_cost': 18, 'min_level': 10, 'base_success': 35, 'rewards': {'gold': (600, 1800), 'xp': 48}, 'failure': {'jail_minutes': 240, 'gold_fine': 300, 'injury': 20}, 'category': 'heist'},
    
    # Level 13+ (Legendary - high energy, high reward)
    {'id': 'assassination', 'name': 'Attentat', 'description': 'Führe einen Auftragsmord aus', 'energy_cost': 22, 'min_level': 13, 'base_success': 30, 'rewards': {'gold': (1200, 3000), 'xp': 72}, 'failure': {'jail_minutes': 360, 'gold_fine': 800, 'injury': 40}, 'category': 'assassination'},
    {'id': 'dragon_egg_theft', 'name': 'Drachenei stehlen', 'description': 'Stehle ein Drachenei aus einer Höhle', 'energy_cost': 30, 'min_level': 18, 'base_success': 20, 'rewards': {'gold': (3600, 9600), 'xp': 180}, 'failure': {'jail_minutes': 480, 'gold_fine': 2000, 'injury': 60}, 'category': 'legendary'},
]

# ============================================================================
# MASTER DATA - QUESTS
# ============================================================================

MASTER_QUESTS = [
    # Knight Quests - Combat & Honor focused
    {'id': 'quest_rats', 'name': 'Rattenplage', 'description': 'Töte 10 Ratten in den Stadtkanälen', 'min_level': 1, 'energy_cost': 10, 'duration_minutes': 15, 'rewards': {'gold': 60, 'xp': 12}, 'repeatable': True, 'paths': ['knight', 'shadow']},
    {'id': 'quest_escort', 'name': 'Händler-Eskorte', 'description': 'Eskortiere einen Händler sicher durch den Wald', 'min_level': 3, 'energy_cost': 14, 'duration_minutes': 20, 'rewards': {'gold': 120, 'xp': 30}, 'repeatable': True, 'paths': ['knight', 'noble']},
    {'id': 'quest_wolves', 'name': 'Wolfsrudel', 'description': 'Eliminiere ein Wolfsrudel das Reisende bedroht', 'min_level': 5, 'energy_cost': 18, 'duration_minutes': 30, 'rewards': {'gold': 240, 'xp': 48}, 'repeatable': True, 'paths': ['knight']},
    {'id': 'quest_bandit_camp', 'name': 'Banditenlager', 'description': 'Zerstöre ein Banditenlager außerhalb der Stadt', 'min_level': 5, 'energy_cost': 22, 'duration_minutes': 45, 'rewards': {'gold': 300, 'xp': 60, 'item': 'sword_steel'}, 'repeatable': False, 'paths': ['knight']},
    {'id': 'quest_rescue', 'name': 'Rettungsmission', 'description': 'Rette einen verschleppten Bürger aus Feindeshand', 'min_level': 8, 'energy_cost': 25, 'duration_minutes': 60, 'rewards': {'gold': 600, 'xp': 96}, 'repeatable': True, 'paths': ['knight']},
    {'id': 'quest_artifact', 'name': 'Verlorenes Artefakt', 'description': 'Finde ein verlorenes Artefakt in den Ruinen', 'min_level': 10, 'energy_cost': 30, 'duration_minutes': 90, 'rewards': {'gold': 960, 'xp': 144}, 'repeatable': False, 'paths': ['knight', 'shadow']},
    {'id': 'quest_dragon', 'name': 'Drachen-Bedrohung', 'description': 'Vertreibe einen jungen Drachen aus den Bergen', 'min_level': 15, 'energy_cost': 35, 'duration_minutes': 90, 'rewards': {'gold': 2400, 'xp': 240, 'item': 'relic_dragon_tooth'}, 'repeatable': False, 'paths': ['knight']},
    
    # Shadow Quests - Stealth & Crime focused
    {'id': 'quest_shadow_intel', 'name': 'Geheime Informationen', 'description': 'Beschaffe vertrauliche Informationen aus dem Stadtarchiv', 'min_level': 1, 'energy_cost': 10, 'duration_minutes': 15, 'rewards': {'gold': 80, 'xp': 12}, 'repeatable': True, 'paths': ['shadow']},
    {'id': 'quest_shadow_heist', 'name': 'Einbruch', 'description': 'Stehle wertvolle Ware aus einem Händlerhaus', 'min_level': 4, 'energy_cost': 16, 'duration_minutes': 25, 'rewards': {'gold': 200, 'xp': 40}, 'repeatable': True, 'paths': ['shadow']},
    {'id': 'quest_shadow_assassin', 'name': 'Auftragsmord', 'description': 'Eliminiere ein Ziel im Auftrag der Gilde', 'min_level': 8, 'energy_cost': 24, 'duration_minutes': 50, 'rewards': {'gold': 720, 'xp': 100}, 'repeatable': True, 'paths': ['shadow']},
    {'id': 'quest_shadow_poison', 'name': 'Giftmischer', 'description': 'Braue ein tödliches Gift für die Schattengilde', 'min_level': 12, 'energy_cost': 28, 'duration_minutes': 75, 'rewards': {'gold': 1200, 'xp': 160}, 'repeatable': False, 'paths': ['shadow']},
    
    # Noble Quests - Commerce & Diplomacy focused
    {'id': 'quest_noble_trade', 'name': 'Handelsabkommen', 'description': 'Verhandle ein profitables Handelsabkommen mit einem Königreich', 'min_level': 1, 'energy_cost': 8, 'duration_minutes': 12, 'rewards': {'gold': 100, 'xp': 10}, 'repeatable': True, 'paths': ['noble']},
    {'id': 'quest_noble_invest', 'name': 'Investition', 'description': 'Investiere in ein vielversprechendes Handelsunternehmen', 'min_level': 4, 'energy_cost': 12, 'duration_minutes': 20, 'rewards': {'gold': 250, 'xp': 35}, 'repeatable': True, 'paths': ['noble']},
    {'id': 'quest_noble_caravan', 'name': 'Karawanen-Geschäft', 'description': 'Organisiere eine profitable Handelskarawane', 'min_level': 7, 'energy_cost': 18, 'duration_minutes': 40, 'rewards': {'gold': 600, 'xp': 80}, 'repeatable': True, 'paths': ['noble']},
    {'id': 'quest_noble_monopoly', 'name': 'Marktmonopol', 'description': 'Erlange die Kontrolle über den Gewürzhandel', 'min_level': 12, 'energy_cost': 26, 'duration_minutes': 80, 'rewards': {'gold': 1800, 'xp': 180}, 'repeatable': False, 'paths': ['noble']},
]

# ============================================================================
# MASTER DATA - CREATURES (for Hunting)
# ============================================================================

MASTER_CREATURES = [
    # Balanced for new energy economy - reduced costs, increased rewards
    {'id': 'wolf', 'name': 'Wolf', 'hp': 30, 'power': 15, 'min_level': 5, 'energy_cost': 12, 'rewards': {'gold': (40, 100), 'xp': 18}},
    {'id': 'bear', 'name': 'Bär', 'hp': 60, 'power': 35, 'min_level': 10, 'energy_cost': 20, 'rewards': {'gold': (120, 240), 'xp': 48}},
    {'id': 'troll', 'name': 'Troll', 'hp': 100, 'power': 50, 'min_level': 15, 'energy_cost': 28, 'rewards': {'gold': (360, 720), 'xp': 120}},
    {'id': 'dragon_young', 'name': 'Junger Drache', 'hp': 200, 'power': 80, 'min_level': 20, 'energy_cost': 40, 'rewards': {'gold': (1200, 3600), 'xp': 360, 'item_chance': ('relic_dragon_tooth', 25)}},
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
    {"id": "aethoria_capital", "name": "Aethoria Prime", "desc": "The capital of the Realm. Trade, power, and intrigue converge.", "image": "https://images.unsplash.com/photo-1533154683836-84ea7a0bc310?w=400&q=50", "type": "Capital", "danger": "Medium", "min_level": 1, "travel_cost": 0},
    {"id": "ironhold", "name": "Ironhold", "desc": "A fortress city of steel and fire. Home to the greatest warriors.", "image": "https://images.unsplash.com/photo-1621947081720-86970823b77a?w=400&q=50", "type": "Military", "danger": "High", "min_level": 3, "travel_cost": 50},
    {"id": "shadowfen", "name": "Shadowfen", "desc": "A city of fog and secrets, where rogues and thieves hold court. Home of the Shadow Guild.", "image": "https://images.unsplash.com/photo-1518709766631-a6a7f45921c3?w=400&q=50", "type": "Underworld", "danger": "Very High", "min_level": 2, "travel_cost": 50},
    {"id": "goldenveil", "name": "Goldenveil", "desc": "The Realm's most prosperous trading city. Every merchant dreams of it.", "image": "https://images.unsplash.com/photo-1501183638710-841dd1904471?w=400&q=50", "type": "Commerce", "danger": "Low", "min_level": 2, "travel_cost": 50},
    {"id": "stonecrest", "name": "Stonecrest", "desc": "Ancient mountains hiding powerful arcane secrets in their caves.", "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=50", "type": "Arcane", "danger": "High", "min_level": 5, "travel_cost": 75},
    {"id": "crystalmere", "name": "Crystalmere", "desc": "A lakeside city of extraordinary beauty and political scheming.", "image": "https://images.unsplash.com/photo-1499678329028-101435549a4e?w=400&q=50", "type": "Noble", "danger": "Medium", "min_level": 4, "travel_cost": 60},
    {"id": "embervast", "name": "Embervast", "desc": "The volcanic borderlands, rich in dragon-forged materials.", "image": "https://images.unsplash.com/photo-1527482797697-8795b05a13fe?w=400&q=50", "type": "Wilds", "danger": "Extreme", "min_level": 10, "travel_cost": 100},
    {"id": "tidehaven", "name": "Tidehaven", "desc": "A port city where smugglers and merchants clash over sea routes.", "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=50", "type": "Maritime", "danger": "High", "min_level": 6, "travel_cost": 70},
    {"id": "duskwood", "name": "Duskwood", "desc": "An ancient forest kingdom where shapeshifters and druids dwell.", "image": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=400&q=50", "type": "Forest", "danger": "Medium", "min_level": 4, "travel_cost": 55},
    {"id": "frostholm", "name": "Frostholm", "desc": "The frozen north: hard people, rare pelts, and glacier-locked tombs.", "image": "https://images.unsplash.com/photo-1491555103944-7c647fd857e6?w=400&q=50", "type": "Frozen", "danger": "Very High", "min_level": 12, "travel_cost": 120},
    {"id": "sunkeep", "name": "Sunkeep", "desc": "A desert kingdom where ruins of the First Empire still stand.", "image": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=400&q=50", "type": "Desert", "danger": "High", "min_level": 8, "travel_cost": 85},
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
    """Calculate XP required for next level (remaining XP needed)"""
    if current_level >= len(LEVEL_XP_REQUIREMENTS):
        return 0  # Max level reached
    
    next_level_threshold = LEVEL_XP_REQUIREMENTS[current_level]
    return next_level_threshold - current_xp  # How much XP is still needed

def ensure_tz_aware(dt):
    """Ensure datetime is timezone-aware (UTC)"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    if isinstance(dt, datetime) and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


async def check_idempotency(idempotency_key: str, user_id: str, operation: str) -> Optional[dict]:
    """
    Check if operation was already executed with this idempotency key.
    Returns cached result if found, None if this is a new operation.
    Idempotency keys expire after 24 hours.
    """
    if not idempotency_key:
        return None
    
    # Check for existing operation
    existing = await db.idempotency_keys.find_one({
        'key': idempotency_key,
        'user_id': user_id,
        'operation': operation
    })
    
    if existing:
        # Key exists - return cached result
        logger.info(f"Idempotent request detected: {operation} - {idempotency_key}")
        return existing.get('result')
    
    return None

async def store_idempotency_result(idempotency_key: str, user_id: str, operation: str, result: dict):
    """Store operation result for idempotency checks"""
    if not idempotency_key:
        return
    
    await db.idempotency_keys.insert_one({
        'key': idempotency_key,
        'user_id': user_id,
        'operation': operation,
        'result': result,
        'created_at': datetime.now(timezone.utc),
        'expires_at': datetime.now(timezone.utc) + timedelta(hours=24)
    })
    
    # Create TTL index for automatic cleanup (only once)
    try:
        await db.idempotency_keys.create_index('expires_at', expireAfterSeconds=0)
    except Exception:
        pass  # Index may already exist

async def regenerate_energy(user: dict) -> int:
    """Calculate and update current energy"""
    last_regen = user.get('last_energy_regen')
    current_energy = user.get('energy', MAX_ENERGY)
    
    if not last_regen or current_energy >= MAX_ENERGY:
        return min(current_energy, MAX_ENERGY)
    
    if isinstance(last_regen, str):
        last_regen = datetime.fromisoformat(last_regen.replace('Z', '+00:00'))
    elif isinstance(last_regen, datetime) and last_regen.tzinfo is None:
        last_regen = last_regen.replace(tzinfo=timezone.utc)
    
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
        release_time = ensure_tz_aware(release_time)
        
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
    elif isinstance(last_regen, datetime) and last_regen.tzinfo is None:
        last_regen = last_regen.replace(tzinfo=timezone.utc)
    
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
        release_time = ensure_tz_aware(release_time)
        
        if datetime.now(timezone.utc) >= release_time:
            await db.dungeon_sessions.update_one(
                {'user_id': user['id'], 'released': False},
                {'$set': {'released': True, 'actual_release': datetime.now(timezone.utc)}}
            )
            return None
        else:
            seconds_remaining = int((release_time - datetime.now(timezone.utc)).total_seconds())
            return {
                'in_dungeon': True,
                'release_time': release_time.isoformat(),
                'seconds_remaining': max(0, seconds_remaining),
                'crime': dungeon_session.get('crime_name', 'Unknown')
            }
    return None

async def check_hospital_status(user: dict) -> Optional[dict]:
    """Check if user is in hospital"""
    hospital_session = await db.hospital_sessions.find_one({'user_id': user['id'], 'released': False})
    if hospital_session:
        release_time = hospital_session['release_time']
        release_time = ensure_tz_aware(release_time)
        
        if datetime.now(timezone.utc) >= release_time:
            await db.hospital_sessions.update_one(
                {'user_id': user['id'], 'released': False},
                {'$set': {'released': True, 'actual_release': datetime.now(timezone.utc)}}
            )
            await db.users.update_one({'id': user['id']}, {'$set': {'hp': MAX_HP}})
            return None
        else:
            seconds_remaining = int((release_time - datetime.now(timezone.utc)).total_seconds())
            return {
                'in_hospital': True,
                'release_time': release_time.isoformat(),
                'seconds_remaining': max(0, seconds_remaining),
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
    idempotency_key: Optional[str] = None  # Optional idempotency key for preventing duplicate purchases

class BankDepositRequest(BaseModel):
    amount: int = Field(..., ge=1)
    idempotency_key: Optional[str] = None  # Optional idempotency key for preventing duplicate deposits

class BankWithdrawRequest(BaseModel):
    amount: int = Field(..., ge=1)
    idempotency_key: Optional[str] = None  # Optional idempotency key for preventing duplicate withdrawals

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
    slot: Literal['weapon', 'offhand', 'armor', 'helmet', 'boots']

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
# FASTAPI APP SETUP + RATE LIMITING
# ============================================================================

# Initialize rate limiter (in-memory backend)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Realm of Aethoria API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def startup_event():
    await seed_database()
    
    # MIGRATION: Rename 'shield' to 'offhand' and add 'boots' slot for existing users
    try:
        users_with_old_equipment = await db.users.find({'equipment.shield': {'$exists': True}}).to_list(1000)
        if users_with_old_equipment:
            for user in users_with_old_equipment:
                equipment = user.get('equipment', {})
                # Move shield to offhand
                if 'shield' in equipment:
                    equipment['offhand'] = equipment.pop('shield')
                # Add boots if missing
                if 'boots' not in equipment:
                    equipment['boots'] = None
                
                await db.users.update_one(
                    {'id': user['id']},
                    {'$set': {'equipment': equipment}}
                )
            logger.info(f"✓ Migrated {len(users_with_old_equipment)} users: shield→offhand, added boots slot")
    except Exception as e:
        logger.warning(f"Migration warning: {e}")
    
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
        'equipment': {'weapon': None, 'offhand': None, 'armor': None, 'helmet': None, 'boots': None},
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
        complete_time = ensure_tz_aware(complete_time)
        
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
        complete_time = ensure_tz_aware(complete_time)
        
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
        arrival_time = ensure_tz_aware(arrival_time)
        
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
    total_strength_bonus = 0
    total_speed_bonus = 0
    total_dexterity_bonus = 0
    
    for slot, item_id in current_user.get('equipment', {}).items():
        if item_id:
            item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
            if item_data:
                equipped_items.append({**item_data, 'slot': slot})
                if 'defense' in item_data:
                    total_defense_bonus += item_data['defense']
                if 'strength' in item_data:
                    total_strength_bonus += item_data['strength']
                if 'speed' in item_data:
                    total_speed_bonus += item_data['speed']
                if 'dexterity' in item_data:
                    total_dexterity_bonus += item_data['dexterity']
    
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
            'xp': current_user['xp'],
            'xp_required': calculate_xp_for_next_level(current_user['xp'], current_user['level']),
        },
        'stats': {
            'strength': current_user['stats']['strength'],
            'dexterity': current_user['stats']['dexterity'],
            'speed': current_user['stats']['speed'],
            'defense': current_user['stats']['defense'],
            'total_strength': current_user['stats']['strength'] + total_strength_bonus,
            'total_dexterity': current_user['stats']['dexterity'] + total_dexterity_bonus,
            'total_speed': current_user['stats']['speed'] + total_speed_bonus,
            'total_defense': current_user['stats']['defense'] + total_defense_bonus,
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
@limiter.limit("40/minute")  # Max 40 training sessions per minute
async def start_training(req: TrainRequest, request: Request, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check restrictions
    if await check_dungeon_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst nicht trainieren während du im Kerker bist")
    
    if await check_hospital_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst nicht trainieren während du verletzt bist")
    
    # Check if already training THIS specific stat
    existing = await db.training_sessions.find_one({'user_id': user_id, 'stat': req.stat, 'completed': False})
    if existing:
        raise HTTPException(status_code=400, detail=f"Du trainierst {req.stat} bereits")
    
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
@limiter.limit("30/minute")  # Max 30 crimes per minute per IP
async def commit_crime(req: CrimeRequest, request: Request, current_user: dict = Depends(get_current_user)):
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
        
        # Economy log
        logger.info(f"Crime success: {user_id} | {crime['name']} | +{gold_reward}g, +{xp_reward}xp | Roll: {roll}/{success_chance}")
        
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
@limiter.limit("20/minute")  # Max 20 attacks per minute per IP
async def attack_player(req: CombatRequest, request: Request, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check restrictions
    if await check_dungeon_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst nicht angreifen während du im Kerker bist")
    
    if await check_hospital_status(current_user):
        raise HTTPException(status_code=400, detail="Du kannst nicht angreifen während du verletzt bist")
    
    # Check energy (reduced from 25 → 15 for better combat accessibility)
    current_energy = await regenerate_energy(current_user)
    if current_energy < 15:
        raise HTTPException(status_code=400, detail="Nicht genug Energie (benötigt: 15)")
    
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
        {'$inc': {'energy': -15}, '$set': {'last_energy_regen': datetime.now(timezone.utc)}}
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
        # For mug action: only steal gold, no damage
        if req.action == 'mug':
            max_steal = target['gold'] // 3  # Max 33% of target's gold
            gold_stolen = min(target['gold'], random.randint(20, max(100, max_steal)))
            
            if gold_stolen > 0:
                await db.users.update_one({'id': target['id']}, {'$inc': {'gold': -gold_stolen}})
                await db.users.update_one({'id': user_id}, {'$inc': {'gold': gold_stolen}})
            
            # Chance to get jailed (30% for successful mug)
            if random.random() < 0.30:
                jail_minutes = random.randint(15, 45)
                await db.dungeon_sessions.insert_one({
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'crime_name': 'Ausrauben',
                    'arrest_time': datetime.now(timezone.utc),
                    'release_time': datetime.now(timezone.utc) + timedelta(minutes=jail_minutes),
                    'released': False
                })
                
                # Log combat (mug)
                combat_log = {
                    'id': str(uuid.uuid4()),
                    'attacker_id': user_id,
                    'attacker_name': current_user['username'],
                    'defender_id': target['id'],
                    'defender_name': target['username'],
                    'action': 'mug',
                    'winner': 'attacker',
                    'damage': 0,
                    'gold_stolen': gold_stolen,
                    'hospital_minutes': 0,
                    'timestamp': datetime.now(timezone.utc)
                }
                await db.combat_logs.insert_one(combat_log)
                
                # Update stats
                await db.users.update_one({'id': user_id}, {'$inc': {'combat_wins': 1}})
                await db.users.update_one({'id': target['id']}, {'$inc': {'combat_losses': 1}})
                
                # Ticker
                await db.ticker_events.insert_one({
                    'id': str(uuid.uuid4()),
                    'event': f'{current_user["username"]} hat {target["username"]} ausgeraubt und wurde erwischt!',
                    'type': 'crime',
                    'user_id': user_id,
                    'created_at': datetime.now(timezone.utc)
                })
                
                return {
                    'success': True,
                    'won': True,
                    'message': f'Du hast {gold_stolen} Gold gestohlen, wurdest aber erwischt und landest im Kerker für {jail_minutes} Minuten!',
                    'gold_stolen': gold_stolen,
                    'damage': 0,
                    'jailed': True,
                    'jail_minutes': jail_minutes
                }
            else:
                # Successful mug without getting caught
                combat_log = {
                    'id': str(uuid.uuid4()),
                    'attacker_id': user_id,
                    'attacker_name': current_user['username'],
                    'defender_id': target['id'],
                    'defender_name': target['username'],
                    'action': 'mug',
                    'winner': 'attacker',
                    'damage': 0,
                    'gold_stolen': gold_stolen,
                    'hospital_minutes': 0,
                    'timestamp': datetime.now(timezone.utc)
                }
                await db.combat_logs.insert_one(combat_log)
                
                # Update stats
                await db.users.update_one({'id': user_id}, {'$inc': {'combat_wins': 1}})
                await db.users.update_one({'id': target['id']}, {'$inc': {'combat_losses': 1}})
                
                # Ticker
                await db.ticker_events.insert_one({
                    'id': str(uuid.uuid4()),
                    'event': f'{current_user["username"]} hat {target["username"]} ausgeraubt!',
                    'type': 'crime',
                    'user_id': user_id,
                    'created_at': datetime.now(timezone.utc)
                })
                
                return {
                    'success': True,
                    'won': True,
                    'message': f'Du hast {gold_stolen} Gold gestohlen!',
                    'gold_stolen': gold_stolen,
                    'damage': 0,
                    'jailed': False
                }
        
        # For normal attack/hospitalize: deal damage
        else:
            # Calculate damage
            base_damage = random.randint(20, 50)
            damage = max(10, base_damage - defender_armor_bonus // 2)
            new_target_hp = max(0, target_hp - damage)
            
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
            gold_stolen = 0
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
        
        # Economy log
        logger.info(f"Combat victory: {user_id} vs {target['id']} | {req.action} | dmg:{damage} | gold:{gold_stolen} | xp:{xp_gain}")
        
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




# ============================================================================
# QUESTS SYSTEM
# ============================================================================

@app.get("/api/game/quests/available")
async def get_available_quests(current_user: dict = Depends(get_current_user)):
    """Get available quests"""
    # Check active quest
    active = await db.user_quests.find_one({'user_id': current_user['id'], 'status': 'active'}, {'_id': 0})
    
    # Get completed (non-repeatable) quests
    completed_non_repeat = await db.user_quests.find(
        {'user_id': current_user['id'], 'status': 'completed'},
        {'quest_id': 1}
    ).to_list(100)
    completed_ids = [q['quest_id'] for q in completed_non_repeat]
    
    # Filter available
    user_path = current_user.get('path_choice', 'knight')
    available = []
    for quest in MASTER_QUESTS:
        # Check level
        if current_user['level'] < quest['min_level']:
            continue
        # Check path compatibility
        if user_path not in quest.get('paths', ['knight', 'shadow', 'noble']):
            continue
        # Check if already completed (and not repeatable)
        if not quest.get('repeatable', False) and quest['id'] in completed_ids:
            continue
        available.append(quest)
    
    return {
        'active_quest': serialize_doc(active),
        'available_quests': available
    }

@app.post("/api/game/quests/accept")
async def accept_quest(req: QuestRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check if already on quest
    active = await db.user_quests.find_one({'user_id': user_id, 'status': 'active'})
    if active:
        raise HTTPException(status_code=400, detail="Du hast bereits eine aktive Quest")
    
    # Find quest
    quest = next((q for q in MASTER_QUESTS if q['id'] == req.quest_id), None)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest nicht gefunden")
    
    if current_user['level'] < quest['min_level']:
        raise HTTPException(status_code=400, detail=f"Level {quest['min_level']} erforderlich")
    
    # Check energy
    current_energy = await regenerate_energy(current_user)
    if current_energy < quest['energy_cost']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Energie (benötigt: {quest['energy_cost']})")
    
    # Deduct energy
    await db.users.update_one(
        {'id': user_id},
        {'$inc': {'energy': -quest['energy_cost']}, '$set': {'last_energy_regen': datetime.now(timezone.utc)}}
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
        'status': 'active'
    }
    await db.user_quests.insert_one(user_quest)
    
    return {
        'success': True,
        'message': f'Quest "{quest["name"]}" akzeptiert!',
        'complete_time': complete_time.isoformat(),
        'duration_minutes': quest['duration_minutes']
    }

@app.post("/api/game/quests/complete")
async def complete_quest(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    user_quest = await db.user_quests.find_one({'user_id': user_id, 'status': 'active'})
    if not user_quest:
        raise HTTPException(status_code=404, detail="Keine aktive Quest")
    
    complete_time = user_quest['complete_time']
    if isinstance(complete_time, str):
        complete_time = datetime.fromisoformat(complete_time.replace('Z', '+00:00'))
    
    if datetime.now(timezone.utc) < complete_time:
        remaining = int((complete_time - datetime.now(timezone.utc)).total_seconds() / 60)
        raise HTTPException(status_code=400, detail=f"Quest noch nicht abgeschlossen ({remaining} Min verbleibend)")
    
    # Find quest
    quest = next((q for q in MASTER_QUESTS if q['id'] == user_quest['quest_id']), None)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest Daten nicht gefunden")
    
    # Rewards
    gold_reward = quest['rewards']['gold']
    xp_reward = quest['rewards']['xp']
    
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': gold_reward, 'xp': xp_reward}})
    
    # Mark completed
    await db.user_quests.update_one(
        {'id': user_quest['id']},
        {'$set': {'status': 'completed', 'completed_at': datetime.now(timezone.utc)}}
    )
    
    # Item reward
    item_reward = None
    if 'item' in quest['rewards']:
        item_id = quest['rewards']['item']
        existing = await db.inventories.find_one({'user_id': user_id, 'item_id': item_id})
        if existing:
            await db.inventories.update_one({'user_id': user_id, 'item_id': item_id}, {'$inc': {'quantity': 1}})
        else:
            await db.inventories.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'item_id': item_id,
                'quantity': 1,
                'acquired_at': datetime.now(timezone.utc)
            })
        
        item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
        item_reward = item_data['name'] if item_data else item_id
    
    # Level up check
    updated_user = await db.users.find_one({'id': user_id})
    new_level = calculate_level(updated_user['xp'])
    level_up = new_level > updated_user['level']
    if level_up:
        await db.users.update_one({'id': user_id}, {'$set': {'level': new_level}})
        await log_event('quest', f'{current_user["username"]} reached level {new_level}!', user_id)
    
    await log_event('quest', f'{current_user["username"]} completed quest: {quest["name"]}', user_id)
    
    message = f'Quest abgeschlossen! +{gold_reward} Gold, +{xp_reward} XP'
    if item_reward:
        message += f', +1 {item_reward}'
    
    return {
        'success': True,
        'message': message,
        'rewards': {'gold': gold_reward, 'xp': xp_reward, 'item': item_reward},
        'level_up': level_up,
        'new_level': new_level if level_up else None
    }

# ============================================================================
# INVENTORY SYSTEM
# ============================================================================

@app.get("/api/game/inventory")
async def get_inventory(current_user: dict = Depends(get_current_user)):
    """Get inventory"""
    inv_items = await db.inventories.find({'user_id': current_user['id']}, {'_id': 0}).to_list(200)
    
    enriched = []
    for inv_item in inv_items:
        item_data = next((i for i in MASTER_ITEMS if i['id'] == inv_item['item_id']), None)
        if item_data:
            enriched.append({**inv_item, 'item_details': item_data})
    
    return {
        'inventory': serialize_doc(enriched),
        'equipped': current_user.get('equipment', {})
    }

@app.post("/api/game/inventory/use")
async def use_item(req: UseItemRequest, current_user: dict = Depends(get_current_user)):
    """Use consumable"""
    user_id = current_user['id']
    
    inv_item = await db.inventories.find_one({'user_id': user_id, 'item_id': req.item_id})
    if not inv_item or inv_item['quantity'] < 1:
        raise HTTPException(status_code=404, detail="Item nicht im Inventar")
    
    item_data = next((i for i in MASTER_ITEMS if i['id'] == req.item_id), None)
    if not item_data or item_data['type'] != 'consumable':
        raise HTTPException(status_code=400, detail="Dieser Gegenstand kann nicht benutzt werden")
    
    # Apply effects
    effect = item_data.get('effect', {})
    updates = {}
    messages = []
    
    if 'hp' in effect:
        current_hp = await regenerate_hp(current_user)
        new_hp = min(MAX_HP, current_hp + effect['hp'])
        updates['hp'] = new_hp
        messages.append(f"+{effect['hp']} HP")
    
    if 'energy' in effect:
        current_energy = await regenerate_energy(current_user)
        new_energy = min(MAX_ENERGY, current_energy + effect['energy'])
        updates['energy'] = new_energy
        messages.append(f"+{effect['energy']} Energie")
    
    if updates:
        await db.users.update_one({'id': user_id}, {'$set': updates})
    
    # Remove from inventory
    if inv_item['quantity'] == 1:
        await db.inventories.delete_one({'id': inv_item['id']})
    else:
        await db.inventories.update_one({'id': inv_item['id']}, {'$inc': {'quantity': -1}})
    
    return {
        'success': True,
        'message': f'{item_data["name"]} benutzt: {", ".join(messages)}',
        'effects': effect
    }

@app.post("/api/game/inventory/equip")
async def equip_item(req: EquipItemRequest, current_user: dict = Depends(get_current_user)):
    """Equip item"""
    user_id = current_user['id']
    
    # Check if in inventory
    inv_item = await db.inventories.find_one({'user_id': user_id, 'item_id': req.item_id})
    if not inv_item:
        raise HTTPException(status_code=404, detail="Item nicht im Inventar")
    
    item_data = next((i for i in MASTER_ITEMS if i['id'] == req.item_id), None)
    if not item_data:
        raise HTTPException(status_code=404, detail="Item Daten nicht gefunden")
    
    # Check if equipable
    if item_data.get('slot') != req.slot:
        raise HTTPException(status_code=400, detail=f"Dieser Gegenstand gehört in Slot: {item_data.get('slot', 'none')}")
    
    # Unequip current item in slot (return to inventory)
    current_equipment = current_user.get('equipment', {})
    old_item_id = current_equipment.get(req.slot)
    
    if old_item_id:
        existing_inv = await db.inventories.find_one({'user_id': user_id, 'item_id': old_item_id})
        if existing_inv:
            await db.inventories.update_one({'user_id': user_id, 'item_id': old_item_id}, {'$inc': {'quantity': 1}})
        else:
            await db.inventories.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'item_id': old_item_id,
                'quantity': 1,
                'acquired_at': datetime.now(timezone.utc)
            })
    
    # Remove new item from inventory
    if inv_item['quantity'] == 1:
        await db.inventories.delete_one({'id': inv_item['id']})
    else:
        await db.inventories.update_one({'id': inv_item['id']}, {'$inc': {'quantity': -1}})
    
    # Equip
    await db.users.update_one(
        {'id': user_id},
        {'$set': {f'equipment.{req.slot}': req.item_id}}
    )
    
    # Get updated equipment
    updated_user = await db.users.find_one({'id': user_id})
    equipped_items = {}
    for slot, item_id in updated_user.get('equipment', {}).items():
        if item_id:
            item_info = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
            if item_info:
                equipped_items[slot] = item_info
    
    return {
        'success': True,
        'message': f'{item_data["name"]} ausgerüstet',
        'equipment': equipped_items
    }

@app.post("/api/game/inventory/unequip")
async def unequip_item(slot: str, current_user: dict = Depends(get_current_user)):
    """Unequip item from slot"""
    user_id = current_user['id']
    
    equipment = current_user.get('equipment', {})
    item_id = equipment.get(slot)
    
    if not item_id:
        raise HTTPException(status_code=400, detail="Kein Gegenstand in diesem Slot")
    
    # Return to inventory
    existing = await db.inventories.find_one({'user_id': user_id, 'item_id': item_id})
    if existing:
        await db.inventories.update_one({'user_id': user_id, 'item_id': item_id}, {'$inc': {'quantity': 1}})
    else:
        await db.inventories.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'item_id': item_id,
            'quantity': 1,
            'acquired_at': datetime.now(timezone.utc)
        })
    
    # Unequip
    await db.users.update_one({'id': user_id}, {'$set': {f'equipment.{slot}': None}})
    
    return {'success': True, 'message': 'Gegenstand abgelegt'}

# ============================================================================
# SHOP SYSTEM
# ============================================================================

@app.get("/api/game/shop/items")
async def get_shop_items(current_user: dict = Depends(get_current_user)):
    """Get shop inventory"""
    available = [item for item in MASTER_ITEMS if item['required_level'] <= current_user['level']]
    return available

@app.post("/api/game/shop/buy")
@limiter.limit("60/minute")  # Max 60 shop purchases per minute
async def buy_from_shop(item_id: str, quantity: int = 1, request: Request = None, current_user: dict = Depends(get_current_user)):
    """Buy from shop"""
    user_id = current_user['id']
    
    item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
    if not item_data:
        raise HTTPException(status_code=404, detail="Gegenstand nicht gefunden")
    
    if current_user['level'] < item_data['required_level']:
        raise HTTPException(status_code=400, detail=f"Level {item_data['required_level']} erforderlich")
    
    total_cost = item_data['price'] * quantity
    if current_user['gold'] < total_cost:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {total_cost})")
    
    # Deduct gold
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -total_cost}})
    
    # Add to inventory
    existing = await db.inventories.find_one({'user_id': user_id, 'item_id': item_id})
    if existing:
        await db.inventories.update_one({'user_id': user_id, 'item_id': item_id}, {'$inc': {'quantity': quantity}})
    else:
        await db.inventories.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'item_id': item_id,
            'quantity': quantity,
            'acquired_at': datetime.now(timezone.utc)
        })
    
    result = {
        'success': True,
        'message': f'{quantity}x {item_data["name"]} gekauft für {total_cost} Gold',
        'cost': total_cost
    }
    
    # Economy log
    logger.info(f"Shop purchase: {user_id} | {quantity}x {item_id} | -{total_cost}g")
    
    return result

# ============================================================================
# MARKET SYSTEM
# ============================================================================

@app.get("/api/game/market/listings")
async def get_market_listings(item_type: Optional[str] = None, limit: int = 50):
    """Get market listings"""
    query = {'active': True}
    if item_type:
        query['item_type'] = item_type
    
    listings = await db.market_listings.find(query, {'_id': 0}).sort('created_at', -1).limit(limit).to_list(limit)
    
    # Enrich
    enriched = []
    for listing in listings:
        item_data = next((i for i in MASTER_ITEMS if i['id'] == listing['item_id']), None)
        seller = await db.users.find_one({'id': listing['seller_id']}, {'username': 1, 'level': 1})
        
        enriched.append({
            **serialize_doc(listing),
            'item_details': item_data,
            'seller_name': seller['username'] if seller else 'Unknown',
            'seller_level': seller['level'] if seller else 1
        })
    
    return enriched

@app.post("/api/game/market/create")
async def create_market_listing(req: MarketListingCreate, current_user: dict = Depends(get_current_user)):
    """Create market listing"""
    user_id = current_user['id']
    
    inv_item = await db.inventories.find_one({'user_id': user_id, 'item_id': req.item_id})
    if not inv_item or inv_item['quantity'] < req.quantity:
        raise HTTPException(status_code=400, detail="Nicht genug Gegenstände im Inventar")
    
    item_data = next((i for i in MASTER_ITEMS if i['id'] == req.item_id), None)
    if not item_data:
        raise HTTPException(status_code=404, detail="Gegenstand nicht gefunden")
    
    # Remove from inventory
    if inv_item['quantity'] == req.quantity:
        await db.inventories.delete_one({'id': inv_item['id']})
    else:
        await db.inventories.update_one({'id': inv_item['id']}, {'$inc': {'quantity': -req.quantity}})
    
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
    await db.market_listings.insert_one(listing)
    
    return {
        'success': True,
        'message': f'Angebot erstellt: {req.quantity}x {item_data["name"]} für {listing["total_price"]} Gold',
        'listing_id': listing['id']
    }

@app.post("/api/game/market/buy")
@limiter.limit("60/minute")  # Max 60 market purchases per minute
async def buy_from_market(req: MarketBuyRequest, request: Request, current_user: dict = Depends(get_current_user)):
    """Buy from market with idempotency support"""
    user_id = current_user['id']
    
    # Check idempotency
    if req.idempotency_key:
        cached = await check_idempotency(req.idempotency_key, user_id, 'market_buy')
        if cached:
            return cached
    
    listing = await db.market_listings.find_one({'id': req.listing_id, 'active': True})
    if not listing:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    
    if listing['seller_id'] == user_id:
        raise HTTPException(status_code=400, detail="Du kannst nicht von dir selbst kaufen")
    
    if req.quantity > listing['quantity']:
        raise HTTPException(status_code=400, detail="Nicht genug verfügbar")
    
    total_cost = req.quantity * listing['price_per_unit']
    if current_user['gold'] < total_cost:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {total_cost})")
    
    # Transfer gold (atomic)
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -total_cost}})
    await db.users.update_one({'id': listing['seller_id']}, {'$inc': {'gold': total_cost}})
    
    # Add to buyer inventory
    existing = await db.inventories.find_one({'user_id': user_id, 'item_id': listing['item_id']})
    if existing:
        await db.inventories.update_one({'user_id': user_id, 'item_id': listing['item_id']}, {'$inc': {'quantity': req.quantity}})
    else:
        await db.inventories.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'item_id': listing['item_id'],
            'quantity': req.quantity,
            'acquired_at': datetime.now(timezone.utc)
        })
    
    # Update listing
    if req.quantity == listing['quantity']:
        await db.market_listings.update_one({'id': req.listing_id}, {'$set': {'active': False}})
    else:
        await db.market_listings.update_one(
            {'id': req.listing_id},
            {
                '$inc': {'quantity': -req.quantity},
                '$set': {'total_price': (listing['quantity'] - req.quantity) * listing['price_per_unit']}
            }
        )
    
    # Check merchant achievement
    total_trade_value = await db.market_listings.aggregate([
        {'$match': {'seller_id': user_id, 'active': False}},
        {'$group': {'_id': None, 'total': {'$sum': '$total_price'}}}
    ]).to_list(1)
    
    if total_trade_value and total_trade_value[0]['total'] >= 1000:
        await check_and_award_achievement(user_id, 'merchant')
    
    result = {
        'success': True,
        'message': f'{req.quantity}x {listing["item_name"]} gekauft für {total_cost} Gold',
        'cost': total_cost
    }
    
    # Store for idempotency
    if req.idempotency_key:
        await store_idempotency_result(req.idempotency_key, user_id, 'market_buy', result)
    
    logger.info(f"Market purchase: {user_id} bought {req.quantity}x {listing['item_id']} for {total_cost} gold from {listing['seller_id']}")
    return result

@app.get("/api/game/market/my-listings")
async def get_my_listings(current_user: dict = Depends(get_current_user)):
    """Get own listings"""
    listings = await db.market_listings.find(
        {'seller_id': current_user['id'], 'active': True},
        {'_id': 0}
    ).to_list(100)
    
    enriched = []
    for listing in listings:
        item_data = next((i for i in MASTER_ITEMS if i['id'] == listing['item_id']), None)
        enriched.append({**serialize_doc(listing), 'item_details': item_data})
    
    return enriched

@app.delete("/api/game/market/cancel/{listing_id}")
async def cancel_listing(listing_id: str, current_user: dict = Depends(get_current_user)):
    """Cancel listing"""
    listing = await db.market_listings.find_one({'id': listing_id, 'seller_id': current_user['id'], 'active': True})
    if not listing:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    
    # Return items
    existing = await db.inventories.find_one({'user_id': current_user['id'], 'item_id': listing['item_id']})
    if existing:
        await db.inventories.update_one({'user_id': current_user['id'], 'item_id': listing['item_id']}, {'$inc': {'quantity': listing['quantity']}})
    else:
        await db.inventories.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': current_user['id'],
            'item_id': listing['item_id'],
            'quantity': listing['quantity'],
            'acquired_at': datetime.now(timezone.utc)
        })
    
    await db.market_listings.update_one({'id': listing_id}, {'$set': {'active': False}})
    
    return {'success': True, 'message': f'{listing["quantity"]}x {listing["item_name"]} zurück im Inventar'}

# ============================================================================
# BANKING SYSTEM (Treasury + Bank)
# ============================================================================

@app.get("/api/game/bank/account")
async def get_bank_account(current_user: dict = Depends(get_current_user)):
    """Get bank account"""
    account = await db.bank_accounts.find_one({'user_id': current_user['id']}, {'_id': 0})
    if not account:
        account = {
            'id': str(uuid.uuid4()),
            'user_id': current_user['id'],
            'balance': 0,
            'created_at': datetime.now(timezone.utc)
        }
        await db.bank_accounts.insert_one(account)
    
    return serialize_doc(account)

@app.post("/api/game/bank/deposit")
@limiter.limit("60/minute")  # Max 60 deposits per minute
async def bank_deposit(req: BankDepositRequest, request: Request, current_user: dict = Depends(get_current_user)):
    """Deposit to bank with idempotency support"""
    user_id = current_user['id']
    
    # Check idempotency
    if req.idempotency_key:
        cached = await check_idempotency(req.idempotency_key, user_id, 'bank_deposit')
        if cached:
            return cached
    
    if current_user['gold'] < req.amount:
        raise HTTPException(status_code=400, detail="Nicht genug Gold")
    
    # Atomic transaction
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -req.amount}})
    await db.bank_accounts.update_one(
        {'user_id': user_id},
        {'$inc': {'balance': req.amount}},
        upsert=True
    )
    
    result = {'success': True, 'message': f'{req.amount} Gold eingezahlt'}
    
    # Store for idempotency
    if req.idempotency_key:
        await store_idempotency_result(req.idempotency_key, user_id, 'bank_deposit', result)
    
    logger.info(f"Bank deposit: {user_id} deposited {req.amount} gold")
    return result

@app.post("/api/game/bank/withdraw")
@limiter.limit("60/minute")  # Max 60 withdrawals per minute
async def bank_withdraw(req: BankWithdrawRequest, request: Request, current_user: dict = Depends(get_current_user)):
    """Withdraw from bank with idempotency support"""
    user_id = current_user['id']
    
    # Check idempotency
    if req.idempotency_key:
        cached = await check_idempotency(req.idempotency_key, user_id, 'bank_withdraw')
        if cached:
            return cached
    
    account = await db.bank_accounts.find_one({'user_id': user_id})
    if not account or account['balance'] < req.amount:
        raise HTTPException(status_code=400, detail="Nicht genug Gold auf dem Bankkonto")
    
    # Atomic transaction
    await db.bank_accounts.update_one({'user_id': user_id}, {'$inc': {'balance': -req.amount}})
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': req.amount}})
    
    # Check rich achievement
    updated_user = await db.users.find_one({'id': user_id})
    if updated_user['gold'] >= 10000:
        await check_and_award_achievement(user_id, 'rich')
    
    result = {'success': True, 'message': f'{req.amount} Gold abgehoben'}
    
    # Store for idempotency
    if req.idempotency_key:
        await store_idempotency_result(req.idempotency_key, user_id, 'bank_withdraw', result)
    
    logger.info(f"Bank withdraw: {user_id} withdrew {req.amount} gold")
    return result

# ============================================================================
# GUILDS SYSTEM
# ============================================================================

@app.get("/api/game/guilds")
async def get_guilds(limit: int = 50):
    """Get list of guilds"""
    guilds = await db.guilds.find({}, {'_id': 0}).sort('member_count', -1).limit(limit).to_list(limit)
    return serialize_doc(guilds)

@app.post("/api/game/guilds/create")
async def create_guild(req: GuildCreateRequest, current_user: dict = Depends(get_current_user)):
    """Create guild"""
    user_id = current_user['id']
    
    # Check if already in guild
    existing_membership = await db.guild_members.find_one({'user_id': user_id})
    if existing_membership:
        raise HTTPException(status_code=400, detail="Du bist bereits Mitglied einer Gilde")
    
    # Check name uniqueness
    existing_guild = await db.guilds.find_one({'name': req.name})
    if existing_guild:
        raise HTTPException(status_code=400, detail="Gildenname bereits vergeben")
    
    # Cost to create
    creation_cost = 5000
    if current_user['gold'] < creation_cost:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {creation_cost})")
    
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -creation_cost}})
    
    # Create guild
    guild_id = str(uuid.uuid4())
    guild = {
        'id': guild_id,
        'name': req.name,
        'description': req.description,
        'leader_id': user_id,
        'leader_name': current_user['username'],
        'member_count': 1,
        'created_at': datetime.now(timezone.utc)
    }
    await db.guilds.insert_one(guild)
    
    # Add member
    await db.guild_members.insert_one({
        'id': str(uuid.uuid4()),
        'guild_id': guild_id,
        'user_id': user_id,
        'username': current_user['username'],
        'role': 'leader',
        'joined_at': datetime.now(timezone.utc)
    })
    
    await log_event('guild', f'{current_user["username"]} founded guild: {req.name}', user_id)
    await check_and_award_achievement(user_id, 'guild_master')
    
    return {
        'success': True,
        'message': f'Gilde "{req.name}" gegründet!',
        'guild_id': guild_id
    }

@app.post("/api/game/guilds/{guild_id}/join")
async def join_guild(guild_id: str, current_user: dict = Depends(get_current_user)):
    """Join guild"""
    user_id = current_user['id']
    
    # Check if already in guild
    existing_membership = await db.guild_members.find_one({'user_id': user_id})
    if existing_membership:
        raise HTTPException(status_code=400, detail="Du bist bereits Mitglied einer Gilde")
    
    # Find guild
    guild = await db.guilds.find_one({'id': guild_id})
    if not guild:
        raise HTTPException(status_code=404, detail="Gilde nicht gefunden")
    
    # Add member
    await db.guild_members.insert_one({
        'id': str(uuid.uuid4()),
        'guild_id': guild_id,
        'user_id': user_id,
        'username': current_user['username'],
        'role': 'member',
        'joined_at': datetime.now(timezone.utc)
    })
    
    # Update count
    await db.guilds.update_one({'id': guild_id}, {'$inc': {'member_count': 1}})
    
    await log_event('guild', f'{current_user["username"]} joined guild: {guild["name"]}', user_id)
    
    return {'success': True, 'message': f'Du bist der Gilde "{guild["name"]}" beigetreten!'}

@app.get("/api/game/guilds/my-guild")
async def get_my_guild(current_user: dict = Depends(get_current_user)):
    """Get user's guild"""
    membership = await db.guild_members.find_one({'user_id': current_user['id']}, {'_id': 0})
    if not membership:
        return None
    
    guild = await db.guilds.find_one({'id': membership['guild_id']}, {'_id': 0})
    members = await db.guild_members.find({'guild_id': membership['guild_id']}, {'_id': 0}).to_list(100)
    
    return {
        'guild': serialize_doc(guild),
        'my_role': membership['role'],
        'members': serialize_doc(members)
    }

@app.post("/api/game/guilds/leave")
async def leave_guild(current_user: dict = Depends(get_current_user)):
    """Leave guild"""
    user_id = current_user['id']
    
    membership = await db.guild_members.find_one({'user_id': user_id})
    if not membership:
        raise HTTPException(status_code=400, detail="Du bist in keiner Gilde")
    
    if membership['role'] == 'leader':
        raise HTTPException(status_code=400, detail="Der Gildenführer kann nicht einfach gehen. Übergib die Führung oder löse die Gilde auf.")
    
    guild = await db.guilds.find_one({'id': membership['guild_id']})
    
    await db.guild_members.delete_one({'id': membership['id']})
    await db.guilds.update_one({'id': membership['guild_id']}, {'$inc': {'member_count': -1}})
    
    return {'success': True, 'message': f'Du hast die Gilde "{guild["name"]}" verlassen'}

# ============================================================================
# TAVERN GAMBLING
# ============================================================================

@app.post("/api/game/tavern/dice")
async def play_dice(req: DiceGameRequest, current_user: dict = Depends(get_current_user)):
    """Play dice game"""
    user_id = current_user['id']
    
    if current_user['gold'] < req.wager:
        raise HTTPException(status_code=400, detail="Nicht genug Gold für diesen Einsatz")
    
    # Deduct wager
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -req.wager}})
    
    # Roll 6 dice
    rolls = [random.randint(1, 6) for _ in range(6)]
    total = sum(rolls)
    
    # Win condition: total >= 21 (generous)
    won = total >= 21
    
    if won:
        winnings = req.wager * 2
        await db.users.update_one({'id': user_id}, {'$inc': {'gold': winnings}})
        
        return {
            'success': True,
            'won': True,
            'message': f'Gewonnen! {winnings} Gold',
            'rolls': rolls,
            'total': total,
            'winnings': winnings,
            'net_profit': winnings - req.wager
        }
    else:
        return {
            'success': True,
            'won': False,
            'message': f'Verloren! {req.wager} Gold verloren',
            'rolls': rolls,
            'total': total,
            'net_profit': -req.wager
        }

# ============================================================================
# EXPLORATION & HUNTING
# ============================================================================

@app.post("/api/game/travel")
async def travel_to_kingdom(req: TravelRequest, current_user: dict = Depends(get_current_user)):
    """Travel to another kingdom"""
    user_id = current_user['id']
    
    # Check if already traveling
    existing = await db.travel_sessions.find_one({'user_id': user_id, 'completed': False})
    if existing:
        raise HTTPException(status_code=400, detail="Du reist bereits")
    
    # Find kingdom
    kingdom = next((k for k in KINGDOMS if k['id'] == req.kingdom_id), None)
    if not kingdom:
        raise HTTPException(status_code=404, detail="Königreich nicht gefunden")
    
    if current_user['location'] == req.kingdom_id:
        raise HTTPException(status_code=400, detail="Du bist bereits hier")
    
    # Check level requirement
    if current_user['level'] < kingdom.get('min_level', 1):
        raise HTTPException(status_code=400, detail=f"Level {kingdom['min_level']} erforderlich für {kingdom['name']}")
    
    # Travel cost and duration
    travel_cost = kingdom.get('travel_cost', 50)
    travel_duration = 30  # minutes
    
    current_energy = await regenerate_energy(current_user)
    if current_energy < 15:
        raise HTTPException(status_code=400, detail="Nicht genug Energie zum Reisen (benötigt: 15)")
    
    if current_user['gold'] < travel_cost:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {travel_cost})")
    
    # Deduct costs
    await db.users.update_one(
        {'id': user_id},
        {
            '$inc': {'gold': -travel_cost, 'energy': -15},
            '$set': {'last_energy_regen': datetime.now(timezone.utc)}
        }
    )
    
    # Create travel session
    arrival_time = datetime.now(timezone.utc) + timedelta(minutes=travel_duration)
    await db.travel_sessions.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'from_kingdom': current_user['location'],
        'to_kingdom': req.kingdom_id,
        'destination_name': kingdom['name'],
        'start_time': datetime.now(timezone.utc),
        'arrival_time': arrival_time,
        'completed': False
    })
    
    return {
        'success': True,
        'message': f'Reise nach {kingdom["name"]} begonnen',
        'arrival_time': arrival_time.isoformat(),
        'duration_minutes': travel_duration
    }

@app.post("/api/game/travel/complete")
async def complete_travel(current_user: dict = Depends(get_current_user)):
    """Complete travel"""
    user_id = current_user['id']
    
    travel = await db.travel_sessions.find_one({'user_id': user_id, 'completed': False})
    if not travel:
        raise HTTPException(status_code=404, detail="Keine aktive Reise")
    
    arrival_time = travel['arrival_time']
    if isinstance(arrival_time, str):
        arrival_time = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
    
    if datetime.now(timezone.utc) < arrival_time:
        raise HTTPException(status_code=400, detail="Reise noch nicht abgeschlossen")
    
    # Update location
    await db.users.update_one({'id': user_id}, {'$set': {'location': travel['to_kingdom']}})
    await db.travel_sessions.update_one({'id': travel['id']}, {'$set': {'completed': True}})
    
    return {
        'success': True,
        'message': f'Ankunft in {travel["destination_name"]}!'
    }

@app.get("/api/game/hunting/creatures")
async def get_creatures(current_user: dict = Depends(get_current_user)):
    """Get huntable creatures"""
    creatures = [c for c in MASTER_CREATURES if current_user['level'] >= c['min_level']]
    return creatures

@app.post("/api/game/hunting/hunt")
async def hunt_creature(req: HuntRequest, current_user: dict = Depends(get_current_user)):
    """Hunt creature"""
    user_id = current_user['id']
    
    creature = next((c for c in MASTER_CREATURES if c['id'] == req.creature_id), None)
    if not creature:
        raise HTTPException(status_code=404, detail="Kreatur nicht gefunden")
    
    if current_user['level'] < creature['min_level']:
        raise HTTPException(status_code=400, detail=f"Level {creature['min_level']} erforderlich")
    
    current_energy = await regenerate_energy(current_user)
    if current_energy < creature['energy_cost']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Energie (benötigt: {creature['energy_cost']})")
    
    # Deduct energy
    await db.users.update_one(
        {'id': user_id},
        {'$inc': {'energy': -creature['energy_cost']}, '$set': {'last_energy_regen': datetime.now(timezone.utc)}}
    )
    
    # Combat calculation
    player_power = current_user['stats']['strength'] + current_user['stats']['dexterity'] + random.randint(0, 30)
    creature_power = creature['power'] + random.randint(0, 20)
    
    won = player_power > creature_power
    
    if won:
        gold_reward = random.randint(*creature['rewards']['gold'])
        xp_reward = creature['rewards']['xp']
        
        await db.users.update_one({'id': user_id}, {'$inc': {'gold': gold_reward, 'xp': xp_reward}})
        
        # Item chance
        item_gained = None
        if 'item_chance' in creature['rewards']:
            item_id, chance = creature['rewards']['item_chance']
            if random.randint(1, 100) <= chance:
                existing = await db.inventories.find_one({'user_id': user_id, 'item_id': item_id})
                if existing:
                    await db.inventories.update_one({'user_id': user_id, 'item_id': item_id}, {'$inc': {'quantity': 1}})
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
        
        await log_event('combat', f'{current_user["username"]} defeated a {creature["name"]}!', user_id)
        
        message = f'Sieg! +{gold_reward} Gold, +{xp_reward} XP'
        if item_gained:
            message += f', +1 {item_gained}'
        
        return {
            'success': True,
            'won': True,
            'message': message,
            'rewards': {'gold': gold_reward, 'xp': xp_reward, 'item': item_gained}
        }
    else:
        # Lost - take damage
        damage = random.randint(20, 40)
        current_hp = await regenerate_hp(current_user)
        new_hp = max(0, current_hp - damage)
        
        await db.users.update_one({'id': user_id}, {'$set': {'hp': new_hp, 'last_hp_regen': datetime.now(timezone.utc)}})
        
        # Hospital if needed
        if new_hp == 0:
            await db.hospital_sessions.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'reason': 'hunting_injury',
                'admit_time': datetime.now(timezone.utc),
                'release_time': datetime.now(timezone.utc) + timedelta(minutes=45),
                'released': False
            })
        
        return {
            'success': True,
            'won': False,
            'message': f'Niederlage! -{damage} HP',
            'damage': damage,
            'hospitalized': new_hp == 0
        }

# ============================================================================
# BOUNTIES SYSTEM
# ============================================================================

@app.get("/api/game/bounties")
async def get_bounties(limit: int = 30):
    """Get active bounties"""
    bounties = await db.bounties.find({'active': True}, {'_id': 0}).sort('reward', -1).limit(limit).to_list(limit)
    return serialize_doc(bounties)

@app.post("/api/game/bounties/create")
async def create_bounty(req: BountyCreateRequest, current_user: dict = Depends(get_current_user)):
    """Place bounty on player"""
    user_id = current_user['id']
    
    # Find target
    target = await db.users.find_one({'username': req.target_username})
    if not target:
        raise HTTPException(status_code=404, detail="Ziel nicht gefunden")
    
    if target['id'] == user_id:
        raise HTTPException(status_code=400, detail="Du kannst kein Kopfgeld auf dich selbst aussetzen")
    
    # Check if bounty already exists
    existing = await db.bounties.find_one({'target_id': target['id'], 'active': True})
    if existing:
        raise HTTPException(status_code=400, detail="Auf diesen Spieler ist bereits ein Kopfgeld ausgesetzt")
    
    # Check gold
    if current_user['gold'] < req.reward_amount:
        raise HTTPException(status_code=400, detail="Nicht genug Gold")
    
    # Deduct gold
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -req.reward_amount}})
    
    # Create bounty
    bounty = {
        'id': str(uuid.uuid4()),
        'target_id': target['id'],
        'target_name': target['username'],
        'target_level': target['level'],
        'placed_by_id': user_id,
        'placed_by_name': current_user['username'],
        'reward': req.reward_amount,
        'active': True,
        'created_at': datetime.now(timezone.utc)
    }
    await db.bounties.insert_one(bounty)
    
    await log_event('bounty', f'Kopfgeld auf {target["username"]}: {req.reward_amount} Gold!', user_id)
    
    return {
        'success': True,
        'message': f'Kopfgeld von {req.reward_amount} Gold auf {target["username"]} ausgesetzt'
    }

# ============================================================================
# PROPERTIES SYSTEM
# ============================================================================

@app.get("/api/game/properties/available")
async def get_available_properties(current_user: dict = Depends(get_current_user)):
    """Get properties available for purchase"""
    # Get owned properties
    owned = await db.user_properties.find({'user_id': current_user['id']}, {'property_id': 1}).to_list(100)
    owned_ids = [p['property_id'] for p in owned]
    
    # Filter available
    available = [p for p in MASTER_PROPERTIES if p['id'] not in owned_ids and current_user['level'] >= p['min_level']]
    
    return {'properties': available}

@app.post("/api/game/properties/buy")
async def buy_property(req: PropertyBuyRequest, current_user: dict = Depends(get_current_user)):
    """Buy property"""
    user_id = current_user['id']
    
    # Check if already owned
    existing = await db.user_properties.find_one({'user_id': user_id, 'property_id': req.property_id})
    if existing:
        raise HTTPException(status_code=400, detail="Du besitzt diese Immobilie bereits")
    
    # Find property
    prop = next((p for p in MASTER_PROPERTIES if p['id'] == req.property_id), None)
    if not prop:
        raise HTTPException(status_code=404, detail="Immobilie nicht gefunden")
    
    if current_user['level'] < prop['min_level']:
        raise HTTPException(status_code=400, detail=f"Level {prop['min_level']} erforderlich")
    
    if current_user['gold'] < prop['price']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {prop['price']})")
    
    # Purchase
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -prop['price']}})
    
    await db.user_properties.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'property_id': req.property_id,
        'property_name': prop['name'],
        'purchased_at': datetime.now(timezone.utc),
        'last_collected': datetime.now(timezone.utc)
    })
    
    # Check achievement
    property_count = await db.user_properties.count_documents({'user_id': user_id})
    if property_count == 1:
        await check_and_award_achievement(user_id, 'property_owner')
    
    await log_event('market', f'{current_user["username"]} purchased property: {prop["name"]}', user_id)
    
    return {
        'success': True,
        'message': f'{prop["name"]} gekauft für {prop["price"]} Gold!'
    }

@app.get("/api/game/properties/my-properties")
async def get_my_properties(current_user: dict = Depends(get_current_user)):
    """Get owned properties"""
    properties = await db.user_properties.find({'user_id': current_user['id']}, {'_id': 0}).to_list(100)
    
    # Enrich with details
    enriched = []
    for prop in properties:
        prop_data = next((p for p in MASTER_PROPERTIES if p['id'] == prop['property_id']), None)
        if prop_data:
            # Calculate available income
            last_collected = prop.get('last_collected')
            if isinstance(last_collected, str):
                last_collected = datetime.fromisoformat(last_collected.replace('Z', '+00:00'))
            
            days_passed = (datetime.now(timezone.utc) - last_collected).total_seconds() / 86400
            available_income = int(days_passed * prop_data['daily_income'])
            
            enriched.append({
                **serialize_doc(prop),
                'property_details': prop_data,
                'available_income': available_income,
                'income_ready': available_income > 0,
                # Add all property data fields
                'name': prop_data['name'],
                'description': prop_data['description'],
                'income_per_day': prop_data['daily_income']
            })
    
    return {'properties': enriched}

@app.post("/api/game/properties/collect/{property_id}")
async def collect_property_income(property_id: str, current_user: dict = Depends(get_current_user)):
    """Collect income from property"""
    user_id = current_user['id']
    
    user_prop = await db.user_properties.find_one({'id': property_id, 'user_id': user_id})
    if not user_prop:
        raise HTTPException(status_code=404, detail="Immobilie nicht gefunden")
    
    prop_data = next((p for p in MASTER_PROPERTIES if p['id'] == user_prop['property_id']), None)
    if not prop_data:
        raise HTTPException(status_code=404, detail="Immobilien-Daten nicht gefunden")
    
    last_collected = user_prop.get('last_collected')
    if isinstance(last_collected, str):
        last_collected = datetime.fromisoformat(last_collected.replace('Z', '+00:00'))
    
    days_passed = (datetime.now(timezone.utc) - last_collected).total_seconds() / 86400
    income = int(days_passed * prop_data['daily_income'])
    
    if income < 1:
        raise HTTPException(status_code=400, detail="Noch kein Einkommen verfügbar")
    
    # Collect
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': income}})
    await db.user_properties.update_one(
        {'id': property_id},
        {'$set': {'last_collected': datetime.now(timezone.utc)}}
    )
    
    return {
        'success': True,
        'message': f'{income} Gold von {prop_data["name"]} eingesammelt',
        'income': income
    }

# ============================================================================
# MESSAGES SYSTEM
# ============================================================================

@app.get("/api/game/messages")
async def get_messages(current_user: dict = Depends(get_current_user), limit: int = 50):
    """Get inbox"""
    messages = await db.messages.find(
        {'recipient_id': current_user['id']},
        {'_id': 0}
    ).sort('sent_at', -1).limit(limit).to_list(limit)
    
    return serialize_doc(messages)

@app.post("/api/game/messages/send")
async def send_message(req: MessageSendRequest, current_user: dict = Depends(get_current_user)):
    """Send message"""
    user_id = current_user['id']
    
    # Find recipient
    recipient = await db.users.find_one({'username': req.recipient_username})
    if not recipient:
        raise HTTPException(status_code=404, detail="Empfänger nicht gefunden")
    
    if recipient['id'] == user_id:
        raise HTTPException(status_code=400, detail="Du kannst dir nicht selbst schreiben")
    
    # Create message
    message = {
        'id': str(uuid.uuid4()),
        'sender_id': user_id,
        'sender_name': current_user['username'],
        'recipient_id': recipient['id'],
        'recipient_name': recipient['username'],
        'subject': req.subject,
        'body': req.body,
        'read': False,
        'sent_at': datetime.now(timezone.utc)
    }
    await db.messages.insert_one(message)
    
    return {'success': True, 'message': f'Nachricht an {req.recipient_username} gesendet'}

@app.post("/api/game/messages/{message_id}/read")
async def mark_message_read(message_id: str, current_user: dict = Depends(get_current_user)):
    """Mark message as read"""
    message = await db.messages.find_one({'id': message_id, 'recipient_id': current_user['id']})
    if not message:
        raise HTTPException(status_code=404, detail="Nachricht nicht gefunden")
    
    await db.messages.update_one({'id': message_id}, {'$set': {'read': True}})
    
    return {'success': True}

# ============================================================================
# HOSPITAL & DUNGEON STATUS
# ============================================================================

@app.get("/api/game/hospital")
async def get_hospital_patients(limit: int = 30):
    """Get hospitalized players"""
    sessions = await db.hospital_sessions.find(
        {'released': False},
        {'_id': 0}
    ).sort('admit_time', -1).limit(limit).to_list(limit)
    
    return serialize_doc(sessions)

@app.get("/api/game/dungeon")
async def get_dungeon_inmates(current_user: dict = Depends(get_current_user), limit: int = 30):
    """Get jailed players (only showing current user's session if exists, plus public list)"""
    # Get current user's session
    user_session = await db.dungeon_sessions.find_one(
        {'user_id': current_user['id'], 'released': False},
        {'_id': 0}
    )
    
    # Get other inmates (public list)
    other_sessions = await db.dungeon_sessions.find(
        {'released': False, 'user_id': {'$ne': current_user['id']}},
        {'_id': 0}
    ).sort('arrest_time', -1).limit(limit).to_list(limit)
    
    return {
        'user_session': serialize_doc(user_session) if user_session else None,
        'other_inmates': serialize_doc(other_sessions)
    }

# ============================================================================
# ACHIEVEMENTS
# ============================================================================

@app.get("/api/game/achievements")
async def get_achievements(current_user: dict = Depends(get_current_user)):
    """Get achievements"""
    # Get earned
    earned = await db.user_achievements.find({'user_id': current_user['id']}, {'achievement_id': 1}).to_list(100)
    earned_ids = [a['achievement_id'] for a in earned]
    
    # All achievements
    all_achievements = []
    for ach in MASTER_ACHIEVEMENTS:
        all_achievements.append({
            **ach,
            'earned': ach['id'] in earned_ids
        })
    
    return all_achievements

# ============================================================================
# LANDING PAGE ENDPOINTS (PRESERVE EXISTING)
# ============================================================================

async def get_real_leaderboard(limit: int = 10) -> list:
    """Get real leaderboard from users"""
    users = await db.users.find(
        {},
        {"_id": 0, "password": 0, "email": 0}
    ).sort([("level", -1), ("xp", -1)]).limit(limit).to_list(limit)
    
    result = []
    for rank, u in enumerate(users, start=1):
        created = u.get("created_at")
        if isinstance(created, datetime):
            created_dt = created
            # Ensure timezone awareness for datetime objects
            if created_dt.tzinfo is None:
                created_dt = created_dt.replace(tzinfo=timezone.utc)
        else:
            created_dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
        
        days_in_realm = (datetime.now(timezone.utc) - created_dt).days
        
        path_key = u.get("path_choice", "knight")
        result.append({
            "rank": rank,
            "username": u.get("username", "Unknown"),
            "title": u.get("title", "Adventurer"),
            "age": days_in_realm,
            "level": u.get("level", 1),
            "xp": u.get("xp", 0),
            "path_choice": path_key,
            "path_label": PATH_LABELS.get(path_key, "Knight"),
            "path_icon": PATH_ICONS.get(path_key, "⚔️"),
            "improvement": round(u.get("xp", 0) / max(days_in_realm, 1), 2) if days_in_realm > 0 else 0.0,
        })
    return result

async def get_real_online_stats() -> dict:
    """Get real online stats"""
    now = datetime.now(timezone.utc)
    time_15m = now - timedelta(minutes=15)
    time_1h = now - timedelta(hours=1)
    time_24h = now - timedelta(hours=24)
    
    now_count = await db.users.count_documents({"last_seen": {"$gte": time_15m}})
    hour_count = await db.users.count_documents({"last_seen": {"$gte": time_1h}})
    day_count = await db.users.count_documents({"last_seen": {"$gte": time_24h}})
    total_count = await db.users.count_documents({})
    
    return {
        "now": now_count,
        "last_hour": hour_count,
        "last_24h": day_count,
        "total": total_count,
    }

async def get_real_ticker() -> list:
    """Get real event ticker"""
    events = await db.events.find({}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
    return serialize_doc(events)

@app.get("/api/landing")
async def get_landing():
    """Landing page data"""
    leaderboard = await get_real_leaderboard(10)
    ticker = await get_real_ticker()
    online = await get_real_online_stats()
    features = await db.features.find({}, {"_id": 0}).sort("index", 1).to_list(100)
    reviews = await db.reviews.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    
    # Format reviews
    enriched_reviews = []
    for review in reviews:
        created = review.get('created_at')
        if isinstance(created, datetime):
            created_dt = created
        else:
            created_dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
        
        days_ago = (datetime.now(timezone.utc) - created_dt).days
        if days_ago == 0:
            date_str = "Heute"
        elif days_ago == 1:
            date_str = "Gestern"
        elif days_ago < 30:
            date_str = f"vor {days_ago} Tagen"
        else:
            date_str = created_dt.strftime("%-d. %B %Y")
        
        enriched_reviews.append({
            'id': review['id'],
            'author': review['author'],
            'rating': review['rating'],
            'text': review['text'],
            'verified': True,
            'date': date_str
        })
    
    news = await db.news.find({}, {"_id": 0}).to_list(100)
    paths = await db.paths.find({}, {"_id": 0}).to_list(10)
    kingdoms = await db.kingdoms.find({}, {"_id": 0}).to_list(20)
    
    return {
        "ticker": ticker,
        "leaderboard": leaderboard,
        "online": online,
        "features": serialize_doc(features),
        "reviews": enriched_reviews,
        "news": serialize_doc(news),
        "paths": serialize_doc(paths),
        "kingdoms": serialize_doc(kingdoms),
    }

@app.get("/api/reviews")
async def get_reviews_only():
    """Just reviews for landing"""
    reviews = await db.reviews.find({}, {'_id': 0}).sort('created_at', -1).to_list(100)
    
    enriched = []
    for review in reviews:
        created = review.get('created_at')
        if isinstance(created, datetime):
            created_dt = created
        else:
            created_dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
        
        days_ago = (datetime.now(timezone.utc) - created_dt).days
        if days_ago == 0:
            date_str = "Heute"
        elif days_ago == 1:
            date_str = "Gestern"
        elif days_ago < 30:
            date_str = f"vor {days_ago} Tagen"
        else:
            date_str = created_dt.strftime("%-d. %B %Y")
        
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
    """Create review"""
    existing = await db.reviews.find_one({'user_id': current_user['id']})
    if existing:
        raise HTTPException(status_code=400, detail="Du hast bereits eine Bewertung abgegeben")
    
    review = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'author': current_user['username'],
        'rating': req.rating,
        'text': req.text,
        'verified': True,
        'created_at': datetime.now(timezone.utc)
    }
    await db.reviews.insert_one(review)
    
    return {'success': True, 'message': 'Vielen Dank für deine Bewertung!'}

# ============================================================================
# CORS SETUP
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
