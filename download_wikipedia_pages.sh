#!/bin/bash
# Download Wikipedia battle list pages
# Usage: ./download_wikipedia_pages.sh

set -e

# Create output directory
mkdir -p wikipedia_html

# Array of URLs to download
urls=(
    "https://en.wikipedia.org/wiki/List_of_battles_before_301"
    "https://en.wikipedia.org/wiki/List_of_battles_301–1300"
    "https://en.wikipedia.org/wiki/List_of_battles_1301–1400"
    "https://en.wikipedia.org/wiki/List_of_battles_1401–1500"
    "https://en.wikipedia.org/wiki/List_of_battles_1501–1600"
    "https://en.wikipedia.org/wiki/List_of_battles_1601–1700"
    "https://en.wikipedia.org/wiki/List_of_battles_1701–1800"
    "https://en.wikipedia.org/wiki/List_of_battles_1801–1900"
    "https://en.wikipedia.org/wiki/List_of_battles_1901–2000"
)

echo "Downloading Wikipedia battle list pages..."
echo "=========================================="
echo ""

count=1
total=${#urls[@]}

for url in "${urls[@]}"; do
    # Extract filename from URL
    filename=$(echo "$url" | sed 's/.*\///' | sed 's/–/-/g')
    output="wikipedia_html/${filename}.html"

    echo "[$count/$total] Downloading: $filename"

    # Download with wget
    wget -q --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
         --timeout=30 \
         -O "$output" \
         "$url" 2>/dev/null || {
        echo "  ✗ Failed to download"
        continue
    }

    echo "  ✓ Saved to: $output"

    # Be respectful - wait between requests
    if [ $count -lt $total ]; then
        sleep 2
    fi

    ((count++))
done

echo ""
echo "✓ Download complete!"
echo "✓ Files saved in: wikipedia_html/"
echo ""
echo "Next step: Parse the HTML files with:"
echo "  python parse_local_html.py --directory wikipedia_html/ --output battles.csv"
