import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/BattleMap.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const BattleMap = ({ battles }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    if (!mapInstanceRef.current) {
      mapInstanceRef.current = L.map(mapRef.current).setView([48.8566, 2.3522], 6);
      
      // CartoDB Positron - Clean, modern style
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap &copy; CartoDB',
        maxZoom: 19
      }).addTo(mapInstanceRef.current);
    }

    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    battles.forEach(battle => {
      if (battle.latitude && battle.longitude) {
        const marker = L.marker([battle.latitude, battle.longitude])
          .addTo(mapInstanceRef.current)
          .bindPopup(`
            <div class="battle-popup">
              <h3>${battle.name}</h3>
              <p><strong>Period:</strong> ${battle.war_period || 'Unknown'}</p>
              <p><strong>Date:</strong> ${battle.start_date || 'Unknown'}</p>
              <p><strong>Outcome:</strong> ${battle.outcome || 'Unknown'}</p>
            </div>
          `);
        markersRef.current.push(marker);
      }
    });
  }, [battles]);

  return (
    <div className="map-container">
      <div ref={mapRef} className="battle-map" />
      <div className="map-legend">
        <h4 style={{ margin: '0 0 0.5rem 0' }}>Legend</h4>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#3388ff' }} />
          <span>Battle Site</span>
        </div>
      </div>
    </div>
  );
};

export default BattleMap;
