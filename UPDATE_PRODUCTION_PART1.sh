#!/bin/bash
# Part 1: Update Backend + 3 Frontend Components
# Run from /opt/aethoria

cd /opt/aethoria || exit 1

echo "🔧 Applying Bug Fixes - Part 1/2..."

# Backup
BACKUP_DIR="backups/fixes_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR/{backend,frontend/src/{components,pages}}
cp backend/server.py $BACKUP_DIR/backend/ 2>/dev/null
cp frontend/src/components/*.jsx $BACKUP_DIR/frontend/src/components/ 2>/dev/null
cp frontend/src/pages/*.jsx $BACKUP_DIR/frontend/src/pages/ 2>/dev/null
echo "✅ Backup: $BACKUP_DIR"

echo "📝 Updating AuthModals.jsx..."
