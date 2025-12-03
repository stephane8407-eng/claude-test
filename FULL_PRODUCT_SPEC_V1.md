# SPV TREASURE MAP - FULL PRODUCT & TECH SPEC v1

**Last Updated:** November 28, 2024  
**Status:** Approved for implementation  
**Target:** Chirac MVP pilot

---

## 0. HIGH-LEVEL CONCEPT

Two-layer platform for village identity and tourism:

1. **Public layer (top)** – Interactive map + village stories for visitors
2. **Village engine (bottom)** – Identity audit + admin tools for communes

**Goal:** Help small villages (<3-5k inhabitants) revive by surfacing their identity and creating tourism/development opportunities.

---

## 1. CORE ENTITIES & DATA MODEL

### 1.1 Settlement (villages table)

Represents a commune, village, or small town.

```sql
-- EXISTING fields to keep
id, name, slug, country, department, region, latitude, longitude,
population, area_km2, subscription_tier, subscription_status, settings, created_at

-- NEW fields to add
summary_identity TEXT,           -- Short tagline for public display
long_identity TEXT,              -- 1-3 paragraph narrative
live_here_summary TEXT,          -- "Living here" section content
hero_image_url VARCHAR(500),     -- Hero image for public page
themes TEXT[]                    -- Array of theme tags
```

### 1.2 Place (pois table)

Physical features: chapel, château, pond, forge, etc.

```sql
-- EXISTING fields to keep
id, village_id, poi_type_id, name, description, latitude, longitude, created_at

-- NEW fields to add
slug VARCHAR(100) UNIQUE,
hero_image_url VARCHAR(500),
access VARCHAR(50),              -- 'public', 'private', 'ruin', 'restricted'
themes TEXT[],                   -- Array of theme tags
status VARCHAR(20) DEFAULT 'published'  -- 'draft', 'published' (for mobile capture)
```

### 1.3 Event (conflicts table)

Historical or contemporary events.

```sql
-- EXISTING fields to keep
id, village_id, name, description, date, latitude, longitude, 
conflict_type, period, participants, outcome, created_at

-- NEW fields to add
slug VARCHAR(100) UNIQUE,
event_type VARCHAR(50),          -- battle, siege, festival, flood, etc.
date_text VARCHAR(100),          -- "c. 1450" or "August 1944"
scale VARCHAR(20),               -- local, regional, national
themes TEXT[],
sources TEXT[],                  -- Array of source URLs/references
status VARCHAR(20) DEFAULT 'published'
```

### 1.4 Route (qr_routes table - expand)

Walking trails and experiences.

```sql
-- EXISTING fields to keep
id, village_id, name, description, created_at

-- NEW fields to add
slug VARCHAR(100) UNIQUE,
hero_image_url VARCHAR(500),
gpx_url VARCHAR(500),            -- URL to GPX file
distance_km DECIMAL(5,2),
duration_minutes INTEGER,
difficulty VARCHAR(20),          -- 'easy', 'medium', 'hard'
route_type VARCHAR(50),          -- 'walk', 'hike', 'cycle', 'trail_run'
school_friendly BOOLEAN DEFAULT FALSE,
themes TEXT[],
waypoints JSONB                  -- Array of {lat, lng, name, description, placeId?}
```

### 1.5 Topic (NEW TABLE)

Theme-based SEO landing pages.

```sql
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    short_description TEXT,
    long_description TEXT,       -- 300-800 words for SEO
    hero_image_url VARCHAR(500),
    tags TEXT[],                 -- For auto-association with entities
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 1.6 Sponsor (NEW TABLE)

Partners and advertisers.

```sql
CREATE TABLE sponsors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    logo_url VARCHAR(500),
    website_url VARCHAR(500),
    short_description TEXT,
    type VARCHAR(50) NOT NULL,   -- 'local_business', 'regional_partner', 'founding_partner'
    sector VARCHAR(100),         -- 'real_estate', 'bank', 'tourism', 'eco', etc.
    regions TEXT[],              -- Administrative regions or free tags
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 1.7 SponsorSlot (NEW TABLE)

Links sponsors to objects with timing and analytics.

