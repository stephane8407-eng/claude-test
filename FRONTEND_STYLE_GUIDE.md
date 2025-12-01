# SPV TREASURE MAP - FRONTEND STYLE GUIDE

**For Claude Code: Read this file before any frontend/UI work.**

---

## 1. VISUAL PHILOSOPHY

### What We Want
- **Calm, professional, trustworthy** - like a quality tourism or heritage site
- **Map-focused** - the map is the hero, not marketing fluff
- **Clean and breathable** - generous whitespace, not cramped
- **Modern but warm** - heritage/outdoors feel, not corporate SaaS

### What We DON'T Want
- ❌ Electric blue gradients
- ❌ "AI dashboard" aesthetic with confidence scores
- ❌ Generic SaaS landing page style
- ❌ Cramped text close to borders
- ❌ Tiny fonts that are hard to read
- ❌ Components that look AI-generated or template-y

---

## 2. COLOR PALETTE

### Primary: Teal `#008080`
- Use for: Buttons, links, headings, map markers, active states
- This is the MAIN accent color

### Secondary: Lilac `#C8A2C8`
- Use SPARINGLY as a light highlight only
- Secondary buttons, subtle accents, hover states
- NOT for large areas or gradients

### Backgrounds
- `#FFFFFF` - Primary background (white)
- `#F5F5F5` - Secondary background (light grey)
- `#FAFAFA` - Card backgrounds

### Text
- `#1F2937` - Primary text (dark grey, not pure black)
- `#6B7280` - Secondary/muted text
- `#9CA3AF` - Placeholder text

### DO NOT USE
- ❌ Electric blue (`#3B82F6` or similar)
- ❌ Full-width colored gradients
- ❌ Bright saturated backgrounds

---

## 3. TYPOGRAPHY

### Font Stack
```css
font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Sizes (Desktop)
- **Page title:** 32-36px, font-weight 700
- **Section title:** 24px, font-weight 600
- **Card title:** 18-20px, font-weight 600
- **Body text:** 16px (MINIMUM - never smaller on main content)
- **Small labels:** 14px (only for metadata, badges)
- **Tiny text:** 12px (only for legal, footnotes)

### Rules
- ✅ Base font size: 16px minimum for all readable content
- ✅ Line height: 1.5 for body text, 1.3 for headings
- ❌ Never use font-size below 14px for user-facing content
- ❌ Never use light font-weight (300) for body text

---

## 4. SPACING

### Base Unit: 4px grid
- `4px` - Tiny gaps
- `8px` - Small gaps (between inline elements)
- `12px` - Medium-small
- `16px` - Standard padding inside cards (MINIMUM)
- `24px` - Section gaps
- `32px` - Large section spacing
- `48px` - Page section breaks
- `64px` - Major layout gaps

### Card Padding
- ✅ Minimum 16px padding inside all cards
- ✅ Minimum 12px padding on mobile
- ❌ Never less than 12px padding

### Rules
- ✅ Generous whitespace - let the layout breathe
- ✅ Consistent spacing throughout
- ❌ Never cram content against borders

---

## 5. COMPONENTS

### Buttons
```css
/* Primary Button */
background: #008080;
color: white;
padding: 12px 24px;
border-radius: 8px;
font-size: 16px;
font-weight: 500;

/* Secondary Button */
background: white;
color: #008080;
border: 1px solid #008080;
padding: 12px 24px;
border-radius: 8px;

/* Ghost Button */
background: transparent;
color: #008080;
padding: 12px 24px;
```

### Cards
```css
background: white;
border: 1px solid #E5E7EB;
border-radius: 12px;
padding: 16px; /* MINIMUM */
box-shadow: 0 1px 3px rgba(0,0,0,0.08);
```

### Cards - DO NOT
- ❌ Full-width colored headers/bars
- ❌ Gradient backgrounds
- ❌ Less than 16px padding
- ❌ "Dashboard widget" aesthetic

### Input Fields
```css
padding: 12px 16px;
border: 1px solid #D1D5DB;
border-radius: 8px;
font-size: 16px;

/* Placeholder */
color: #9CA3AF;

