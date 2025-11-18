#!/bin/bash

# Script to fix Pi5 pull issue with logs/futterkarre.log
echo "🔧 Fixing Pi5 Git Pull Issue..."

# Commands for Pi5 to execute
echo "Execute these commands on your Pi5:"
echo ""
echo "cd /home/daniel/Futterkarre"
echo ""
echo "# Remove log file from git tracking (but keep the file)"
echo "git rm --cached logs/futterkarre.log"
echo ""
echo "# Commit the removal"
echo "git commit -m '🗂️ Remove log file from version control'"
echo ""
echo "# Now pull the latest changes"
echo "git pull origin main"
echo ""
echo "# Push the fix back"
echo "git push origin main"
echo ""
echo "✅ Done! The log file will no longer be tracked by Git."