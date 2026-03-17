# 🧹 Hetzner Server komplett säubern

## ⚠️ WARNUNG - LIEST DIES ZUERST!

**Dieses Script löscht ALLES auf deinem Server:**
- ✅ Alle laufenden Services (Docker, systemd, PM2)
- ✅ Alle installierten Datenbanken und deren Daten
- ✅ Alle Webserver-Konfigurationen
- ✅ Alle Anwendungsdateien
- ✅ Alle Logs

**⚠️ BACKUP ERSTELLEN FALLS NÖTIG!**

Wenn du noch etwas vom alten Projekt brauchst:
```bash
# Backup erstellen
tar -czf /root/backup-$(date +%Y%m%d).tar.gz /opt /var/www /home

# Irgendwo sicher speichern (lokal downloaden)
scp root@DEINE_SERVER_IP:/root/backup-*.tar.gz ~/backups/
```

---

## 🚀 Automatisches Cleanup-Script

**Kopiere dieses Script und führe es aus:**

```bash
#!/bin/bash
# Komplettes Server-Cleanup Script
# Entfernt ALLES vom alten Projekt

set -e

echo "================================================"
echo "🧹 HETZNER SERVER - KOMPLETTES CLEANUP"
echo "================================================"
echo ""
echo "⚠️  WARNUNG: Dies löscht:"
echo "   • Alle Docker Container & Images"
echo "   • Alle Datenbanken (MySQL, PostgreSQL, MongoDB, Redis)"
echo "   • Alle Webserver (Apache, Nginx, Caddy)"
echo "   • Alle Node/Python Apps"
echo "   • Alle Logs und Configs"
echo ""
read -p "🔴 Wirklich ALLES löschen? (yes/no) " -r
echo
if [[ ! $REPLY == "yes" ]]; then
    echo "Abgebrochen. (Tipp: Tippe 'yes' zum Bestätigen)"
    exit 1
fi

echo ""
echo "🛑 Schritt 1: Alle laufenden Services stoppen..."

# Stoppe alle Docker Container
if command -v docker &> /dev/null; then
    echo "   Stoppe Docker-Container..."
    docker stop $(docker ps -aq) 2>/dev/null || true
    docker rm $(docker ps -aq) 2>/dev/null || true
fi

# Stoppe systemd services
echo "   Stoppe systemd Services..."
systemctl stop nginx apache2 caddy 2>/dev/null || true
systemctl stop mysql postgresql mongod redis-server 2>/dev/null || true
systemctl stop node* python* 2>/dev/null || true

# Stoppe PM2 processes
if command -v pm2 &> /dev/null; then
    echo "   Stoppe PM2 Prozesse..."
    pm2 kill 2>/dev/null || true
fi

# Stoppe alle python/node prozesse
pkill -9 python3 2>/dev/null || true
pkill -9 node 2>/dev/null || true

echo "✅ Alle Services gestoppt"

echo ""
echo "🗑️  Schritt 2: Software deinstallieren..."

# Deinstalliere Docker
if command -v docker &> /dev/null; then
    echo "   Entferne Docker..."
    apt remove --purge docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-buildx-plugin -y 2>/dev/null || true
    apt remove --purge docker.io docker-compose -y 2>/dev/null || true
    rm -rf /var/lib/docker
    rm -rf /var/lib/containerd
fi

# Deinstalliere Webserver
echo "   Entferne Webserver..."
apt remove --purge nginx nginx-common nginx-core -y 2>/dev/null || true
apt remove --purge apache2 apache2-utils -y 2>/dev/null || true
apt remove --purge caddy -y 2>/dev/null || true

# Deinstalliere Datenbanken
echo "   Entferne Datenbanken..."
apt remove --purge mysql-server mysql-client mysql-common -y 2>/dev/null || true
apt remove --purge postgresql postgresql-contrib -y 2>/dev/null || true
apt remove --purge mongodb-org mongodb-org-server -y 2>/dev/null || true
apt remove --purge redis-server redis-tools -y 2>/dev/null || true

# Deinstalliere Node.js & NPM
echo "   Entferne Node.js..."
apt remove --purge nodejs npm -y 2>/dev/null || true
rm -rf /usr/local/lib/node_modules
rm -rf /usr/local/bin/npm
rm -rf /usr/local/bin/node
rm -rf /usr/local/bin/yarn

# Deinstalliere PM2
npm uninstall -g pm2 2>/dev/null || true

# Autoremove
apt autoremove -y
apt autoclean -y

echo "✅ Software deinstalliert"

echo ""
echo "📁 Schritt 3: Dateien & Configs löschen..."

# Lösche App-Verzeichnisse
rm -rf /opt/* 2>/dev/null || true
rm -rf /var/www/* 2>/dev/null || true
rm -rf /srv/* 2>/dev/null || true
rm -rf /home/*/app 2>/dev/null || true
rm -rf /root/app 2>/dev/null || true

# Lösche Datenbank-Daten
rm -rf /var/lib/mysql
rm -rf /var/lib/postgresql
rm -rf /var/lib/mongodb
rm -rf /var/lib/redis

# Lösche Webserver-Configs
rm -rf /etc/nginx
rm -rf /etc/apache2
rm -rf /etc/caddy

# Lösche systemd service files
rm -f /etc/systemd/system/*app*.service 2>/dev/null || true
rm -f /etc/systemd/system/*api*.service 2>/dev/null || true
rm -f /etc/systemd/system/*frontend*.service 2>/dev/null || true
rm -f /etc/systemd/system/*backend*.service 2>/dev/null || true
systemctl daemon-reload

# Lösche Logs
rm -rf /var/log/nginx
rm -rf /var/log/apache2
rm -rf /var/log/mongodb
rm -rf /var/log/mysql
rm -rf /var/log/postgresql

# Lösche User-Verzeichnisse (nur App-bezogen)
rm -rf ~/.npm
rm -rf ~/.cache
rm -rf ~/.local/share/pnpm

echo "✅ Dateien gelöscht"

echo ""
echo "🔧 Schritt 4: System aufräumen..."

# Update Package-Listen
apt update

# Lösche verwaiste Packages
apt autoremove --purge -y
apt autoclean -y

# Clear temp files
rm -rf /tmp/*
rm -rf /var/tmp/*

echo "✅ System aufgeräumt"

echo ""
echo "👥 Schritt 5: User-Accounts prüfen..."

# Liste alle Non-System-User
echo "   Folgende User-Accounts existieren:"
awk -F: '$3 >= 1000 {print "   - " $1 " (UID: " $3 ")"}' /etc/passwd

echo ""
read -p "User-Accounts löschen? (meist nicht nötig) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   Lösche App-User..."
    userdel -r www-data 2>/dev/null || true
    # Füge hier weitere User hinzu falls nötig
fi

echo ""
echo "🔥 Schritt 6: Docker komplett entfernen (optional)..."

read -p "Auch Docker komplett löschen? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    apt remove --purge docker-ce docker-ce-cli containerd.io -y
    rm -rf /var/lib/docker
    rm -rf /etc/docker
    echo "✅ Docker entfernt"
fi

echo ""
echo "================================================"
echo "✅ SERVER IST JETZT KOMPLETT SAUBER!"
echo "================================================"
echo ""
echo "📊 Status:"
df -h | grep -E "Filesystem|/$"
echo ""
echo "💾 Freier Speicher:"
free -h
echo ""
echo "🎯 Nächste Schritte:"
echo "   1. Optional: Server neustarten (reboot)"
echo "   2. Deployment-Package hochladen"
echo "   3. Docker neu installieren"
echo "   4. App deployen!"
echo ""
```

