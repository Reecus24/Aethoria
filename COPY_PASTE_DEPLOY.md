# 🎯 HETZNER DEPLOYMENT - COPY & PASTE BEFEHLE

## 🚀 Schritt-für-Schritt (15 Minuten)

### Auf deinem LOKALEN Rechner:

#### 1. Download das Deployment-Package von Emergent

```bash
# Das Package liegt hier: /app/aethoria-deploy-20260317_053427.tar.gz
# Lade es über das Emergent UI herunter
```

#### 2. Lade es auf deinen Hetzner Server

```bash
# Ersetze DEINE_SERVER_IP mit deiner echten IP
scp aethoria-deploy-*.tar.gz root@DEINE_SERVER_IP:/tmp/
```

---

### Auf deinem HETZNER Server:

#### 3. SSH in den Server

```bash
ssh root@DEINE_SERVER_IP
```

#### 4. Docker installieren (falls noch nicht vorhanden)

```bash
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y
```

#### 5. App entpacken

```bash
cd /opt
tar -xzf /tmp/aethoria-deploy-*.tar.gz
mv aethoria-export aethoria
cd aethoria
```

#### 6. Environment konfigurieren

```bash
# Erstelle .env aus Vorlage
cp .env.example .env

# Generiere sicheren JWT Key
JWT_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "Dein JWT_SECRET: $JWT_KEY"

# Editiere .env
nano .env

# Ändere diese Zeilen:
# MONGO_ROOT_PASSWORD=mein_sicheres_passwort_123
# JWT_SECRET=<der generierte key von oben>
# FRONTEND_BACKEND_URL=http://DEINE_SERVER_IP
#
# Speichern: Ctrl+X, dann Y, dann Enter
```

#### 7. Starten!

```bash
docker compose up -d --build

# Warte 30 Sekunden
sleep 30

# Prüfe Status
docker compose ps

# Sollte zeigen:
# aethoria-mongodb    running
# aethoria-backend    running  
# aethoria-frontend   running
# aethoria-nginx      running
```

#### 8. Testen!

```bash
# Test API
curl http://localhost:8001/api/landing

# Sollte JSON zurückgeben mit leaderboard, ticker, etc.
```

#### 9. Firewall öffnen

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

#### 10. Im Browser öffnen!

```
http://DEINE_SERVER_IP
```

---

## ✅ FERTIG! Dein Spiel läuft!

### Nützliche Befehle:

```bash
# Logs anschauen
docker compose logs -f backend

# Service neustarten
docker compose restart backend

# Alles stoppen
docker compose down

# Alles neustarten
docker compose restart
```

---

## 🔧 Wenn etwas nicht funktioniert:

### Backend Error:

```bash
# Logs checken
docker compose logs backend | tail -50

# Häufigster Fehler: MongoDB Connection
# Lösung: Prüfe .env MONGO_URL
cat .env | grep MONGO_URL
```

### Frontend zeigt Fehler:

```bash
# Prüfe Backend läuft
curl http://localhost:8001/api/landing

# Prüfe .env.production
cat /opt/aethoria/frontend/.env.production

# Neu bauen
docker compose up -d --build frontend
```

### 502 Bad Gateway:

```bash
# Backend ist down
docker compose restart backend

# Oder Nginx config fehler
docker compose logs nginx
```

---

## 🎮 Game-Bots starten (Optional)

```bash
cd /opt/aethoria

# Bots laufen lassen (erzeugt Events für den Ticker)
bash start_bots.sh

# Oder dauerhaft im Hintergrund
nohup python3 game_bot.py > /tmp/bots.log 2>&1 &
```

---

## 📊 Monitoring & Maintenance

### Backup erstellen:

```bash
# MongoDB Backup
docker exec aethoria-mongodb mongodump --out /dump
docker cp aethoria-mongodb:/dump ./backup-$(date +%Y%m%d)
tar -czf backup-$(date +%Y%m%d).tar.gz backup-$(date +%Y%m%d)
```

### Automatisches Backup (Cronjob):

```bash
# Backup-Script erstellen
cat > /opt/aethoria/backup.sh << 'EOF'
#!/bin/bash
docker exec aethoria-mongodb mongodump --out /dump
docker cp aethoria-mongodb:/dump /backups/aethoria-$(date +%Y%m%d)
EOF

chmod +x /opt/aethoria/backup.sh

# Täglich um 3 Uhr
(crontab -l; echo "0 3 * * * /opt/aethoria/backup.sh") | crontab -
```

### Ressourcen überwachen:

```bash
# Docker Stats
docker stats

# Server-Ressourcen
htop
```

---

## 🆘 Support

Bei Problemen:
1. Prüfe Logs: `docker compose logs -f`
2. Prüfe Status: `docker compose ps`
3. Prüfe .env Datei: `cat .env`
4. Google den Fehler aus den Logs
5. Server neustarten: `reboot` (als letztes Mittel)

**Wichtige Log-Files:**
- Backend: `docker compose logs backend`
- Frontend: `docker compose logs frontend`
- MongoDB: `docker compose logs mongodb`
- Nginx: `docker compose logs nginx`
