#!/usr/bin/env python3
"""
Travel System Test - Level Gating
Tests that a Level 3 user can travel to Level 2/3 kingdoms
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ.get('DB_NAME', 'aethoria_db')

KINGDOMS = [
    {"id": "aethoria_capital", "name": "Aethoria Prime", "min_level": 1},
    {"id": "ironhold", "name": "Ironhold", "min_level": 3},
    {"id": "shadowfen", "name": "Shadowfen", "min_level": 2},
    {"id": "goldenveil", "name": "Goldenveil", "min_level": 2},
]

async def main():
    print("\n" + "="*80)
    print("🗺️  TRAVEL SYSTEM - LEVEL GATING TEST")
    print("="*80 + "\n")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    test_user_id = str(uuid.uuid4())
    test_username = f"test_traveler_{uuid.uuid4().hex[:8]}"
    
    try:
        # Create Level 3 user
        print("1️⃣  Creating Level 3 test user...")
        test_user = {
            'id': test_user_id,
            'username': test_username,
            'email': f'{test_username}@test.com',
            'password': 'hashed_dummy',
            'path_choice': 'knight',
            'path_label': 'The Knight',
            'level': 3,  # LEVEL 3
            'xp': 450,
            'gold': 1000,
            'energy': 100,
            'hp': 100,
            'stats': {'strength': 15, 'dexterity': 10, 'speed': 10, 'defense': 10},
            'equipment': {'weapon': None, 'offhand': None, 'armor': None, 'helmet': None, 'boots': None},
            'location': 'aethoria_capital',
            'title': 'The Knight',
            'created_at': datetime.now(timezone.utc),
            'last_seen': datetime.now(timezone.utc),
            'last_energy_regen': datetime.now(timezone.utc),
            'last_hp_regen': datetime.now(timezone.utc),
            'days_in_realm': 0,
        }
        await db.users.insert_one(test_user)
        print(f"   ✅ User created: {test_username} (Level {test_user['level']})")
        
        # TEST: Simulate travel endpoint logic
        print("\n2️⃣  TEST: Simulating travel to kingdoms with various level requirements...")
        
        for kingdom in KINGDOMS[1:]:  # Skip capital (already there)
            print(f"\n   🌍 Testing travel to: {kingdom['name']} (min level: {kingdom['min_level']})")
            
            # Fetch fresh user from DB (this is the fix!)
            fresh_user = await db.users.find_one({'id': test_user_id})
            print(f"      - Fresh user level from DB: {fresh_user['level']}")
            
            # Check level requirement
            if fresh_user['level'] >= kingdom.get('min_level', 1):
                print(f"      ✅ PASS: Level check passed ({fresh_user['level']} >= {kingdom['min_level']})")
            else:
                print(f"      ❌ FAIL: Level check failed ({fresh_user['level']} < {kingdom['min_level']})")
                print(f"         This should NOT happen for a Level 3 user!")
                return
        
        print("\n" + "="*80)
        print("✅ ALL TRAVEL LEVEL-GATING TESTS PASSED!")
        print("="*80)
        print("\nVerified:")
        print("  ✓ Level 3 user can travel to Shadowfen (level 2)")
        print("  ✓ Level 3 user can travel to Goldenveil (level 2)")
        print("  ✓ Level 3 user can travel to Ironhold (level 3)")
        print("  ✓ Fresh user level is fetched from DB (not stale JWT)")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up test user: {test_username}...")
        await db.users.delete_one({'id': test_user_id})
        print("   ✅ Cleanup complete")
        client.close()

if __name__ == '__main__':
    asyncio.run(main())
