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

## 10. WORKING INSTRUCTIONS FOR CLAUDE CODE

### Approach:
1. **Read first** - Always read relevant files before proposing changes
2. **Vertical slices** - Complete one flow end-to-end before moving to next
3. **Small commits** - Frequent commits with clear messages
4. **Design system** - Apply colours, spacing, components consistently

### Order of Implementation:
1. Backend: new tables + API endpoints
2. Public frontend: map page → village page → route page
3. Admin frontend: layout → identity wizard → CRUD pages
4. Polish: SEO, search logging, sponsor tracking

### Don't:
- Rewrite entire files unnecessarily
- Change data model without discussing
- Skip the design system
- Leave features half-implemented
