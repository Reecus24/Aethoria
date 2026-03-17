# 🚀 Deployment von GitHub → Hetzner Server

## 1:1 Copy & Paste Befehle

---

## Schritt 1: SSH in deinen Server

```bash
ssh root@DEINE_SERVER_IP
```

Ersetze `DEINE_SERVER_IP` mit deiner echten IP (z.B. `ssh root@159.69.123.45`)

---

## Schritt 2: Altes Projekt löschen (falls vorhanden)

```bash
# Stoppe alle laufenden Services
docker stop $(docker ps -aq) 2>/dev/null || true
systemctl stop nginx apache2 mysql postgresql mongod 2>/dev/null || true
pkill -9 node 2>/dev/null || true
pkill -9 python3 2>/dev/null || true

# Lösche alte App-Verzeichnisse
rm -rf /opt/aethoria
rm -rf /opt/*  # ⚠️ Nur wenn du wirklich ALLES löschen willst!

# Autoremove
apt autoremove -y

echo "✅ Alte Projekte entfernt"
```

---

## Schritt 3: Docker installieren (falls noch nicht vorhanden)

```bash
# Prüfe ob Docker schon existiert
docker --version

# Wenn nicht, installiere Docker:
curl -fsSL https://get.docker.com | sh

# Docker Compose installieren
apt install docker-compose-plugin -y

# Teste Docker
docker --version
docker compose version

echo "✅ Docker installiert"
```

---

## Schritt 4: Git installieren & Repo clonen

```bash
# Git installieren (falls nicht vorhanden)
apt install git -y

# Gehe zu /opt Verzeichnis
cd /opt

# Clone dein GitHub Repo
git clone https://github.com/DEIN_USERNAME/DEIN_REPO_NAME.git aethoria

# Gehe in das Verzeichnis
cd aethoria

# Prüfe Dateien
ls -la

echo "✅ Repo gecloned"
```

**Ersetze in dem `git clone` Befehl:**
- `DEIN_USERNAME` mit deinem GitHub-Username
- `DEIN_REPO_NAME` mit dem Repo-Namen

**Beispiel:**
```bash
git clone https://github.com/maxmustermann/realm-of-aethoria.git aethoria
```

---

## Schritt 5: Environment-Dateien erstellen

```bash
cd /opt/aethoria

# Erstelle .env für Docker Compose
cat > .env << 'EOF'
MONGO_ROOT_PASSWORD=sicheres_mongo_passwort_2024
JWT_SECRET=GENERIERE_EINEN_HIER
FRONTEND_BACKEND_URL=http://DEINE_SERVER_IP
EOF

# Generiere sicheren JWT Secret
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"

# ⚠️ Kopiere den generierten JWT_SECRET und füge ihn in die .env ein:
nano .env

# Editiere diese Zeilen:
# 1. MONGO_ROOT_PASSWORD=dein_sicheres_passwort (erfinde eins)
# 2. JWT_SECRET=<der generierte key von oben einfügen>
# 3. FRONTEND_BACKEND_URL=http://DEINE_SERVER_IP (z.B. http://159.69.123.45)
#
# Speichern: Ctrl+X, dann Y, dann Enter

echo "✅ Environment konfiguriert"
```

---

## Schritt 6: Backend .env erstellen

```bash
cd /opt/aethoria/backend

# Erstelle Backend .env
cat > .env << 'EOF'
MONGO_URL=mongodb://admin:sicheres_mongo_passwort_2024@mongodb:27017/aethoria?authSource=admin
JWT_SECRET=DER_GLEICHE_WIE_OBEN
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=30
EOF

# ⚠️ Editiere und füge den gleichen JWT_SECRET wie in /opt/aethoria/.env ein:
nano .env

# Stelle sicher dass MONGO_URL das gleiche Passwort hat wie in der Haupt-.env!

echo "✅ Backend .env erstellt"
```

---

## Schritt 7: Frontend .env erstellen

```bash
cd /opt/aethoria/frontend

# Erstelle Frontend .env
cat > .env.production << 'EOF'
REACT_APP_BACKEND_URL=http://DEINE_SERVER_IP
EOF

# ⚠️ Ersetze DEINE_SERVER_IP:
nano .env.production

# Wenn du eine Domain hast, nutze:
# REACT_APP_BACKEND_URL=https://deine-domain.de

echo "✅ Frontend .env erstellt"
```

---

## Schritt 8: App mit Docker starten! 🚀

```bash
cd /opt/aethoria

# Starte alle Services
docker compose up -d --build

# Dies baut und startet:
# - MongoDB
# - Backend (FastAPI)
# - Frontend (React)
# - Nginx (Reverse Proxy)

echo "⏳ Warte 30 Sekunden für Startup..."
sleep 30

# Prüfe Status
docker compose ps

# Sollte zeigen:
# NAME                  STATUS
# aethoria-mongodb      Up
# aethoria-backend      Up
# aethoria-frontend     Up
# aethoria-nginx        Up

echo "✅ Services laufen!"
```

