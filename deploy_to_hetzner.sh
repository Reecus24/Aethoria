#!/bin/bash
# Automatisches Deployment-Script für Hetzner Server
# Usage: bash deploy_to_hetzner.sh

set -e  # Exit on error

echo "================================================"
echo "🚀 Realm of Aethoria - Hetzner Deployment"
echo "================================================"
echo ""

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Bitte als root ausführen: sudo bash deploy_to_hetzner.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNUNG: Dieses Script wird:${NC}"
echo "   1. Alte Services stoppen"
echo "   2. Dependencies installieren"
echo "   3. MongoDB einrichten"
echo "   4. Die App installieren"
echo "   5. Systemd services erstellen"
echo "   6. Nginx konfigurieren"
echo ""
read -p "Fortfahren? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Abgebrochen."
    exit 1
fi

# Variablen (anpassen!)
APP_DIR="/opt/aethoria"
DOMAIN="deine-domain.de"  # Ändere dies zu deiner Domain oder IP!

echo ""
echo "📦 Schritt 1: System-Dependencies installieren..."

# Update system
apt update && apt upgrade -y

# Install Python
apt install python3 python3-pip python3-venv -y

# Install Node.js 20.x
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install nodejs -y
fi

# Install Yarn
npm install -g yarn

# Install MongoDB
if ! command -v mongod &> /dev/null; then
    curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
       gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
    
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
    tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    
    apt update
    apt install mongodb-org -y
fi

# Install Nginx
apt install nginx -y

echo -e "${GREEN}✅ Dependencies installiert${NC}"

echo ""
echo "🗄️  Schritt 2: MongoDB starten..."

systemctl start mongod
systemctl enable mongod
sleep 3

# Test MongoDB
if mongosh --eval "db.version()" &> /dev/null; then
    echo -e "${GREEN}✅ MongoDB läuft${NC}"
else
    echo -e "${RED}❌ MongoDB fehler${NC}"
    exit 1
fi

echo ""
echo "📁 Schritt 3: App-Verzeichnis vorbereiten..."

mkdir -p $APP_DIR
mkdir -p /var/log/aethoria
chown -R www-data:www-data /var/log/aethoria

echo -e "${GREEN}✅ Verzeichnisse erstellt${NC}"

echo ""
echo -e "${YELLOW}📋 Schritt 4: App-Dateien kopieren${NC}"
echo ""
echo "WICHTIG: Du musst jetzt die App-Dateien nach $APP_DIR kopieren!"
echo ""
echo "Von deinem lokalen Rechner:"
echo "  rsync -avz /pfad/zu/app/backend/ root@$HOSTNAME:$APP_DIR/backend/"
echo "  rsync -avz /pfad/zu/app/frontend/ root@$HOSTNAME:$APP_DIR/frontend/"
echo ""
read -p "Dateien kopiert? Drücke ENTER wenn fertig..."

echo ""
echo "🐍 Schritt 5: Backend einrichten..."

cd $APP_DIR/backend

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    cat > .env << EOF_ENV
MONGO_URL=mongodb://localhost:27017/aethoria
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=30
EOF_ENV
    echo -e "${GREEN}✅ Backend .env erstellt${NC}"
fi

deactivate

echo ""
echo "⚛️  Schritt 6: Frontend bauen..."

cd $APP_DIR/frontend

# Install dependencies
yarn install

# Create production .env
cat > .env.production << EOF_ENV
REACT_APP_BACKEND_URL=https://$DOMAIN
EOF_ENV

# Build
yarn build

if [ -d "build" ]; then
    echo -e "${GREEN}✅ Frontend gebaut${NC}"
else
    echo -e "${RED}❌ Frontend build fehlgeschlagen${NC}"
    exit 1
fi

echo ""
echo "🔧 Schritt 7: Systemd Services erstellen..."

# Backend Service
cat > /etc/systemd/system/aethoria-backend.service << 'EOF_SERVICE'
[Unit]
Description=Realm of Aethoria Backend
After=network.target mongod.service
Requires=mongod.service

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
EOF_SERVICE

# Frontend Service
cat > /etc/systemd/system/aethoria-frontend.service << 'EOF_SERVICE'
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
EOF_SERVICE

# Install serve
yarn global add serve

# Fix permissions
chown -R www-data:www-data $APP_DIR

# Reload and start
systemctl daemon-reload
systemctl enable aethoria-backend aethoria-frontend
systemctl start aethoria-backend aethoria-frontend

sleep 5

echo -e "${GREEN}✅ Services gestartet${NC}"

echo ""
echo "🌐 Schritt 8: Nginx konfigurieren..."

# Nginx config already created in previous step
systemctl restart nginx

echo ""
echo "================================================"
echo -e "${GREEN}✅ DEPLOYMENT KOMPLETT!${NC}"
echo "================================================"
echo ""
echo "🌐 Deine App läuft auf:"
echo "   http://$DOMAIN"
echo "   oder http://$(hostname -I | awk '{print $1}')"
echo ""
echo "📊 Services prüfen:"
echo "   sudo systemctl status aethoria-backend"
echo "   sudo systemctl status aethoria-frontend"
echo ""
echo "📝 Logs anschauen:"
echo "   sudo tail -f /var/log/aethoria/backend.log"
echo ""
echo "🔐 Für SSL (falls Domain vorhanden):"
echo "   sudo certbot --nginx -d $DOMAIN"
echo ""
