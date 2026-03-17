from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import random
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ─────────────────────────────────────────────
# DB + App
# ─────────────────────────────────────────────
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET    = os.environ.get('JWT_SECRET', 'aethoria-realm-secret-key-2026')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_DAYS = 7

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    path_choice: Optional[str] = "knight"

class UserLogin(BaseModel):
    email: str
    password: str

class ReviewCreate(BaseModel):
    text: str
    rating: int   # 1-5

class NewsCreate(BaseModel):
    title: str
    password: str  # simple admin passphrase

# ─────────────────────────────────────────────
# Path Starters
# ─────────────────────────────────────────────
PATH_STARTERS: Dict[str, Dict] = {
    "knight": {"title": "Novice Knight",  "strength": 12, "dexterity": 6,  "speed": 8,  "defense": 10, "gold": 150, "xp": 0},
    "shadow": {"title": "Fledgling Rogue","strength": 7,  "dexterity": 14, "speed": 12, "defense": 5,  "gold": 200, "xp": 0},
    "noble":  {"title": "Minor Noble",    "strength": 5,  "dexterity": 8,  "speed": 6,  "defense": 7,  "gold": 500, "xp": 0},
}
PATH_LABELS = {"knight": "The Knight", "shadow": "The Shadow", "noble": "The Noble"}
PATH_ICONS  = {"knight": "⚔️", "shadow": "🗡️", "noble": "👑"}

ADMIN_PASS = os.environ.get("ADMIN_PASS", "aethoria-admin-2026")

