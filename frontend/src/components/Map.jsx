import React, { useState, useEffect, useCallback } from 'react';
import MapGL, { Marker, Popup, NavigationControl, ScaleControl, FullscreenControl } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import BattlePopup from './BattlePopup';
import ConflictPopup from './ConflictPopup';
import './Map.css';

// Mapbox access token
const MAPBOX_TOKEN = 'pk.eyJ1Ijoic3RlcGhhbmU4NyIsImEiOiJjbWk4eHAweXowNzhqMmxyNHkyemhmaHBmIn0.mKTbBzbLTf5rQEaQ35CD-w';

// Color scheme for war periods
const WAR_PERIOD_COLORS = {
  'WW1': '#dc2626',           // red
  'WW2': '#991b1b',           // darkred
  'Napoleonic Wars': '#2563eb', // blue
  'Hundred Years War': '#7c3aed', // purple
  'Medieval': '#16a34a',      // green
};

const DEFAULT_COLOR = '#6b7280'; // gray for others

const getMarkerColor = (warPeriod) => {
  return WAR_PERIOD_COLORS[warPeriod] || DEFAULT_COLOR;
};

const Map = () => {
  const [viewState, setViewState] = useState({
    longitude: 2.2137,
    latitude: 46.2276,
    zoom: 6
  });

  const [battles, setBattles] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [selectedBattle, setSelectedBattle] = useState(null);
  const [selectedConflict, setSelectedConflict] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch battles from API
  useEffect(() => {
    const fetchBattles = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/battles/?limit=1000');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setBattles(data.results || []);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch battles:', err);
        setError('Failed to load battles. Make sure the backend API is running at http://localhost:8000');
      } finally {
        setLoading(false);
      }
    };

    fetchBattles();
  }, []);

  // Fetch conflicts from API
  useEffect(() => {
    const fetchConflicts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/conflicts/?limit=1000');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setConflicts(data.results || []);
      } catch (err) {
        console.error('Failed to fetch conflicts:', err);
        // Don't set error state here - conflicts are optional
      }
    };

    fetchConflicts();
  }, []);

  const handleMarkerClick = useCallback((battle, e) => {
    e.originalEvent.stopPropagation();
    setSelectedBattle(battle);
    setSelectedConflict(null);
  }, []);

  const handleConflictMarkerClick = useCallback((conflict, e) => {
    e.originalEvent.stopPropagation();
    setSelectedConflict(conflict);
    setSelectedBattle(null);
  }, []);

  const handleClosePopup = useCallback(() => {
    setSelectedBattle(null);
    setSelectedConflict(null);
  }, []);

  return (
    <div className="map-container">
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Loading battles...</p>
        </div>
      )}

      {error && (
        <div className="error-overlay">
          <div className="error-message">
            <h3>⚠️ Error</h3>
            <p>{error}</p>
          </div>
        </div>
      )}

      <MapGL
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/outdoors-v12"
        mapboxAccessToken={MAPBOX_TOKEN}
      >
        {/* Navigation controls (zoom buttons) */}
        <NavigationControl position="top-right" />

        {/* Scale control */}
        <ScaleControl position="bottom-right" />

        {/* Fullscreen control */}
        <FullscreenControl position="top-right" />

        {/* Battle markers */}
        {battles.map((battle) => (
          <Marker
            key={`battle-${battle.id}`}
            longitude={battle.longitude}
            latitude={battle.latitude}
            anchor="bottom"
            onClick={(e) => handleMarkerClick(battle, e)}
          >
            <div
              className="marker-pin"
              style={{
                backgroundColor: getMarkerColor(battle.war_period),
                cursor: 'pointer'
              }}
              title={battle.name}
            >
              <div className="marker-pulse" style={{ borderColor: getMarkerColor(battle.war_period) }} />
            </div>
          </Marker>
        ))}

        {/* Conflict markers (AI-scraped, shown in red) */}
        {conflicts.map((conflict) => (
          <Marker
            key={`conflict-${conflict.id}`}
            longitude={conflict.longitude}
            latitude={conflict.latitude}
            anchor="bottom"
            onClick={(e) => handleConflictMarkerClick(conflict, e)}
          >
            <div
              className="marker-pin conflict-marker"
              style={{
                backgroundColor: '#f97316',
                cursor: 'pointer'
              }}
              title={conflict.name}
            >
              <div className="marker-pulse" style={{ borderColor: '#f97316' }} />
            </div>
          </Marker>
        ))}

        {/* Battle Popup */}
        {selectedBattle && (
          <Popup
            longitude={selectedBattle.longitude}
            latitude={selectedBattle.latitude}
            anchor="top"
            onClose={handleClosePopup}
            closeOnClick={false}
            className="battle-popup-container"
          >
            <BattlePopup battle={selectedBattle} />
          </Popup>
        )}

        {/* Conflict Popup */}
        {selectedConflict && (
          <Popup
            longitude={selectedConflict.longitude}
            latitude={selectedConflict.latitude}
            anchor="top"
            onClose={handleClosePopup}
            closeOnClick={false}
            className="conflict-popup-container"
          >
            <ConflictPopup conflict={selectedConflict} />
          </Popup>
        )}
      </MapGL>

      {/* Battle & Conflict count indicator */}
      {!loading && !error && (
        <div className="battle-count">
          {battles.length} battles • {conflicts.length} conflicts loaded
        </div>
      )}

      {/* Legend */}
      {!loading && !error && (
        <div className="legend">
          <h4>War Periods</h4>
          <div className="legend-items">
            {Object.entries(WAR_PERIOD_COLORS).map(([period, color]) => (
              <div key={period} className="legend-item">
                <div className="legend-color" style={{ backgroundColor: color }}></div>
                <span>{period}</span>
              </div>
            ))}
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: DEFAULT_COLOR }}></div>
              <span>Other</span>
            </div>
          </div>

          {conflicts.length > 0 && (
            <>
              <h4 style={{ marginTop: '16px' }}>AI Deep Analysis</h4>
              <div className="legend-items">
                <div className="legend-item">
                  <div className="legend-color" style={{ backgroundColor: '#f97316' }}></div>
                  <span>🔍 AI-Discovered Conflicts (Deep Analysis)</span>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default Map;
