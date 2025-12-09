/**
 * AdminIdentityCard Component
 *
 * Admin-only display of identity theme with full audit data.
 * Shows confidence scores, evidence sources, and raw data.
 * NOT for public pages - use PublicThemeCard instead.
 */
import { Link } from 'react-router-dom';
import './AdminIdentityCard.css';

export function AdminIdentityCard({ theme, villageSlug }) {
  if (!theme) return null;

  const confidencePercent = Math.round((theme.confidence_score || 0) * 100);
  const confidenceLevel = confidencePercent >= 80 ? 'high' : confidencePercent >= 60 ? 'medium' : 'low';

  return (
    <div className="spv-admin-card">
      {/* Header with confidence score */}
      <div className="spv-admin-card__header">
        <div className="spv-admin-card__header-top">
          <span className="spv-admin-card__id">Theme #{theme.id}</span>
          <span className={`spv-admin-card__confidence spv-admin-card__confidence--${confidenceLevel}`}>
            {confidencePercent}% confidence
          </span>
        </div>
        <h3 className="spv-admin-card__title">{theme.theme_name}</h3>
      </div>

      {/* Content */}
      <div className="spv-admin-card__content">
        {/* Theme Story */}
        {theme.theme_story && (
          <div className="spv-admin-card__section">
            <h4 className="spv-admin-card__section-title">Theme Story</h4>
            <p className="spv-admin-card__text">{theme.theme_story}</p>
          </div>
        )}

        {/* Evidence Section - Admin only data */}
        {theme.evidence && (
          <div className="spv-admin-card__section">
            <h4 className="spv-admin-card__section-title">Source Evidence</h4>
            <div className="spv-admin-card__evidence">
              {theme.evidence.conflicts && theme.evidence.conflicts.length > 0 && (
                <div className="spv-admin-card__evidence-group">
                  <span className="spv-admin-card__evidence-label">
                    Conflicts ({theme.evidence.conflicts.length}):
                  </span>
                  <ul className="spv-admin-card__evidence-list">
                    {theme.evidence.conflicts.slice(0, 5).map((conflict, i) => (
                      <li key={i}>{conflict}</li>
                    ))}
                    {theme.evidence.conflicts.length > 5 && (
                      <li className="spv-admin-card__evidence-more">
                        +{theme.evidence.conflicts.length - 5} more...
                      </li>
                    )}
                  </ul>
                </div>
              )}
              {theme.evidence.pois && theme.evidence.pois.length > 0 && (
                <div className="spv-admin-card__evidence-group">
                  <span className="spv-admin-card__evidence-label">
                    POIs ({theme.evidence.pois.length}):
                  </span>
                  <ul className="spv-admin-card__evidence-list">
                    {theme.evidence.pois.slice(0, 5).map((poi, i) => (
                      <li key={i}>{poi}</li>
                    ))}
                    {theme.evidence.pois.length > 5 && (
                      <li className="spv-admin-card__evidence-more">
                        +{theme.evidence.pois.length - 5} more...
                      </li>
                    )}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Project Ideas */}
        {theme.project_ideas && theme.project_ideas.length > 0 && (
          <div className="spv-admin-card__section">
            <h4 className="spv-admin-card__section-title">Tourism Project Ideas</h4>
            <ul className="spv-admin-card__ideas">
              {theme.project_ideas.map((idea, i) => (
                <li key={i} className="spv-admin-card__idea">
                  <span className="spv-admin-card__idea-title">{idea.title || idea}</span>
                  {idea.estimated_impact && (
                    <span className="spv-admin-card__idea-impact">
                      Impact: {idea.estimated_impact}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Raw metadata for debugging */}
        {theme.created_at && (
          <div className="spv-admin-card__meta">
            <span>Created: {new Date(theme.created_at).toLocaleDateString('fr-FR')}</span>
            {theme.updated_at && (
              <span>Updated: {new Date(theme.updated_at).toLocaleDateString('fr-FR')}</span>
            )}
          </div>
        )}

        {/* Admin actions */}
        <div className="spv-admin-card__actions">
          <Link
            to={`/villages/${villageSlug}/identity/${theme.id}`}
            className="spv-admin-card__link"
          >
            View Full Analysis →
          </Link>
        </div>
      </div>
    </div>
  );
}
