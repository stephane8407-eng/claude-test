/**
 * AdminThemeCard
 *
 * Admin-only theme display with confidence score and accept/reject toggle.
 * Shows theme details with bullets and tourism ideas.
 * Handles both mock data (arrays) and real AI data (strings).
 * Supports 3-tier system with visual badges.
 */
import { useState } from 'react';
import './AdminThemeCard.css';

const DESCRIPTION_CHAR_LIMIT = 150;

/**
 * Get tier information for visual display
 */
function getTierInfo(tier) {
  const tiers = {
    1: {
      label: 'Parcours Prouvé',
      badge: 'Sécurisé',
      emoji: '🛡️',
      colorClass: 'spv-admin-theme__tier--proven',
      description: 'Basé sur des réussites avérées, faible risque'
    },
    2: {
      label: 'Innovation Ciblée',
      badge: 'Innovant',
      emoji: '💡',
      colorClass: 'spv-admin-theme__tier--innovation',
      description: 'Adapté aux atouts uniques du village'
    },
    3: {
      label: 'Vision Transformatrice',
      badge: 'Pionnier',
      emoji: '🚀',
      colorClass: 'spv-admin-theme__tier--breakthrough',
      description: 'Avant-garde, potentiel de rupture'
    }
  };
  return tiers[tier] || tiers[1];
}

/**
 * Normalize description to string format for expandable display
 * - If array: join with spaces
 * - If string: use as-is
 */
function normalizeDescriptionToString(description) {
  if (!description) return '';
  if (Array.isArray(description)) return description.join(' ');
  if (typeof description === 'string') return description;
  return '';
}

/**
 * Normalize tourism ideas to array format
 */
function normalizeTourismIdeas(ideas) {
  if (!ideas) return [];
  if (Array.isArray(ideas)) return ideas;
  if (typeof ideas === 'string') return [ideas];
  return [];
}

export function AdminThemeCard({ theme, index, isAccepted, onToggle }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const confidencePercent = Math.round((theme.confidence || 0) * 100);
  const confidenceLevel = confidencePercent >= 80 ? 'high' : confidencePercent >= 60 ? 'medium' : 'low';

  // Get tier information (use theme.tier if provided, otherwise use index directly)
  // Note: index is already 1-based when passed from parent
  const tier = theme.tier || index;
  const tierInfo = getTierInfo(tier);

  // Normalize data formats - handle both mock (array) and real AI (string) formats
  const description = normalizeDescriptionToString(theme.description);
  const tourismIdeas = normalizeTourismIdeas(theme.tourism_ideas || theme.tourismIdeas);

  // Get title - handle both formats
  const title = theme.title || theme.name || 'Thème sans titre';

  // Check if description needs truncation
  const needsTruncation = description.length > DESCRIPTION_CHAR_LIMIT;
  const displayText = isExpanded || !needsTruncation
    ? description
    : description.substring(0, DESCRIPTION_CHAR_LIMIT);

  return (
    <div className={`spv-admin-theme ${isAccepted ? 'spv-admin-theme--accepted' : 'spv-admin-theme--rejected'}`}>
      {/* Tier Badge */}
      <div className={`spv-admin-theme__tier-badge ${tierInfo.colorClass}`}>
        <span className="spv-admin-theme__tier-emoji">{tierInfo.emoji}</span>
        <span className="spv-admin-theme__tier-label">{tierInfo.badge}</span>
      </div>
      <p className="spv-admin-theme__tier-description">{tierInfo.description}</p>

      {/* Header */}
      <div className="spv-admin-theme__header">
        <span className="spv-admin-theme__number">Niveau {tier}</span>
        <span className={`spv-admin-theme__confidence spv-admin-theme__confidence--${confidenceLevel}`}>
          {confidencePercent}%
        </span>
      </div>

      {/* Title */}
      <h3 className="spv-admin-theme__title">{title}</h3>

      {/* Description with expand/collapse */}
      {description && (
        <div className="spv-admin-theme__description-wrapper">
          <p className={`spv-admin-theme__description ${isExpanded ? 'spv-admin-theme__description--expanded' : ''}`}>
            {displayText}
            {!isExpanded && needsTruncation && '...'}
          </p>
          {needsTruncation && (
            <button
              type="button"
              className="spv-admin-theme__expand-btn"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? 'Lire moins' : 'Lire plus...'}
            </button>
          )}
        </div>
      )}

      {/* Tourism ideas */}
      {tourismIdeas.length > 0 && (
        <div className="spv-admin-theme__ideas">
          <h4 className="spv-admin-theme__ideas-title">Idées tourisme:</h4>
          <ul className="spv-admin-theme__ideas-list">
            {tourismIdeas.map((idea, i) => (
              <li key={i}>{idea}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Accept toggle */}
      <label className="spv-admin-theme__toggle">
        <input
          type="checkbox"
          checked={isAccepted}
          onChange={onToggle}
          className="spv-admin-theme__checkbox"
        />
        <span className="spv-admin-theme__toggle-label">
          {isAccepted ? 'Thème accepté' : 'Thème refusé'}
        </span>
      </label>
    </div>
  );
}
