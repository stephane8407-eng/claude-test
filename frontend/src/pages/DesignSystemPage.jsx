/**
 * Design System Preview Page
 *
 * URL: /design-system
 *
 * Showcases all UI components for verification and documentation.
 */
import { useState } from 'react';
import { Button, Card, ThemeChip, SponsorCard, SponsorBadge, RouteCard } from '../components/ui';

// Sample data for demos
const SAMPLE_SPONSOR = {
  name: 'Crédit Agricole',
  slug: 'credit-agricole',
  logo_url: 'https://upload.wikimedia.org/wikipedia/fr/thumb/4/4f/Logo_CA.svg/200px-Logo_CA.svg.png',
  website_url: 'https://www.credit-agricole.fr',
  short_description: 'Votre partenaire bancaire local pour tous vos projets.',
  sector: 'bank',
};

const SAMPLE_ROUTE = {
  name: 'Sentier des Étangs',
  slug: 'sentier-des-etangs',
  description: 'Une balade paisible à travers les étangs historiques de la région.',
  hero_image_url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800',
  distance_km: 5.2,
  duration_minutes: 90,
  difficulty: 'easy',
  route_type: 'walk',
  school_friendly: true,
  themes: ['ponds', 'forests', 'medieval'],
  village: { name: 'Chirac', slug: 'chirac' },
};

const SAMPLE_THEMES = ['ww2', 'medieval', 'ponds', 'chateaux', 'school_friendly'];

