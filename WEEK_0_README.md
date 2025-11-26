# Week 0: AI Validation Test

**Purpose**: Prove the identity engine works BEFORE building infrastructure

**Time**: 30 minutes  
**Cost**: ~$0.05-0.10  
**Critical**: If AI fails, better to know now than after 8 weeks of building

---

## What You're Testing

Can Claude Sonnet 4 generate **quality identity themes** from village data that:
- Feel unique (not generic)
- Are evidence-based
- Include actionable projects
- Would impress a commune mayor

---

## Files You Need

Download these 3 files from Claude:
1. `chirac_data.json` - Test data
2. `test_identity_analysis.py` - Test script  
3. `EVALUATION_WORKSHEET.md` - Evaluation checklist

---

## How to Run (30 minutes total)

### Step 1: Setup (5 mins)

```bash
# Navigate to your project
cd ~/Documents/treasure-hunting/claude-test

# Activate venv
source backend/venv/bin/activate

# Install Anthropic SDK (if not already done)
pip install anthropic

# Set your API key (get from: https://console.anthropic.com/)
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

### Step 2: Run Test (30 seconds)

```bash
# Make sure chirac_data.json is in same directory as script
python test_identity_analysis.py
```

Expected output:
```
🧪 SPV Treasure Map - Week 0 AI Validation Test
================================================================================

📂 Loading Chirac test data...
✅ Loaded data for Chirac

📝 Building analysis prompt...
✅ Prompt ready

Calling Claude API...
Model: claude-sonnet-4-20250514
Prompt length: 2847 characters

✅ API call successful!
Input tokens: 1,234
Output tokens: 2,456
Cost: $0.0407

🔍 Parsing response...
✅ Found 3 themes

💾 Results saved to: test_results/chirac_analysis_20241125_140530.json

================================================================================
IDENTITY ANALYSIS RESULTS
================================================================================

THEME 1: Village of Living Waters
Confidence: 87/100

Supporting Evidence:
  • 15 ponds (exceptional 0.58 per km² density)
  • River Vienne borders
  • Zero commercial fishing despite water resources
  • 50 hectares of oak forest (water retention)

Why It Matters:
  This village sits on exceptional water resources that shaped its identity for
  centuries but are now unexploited. The pond density is 3x regional average,
  suggesting historical importance (mills, fish farming, irrigation). Today
  this represents both identity and economic opportunity.

Proposed Projects:
  1. Sustainable Pond Fish Farming Initiative
     Pilot project to revive traditional fish farming with modern sustainable practices
     Timeline: 12-18 months
     Budget: €15,000-25,000
     Partners: INRAE (aquaculture research), Charente Fisheries Federation
     Funding: LEADER, FEADER (rural development funds)
     First steps:
       - Contact INRAE Nouvelle-Aquitaine aquaculture department
       - Water quality testing on 3 pilot ponds
       - Meet with Charente Fisheries Federation for technical guidance
       - Apply for LEADER exploratory grant (€5,000)

  [... more projects ...]
```

### Step 3: Evaluate (20 mins)

Open `EVALUATION_WORKSHEET.md` and rate each theme:

For each theme, score 1-10 on:
- **Memorable?** (catchy name, sticks in mind)
- **Unique?** (specific to Chirac, not generic)
- **Evidence-based?** (clear connection to assets)
- **Actionable?** (projects feel realistic)
- **Compelling?** (would work for mayor pitch)

Total: __/50 → __/10

For each project, check:
- [ ] Could start tomorrow?
- [ ] Budget realistic?
- [ ] Partners are real organizations?
- [ ] First steps specific enough?

Total checks: __/5

### Step 4: Decision (5 mins)

Count how many criteria are met (need 3+ to proceed):

- [ ] At least 1 theme scores 8+/10
- [ ] At least 2 projects are actionable (4+/5)
- [ ] Themes feel unique (not generic)
- [ ] Cost is reasonable (<$0.20)
- [ ] You'd show this to Chirac mayor

**Total criteria met: __/5**

---

## What Good Looks Like

### ✅ Good Theme Example
```
Name: "Village of Living Waters - Dormant Aquaculture Hub"
Confidence: 87/100
Evidence: 15 ponds (0.58/km², 3x regional average) + River Vienne + 
          zero commercial fishing + historical forge water management
