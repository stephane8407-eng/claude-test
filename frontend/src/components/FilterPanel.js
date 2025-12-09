import React from 'react';
import '../styles/FilterPanel.css';

function FilterPanel({ filters, onFilterChange, battleCount }) {
  const update = (field, value) => onFilterChange({ ...filters, [field]: value });
  
  return (
    <div className="filter-panel">
      <div className="filter-group">
        <label>Country:</label>
        <select value={filters.country} onChange={(e) => update('country', e.target.value)}>
          <option value="">All</option>
          <option value="FR">France</option>
        </select>
      </div>
      <span className="battle-count">{battleCount} battles</span>
    </div>
  );
}

export default FilterPanel;
