#!/usr/bin/env python3
"""Clean up test data from database"""
import os
import sys
sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def cleanup():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client['aethoria']
    
    user_count = await db.users.count_documents({})
    event_count = await db.events.count_documents({})
    
    print(f"📊 Vor dem Cleanup:")
    print(f"   Users: {user_count}")
    print(f"   Events: {event_count}")
    
    # Delete everything
    collections = [
        'users', 'events', 'inventories', 'equipment', 'training_sessions', 
        'crime_logs', 'combat_logs', 'user_quests', 'bank_accounts', 
        'bank_investments', 'guilds', 'guild_members', 'messages', 
        'market_listings', 'hospital_sessions', 'dungeon_sessions', 
        'travel_sessions', 'bounties', 'user_properties', 'user_achievements', 
        'hunting_logs', 'idempotency_keys'
    ]
    
    total_deleted = 0
    for coll in collections:
        result = await db[coll].delete_many({})
        if result.deleted_count > 0:
            print(f"   ✓ {coll}: {result.deleted_count} gelöscht")
            total_deleted += result.deleted_count
    
    print(f"\n✅ Datenbank komplett gesäubert!")
    print(f"   Gesamt gelöscht: {total_deleted} Dokumente")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(cleanup())
