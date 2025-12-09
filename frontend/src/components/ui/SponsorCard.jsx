/**
 * SponsorCard Component
 *
 * Displays sponsor information with logo, name, description, and tracked link.
 * Click tracking is done via the /api/sponsor-click/[slotId] endpoint.
 */
import './SponsorCard.css';

function SponsorCard({
  sponsor,
  slotId,
  position = 'primary',
  showDescription = true,
  compact = false,
  className = '',
  ...props
}) {
  // Build the tracked click URL
  const trackedUrl = slotId
    ? `/api/sponsor-click/${slotId}`
    : sponsor?.website_url;

  const classes = [
    'spv-sponsor-card',
    `spv-sponsor-card--${position}`,
    compact && 'spv-sponsor-card--compact',
    className
  ].filter(Boolean).join(' ');

  if (!sponsor) {
    return null;
  }

  return (
    <a
      href={trackedUrl}
      target="_blank"
      rel="noopener noreferrer sponsored"
      className={classes}
      {...props}
    >
      <div className="spv-sponsor-card__logo-container">
        {sponsor.logo_url ? (
          <img
            src={sponsor.logo_url}
            alt={`${sponsor.name} logo`}
            className="spv-sponsor-card__logo"
            loading="lazy"
          />
        ) : (
          <div className="spv-sponsor-card__logo-placeholder">
            <span>{sponsor.name.charAt(0)}</span>
          </div>
        )}
      </div>

      <div className="spv-sponsor-card__content">
        <h4 className="spv-sponsor-card__name">{sponsor.name}</h4>

        {showDescription && sponsor.short_description && (
          <p className="spv-sponsor-card__description">
            {sponsor.short_description}
          </p>
        )}

        {sponsor.sector && (
          <span className="spv-sponsor-card__sector">{sponsor.sector}</span>
        )}
      </div>

      <div className="spv-sponsor-card__arrow">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M5.22 14.78a.75.75 0 001.06 0l7.22-7.22v5.69a.75.75 0 001.5 0v-7.5a.75.75 0 00-.75-.75h-7.5a.75.75 0 000 1.5h5.69l-7.22 7.22a.75.75 0 000 1.06z" clipRule="evenodd" />
        </svg>
      </div>
    </a>
  );
}

/**
 * SponsorBadge - Smaller inline sponsor mention
 * Usage: "Soutenu par [Sponsor]"
 */
function SponsorBadge({ sponsor, slotId, label = 'Soutenu par' }) {
  const trackedUrl = slotId
    ? `/api/sponsor-click/${slotId}`
    : sponsor?.website_url;

  if (!sponsor) {
    return null;
  }

  return (
    <span className="spv-sponsor-badge">
      <span className="spv-sponsor-badge__label">{label}</span>
      <a
        href={trackedUrl}
        target="_blank"
        rel="noopener noreferrer sponsored"
        className="spv-sponsor-badge__link"
      >
        {sponsor.logo_url && (
          <img
            src={sponsor.logo_url}
            alt=""
            className="spv-sponsor-badge__logo"
          />
        )}
        <span className="spv-sponsor-badge__name">{sponsor.name}</span>
      </a>
    </span>
  );
}

export { SponsorCard, SponsorBadge };
