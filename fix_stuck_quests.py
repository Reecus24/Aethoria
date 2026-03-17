#!/usr/bin/env python3
"""
Script zum Prüfen und Zurücksetzen von feststeckenden Quests
Auf Hetzner ausführen: python3 fix_stuck_quests.py <username>
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'aethoria_db')

async def fix_quests(username):
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"\n🔍 Suche User: {username}")
    user = await db.users.find_one({'username': username})
    
    if not user:
        print(f"❌ User '{username}' nicht gefunden")
        client.close()
        return
    
    user_id = user['id']
    print(f"✅ User gefunden: {user['username']} (Level {user['level']})")
    
    # Alle Quests für diesen User
    all_quests = await db.user_quests.find({'user_id': user_id}).to_list(100)
    
    print(f"\n📋 AKTUELLE QUESTS:")
    print("=" * 70)
    
    if not all_quests:
        print("✅ Keine Quests in der Datenbank")
    else:
        for q in all_quests:
            status_emoji = "🔴" if q.get('status') == 'active' else "✅"
            print(f"{status_emoji} Quest: {q.get('quest_id', 'unknown')}")
            print(f"   Status: {q.get('status', 'unknown')}")
            print(f"   Started: {q.get('start_time', 'unknown')}")
    
    # Count active
    active_quests = [q for q in all_quests if q.get('status') == 'active']
    
    if active_quests:
        print(f"\n⚠️  PROBLEM: {len(active_quests)} aktive Quest(s) gefunden!")
        print(f"\n🔧 LÖSUNG:")
        print(f"   1) Quest als 'completed' markieren (Sie bekommen die Belohnungen)")
        print(f"   2) Quest komplett löschen (keine Belohnungen)")
        
        choice = input(f"\nWas möchten Sie tun? (1/2 oder 'n' zum Abbrechen): ")
        
        if choice == '1':
            # Mark as completed
            for q in active_quests:
                await db.user_quests.update_one(
                    {'_id': q['_id']},
                    {'$set': {'status': 'completed', 'completed_at': datetime.now(timezone.utc)}}
                )
            print(f"   ✅ {len(active_quests)} Quest(s) als 'completed' markiert")
        
        elif choice == '2':
            # Delete completely
            result = await db.user_quests.delete_many({'user_id': user_id, 'status': 'active'})
            print(f"   ✅ {result.deleted_count} aktive Quest(s) gelöscht")
        
        else:
            print(f"   ℹ️  Keine Änderungen vorgenommen")
    else:
        print(f"\n✅ Keine aktiven Quests - alles in Ordnung!")
    
    client.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 fix_stuck_quests.py <username>")
        print("Beispiel: python3 fix_stuck_quests.py MegaKnight")
        sys.exit(1)
    
    username = sys.argv[1]
    asyncio.run(fix_quests(username))
