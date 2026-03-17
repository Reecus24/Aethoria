# 🐳 Docker Deployment (EINFACHSTE METHODE!)

## Schnellstart in 5 Schritten

### 1. Server vorbereiten

```bash
# SSH in deinen Hetzner Server
ssh root@deine-server-ip

# Docker installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose installieren
apt install docker-compose-plugin -y

# Teste Docker
docker --version
docker compose version
```

### 2. App-Dateien hochladen

**Von deinem lokalen Rechner:**

```bash
# Gesamtes /app Verzeichnis hochladen
rsync -avz --progress /pfad/zu/emergent/app/ root@deine-server-ip:/opt/aethoria/

# ODER mit SCP
scp -r /pfad/zu/app root@deine-server-ip:/opt/aethoria/
```

### 3. Environment konfigurieren

```bash
# Auf dem Server
cd /opt/aethoria

# .env Datei erstellen
cp .env.example .env

# Generiere sicheren JWT Secret
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# .env editieren
nano .env

# Fülle aus:
# MONGO_ROOT_PASSWORD=dein_sicheres_passwort
# JWT_SECRET=<der generierte key>
# FRONTEND_BACKEND_URL=https://deine-domain.de (oder http://deine-ip)
```

### 4. App starten!

```bash
cd /opt/aethoria

# Alle Container bauen und starten
docker compose up -d --build

# Status prüfen
docker compose ps

# Logs anschauen
docker compose logs -f
```

### 5. Fertig! 🎉

Öffne deinen Browser:
- `http://deine-server-ip` (ohne SSL)
- `http://deine-domain.de` (ohne SSL)

Für SSL siehe unten ⬇️

---

## Docker Commands Cheatsheet

```bash
# Alles starten
docker compose up -d

# Alles stoppen
docker compose down

# Logs anschauen (alle Services)
docker compose logs -f

# Logs nur Backend
docker compose logs -f backend

# Service neustarten
docker compose restart backend

# App updaten (nach Code-Änderungen)
docker compose down
docker compose up -d --build

# Datenbank-Backup
docker exec aethoria-mongodb mongodump --out /dump
docker cp aethoria-mongodb:/dump ./mongodb-backup-$(date +%Y%m%d)

# In Container gehen (zum Debuggen)
docker exec -it aethoria-backend bash
docker exec -it aethoria-frontend sh

# Alles löschen und neu starten (VORSICHT!)
docker compose down -v  # -v löscht auch Datenbank!
docker compose up -d --build
```

---

## SSL mit Nginx Proxy Manager (Einfacher als Certbot!)

### Option A: Nginx Proxy Manager (EMPFOHLEN)

```bash
# Erstelle separates docker-compose.yml für NPM
cat > docker-compose.npm.yml << 'EOF'
version: '3.8'
services:
  nginx-proxy-manager:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: always
    ports:
      - '80:80'
      - '443:443'
      - '81:81'  # Admin UI
    volumes:
      - ./npm-data:/data
      - ./letsencrypt:/etc/letsencrypt
EOF

# NPM starten
docker compose -f docker-compose.npm.yml up -d

# Jetzt öffne http://deine-server-ip:81
# Login: admin@example.com / changeme
# Ändere sofort das Passwort!

# In der UI:
# 1. Gehe zu "Proxy Hosts"
# 2. Klicke "Add Proxy Host"
# 3. Fülle aus:
#    - Domain: deine-domain.de
#    - Scheme: http
#    - Forward Hostname: deine-server-ip
#    - Forward Port: 80
# 4. Tab "SSL": 
#    - Request new SSL Certificate
#    - Force SSL: ON
# 5. Save

# Fertig! SSL ist automatisch konfiguriert!
```

### Option B: Certbot direkt

```bash
# Certbot installieren
apt install certbot -y

# Stoppe Nginx Container kurz
docker compose stop nginx

# SSL-Zertifikat holen
certbot certonly --standalone -d deine-domain.de

# Zertifikate nach /opt/aethoria/ssl kopieren
mkdir -p /opt/aethoria/ssl
cp /etc/letsencrypt/live/deine-domain.de/fullchain.pem /opt/aethoria/ssl/
cp /etc/letsencrypt/live/deine-domain.de/privkey.pem /opt/aethoria/ssl/

# nginx.conf updaten (füge SSL-Block hinzu)
# Dann: docker compose up -d
```

