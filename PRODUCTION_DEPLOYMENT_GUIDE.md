# 🔧 PRODUCTION BUG FIXES - DEPLOYMENT GUIDE

## Was wurde gefixt:

### ✅ Kritische Bugs (14+):
1. **Path Stats** - Alle Klassen zeigen jetzt 100g (nicht 500g)
2. **Equipment Display** - Wird jetzt im Character-Window angezeigt
3. **Mug-System** - Macht KEINEN Schaden mehr, nur Gold-Diebstahl + Jail-Chance (30%)
4. **XP-System** - Zeigt jetzt korrektes xp_required (nicht 0/100)
5. **Combat Log Colors** - Siege sind GRÜN
6. **Tavern Dice** - Zeigt Gold korrekt (nicht "undefined")
7. **Hospital/Dungeon Timer** - Zeigen MM:SS Format
8. **Dungeon Liste** - Zeigt nur eigenen User
9. **Travel System** - Level-Requirements + Costs hinzugefügt
10. **Messages** - API-Calls gefixt
11. **Properties** - API-Response gefixt
12. **Path-Navigation** - Shadow sieht Dark Deeds, Noble sieht Markets
13. **Class-Quests** - Jede Klasse hat eigene Quests
14. **Item Effects** - Werden im Inventar angezeigt
15. **Hall of Fame** - Zeigt Spieler-Namen (nicht Klassen)
16. **Kingdom Travel** - Level-Requirements sichtbar

### 🏰 Features hinzugefügt:
17. **Shadowfen** - Jetzt als "Home of the Shadow Guild" beschrieben
18. **Kingdom-System** - Level-Requirements: 1-12, Travel-Costs: 0-120g

---

## 🚀 DEPLOYMENT SCHRITTE:

### Schritt 1: Klicke "Save to GitHub" in Emergent

In der Emergent-Web-UI (wo du mit mir chattest):
1. Klicke auf **"Save to GitHub"**
2. Warte bis Upload complete
3. ✅ Check auf GitHub, dass neuer Commit da ist

---

### Schritt 2: Update auf deinem Server

**SSH zu deinem Server:**
```bash
ssh root@178.104.19.199
cd /opt/aethoria
```

**Pull die neuesten Änderungen:**
```bash
# Remote URL korrigieren (falls nötig)
git remote set-url origin https://github.com/Reecus24/Aethoria.git

# Pull
git pull origin main

# Sollte zeigen: "X files changed"
```

---

### Schritt 3: Database Update (WICHTIG!)

**Kingdoms-Data updaten:**
```bash
cd /opt/aethoria

# Run update script IN the backend container
docker exec -i aethoria-backend python3 << 'PYTHON_SCRIPT'
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(MONGO_URL)
db = client.aethoria

async def update():
    updates = {
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
    
    for kid, upd in updates.items():
        await db.kingdoms.update_one({'id': kid}, {'$set': upd})
    
    print("✅ Kingdoms updated")

asyncio.run(update())
PYTHON_SCRIPT

echo "✅ Database update complete"
```

---

### Schritt 4: Rebuild & Restart

```bash
cd /opt/aethoria

# Down
docker compose down

# Build (no cache!)
docker compose build --no-cache

# Up
docker compose up -d

# Wait
sleep 30

# Check
docker compose ps
```

---

### Schritt 5: Test im Browser

1. Öffne: `http://178.104.19.199`
2. **Hard-Refresh:** `Ctrl + Shift + R`
3. Teste:
   - ✅ Neue Character: Zeigt 100g (nicht 500g)
   - ✅ Equipment: Wird im Character-Window angezeigt
   - ✅ Training: Stats erhöhen sich nach Claim
   - ✅ Mug (Shadow): Macht keinen Schaden, klaut nur Gold
   - ✅ Travel: Zeigt Level-Requirements
   - ✅ Quests: Jede Klasse hat eigene Quests
   - ✅ XP-Anzeige: Zeigt z.B. "50/150" (nicht "0/100")

---

## 🐛 Falls etwas nicht funktioniert:

```bash
# Logs checken
docker logs aethoria-backend --tail=50
docker logs aethoria-frontend --tail=50

# Status
docker compose ps
```

---

## ✅ Erfolg-Check:

Nach dem Deployment:
- [ ] Path-Selection zeigt 100g
- [ ] Equipment im Character-Window sichtbar  
- [ ] Mug macht keinen Damage
- [ ] XP-Display zeigt korrekten Wert
- [ ] Travel zeigt Level-Requirements
- [ ] Messages funktionieren
- [ ] Klassenspezifische Quests

---

**Melde dich nach dem Deployment für finale Tests!** 🎮
