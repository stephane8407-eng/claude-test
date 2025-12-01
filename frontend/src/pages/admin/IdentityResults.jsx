/**
 * IdentityResults
 *
 * Display and edit AI-generated identity results.
 * Allows editing, accepting/rejecting themes, and saving to database.
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdminThemeCard } from './components/AdminThemeCard';
import { ProjectSuggestionCard } from './components/ProjectSuggestionCard';
import './IdentityResults.css';

export function IdentityResults({ results, villageSlug, onRegenerate, onBackToEdit }) {
  const navigate = useNavigate();

  // Editable fields
  const [summaryIdentity, setSummaryIdentity] = useState(results.summaryIdentity || '');
  const [longIdentity, setLongIdentity] = useState(results.longIdentity || '');
  const [liveHereSummary, setLiveHereSummary] = useState(results.liveHereSummary || '');

  // Theme acceptance state
  const [acceptedThemes, setAcceptedThemes] = useState(
    results.themes?.map((_, i) => true) || []
  );

  // Project state (can remove)
  const [projects, setProjects] = useState(results.suggested_projects || []);

  // Saving state
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  const toggleTheme = (index) => {
    setAcceptedThemes(prev => {
      const updated = [...prev];
      updated[index] = !updated[index];
      return updated;
    });
  };

  const removeProject = (index) => {
    setProjects(prev => prev.filter((_, i) => i !== index));
  };

  const handleSaveAndPublish = async () => {
    setIsSaving(true);
    setSaveError(null);

    try {
      // Prepare accepted themes
      const themesToSave = results.themes
        ?.filter((_, i) => acceptedThemes[i])
        .map(theme => ({
          theme_name: theme.title,
          confidence_score: theme.confidence,
          theme_story: theme.description?.join(' '),
          project_ideas: theme.tourism_ideas?.map(idea => ({ title: idea })),
        })) || [];

      // Prepare projects
      const projectsToSave = projects.map(p => ({
        title: p.title,
        short_description: p.short_description,
        themes: p.themes,
        status: 'idea',
        source: 'ai_suggested',
      }));

      // Save identity to village
      const response = await fetch(`/api/villages/${villageSlug}/identity`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          summary_identity: summaryIdentity,
          long_identity: longIdentity,
          live_here_summary: liveHereSummary,
          themes: themesToSave,
          projects: projectsToSave,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save identity');
      }

      // Clear draft from localStorage
      localStorage.removeItem('spv_identity_audit_draft');

      // Redirect to village page or dashboard
      navigate(`/villages/${villageSlug}`);
    } catch (err) {
      console.error('Save failed:', err);
      setSaveError('Échec de la sauvegarde. Veuillez réessayer.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="spv-results">
      <div className="spv-results__header">
        <h1 className="spv-results__title">Résultats de l'audit</h1>
        <p className="spv-results__subtitle">
          Modifiez les textes générés et sélectionnez les thèmes à conserver.
        </p>
      </div>

      {/* Identity Summary */}
      <section className="spv-results__section">
        <div className="spv-results__section-header">
          <h2 className="spv-results__section-title">Identité résumée</h2>
          <span className="spv-results__section-hint">
            Apparaît sur la page publique du village
          </span>
        </div>
        <textarea
          className="spv-results__textarea"
          value={summaryIdentity}
          onChange={(e) => setSummaryIdentity(e.target.value)}
          rows={3}
        />
        <div className="spv-results__char-count">
          {summaryIdentity.length} caractères
        </div>
      </section>

      {/* Long Identity */}
      <section className="spv-results__section">
        <div className="spv-results__section-header">
          <h2 className="spv-results__section-title">Identité détaillée</h2>
          <span className="spv-results__section-hint">
            1-3 paragraphes décrivant l'identité du village
          </span>
        </div>
        <textarea
          className="spv-results__textarea spv-results__textarea--large"
          value={longIdentity}
          onChange={(e) => setLongIdentity(e.target.value)}
          rows={6}
        />
        <div className="spv-results__char-count">
          {longIdentity.length} caractères
        </div>
      </section>

      {/* Live Here Summary */}
      <section className="spv-results__section">
        <div className="spv-results__section-header">
          <h2 className="spv-results__section-title">Vivre ici</h2>
          <span className="spv-results__section-hint">
            Description de la vie quotidienne au village
          </span>
        </div>
        <textarea
          className="spv-results__textarea"
          value={liveHereSummary}
          onChange={(e) => setLiveHereSummary(e.target.value)}
          rows={4}
        />
        <div className="spv-results__char-count">
          {liveHereSummary.length} caractères
        </div>
      </section>

      {/* Themes */}
      {results.themes && results.themes.length > 0 && (
        <section className="spv-results__section">
          <div className="spv-results__section-header">
            <h2 className="spv-results__section-title">Thèmes suggérés</h2>
            <span className="spv-results__section-hint">
              Sélectionnez les thèmes à conserver (vue admin uniquement)
            </span>
          </div>
          <div className="spv-results__themes-grid">
            {results.themes.map((theme, index) => (
              <AdminThemeCard
                key={index}
                theme={theme}
                index={index + 1}
                isAccepted={acceptedThemes[index]}
                onToggle={() => toggleTheme(index)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Suggested Projects */}
      {projects.length > 0 && (
        <section className="spv-results__section">
          <div className="spv-results__section-header">
            <h2 className="spv-results__section-title">Projets suggérés</h2>
            <span className="spv-results__section-hint">
              Idées de projets générées à partir de l'audit
            </span>
          </div>
          <div className="spv-results__projects-list">
            {projects.map((project, index) => (
              <ProjectSuggestionCard
                key={index}
                project={project}
                onRemove={() => removeProject(index)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Action Buttons */}
      <div className="spv-results__actions">
        {saveError && (
          <div className="spv-results__error">
            {saveError}
          </div>
        )}

        <div className="spv-results__buttons">
          <button
            type="button"
            className="spv-results__btn spv-results__btn--ghost"
            onClick={onBackToEdit}
          >
            Modifier les données
          </button>

          <button
            type="button"
            className="spv-results__btn spv-results__btn--secondary"
            onClick={onRegenerate}
          >
            Régénérer
          </button>

          <button
            type="button"
            className="spv-results__btn spv-results__btn--primary"
            onClick={handleSaveAndPublish}
            disabled={isSaving}
          >
            {isSaving ? 'Sauvegarde...' : 'Sauvegarder et publier'}
          </button>
        </div>
      </div>
    </div>
  );
}