# ─────────────────────────────────────────────
# Static Seed Data  (features, paths, kingdoms only)
# ─────────────────────────────────────────────
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
    {"title": "No Cost", "desc": "The Realm has no banners of commerce — free forever, the greatest RPG undying!", "icon": "🆓"},
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
    {"name": "Aethoria Prime", "desc": "The capital of the Realm. Trade, power, and intrigue converge.", "image": "https://images.unsplash.com/photo-1533154683836-84ea7a0bc310?w=400&q=50", "type": "Capital", "danger": "Medium"},
    {"name": "Ironhold",       "desc": "A fortress city of steel and fire. Home to the greatest warriors.", "image": "https://images.unsplash.com/photo-1621947081720-86970823b77a?w=400&q=50", "type": "Military", "danger": "High"},
    {"name": "Shadowfen",      "desc": "A city of fog and secrets, where rogues and thieves hold court.", "image": "https://images.unsplash.com/photo-1518709766631-a6a7f45921c3?w=400&q=50", "type": "Underworld", "danger": "Very High"},
    {"name": "Goldenveil",     "desc": "The Realm's most prosperous trading city. Every merchant dreams of it.", "image": "https://images.unsplash.com/photo-1501183638710-841dd1904471?w=400&q=50", "type": "Commerce", "danger": "Low"},
    {"name": "Stonecrest",     "desc": "Ancient mountains hiding powerful arcane secrets in their caves.", "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=50", "type": "Arcane", "danger": "High"},
    {"name": "Crystalmere",    "desc": "A lakeside city of extraordinary beauty and political scheming.", "image": "https://images.unsplash.com/photo-1499678329028-101435549a4e?w=400&q=50", "type": "Noble", "danger": "Medium"},
    {"name": "Embervast",      "desc": "The volcanic borderlands, rich in dragon-forged materials.", "image": "https://images.unsplash.com/photo-1527482797697-8795b05a13fe?w=400&q=50", "type": "Wilds", "danger": "Extreme"},
    {"name": "Tidehaven",      "desc": "A port city where smugglers and merchants clash over sea routes.", "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=50", "type": "Maritime", "danger": "High"},
    {"name": "Duskwood",       "desc": "An ancient forest kingdom where shapeshifters and druids dwell.", "image": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=400&q=50", "type": "Forest", "danger": "Medium"},
    {"name": "Frostholm",      "desc": "The frozen north: hard people, rare pelts, and glacier-locked tombs.", "image": "https://images.unsplash.com/photo-1491555103944-7c647fd857e6?w=400&q=50", "type": "Frozen", "danger": "Very High"},
    {"name": "Sunkeep",        "desc": "A desert kingdom where ruins of the First Empire still stand.", "image": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=400&q=50", "type": "Desert", "danger": "High"},
]

# ─────────────────────────────────────────────
# NEWS with real computed dates (relative to now)
# ─────────────────────────────────────────────
def make_initial_news():
    now = datetime.now(timezone.utc)
    entries = [
        {"title": "Realm of Aethoria opens its gates — welcome, adventurers!",         "days_ago": 0},
        {"title": "Character Paths launched: Choose Knight, Shadow, or Noble",           "days_ago": 1},
        {"title": "11 Kingdoms now available for exploration — travel system active",    "days_ago": 3},
        {"title": "Hall of Legends now displays real registered adventurers",            "days_ago": 5},
        {"title": "Review system launched — share your experience with the Realm",      "days_ago": 7},
        {"title": "Online counter now tracks real active adventurers in real-time",      "days_ago": 10},
        {"title": "Character Dashboard released — view your stats and path anytime",     "days_ago": 14},
        {"title": "Realm Event Ticker now shows real activity from real adventurers",    "days_ago": 18},
    ]
    result = []
    for e in entries:
        ts = now - timedelta(days=e["days_ago"])
        result.append({
            "id": str(uuid.uuid4()),
            "title": e["title"],
            "date": ts.strftime("%-d. %B %Y"),   # e.g. "17. March 2026"
            "date_iso": ts.isoformat(),
            "url": "#",
        })
    return result

# ─────────────────────────────────────────────
# JWT Helpers
# ─────────────────────────────────────────────
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
        raise HTTPException(status_code=401, detail="Session expired — please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token — please log in again")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    payload = decode_access_token(credentials.credentials)
    user = await db.users.find_one({"id": payload["sub"]})
    if not user:
        raise HTTPException(status_code=401, detail="Adventurer not found in the Realm")
    return user

async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Returns user if authenticated, None otherwise."""
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        return await db.users.find_one({"id": payload["sub"]})
    except Exception:
        return None

# ─────────────────────────────────────────────
# Serialization
# ─────────────────────────────────────────────
def serialize_doc(doc):
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

def user_to_profile(user: dict) -> dict:
    created = user.get("created_at", datetime.now(timezone.utc).isoformat())
    if isinstance(created, datetime):
        created = created.isoformat()
    try:
        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        days_in_realm = (datetime.now(timezone.utc) - created_dt).days
    except Exception:
        days_in_realm = 0
    path_key = user.get("path_choice", "knight")
    return {
        "id": user.get("id"),
        "username": user.get("username"),
        "email": user.get("email"),
        "level": user.get("level", 1),
        "title": user.get("title", "Novice Adventurer"),
        "path_choice": path_key,
        "path_label": PATH_LABELS.get(path_key, "Unknown"),
        "strength": user.get("strength", 5),
        "dexterity": user.get("dexterity", 5),
        "speed": user.get("speed", 5),
        "defense": user.get("defense", 5),
        "gold": user.get("gold", 100),
        "xp": user.get("xp", 0),
        "days_in_realm": days_in_realm,
        "created_at": created,
    }

def format_created_at(iso_str: str) -> str:
    """Return human-readable date like '17. March 2026'"""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%-d. %B %Y")
    except Exception:
        return iso_str

# ─────────────────────────────────────────────
# Event Logging Helper
# ─────────────────────────────────────────────
EVENT_TEMPLATES = {
    "register": [
        "{username} joined the Realm as {path_label}",
        "A new adventurer, {username}, has entered Aethoria as {path_label}",
        "{username} forged their legend — {path_label} path chosen",
    ],
    "login": [
        "{username} returned to the Realm",
        "The gate opened for {username}",
        "{username} entered Aethoria once more",
    ],
}
EVENT_TYPES = {
    "register": "quest",
    "login": "combat",
}

async def log_event(event_type: str, username: str, path_label: str = ""):
    templates = EVENT_TEMPLATES.get(event_type, ["{username} did something"])
    template = random.choice(templates)
    text = template.format(username=username, path_label=path_label)
    doc = {
        "id": str(uuid.uuid4()),
        "event": text,
        "type": EVENT_TYPES.get(event_type, "default"),
        "username": username,
        "time": "moments ago",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.events.insert_one(doc)
    # Keep only last 100 events
    count = await db.events.count_documents({})
    if count > 100:
        oldest = await db.events.find({}, {"_id": 1}).sort("created_at", 1).limit(count - 100).to_list(None)
        if oldest:
            ids = [d["_id"] for d in oldest]
            await db.events.delete_many({"_id": {"$in": ids}})

# ─────────────────────────────────────────────
# Seed DB — only static data (no fake users/leaderboard/reviews)
# ─────────────────────────────────────────────
async def seed_database():
    if await db.features.count_documents({}) == 0:
        await db.features.insert_many([{"id": str(uuid.uuid4()), "index": i, **f} for i, f in enumerate(FEATURES)])

    if await db.paths.count_documents({}) == 0:
        await db.paths.insert_many([{"id": str(uuid.uuid4()), "key": k, **v} for k, v in PATHS.items()])

    if await db.kingdoms.count_documents({}) == 0:
        await db.kingdoms.insert_many([{"id": str(uuid.uuid4()), **k} for k in KINGDOMS])

    # News: always wipe and re-seed with correct real dates
    await db.news.delete_many({})
    await db.news.insert_many(make_initial_news())

    logger.info("Database seeded successfully (real data only)")

@app.on_event("startup")
async def startup_event():
    await seed_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# ─────────────────────────────────────────────
# Real Leaderboard (from db.users)
# ─────────────────────────────────────────────
async def get_real_leaderboard(limit: int = 10) -> list:
    users = await db.users.find(
        {},
        {"_id": 0, "password": 0, "email": 0}
    ).sort([("level", -1), ("xp", -1)]).limit(limit).to_list(limit)

    result = []
    for rank, u in enumerate(users, start=1):
        created = u.get("created_at", datetime.now(timezone.utc).isoformat())
        if isinstance(created, datetime):
            created = created.isoformat()
        try:
            created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            days_in_realm = (datetime.now(timezone.utc) - created_dt).days
        except Exception:
            days_in_realm = 0

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
            "created_at": format_created_at(created),
        })
    return result

# ─────────────────────────────────────────────
# Real Online Counter (from last_seen)
# ─────────────────────────────────────────────
async def get_real_online_stats() -> dict:
    now = datetime.now(timezone.utc)
    iso_15m = (now - timedelta(minutes=15)).isoformat()
    iso_1h  = (now - timedelta(hours=1)).isoformat()
    iso_24h = (now - timedelta(hours=24)).isoformat()

    now_count    = await db.users.count_documents({"last_seen": {"$gte": iso_15m}})
    hour_count   = await db.users.count_documents({"last_seen": {"$gte": iso_1h}})
    day_count    = await db.users.count_documents({"last_seen": {"$gte": iso_24h}})
    total_count  = await db.users.count_documents({})

    return {
        "now": now_count,
        "last_hour": hour_count,
        "last_24h": day_count,
        "total": total_count,
    }

# ─────────────────────────────────────────────
# Real Ticker (from db.events)
# ─────────────────────────────────────────────
async def get_real_ticker() -> list:
    events = await db.events.find({}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
    return serialize_doc(events)

# ─────────────────────────────────────────────
# Landing Endpoint (all real data)
# ─────────────────────────────────────────────
@api_router.get("/landing")
async def get_landing():
    leaderboard = await get_real_leaderboard(10)
    ticker      = await get_real_ticker()
    online      = await get_real_online_stats()
    features    = await db.features.find({}, {"_id": 0}).sort("index", 1).to_list(100)
    reviews     = await db.reviews.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    news        = await db.news.find({}, {"_id": 0}).sort("date_iso", -1).to_list(20)
    paths       = await db.paths.find({}, {"_id": 0}).to_list(10)
    kingdoms    = await db.kingdoms.find({}, {"_id": 0}).to_list(20)

    return {
        "ticker":      serialize_doc(ticker),
        "features":    serialize_doc(features),
        "leaderboard": leaderboard,
        "reviews":     serialize_doc(reviews),
        "news":        serialize_doc(news),
        "paths":       serialize_doc(paths),
        "kingdoms":    serialize_doc(kingdoms),
        "online":      online,
    }

@api_router.get("/ticker")
async def get_ticker_endpoint():
    return await get_real_ticker()

@api_router.get("/leaderboard")
async def get_leaderboard_endpoint():
    return await get_real_leaderboard(10)

@api_router.get("/reviews")
async def get_reviews_endpoint():
    reviews = await db.reviews.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return serialize_doc(reviews)

@api_router.get("/news")
async def get_news_endpoint():
    news = await db.news.find({}, {"_id": 0}).sort("date_iso", -1).to_list(20)
    return serialize_doc(news)

@api_router.get("/features")
async def get_features_endpoint():
    features = await db.features.find({}, {"_id": 0}).sort("index", 1).to_list(100)
    return serialize_doc(features)

@api_router.get("/paths")
async def get_paths_endpoint():
    return serialize_doc(await db.paths.find({}, {"_id": 0}).to_list(10))

@api_router.get("/kingdoms")
async def get_kingdoms_endpoint():
    return serialize_doc(await db.kingdoms.find({}, {"_id": 0}).to_list(20))

@api_router.get("/stats/online")
async def get_online_stats_endpoint():
    return await get_real_online_stats()

# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────
@api_router.post("/auth/register")
async def register(user: UserRegister):
    if not user.username or not user.email or not user.password:
        raise HTTPException(status_code=400, detail="All fields are required")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Passphrase must be at least 6 characters")

    path_choice = (user.path_choice or "knight").lower()
    if path_choice not in PATH_STARTERS:
        path_choice = "knight"

    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="An adventurer with this email already exists in the Realm")
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="This adventurer name is already taken in the Realm")

    hashed   = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    starter  = PATH_STARTERS[path_choice].copy()
    now_iso  = datetime.now(timezone.utc).isoformat()

    user_doc = {
        "id": str(uuid.uuid4()),
        "username": user.username,
        "email": user.email,
        "password": hashed,
        "created_at": now_iso,
        "last_seen": now_iso,
        "level": 1,
        "path_choice": path_choice,
        **starter,
    }
    await db.users.insert_one(user_doc)

    # Log real event
    await log_event("register", user.username, PATH_LABELS.get(path_choice, "Knight"))

    token   = create_access_token(user_doc["id"], user.username)
    profile = user_to_profile(user_doc)
    return {
        "success": True,
        "message": f"Welcome to the Realm, {user.username}! Your legend begins now.",
        "token": token,
        "user": profile,
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="All fields are required")

    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=401, detail="No adventurer found with those credentials")
    if not bcrypt.checkpw(credentials.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Incorrect passphrase — the dungeon guards grow suspicious")

    # Update last_seen
    now_iso = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"id": user["id"]}, {"$set": {"last_seen": now_iso}})

    # Log real event (only log occasionally to avoid flooding ticker)
    existing = await db.events.count_documents({"username": user["username"], "type": "combat"})
    if existing == 0 or random.random() < 0.3:
        await log_event("login", user["username"])

    token   = create_access_token(user["id"], user["username"])
    profile = user_to_profile({**user, "last_seen": now_iso})
    return {
        "success": True,
        "message": f"Welcome back, {user['username']}! The Realm awaits your return.",
        "token": token,
        "user": profile,
    }

@api_router.post("/auth/logout")
async def logout():
    return {"success": True, "message": "You have left the Realm safely. Until next time."}

@api_router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    # Update last_seen on every /me call (keeps "online now" accurate)
    now_iso = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"id": current_user["id"]}, {"$set": {"last_seen": now_iso}})
    return {"success": True, "user": user_to_profile({**current_user, "last_seen": now_iso})}

# ─────────────────────────────────────────────
# Reviews — real user submissions
# ─────────────────────────────────────────────
@api_router.post("/reviews")
async def create_review(review: ReviewCreate, current_user: dict = Depends(get_current_user)):
    if not review.text or len(review.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Review must be at least 10 characters")
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    # Prevent duplicate reviews from same user
    existing = await db.reviews.find_one({"user_id": current_user["id"]})
    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted a review for the Realm")

    now = datetime.now(timezone.utc)
    doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "author": current_user["username"],
        "path_label": PATH_LABELS.get(current_user.get("path_choice", "knight"), "Knight"),
        "rating": review.rating,
        "text": review.text.strip(),
        "date": now.strftime("%-d. %B %Y"),
        "created_at": now.isoformat(),
    }
    await db.reviews.insert_one(doc)
    return {"success": True, "message": "Your testimonial has been inscribed in the Realm's annals!", "review": serialize_doc(doc)}

@api_router.delete("/reviews/mine")
async def delete_my_review(current_user: dict = Depends(get_current_user)):
    result = await db.reviews.delete_one({"user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No review found for your adventurer")
    return {"success": True, "message": "Your review has been removed from the annals"}

# ─────────────────────────────────────────────
# News — admin can add real patch notes
# ─────────────────────────────────────────────
@api_router.post("/news")
async def create_news(item: NewsCreate):
    if item.password != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Invalid admin passphrase")
    if not item.title or len(item.title.strip()) < 5:
        raise HTTPException(status_code=400, detail="Title must be at least 5 characters")

    now = datetime.now(timezone.utc)
    doc = {
        "id": str(uuid.uuid4()),
        "title": item.title.strip(),
        "date": now.strftime("%-d. %B %Y"),
        "date_iso": now.isoformat(),
        "url": "#",
    }
    await db.news.insert_one(doc)
    return {"success": True, "message": "Chronicle added to the Royal Gazette!", "news": serialize_doc(doc)}

# ─────────────────────────────────────────────
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
