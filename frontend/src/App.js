import React, { useState, useEffect } from 'react';
import './styles/App.css';
import BattleMap from './components/BattleMap';
import FilterPanel from './components/FilterPanel';

function App() {
  const [battles, setBattles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ country: '', warPeriod: '' });

  useEffect(() => {
    fetch('http://localhost:8000/api/battles')
      .then(res => {
        if (!res.ok) throw new Error('Backend not running');
        return res.json();
      })
      .then(data => {
        setBattles(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error:', err);
        setError('Backend API not running. Start backend first!');
        setLoading(false);
      });
  }, []);

  const filteredBattles = battles.filter(battle => {
    if (filters.country && battle.country !== filters.country) return false;
    if (filters.warPeriod && battle.war_period !== filters.warPeriod) return false;
    return true;
  });

  return (
    <div className="App">
      <header className="App-header">
        <h1>⚔️ SPV Treasure Map - Historical Battles</h1>
      </header>
      <FilterPanel 
        filters={filters}
        onFilterChange={setFilters}
        battleCount={filteredBattles.length}
      />
      {error ? (
        <div className="loading" style={{color: '#ef4444'}}>
          ❌ {error}
        </div>
      ) : loading ? (
        <div className="loading">Loading battles...</div>
      ) : (
        <BattleMap battles={filteredBattles} />
      )}
    </div>
  );
}

export default App;
