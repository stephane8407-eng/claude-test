/**
 * ProjectSuggestionCard
 *
 * Display a suggested project with Phase D placeholders.
 * Shows title, description, themes, and removable.
 */
import './ProjectSuggestionCard.css';

export function ProjectSuggestionCard({ project, onRemove }) {
  return (
    <div className="spv-project-card">
      <div className="spv-project-card__main">
        <div className="spv-project-card__header">
          <h3 className="spv-project-card__title">{project.title}</h3>
          <button
            type="button"
            className="spv-project-card__remove"
            onClick={onRemove}
            title="Supprimer ce projet"
          >
            ×
          </button>
        </div>

        <p className="spv-project-card__description">
          {project.short_description}
        </p>

        {/* Themes */}
        {project.themes && project.themes.length > 0 && (
          <div className="spv-project-card__themes">
            {project.themes.map((theme, i) => (
              <span key={i} className="spv-project-card__theme">
                {theme}
              </span>
            ))}
          </div>
        )}

        {/* Meta info */}
        <div className="spv-project-card__meta">
          {project.difficulty && (
            <span className="spv-project-card__meta-item">
              Difficulté: {getDifficultyLabel(project.difficulty)}
            </span>
          )}
          {project.estimated_timeline_months && (
            <span className="spv-project-card__meta-item">
              Durée: ~{project.estimated_timeline_months} mois
            </span>
          )}
          {project.estimated_budget_range && (
            <span className="spv-project-card__meta-item">
              Budget: {project.estimated_budget_range}€
            </span>
          )}
        </div>
      </div>

      {/* Phase D Placeholders */}
      <div className="spv-project-card__phase-d">
        <div className="spv-project-card__placeholder">
          <span className="spv-project-card__placeholder-label">Inspiré par:</span>
          <span className="spv-project-card__placeholder-value">
            {project.inspired_by || <em>À venir (Phase D)</em>}
          </span>
        </div>

        <div className="spv-project-card__placeholder">
          <span className="spv-project-card__placeholder-label">Financements potentiels:</span>
          <span className="spv-project-card__placeholder-value">
            {project.potential_funding?.length > 0
              ? project.potential_funding.join(', ')
              : <em>À venir (Phase D)</em>
            }
          </span>
        </div>

        <div className="spv-project-card__placeholder">
          <span className="spv-project-card__placeholder-label">Premières étapes:</span>
          <span className="spv-project-card__placeholder-value">
            {project.first_steps?.length > 0
              ? project.first_steps.join(', ')
              : <em>À venir (Phase D)</em>
            }
          </span>
        </div>
      </div>
    </div>
  );
}

function getDifficultyLabel(difficulty) {
  const labels = {
    easy: 'Facile',
    moderate: 'Modéré',
    hard: 'Difficile',
  };
  return labels[difficulty] || difficulty;
}