export function DesignSystemPage() {
  const [selectedThemes, setSelectedThemes] = useState([]);

  const toggleTheme = (theme) => {
    setSelectedThemes((prev) =>
      prev.includes(theme)
        ? prev.filter((t) => t !== theme)
        : [...prev, theme]
    );
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] py-12 px-6">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12">
          <h1 className="text-[var(--font-size-3xl)] font-bold text-[var(--color-text)] mb-2">
            SPV Design System
          </h1>
          <p className="text-[var(--color-text-muted)]">
            Component library for SPV Treasure Map V1
          </p>
        </header>

        {/* Colors */}
        <Section title="Colors" description="Primary teal + secondary lilac palette">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <ColorSwatch name="Primary" var="--color-primary" />
            <ColorSwatch name="Primary Hover" var="--color-primary-hover" />
            <ColorSwatch name="Primary Light" var="--color-primary-light" textDark />
            <ColorSwatch name="Secondary" var="--color-secondary" />
            <ColorSwatch name="Secondary Hover" var="--color-secondary-hover" />
            <ColorSwatch name="Secondary Light" var="--color-secondary-light" textDark />
            <ColorSwatch name="Background" var="--color-background" textDark />
            <ColorSwatch name="Surface" var="--color-surface" textDark />
            <ColorSwatch name="Text" var="--color-text" />
            <ColorSwatch name="Text Muted" var="--color-text-muted" />
            <ColorSwatch name="Border" var="--color-border" textDark />
            <ColorSwatch name="Success" var="--color-success" />
          </div>
        </Section>

        {/* Buttons */}
        <Section title="Buttons" description="Primary, secondary, outline, ghost variants">
          <div className="space-y-6">
            {/* Variants */}
            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">Variants</h4>
              <div className="flex flex-wrap gap-3">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
              </div>
            </div>

            {/* Sizes */}
            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">Sizes</h4>
              <div className="flex flex-wrap items-center gap-3">
                <Button size="sm">Small</Button>
                <Button size="md">Medium</Button>
                <Button size="lg">Large</Button>
              </div>
            </div>

            {/* States */}
            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">States</h4>
              <div className="flex flex-wrap gap-3">
                <Button disabled>Disabled</Button>
                <Button loading>Loading</Button>
                <Button fullWidth>Full Width</Button>
              </div>
            </div>

            {/* With icons */}
            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">With Icons</h4>
              <div className="flex flex-wrap gap-3">
                <Button
                  leftIcon={
                    <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-11.25a.75.75 0 00-1.5 0v2.5h-2.5a.75.75 0 000 1.5h2.5v2.5a.75.75 0 001.5 0v-2.5h2.5a.75.75 0 000-1.5h-2.5v-2.5z" clipRule="evenodd" />
                    </svg>
                  }
                >
                  Add Item
                </Button>
                <Button
                  variant="outline"
                  rightIcon={
                    <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                      <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
                    </svg>
                  }
                >
                  Continue
                </Button>
              </div>
            </div>
          </div>
        </Section>

        {/* Cards */}
        <Section title="Cards" description="Flexible container with optional hero image">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card title="Simple Card" subtitle="With title and subtitle">
              <p className="text-[var(--color-text-muted)]">
                This is the card content. Cards have a 12px border radius and subtle shadow.
              </p>
            </Card>

            <Card
              heroImage="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
              heroImageAlt="Mountain landscape"
              title="Card with Hero"
              subtitle="Includes image"
            >
              <p className="text-[var(--color-text-muted)]">
                Cards can have hero images that scale on hover.
              </p>
            </Card>

            <Card
              to="/villages/chirac"
              title="Clickable Card"
              subtitle="Links to another page"
            >
              <p className="text-[var(--color-text-muted)]">
                Click this card to navigate (uses React Router).
              </p>
            </Card>

            <Card
              title="Card with Footer"
              subtitle="Has action buttons"
              footer={
                <div className="flex gap-2">
                  <Button size="sm" variant="outline">Cancel</Button>
                  <Button size="sm">Save</Button>
                </div>
              }
            >
              <p className="text-[var(--color-text-muted)]">
                Footer section for actions or metadata.
              </p>
            </Card>
          </div>
        </Section>

        {/* Theme Chips */}
        <Section title="Theme Chips" description="Clickable tags for filtering by theme">
          <div className="space-y-6">
            {/* Variants */}
            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">Variants</h4>
              <div className="flex flex-wrap gap-2">
                <ThemeChip theme="ww2" variant="primary" />
                <ThemeChip theme="medieval" variant="secondary" />
                <ThemeChip theme="ponds" variant="outline" />
              </div>
            </div>

            {/* Sizes */}
            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">Sizes</h4>
              <div className="flex flex-wrap items-center gap-2">
                <ThemeChip theme="forests" size="sm" />
                <ThemeChip theme="chateaux" size="md" />
                <ThemeChip theme="legends" size="lg" />
              </div>
            </div>

            {/* Interactive */}
            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">Interactive Selection</h4>
              <div className="flex flex-wrap gap-2 mb-3">
                {SAMPLE_THEMES.map((theme) => (
                  <ThemeChip
                    key={theme}
                    theme={theme}
                    selected={selectedThemes.includes(theme)}
                    onClick={toggleTheme}
                  />
                ))}
              </div>
              <p className="text-sm text-[var(--color-text-muted)]">
                Selected: {selectedThemes.length > 0 ? selectedThemes.join(', ') : 'none'}
              </p>
            </div>

            {/* Removable */}
            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">Removable</h4>
              <div className="flex flex-wrap gap-2">
                <ThemeChip theme="ww2" removable onRemove={(t) => alert(`Remove: ${t}`)} />
                <ThemeChip theme="medieval" removable onRemove={(t) => alert(`Remove: ${t}`)} />
              </div>
            </div>
          </div>
        </Section>

        {/* Sponsor Cards */}
        <Section title="Sponsor Cards" description="Display partners with tracked links">
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">Full Card</h4>
              <div className="max-w-md">
                <SponsorCard sponsor={SAMPLE_SPONSOR} slotId={1} />
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">Compact Card</h4>
              <div className="max-w-sm">
                <SponsorCard sponsor={SAMPLE_SPONSOR} slotId={1} compact />
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-[var(--color-text-muted)] mb-3">Inline Badge</h4>
              <p className="text-[var(--color-text)]">
                Cette route est <SponsorBadge sponsor={SAMPLE_SPONSOR} slotId={1} label="soutenue par" />
              </p>
            </div>
          </div>
        </Section>

        {/* Route Cards */}
        <Section title="Route Cards" description="Display walking routes with stats">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <RouteCard route={SAMPLE_ROUTE} />

            <RouteCard
              route={{
                ...SAMPLE_ROUTE,
                name: 'Trail des Collines',
                difficulty: 'hard',
                route_type: 'hike',
                distance_km: 12.5,
                duration_minutes: 240,
                school_friendly: false,
                themes: ['mountains', 'forests'],
              }}
            />

            <RouteCard
              route={{
                ...SAMPLE_ROUTE,
                name: 'Circuit Vélo',
                difficulty: 'medium',
                route_type: 'cycle',
                distance_km: 25,
                duration_minutes: 120,
                hero_image_url: null,
              }}
              showVillage
            />
          </div>
        </Section>

        {/* Spacing */}
        <Section title="Spacing Scale" description="4px grid system">
          <div className="flex flex-wrap items-end gap-4">
            {[1, 2, 3, 4, 6, 8, 12, 16].map((n) => (
              <div key={n} className="text-center">
                <div
                  className="bg-[var(--color-primary)]"
                  style={{
                    width: `var(--spacing-${n})`,
                    height: `var(--spacing-${n})`,
                  }}
                />
                <span className="text-xs text-[var(--color-text-muted)] mt-1 block">
                  {n} ({n * 4}px)
                </span>
              </div>
            ))}
          </div>
        </Section>

        {/* Border Radius */}
        <Section title="Border Radius" description="Consistent corner rounding">
          <div className="flex flex-wrap gap-6">
            {['sm', 'md', 'lg', 'xl', 'full'].map((size) => (
              <div key={size} className="text-center">
                <div
                  className="w-16 h-16 bg-[var(--color-primary)]"
                  style={{ borderRadius: `var(--radius-${size})` }}
                />
                <span className="text-xs text-[var(--color-text-muted)] mt-2 block">
                  {size}
                </span>
              </div>
            ))}
          </div>
        </Section>

        {/* Shadows */}
        <Section title="Shadows" description="Elevation levels">
          <div className="flex flex-wrap gap-6">
            {['sm', 'md', 'lg', 'xl', 'card'].map((size) => (
              <div key={size} className="text-center">
                <div
                  className="w-20 h-20 bg-[var(--color-surface)] rounded-lg flex items-center justify-center"
                  style={{ boxShadow: `var(--shadow-${size})` }}
                >
                  <span className="text-xs text-[var(--color-text-muted)]">{size}</span>
                </div>
              </div>
            ))}
          </div>
        </Section>
      </div>
    </div>
  );
}

// Helper components
function Section({ title, description, children }) {
  return (
    <section className="mb-16">
      <div className="mb-6">
        <h2 className="text-[var(--font-size-2xl)] font-semibold text-[var(--color-text)]">
          {title}
        </h2>
        {description && (
          <p className="text-[var(--color-text-muted)] mt-1">{description}</p>
        )}
      </div>
      {children}
    </section>
  );
}

function ColorSwatch({ name, var: cssVar, textDark = false }) {
  return (
    <div className="text-center">
      <div
        className="h-16 rounded-lg mb-2 flex items-center justify-center"
        style={{ backgroundColor: `var(${cssVar})` }}
      >
        <span
          className="text-xs font-mono"
          style={{ color: textDark ? 'var(--color-text)' : 'white' }}
        >
          {cssVar.replace('--color-', '')}
        </span>
      </div>
      <span className="text-xs text-[var(--color-text-muted)]">{name}</span>
    </div>
  );
}
