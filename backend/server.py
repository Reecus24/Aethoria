from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import random
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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

JWT_SECRET = os.environ.get('JWT_SECRET', 'aethoria-fallback-secret-key-2026')
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
    path_choice: Optional[str] = "knight"   # knight | shadow | noble

class UserLogin(BaseModel):
    email: str
    password: str

# ─────────────────────────────────────────────
# Path Starter Stats
# ─────────────────────────────────────────────

PATH_STARTERS: Dict[str, Dict] = {
    "knight": {
        "title": "Novice Knight",
        "strength": 12,
        "dexterity": 6,
        "speed": 8,
        "defense": 10,
        "gold": 150,
        "xp": 0,
    },
    "shadow": {
        "title": "Fledgling Rogue",
        "strength": 7,
        "dexterity": 14,
        "speed": 12,
        "defense": 5,
        "gold": 200,
        "xp": 0,
    },
    "noble": {
        "title": "Minor Noble",
        "strength": 5,
        "dexterity": 8,
        "speed": 6,
        "defense": 7,
        "gold": 500,
        "xp": 0,
    },
}

PATH_LABELS = {
    "knight": "The Knight",
    "shadow": "The Shadow",
    "noble":  "The Noble",
}

# ─────────────────────────────────────────────
# Seed Data
# ─────────────────────────────────────────────

TICKER_EVENTS = [
    {"event": "Sir Aldric was thrown into the dungeon: caught stealing from the market stalls", "type": "dungeon", "time": "moments ago"},
    {"event": "Lady Seraphina defeated Lord Malachar in brutal combat", "type": "combat", "time": "moments ago"},
    {"event": "The Shadow Theron pickpocketed a travelling merchant", "type": "crime", "time": "moments ago"},
    {"event": "Guild of the Iron Fist declared war on the Order of the Crimson Rose", "type": "guild", "time": "moments ago"},
    {"event": "Drakon the Bold completed the Quest of the Dragon's Eye", "type": "quest", "time": "moments ago"},
    {"event": "Morgana was arrested: caught brewing forbidden elixirs in the Alchemist Quarter", "type": "dungeon", "time": "moments ago"},
    {"event": "Knight Commander Voss challenged and hospitalised a rival noble", "type": "combat", "time": "moments ago"},
    {"event": "The Rogue Silas robbed the Royal Treasury vaults", "type": "crime", "time": "moments ago"},
    {"event": "Lady Elara left Baron Halvorn wounded at the crossroads", "type": "combat", "time": "moments ago"},
    {"event": "Brother Cedric escaped the dungeon using an ancient key", "type": "dungeon", "time": "moments ago"},
    {"event": "Merchant Lord Cassius cornered the iron ore market", "type": "market", "time": "moments ago"},
    {"event": "The Archer Lyra placed a bounty on the head of Darkblade", "type": "bounty", "time": "moments ago"},
    {"event": "Wizard Orenthal was caught casting forbidden curses", "type": "dungeon", "time": "moments ago"},
    {"event": "Shield-Maiden Brunhild won the Grand Tournament", "type": "quest", "time": "moments ago"},
    {"event": "The Order of Shadows completed an organized raid on the Merchant District", "type": "guild", "time": "moments ago"},
]

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

LEADERBOARD = [
    {"rank": 1, "username": "LordDrakon", "age": 1605, "level": 87, "improvement": 37.62, "title": "Dragon Slayer"},
    {"rank": 2, "username": "ShadowQueen", "age": 3542, "level": 74, "improvement": 37.36, "title": "Guild Mistress"},
    {"rank": 3, "username": "IronFistVoss", "age": 21, "level": 69, "improvement": 36.76, "title": "Warlord"},
    {"rank": 4, "username": "ArcaneSeraphina", "age": 1499, "level": 65, "improvement": 36.71, "title": "Archmage"},
    {"rank": 5, "username": "BladedRaven", "age": 775, "level": 63, "improvement": 36.12, "title": "Master Rogue"},
    {"rank": 6, "username": "NobleCassius", "age": 920, "level": 61, "improvement": 35.88, "title": "Merchant Lord"},
    {"rank": 7, "username": "ThunderSword", "age": 440, "level": 59, "improvement": 35.42, "title": "Champion"},
    {"rank": 8, "username": "MoonHuntress", "age": 310, "level": 57, "improvement": 34.95, "title": "Ranger Lord"},
    {"rank": 9, "username": "CrimsonBaron", "age": 1820, "level": 55, "improvement": 34.71, "title": "Noble Crusader"},
    {"rank": 10, "username": "DarkWarden", "age": 670, "level": 53, "improvement": 34.23, "title": "Shadow Walker"},
]