**Speichere dies als `cleanup_server.sh` und führe es aus:**

```bash
# Auf dem Server
nano cleanup_server.sh
# Füge das Script oben ein, speichere mit Ctrl+X, Y, Enter

chmod +x cleanup_server.sh
sudo bash cleanup_server.sh
```

---

## 🎯 Schnelle manuelle Cleanup-Befehle

Falls du das Script nicht verwenden willst:

### 1. Docker komplett entfernen:

```bash
# Stoppe und lösche alle Container
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi $(docker images -q) -f

# Lösche Docker Volumes (DATENBANKEN!)
docker volume rm $(docker volume ls -q)

# Deinstalliere Docker
apt remove --purge docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
rm -rf /var/lib/docker
rm -rf /etc/docker
```

### 2. Alle Webserver entfernen:

```bash
# Nginx
systemctl stop nginx
apt remove --purge nginx* -y
rm -rf /etc/nginx
rm -rf /var/log/nginx

# Apache
systemctl stop apache2
apt remove --purge apache2* -y
rm -rf /etc/apache2
rm -rf /var/log/apache2

# Caddy
systemctl stop caddy
apt remove --purge caddy -y
rm -rf /etc/caddy
```

### 3. Alle Datenbanken entfernen:

```bash
# MySQL/MariaDB
systemctl stop mysql mariadb
apt remove --purge mysql* mariadb* -y
rm -rf /var/lib/mysql
rm -rf /etc/mysql

# PostgreSQL
systemctl stop postgresql
apt remove --purge postgresql* -y
rm -rf /var/lib/postgresql
rm -rf /etc/postgresql

# MongoDB
systemctl stop mongod
apt remove --purge mongodb-org* -y
rm -rf /var/lib/mongodb
rm -rf /etc/mongod.conf

# Redis
systemctl stop redis
apt remove --purge redis* -y
rm -rf /var/lib/redis
```

