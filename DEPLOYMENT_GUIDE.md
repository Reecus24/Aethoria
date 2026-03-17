# 🚀 Realm of Aethoria - Hetzner Deployment Guide

## Übersicht

Dieser Guide zeigt dir, wie du das komplette Spiel auf deinem Hetzner Server deployest.

**Was du brauchst:**
- Hetzner Server (Ubuntu 22.04 oder 24.04 empfohlen)
- Domain (optional, aber empfohlen für SSL)
- Root/Sudo-Zugriff

**Deployment-Methoden:**
1. **Native Deployment** (empfohlen) - Direktes Setup mit systemd
2. **Docker Deployment** (einfacher) - Container-basiert

---

## Option 1: Native Deployment (Empfohlen)

### Schritt 1: Server komplett reinigen

```bash
# SSH in deinen Server
ssh root@deine-server-ip

# Stoppe alle laufenden Services (falls vorhanden)
sudo systemctl stop nginx mongodb apache2 2>/dev/null
sudo systemctl stop aethoria-backend aethoria-frontend 2>/dev/null

# Entferne alte Installationen (VORSICHT: löscht alles!)
sudo apt remove --purge nginx mongodb-org apache2 nodejs npm -y
sudo apt autoremove -y

# Lösche alte App-Dateien
sudo rm -rf /var/www/aethoria
sudo rm -rf /opt/aethoria
sudo rm -rf /etc/systemd/system/aethoria-*
sudo rm -rf /var/log/aethoria

# Lösche MongoDB-Daten (falls du neu anfangen willst)
sudo rm -rf /var/lib/mongodb/*

echo "✅ Server ist sauber!"
```

---

### Schritt 2: System-Dependencies installieren

```bash
# System updaten
sudo apt update && sudo apt upgrade -y

# Python 3.11+ installieren
sudo apt install python3 python3-pip python3-venv -y

# Node.js 20.x installieren
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# MongoDB installieren (Community Edition)
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] \
https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

sudo apt update
sudo apt install mongodb-org -y

# Nginx installieren
sudo apt install nginx -y

# Git installieren
sudo apt install git -y

# Verify installations
echo "--- Versions ---"
python3 --version
node --version
mongod --version | head -1
nginx -v

echo "✅ Alle Dependencies installiert!"
```

---

### Schritt 3: MongoDB konfigurieren

```bash
# MongoDB starten
sudo systemctl start mongod
sudo systemctl enable mongod

# MongoDB-User für die App erstellen (optional, aber sicherer)
mongosh << 'EOF'
use aethoria
db.createUser({
  user: "aethoria_user",
  pwd: "DEIN_SICHERES_PASSWORT_HIER",  # ⚠️ ÄNDERE DIES!
  roles: [{ role: "readWrite", db: "aethoria" }]
})
exit
EOF

# Test MongoDB
mongosh --eval "db.version()"

echo "✅ MongoDB läuft!"
```

---

### Schritt 4: App auf den Server kopieren

**Methode A: Mit Git (empfohlen)**

```bash
# Erstelle App-Verzeichnis
sudo mkdir -p /opt/aethoria
sudo chown $USER:$USER /opt/aethoria
cd /opt/aethoria

# Lade die App-Dateien hoch (von deinem lokalen Rechner)
# Du musst die Dateien erst von Emergent herunterladen
```

**Methode B: Direkt von Emergent exportieren**

Auf deinem **lokalen Rechner**, lade die Dateien von Emergent herunter:

```bash
# Option 1: ZIP-Download über Emergent UI
# Option 2: Git-Clone wenn du ein Repo hast
```

Dann auf den Server hochladen:

```bash
# Von deinem lokalen Rechner
scp -r /pfad/zu/app root@deine-server-ip:/opt/aethoria/

# ODER mit rsync (besser)
rsync -avz --progress /pfad/zu/app/ root@deine-server-ip:/opt/aethoria/
```

**Manuelle Struktur (falls du die Dateien manuell kopierst):**

```bash
cd /opt/aethoria

# Erstelle Struktur
mkdir -p backend frontend

# Kopiere Backend-Dateien
# - backend/server.py
# - backend/requirements.txt
# - backend/.env

# Kopiere Frontend-Dateien  
# - frontend/package.json
# - frontend/src/
# - frontend/public/
# - frontend/.env
```

---

### Schritt 5: Backend einrichten

```bash
cd /opt/aethoria/backend

# Python Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt

# .env Datei erstellen
cat > .env << 'EOF'
MONGO_URL=mongodb://aethoria_user:DEIN_PASSWORT@localhost:27017/aethoria
JWT_SECRET=GENERIERE_EINEN_SICHEREN_RANDOM_KEY_HIER
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=30
EOF

# Generiere sicheren JWT Secret
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> .env.new
# Kopiere den JWT_SECRET in die .env Datei

# Test Backend
python3 server.py &
BACKEND_PID=$!
sleep 5

# Test API
curl http://localhost:8001/api/landing
kill $BACKEND_PID

echo "✅ Backend funktioniert!"
```