---

## Troubleshooting

### Container startet nicht:

```bash
# Prüfe Logs
docker compose logs backend

# Prüfe ob Port bereits belegt
sudo netstat -tulpn | grep :8001
sudo netstat -tulpn | grep :3000

# Prüfe .env Datei
cat .env
```

### MongoDB Connection Error:

```bash
# Prüfe MongoDB Container
docker compose logs mongodb

# Teste Connection
docker exec -it aethoria-mongodb mongosh -u admin -p DEIN_PASSWORT

# Prüfe MONGO_URL in .env
```

### Frontend zeigt Backend-Fehler:

```bash
# Prüfe Backend logs
docker compose logs backend

# Teste Backend direkt
curl http://localhost:8001/api/landing
```

---

## Production Checklist

Vor dem Live-Gang:

- [ ] `.env` Datei ausgefüllt mit sicheren Passwörtern
- [ ] JWT_SECRET generiert (32+ Zeichen)
- [ ] Domain konfiguriert (DNS A-Record zeigt auf Server-IP)
- [ ] SSL aktiviert (HTTPS)
- [ ] Firewall konfiguriert (UFW: Port 80, 443, 22)
- [ ] MongoDB-Backups eingerichtet (cronjob)
- [ ] Services starten automatisch (docker compose restart policy: always)
- [ ] Monitoring eingerichtet (optional: Uptime Kuma, Grafana)

---

## Performance-Tipps

### MongoDB-Indizes optimieren:

```bash
docker exec -it aethoria-mongodb mongosh -u admin -p DEIN_PASSWORT

use aethoria
db.users.createIndex({ "username": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })
db.events.createIndex({ "created_at": -1 })
db.market_listings.createIndex({ "active": 1, "item_id": 1 })
```

### Container-Ressourcen begrenzen:

Füge in `docker-compose.yml` hinzu:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

---

## Update-Prozess

```bash
# 1. Neue Dateien hochladen
rsync -avz /lokaler/pfad/ root@server:/opt/aethoria/

# 2. Container neu bauen und starten
cd /opt/aethoria
docker compose down
docker compose up -d --build

# 3. Prüfe Logs
docker compose logs -f

# Fertig!
```

---

## Backup & Restore

### Backup erstellen:

```bash
# MongoDB Backup
docker exec aethoria-mongodb mongodump --out /dump
docker cp aethoria-mongodb:/dump ./backup-$(date +%Y%m%d)
tar -czf backup-$(date +%Y%m%d).tar.gz backup-$(date +%Y%m%d)

# Code Backup
tar -czf aethoria-code-$(date +%Y%m%d).tar.gz /opt/aethoria
```

### Restore:

```bash
# Entpacke Backup
tar -xzf backup-20260317.tar.gz

# Restore MongoDB
docker cp backup-20260317 aethoria-mongodb:/restore
docker exec aethoria-mongodb mongorestore /restore
```

---

## Automatisches Backup (Cronjob)

```bash
# Backup-Script erstellen
cat > /opt/aethoria/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/aethoria"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# MongoDB Backup
docker exec aethoria-mongodb mongodump --out /dump
docker cp aethoria-mongodb:/dump $BACKUP_DIR/db-$DATE

# Komprimieren
cd $BACKUP_DIR
tar -czf db-$DATE.tar.gz db-$DATE
rm -rf db-$DATE

# Alte Backups löschen (älter als 7 Tage)
find $BACKUP_DIR -name "db-*.tar.gz" -mtime +7 -delete

echo "Backup complete: $BACKUP_DIR/db-$DATE.tar.gz"
EOF

chmod +x /opt/aethoria/backup.sh

# Cronjob erstellen (täglich um 3 Uhr nachts)
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/aethoria/backup.sh") | crontab -
```
