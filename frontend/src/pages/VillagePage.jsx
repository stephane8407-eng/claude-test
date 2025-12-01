/**
 * VillagePage - Public Village Detail
 *
 * Clean white design with teal accents.
 * NO blue gradients, NO AI terminology, NO confidence scores.
 */
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MainLayout } from '../components/layout/index';
import { villageAPI, poiAPI, identityAPI } from '../services/api';
import { VillageMap } from '../components/village/VillageMap';
import { PublicThemeCard } from '../components/village/PublicThemeCard';
import { PublicPlaceCard } from '../components/village/PublicPlaceCard';
import { RouteCard, ThemeChip } from '../components/ui';
import './VillagePage.css';

export function VillagePage() {
  const { slug } = useParams();
  const [village, setVillage] = useState(null);
  const [pois, setPois] = useState([]);
  const [themes, setThemes] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadVillageData();
  }, [slug]);

  const loadVillageData = async () => {
    try {
      setLoading(true);
      const [villageData, poisData, themesData] = await Promise.all([
        villageAPI.getBySlug(slug),
        poiAPI.list(slug).catch(() => []),
        identityAPI.listThemes(slug).catch(() => [])
      ]);

      setVillage(villageData);
      setPois(Array.isArray(poisData) ? poisData : []);
      setThemes(Array.isArray(themesData) ? themesData : []);
      // TODO: Load routes when API is ready
      setRoutes([]);
    } catch (err) {
      console.error('Failed to load village data:', err);
      setError('Impossible de charger les informations du village');
    } finally {
      setLoading(false);
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
        {/* Header - Clean white, no gradient */}
        <header className="spv-village__header">
          <div className="spv-village__header-content">
            <h1 className="spv-village__name">{village.name}</h1>

            {village.summary_identity && (
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
        {village.long_identity && (
          <section className="spv-village__section">
            <div className="spv-village__narrative">
              <p>{village.long_identity}</p>
            </div>
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

        {/* Identity Themes - Public friendly display */}
        {themes.length > 0 && (
          <section className="spv-village__section spv-village__section--alt">
            <h2 className="spv-village__section-title">Thèmes & Identité</h2>
            <div className="spv-village__themes-grid">
              {themes.slice(0, 3).map((theme, index) => (
                <PublicThemeCard
                  key={theme.id || index}
                  theme={theme}
                  villageSlug={slug}
                />
              ))}
            </div>
          </section>
        )}

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
        {village.live_here_summary && (
          <section className="spv-village__section">
            <h2 className="spv-village__section-title">Vivre à {village.name}</h2>
            <div className="spv-village__living">
              <p>{village.live_here_summary}</p>
            </div>
          </section>
        )}

        {/* Partners Section - placeholder for sponsors */}
        {/* TODO: Add SponsorSlots display when API ready */}

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