REVIEWS = [
    {"author": "DragonKnight88", "rating": 5, "text": "This realm is a masterpiece! The depth of gameplay is unmatched — from the guilds to the tournaments. Years of adventure await you!", "date": "December 13, 2025"},
    {"author": "ShadowRogue42", "rating": 5, "text": "Best text-based RPG I have ever played. The community is incredible, and the developers are always adding new content. Truly a living world!", "date": "December 09, 2025"},
    {"author": "NobleMerchant", "rating": 5, "text": "I have been playing Aethoria for 3 YEARS and I STILL love it! Definitely one of my favourite games of all time. The guild system alone is worth it!", "date": "December 07, 2025"},
    {"author": "ArcaneMage77", "rating": 4, "text": "Incredible game, mainly because the developers are actively online and the staff help you. The community makes it a 5/5 experience!", "date": "November 28, 2025"},
    {"author": "IronFistBrunhild", "rating": 5, "text": "This is a truly awesome game. I even invested real gold because I never do that! The depth and community are unparalleled. Cheers to 21 years of adventure!", "date": "November 15, 2025"},
    {"author": "SwiftArcher", "rating": 4, "text": "Great game — years of fun with a massive community. You can be in a thieves guild, a merchant house, or a knightly order. It is all there and more!", "date": "November 03, 2025"},
    {"author": "DuskCrawler", "rating": 5, "text": "Best game I have played in a very long time! The depth is astounding and the community is friendly and helpful. This game does not disappoint!", "date": "November 02, 2025"},
    {"author": "MoonlitPaladin", "rating": 4, "text": "There is no game like this one out there. Very hard to learn but once you master it, you will not play anything else. A true legend of the genre.", "date": "October 10, 2025"},
]

NEWS = [
    {"title": "Chronicles #424: Level 100 Honour Badges, 20 New Legendary Items, Combat Finale Bonus Adjusted", "date": "March 01, 2026", "url": "#"},
    {"title": "Chronicles #423: Practice Duel NPCs, Favourite Counters for Bazaars now live", "date": "February 22, 2026", "url": "#"},
    {"title": "Chronicles #422: Fallen Hero Badges, Advanced Quest Sorting, New Scenario, Bomb Counters", "date": "February 15, 2026", "url": "#"},
    {"title": "Chronicles #421: Balance adjustments and guild war improvements", "date": "February 17, 2026", "url": "#"},
    {"title": "Chronicles #420: Merchant House overhaul and new trade routes added", "date": "February 10, 2026", "url": "#"},
    {"title": "Chronicles #419: New dungeon mechanics and escape rune system", "date": "February 03, 2026", "url": "#"},
    {"title": "Chronicles #418: Seasonal tournament results and prize distribution", "date": "January 27, 2026", "url": "#"},
    {"title": "Updated Realm Rules: Arcane Scripting & Forbidden Knowledge Policy", "date": "January 25, 2026", "url": "#"},
]

PATHS = {
    "knight": {
        "title": "The Knight",
        "subtitle": "Master of Combat & Honour",
        "description": "Forge yourself into an unstoppable warrior. Train daily at the Royal Barracks, master every weapon from the humble shortsword to the legendary dragon-forged blade. Win glory in the tournament grounds, defend your guild in faction wars, and rise to become the most feared combatant in all of Aethoria.",
        "highlights": ["Melee Weapons: axes, swords, maces, legendary enchanted blades", "Train Strength, Speed, Defence and Dexterity at the Barracks", "Compete in Grand Tournaments and Faction Wars", "Earn the rank of Champion and be enshrined in the Hall of Legends"],
        "icon": "⚔️",
        "color": "#C0392B"
    },
    "shadow": {
        "title": "The Shadow",
        "subtitle": "Master of Darkness & Cunning",
        "description": "Slip through the cracks of society, unseen and unstoppable. Master the art of dark deeds, pickpocketing, burglary and guild-organised crimes. Craft arcane curses. Place bounties and collect them. The shadows of Aethoria hold more power than any sword — if you dare to wield them.",
        "highlights": ["50+ Dark Deeds with hundreds of unique outcomes", "Craft and deploy Arcane Curses against enemies", "Place and collect Hunter's Contracts (Bounties)", "Master the art of Guild-organised shadow operations"],
        "icon": "🗡️",
        "color": "#8E44AD"
    },
    "noble": {
        "title": "The Noble",
        "subtitle": "Master of Gold & Power",
        "description": "True power lies not in strength but in wealth and influence. Build your Merchant House, hire players as your retainers, dominate the trade markets, invest in the Royal Treasury, and acquire magnificent strongholds. The Realm's economy bends to the will of those with enough gold — and the cunning to use it.",
        "highlights": ["Found and manage one of 39 Merchant Houses", "Dominate the Merchant Exchange and drive prices", "Acquire Strongholds — from modest manors to grand castles", "Forge Noble Bonds and political alliances"],
        "icon": "👑",
        "color": "#D4AC0D"
    }
}

