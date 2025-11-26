#!/usr/bin/env python3
"""
Week 0 AI Validation Test for SPV Treasure Map Identity Engine

Tests whether Claude Sonnet 4 can generate quality identity themes
from village data before building infrastructure.

Expected cost: ~$0.05-0.10 per test
Expected time: 30 seconds
"""

import json
import os
from datetime import datetime
from anthropic import Anthropic

def load_test_data():
    """Load Chirac test data from JSON file"""
    with open('chirac_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def build_analysis_prompt(village_data):
    """Build comprehensive prompt for identity analysis"""
    
    prompt = f"""You are analyzing the village of {village_data['village_name']} to identify its core identity themes.

VILLAGE DATA:

Basic Info:
- Population: {village_data['basic_info']['population']}
- Area: {village_data['basic_info']['area_km2']} km²
- Type: {village_data['basic_info']['commune_type']}

Environmental Assets:
- {village_data['environmental_assets']['ponds']['count']} ponds ({village_data['environmental_assets']['ponds']['total_area_hectares']} hectares total)
- Pond density: {village_data['environmental_assets']['ponds']['density_per_km2']} per km²
- {', '.join(village_data['environmental_assets']['rivers'])}
- {village_data['environmental_assets']['forests']['area_hectares']} hectares of {village_data['environmental_assets']['forests']['type']} forest

Historical Conflicts:
- Total: {village_data['historical_conflicts']['total_count']} conflicts over {village_data['historical_conflicts']['time_span']}
- Major event: {village_data['historical_conflicts']['major_events'][0]['name']} ({village_data['historical_conflicts']['major_events'][0]['date']})
  {village_data['historical_conflicts']['major_events'][0]['description']}

Industrial Heritage:
- Forges de l'Âge: {village_data['industrial_heritage']['forges_de_lage']['period']}
- Activities: {', '.join(village_data['industrial_heritage']['forges_de_lage']['activities'])}
- Scale: {village_data['industrial_heritage']['forges_de_lage']['scale']}

Economic Situation:
- {village_data['economic_situation']['farms']['count']} farms ({village_data['economic_situation']['farms']['trend']})
- Tourism: {village_data['economic_situation']['tourism']['infrastructure']} infrastructure
- Fishing: {village_data['economic_situation']['fishing']['commercial']} commercial operations (despite {village_data['environmental_assets']['ponds']['count']} ponds!)

Demographics:
- Population change: {village_data['demographics']['population_history']['1945']} (1945) → {village_data['demographics']['population_history']['2024']} (2024)
- Trend: {village_data['demographics']['age_structure']}

YOUR TASK:

Identify 2-3 CORE IDENTITY THEMES for this village.

CRITICAL REQUIREMENTS:
1. Look for CONNECTIONS between assets, not just listing them
   Example: "15 ponds + River Vienne + no fish farming = 'Village of Living Waters' theme"
   
2. Avoid GENERIC themes like:
   ❌ "Historic Village"
   ❌ "Natural Beauty" 
   ❌ "Rich Heritage"
   
3. Each theme MUST have:
   - Memorable name (3-5 words)
   - Confidence score (0-100, be honest)
   - Supporting evidence (which specific assets support this?)
   - Why it matters (how does this shape village identity?)
   - 2-3 concrete projects with:
     * Timeline (realistic months/years)
     * Budget (realistic euros)
     * Partners (real organizations: INRAE, departmental tourism, UNESCO, etc.)
     * Funding sources (LEADER, FEADER, departmental grants, etc.)
     * First steps (specific enough to execute tomorrow)

OUTPUT FORMAT (JSON only):
{{
  "themes": [
    {{
      "name": "Theme name here",
      "confidence": 85,
      "supporting_evidence": ["Specific asset 1", "Specific asset 2"],
      "why_it_matters": "One paragraph explanation",
      "projects": [
        {{
          "name": "Project name",
          "description": "What would be done",
          "timeline": "6-12 months",
          "budget": "€5,000-15,000",
          "partners": ["Organization 1", "Organization 2"],
          "funding_sources": ["LEADER", "Regional grants"],
          "first_steps": ["Specific action 1", "Specific action 2"]
        }}
      ]
    }}
  ]
}}

Respond with ONLY valid JSON. No markdown, no explanation, just the JSON object.
"""
    
    return prompt

def call_claude_api(prompt):
    """Call Claude Sonnet 4 API with the analysis prompt"""
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set!")
    
    client = Anthropic(api_key=api_key)
    
    print("Calling Claude API...")
    print(f"Model: claude-sonnet-4-20250514")
    print(f"Prompt length: {len(prompt)} characters\n")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Calculate cost
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    input_cost = (input_tokens / 1_000_000) * 3  # $3 per M tokens
    output_cost = (output_tokens / 1_000_000) * 15  # $15 per M tokens
    total_cost = input_cost + output_cost
    
    print(f"✅ API call successful!")
    print(f"Input tokens: {input_tokens:,}")
    print(f"Output tokens: {output_tokens:,}")
    print(f"Cost: ${total_cost:.4f}\n")
    
    return response.content[0].text, total_cost

def parse_response(response_text):
    """Parse Claude's JSON response, handling markdown if present"""
    
    # Strip markdown code blocks if present
    text = response_text.strip()
    if text.startswith('```json'):
        text = text[7:]  # Remove ```json
    if text.startswith('```'):
        text = text[3:]   # Remove ```
    if text.endswith('```'):
        text = text[:-3]  # Remove trailing ```
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        print(f"Response was:\n{response_text}")
        raise

def save_results(village_data, analysis, cost):
    """Save test results to file"""
    
    os.makedirs('test_results', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"test_results/chirac_analysis_{timestamp}.json"
    
    results = {
        "timestamp": timestamp,
        "village": village_data['village_name'],
        "cost": cost,
        "analysis": analysis
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {filename}\n")
    return filename

def display_results(analysis):
    """Display results in readable format"""
    
    print("=" * 80)
    print("IDENTITY ANALYSIS RESULTS")
    print("=" * 80)
    print()
    
    for i, theme in enumerate(analysis['themes'], 1):
        print(f"THEME {i}: {theme['name']}")
        print(f"Confidence: {theme['confidence']}/100")
        print()
        
        print("Supporting Evidence:")
        for evidence in theme['supporting_evidence']:
            print(f"  • {evidence}")
        print()
        
        print(f"Why It Matters:")
        print(f"  {theme['why_it_matters']}")
        print()
        
        print("Proposed Projects:")
        for j, project in enumerate(theme['projects'], 1):
            print(f"  {j}. {project['name']}")
            print(f"     {project['description']}")
            print(f"     Timeline: {project['timeline']}")
            print(f"     Budget: {project['budget']}")
            print(f"     Partners: {', '.join(project['partners'])}")
            print(f"     Funding: {', '.join(project['funding_sources'])}")
            print(f"     First steps:")
            for step in project['first_steps']:
                print(f"       - {step}")
            print()
        
        print("-" * 80)
        print()

def main():
    """Run the Week 0 validation test"""
    
    print("🧪 SPV Treasure Map - Week 0 AI Validation Test")
    print("=" * 80)
    print()
    
    # Load test data
    print("📂 Loading Chirac test data...")
    village_data = load_test_data()
    print(f"✅ Loaded data for {village_data['village_name']}\n")
    
    # Build prompt
    print("📝 Building analysis prompt...")
    prompt = build_analysis_prompt(village_data)
    print("✅ Prompt ready\n")
    
    # Call API
    response_text, cost = call_claude_api(prompt)
    
    # Parse response
    print("🔍 Parsing response...")
    analysis = parse_response(response_text)
    print(f"✅ Found {len(analysis['themes'])} themes\n")
    
    # Save results
    filename = save_results(village_data, analysis, cost)
    
    # Display results
    display_results(analysis)
    
    # Final instructions
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Review the themes above")
    print("2. Fill out EVALUATION_WORKSHEET.md")
    print("3. Make GO/NO-GO decision:")
    print("   ✅ 3+ criteria met → Proceed to Week 1")
    print("   ⚠️  2 criteria met → Iterate on prompts")
    print("   ❌ 0-1 criteria met → Reconsider strategy")
    print()
    print(f"4. Detailed results saved in: {filename}")
    print()

if __name__ == '__main__':
    main()
