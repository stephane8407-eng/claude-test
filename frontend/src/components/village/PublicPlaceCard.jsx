/**
 * PublicPlaceCard Component
 *
 * Clean place card for public village page.
 * Small image placeholder, name + subtitle, 2-3 tags, teal button.
 */
import { Link } from 'react-router-dom';
import './PublicPlaceCard.css';

export function PublicPlaceCard({ place, villageSlug }) {
  const {
    id,
    name,
    poi_type,
    access,
    description,
    hero_image_url,
    image_url,
  } = place;

  const imageUrl = hero_image_url || image_url;

  // Build tags array
  const tags = [];
  if (poi_type) tags.push(formatTag(poi_type));
  if (access) tags.push(formatAccess(access));

  return (
    <article className="spv-place-card">
      {/* Image or placeholder */}
      <div className="spv-place-card__image">
        {imageUrl ? (
          <img src={imageUrl} alt={name} />
        ) : (
          <div className="spv-place-card__placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
            </svg>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="spv-place-card__content">
        <h3 className="spv-place-card__name">{name}</h3>

        {description && (
          <p className="spv-place-card__description">
            {description.length > 100 ? `${description.slice(0, 100)}...` : description}
          </p>
        )}

        {/* Tags */}
        {tags.length > 0 && (
          <div className="spv-place-card__tags">
            {tags.map((tag, index) => (
              <span key={index} className="spv-place-card__tag">{tag}</span>
            ))}
          </div>
        )}

        {/* Action */}
        <Link
          to={`/places/${place.slug || id}`}
          className="spv-place-card__button"
        >
          En savoir plus
        </Link>
      </div>
    </article>
  );
}

function formatTag(type) {
  const typeLabels = {
    pond: 'Étang',
    chapel: 'Chapelle',
    church: 'Église',
    castle: 'Château',
    forge: 'Forge',
    mill: 'Moulin',
    monument: 'Monument',
    ruins: 'Ruines',
    nature: 'Nature',
  };
  return typeLabels[type?.toLowerCase()] || type;
}

function formatAccess(access) {
  const accessLabels = {
    public: 'Public',
    private: 'Privé',
    restricted: 'Accès restreint',
    ruin: 'Ruines',
  };
  return accessLabels[access?.toLowerCase()] || access;
}