KINGDOMS = [
    {"name": "Aethoria Prime", "desc": "The capital of the Realm. Trade, power, and intrigue converge.", "image": "https://images.unsplash.com/photo-1533154683836-84ea7a0bc310?w=400&q=50", "type": "Capital", "danger": "Medium"},
    {"name": "Ironhold", "desc": "A fortress city of steel and fire. Home to the greatest warriors.", "image": "https://images.unsplash.com/photo-1621947081720-86970823b77a?w=400&q=50", "type": "Military", "danger": "High"},
    {"name": "Shadowfen", "desc": "A city of fog and secrets, where rogues and thieves hold court.", "image": "https://images.unsplash.com/photo-1518709766631-a6a7f45921c3?w=400&q=50", "type": "Underworld", "danger": "Very High"},
    {"name": "Goldenveil", "desc": "The Realm's most prosperous trading city. Every merchant dreams of it.", "image": "https://images.unsplash.com/photo-1501183638710-841dd1904471?w=400&q=50", "type": "Commerce", "danger": "Low"},
    {"name": "Stonecrest", "desc": "Ancient mountains hiding powerful arcane secrets in their caves.", "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=50", "type": "Arcane", "danger": "High"},
    {"name": "Crystalmere", "desc": "A lakeside city of extraordinary beauty and political scheming.", "image": "https://images.unsplash.com/photo-1499678329028-101435549a4e?w=400&q=50", "type": "Noble", "danger": "Medium"},
    {"name": "Embervast", "desc": "The volcanic borderlands, rich in dragon-forged materials.", "image": "https://images.unsplash.com/photo-1527482797697-8795b05a13fe?w=400&q=50", "type": "Wilds", "danger": "Extreme"},
    {"name": "Tidehaven", "desc": "A port city where smugglers and merchants clash over sea routes.", "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=50", "type": "Maritime", "danger": "High"},
    {"name": "Duskwood", "desc": "An ancient forest kingdom where shapeshifters and druids dwell.", "image": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=400&q=50", "type": "Forest", "danger": "Medium"},
    {"name": "Frostholm", "desc": "The frozen north: hard people, rare pelts, and glacier-locked tombs.", "image": "https://images.unsplash.com/photo-1491555103944-7c647fd857e6?w=400&q=50", "type": "Frozen", "danger": "Very High"},
    {"name": "Sunkeep", "desc": "A desert kingdom where ruins of the First Empire still stand.", "image": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=400&q=50", "type": "Desert", "danger": "High"},
]

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
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired — please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token — please log in again")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required — enter the gate first")
    payload = decode_access_token(credentials.credentials)
    user = await db.users.find_one({"id": payload["sub"]})
    if not user:
        raise HTTPException(status_code=401, detail="Adventurer not found in the Realm")
    return user


# ─────────────────────────────────────────────
# Seed DB on startup
# ─────────────────────────────────────────────

async def seed_database():
    count = await db.ticker_events.count_documents({})
    if count == 0:
        await db.ticker_events.insert_many([{"id": str(uuid.uuid4()), **e} for e in TICKER_EVENTS])

    count = await db.features.count_documents({})
    if count == 0:
        await db.features.insert_many([{"id": str(uuid.uuid4()), "index": i, **f} for i, f in enumerate(FEATURES)])

    count = await db.leaderboard.count_documents({})
    if count == 0:
        await db.leaderboard.insert_many([{"id": str(uuid.uuid4()), **e} for e in LEADERBOARD])

    count = await db.reviews.count_documents({})
    if count == 0:
        await db.reviews.insert_many([{"id": str(uuid.uuid4()), **r} for r in REVIEWS])

    count = await db.news.count_documents({})
    if count == 0:
        await db.news.insert_many([{"id": str(uuid.uuid4()), **n} for n in NEWS])

    count = await db.paths.count_documents({})
    if count == 0:
        await db.paths.insert_many([{"id": str(uuid.uuid4()), "key": k, **v} for k, v in PATHS.items()])

    count = await db.kingdoms.count_documents({})
    if count == 0:
        await db.kingdoms.insert_many([{"id": str(uuid.uuid4()), **k} for k in KINGDOMS])

    logger.info("Database seeded successfully")


@app.on_event("startup")
async def startup_event():
    await seed_database()


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


# ─────────────────────────────────────────────
# Serialization helper
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
            elif isinstance(v, dict):
                result[k] = serialize_doc(v)
            elif isinstance(v, list):
                result[k] = [serialize_doc(i) if isinstance(i, dict) else i for i in v]
            elif isinstance(v, datetime):
                result[k] = v.isoformat()
            else:
                result[k] = v
        return result
    return doc


def user_to_profile(user: dict) -> dict:
    """Return safe public profile (no password)."""
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


# ─────────────────────────────────────────────
# Landing / Aggregated Endpoint
# ─────────────────────────────────────────────

@api_router.get("/landing")
async def get_landing():
    ticker = await db.ticker_events.find({}, {"_id": 0}).to_list(100)
    features = await db.features.find({}, {"_id": 0}).sort("index", 1).to_list(100)
    leaderboard = await db.leaderboard.find({}, {"_id": 0}).sort("rank", 1).to_list(50)
    reviews = await db.reviews.find({}, {"_id": 0}).to_list(50)
    news = await db.news.find({}, {"_id": 0}).to_list(20)
    paths = await db.paths.find({}, {"_id": 0}).to_list(10)
    kingdoms = await db.kingdoms.find({}, {"_id": 0}).to_list(20)

    return {
        "ticker": serialize_doc(ticker),
        "features": serialize_doc(features),
        "leaderboard": serialize_doc(leaderboard),
        "reviews": serialize_doc(reviews),
        "news": serialize_doc(news),
        "paths": serialize_doc(paths),
        "kingdoms": serialize_doc(kingdoms),
        "online": {
            "now": random.randint(2800, 3500),
            "last_hour": random.randint(8000, 12000),
            "last_24h": random.randint(35000, 55000),
        },
    }


@api_router.get("/ticker")
async def get_ticker():
    ticker = await db.ticker_events.find({}, {"_id": 0}).to_list(100)
    return serialize_doc(ticker)


@api_router.get("/leaderboard")
async def get_leaderboard():
    entries = await db.leaderboard.find({}, {"_id": 0}).sort("rank", 1).to_list(50)
    return serialize_doc(entries)


@api_router.get("/reviews")
async def get_reviews():
    return serialize_doc(await db.reviews.find({}, {"_id": 0}).to_list(50))


@api_router.get("/news")
async def get_news():
    return serialize_doc(await db.news.find({}, {"_id": 0}).to_list(20))


@api_router.get("/features")
async def get_features():
    features = await db.features.find({}, {"_id": 0}).sort("index", 1).to_list(100)
    return serialize_doc(features)


@api_router.get("/paths")
async def get_paths():
    return serialize_doc(await db.paths.find({}, {"_id": 0}).to_list(10))


@api_router.get("/kingdoms")
async def get_kingdoms():
    return serialize_doc(await db.kingdoms.find({}, {"_id": 0}).to_list(20))


@api_router.get("/stats/online")
async def get_online_stats():
    return {
        "now": random.randint(2800, 3500),
        "last_hour": random.randint(8000, 12000),
        "last_24h": random.randint(35000, 55000),
    }


# ─────────────────────────────────────────────
# Auth Endpoints
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

    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    starter = PATH_STARTERS[path_choice].copy()

    user_doc = {
        "id": str(uuid.uuid4()),
        "username": user.username,
        "email": user.email,
        "password": hashed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "level": 1,
        "path_choice": path_choice,
        **starter,
    }
    await db.users.insert_one(user_doc)

    token = create_access_token(user_doc["id"], user.username)
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

    token = create_access_token(user["id"], user["username"])
    profile = user_to_profile(user)

    return {
        "success": True,
        "message": f"Welcome back, {user['username']}! The Realm awaits your return.",
        "token": token,
        "user": profile,
    }


@api_router.post("/auth/logout")
async def logout():
    # Client-side token invalidation (stateless JWT)
    return {"success": True, "message": "You have left the Realm safely. Until next time."}


@api_router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": user_to_profile(current_user)}


# ─────────────────────────────────────────────
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
