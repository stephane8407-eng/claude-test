/**
 * FundingProgramsPage
 *
 * Admin page for managing funding programs (for project funding matches).
 * Platform admin only.
 */
import { useState, useEffect } from 'react';
import { fundingAPI } from '../../services/api';
import './FundingProgramsPage.css';

export function FundingProgramsPage() {
  const [programs, setPrograms] = useState([]);
  const [filters, setFilters] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedTheme, setSelectedTheme] = useState('');
  const [showActive, setShowActive] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingProgram, setEditingProgram] = useState(null);

  useEffect(() => {
    loadData();
  }, [selectedCountry, selectedProvider, selectedTheme, showActive, searchQuery]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load filters if not loaded
      if (!filters) {
        const filterData = await fundingAPI.getFilters();
        setFilters(filterData);
      }

      // Load programs with filters
      const params = {};
      if (selectedCountry) params.country = selectedCountry;
      if (selectedProvider) params.provider = selectedProvider;
      if (selectedTheme) params.theme = selectedTheme;
      if (showActive !== null) params.is_active = showActive;
      if (searchQuery) params.search = searchQuery;

      const data = await fundingAPI.list(params);
      setPrograms(data.results || []);
    } catch (err) {
      console.error('Failed to load funding programs:', err);
      setError('Échec du chargement des programmes de financement');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce programme ?')) {
      return;
    }

    try {
      await fundingAPI.delete(id);
      setPrograms(programs.filter(p => p.id !== id));
    } catch (err) {
      console.error('Failed to delete:', err);
      setError('Échec de la suppression');
    }
  };

  const handleEdit = (program) => {
    setEditingProgram(program);
    setShowModal(true);
  };

  const handleCreate = () => {
    setEditingProgram(null);
    setShowModal(true);
  };

  const handleSave = async (data) => {
    try {
      if (editingProgram) {
        await fundingAPI.update(editingProgram.id, data);
      } else {
        await fundingAPI.create(data);
      }
      setShowModal(false);
      loadData();
    } catch (err) {
      console.error('Failed to save:', err);
      setError('Échec de la sauvegarde');
    }
  };

  const formatAmount = (min, max) => {
    if (min && max) {
      return `€${min.toLocaleString()} - €${max.toLocaleString()}`;
    } else if (max) {
      return `Jusqu'à €${max.toLocaleString()}`;
    } else if (min) {
      return `À partir de €${min.toLocaleString()}`;
    }
    return 'Variable';
  };

  return (
    <div className="spv-funding">
      <div className="spv-funding__header">
        <div>
          <h1 className="spv-funding__title">Programmes de financement</h1>
          <p className="spv-funding__subtitle">
            Subventions et aides pour les projets de revitalisation
          </p>
        </div>
        <button
          className="spv-funding__add-btn"
          onClick={handleCreate}
        >
          + Ajouter un programme
        </button>
      </div>

      {/* Filters */}
      <div className="spv-funding__filters">
        <input
          type="text"
          placeholder="Rechercher..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="spv-funding__search"
        />

        <select
          value={selectedCountry}
          onChange={(e) => setSelectedCountry(e.target.value)}
          className="spv-funding__select"
        >
          <option value="">Tous les pays</option>
          {filters?.countries?.map(country => (
            <option key={country} value={country}>{country}</option>
          ))}
        </select>

        <select
          value={selectedProvider}
          onChange={(e) => setSelectedProvider(e.target.value)}
          className="spv-funding__select"
        >
          <option value="">Tous les fournisseurs</option>
          {filters?.providers?.map(provider => (
            <option key={provider} value={provider}>{provider}</option>
          ))}
        </select>

        <select
          value={selectedTheme}
          onChange={(e) => setSelectedTheme(e.target.value)}
          className="spv-funding__select"
        >
          <option value="">Tous les thèmes</option>
          {filters?.themes?.map(theme => (
            <option key={theme} value={theme}>{theme}</option>
          ))}
        </select>

        <label className="spv-funding__checkbox-label">
          <input
            type="checkbox"
            checked={showActive}
            onChange={(e) => setShowActive(e.target.checked)}
          />
          Actifs uniquement
        </label>
      </div>

      {/* Error message */}
      {error && (
        <div className="spv-funding__error">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="spv-funding__loading">Chargement...</div>
      )}

      {/* Table */}
      {!loading && (
        <div className="spv-funding__table-container">
          <table className="spv-funding__table">
            <thead>
              <tr>
                <th>Programme</th>
                <th>Fournisseur</th>
                <th>Montants</th>
                <th>Type</th>
                <th>Thèmes éligibles</th>
                <th>Délai</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {programs.map(program => (
                <tr key={program.id}>
                  <td>
                    <div className="spv-funding__program-name">
                      {program.name}
                    </div>
                    <div className="spv-funding__deadline-type">
                      {program.deadline_type === 'rolling' ? 'En continu' :
                       program.deadline_type === 'annual' ? 'Annuel' :
                       program.deadline_type}
                    </div>
                  </td>
                  <td>{program.provider}</td>
                  <td>
                    <div className="spv-funding__amount">
                      {formatAmount(program.amount_min, program.amount_max)}
                    </div>
                    {program.funding_percentage_max && (
                      <div className="spv-funding__percentage">
                        Jusqu'à {program.funding_percentage_max}%
                      </div>
                    )}
                  </td>
                  <td>
                    <span className={`spv-funding__type spv-funding__type--${program.funding_type}`}>
                      {program.funding_type === 'grant' ? 'Subvention' :
                       program.funding_type === 'loan' ? 'Prêt' :
                       program.funding_type === 'subsidy' ? 'Aide' :
                       program.funding_type}
                    </span>
                  </td>
                  <td>
                    <div className="spv-funding__themes">
                      {program.eligible_themes?.slice(0, 3).map(theme => (
                        <span key={theme} className="spv-funding__theme-tag">
                          {theme}
                        </span>
                      ))}
                      {program.eligible_themes?.length > 3 && (
                        <span className="spv-funding__theme-more">
                          +{program.eligible_themes.length - 3}
                        </span>
                      )}
                    </div>
                  </td>
                  <td>
                    {program.typical_timeline_months ? (
                      <span>{program.typical_timeline_months} mois</span>
                    ) : (
                      <span className="spv-funding__na">-</span>
                    )}
                  </td>
                  <td>
                    <span className={`spv-funding__status ${program.is_active ? 'spv-funding__status--active' : 'spv-funding__status--inactive'}`}>
                      {program.is_active ? 'Actif' : 'Inactif'}
                    </span>
                  </td>
                  <td>
                    <div className="spv-funding__actions">
                      <button
                        className="spv-funding__action-btn"
                        onClick={() => handleEdit(program)}
                        title="Modifier"
                      >
                        Modifier
                      </button>
                      <button
                        className="spv-funding__action-btn spv-funding__action-btn--danger"
                        onClick={() => handleDelete(program.id)}
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

          {programs.length === 0 && (
            <div className="spv-funding__empty">
              Aucun programme de financement trouvé
            </div>
          )}
        </div>
      )}

      {/* Edit/Create Modal */}
      {showModal && (
        <FundingProgramModal
          program={editingProgram}
          onSave={handleSave}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}

/**
 * Modal for creating/editing funding programs
 */
function FundingProgramModal({ program, onSave, onClose }) {
  const [formData, setFormData] = useState({
    name: program?.name || '',
    provider: program?.provider || '',
    country: program?.country || 'France',
    eligible_themes: program?.eligible_themes?.join(', ') || '',
    eligible_population_max: program?.eligible_population_max || '',
    funding_type: program?.funding_type || 'grant',
    amount_min: program?.amount_min || '',
    amount_max: program?.amount_max || '',
    funding_percentage_max: program?.funding_percentage_max || '',
    application_url: program?.application_url || '',
    deadline_type: program?.deadline_type || 'rolling',
    deadline_date: program?.deadline_date || '',
    process_summary: program?.process_summary || '',
    typical_timeline_months: program?.typical_timeline_months || '',
    tips: program?.tips || '',
    sources: program?.sources?.join('\n') || '',
    is_active: program?.is_active ?? true,
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    // Transform data
    const data = {
      ...formData,
      eligible_themes: formData.eligible_themes.split(',').map(t => t.trim()).filter(t => t),
      eligible_population_max: formData.eligible_population_max ? parseInt(formData.eligible_population_max) : null,
      amount_min: formData.amount_min ? parseInt(formData.amount_min) : null,
      amount_max: formData.amount_max ? parseInt(formData.amount_max) : null,
      funding_percentage_max: formData.funding_percentage_max ? parseInt(formData.funding_percentage_max) : null,
      typical_timeline_months: formData.typical_timeline_months ? parseInt(formData.typical_timeline_months) : null,
      sources: formData.sources.split('\n').filter(s => s.trim()),
      deadline_date: formData.deadline_date || null,
    };

    onSave(data);
  };

  return (
    <div className="spv-modal-overlay" onClick={onClose}>
      <div className="spv-modal" onClick={(e) => e.stopPropagation()}>
        <div className="spv-modal__header">
          <h2>{program ? 'Modifier le programme' : 'Nouveau programme'}</h2>
          <button className="spv-modal__close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="spv-modal__form">
          <div className="spv-modal__row">
            <div className="spv-modal__field">
              <label>Nom du programme *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="spv-modal__field">
              <label>Fournisseur *</label>
              <input
                type="text"
                value={formData.provider}
                onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                required
                placeholder="Ex: EU, État, Région"
              />
            </div>
          </div>

          <div className="spv-modal__row">
            <div className="spv-modal__field">
              <label>Pays *</label>
              <input
                type="text"
                value={formData.country}
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                required
              />
            </div>
            <div className="spv-modal__field">
              <label>Type de financement</label>
              <select
                value={formData.funding_type}
                onChange={(e) => setFormData({ ...formData, funding_type: e.target.value })}
              >
                <option value="grant">Subvention</option>
                <option value="loan">Prêt</option>
                <option value="subsidy">Aide</option>
                <option value="tax_credit">Crédit d'impôt</option>
                <option value="guarantee">Garantie</option>
              </select>
            </div>
          </div>

          <div className="spv-modal__row">
            <div className="spv-modal__field">
              <label>Montant min (€)</label>
              <input
                type="number"
                value={formData.amount_min}
                onChange={(e) => setFormData({ ...formData, amount_min: e.target.value })}
              />
            </div>
            <div className="spv-modal__field">
              <label>Montant max (€)</label>
              <input
                type="number"
                value={formData.amount_max}
                onChange={(e) => setFormData({ ...formData, amount_max: e.target.value })}
              />
            </div>
            <div className="spv-modal__field">
              <label>% max financement</label>
              <input
                type="number"
                value={formData.funding_percentage_max}
                onChange={(e) => setFormData({ ...formData, funding_percentage_max: e.target.value })}
                max="100"
              />
            </div>
          </div>

          <div className="spv-modal__field">
            <label>Thèmes éligibles (séparés par virgule)</label>
            <input
              type="text"
              value={formData.eligible_themes}
              onChange={(e) => setFormData({ ...formData, eligible_themes: e.target.value })}
              placeholder="heritage, ecology, tourism, agriculture"
            />
          </div>

          <div className="spv-modal__row">
            <div className="spv-modal__field">
              <label>Population max éligible</label>
              <input
                type="number"
                value={formData.eligible_population_max}
                onChange={(e) => setFormData({ ...formData, eligible_population_max: e.target.value })}
                placeholder="Laisser vide si pas de limite"
              />
            </div>
            <div className="spv-modal__field">
              <label>Délai typique (mois)</label>
              <input
                type="number"
                value={formData.typical_timeline_months}
                onChange={(e) => setFormData({ ...formData, typical_timeline_months: e.target.value })}
              />
            </div>
          </div>

          <div className="spv-modal__row">
            <div className="spv-modal__field">
              <label>Type d'échéance</label>
              <select
                value={formData.deadline_type}
                onChange={(e) => setFormData({ ...formData, deadline_type: e.target.value })}
              >
                <option value="rolling">En continu</option>
                <option value="annual">Annuel</option>
                <option value="quarterly">Trimestriel</option>
                <option value="one_time">Unique</option>
              </select>
            </div>
            <div className="spv-modal__field">
              <label>Date d'échéance</label>
              <input
                type="date"
                value={formData.deadline_date}
                onChange={(e) => setFormData({ ...formData, deadline_date: e.target.value })}
              />
            </div>
          </div>

          <div className="spv-modal__field">
            <label>URL de candidature</label>
            <input
              type="url"
              value={formData.application_url}
              onChange={(e) => setFormData({ ...formData, application_url: e.target.value })}
              placeholder="https://..."
            />
          </div>

          <div className="spv-modal__field">
            <label>Résumé du processus</label>
            <textarea
              value={formData.process_summary}
              onChange={(e) => setFormData({ ...formData, process_summary: e.target.value })}
              rows={4}
              placeholder="Décrivez les étapes du processus de candidature..."
            />
          </div>

          <div className="spv-modal__field">
            <label>Conseils</label>
            <textarea
              value={formData.tips}
              onChange={(e) => setFormData({ ...formData, tips: e.target.value })}
              rows={3}
              placeholder="Conseils pour maximiser les chances de succès..."
            />
          </div>

          <div className="spv-modal__field">
            <label>Sources/URLs (une par ligne)</label>
            <textarea
              value={formData.sources}
              onChange={(e) => setFormData({ ...formData, sources: e.target.value })}
              rows={2}
              placeholder="https://example.com"
            />
          </div>

          <div className="spv-modal__field">
            <label className="spv-funding__checkbox-label">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
              Programme actif
            </label>
          </div>

          <div className="spv-modal__actions">
            <button type="button" className="spv-modal__btn--secondary" onClick={onClose}>
              Annuler
            </button>
            <button type="submit" className="spv-modal__btn--primary">
              {program ? 'Mettre à jour' : 'Créer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default FundingProgramsPage;
