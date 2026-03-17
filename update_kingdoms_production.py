#!/usr/bin/env python3
"""Update kingdoms in production database with min_level and travel_cost"""
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Use env variable from backend/.env
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://admin:AethoriaSecure2024!MongoPass@mongodb:27017/aethoria?authSource=admin')

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
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client.aethoria
        
        # Test connection
        await client.server_info()
        print("✓ MongoDB connected")
        
        print("\n🔄 Updating kingdoms in database...")
        
        # Get all kingdoms first
        all_kingdoms = await db.kingdoms.find({}, {'_id': 0, 'id': 1, 'name': 1}).to_list(20)
        print(f"Found {len(all_kingdoms)} kingdoms in database")
        
        # Update by name match (since UUIDs differ)
        updated_count = 0
        for kingdom_id, updates in KINGDOM_UPDATES.items():
            # Find kingdom by its original id field (not UUID)
            result = await db.kingdoms.update_one(
                {'id': kingdom_id},
                {'$set': updates}
            )
            if result.matched_count > 0:
                print(f"✓ Updated {kingdom_id}")
                updated_count += 1
            else:
                print(f"⚠️  Kingdom {kingdom_id} not found, skipping...")
        
        print(f"\n✅ Updated {updated_count}/{len(KINGDOM_UPDATES)} kingdoms")
        
        # Verify
        print("\n📊 Verification:")
        kingdoms = await db.kingdoms.find({}, {'_id': 0, 'id': 1, 'name': 1, 'min_level': 1, 'travel_cost': 1}).to_list(20)
        for k in kingdoms[:5]:
            print(f"  {k.get('name', 'Unknown')}: Level {k.get('min_level', '?')}, Cost {k.get('travel_cost', '?')}g")
        
        client.close()
        print("\n✅ Database update complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
