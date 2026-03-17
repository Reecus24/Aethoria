#!/bin/bash
# Export-Script: Erstellt ein deployment-ready Package
# Erstellt: aethoria-deploy.tar.gz

set -e

echo "📦 Erstelle Deployment-Package..."

EXPORT_DIR="/tmp/aethoria-export"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="aethoria-deploy-${TIMESTAMP}.tar.gz"

# Cleanup old export
rm -rf $EXPORT_DIR
mkdir -p $EXPORT_DIR

echo "📁 Kopiere Dateien..."

# Backend
mkdir -p $EXPORT_DIR/backend
cp /app/backend/server.py $EXPORT_DIR/backend/
cp /app/backend/requirements.txt $EXPORT_DIR/backend/
cp /app/backend/Dockerfile $EXPORT_DIR/backend/
cp /app/backend/.env $EXPORT_DIR/backend/.env.example  # Als Beispiel

# Frontend
mkdir -p $EXPORT_DIR/frontend/src
cp -r /app/frontend/src/* $EXPORT_DIR/frontend/src/
cp -r /app/frontend/public $EXPORT_DIR/frontend/ 2>/dev/null || true
cp /app/frontend/package.json $EXPORT_DIR/frontend/
cp /app/frontend/yarn.lock $EXPORT_DIR/frontend/ 2>/dev/null || true
cp /app/frontend/Dockerfile $EXPORT_DIR/frontend/
cp /app/frontend/.env $EXPORT_DIR/frontend/.env.example

# Deployment configs
cp /app/docker-compose.yml $EXPORT_DIR/
cp /app/nginx.conf $EXPORT_DIR/
cp /app/.env.example $EXPORT_DIR/

# Guides
cp /app/DEPLOYMENT_GUIDE.md $EXPORT_DIR/
cp /app/DOCKER_DEPLOYMENT.md $EXPORT_DIR/
cp /app/QUICK_DEPLOY.md $EXPORT_DIR/README.md  # Quick Deploy als Haupt-README

# Scripts
cp /app/deploy_to_hetzner.sh $EXPORT_DIR/
cp /app/start_bots.sh $EXPORT_DIR/
cp /app/game_bot_quick.py $EXPORT_DIR/

# Design & Docs
cp /app/design_guidelines.md $EXPORT_DIR/ 2>/dev/null || true
cp /app/balancing_analysis.md $EXPORT_DIR/ 2>/dev/null || true

echo "🗜️  Erstelle Archive..."

cd /tmp
tar -czf $ARCHIVE_NAME aethoria-export/

# Move to app directory
mv $ARCHIVE_NAME /app/

# Cleanup
rm -rf $EXPORT_DIR

echo ""
echo "✅ Package erstellt!"
echo "📦 Datei: /app/$ARCHIVE_NAME"
echo ""
echo "🚀 Nächste Schritte:"
echo "   1. Download: /app/$ARCHIVE_NAME"
echo "   2. Auf deinen Server laden:"
echo "      scp /app/$ARCHIVE_NAME root@DEINE_SERVER_IP:/tmp/"
echo "   3. Auf dem Server entpacken:"
echo "      cd /opt && tar -xzf /tmp/$ARCHIVE_NAME"
echo "      mv aethoria-export aethoria"
echo "   4. README.md im Verzeichnis folgen"
echo ""