### 4. Node.js & Python komplett entfernen:

```bash
# Node.js
apt remove --purge nodejs npm -y
rm -rf /usr/local/lib/node_modules
rm -rf /usr/local/bin/npm
rm -rf /usr/local/bin/node
rm -rf /usr/local/bin/yarn
rm -rf ~/.npm
rm -rf ~/.yarn

# PM2 (falls installiert)
npm uninstall -g pm2 || true
pm2 kill || true

# Python pip packages (optional)
pip3 freeze | xargs pip3 uninstall -y || true
```

### 5. Alle App-Verzeichnisse löschen:

```bash
# Standard App-Locations
rm -rf /opt/*
rm -rf /var/www/*
rm -rf /srv/*
rm -rf /home/*/app
rm -rf ~/app
rm -rf ~/projects

# Versteckte Configs
rm -rf ~/.config/nginx
rm -rf ~/.config/pm2
```

### 6. Systemd Services aufräumen:

```bash
# Liste alle Custom-Services
systemctl list-unit-files | grep -v "^systemd\|^getty\|^dbus"

# Stoppe und deaktiviere alle Custom-Services
systemctl stop *.service
systemctl disable *.service

# Lösche Custom-Service-Dateien
rm -f /etc/systemd/system/*.service
rm -f /lib/systemd/system/*app*.service

# Reload systemd
systemctl daemon-reload
systemctl reset-failed
```

### 7. Logs löschen:

```bash
# Lösche alle App-Logs
rm -rf /var/log/nginx
rm -rf /var/log/apache2
rm -rf /var/log/mysql
rm -rf /var/log/postgresql
rm -rf /var/log/mongodb

# Journal logs
journalctl --vacuum-time=1d

# Temp files
rm -rf /tmp/*
rm -rf /var/tmp/*
```

### 8. System aufräumen:

```bash
# Orphaned packages entfernen
apt autoremove --purge -y
apt autoclean -y

# Package-Listen updaten
apt update
```

### 9. Firewall zurücksetzen:

```bash
# UFW Rules löschen
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp  # SSH nicht blockieren!
ufw --force enable
```

### 10. FERTIG! Server neustarten:

```bash
# Optional aber empfohlen
reboot
```

---

## 🎯 ODER: Der "Nuclear Option" One-Liner

**⚠️ EXTREM VORSICHTIG! Dies löscht ALLES (außer OS):**

```bash
# SSH in Server
ssh root@DEINE_SERVER_IP

# Kopiere und führe aus (COPY & PASTE):
sudo bash << 'CLEANUP_SCRIPT'
echo "🔴 Starting NUCLEAR CLEANUP..."

# Stop everything
systemctl stop nginx apache2 mysql postgresql mongod redis docker 2>/dev/null || true
docker stop $(docker ps -aq) 2>/dev/null || true
pkill -9 node 2>/dev/null || true
pkill -9 python3 2>/dev/null || true
pm2 kill 2>/dev/null || true

# Remove software
apt remove --purge nginx* apache2* mysql* postgresql* mongodb* redis* docker* nodejs npm caddy -y 2>/dev/null || true

# Delete data directories
rm -rf /opt/* /var/www/* /srv/* /home/*/app
rm -rf /var/lib/mysql /var/lib/postgresql /var/lib/mongodb /var/lib/redis /var/lib/docker
rm -rf /etc/nginx /etc/apache2 /etc/mysql /etc/postgresql

# Delete systemd services
rm -f /etc/systemd/system/*.service 2>/dev/null || true
systemctl daemon-reload

# Clean logs
rm -rf /var/log/nginx /var/log/apache2 /var/log/mysql /var/log/postgresql
journalctl --vacuum-time=1d

# Autoremove
apt autoremove --purge -y
apt autoclean -y

# Reset firewall
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22
ufw --force enable

echo ""
echo "✅ SERVER IST SAUBER!"
echo "💾 Freier Speicher:"
df -h / | tail -1
echo ""
echo "🔄 Server neustarten empfohlen: reboot"
CLEANUP_SCRIPT

# Server neustarten
read -p "Server jetzt neustarten? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    reboot
fi
```

