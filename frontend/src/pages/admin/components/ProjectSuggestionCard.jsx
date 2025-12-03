/**
 * ProjectSuggestionCard
 *
 * Display a suggested project with Phase D data.
 * Shows title, description, themes, and removable.
 * Handles both mock data and real AI data formats.
 */
import './ProjectSuggestionCard.css';

/**
 * Get description from various field names
 */
function getDescription(project) {
  return project.short_description || project.description || '';
}

/**
 * Get timeline display string
 */
function getTimeline(project) {
  // Real AI format (via wizard transformation): "12 mois"
  if (project.estimated_timeline) {
    return project.estimated_timeline;
  }
  // Direct API format: timeline_months as number
  if (project.timeline_months) {
    return `${project.timeline_months} mois`;
  }
  // Mock format
  if (project.estimated_timeline_months) {
    return `~${project.estimated_timeline_months} mois`;
  }
  return null;
}

/**
 * Get budget display string
 */
function getBudget(project) {
  // Real AI format (via wizard transformation): "€30,000 - €60,000"
  if (project.estimated_budget) {
    return project.estimated_budget;
  }
  // Direct API format: budget_min/budget_max as numbers
  if (project.budget_min !== undefined && project.budget_max !== undefined) {
    return `€${project.budget_min.toLocaleString()} - €${project.budget_max.toLocaleString()}`;
  }
  // Mock format
  if (project.estimated_budget_range) {
    return `${project.estimated_budget_range}€`;
  }
  return null;
}

/**
 * Get inspired_by display string
 */
function getInspiredBy(project) {
  if (!project.inspired_by) return null;
  // Already a string (transformed or mock)
  if (typeof project.inspired_by === 'string') {
    return project.inspired_by;
  }
  // Object format from API: { village_name, relevance }
  if (typeof project.inspired_by === 'object') {
    return project.inspired_by.village_name || null;
  }
  return null;
}

/**
 * Get funding programs as array of strings
 */
function getFundingPrograms(project) {
  if (!project.potential_funding || project.potential_funding.length === 0) {
    return [];
  }
  // Array of strings (transformed or mock)
  if (typeof project.potential_funding[0] === 'string') {
    return project.potential_funding;
  }
  // Array of objects from API: [{ program_name, match_score, ... }]
  return project.potential_funding.map(f =>
    typeof f === 'object' ? f.program_name : f
  );
}

export function ProjectSuggestionCard({ project, onRemove }) {
  const description = getDescription(project);
  const timeline = getTimeline(project);
  const budget = getBudget(project);
  const inspiredBy = getInspiredBy(project);
  const fundingPrograms = getFundingPrograms(project);

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
          {description}
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
          {timeline && (
            <span className="spv-project-card__meta-item">
              Durée: {timeline}
            </span>
          )}
          {budget && (
            <span className="spv-project-card__meta-item">
              Budget: {budget}
            </span>
          )}
        </div>
      </div>

      {/* Phase D Data - RAG Context */}
      <div className="spv-project-card__phase-d">
        <div className="spv-project-card__placeholder">
          <span className="spv-project-card__placeholder-label">Inspiré par:</span>
          <span className="spv-project-card__placeholder-value">
            {inspiredBy || <em>Non spécifié</em>}
          </span>
        </div>

        <div className="spv-project-card__placeholder">
          <span className="spv-project-card__placeholder-label">Financements potentiels:</span>
          <span className="spv-project-card__placeholder-value">
            {fundingPrograms.length > 0
              ? fundingPrograms.join(', ')
              : <em>Non spécifié</em>
            }
          </span>
        </div>

        <div className="spv-project-card__placeholder">
          <span className="spv-project-card__placeholder-label">Premières étapes:</span>
          <span className="spv-project-card__placeholder-value">
            {project.first_steps?.length > 0
              ? project.first_steps.join(', ')
              : <em>Non spécifié</em>
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
