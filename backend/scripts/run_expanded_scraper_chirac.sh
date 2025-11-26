#!/bin/bash
#
# Run Expanded AI Conflict Scraper for Chirac Region
# Coverage: 2,500 years (500 BC - 2024 AD), 100km radius
#
# Expected output: 90-170 conflicts
# Cost: ~$2-3 (Claude API)
# Time: 4-8 hours
#

set -e

echo "=================================="
echo "EXPANDED CONFLICT SCRAPER"
echo "2,500 Years of History (500 BC - 2024 AD)"
echo "=================================="
echo ""
echo "Location: Chirac, Charente"
echo "Coordinates: 45.9164°N, 0.6542°E"
echo "Radius: 100km"
echo ""
echo "Major sites covered:"
echo "  - Cassinomagus (Chassenon)"
echo "  - Angoulême (Iculisma)"
echo "  - Confolens"
echo "  - Rochechouart"
echo "  - Chabanais"
echo ""
echo "Historical periods (14 total):"
echo "  1. Gallic Tribes Era (500-58 BC)"
echo "  2. Gallic Wars (58-50 BC)"
echo "  3. Roman Gaul (50 BC - 410 AD) ⭐ Cassinomagus"
echo "  4. Late Antiquity (410-800 AD)"
echo "  5. Early Medieval (800-1000)"
echo "  6. High Medieval (1000-1337)"
echo "  7. Hundred Years War (1337-1453)"
echo "  8. Wars of Religion (1562-1598)"
echo "  9. 17th Century (1600-1700)"
echo "  10. French Revolution (1789-1799)"
echo "  11. Napoleonic Era (1799-1815)"
echo "  12. 19th Century (1815-1914)"
echo "  13. World War I (1914-1918)"
echo "  14. World War II (1939-1945)"
echo ""
echo "=================================="
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Check for .env file
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Create backend/.env with:"
    echo "  GOOGLE_API_KEY=your_key"
    echo "  GOOGLE_CSE_ID=your_cse_id"
    echo "  ANTHROPIC_API_KEY=your_anthropic_key"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the expanded scraper
echo "Starting expanded scraper..."
echo ""

python app/scrapers/ai_conflict_scraper_expanded.py \
    --location "Chirac" \
    --department "Charente" \
    --region "Nouvelle-Aquitaine" \
    --lat 45.9164 \
    --lng 0.6542 \
    --radius 100 \
    --output "chirac_2500years_conflicts.json" \
    --delay 2.0

echo ""
echo "=================================="
echo "✅ SCRAPING COMPLETE!"
echo "=================================="
echo ""
echo "Output file: chirac_2500years_conflicts.json"
echo ""
echo "Next steps:"
echo "  1. Review the JSON output"
echo "  2. Import conflicts to database:"
echo "     python scripts/import_conflicts.py chirac_2500years_conflicts.json"
echo ""
