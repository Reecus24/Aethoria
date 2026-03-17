#!/usr/bin/env python3
"""Update kingdoms in database with min_level and travel_cost"""
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')

KINGDOM_UPDATES = {
    'aethoria_capital': {'min_level': 1, 'travel_cost': 0},
    'ironhold': {'min_level': 3, 'travel_cost': 50},
    'shadowfen': {'min_level': 2, 'travel_cost': 50, 'desc': 'A city of fog and secrets, where rogues and thieves hold court. Home of the Shadow Guild.'},
    'goldenveil': {'min_level': 2, 'travel_cost': 50},
    'stonecrest': {'min_level': 5, 'travel_cost': 75},
    'crystalmere': {'min_level': 4, 'travel_cost': 60},
    'embervast': {'min_level': 10, 'travel_cost': 100},
    'tidehaven': {'min_level': 6, 'travel_cost': 70},
    'duskwood': {'min_level': 4, 'travel_cost': 55},
    'frostholm': {'min_level': 12, 'travel_cost': 120},
    'sunkeep': {'min_level': 8, 'travel_cost': 85},
}

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.aethoria
    
    print("🔄 Updating kingdoms...")
    
    for kingdom_id, updates in KINGDOM_UPDATES.items():
        result = await db.kingdoms.update_one(
            {'id': kingdom_id},
            {'$set': updates}
        )
        print(f"✓ Updated {kingdom_id}: {updates}")
    
    # Verify
    kingdoms = await db.kingdoms.find({}, {'_id': 0, 'id': 1, 'name': 1, 'min_level': 1, 'travel_cost': 1}).to_list(20)
    print("\n✅ Verification:")
    for k in kingdoms:
        print(f"  {k['name']}: Level {k.get('min_level', '?')}, Cost {k.get('travel_cost', '?')}g")
    
    client.close()
    print("\n✅ Done!")

if __name__ == '__main__':
    asyncio.run(main())
