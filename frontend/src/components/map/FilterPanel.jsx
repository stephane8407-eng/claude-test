/**
 * FilterPanel Component
 *
 * Search box and theme filter checkboxes for the map explorer.
 * Groups: History, Nature, Heritage
 */
import { useState } from 'react';
import { ThemeChip } from '../ui';
import './FilterPanel.css';

// Theme categories with their filters
const FILTER_GROUPS = [
  {
    id: 'history',
    label: 'Histoire',
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
      </svg>
    ),
    themes: [
      { id: 'ww2', label: 'WWII / Villages brûlés' },
      { id: 'medieval', label: 'Médiéval' },
      { id: 'roman', label: 'Romain' },
      { id: 'revolution', label: 'Révolution' },
    ],
  },
  {
    id: 'nature',
    label: 'Nature',
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
      </svg>
    ),
    themes: [
      { id: 'ponds', label: 'Étangs' },
      { id: 'rivers', label: 'Rivières' },
      { id: 'forests', label: 'Forêts' },
      { id: 'mountains', label: 'Montagnes' },
    ],
  },
  {
    id: 'heritage',
    label: 'Patrimoine',
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd" />
      </svg>
    ),
    themes: [
      { id: 'chateaux', label: 'Châteaux' },
      { id: 'churches', label: 'Églises' },
      { id: 'industrial', label: 'Patrimoine industriel' },
      { id: 'legends', label: 'Légendes' },
    ],
  },
];

export function FilterPanel({
  searchQuery = '',
  onSearchChange,
  selectedThemes = [],
  onThemeToggle,
  onClearFilters,
  villageCount = 0,
  isOpen = true,
  onClose,
}) {
  const [expandedGroups, setExpandedGroups] = useState(['history', 'nature', 'heritage']);

  const toggleGroup = (groupId) => {
    setExpandedGroups((prev) =>
      prev.includes(groupId)
        ? prev.filter((id) => id !== groupId)
        : [...prev, groupId]
    );
  };

  const hasActiveFilters = searchQuery || selectedThemes.length > 0;

  return (
    <aside className={`spv-filter-panel ${isOpen ? 'spv-filter-panel--open' : ''}`}>
      {/* Header */}
      <div className="spv-filter-panel__header">
        <h2 className="spv-filter-panel__title">Filtres</h2>
        {onClose && (
          <button className="spv-filter-panel__close" onClick={onClose} aria-label="Fermer">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>

      {/* Search Box */}
      <div className="spv-filter-panel__search">
        <div className="spv-search-box">
          <svg viewBox="0 0 20 20" fill="currentColor" className="spv-search-box__icon">
            <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
          </svg>
          <input
            type="text"
            placeholder="Rechercher un village, thème..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="spv-search-box__input"
          />
          {searchQuery && (
            <button
              className="spv-search-box__clear"
              onClick={() => onSearchChange('')}
              aria-label="Effacer"
            >
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Results Count */}
      <div className="spv-filter-panel__count">
        <span className="spv-filter-panel__count-number">{villageCount}</span>
        <span className="spv-filter-panel__count-label">
          {villageCount === 1 ? 'village trouvé' : 'villages trouvés'}
        </span>
      </div>

      {/* Active Filters */}
      {hasActiveFilters && (
        <div className="spv-filter-panel__active">
          <div className="spv-filter-panel__active-header">
            <span>Filtres actifs</span>
            <button className="spv-filter-panel__clear" onClick={onClearFilters}>
              Tout effacer
            </button>
          </div>
          <div className="spv-filter-panel__active-chips">
            {selectedThemes.map((theme) => (
              <ThemeChip
                key={theme}
                theme={theme}
                size="sm"
                removable
                onRemove={() => onThemeToggle(theme)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Filter Groups */}
      <div className="spv-filter-panel__groups">
        {FILTER_GROUPS.map((group) => (
          <div key={group.id} className="spv-filter-group">
            <button
              className="spv-filter-group__header"
              onClick={() => toggleGroup(group.id)}
              aria-expanded={expandedGroups.includes(group.id)}
            >
              <span className="spv-filter-group__icon">{group.icon}</span>
              <span className="spv-filter-group__label">{group.label}</span>
              <svg
                viewBox="0 0 20 20"
                fill="currentColor"
                className={`spv-filter-group__chevron ${
                  expandedGroups.includes(group.id) ? 'spv-filter-group__chevron--open' : ''
                }`}
              >
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>

            {expandedGroups.includes(group.id) && (
              <div className="spv-filter-group__options">
                {group.themes.map((theme) => (
                  <label key={theme.id} className="spv-filter-option">
                    <input
                      type="checkbox"
                      checked={selectedThemes.includes(theme.id)}
                      onChange={() => onThemeToggle(theme.id)}
                      className="spv-filter-option__checkbox"
                    />
                    <span className="spv-filter-option__label">{theme.label}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </aside>
  );
}