---

## 🔍 Vor dem Cleanup: Check was läuft

**Finde heraus, was aktuell auf dem Server läuft:**

```bash
# Welche Services laufen?
systemctl list-units --type=service --state=running

# Welche Docker Container?
docker ps -a

# Welche Ports sind belegt?
netstat -tulpn | grep LISTEN
# ODER
ss -tulpn | grep LISTEN

# Welche Prozesse laufen?
ps aux | grep -E "node|python|nginx|apache|mysql|mongo"

# Speicherverbrauch
df -h
du -sh /opt/* /var/www/* 2>/dev/null
```

---

## 📋 Selektives Cleanup (wenn du nur bestimmte Dinge löschen willst)

### Nur Docker:
```bash
docker stop $(docker ps -aq) && docker rm $(docker ps -aq)
docker rmi $(docker images -q) -f
docker volume prune -f
docker system prune -a -f
```

### Nur Node.js Apps:
```bash
pkill -9 node
pm2 kill
rm -rf /opt/*/node_modules
rm -rf ~/*/node_modules
```

### Nur Datenbanken:
```bash
systemctl stop mysql postgresql mongod redis
apt remove --purge mysql* postgresql* mongodb* redis* -y
rm -rf /var/lib/mysql /var/lib/postgresql /var/lib/mongodb /var/lib/redis
```

### Nur Webserver-Configs:
```bash
systemctl stop nginx apache2
rm -rf /etc/nginx/sites-enabled/*
rm -rf /etc/nginx/sites-available/*
rm -rf /etc/apache2/sites-enabled/*
rm -rf /etc/apache2/sites-available/*
```

---

## ✅ Nach dem Cleanup

**Prüfe, dass der Server sauber ist:**

```bash
# Keine laufenden Container
docker ps  # Sollte leer sein (oder "command not found")

# Keine laufenden Web-Services
netstat -tulpn | grep -E ":80|:443|:8000|:3000"  # Sollte leer sein

# Freier Speicher
df -h /

# System ist ready
echo "✅ Server ist sauber und bereit für neues Deployment!"
```

**Jetzt kannst du das Aethoria-Deployment starten:**

1. Folge `COPY_PASTE_DEPLOY.md` aus dem Deployment-Package
2. Oder starte direkt mit Docker: `curl -fsSL https://get.docker.com | sh`

---

## 🆘 Falls etwas schief geht

### SSH funktioniert nicht mehr:
- **NICHT PANIKEN!** 
- Gehe zu Hetzner Cloud Console
- Öffne die "Console" (Browser-basiert)
- Logge dich ein und fixe das Problem

### Server ist zu voll:
```bash
# Finde große Dateien
du -sh /* | sort -hr | head -20
du -sh /var/lib/* | sort -hr | head -20

# Lösche große Log-Dateien
find /var/log -type f -size +100M -delete
```

### Firewall hat dich ausgesperrt:
```bash
# In Hetzner Console:
ufw disable
# Dann neu konfigurieren mit SSH erlaubt
```

---

## 🔄 Alternative: Server komplett neu aufsetzen

**Die EINFACHSTE Lösung - wenn alles zu chaotisch ist:**

1. Gehe zu **Hetzner Cloud Console**
2. Lösche den Server komplett
3. Erstelle einen **neuen Server**:
   - Image: **Ubuntu 24.04**
   - Type: CX22 oder besser (min. 2GB RAM)
   - Datacenter: Nürnberg (näher)
4. SSH-Key hinzufügen
5. Server erstellen
6. Deployment-Package hochladen und deployen!

**Vorteile:**
- ✅ 100% sauber, keine Reste
- ✅ Neueste Ubuntu-Version
- ✅ Keine versteckten Configs
- ✅ 5 Minuten Setup

---

## 💡 Empfehlung

**Für den saubersten Start:**

1. **Backup** vom alten Projekt (falls nötig)
2. **Server neu aufsetzen** in Hetzner Console (5 Minuten)
3. **Frischer Ubuntu Server** → direkt Aethoria deployen

Das ist **schneller und sauberer** als manuelles Cleanup!

Aber wenn du den existierenden Server behalten willst, nutze das Cleanup-Script oben. ☝️