Why: Water shaped identity for centuries (mills, forges, irrigation) but 
     economic potential now dormant. Revival = identity + jobs.
Projects: 
  1. Pilot sustainable pond fish farming (€15K, 12mo, INRAE partner)
  2. Educational "Water Trail" linking ponds + river + forge ruins
  3. Annual "Water Festival" celebrating aquatic heritage
```

**Why it works**:
- Name is specific and memorable
- Evidence shows CONNECTIONS (not just listing)
- Projects are actionable with real partners
- Budget realistic
- You could pitch this tomorrow

### ❌ Bad Theme Example
```
Name: "Historic Village"
Confidence: 90/100
Evidence: Has history, old buildings
Why: History is important
Projects:
  1. Make website about history
  2. Put up some signs
  3. Tell people about history
```

**Why it fails**:
- Generic (every village has "history")
- No specific evidence
- Projects vague, no partners, no budget
- Couldn't pitch this to mayor

---

## Expected Outcomes

### ✅ Best Case: GO (3+ criteria met)
**What happened**: AI produced 2-3 strong themes with actionable projects

**Next steps**: 
- Week 1: Build multi-tenancy database
- Week 2-3: Flexible POI system
- Week 4-8: Identity engine infrastructure
- Confident the AI will work at scale

**Timeline**: 16-20 weeks to first paying customer

---

### ⚠️ Medium Case: ITERATE (2 criteria met)
**What happened**: Themes are OK but projects weak, or vice versa

**Next steps**:
- Refine prompts (more specific examples)
- Try different framing
- Test with another village (Manot or Exideuil)
- Retest (cost: another $0.05-0.10)

**Timeline**: +1-2 weeks for iteration, then proceed

---

### ❌ Worst Case: STOP (0-1 criteria met)
**What happened**: Themes generic, projects unrealistic, not compelling

**Decision**: Reconsider identity engine strategy

**Options**:
1. **Simplify**: Manual themes (you write them) + AI just for details
2. **Pivot**: Focus on QR codes + routes only (no identity engine)
3. **Different AI**: Try GPT-4o or Claude Opus (more expensive)
4. **Hybrid**: Start with 10 templates, let AI customize

**Cost saved**: $0.50 test vs 8 weeks of building infrastructure

---

## Cost Breakdown

**This test**:
- Input: ~1,500 tokens × $3/M = $0.0045
- Output: ~3,000 tokens × $15/M = $0.045
- **Total: ~$0.05-0.10 per village**

**At scale** (if we proceed):
- 1,000 villages × $0.08 = $80
- Annual reanalysis: $80/year
- Total AI cost: $80-160/year

**Revenue potential** (if we proceed):
- 1,000 villages × €500/year = €500,000/year

**ROI**: 3,125:1 (€500K revenue / €160 AI cost)

---

## FAQs

**Q: What if I don't have an API key?**  
A: Get one at https://console.anthropic.com/ (free $5 credit)

**Q: What if the test costs more than $0.10?**  
A: Something's wrong - contact Claude for help

**Q: Can I test multiple villages?**  
A: Yes! Create `manot_data.json` and run again (cost: another $0.05)

**Q: What if themes are good but projects are weak?**  
A: That's OK - we can improve project prompts later. Themes are harder.

**Q: Should I test with GPT-4o too?**  
A: Not yet. One test first. If you proceed, we'll compare models in Week 8.

---

## Next Steps After Test

### If GO → Week 1: Multi-Tenancy Setup
- Create `villages` table
- Add `village_id` foreign keys
- Build basic admin interface
- Test with 2 dummy villages

### If ITERATE → Improve Prompts
- Add more specific examples
- Try different framing
- Test with 2-3 villages
- Compare results

### If STOP → Regroup
- Review options (above)
- Discuss with Claude
- Decide: simplify, pivot, or try different approach

---

**Remember**: This $0.05 test validates a €500,000/year business model!