/* Focus */
border-color: #008080;
outline: none;
box-shadow: 0 0 0 3px rgba(0, 128, 128, 0.1);
```

### Search Box Rules
- ✅ Placeholder text disappears on focus/typing
- ✅ Icon positioned clearly (left side, not overlapping)
- ✅ Adequate padding so text doesn't touch icon

---

## 6. PAGE LAYOUTS

### Homepage (`/`)
- Simple marketing page explaining SPV
- Hero section with tagline
- "Explore the map" CTA button
- "For communes" section
- NOT the map itself

### Map Explorer (`/explore`)
- Large map taking most of viewport
- Filter panel on left (desktop) or drawer (mobile)
- Clean, minimal chrome
- Focus on the map content

### Village Page (`/villages/[slug]`)
- Clean white header with village name + tagline
- Small metric badges (not big colored bars)
- Embedded map
- Theme stories (NOT raw identity audit)
- Place cards
- Route cards
- Partners section

---

## 7. MAP PAGE SPECIFICS

### Filter Panel
- Font size: 16px for labels, 14px for checkboxes
- Group headings: 16px, font-weight 600
- Adequate spacing between groups (16px minimum)
- Search box: Clear placeholder behavior

### Map Markers
- Size: At least 24px diameter
- Teal for villages
- Distinct colors for POI types if needed
- Clickable with clear hover state

### Map Popups
- Clean white background
- 16px padding minimum
- Village name, tagline, theme chips
- "View village" button

---

## 8. VILLAGE PAGE SPECIFICS

### Header
- ✅ White background
- ✅ Village name: 32px, font-weight 700
- ✅ Tagline: 18px, text-muted color
- ✅ Metrics as small badges (not big bars)
- ❌ NO full-width blue/gradient banners

### Identity/Theme Display (PUBLIC)
Show themes as friendly story cards:
- Title: "Forges of Resilience" (not "Identity Theme #1")
- 2-3 bullet points explaining the theme
- 1-2 tourism/project ideas
- "Explore this theme" link

DO NOT SHOW on public pages:
- ❌ "Identity Theme #1/#2/#3" labels
- ❌ Confidence percentages
- ❌ AI analysis details
- ❌ SWOT data
- ❌ Any "audit" terminology

### Place Cards
- Small image or tasteful placeholder (not big blue bars)
- Name + subtitle
- 2-3 tags (e.g., "Pond • Private")
- Teal "Learn more" button
- Reduce columns (2-3 max) so layout breathes

### Route Cards
- Image or map snippet
- Route name
- Distance, duration, difficulty badges
- Theme chips
- "View route" button

---

## 9. EVENT/CONFLICT POPUPS

When clicking a conflict on the map, show:
- Event name
- Date or period
- 1-2 lines of description
- "View details" link

If no description exists:
- Either hide from public map
- Or show minimal info with "Details coming soon"

---

## 10. ADMIN VS PUBLIC SEPARATION

### Public Pages Show:
- Curated identity narratives
- Human-friendly theme stories
- Places, routes, events (with descriptions)
- Sponsor information

### Admin Pages Show:
- Raw identity audit data
- Confidence scores
- AI analysis details
- SWOT summaries
- "Theme #1/#2/#3" labels
- Edit controls

### Rule
Create SEPARATE components if needed:
- `IdentityThemeCard.jsx` - for public (friendly display)
- `IdentityAuditCard.jsx` - for admin (raw data + scores)

---

## 11. RESPONSIVE DESIGN

### Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Mobile Rules
- Filter panel becomes drawer/modal
- Single column layouts for cards
- Touch-friendly tap targets (44px minimum)
- Font sizes same or larger than desktop

---

## 12. CHECKLIST BEFORE COMMITTING UI CHANGES

Before any frontend commit, verify:

- [ ] Base font size is 16px minimum
- [ ] Card padding is 16px minimum
- [ ] No electric blue or large gradients
- [ ] Teal is primary accent, lilac only as subtle highlight
- [ ] No identity audit details on public pages
- [ ] Placeholder text disappears on input focus
- [ ] Layout has generous whitespace
- [ ] Components don't look "AI-generated" or generic
- [ ] Matches the calm, map-page visual language

---

## 13. REFERENCE SITES (Aesthetic Inspiration)

For the overall feel, reference:
- **Komoot** - clean outdoor/hiking maps
- **AllTrails** - route displays
- **French heritage sites** - cultural, warm tone
- **NOT:** Generic SaaS dashboards, AI tools, corporate sites

---

## 14. QUICK REFERENCE

| Element | Size/Value |
|---------|------------|
| Primary color | `#008080` (Teal) |
| Secondary color | `#C8A2C8` (Lilac - sparingly) |
| Background | `#FFFFFF` or `#F5F5F5` |
| Base font size | 16px minimum |
| Card padding | 16px minimum |
| Card border-radius | 12px |
| Button border-radius | 8px |
| Spacing unit | 4px grid |

---

**Claude Code: Apply these rules to ALL frontend work. When in doubt, choose the calmer, cleaner option.**