---

### Schritt 6: Frontend einrichten

```bash
cd /opt/aethoria/frontend

# Yarn installieren (falls nicht vorhanden)
sudo npm install -g yarn

# Dependencies installieren
yarn install

# .env für Production erstellen
cat > .env.production << 'EOF'
REACT_APP_BACKEND_URL=https://deine-domain.de
EOF

# ⚠️ Wenn du KEINE Domain hast, verwende die Server-IP:
# REACT_APP_BACKEND_URL=http://DEINE_SERVER_IP

# Build für Production
yarn build

echo "✅ Frontend gebaut!"
```

---

### Schritt 7: Systemd Services erstellen

**Backend Service:**

```bash
sudo tee /etc/systemd/system/aethoria-backend.service > /dev/null << 'EOF'
[Unit]
Description=Realm of Aethoria Backend
After=network.target mongodb.service
Requires=mongodb.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/aethoria/backend
Environment="PATH=/opt/aethoria/backend/venv/bin"
ExecStart=/opt/aethoria/backend/venv/bin/python server.py
Restart=always
RestartSec=10

StandardOutput=append:/var/log/aethoria/backend.log
StandardError=append:/var/log/aethoria/backend.error.log

[Install]
WantedBy=multi-user.target
EOF
```

**Frontend Service (mit serve):**

```bash
# Installiere 'serve' global
sudo yarn global add serve

sudo tee /etc/systemd/system/aethoria-frontend.service > /dev/null << 'EOF'
[Unit]
Description=Realm of Aethoria Frontend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/aethoria/frontend
ExecStart=/usr/local/bin/serve -s build -l 3000
Restart=always
RestartSec=10

StandardOutput=append:/var/log/aethoria/frontend.log
StandardError=append:/var/log/aethoria/frontend.error.log

[Install]
WantedBy=multi-user.target
EOF
```

**Logs-Verzeichnis erstellen:**

```bash
sudo mkdir -p /var/log/aethoria
sudo chown www-data:www-data /var/log/aethoria
sudo chown -R www-data:www-data /opt/aethoria
```

**Services starten:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Services aktivieren
sudo systemctl enable aethoria-backend
sudo systemctl enable aethoria-frontend

# Services starten
sudo systemctl start aethoria-backend
sudo systemctl start aethoria-frontend

# Status prüfen
sudo systemctl status aethoria-backend
sudo systemctl status aethoria-frontend

# Logs anschauen
sudo journalctl -u aethoria-backend -f
# (Ctrl+C zum Beenden)
```

---

### Schritt 8: Nginx als Reverse Proxy konfigurieren

```bash
sudo tee /etc/nginx/sites-available/aethoria > /dev/null << 'EOF'
server {
    listen 80;
    server_name deine-domain.de www.deine-domain.de;  # ⚠️ ÄNDERE DIES!
    # ODER für IP-only: server_name DEINE_SERVER_IP;

    # Logs
    access_log /var/log/nginx/aethoria_access.log;
    error_log /var/log/nginx/aethoria_error.log;

    # Backend API (wichtig: /api prefix!)
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend (React)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # React Router - alle Routen zum Frontend
        try_files $uri $uri/ /index.html;
    }

    # Optional: Größere Upload-Limits (falls du später File-Uploads brauchst)
    client_max_body_size 10M;
}
EOF

# Aktiviere die Seite
sudo ln -sf /etc/nginx/sites-available/aethoria /etc/nginx/sites-enabled/

# Entferne default Seite
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx config testen
sudo nginx -t

# Nginx neustarten
sudo systemctl restart nginx

echo "✅ Nginx konfiguriert!"
```

---

### Schritt 9: SSL mit Let's Encrypt (Optional, aber empfohlen)

**Nur wenn du eine Domain hast:**

```bash
# Certbot installieren
sudo apt install certbot python3-certbot-nginx -y

# SSL-Zertifikat erstellen (automatisch!)
sudo certbot --nginx -d deine-domain.de -d www.deine-domain.de

# Certbot fragt nach E-Mail und Bestätigung, dann konfiguriert es automatisch SSL!

# Auto-Renewal einrichten (läuft automatisch)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo "✅ SSL aktiviert! Deine Seite läuft jetzt auf HTTPS!"
```

---

### Schritt 10: Firewall konfigurieren

```bash
# UFW Firewall aktivieren
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

echo "✅ Firewall konfiguriert!"
```

---

### Schritt 11: Finale Tests

```bash
# Prüfe Services
sudo systemctl status aethoria-backend aethoria-frontend nginx mongodb

