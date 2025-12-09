/**
 * ExplorePage - Map Explorer
 *
 * Interactive map page for exploring villages.
 * URL: /explore
 * Layout: Top nav | Filter panel (left) | Map (center) | Preview card (right)
 */
import { useState, useEffect, useMemo } from 'react';
import { MainLayout } from '../components/layout/index';
import { FilterPanel, MapExplorer, VillagePreviewCard } from '../components/map/index';
import { villageAPI } from '../services/api';
import './ExplorePage.css';

export function ExplorePage() {
  // State
  const [villages, setVillages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedThemes, setSelectedThemes] = useState([]);
  const [filterPanelOpen, setFilterPanelOpen] = useState(false);

  // Map state
  const [selectedVillage, setSelectedVillage] = useState(null);

  // Fetch villages on mount
  useEffect(() => {
    loadVillages();
  }, []);

  const loadVillages = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await villageAPI.list();
      // Handle both array and paginated response
      const villageList = Array.isArray(data) ? data : data.results || [];
      setVillages(villageList);
    } catch (err) {
      console.error('Failed to load villages:', err);
      setError('Impossible de charger les villages');
    } finally {
      setLoading(false);
    }
  };

  // Filter villages based on search and themes
  const filteredVillages = useMemo(() => {
    return villages.filter((village) => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesName = village.name?.toLowerCase().includes(query);
        const matchesSummary = village.summary_identity?.toLowerCase().includes(query);
        const matchesTheme = village.themes?.some((t) =>
          t.toLowerCase().includes(query)
        );
        if (!matchesName && !matchesSummary && !matchesTheme) {
          return false;
        }
      }

      // Theme filter
      if (selectedThemes.length > 0) {
        const villageThemes = village.themes || [];
        const hasMatchingTheme = selectedThemes.some((theme) =>
          villageThemes.includes(theme)
        );
        if (!hasMatchingTheme) {
          return false;
        }
      }

      return true;
    });
  }, [villages, searchQuery, selectedThemes]);

  // Handlers
  const handleThemeToggle = (theme) => {
    setSelectedThemes((prev) =>
      prev.includes(theme)
        ? prev.filter((t) => t !== theme)
        : [...prev, theme]
    );
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedThemes([]);
  };

  const handleVillageSelect = (village) => {
    setSelectedVillage(village);
  };

  const handleClosePreview = () => {
    setSelectedVillage(null);
  };

  return (
    <MainLayout>
      <div className="spv-home">
        {/* Mobile Filter Toggle */}
        <button
          className="spv-home__filter-toggle"
          onClick={() => setFilterPanelOpen(true)}
          aria-label="Ouvrir les filtres"
        >
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clipRule="evenodd" />
          </svg>
          Filtres
          {selectedThemes.length > 0 && (
            <span className="spv-home__filter-badge">{selectedThemes.length}</span>
          )}
        </button>

        {/* Filter Panel */}
        <FilterPanel
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedThemes={selectedThemes}
          onThemeToggle={handleThemeToggle}
          onClearFilters={handleClearFilters}
          villageCount={filteredVillages.length}
          isOpen={filterPanelOpen}
          onClose={() => setFilterPanelOpen(false)}
        />

        {/* Main Content Area */}
        <div className="spv-home__content">
          {/* Map */}
          <div className="spv-home__map">
            {loading ? (
              <div className="spv-home__loading">
                <div className="spv-home__spinner" />
                <span>Chargement de la carte...</span>
              </div>
            ) : error ? (
              <div className="spv-home__error">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>{error}</span>
                <button onClick={loadVillages}>Réessayer</button>
              </div>
            ) : (
              <MapExplorer
                villages={filteredVillages}
                selectedVillage={selectedVillage}
                onVillageSelect={handleVillageSelect}
              />
            )}
          </div>

          {/* Village Preview Card (Desktop) */}
          {selectedVillage && (
            <div className="spv-home__preview">
              <VillagePreviewCard
                village={selectedVillage}
                onClose={handleClosePreview}
              />
            </div>
          )}
        </div>

        {/* Mobile Preview Card (Bottom Sheet) */}
        {selectedVillage && (
          <div className="spv-home__preview-mobile">
            <VillagePreviewCard
              village={selectedVillage}
              onClose={handleClosePreview}
            />
          </div>
        )}
      </div>
    </MainLayout>
  );
}
