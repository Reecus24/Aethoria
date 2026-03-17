# ⚡ SCHNELLSTART - In 10 Minuten Live!

## 🎯 Die einfachste Methode: Docker

### 1. Server vorbereiten (2 Minuten)

```bash
# SSH in deinen Hetzner Server
ssh root@DEINE_SERVER_IP

# Docker installieren (ein Befehl!)
curl -fsSL https://get.docker.com | sh

# Docker Compose installieren
apt install docker-compose-plugin -y
```

### 2. App hochladen (3 Minuten)

**Auf deinem lokalen Rechner:**

Zuerst die App von Emergent herunterladen:
- Gehe zu deinem Emergent Dashboard
- Finde dein Projekt "dragon-quest-46"  
- Klicke auf "Download" oder "Export"
- Entpacke die ZIP-Datei

Dann auf den Server laden:

```bash
# Ersetze /pfad/zu/app mit deinem tatsächlichen Pfad
rsync -avz --progress /pfad/zu/app/ root@DEINE_SERVER_IP:/opt/aethoria/
```

### 3. Konfiguration (2 Minuten)

**Auf dem Server:**

```bash
cd /opt/aethoria

# Erstelle .env Datei
cat > .env << 'EOF'
MONGO_ROOT_PASSWORD=mein_sicheres_passwort_2024
JWT_SECRET=super_geheimer_schluessel_32_zeichen_lang
FRONTEND_BACKEND_URL=http://DEINE_SERVER_IP
EOF

# ⚠️ WICHTIG: Ersetze "DEINE_SERVER_IP" mit deiner echten IP!
# Beispiel: FRONTEND_BACKEND_URL=http://159.69.123.456

# Editiere die Datei
nano .env
# Drücke Ctrl+X, dann Y, dann Enter zum Speichern
```

### 4. Starten! (1 Minute)

```bash
cd /opt/aethoria

# Alles starten
docker compose up -d --build

# Warte 30 Sekunden für den Start
sleep 30

# Prüfe Status
docker compose ps
```

### 5. Testen! (2 Minuten)

```bash
# Test API
curl http://localhost:8001/api/landing

# Öffne in deinem Browser:
# http://DEINE_SERVER_IP
```

### 🎉 FERTIG! Dein Spiel läuft!

---

## 🔐 SSL hinzufügen (Optional, 5 Minuten extra)

**Nur wenn du eine Domain hast (z.B. meinspiel.de):**

### Methode 1: Nginx Proxy Manager (EINFACHSTE!)

```bash
# Stoppe die App kurz
cd /opt/aethoria
docker compose down

# Editiere docker-compose.yml
nano docker-compose.yml

# Entferne die "ports:" Zeilen bei nginx (80:80 und 443:443)
# Speichere und beende

# Installiere Nginx Proxy Manager
cat > docker-compose.npm.yml << 'EOF'
version: '3.8'
services:
  nginx-proxy-manager:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: always
    ports:
      - '80:80'
      - '443:443'
      - '81:81'
    volumes:
      - ./npm-data:/data
      - ./letsencrypt:/etc/letsencrypt
EOF

# Starte beides
docker compose up -d
docker compose -f docker-compose.npm.yml up -d

# Öffne http://DEINE_SERVER_IP:81
# Login: admin@example.com / changeme
# Ändere sofort das Passwort!

# In der UI:
# 1. "Proxy Hosts" → "Add Proxy Host"
# 2. Domain: deine-domain.de
# 3. Forward to: aethoria-nginx (oder deine Server-IP)
# 4. Port: 80
# 5. Tab "SSL" → Request new certificate
# 6. Save

# Fertig! https://deine-domain.de läuft!
```

### Methode 2: Certbot direkt

```bash
apt install certbot -y

# Stoppe Container auf Port 80
docker compose stop nginx

# Hole Zertifikat
certbot certonly --standalone -d deine-domain.de

# Kopiere Zertifikate
mkdir -p /opt/aethoria/ssl
cp /etc/letsencrypt/live/deine-domain.de/fullchain.pem /opt/aethoria/ssl/
cp /etc/letsencrypt/live/deine-domain.de/privkey.pem /opt/aethoria/ssl/

# Editiere nginx.conf und füge SSL hinzu
# Dann: docker compose up -d
```

---

## 🛠️ Häufige Befehle

```bash
# Status checken
docker compose ps

# Logs live
docker compose logs -f

# Backend neustarten
docker compose restart backend

# Alles neustarten
docker compose restart

# Alles stoppen
docker compose down

# Alles löschen (inkl. Datenbank!)
docker compose down -v

# Ressourcen-Verbrauch checken
docker stats
```

---

## ⚠️ Wichtige Hinweise

1. **Firewall öffnen:**
   ```bash
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 22/tcp  # SSH!
   ufw enable
   ```

2. **Domain-DNS konfigurieren:**
   - Gehe zu deinem Domain-Provider
   - Erstelle einen A-Record:
     - Name: @ (oder www)
     - Typ: A
     - Wert: DEINE_SERVER_IP
   - Warte 5-10 Minuten für DNS-Propagierung

3. **Monitoring:**
   - Installiere Uptime Kuma für Monitoring: `docker run -d --restart=always -p 3001:3001 louislam/uptime-kuma:1`
   - Öffne http://DEINE_SERVER_IP:3001

---

## 🐛 Probleme lösen

### "Container startet nicht":
```bash
docker compose logs backend  # Zeigt Fehler
```

### "502 Bad Gateway":
```bash
# Backend läuft nicht
docker compose restart backend
docker compose logs backend
```

### "MongoDB connection failed":
```bash
# Prüfe MongoDB
docker compose logs mongodb

# Prüfe .env MONGO_URL
cat .env
```

### "Frontend zeigt altes Code":
```bash
# Browser-Cache löschen: Ctrl+Shift+R
# Oder Frontend neu bauen:
docker compose up -d --build frontend
```

---

## 📦 Produktions-Optimierungen

### Ressourcen-Limits setzen:

Editiere `docker-compose.yml` und füge hinzu:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 1G
```

### Automatische Backups:

```bash
# Cronjob für täglich 3 Uhr
crontab -e

# Füge hinzu:
0 3 * * * cd /opt/aethoria && docker exec aethoria-mongodb mongodump --out /dump && docker cp aethoria-mongodb:/dump /backups/aethoria-$(date +\%Y\%m\%d)
```

---

## ✅ Fertig!

Dein Spiel läuft jetzt auf:
- **HTTP:** `http://deine-server-ip` oder `http://deine-domain.de`
- **HTTPS:** `https://deine-domain.de` (nach SSL-Setup)

**Support-Commands:**
- Status: `docker compose ps`
- Logs: `docker compose logs -f`
- Restart: `docker compose restart`
- Stop: `docker compose down`
