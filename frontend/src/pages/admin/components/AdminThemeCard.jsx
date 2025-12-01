/**
 * AdminThemeCard
 *
 * Admin-only theme display with confidence score and accept/reject toggle.
 * Shows theme details with bullets and tourism ideas.
 */
import './AdminThemeCard.css';

export function AdminThemeCard({ theme, index, isAccepted, onToggle }) {
  const confidencePercent = Math.round((theme.confidence || 0) * 100);
  const confidenceLevel = confidencePercent >= 80 ? 'high' : confidencePercent >= 60 ? 'medium' : 'low';

  return (
    <div className={`spv-admin-theme ${isAccepted ? 'spv-admin-theme--accepted' : 'spv-admin-theme--rejected'}`}>
      {/* Header */}
      <div className="spv-admin-theme__header">
        <span className="spv-admin-theme__number">Theme #{index}</span>
        <span className={`spv-admin-theme__confidence spv-admin-theme__confidence--${confidenceLevel}`}>
          {confidencePercent}%
        </span>
      </div>

      {/* Title */}
      <h3 className="spv-admin-theme__title">{theme.title}</h3>

      {/* Description bullets */}
      {theme.description && theme.description.length > 0 && (
        <ul className="spv-admin-theme__bullets">
          {theme.description.map((bullet, i) => (
            <li key={i}>{bullet}</li>
          ))}
        </ul>
      )}

      {/* Tourism ideas */}
      {theme.tourism_ideas && theme.tourism_ideas.length > 0 && (
        <div className="spv-admin-theme__ideas">
          <h4 className="spv-admin-theme__ideas-title">Idées tourisme:</h4>
          <ul className="spv-admin-theme__ideas-list">
            {theme.tourism_ideas.map((idea, i) => (
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
