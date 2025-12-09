/**
 * CaseStudiesPage
 *
 * Admin page for managing revival case studies (RAG context for AI).
 * Platform admin only.
 */
import { useState, useEffect } from 'react';
import { caseStudiesAPI } from '../../services/api';
import './CaseStudiesPage.css';

export function CaseStudiesPage() {
  const [caseStudies, setCaseStudies] = useState([]);
  const [filters, setFilters] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedTheme, setSelectedTheme] = useState('');
  const [selectedPopBand, setSelectedPopBand] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingStudy, setEditingStudy] = useState(null);

  useEffect(() => {
    loadData();
  }, [selectedCountry, selectedTheme, selectedPopBand, searchQuery]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load filters if not loaded
      if (!filters) {
        const filterData = await caseStudiesAPI.getFilters();
        setFilters(filterData);
      }

      // Load case studies with filters
      const params = {};
      if (selectedCountry) params.country = selectedCountry;
      if (selectedTheme) params.theme = selectedTheme;
      if (selectedPopBand) params.population_band = selectedPopBand;
      if (searchQuery) params.search = searchQuery;

      const data = await caseStudiesAPI.list(params);
      setCaseStudies(data.results || []);
    } catch (err) {
      console.error('Failed to load case studies:', err);
      setError('Échec du chargement des études de cas');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette étude de cas ?')) {
      return;
    }

    try {
      await caseStudiesAPI.delete(id);
      setCaseStudies(caseStudies.filter(cs => cs.id !== id));
    } catch (err) {
      console.error('Failed to delete:', err);
      setError('Échec de la suppression');
    }
  };

  const handleEdit = (study) => {
    setEditingStudy(study);
    setShowModal(true);
  };

  const handleCreate = () => {
    setEditingStudy(null);
    setShowModal(true);
  };

  const handleSave = async (data) => {
    try {
      if (editingStudy) {
        await caseStudiesAPI.update(editingStudy.id, data);
      } else {
        await caseStudiesAPI.create(data);
      }
      setShowModal(false);
      loadData();
    } catch (err) {
      console.error('Failed to save:', err);
      setError('Échec de la sauvegarde');
    }
  };

  const formatPopulationBand = (band) => {
    const labels = {
      'under_100': '< 100',
      '100_500': '100-500',
      '500_1000': '500-1000',
      '1000_5000': '1000-5000',
      '5000_plus': '5000+',
    };
    return labels[band] || band;
  };

  return (
    <div className="spv-case-studies">
      <div className="spv-case-studies__header">
        <div>
          <h1 className="spv-case-studies__title">Études de cas</h1>
          <p className="spv-case-studies__subtitle">
            Exemples réels de villages revitalisés (contexte RAG pour l'IA)
          </p>
        </div>
        <button
          className="spv-case-studies__add-btn"
          onClick={handleCreate}
        >
          + Ajouter une étude
        </button>
      </div>

      {/* Filters */}
      <div className="spv-case-studies__filters">
        <input
          type="text"
          placeholder="Rechercher..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="spv-case-studies__search"
        />

        <select
          value={selectedCountry}
          onChange={(e) => setSelectedCountry(e.target.value)}
          className="spv-case-studies__select"
        >
          <option value="">Tous les pays</option>
          {filters?.countries?.map(country => (
            <option key={country} value={country}>{country}</option>
          ))}
        </select>

        <select
          value={selectedTheme}
          onChange={(e) => setSelectedTheme(e.target.value)}
          className="spv-case-studies__select"
        >
          <option value="">Tous les thèmes</option>
          {filters?.themes?.map(theme => (
            <option key={theme} value={theme}>{theme}</option>
          ))}
        </select>

        <select
          value={selectedPopBand}
          onChange={(e) => setSelectedPopBand(e.target.value)}
          className="spv-case-studies__select"
        >
          <option value="">Toutes populations</option>
          {filters?.population_bands?.map(band => (
            <option key={band} value={band}>{formatPopulationBand(band)}</option>
          ))}
        </select>
      </div>

      {/* Error message */}
      {error && (
        <div className="spv-case-studies__error">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="spv-case-studies__loading">Chargement...</div>
      )}

      {/* Table */}
      {!loading && (
        <div className="spv-case-studies__table-container">
          <table className="spv-case-studies__table">
            <thead>
              <tr>
                <th>Village</th>
                <th>Pays</th>
                <th>Population</th>
                <th>Type</th>
                <th>Thèmes</th>
                <th>Durée</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {caseStudies.map(study => (
                <tr key={study.id}>
                  <td>
                    <div className="spv-case-studies__village-name">
                      {study.village_name}
                    </div>
                    <div className="spv-case-studies__region">
                      {study.region}
                    </div>
                  </td>
                  <td>{study.country}</td>
                  <td>
                    {study.population_before && study.population_after ? (
                      <span>
                        {study.population_before} → {study.population_after}
                      </span>
                    ) : (
                      formatPopulationBand(study.population_band)
                    )}
                  </td>
                  <td>
                    <span className={`spv-case-studies__type spv-case-studies__type--${study.revival_type}`}>
                      {study.revival_type?.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <div className="spv-case-studies__themes">
                      {study.themes?.slice(0, 3).map(theme => (
                        <span key={theme} className="spv-case-studies__theme-tag">
                          {theme}
                        </span>
                      ))}
                      {study.themes?.length > 3 && (
                        <span className="spv-case-studies__theme-more">
                          +{study.themes.length - 3}
                        </span>
                      )}
                    </div>
                  </td>
                  <td>{study.timeline_years} ans</td>
                  <td>
                    <div className="spv-case-studies__actions">
                      <button
                        className="spv-case-studies__action-btn"
                        onClick={() => handleEdit(study)}
                        title="Modifier"
                      >
                        Modifier
                      </button>
                      <button
                        className="spv-case-studies__action-btn spv-case-studies__action-btn--danger"
                        onClick={() => handleDelete(study.id)}
                        title="Supprimer"
                      >
                        Supprimer
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {caseStudies.length === 0 && (
            <div className="spv-case-studies__empty">
              Aucune étude de cas trouvée
            </div>
          )}
        </div>
      )}

      {/* Edit/Create Modal */}
      {showModal && (
        <CaseStudyModal
          study={editingStudy}
          onSave={handleSave}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}

/**
 * Modal for creating/editing case studies
 */
function CaseStudyModal({ study, onSave, onClose }) {
  const [formData, setFormData] = useState({
    village_name: study?.village_name || '',
    country: study?.country || 'France',
    region: study?.region || '',
    population_before: study?.population_before || '',
    population_after: study?.population_after || '',
    population_band: study?.population_band || '',
    revival_type: study?.revival_type || '',
    strategy: study?.strategy || '',
    key_projects: study?.key_projects?.join('\n') || '',
    outcomes: study?.outcomes || '',
    lessons_learned: study?.lessons_learned || '',
    timeline_years: study?.timeline_years || '',
    themes: study?.themes?.join(', ') || '',
    geography_tags: study?.geography_tags?.join(', ') || '',
    funding_sources: study?.funding_sources?.join(', ') || '',
    sources: study?.sources?.join('\n') || '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    // Transform data
    const data = {
      ...formData,
      population_before: formData.population_before ? parseInt(formData.population_before) : null,
      population_after: formData.population_after ? parseInt(formData.population_after) : null,
      timeline_years: formData.timeline_years ? parseInt(formData.timeline_years) : null,
      key_projects: formData.key_projects.split('\n').filter(p => p.trim()),
      themes: formData.themes.split(',').map(t => t.trim()).filter(t => t),
      geography_tags: formData.geography_tags.split(',').map(t => t.trim()).filter(t => t),
      funding_sources: formData.funding_sources.split(',').map(f => f.trim()).filter(f => f),
      sources: formData.sources.split('\n').filter(s => s.trim()),
    };

    onSave(data);
  };

  return (
    <div className="spv-modal-overlay" onClick={onClose}>
      <div className="spv-modal" onClick={(e) => e.stopPropagation()}>
        <div className="spv-modal__header">
          <h2>{study ? 'Modifier l\'étude de cas' : 'Nouvelle étude de cas'}</h2>
          <button className="spv-modal__close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="spv-modal__form">
          <div className="spv-modal__row">
            <div className="spv-modal__field">
              <label>Nom du village *</label>
              <input
                type="text"
                value={formData.village_name}
                onChange={(e) => setFormData({ ...formData, village_name: e.target.value })}
                required
              />
            </div>
            <div className="spv-modal__field">
              <label>Pays *</label>
              <input
                type="text"
                value={formData.country}
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="spv-modal__field">
            <label>Région</label>
            <input
              type="text"
              value={formData.region}
              onChange={(e) => setFormData({ ...formData, region: e.target.value })}
              placeholder="Ex: Dordogne, Nouvelle-Aquitaine"
            />
          </div>

          <div className="spv-modal__row">
            <div className="spv-modal__field">
              <label>Population avant</label>
              <input
                type="number"
                value={formData.population_before}
                onChange={(e) => setFormData({ ...formData, population_before: e.target.value })}
              />
            </div>
            <div className="spv-modal__field">
              <label>Population après</label>
              <input
                type="number"
                value={formData.population_after}
                onChange={(e) => setFormData({ ...formData, population_after: e.target.value })}
              />
            </div>
            <div className="spv-modal__field">
              <label>Tranche de population</label>
              <select
                value={formData.population_band}
                onChange={(e) => setFormData({ ...formData, population_band: e.target.value })}
              >
                <option value="">Sélectionner...</option>
                <option value="under_100">&lt; 100</option>
                <option value="100_500">100-500</option>
                <option value="500_1000">500-1000</option>
                <option value="1000_5000">1000-5000</option>
                <option value="5000_plus">5000+</option>
              </select>
            </div>
          </div>

          <div className="spv-modal__row">
            <div className="spv-modal__field">
              <label>Type de revitalisation</label>
              <select
                value={formData.revival_type}
                onChange={(e) => setFormData({ ...formData, revival_type: e.target.value })}
              >
                <option value="">Sélectionner...</option>
                <option value="eco_village">Éco-village</option>
                <option value="artisan_hub">Pôle artisanal</option>
                <option value="heritage_tourism">Tourisme patrimonial</option>
                <option value="remote_work">Télétravail</option>
                <option value="agriculture">Agriculture</option>
                <option value="wine_tourism">Oenotourisme</option>
                <option value="cultural">Culturel</option>
              </select>
            </div>
            <div className="spv-modal__field">
              <label>Durée (années)</label>
              <input
                type="number"
                value={formData.timeline_years}
                onChange={(e) => setFormData({ ...formData, timeline_years: e.target.value })}
              />
            </div>
          </div>

          <div className="spv-modal__field">
            <label>Stratégie *</label>
            <textarea
              value={formData.strategy}
              onChange={(e) => setFormData({ ...formData, strategy: e.target.value })}
              rows={4}
              required
              placeholder="Décrivez la stratégie principale adoptée..."
            />
          </div>

          <div className="spv-modal__field">
            <label>Projets clés (un par ligne)</label>
            <textarea
              value={formData.key_projects}
              onChange={(e) => setFormData({ ...formData, key_projects: e.target.value })}
              rows={4}
              placeholder="Projet 1&#10;Projet 2&#10;Projet 3"
            />
          </div>

          <div className="spv-modal__field">
            <label>Résultats *</label>
            <textarea
              value={formData.outcomes}
              onChange={(e) => setFormData({ ...formData, outcomes: e.target.value })}
              rows={3}
              required
              placeholder="Décrivez les résultats obtenus..."
            />
          </div>

          <div className="spv-modal__field">
            <label>Leçons apprises</label>
            <textarea
              value={formData.lessons_learned}
              onChange={(e) => setFormData({ ...formData, lessons_learned: e.target.value })}
              rows={3}
              placeholder="Quelles leçons retenir de cette expérience ?"
            />
          </div>

          <div className="spv-modal__row">
            <div className="spv-modal__field">
              <label>Thèmes (séparés par virgule)</label>
              <input
                type="text"
                value={formData.themes}
                onChange={(e) => setFormData({ ...formData, themes: e.target.value })}
                placeholder="heritage, ecology, tourism"
              />
            </div>
            <div className="spv-modal__field">
              <label>Géographie (séparés par virgule)</label>
              <input
                type="text"
                value={formData.geography_tags}
                onChange={(e) => setFormData({ ...formData, geography_tags: e.target.value })}
                placeholder="mountains, forest, river"
              />
            </div>
          </div>

          <div className="spv-modal__field">
            <label>Sources de financement (séparées par virgule)</label>
            <input
              type="text"
              value={formData.funding_sources}
              onChange={(e) => setFormData({ ...formData, funding_sources: e.target.value })}
              placeholder="LEADER, Fondation du Patrimoine"
            />
          </div>

          <div className="spv-modal__field">
            <label>Sources/URLs (une par ligne)</label>
            <textarea
              value={formData.sources}
              onChange={(e) => setFormData({ ...formData, sources: e.target.value })}
              rows={2}
              placeholder="https://example.com/article"
            />
          </div>

          <div className="spv-modal__actions">
            <button type="button" className="spv-modal__btn--secondary" onClick={onClose}>
              Annuler
            </button>
            <button type="submit" className="spv-modal__btn--primary">
              {study ? 'Mettre à jour' : 'Créer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CaseStudiesPage;
