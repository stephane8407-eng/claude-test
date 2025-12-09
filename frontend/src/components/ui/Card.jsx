/**
 * Card Component
 *
 * Flexible card with optional hero image, title, subtitle, and content.
 */
import { Link } from 'react-router-dom';
import './Card.css';

function Card({
  children,
  heroImage = null,
  heroImageAlt = '',
  title = null,
  subtitle = null,
  footer = null,
  to = null,
  onClick = null,
  hoverable = true,
  className = '',
  ...props
}) {
  const classes = [
    'spv-card',
    hoverable && 'spv-card--hoverable',
    (to || onClick) && 'spv-card--clickable',
    heroImage && 'spv-card--has-hero',
    className
  ].filter(Boolean).join(' ');

  const content = (
    <>
      {heroImage && (
        <div className="spv-card__hero">
          <img
            src={heroImage}
            alt={heroImageAlt}
            className="spv-card__hero-image"
            loading="lazy"
          />
        </div>
      )}
      <div className="spv-card__body">
        {(title || subtitle) && (
          <div className="spv-card__header">
            {title && <h3 className="spv-card__title">{title}</h3>}
            {subtitle && <p className="spv-card__subtitle">{subtitle}</p>}
          </div>
        )}
        {children && <div className="spv-card__content">{children}</div>}
      </div>
      {footer && <div className="spv-card__footer">{footer}</div>}
    </>
  );

  // If it's a link
  if (to) {
    return (
      <Link to={to} className={classes} {...props}>
        {content}
      </Link>
    );
  }

  // If it's clickable
  if (onClick) {
    return (
      <div
        className={classes}
        onClick={onClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            onClick(e);
          }
        }}
        {...props}
      >
        {content}
      </div>
    );
  }

  // Default static card
  return (
    <div className={classes} {...props}>
      {content}
    </div>
  );
}

export { Card };