---

## Schritt 9: Firewall öffnen

```bash
# Öffne HTTP/HTTPS Ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp  # SSH (wichtig!)
ufw --force enable

echo "✅ Firewall konfiguriert"
```

---

## Schritt 10: Testen! 🎮

```bash
# Test Backend API
curl http://localhost:8001/api/landing

# Sollte JSON mit Leaderboard, Ticker, etc. zurückgeben

# Test Frontend
curl http://localhost

# Sollte HTML zurückgeben
```

**Öffne in deinem Browser:**
```
http://DEINE_SERVER_IP
```

**Ersetze DEINE_SERVER_IP mit deiner echten IP!**

---

## ✅ FERTIG! Dein Spiel läuft!

**Nützliche Befehle:**

```bash
# Logs anschauen (alles)
docker compose logs -f

# Nur Backend-Logs
docker compose logs -f backend

# Nur Frontend-Logs
docker compose logs -f frontend

# Status checken
docker compose ps

# Service neustarten
docker compose restart backend

# Alles neustarten
docker compose restart

# Alles stoppen
docker compose down
```

---

## 🔧 Wenn etwas nicht funktioniert:

### Backend startet nicht:

```bash
# Logs checken
docker compose logs backend

# Häufigster Fehler: .env nicht richtig konfiguriert
cat backend/.env
```

### Frontend zeigt Fehler:

```bash
# Prüfe ob Backend läuft
curl http://localhost:8001/api/landing

# Prüfe Frontend .env
cat frontend/.env.production

# Neu bauen
docker compose up -d --build frontend
```

### "Cannot connect to Docker daemon":

```bash
# Docker starten
systemctl start docker

# Oder Docker neu installieren
curl -fsSL https://get.docker.com | sh
```

### MongoDB Connection Error:

```bash
# Prüfe MongoDB läuft
docker compose logs mongodb

# Prüfe Passwort in beiden .env Dateien übereinstimmt
cat .env | grep MONGO_ROOT_PASSWORD
cat backend/.env | grep MONGO_URL
```

---

## 🎮 Game-Bots starten (optional)

```bash
cd /opt/aethoria

# Bots für lebendige Events
bash start_bots.sh

# Das registriert 5 KI-Spieler und lässt sie spielen
```

---

## 🔄 Code-Updates von GitHub

**Später, wenn du Code-Änderungen machst:**

```bash
cd /opt/aethoria

# Stoppe Services
docker compose down

# Hole neuesten Code
git pull origin main

# Starte neu (baut automatisch neu)
docker compose up -d --build

# Fertig!
```

---

## 📊 Monitoring

```bash
# Docker Stats (Ressourcen-Verbrauch)
docker stats

# Alle Logs live
docker compose logs -f

# System-Ressourcen
htop  # (installiere mit: apt install htop)
```

---

## 🆘 Emergency Commands

```bash
# Alles stoppen
docker compose down

# Alles neu starten
docker compose up -d --build

# Datenbank zurücksetzen (⚠️ löscht alle Spielerdaten!)
docker compose down -v
docker compose up -d --build

# Server neustarten
reboot
```

---

## ✅ Deployment-Checklist

Nach dem Deployment:

- [ ] `docker compose ps` zeigt alle 4 Services als "Up"
- [ ] `curl http://localhost:8001/api/landing` gibt JSON zurück
- [ ] Browser `http://DEINE_SERVER_IP` zeigt die Landing Page
- [ ] Registrierung funktioniert
- [ ] Login funktioniert
- [ ] Game-Dashboard lädt
- [ ] Training/Crimes funktionieren
- [ ] Event-Ticker scrollt mit vernünftiger Geschwindigkeit

---

## 🎯 Nächste Schritte (optional):

### SSL mit Domain hinzufügen:

Siehe `DOCKER_DEPLOYMENT.md` im Package → "SSL mit Nginx Proxy Manager"

### Automatische Backups:

```bash
# Täglich MongoDB-Backup
crontab -e

# Füge hinzu:
0 3 * * * cd /opt/aethoria && docker exec aethoria-mongodb mongodump --out /dump && docker cp aethoria-mongodb:/dump /backups/db-$(date +\%Y\%m\%d)
```

### Monitoring einrichten:

```bash
# Uptime Kuma (einfachstes Monitoring-Tool)
docker run -d --restart=always -p 3001:3001 --name uptime-kuma louislam/uptime-kuma:1

# Öffne: http://DEINE_SERVER_IP:3001
```
