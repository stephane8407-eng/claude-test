/**
 * VillagePreviewCard Component
 *
 * Shows village preview when marker is clicked on map.
 * Displays: name, tagline, theme chips, "Voir la fiche" button
 */
import { Link } from 'react-router-dom';
import { Button, ThemeChip } from '../ui';
import './VillagePreviewCard.css';

export function VillagePreviewCard({ village, onClose }) {
  if (!village) return null;

  const {
    name,
    slug,
    summary_identity,
    hero_image_url,
    themes = [],
  } = village;

  return (
    <div className="spv-village-preview">
      {/* Close Button */}
      <button className="spv-village-preview__close" onClick={onClose} aria-label="Fermer">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>

      {/* Hero Image */}
      {hero_image_url && (
        <div className="spv-village-preview__hero">
          <img
            src={hero_image_url}
            alt={name}
            className="spv-village-preview__hero-image"
          />
        </div>
      )}

      {/* Content */}
      <div className="spv-village-preview__content">
        <h3 className="spv-village-preview__name">{name}</h3>

        {summary_identity && (
          <p className="spv-village-preview__tagline">{summary_identity}</p>
        )}

        {/* Themes */}
        {themes.length > 0 && (
          <div className="spv-village-preview__themes">
            {themes.slice(0, 3).map((theme) => (
              <ThemeChip key={theme} theme={theme} size="sm" />
            ))}
            {themes.length > 3 && (
              <span className="spv-village-preview__more">
                +{themes.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="spv-village-preview__actions">
          <Link to={`/villages/${slug}`}>
            <Button variant="primary" size="sm" fullWidth>
              Voir la fiche
              <svg viewBox="0 0 20 20" fill="currentColor" className="spv-village-preview__arrow">
                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
