#!/bin/bash
# Quick command to populate the realm with bot activity
# Usage: bash /app/start_bots.sh

echo "🤖 Starting 5 AI players..."
cd /app && python3 game_bot_quick.py
echo "✅ Bot session complete!"
echo "🌐 Check the landing page: https://dragon-quest-46.preview.emergentagent.com"