# Test Backend direkt
curl http://localhost:8001/api/landing

# Test über Nginx
curl http://deine-domain.de/api/landing
# ODER: curl http://DEINE_SERVER_IP/api/landing

# Test Frontend
curl http://deine-domain.de/

echo "✅ Alles läuft!"
```

---

## Option 2: Docker Deployment (Einfacher)

Falls du Docker bevorzugst, erstelle ich dir eine Docker-Compose-Konfiguration:

**Vorteile:**
- ✅ Einfacher zu deployen
- ✅ Isolierte Umgebung
- ✅ Einfach zu aktualisieren

**Nachteile:**
- ⚠️ Etwas höherer Ressourcen-Verbrauch
- ⚠️ Zusätzliche Docker-Layer

Soll ich dir die Docker-Version auch erstellen?

---

## Wartung & Management

### Services steuern:

```bash
# Backend neustarten
sudo systemctl restart aethoria-backend

# Frontend neustarten
sudo systemctl restart aethoria-frontend

# Logs anschauen
sudo journalctl -u aethoria-backend -n 100 -f
sudo tail -f /var/log/aethoria/backend.log
```

### App updaten:

```bash
# 1. Neue Version hochladen (rsync/scp)
rsync -avz /lokaler/pfad/ root@server:/opt/aethoria/

# 2. Backend dependencies updaten (falls nötig)
cd /opt/aethoria/backend
source venv/bin/activate
pip install -r requirements.txt

# 3. Frontend neu bauen
cd /opt/aethoria/frontend
yarn install
yarn build

# 4. Services neustarten
sudo systemctl restart aethoria-backend aethoria-frontend
```

### Backup erstellen:

```bash
# MongoDB Backup
mongodump --db aethoria --out /backups/mongodb-$(date +%Y%m%d)

# Code Backup
tar -czf /backups/aethoria-code-$(date +%Y%m%d).tar.gz /opt/aethoria
```

---

## Troubleshooting

### Backend startet nicht:

```bash
# Prüfe Logs
sudo journalctl -u aethoria-backend -n 50

# Prüfe Permissions
sudo chown -R www-data:www-data /opt/aethoria

# Teste manuell
cd /opt/aethoria/backend
source venv/bin/activate
python3 server.py
```

### Frontend lädt nicht:

```bash
# Prüfe Nginx config
sudo nginx -t

# Prüfe Frontend Service
sudo systemctl status aethoria-frontend

# Prüfe Build
ls -la /opt/aethoria/frontend/build/
```

### MongoDB Connection Fehler:

```bash
# Prüfe ob MongoDB läuft
sudo systemctl status mongodb

# Prüfe Connection
mongosh
# Sollte eine Verbindung öffnen

# Prüfe .env MONGO_URL
cat /opt/aethoria/backend/.env
```

---

## Performance-Optimierung

### PM2 statt systemd (für besseres Process-Management):

```bash
# PM2 installieren
sudo npm install -g pm2

# Backend mit PM2 starten
cd /opt/aethoria/backend
source venv/bin/activate
pm2 start server.py --name aethoria-backend --interpreter python3

# Frontend mit PM2
pm2 start "serve -s build -l 3000" --name aethoria-frontend

# Auto-Start bei Reboot
pm2 startup
pm2 save
```

---

## Quick Commands

```bash
# Status checken
sudo systemctl status aethoria-backend aethoria-frontend nginx mongodb

# Alles neustarten
sudo systemctl restart aethoria-backend aethoria-frontend nginx

# Logs live anschauen
sudo tail -f /var/log/aethoria/*.log

# Traffic monitoring
sudo tail -f /var/log/nginx/aethoria_access.log
```

---

## Nächste Schritte nach Deployment

1. ✅ Teste die Seite in deinem Browser: `http://deine-domain.de`
2. ✅ Registriere einen Test-Account
3. ✅ Spiele ein paar Runden
4. ✅ Prüfe die Logs auf Fehler
5. ✅ Optional: Aktiviere die Game-Bots mit `/opt/aethoria/start_bots.sh`

---

## Support

**Häufige Probleme:**

| Problem | Lösung |
|---------|--------|
| 502 Bad Gateway | Backend läuft nicht - prüfe `systemctl status aethoria-backend` |
| API 404 | Nginx-Config falsch - prüfe `/api/` routing |
| Blank page | Frontend build fehlt - prüfe `frontend/build/` existiert |
| DB Connection error | MongoDB läuft nicht - `sudo systemctl start mongodb` |

**MongoDB Standard-URL (ohne Auth):**
```
MONGO_URL=mongodb://localhost:27017/aethoria
```

**MongoDB mit Auth:**
```
MONGO_URL=mongodb://aethoria_user:DEIN_PASSWORT@localhost:27017/aethoria
```
