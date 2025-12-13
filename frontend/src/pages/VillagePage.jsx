/**
 * VillagePage - Public Village Detail
 *
 * Clean white design with teal accents.
 * NO blue gradients, NO AI terminology, NO confidence scores.
 * Includes edit mode for village admins.
 */
import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, PencilIcon, XMarkIcon, CheckIcon } from '@heroicons/react/24/outline';
import { MainLayout } from '../components/layout/index';
import { villageAPI, poiAPI, identityAPI } from '../services/api';
import { VillageMap } from '../components/village/VillageMap';
import { PublicPlaceCard } from '../components/village/PublicPlaceCard';
import { RouteCard, ThemeChip } from '../components/ui';
import { useAuth } from '../contexts/AuthContext';
import './VillagePage.css';

export function VillagePage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [village, setVillage] = useState(null);
  const [pois, setPois] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Edit mode state
  const [editMode, setEditMode] = useState(false);
  const [savedIdentity, setSavedIdentity] = useState(null);
  const [editData, setEditData] = useState({
    summary_identity: '',
    long_identity: '',
    live_here_summary: '',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Check if current user can edit this village
  const canEdit = user && (
    user.role === 'admin' ||
    (user.role === 'village_admin' && user.village_slug === slug)
  );

  useEffect(() => {
    loadVillageData();
  }, [slug]);

  const loadVillageData = async () => {
    try {
      setLoading(true);
      const [villageData, poisData] = await Promise.all([
        villageAPI.getBySlug(slug),
        poiAPI.list(slug).catch(() => [])
      ]);

      setVillage(villageData);
      setPois(Array.isArray(poisData) ? poisData : []);
      // TODO: Load routes when API is ready
      setRoutes([]);

      // Load saved identity if user can edit
      if (user) {
        try {
          const identity = await identityAPI.getIdentity(slug);
          setSavedIdentity(identity);
          setEditData({
            summary_identity: identity.identity_summary || villageData.summary_identity || '',
            long_identity: identity.identity_narrative || villageData.long_identity || '',
            live_here_summary: identity.live_here_summary || villageData.live_here_summary || '',
          });
        } catch {
          // No identity saved yet, use village data
          setEditData({
            summary_identity: villageData.summary_identity || '',
            long_identity: villageData.long_identity || '',
            live_here_summary: villageData.live_here_summary || '',
          });
        }
      }
    } catch (err) {
      console.error('Failed to load village data:', err);
      setError('Impossible de charger les informations du village');
    } finally {
      setLoading(false);
    }
  };

  const handleEditToggle = () => {
    if (editMode) {
      // Cancel edit - reset to original data
      setEditData({
        summary_identity: savedIdentity?.identity_summary || village?.summary_identity || '',
        long_identity: savedIdentity?.identity_narrative || village?.long_identity || '',
        live_here_summary: savedIdentity?.live_here_summary || village?.live_here_summary || '',
      });
      setSaveError(null);
    }
    setEditMode(!editMode);
    setSaveSuccess(false);
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveError(null);
    setSaveSuccess(false);

    try {
      await identityAPI.saveIdentity(slug, {
        summary_identity: editData.summary_identity,
        long_identity: editData.long_identity,
        live_here_summary: editData.live_here_summary,
        themes: savedIdentity?.selected_themes || [],
        projects: savedIdentity?.selected_projects || [],
      });

      // Reload village data to reflect changes
      await loadVillageData();
      setEditMode(false);
      setSaveSuccess(true);

      // Clear success message after 3 seconds
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Save failed:', err);
      setSaveError('Échec de la sauvegarde. Veuillez réessayer.');
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="spv-village-loading">
          <div className="spv-village-loading__spinner" />
          <span>Chargement...</span>
        </div>
      </MainLayout>
    );
  }

  if (error || !village) {
    return (
      <MainLayout>
        <div className="spv-village-error">
          <h1>Village introuvable</h1>
          <p>{error || "Le village demandé n'existe pas."}</p>
          <Link to="/explore" className="spv-village-error__link">
            Retour à la carte
          </Link>
        </div>
      </MainLayout>
    );
  }

  // Calculate stats
  const conflictCount = village.conflict_count || 0;
  const poiCount = pois.length;

  return (
    <MainLayout>
      <div className="spv-village">
        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="spv-village__back-button"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: '#0d9488',
            background: 'none',
            border: 'none',
            padding: '12px 16px',
            cursor: 'pointer',
            fontSize: '15px',
            fontWeight: 500,
            transition: 'color 0.2s'
          }}
          onMouseEnter={(e) => e.target.style.color = '#0f766e'}
          onMouseLeave={(e) => e.target.style.color = '#0d9488'}
        >
          <ArrowLeftIcon style={{ width: '20px', height: '20px' }} />
          <span>Retour</span>
        </button>

        {/* Success Message */}
        {saveSuccess && (
          <div className="spv-village__success-banner" style={{
            background: '#d1fae5',
            color: '#065f46',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <CheckIcon style={{ width: '20px', height: '20px' }} />
            Modifications sauvegardées avec succès !
          </div>
        )}

        {/* Header - Clean white, no gradient */}
        <header className="spv-village__header" style={{ position: 'relative' }}>
          {/* Edit button for admins */}
          {canEdit && (
            <button
              onClick={handleEditToggle}
              className="spv-village__edit-button"
              style={{
                position: 'absolute',
                top: '16px',
                right: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 16px',
                background: editMode ? '#fee2e2' : '#f0fdfa',
                color: editMode ? '#dc2626' : '#0d9488',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 500,
                transition: 'all 0.2s'
              }}
            >
              {editMode ? (
                <>
                  <XMarkIcon style={{ width: '16px', height: '16px' }} />
                  Annuler
                </>
              ) : (
                <>
                  <PencilIcon style={{ width: '16px', height: '16px' }} />
                  Modifier
                </>
              )}
            </button>
          )}

          <div className="spv-village__header-content">
            <h1 className="spv-village__name">{village.name}</h1>

            {editMode ? (
              <div style={{ marginTop: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>
                  Tagline / Identité résumée
                </label>
                <textarea
                  value={editData.summary_identity}
                  onChange={(e) => setEditData({ ...editData, summary_identity: e.target.value })}
                  placeholder="Décrivez l'identité du village en une phrase..."
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    fontSize: '16px',
                    resize: 'vertical',
                    minHeight: '80px'
                  }}
                />
              </div>
            ) : village.summary_identity && (
              <p className="spv-village__tagline">{village.summary_identity}</p>
            )}

            {/* Metrics as inline badges */}
            <div className="spv-village__metrics">
              {conflictCount > 0 && (
                <span className="spv-village__metric">
                  {conflictCount} événements historiques
                </span>
              )}
              {poiCount > 0 && (
                <span className="spv-village__metric">
                  {poiCount} lieux d'intérêt
                </span>
              )}
              {village.population && (
                <span className="spv-village__metric">
                  {village.population} habitants
                </span>
              )}
            </div>

            {/* Theme chips */}
            {village.themes && village.themes.length > 0 && (
              <div className="spv-village__themes">
                {village.themes.slice(0, 5).map((theme) => (
                  <ThemeChip key={theme} theme={theme} size="md" />
                ))}
              </div>
            )}
          </div>
        </header>

        {/* Long Identity Narrative */}
        {(village.long_identity || editMode) && (
          <section className="spv-village__section">
            {editMode ? (
              <div>
                <label style={{ display: 'block', fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>
                  Identité détaillée (1-3 paragraphes)
                </label>
                <textarea
                  value={editData.long_identity}
                  onChange={(e) => setEditData({ ...editData, long_identity: e.target.value })}
                  placeholder="Décrivez l'histoire et l'identité du village..."
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    fontSize: '16px',
                    resize: 'vertical',
                    minHeight: '150px',
                    lineHeight: '1.6'
                  }}
                />
              </div>
            ) : (
              <div className="spv-village__narrative">
                <p>{village.long_identity}</p>
              </div>
            )}
          </section>
        )}

        {/* Interactive Map */}
        <section className="spv-village__section">
          <h2 className="spv-village__section-title">Explorer {village.name}</h2>
          <div className="spv-village__map-container">
            <VillageMap
              villageSlug={slug}
              pois={pois}
              center={{ lat: parseFloat(village.latitude), lng: parseFloat(village.longitude) }}
              showConflicts={true}
              showPOIs={true}
            />
          </div>
        </section>

        {/* Simple Identity Section - replaces theme cards temporarily */}
        <section className="spv-village__section spv-village__section--alt">
          <h2 className="spv-village__section-title">Identité du village</h2>
          <div className="spv-village__identity">
            {village.summary_identity ? (
              <p>{village.summary_identity}</p>
            ) : (
              <p className="spv-village__identity--placeholder">
                Profil identitaire bientôt disponible
              </p>
            )}
          </div>
        </section>

        {/* Places Section */}
        {pois.length > 0 && (
          <section className="spv-village__section">
            <h2 className="spv-village__section-title">Lieux à découvrir</h2>
            <div className="spv-village__places-grid">
              {pois.slice(0, 6).map((poi) => (
                <PublicPlaceCard
                  key={poi.id}
                  place={poi}
                  villageSlug={slug}
                />
              ))}
            </div>
            {pois.length > 6 && (
              <div className="spv-village__more">
                <Link to={`/villages/${slug}/places`} className="spv-village__more-link">
                  Voir tous les lieux ({pois.length})
                </Link>
              </div>
            )}
          </section>
        )}

        {/* Routes Section */}
        {routes.length > 0 && (
          <section className="spv-village__section spv-village__section--alt">
            <h2 className="spv-village__section-title">Parcours de découverte</h2>
            <div className="spv-village__routes-grid">
              {routes.slice(0, 3).map((route) => (
                <RouteCard key={route.id} route={route} showVillage={false} />
              ))}
            </div>
          </section>
        )}

        {/* Living Here Section */}
        {(village.live_here_summary || editMode) && (
          <section className="spv-village__section">
            <h2 className="spv-village__section-title">Vivre à {village.name}</h2>
            {editMode ? (
              <div>
                <label style={{ display: 'block', fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>
                  Description de la vie quotidienne
                </label>
                <textarea
                  value={editData.live_here_summary}
                  onChange={(e) => setEditData({ ...editData, live_here_summary: e.target.value })}
                  placeholder="Décrivez la vie quotidienne au village..."
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    fontSize: '16px',
                    resize: 'vertical',
                    minHeight: '120px',
                    lineHeight: '1.6'
                  }}
                />
              </div>
            ) : (
              <div className="spv-village__living">
                <p>{village.live_here_summary}</p>
              </div>
            )}
          </section>
        )}

        {/* Partners Section - placeholder for sponsors */}
        {/* TODO: Add SponsorSlots display when API ready */}

        {/* Save Button (Edit Mode) */}
        {editMode && (
          <section className="spv-village__section" style={{ paddingTop: '16px' }}>
            {saveError && (
              <div style={{
                background: '#fee2e2',
                color: '#dc2626',
                padding: '12px 16px',
                borderRadius: '8px',
                marginBottom: '16px'
              }}>
                {saveError}
              </div>
            )}

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                onClick={handleEditToggle}
                style={{
                  padding: '12px 24px',
                  background: 'white',
                  color: '#6b7280',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <XMarkIcon style={{ width: '18px', height: '18px' }} />
                Annuler
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                style={{
                  padding: '12px 24px',
                  background: '#0d9488',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: 500,
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  opacity: isSaving ? 0.7 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <CheckIcon style={{ width: '18px', height: '18px' }} />
                {isSaving ? 'Sauvegarde...' : 'Sauvegarder'}
              </button>
            </div>
          </section>
        )}

        {/* Footer CTA */}
        <section className="spv-village__cta">
          <div className="spv-village__cta-content">
            <h2 className="spv-village__cta-title">Envie de découvrir {village.name} ?</h2>
            <p className="spv-village__cta-text">
              Explorez les parcours de découverte et planifiez votre visite.
            </p>
            <div className="spv-village__cta-buttons">
              <Link to={`/villages/${slug}/routes`} className="spv-village__cta-button">
                Voir les parcours
              </Link>
              <Link to="/explore" className="spv-village__cta-button spv-village__cta-button--secondary">
                Retour à la carte
              </Link>
            </div>
          </div>
        </section>
      </div>
    </MainLayout>
  );
}