```sql
CREATE TABLE sponsor_slots (
    id SERIAL PRIMARY KEY,
    sponsor_id INTEGER REFERENCES sponsors(id) ON DELETE CASCADE,
    object_type VARCHAR(50) NOT NULL,  -- 'settlement', 'route', 'topic'
    object_id INTEGER NOT NULL,
    position VARCHAR(20) DEFAULT 'primary',  -- 'primary', 'secondary'
    start_date DATE,
    end_date DATE,
    impression_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 1.8 Project (NEW TABLE)

AI-suggested and tracked initiatives.

```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    settlement_id INTEGER REFERENCES villages(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    short_description TEXT,
    status VARCHAR(50) DEFAULT 'idea',  -- 'idea', 'planned', 'in_progress', 'completed'
    themes TEXT[],
    source VARCHAR(50) DEFAULT 'manual',  -- 'ai_suggested', 'manual'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 1.9 ThemeTag System

Use tags extensively for flexible filters. Tags are stored as TEXT[] arrays on entities.

**Standard tags (not exhaustive):**
- Historical: `ww2`, `ww1`, `hundred_years_war`, `wars_of_religion`, `roman`, `medieval`, `villages_brules`
- Nature: `ponds`, `rivers`, `forests`, `mountains`, `coast`
- Heritage: `chateaux`, `industrial_heritage`, `roman_ruins`, `churches`
- Culture: `folk_festival`, `traditions`, `legends`, `artisans`
- Practical: `school_friendly`, `family_route`, `accessible`

---

## 2. DESIGN SYSTEM

### 2.1 Colours

```css
:root {
  --color-primary: #008080;      /* Teal */
  --color-secondary: #C8A2C8;    /* Lilac */
  --color-background: #F5F5F5;   /* Light grey */
  --color-surface: #FFFFFF;      /* White */
  --color-text: #1F2937;         /* Dark grey */
  --color-text-muted: #6B7280;   /* Medium grey */
}
```

### 2.2 Typography

- Use system UI font stack
- Clear hierarchy: page title (32px), section title (24px), body (16px), small (14px)

### 2.3 Spacing

4px grid: 4, 8, 12, 16, 24, 32, 48, 64

### 2.4 Components

**Buttons:**
- Rounded corners: 8px
- Primary: teal background, white text
- Secondary: white background, teal border
- Hover: slightly darker

**Cards:**
- Light border (#E5E7EB)
- Subtle shadow: `0 1px 3px rgba(0,0,0,0.1)`
- Border radius: 12px
- Padding: 16px

**Panels:**
- For sidebars and info panels
- Background: white or light grey
- Clear section headers

### 2.5 Overall Feel

- Clean, modern, but warm (heritage/outdoors vibes)
- Public pages: inviting, visual, map-first
- Admin pages: calm, tool-like, minimal

---

## 3. PUBLIC LAYER - FRONTEND PAGES

### 3.1 Main Map Page (Homepage)

**URL:** `/`

**Layout:**
- Top nav: Logo | Explorer la carte | À propos | Espace communes
- Main: Large interactive map (70-80% of viewport)
- Side panel (desktop) or drawer (mobile): Filters + search + village preview

**Filters Panel:**
```
🔍 Search: [Rechercher un village, thème...]

📜 History & Conflict:
  □ WWII / Villages brûlés
  □ WWI
  □ Hundred Years War
  □ Medieval
  □ Roman

🌿 Nature:
  □ Ponds / Étangs
  □ Rivers
  □ Forests

🏰 Heritage:
  □ Châteaux
  □ Industrial heritage
  □ Churches / Chapels

🎭 Culture & Life:
  □ Festivals
  □ Legends & Folklore
  □ School-friendly
```

**Map Behaviour:**
- Show village markers (clustered when zoomed out)
- Click marker → show preview card in side panel
- Preview card: name, tagline, 2-3 theme chips, "Voir la fiche" button

### 3.2 Village Detail Page

**URL:** `/villages/[slug]`

**Sections (in order):**

1. **Header**
   - Hero image (or placeholder)
   - Village name + department/region
   - Short identity tagline (summary_identity)

2. **Identity & Themes**
   - 1-3 paragraph narrative (long_identity)
   - Theme chips (clickable → filter map)

3. **Highlights Map**
   - Embedded map centered on village
   - Markers for Places, Events, Route starting points

4. **Routes / Experiences**
   - Cards for associated routes (0-3)
   - Each card: name, distance, time, difficulty, themes, link

5. **History & Heritage**
   - Key historical points (from Events)
   - Link to event detail pages

6. **Environment & Life**
   - Environment description
   - "Living here" section (live_here_summary)
   - 3-5 bullet points

7. **Partners**
   - Section: "Partenaires locaux"
   - Show SponsorSlots for this village
   - Logo + short text + link (tracked via /sponsor-click/[slotId])

8. **Share / QR**
   - Share buttons
   - QR code link

### 3.3 Route Detail Page

**URL:** `/routes/[slug]`

**Sections:**

1. **Header**
   - Route name + village
   - Hero image
   - Sponsor line: "Soutenu par [Sponsor]" if SponsorSlot exists

2. **Map**
   - Full route display
   - If gpx_url exists: draw route line from GPX
   - Show waypoint markers

3. **Key Stats**
   - Distance (km) | Duration (min) | Difficulty | Type
   - Theme chips
   - School-friendly badge if true

4. **Description**
   - Narrative text

5. **Waypoints**
   - Ordered list of stops
   - Each: name, short description, link to Place if linked

6. **Download**
   - "Télécharger GPX" button (if gpx_url exists)

### 3.4 Place Detail Page

**URL:** `/places/[slug]`

**Simple template:**
- Title + type
- Village + region
- Hero image
- Description
- Access info
- Small map
- Theme chips
- Link back to village

### 3.5 Event Detail Page

**URL:** `/events/[slug]`

**Simple template:**
- Title + event type
- Date/period
- Village + region
- Description
- Participants, outcome (if battle)
- Sources list
- Small map
- Theme chips
- Link back to village

### 3.6 Topic Page (SEO Landing)

**URL:** `/themes/[slug]`

**Sections:**

1. **Header**
   - Title + hero image
   - Short description

2. **Long Description**
   - 300-800 words (SEO content)

3. **Map**
   - Shows all villages/routes matching this topic's tags

4. **Featured Villages**
   - Cards for villages with matching tags

5. **Featured Routes**
   - Cards for routes with matching tags

6. **Sponsors**
   - SponsorSlots for this topic

---

## 4. ADMIN LAYER - FRONTEND PAGES

### 4.1 Admin Layout

**Sidebar Navigation (Notion-style):**
```
[Village Name]
─────────────
📊 Dashboard
🎯 Identity Audit
📍 Places
📅 Events  
🚶 Routes
💡 Projects
─────────────
[Platform Admin Only]
📄 Topics
🤝 Sponsors
⚙️ Settings
```

### 4.2 Identity Audit Wizard

**5-Step Wizard with Stepper:**

**Step 1: History & Heritage**
- Checkboxes: war periods involved (WW2, WW1, Medieval, etc.)
- Checkboxes: event types (battles, burned villages, sieges, etc.)
- Text: Notable monuments (church, château, memorials)
- Text: Legends & folklore
- Free text: "Anything else about your history?"

**Step 2: Environment & Resources**
- Checkboxes: water features (ponds, river, lake)
- Checkboxes: landscape (forest, mountains, plateau, valley)
- Text: Farms and agriculture
- Text: Natural resources (wood, stone, etc.)
- Free text: "Describe your natural environment"

**Step 3: Economy, Traditions & Life**
- Checkboxes: local products (existing)
- Text: Potential products not yet developed
- Text: Festivals and annual events
- Checkboxes: services present (school, shop, café, etc.)
- Select: Vibe (calm, lively, family-oriented, artistic, etc.)
- Text: Nearest town/connections
- Free text: "What's it like to live here?"

**Step 4: Free Description**
- Large text area: "Racontez votre village avec vos mots..."
- Prompt: what you love, what worries you, what you'd like in 10 years

**Step 5: Review & Generate**
- Button: "Générer l'identité"
- Loading state while AI processes
- Display results:
  - Generated summary_identity (editable)
  - Generated long_identity (editable)
  - Generated live_here_summary (editable)
  - Suggested themes (checkboxes to accept/reject)
  - Suggested projects (list, can remove)
- Button: "Sauvegarder et publier"

### 4.3 Places Management

**List view:**
- Table: Name | Type | Status | Actions
- Filter by type, status
- Add new button

**Form:**
- Name, slug (auto-generated)
- Type (select from poi_types)
- Description (textarea)
- Location (map picker or lat/lng input)
- Access (select: public, private, ruin, restricted)
- Hero image upload
- Themes (tag input)
- Status (draft/published)

### 4.4 Events Management

**List view:**
- Table: Name | Type | Period | Status | Actions

**Form:**
- Name, slug
- Event type (select)
- Period (select)
- Date or date_text
- Description
- Location (map picker)
- Participants, outcome (if conflict)
- Sources (multi-line or array input)
- Themes
- Status

### 4.5 Routes Management

**List view:**
- Table: Name | Distance | Difficulty | Status | Actions

**Form:**
- Name, slug
- Description
- Hero image upload
- GPX file upload
- Distance, duration, difficulty, route type
- School-friendly toggle
- Themes
- Waypoints editor (add/remove/reorder)
  - Each waypoint: name, description, lat/lng or link to Place

### 4.6 Projects Management

**List view:**
- Table: Title | Status | Source | Actions
- Filter by status

**Form:**
- Title
- Short description
- Status (select: idea, planned, in_progress, completed)
- Themes
- Source (read-only: ai_suggested or manual)

### 4.7 Mobile Capture

**Simple mobile-friendly page:**
- Large "Take Photo" button
- Uses device camera + geolocation
- After capture:
  - Shows photo preview
  - Shows detected lat/lng
  - Select type: Place or Event
  - Optional: quick title
- Creates draft entry
- Admin completes details later on desktop

### 4.8 Sponsor Management (Platform Admin)

**Sponsors list:**
- Table: Name | Type | Sector | Actions

**Sponsor form:**
- Name, slug
- Logo upload
- Website URL
- Short description
- Type (select)
- Sector
- Regions (tag input)

**SponsorSlot management:**
- On sponsor detail page, show active slots
- Add slot form:
  - Object type (select: settlement, route, topic)
  - Object (search/select)
  - Position (primary/secondary)
  - Start date, end date
- Show impression_count, click_count (read-only)

### 4.9 Topic Management (Platform Admin)

**List view:**
- Table: Title | Slug | Actions

**Form:**
- Title, slug
- Short description
- Long description (rich text or markdown)
- Hero image upload
- Tags (determines auto-association)

---

## 5. SPONSOR CLICK TRACKING

### Endpoint: `/api/sponsor-click/[slotId]`

**Behaviour:**
1. Increment `click_count` on SponsorSlot
2. Look up Sponsor.website_url
3. Redirect (302) to sponsor website

### Impression Tracking

When rendering a page with SponsorSlots:
- Call API endpoint to increment `impression_count`
- Can be approximate (no per-user dedupe needed for v1)

---

## 6. GPX HANDLING

### Upload Flow:
1. Admin selects .gpx file in route form
2. Backend saves to storage (local or cloud)
3. Returns URL, stored in Route.gpx_url

### Display Flow:
1. Route page loads
2. If gpx_url exists:
   - Fetch GPX file
   - Parse (client-side, use gpxparser or similar)
   - Draw polyline on map
3. Show "Download GPX" button linking to gpx_url

---

## 7. MEDIA / IMAGE HANDLING

### v1 Approach:
- Local storage in `/uploads/` folder
- Simple upload endpoint: POST /api/upload
  - Accepts image file
  - Validates (jpg, png, webp, max 5MB)
  - Resizes to max 1920px width
  - Strips EXIF
  - Returns URL

### Hero Images:
- Settlement.hero_image_url
- Route.hero_image_url
- Topic.hero_image_url
- Place.hero_image_url

### Admin Forms:
- Include "Upload hero image" field
- Show preview after upload
- Store returned URL

---

## 8. SEARCH & SEO

### Public Search:
- Search box on map page
- Query against: settlement.name, tags, topic.title
- Return matching settlements and topics

### Query Logging:
- Log searches: query, timestamp, results_count
- Simple table for analytics

### SEO:
- Clean URLs: /villages/[slug], /routes/[slug], etc.
- Dynamic meta tags: title, description from entity data
- Open Graph tags for social sharing

### QR Source Tracking:
- Support ?src= query parameter
- Log page views with source
- Don't break routing

---

## 9. AUTH & ROLES

### Roles:
- `platform_admin` - Full access
- `regional_admin` - Manage villages/sponsors in their regions
- `village_admin` - Manage own settlement only

### Permissions:
- Village admins: CRUD for their Places, Events, Routes, Projects
- Village admins: Run identity audit for their settlement
- Village admins: Cannot manage sponsors or topics
- Platform admins: All features including sponsors, topics

---

## 10. REVIVAL CASE STUDIES (AI Training Data)

### 10.1 Purpose

Train the AI identity engine with real-world examples of successful village revivals. When generating themes and projects, the AI references similar villages that succeeded, making recommendations more credible and actionable.

### 10.2 Database Schema

```sql
CREATE TABLE revival_case_studies (
    id SERIAL PRIMARY KEY,
    
    -- Village info
    village_name VARCHAR(255) NOT NULL,
    country VARCHAR(2) NOT NULL,           -- 'FR', 'UK', etc.
    region VARCHAR(100),
    population_before INTEGER,             -- Before revival
    population_after INTEGER,              -- After revival (if known)
    
    -- Revival details
    revival_type VARCHAR(50) NOT NULL,     -- 'eco', 'artisan', 'tourism', 'remote_work', 'heritage', 'agriculture'
    themes TEXT[],                         -- Tags: ponds, forests, ww2, industrial, etc.
    
    -- The story
    challenge TEXT,                        -- What problem they faced
    strategy TEXT,                         -- What approach they took
    key_projects TEXT[],                   -- Specific projects implemented
    outcomes TEXT,                         -- What they achieved
    lessons_learned TEXT,                  -- Key takeaways
    timeline_years INTEGER,                -- How long the revival took
    
    -- For AI matching
    population_band VARCHAR(20),           -- '<500', '500-1000', '1000-3000', '3000-5000'
    geography_tags TEXT[],                 -- 'river', 'forest', 'mountain', 'coast', 'plain'
    
    -- Sources
    source_urls TEXT[],                    -- Links to articles, videos
    source_description TEXT,               -- "YouTube documentary", "News article", etc.
    
    -- Meta
    is_verified BOOLEAN DEFAULT FALSE,     -- Manually verified accuracy
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_case_studies_themes ON revival_case_studies USING GIN(themes);
CREATE INDEX idx_case_studies_type ON revival_case_studies(revival_type);
CREATE INDEX idx_case_studies_country ON revival_case_studies(country);
CREATE INDEX idx_case_studies_population ON revival_case_studies(population_band);
```

### 10.3 Example Case Studies to Add

| Village | Country | Type | Strategy |
|---------|---------|------|----------|
| Saint-Pierre-de-Frugie | FR | eco | Eco-village with organic farming, nature tourism |
| Montrol-Sénard | FR | artisan | Artists and craftspeople residency program |
| Puy-du-Fou | FR | tourism | Theme park based on local history |
| Châtel-Montagne | FR | remote_work | Remote worker hub with co-working |
| Marnay | FR | heritage | Heritage restoration + tourism route |

### 10.4 AI Integration

When generating identity themes, the prompt should:

1. **Find similar case studies** based on:
   - Similar population band
   - Overlapping themes (ponds, forests, ww2, etc.)
   - Similar geography

2. **Include in prompt:**
```
Based on your analysis, also consider these successful revival examples 
from similar villages:

1. Saint-Pierre-de-Frugie (pop. 400, Dordogne):
   - Challenge: Dying village, no jobs, aging population
   - Strategy: Eco-village transformation with organic farming
   - Outcome: Population doubled, became tourism destination
   - Lesson: Nature assets can anchor economic revival

2. [More relevant examples...]

Use these as inspiration when suggesting themes and projects.
Reference specific examples when relevant.
```

### 10.5 Admin UI

**Case Studies Management (Platform Admin):**
- List all case studies with filters (country, type, themes)
- Add/edit form with all fields
- Mark as verified
- Preview how it appears in AI prompts

---

## 11. FUNDING PROGRAMS DATABASE

### 11.1 Purpose

Provide villages with relevant funding opportunities for their projects. When the AI suggests a project, it should also suggest potential funding sources with process guidance.

### 11.2 Database Schema

```sql
CREATE TABLE funding_programs (
    id SERIAL PRIMARY KEY,
    
    -- Basic info
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    provider VARCHAR(255),                 -- "EU", "État français", "Région", "Fondation", etc.
    country VARCHAR(2) NOT NULL,           -- 'FR', 'UK', 'EU'
    
    -- Description
    short_description TEXT,
    long_description TEXT,
    
    -- Eligibility
    eligible_themes TEXT[],                -- 'heritage', 'tourism', 'eco', 'agriculture', 'housing', etc.
    eligible_population_max INTEGER,       -- Max population to be eligible (NULL = no limit)
    eligible_entity_types TEXT[],          -- 'commune', 'association', 'entreprise', 'particulier'
    eligible_regions TEXT[],               -- Specific regions, or empty = all
    
    -- Funding details
    funding_type VARCHAR(50),              -- 'grant', 'loan', 'guarantee', 'tax_credit'
    amount_min INTEGER,                    -- Minimum funding (EUR)
    amount_max INTEGER,                    -- Maximum funding (EUR)
    funding_percentage_max INTEGER,        -- Max % of project funded (e.g. 80)
    
    -- Application
    application_url VARCHAR(500),
    deadline DATE,                         -- NULL = ongoing
    deadline_type VARCHAR(50),             -- 'fixed', 'rolling', 'annual'
    
    -- Process guidance
    process_summary TEXT,                  -- Step-by-step overview
    process_difficulty VARCHAR(20),        -- 'simple', 'moderate', 'complex'
    typical_timeline_months INTEGER,       -- How long approval takes
    tips TEXT,                             -- Insider tips for success
    
    -- Source
    source_url VARCHAR(500) NOT NULL,      -- Official program page
    last_verified_at DATE,
    
    -- Meta
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_funding_themes ON funding_programs USING GIN(eligible_themes);
CREATE INDEX idx_funding_country ON funding_programs(country);
CREATE INDEX idx_funding_active ON funding_programs(is_active);
CREATE INDEX idx_funding_deadline ON funding_programs(deadline);
```

### 11.3 Key Funding Programs to Add (France)

| Program | Provider | Themes | Amount |
|---------|----------|--------|--------|
| LEADER | EU | rural_dev, tourism, agriculture | Up to 80% |
| Petites Villes de Demain | État | revitalization, housing, commerce | Varies |
| Fondation du Patrimoine | Fondation | heritage, restoration | 10-30% |
| FEADER | EU | agriculture, rural | Up to 80% |
| DSIL | État | investment, infrastructure | Varies |
| France Relance - Rénovation | État | energy, buildings | Up to 80% |
| Fonds Vert | État | eco, climate | Varies |

### 11.4 Data Sources

**France:**
- **aides-territoires.beta.gouv.fr** - Government API with all territorial aids
- **europe-en-france.gouv.fr** - EU funding in France
- **banquedesterritoires.fr** - CDC financing

**UK (future):**
- **gov.uk** - Various rural development funds
- **heritagefund.org.uk** - Heritage Lottery Fund

### 11.5 AI Integration

When suggesting projects, match to relevant funding:

```
PROJECT: Create artisan workshop spaces in abandoned farm buildings

💰 POTENTIAL FUNDING:

1. LEADER (EU Rural Development)
   - Amount: Up to 80% of eligible costs
   - Deadline: Rolling applications via local GAL
   - Process: Contact your local GAL (Groupe d'Action Locale)
   - Difficulty: Moderate
   - Timeline: 6-12 months

2. Fondation du Patrimoine
   - Amount: 10-30% for heritage buildings
   - Deadline: Ongoing
   - Process: Online application + site visit
   - Difficulty: Simple
   - Timeline: 2-3 months

📋 RECOMMENDED FIRST STEPS:
1. Contact your EPCI to discuss project
2. Get a "diagnostic territorial" if not done
3. Identify which buildings could be used
4. Apply to LEADER via local GAL
```

### 11.6 Admin UI

**Funding Programs Management (Platform Admin):**
- List all programs with filters (country, themes, active, deadline)
- Add/edit form with all fields
- Mark last verified date
- Bulk import from aides-territoires API (future)

**Public/Village Admin View:**
- Browse funding programs
- Filter by theme, amount, deadline
- See which programs match suggested projects

---

## 12. ENHANCED AI IDENTITY ENGINE

### 12.1 Updated Generation Flow

```
VILLAGE DATA (from audit)
         ↓
    AI ANALYSIS
         ↓
FIND SIMILAR CASE STUDIES ←── revival_case_studies table
         ↓
GENERATE THEMES & PROJECTS
         ↓
MATCH PROJECTS TO FUNDING ←── funding_programs table
         ↓
OUTPUT:
- Identity narrative (with real examples cited)
- Themes (proven in similar villages)
- Projects (with funding recommendations)
- Process guidance
```

### 12.2 Enhanced Project Output

Each suggested project should include:

```python
{
    "title": "Créer des ateliers d'artisans",
    "short_description": "...",
    "themes": ["artisan", "heritage", "tourism"],
    "difficulty": "moderate",
    "estimated_timeline_months": 18,
    "estimated_budget_range": "50000-150000",
    
    # NEW: Inspired by
    "inspired_by": {
        "case_study_id": 5,
        "village_name": "Montrol-Sénard",
        "relevance": "Similar population, also had abandoned buildings"
    },
    
    # NEW: Funding matches
    "potential_funding": [
        {
            "program_id": 12,
            "name": "LEADER",
            "match_score": 0.9,
            "why_relevant": "Matches rural development + artisan themes"
        }
    ],
    
    # NEW: Process hints
    "first_steps": [
        "Contact your EPCI rural development officer",
        "Identify potential buildings",
        "Apply to LEADER via local GAL"
    ]
}
```

---

---

## 13. IMPLEMENTATION ROADMAP

**Vision:** Create an AI-powered platform that makes village revival as easy as possible by automating research, pre-populating audits, generating actionable project plans, and providing grant application kits.

**Target:** €500-1000/year subscription per village with 95%+ profit margin

---

### Phase A: Backend Foundation ✅ COMPLETE
**Status:** Done (Week 0-12)

**What was built:**
- Multi-tenant architecture (27 database tables)
- Authentication & authorization (4 roles, 21 permissions)
- API endpoints for villages, POIs, conflicts, routes, QR codes
- Identity themes engine (basic)
- Subscription tiers & billing structure
- Production infrastructure (Docker, CI/CD, Redis, nginx)

**Current data:**
- Chirac: 123 conflicts, 19 POIs, 3 identity themes
- Manot: Basic data
- AI scraper: 78-82% accuracy for conflicts

---

### Phase B: Public Frontend Foundation ✅ MOSTLY COMPLETE
**Status:** Week 13 (Current)

**Completed:**
- ✅ Design system (teal/lilac, components, style guide)
- ✅ Map explorer page with filters (/explore)
- ✅ Homepage (marketing landing page)
- ✅ Village detail page (basic structure)

**Remaining:**
- Route detail page (with GPX display)
- Place detail page (simple template)
- Event detail page (simple template)
- Topic/theme pages (SEO landing pages)
- Public mini-site template for partners (NEW from vision)

**Timeline:** 1-2 weeks to complete

---

### Phase C: Admin Core Tools ⏳ IN PROGRESS
**Status:** Week 13-14

**Completed:**
- ✅ Identity audit wizard (5-step, localStorage persistence)
- ✅ Admin review page (themes, projects, Phase D placeholders)
- ✅ Mock AI generator (returns sample data)
- ✅ Login system (fixed bcrypt issues)

**Remaining:**
- Mobile capture tool (camera + GPS + draft places)
- Places/Events/Routes CRUD pages
- Projects management interface
- Topic & Sponsor management (platform admin)
- Dashboard improvements

**Timeline:** 2-3 weeks

---

### Phase D: Real AI Engine + RAG Foundation 🎯 NEXT PRIORITY
**Status:** Week 15-17 (2-3 weeks)

**Core AI Infrastructure:**
1. **Real Claude API Integration**
   - Replace mock generator with actual Claude API
   - Structured prompts for identity analysis
   - Project plan generation
   - Cost: ~$1.50 per full audit

2. **Case Studies Database (RAG Context)**
   - Create `revival_case_studies` table
   - Seed with 10-20 real success stories (France + international)
   - Fields: village, strategy, outcomes, lessons, themes, population_band
   - API endpoints for CRUD
   - Similarity matching algorithm

3. **Funding Programs Database**
   - Create `funding_programs` table
   - Seed with 10-20 key French programs:
     * LEADER, Petites Villes de Demain, Fondation du Patrimoine
     * FEADER, DSIL, France Relance, Fonds Vert
   - Fields: eligibility, amounts, deadlines, process_summary
   - Project-to-funding matching logic

4. **Enhanced Identity Generator**
   - Takes audit inputs + photos
   - Queries similar case studies (RAG)
   - Generates 2-3 identity options (NEW)
   - Each option includes:
     * Identity narrative
     * 3-5 themed project suggestions
     * Matched funding programs
     * "Inspired by" case study references
   - Cost: ~$1.50 per generation (2-3 options)

5. **Admin UI for Data Management**
   - Case studies management (add/edit/verify)
   - Funding programs management
   - View which case studies matched which villages

**Outputs after Phase D:**
```
Mayor completes audit
        ↓
Real AI analyzes
        ↓
Returns 2-3 identity options:

Option 1: "Waters of Resilience" (Ponds + Ecology)
  - Inspired by: Saint-Pierre-de-Frugie
  - 5 projects: Pond trail, fishing tourism, eco-education...
  - Funding: LEADER (80%), FEADER
  
Option 2: "Forges of Memory" (WWII + Heritage)
  - Inspired by: Montrol-Sénard
  - 5 projects: Memorial trail, annual commemoration...
  - Funding: Fondation du Patrimoine, DSIL

Option 3: "Agricultural Innovation" (Farms + Sustainability)
  - Inspired by: Châtel-Montagne
  - 5 projects: Organic cooperative, farm tours...
  - Funding: FEADER, Fonds Vert
```

**Timeline:** 2-3 weeks  
**Cost per village:** ~$1.50

---

### Phase E: Pre-Population Engine 🚀 GAME CHANGER
**Status:** Week 18-20 (2-3 weeks)

**The Vision:**
Don't make mayors start with blank forms. Auto-research their village and pre-fill 60-80% of the audit before they even start.

**Implementation:**

1. **Enhanced AI Scraper**
   - Extend existing conflict scraper to gather:
     * POIs (from OSM, Mérimée)
     * Geographic features (OSM, IGN)
     * Heritage sites (POP, Mérimée, MH)
     * Demographics (INSEE API - free)
     * Historical events (Wikipedia, FranceArchives)
     * Past industries (BnF Gallica, archives)

2. **Targeted Scraping Per Section**
   ```python
   # When village is added or "Pre-populate" clicked
   
   # History Section:
   - Search: "{village} + {department} + history"
   - Sources: Wikipedia, FranceArchives, conflicts DB
   - AI extracts: war periods, monuments, legends
   - Pre-ticks: WWII checkbox, Medieval checkbox
   - Pre-fills: "Notable monuments: Église Saint-Cybard (12th c.)"
   
   # Environment Section:
   - Search: OSM tags (natural=pond, natural=forest)
   - INSEE geographic data
   - AI summarizes: "3 ponds identified: Étang Saint-Martin..."
   - Pre-ticks: Ponds, River, Forest checkboxes
   
   # Economy Section:
   - Search: Historical industries from Gallica
   - Current businesses from official registries
   - AI extracts: "Former forge (17th-18th c.), 12 active farms"
   ```

3. **Confidence Scoring**
   - Each pre-filled field has confidence score (0-1)
   - Show to admin: "✓ 85% confident" or "⚠️ 60% - verify"
   - Admin can accept/reject/modify

4. **Background Processing**
   - Don't block UX - process in background
   - Show progress: "Researching history... 30%"
   - Takes 2-5 minutes
   - Admin gets notification when ready

5. **Source Attribution**
   - Every pre-filled field shows source
   - "From: Wikipedia" or "From: POP database"
   - Clickable links to original sources
   - Builds trust, allows verification

**User Experience:**
```
Mayor logs in for first time
        ↓
Clicks "Start Identity Audit"
        ↓
System: "We're researching Chirac... ☕ This takes 2-3 minutes"
        ↓
Progress bar: History ✓ Environment ✓ Economy...
        ↓
Notification: "Your audit is pre-populated and ready!"
        ↓
Mayor opens wizard, sees:
  ☑ WWII (85% confident - FranceArchives)
  ☑ Medieval (78% confident - Church records)
  Monuments: "Église Saint-Cybard (12th c.)" ✏️
  ☑ Ponds: "3 ponds: Étang Saint-Martin, Étang..." ✏️
        ↓
Mayor reviews, adds local knowledge, submits
```

**Cost per village:** $0.30-0.50 for deep scraping  
**Timeline:** 2-3 weeks  
**Value:** Reduces mayor effort by 60-80%

---

### Phase F: Photo Intelligence 📸 VISUAL EVIDENCE
**Status:** Week 21-22 (1-2 weeks)

**Dual Timeline Integration:**

1. **During Audit (First-Time)**
   ```
   Step 2: Environment
   [Pre-populated data shown]
   ☑ Ponds: 3 ponds identified
   
   [📸 Document Your Ponds]
   Opens camera → Takes photo → Auto-geolocates
   "Étang Saint-Martin captured at 45.9139, 0.6543"
   
   Photo linked to Environment section
   AI analyzes: "Well-maintained pond, public access visible"
   ```

2. **After Audit (Refinement)**
   ```
   Admin has initial report
   Realizes: "We forgot about the old mill!"
   
   Goes to village, takes photo of mill
   Uploads via dashboard
   
   Clicks "Refine Identity Report"
   AI re-analyzes with new photo evidence
   New theme emerges: "Industrial Heritage"
   ```

3. **Photo AI Analysis**
   - Describe what's in photo (Claude Vision API)
   - Extract features (pond, building, forest)
   - Assess condition (maintained, ruined, accessible)
   - Suggest categories (heritage, nature, tourism)
   - Cost: $0.01 per photo

4. **Geolocation Intelligence**
   - Photos auto-create draft POIs
   - Map shows photo locations
   - Cluster photos by area
   - Suggest routes based on photo clusters

5. **Public Display Control**
   - Admin reviews each photo
   - Toggle: "Show on public page"
   - Selected photos appear on village mini-site
   - Photos enrich project suggestions

**Timeline:** 1-2 weeks  
**Cost:** ~$0.20 for 20 photos per village

---

### Phase G: Multiple Identity Paths 🎭 CHOICE & FLEXIBILITY
**Status:** Week 23 (1 week)

**The Concept:**
Villages don't have to choose one identity. Show 2-3 options, let them compare, select multiple if they want.

**Implementation:**

1. **Prompt Engineering**
   ```
   "Based on this village data, generate 3 distinct identity options:
   
   Option 1: Focus on strongest theme (highest confidence)
   Option 2: Focus on unique/differentiating theme
   Option 3: Focus on economic opportunity theme
   
   For each option, provide:
   - Identity narrative
   - 5 specific project ideas
   - Matched funding programs
   - Similar success stories
   - Estimated timeline & budget"
   ```

2. **Comparison View**
   - Side-by-side cards for 3 options
   - Show projects per option
   - Show funding matches per option
   - Estimated complexity & costs
   - "Inspired by" villages

3. **Selection Logic**
   - Admin can select 1, 2, or all 3
   - Each selection generates detailed project plans
   - Can run multiple identities in parallel (A/B testing)

4. **Database Structure**
   ```sql
   ALTER TABLE identity_themes ADD COLUMN option_number INTEGER;
   ALTER TABLE identity_themes ADD COLUMN is_selected BOOLEAN DEFAULT FALSE;
   
   -- Village can have multiple active identities
   -- Theme #1, Option 1, Selected ✓
   -- Theme #2, Option 1, Selected ✓
   -- Theme #3, Option 2, Not selected
   ```

**User Experience:**
```
AI generates report
        ↓
Shows 3 identity options:
[Option 1: Waters & Ecology] [Select]
[Option 2: WWII Memory]       [Select]
[Option 3: Agri-Tourism]     [Select]
        ↓
Mayor selects 1 & 2
        ↓
System generates detailed plans for both
```

**Cost:** 2-3x API calls = $1.50-2.00 total  
**Timeline:** 1 week

---

### Phase H: Project Execution Tools 🛠️ FROM IDEA TO REALITY
**Status:** Week 24-27 (3-4 weeks)

**The Vision:**
Don't just suggest projects - give mayors everything they need to actually DO them.

**Features:**

1. **Auto-Generated Project Plans**
   ```
   Project: "Create Circuit des Étangs walking trail"
   
   AI generates:
   
   📋 Overview
   - Description: 8km loop connecting 3 ponds
   - Timeline: 12 months
   - Budget: €45,000-60,000
   - Difficulty: Medium
   
   📍 12-Step Plan
   ✓ 1. Form steering committee [Done]
   ☐ 2. Survey route & assess accessibility [2 weeks]
   ☐ 3. Design trail & signage [3 weeks]
   ☐ 4. Apply for LEADER funding [6 weeks]
   ☐ 5. Obtain permissions from landowners [4 weeks]
   ...
   
   ✅ Checklist per step
   📅 Suggested timeline
   👥 Recommended team roles
   💰 Budget breakdown
   📎 Required documents list
   ```

2. **AI Project Chatbot**
   ```
   Each project has embedded chatbot
   Knows project context
   
   Mayor asks: "How do I contact universities for water research?"
   
   Bot: "For water quality research partnerships:
   
   1. Contact Institut National de Recherche:
      - Dr. Marie Dubois (water quality specialist)
      - Email: m.dubois@inrae.fr
      
   2. University of Limoges, Water Research Lab:
      - Prof. Jean Martin
      - Website: limoges.fr/water-lab
      
   3. Prepare:
      - Project brief (I can generate this)
      - Water samples data
      - Proposed timeline
      
   Would you like me to generate an email template?"
   ```
   
   - Context-aware (knows project, village, goals)
   - Proactive suggestions
   - Can generate documents
   - Remembers conversation history
   - Cost: ~$3/year per project (100 questions)

3. **Checklist System**
   - Per-step checklists
   - Mark items complete
   - Progress tracking
   - Team assignments
   - Due dates

4. **Basic Calendar Integration**
   - Milestones on timeline
   - Deadline reminders
   - Export to Google Calendar (iCal format)
   - Email notifications

5. **Team Collaboration**
   - Assign tasks to team members
   - Comment threads per task
   - @mentions
   - Activity feed
   - Simple but functional

6. **Document Generation**
   - Project brief (PDF)
   - Timeline chart (visual)
   - Budget spreadsheet (CSV/Excel)
   - Team roster
   - One-click generation

**Timeline:** 3-4 weeks  
**Cost per project:** ~$0.50 plan generation + $3/year chatbot

---

### Phase I: Grant Application Kits 💰 FUNDING MADE EASY
**Status:** Week 28-30 (2-3 weeks)

**The Reality:**
We CAN'T auto-fill grant PDF forms (too complex, legal issues).  
We CAN generate perfect content blocks to copy-paste.

**Implementation:**

1. **Grant Template Library**
   - LEADER (EU rural development)
   - Petites Villes de Demain (État)
   - Fondation du Patrimoine (Heritage)
   - FEADER (Agricultural/rural)
   - DSIL (Infrastructure investment)
   - France Relance (Renovation)
   - Fonds Vert (Climate/ecology)

2. **Project-to-Grant Matching**
   ```python
   Project: "Pond trail with educational panels"
   Themes: [ecology, tourism, heritage]
   Budget: €50,000
   
   AI matches:
   1. LEADER - 95% match (rural tourism + ecology)
      - Eligible: Up to 80% funding
      - Application deadline: Rolling (via local GAL)
      
   2. Fondation du Patrimoine - 70% match
      - Eligible: 10-30% for heritage interpretation
      - Application deadline: Ongoing
   ```

3. **Auto-Generated Content Blocks**
   ```
   For each matched grant, AI generates:
   
   📄 "Copy-Paste Kit":
   
   [Section 1: Project Summary - 300 words]
   "The Commune of Chirac proposes to create..."
   [Copy] [Edit in AI]
   
   [Section 2: Objectives & Impact - 400 words]
   "This project addresses rural isolation by..."
   [Copy] [Edit in AI]
   
   [Section 3: Budget Breakdown - Table]
   | Item | Cost | Funding Source |
   |------|------|----------------|
   | Signage | €12,000 | LEADER (80%) |
   ...
   [Copy as CSV] [Copy as formatted table]
   
   [Section 4: Timeline - Gantt Chart]
   [Download PDF] [Copy text version]
   
   [Section 5: Partnership Letters - Template]
   "Dear [Name], The Commune of Chirac invites..."
   [Copy] [Customize]
   
   [Section 6: Environmental Impact - 200 words]
   [Copy]
   
   [Section 7: Community Benefit - 250 words]
   [Copy]
   ```

4. **Formatting Guidance**
   ```
   Shows side-by-side:
   
   [Grant Form PDF Preview] | [Your Content Blocks]
   
   Instructions:
   "Paste Section 1 into form field #3"
   "Paste Budget Table into Section B.2"
   "Attach Timeline PDF as Annex 1"
   
   Visual arrows showing where each block goes
   ```

5. **Multi-Grant Strategy**
   ```
   Budget: €60,000
   
   Suggested funding mix:
   - LEADER: €40,000 (67%)
   - Fondation: €10,000 (17%)
   - Commune: €10,000 (17%)
   
   Generate applications for:
   ☐ LEADER application kit [Generate]
   ☐ Fondation application kit [Generate]
   ☐ Combined budget justification [Generate]
   ```

6. **Process Guidance Per Grant**
   ```
   LEADER Application Process:
   
   Step 1: Contact your local GAL
      - GAL Haute Charente: contact@gal-charente.fr
      - Ask for: Programme guide + application form
      
   Step 2: Submit draft project (2 weeks)
      - Use our generated summary
      - Get feedback
      
   Step 3: Prepare full application (4 weeks)
      - Use our content blocks
      - Gather support letters
      - Get municipality approval
      
   Step 4: Submit & follow up (6-12 months)
      - Typical review time: 3-6 months
      - Be ready to present to committee
   
   💡 Tips from similar projects:
      - Saint-Pierre-de-Frugie waited 4 months
      - They recommend starting 6 months before project start
   ```

**Timeline:** 2-3 weeks  
**Cost per grant kit:** ~$0.30-0.50

---

### Phase J: Public Mini-Sites 🌐 VISIBILITY & PROMOTION
**Status:** Week 31-32 (1-2 weeks)

**The Concept:**
Partner villages get beautiful public pages auto-populated from their audit, showcasing their identity, projects, and routes.

**Features:**

1. **Auto-Population Logic**
   ```
   Village completes audit → Selects identity
           ↓
   Admin controls what's public:
   [✓] Show identity narrative
   [✓] Show selected themes
   [✓] Show active projects
   [✓] Show routes
   [✓] Show photos (selected)
   [  ] Hide sensitive data
           ↓
   Public mini-site auto-generates
   ```

2. **Template Structure**
   ```
   /villages/chirac-charente
   
   [Hero: Village photo + Name]
   "Chirac: Where ponds meet history"
   
   [Identity Section]
   Narrative from audit (approved text)
   
   [Our Projects]
   Cards showing active projects:
   - Circuit des Étangs (In Progress - 40%)
   - Fish Cooperative (Planning)
   - WWII Memorial Trail (Funding)
   
   [Discover Chirac]
   Map + Routes + POIs
   
   [Visit & Stay]
   Practical info, contacts
   
   [Partners]
   Sponsor logos (if any)
   ```

3. **Dynamic Updates**
   - Project progress updates → Auto-reflects on public page
   - New photos approved → Appear in gallery
   - New routes created → Added to map
   - Everything stays fresh automatically

4. **SEO Optimization**
   - Clean URLs: /villages/chirac-charente
   - Meta tags from identity narrative
   - Open Graph for social sharing
   - Structured data (Schema.org)
   - Image optimization

5. **Social Proof**
   ```
   "Join 47 villages reviving through SPV"
   
   [Chirac] "Created 3 routes, €45k in funding"
   [Manot] "Restored chapel, 200 visitors/month"
   ...
   ```

**Timeline:** 1-2 weeks  
**Cost:** Minimal (template-based)

---

### Phase K: Cost Monitoring & Optimization 📊 SUSTAINABILITY
**Status:** Week 33-34 (2 weeks)

**The Need:**
Track API costs, optimize caching, ensure profitability at scale.

**Features:**

1. **Admin Cost Dashboard**
   ```
   💰 API Usage This Month
   
   Total Spent: €127 / €500 budget
   Villages Processed: 42
   Average Cost: €3.02 per village
   
   Breakdown:
   - Pre-population: €63 (50%)
   - Identity generation: €38 (30%)
   - Project plans: €21 (17%)
   - Photo analysis: €5 (4%)
   
   ⚠️ Alerts:
   - Approaching monthly limit (25% remaining)
   - 3 villages over budget (€8+ each)
   
   🔧 Optimization suggestions:
   - Enable aggressive caching for 12 villages
   - Reduce pre-population depth for low-tier villages
   ```

2. **Caching Strategy**
   - Cache scraped data (90 days)
   - Cache AI responses (until data changes)
   - Cache grant content blocks (until grant updates)
   - Reduces costs by 60-80% for repeat operations

3. **Tiered Features**
   ```
   Free villages (non-paying):
   - Basic map presence
   - No pre-population
   - No AI generation
   
   Lite villages (€200/year):
   - Pre-population (Level 1 only)
   - 1 identity option
   - 3 project plans
   
   Partner villages (€500/year):
   - Full pre-population
   - 3 identity options
   - 10 project plans
   - AI chatbot (100 questions/month)
   - Grant application kits
   
   Flagship villages (€1000/year):
   - Everything + priority support
   - Unlimited AI chatbot
   - Custom features
   ```

4. **Performance Monitoring**
   - API response times
   - Background job completion times
   - User satisfaction scores
   - Cost per feature
   - Profit margin per village

5. **Alerts & Limits**
   - Email if monthly budget 80% used
   - Auto-pause expensive operations if exceeded
   - Suggest upgrades to users hitting limits

**Timeline:** 2 weeks

---

### Phase L: Testing, Polish & Launch 🚀 GO LIVE
**Status:** Week 35-36 (2 weeks)

**Final Checklist:**

1. **End-to-End Testing**
   - Complete full cycle for Chirac
   - Complete full cycle for 2-3 test villages
   - Verify all integrations work
   - Load testing (100+ concurrent users)

2. **UI/UX Polish**
   - Fix any remaining visual issues
   - Mobile optimization
   - Loading states & progress indicators
   - Error messages (user-friendly)
   - Success celebrations 🎉

3. **Documentation**
   - User guide for mayors
   - Video tutorials (5-10 minutes each)
   - FAQ section
   - Email templates for onboarding

4. **Legal & Compliance**
   - Privacy policy
   - Terms of service
   - GDPR compliance (data export, deletion)
   - Cookie consent

5. **Launch Plan**
   - Soft launch: 5 pilot villages
   - Gather feedback
   - Fix critical issues
   - Public launch: Marketing campaign
   - PR: "AI Platform Helps Dying Villages Revive"

**Timeline:** 2 weeks

---

## 📊 COMPLETE TIMELINE SUMMARY

| Phase | Duration | Weeks | Status |
|-------|----------|-------|--------|
| **Phase A: Backend Foundation** | 12 weeks | 0-12 | ✅ COMPLETE |
| **Phase B: Public Frontend** | 1-2 weeks | 13-14 | ⏳ 80% done |
| **Phase C: Admin Core Tools** | 2-3 weeks | 14-16 | ⏳ 60% done |
| **Phase D: Real AI + RAG** | 2-3 weeks | 17-19 | 📋 Planned |
| **Phase E: Pre-Population Engine** | 2-3 weeks | 20-22 | 📋 Planned |
| **Phase F: Photo Intelligence** | 1-2 weeks | 23-24 | 📋 Planned |
| **Phase G: Multiple Identities** | 1 week | 25 | 📋 Planned |
| **Phase H: Project Tools** | 3-4 weeks | 26-29 | 📋 Planned |
| **Phase I: Grant Kits** | 2-3 weeks | 30-32 | 📋 Planned |
| **Phase J: Public Mini-Sites** | 1-2 weeks | 33-34 | 📋 Planned |
| **Phase K: Cost Monitoring** | 2 weeks | 35-36 | 📋 Planned |
| **Phase L: Testing & Launch** | 2 weeks | 37-38 | 📋 Planned |
| **TOTAL** | **~38 weeks** | **9 months** | |

---

## 💰 COST ANALYSIS PER VILLAGE

| Feature | Cost |
|---------|------|
| Initial deep scrape | $0.50 |
| Pre-populate audit | $0.30 |
| Photo analysis (20 photos) | $0.20 |
| Generate 3 identity options | $1.50 |
| Generate 5 project plans | $1.25 |
| Generate 3 grant kits | $1.00 |
| AI chatbot (100 questions/year) | $3.00 |
| **Total Year 1** | **$7.75** |
| **Subsequent Years** | **$3-4** (updates + chatbot) |

**Revenue:** €500-1000/year  
**Infrastructure:** ~$0.25/year  
**Total Cost:** ~$8/year  
**Profit Margin:** 98%+ ✅

---

## 🎯 KEY MILESTONES

| Milestone | Week | Description |
|-----------|------|-------------|
| **M1: Foundation Complete** | 12 | ✅ Backend + basic frontend done |
| **M2: Identity Wizard Live** | 16 | ⏳ Mayors can do audits (mock AI) |
| **M3: Real AI Deployed** | 19 | 🎯 Actual identity generation works |
| **M4: Pre-Population Works** | 22 | 🎯 Auto-research saves 60% effort |
| **M5: Full Project Tools** | 29 | 🎯 End-to-end project execution |
| **M6: Grant Kits Ready** | 32 | 🎯 Complete funding support |
| **M7: Public Launch** | 38 | 🚀 Open to all French villages |

---

## 🚦 CURRENT STATUS (Week 13)

**Where we are:**
- ✅ Backend solid (27 tables, APIs working)
- ✅ Design system done
- ✅ Map explorer working
- ✅ Identity wizard complete (mock AI)
- ✅ Login working

**What's next:**
1. Finish Phase B (remaining public pages) - 1 week
2. Finish Phase C (mobile capture, CRUD) - 2 weeks
3. Start Phase D (real AI + RAG) - CRITICAL

**Recommended focus:**
Skip the remaining polish in Phases B/C and jump straight to Phase D (Real AI). The mock is working, let's make it REAL. We can circle back to CRUD pages later.

---

## ⚡ FAST-TRACK OPTION

If you want to prove the concept faster:

**Sprint to MVP (8-10 weeks):**
1. Phase D: Real AI + RAG (3 weeks)
2. Phase E: Basic pre-population (2 weeks)
3. Phase F: Photo integration (1 week)
4. Phase G: Multiple identities (1 week)
5. Polish Chirac as perfect demo (1 week)

**Launch with:**
- Working identity audit (real AI)
- Pre-populated fields (60% done)
- Photo upload capability
- 2-3 identity options
- Case study references
- Funding matches

**Skip for now:**
- Project execution tools (Phase H)
- Grant kits (Phase I)
- Can add in Phase 2 after proving concept

**Result:** Chirac as perfect demo in 8-10 weeks, then sell to other villages

---

## 📋 FUTURE PHASES (Post-Launch)

### Phase M: UK Expansion
- UK funding database (Heritage Fund, etc.)
- UK archives integration
- Stevenage pilot

### Phase N: Advanced Features
- Aides-territoires API integration
- User-submitted case studies
- Village-to-village networking
- Success metrics dashboard

### Phase O: Scale to 1000+ Villages
- Performance optimization
- Multi-language support (Occitan, Breton, etc.)
- White-label for regions
- API for third-party integrations

---

## 14. WORKING INSTRUCTIONS FOR CLAUDE CODE

### Approach:
1. **Read first** - Always read relevant files before proposing changes
2. **Vertical slices** - Complete one flow end-to-end before moving to next
3. **Small commits** - Frequent commits with clear messages
4. **Design system** - Apply colours, spacing, components consistently

### Order of Implementation:
1. ✅ Backend: New tables + field migrations
2. 🔄 Public: Map page with filters → Village page → Route page
3. Admin: Layout → Identity wizard → CRUD pages
4. AI Enhancement: Case studies → Funding → Enhanced generator
5. Polish: SEO, search logging, sponsor tracking

### Don't:
- Rewrite entire files unnecessarily
- Change data model without discussing
- Skip the design system
- Leave features half-implemented

### When implementing AI Enhancement (Phase D):
1. Create revival_case_studies and funding_programs tables
2. Create CRUD APIs for both
3. Seed with initial data (10-20 each)
4. Update identity generator to query similar case studies
5. Add funding matching to project suggestions
6. Build admin UI for managing both databases
