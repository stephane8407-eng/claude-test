/**
 * ThemeChip Component
 *
 * Clickable theme tag with teal/lilac styling.
 * Used for displaying and filtering by theme tags.
 */
import { Link } from 'react-router-dom';
import './ThemeChip.css';

// Theme display names (can be extended)
const THEME_LABELS = {
  // Historical
  ww2: 'WWII',
  ww1: 'WWI',
  hundred_years_war: 'Hundred Years War',
  wars_of_religion: 'Wars of Religion',
  roman: 'Roman',
  medieval: 'Medieval',
  villages_brules: 'Villages brûlés',

  // Nature
  ponds: 'Ponds',
  rivers: 'Rivers',
  forests: 'Forests',
  mountains: 'Mountains',
  coast: 'Coast',

  // Heritage
  chateaux: 'Châteaux',
  industrial_heritage: 'Industrial Heritage',
  roman_ruins: 'Roman Ruins',
  churches: 'Churches',

  // Culture
  folk_festival: 'Folk Festival',
  traditions: 'Traditions',
  legends: 'Legends',
  artisans: 'Artisans',

  // Practical
  school_friendly: 'School Friendly',
  family_route: 'Family Route',
  accessible: 'Accessible',
};

function ThemeChip({
  theme,
  label = null,
  variant = 'primary',
  size = 'md',
  selected = false,
  removable = false,
  onClick = null,
  onRemove = null,
  to = null,
  className = '',
  ...props
}) {
  // Get display label
  const displayLabel = label || THEME_LABELS[theme] || theme.replace(/_/g, ' ');

  const classes = [
    'spv-chip',
    'spv-theme-chip',
    `spv-theme-chip--${variant}`,
    `spv-theme-chip--${size}`,
    selected && 'spv-theme-chip--selected',
    (onClick || to) && 'spv-theme-chip--clickable',
    className
  ].filter(Boolean).join(' ');

  const content = (
    <>
      <span className="spv-theme-chip__label">{displayLabel}</span>
      {removable && (
        <button
          className="spv-theme-chip__remove"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onRemove?.(theme);
          }}
          aria-label={`Remove ${displayLabel}`}
        >
          <svg viewBox="0 0 16 16" fill="currentColor">
            <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
          </svg>
        </button>
      )}
    </>
  );

  // As a link
  if (to) {
    return (
      <Link to={to} className={classes} {...props}>
        {content}
      </Link>
    );
  }

  // As a clickable chip
  if (onClick) {
    return (
      <button type="button" className={classes} onClick={() => onClick(theme)} {...props}>
        {content}
      </button>
    );
  }

  // Static chip
  return (
    <span className={classes} {...props}>
      {content}
    </span>
  );
}

// Export theme labels for external use
ThemeChip.THEME_LABELS = THEME_LABELS;

export { ThemeChip };
