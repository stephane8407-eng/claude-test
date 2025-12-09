/**
 * RouteCard Component
 *
 * Displays route information: name, distance, duration, difficulty, themes.
 */
import { Link } from 'react-router-dom';
import { ThemeChip } from './ThemeChip';
import './RouteCard.css';

// Icons for route types
const RouteTypeIcon = ({ type }) => {
  switch (type) {
    case 'walk':
      return (
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M13.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM9.8 8.9L7 23h2.1l1.8-8 2.1 2v6h2v-7.5l-2.1-2 .6-3C14.8 12 16.8 13 19 13v-2c-1.9 0-3.5-1-4.3-2.4l-1-1.6c-.4-.6-1-1-1.7-1-.3 0-.5.1-.8.1L6 8.3V13h2V9.6l1.8-.7"/>
        </svg>
      );
    case 'hike':
      return (
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M13.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM17.5 10.78c-.29-.27-.65-.38-1-.3l-2.84.57.17-.88-1.31-.07c-.62-.03-1.15.33-1.4.87l-1.18 2.5-.69-.51-1.89 1.55-2.06-1.97L4 14.08l3.73 3.53L9 16.8l.6 1.9-2.1 5.3H10l1.3-4 2.2 2V23h2v-4.32c0-.71-.23-1.43-.7-2l-1.65-2.01 1.2-2.55 1.89 1.32c.4.28.86.43 1.33.43.17 0 .35-.02.53-.06l3.2-.64v-2.11l-3.3.72"/>
        </svg>
      );
    case 'cycle':
      return (
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M15.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM5 12c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5zm5.8-10l2.4 2.4-2.2 2.2-1-1-2 2v5h-2v-6l3-3 1-1.6-2-2h-.5v-1h4v1h-.5l1.8 2zm8.2 1.5c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5z"/>
        </svg>
      );
    case 'trail_run':
      return (
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M13.49 5.48c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm-3.6 13.9l1-4.4 2.1 2v6h2v-7.5l-2.1-2 .6-3c1.3 1.5 3.3 2.5 5.5 2.5v-2c-1.9 0-3.5-1-4.3-2.4l-1-1.6c-.4-.6-1-1-1.7-1-.3 0-.5.1-.8.1l-5.2 2.2v4.7h2v-3.4l1.8-.7-1.6 8.1-4.9-1-.4 2 7 1.4z"/>
        </svg>
      );
    default:
      return (
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M21 4H7V2H5v20h2v-8h14l-2-5 2-5zm-6 5c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2z"/>
        </svg>
      );
  }
};

// Difficulty badge colors
const DIFFICULTY_CONFIG = {
  easy: { label: 'Facile', color: 'easy' },
  medium: { label: 'Moyen', color: 'medium' },
  hard: { label: 'Difficile', color: 'hard' },
};

function RouteCard({
  route,
  to = null,
  showVillage = false,
  showThemes = true,
  maxThemes = 3,
  className = '',
  ...props
}) {
  const {
    name,
    slug,
    description,
    hero_image_url,
    distance_km,
    duration_minutes,
    difficulty,
    route_type,
    school_friendly,
    themes = [],
    village,
  } = route || {};

  // Format duration
  const formatDuration = (minutes) => {
    if (!minutes) return null;
    if (minutes < 60) return `${minutes} min`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h${mins}` : `${hours}h`;
  };

  const classes = [
    'spv-route-card',
    className
  ].filter(Boolean).join(' ');

  const linkTo = to || (slug ? `/routes/${slug}` : null);

  const difficultyConfig = DIFFICULTY_CONFIG[difficulty] || {};

  const content = (
    <>
      {/* Hero image */}
      {hero_image_url && (
        <div className="spv-route-card__hero">
          <img
            src={hero_image_url}
            alt={name}
            className="spv-route-card__hero-image"
            loading="lazy"
          />
          {school_friendly && (
            <span className="spv-route-card__badge spv-route-card__badge--school">
              Scolaire
            </span>
          )}
        </div>
      )}

      <div className="spv-route-card__body">
        {/* Header */}
        <div className="spv-route-card__header">
          <h3 className="spv-route-card__name">{name}</h3>
          {showVillage && village && (
            <p className="spv-route-card__village">{village.name}</p>
          )}
        </div>

        {/* Stats row */}
        <div className="spv-route-card__stats">
          {route_type && (
            <span className="spv-route-card__stat spv-route-card__stat--type">
              <RouteTypeIcon type={route_type} />
              <span>{route_type}</span>
            </span>
          )}

          {distance_km && (
            <span className="spv-route-card__stat">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
              </svg>
              <span>{distance_km} km</span>
            </span>
          )}

          {duration_minutes && (
            <span className="spv-route-card__stat">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
              </svg>
              <span>{formatDuration(duration_minutes)}</span>
            </span>
          )}

          {difficulty && (
            <span className={`spv-route-card__difficulty spv-route-card__difficulty--${difficultyConfig.color}`}>
              {difficultyConfig.label}
            </span>
          )}
        </div>

        {/* Description */}
        {description && (
          <p className="spv-route-card__description">{description}</p>
        )}

        {/* Themes */}
        {showThemes && themes.length > 0 && (
          <div className="spv-route-card__themes">
            {themes.slice(0, maxThemes).map((theme) => (
              <ThemeChip key={theme} theme={theme} size="sm" />
            ))}
            {themes.length > maxThemes && (
              <span className="spv-route-card__more-themes">
                +{themes.length - maxThemes}
              </span>
            )}
          </div>
        )}
      </div>
    </>
  );

  if (linkTo) {
    return (
      <Link to={linkTo} className={classes} {...props}>
        {content}
      </Link>
    );
  }

  return (
    <div className={classes} {...props}>
      {content}
    </div>
  );
}

export { RouteCard };
