/**
 * VillageMap Component
 *
 * Interactive map for village page showing conflicts and POIs.
 * Clean popups with proper styling per FRONTEND_STYLE_GUIDE.
 */
import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../../services/api';
import './VillageMap.css';

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Create conflict marker icon (uses teal/secondary colors instead of harsh red)
const createConflictIcon = () => {
  return L.divIcon({
    className: 'spv-marker spv-marker--conflict',
    html: `
      <div class="spv-marker__pin">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
      </div>
    `,
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -36],
  });
};

// Create POI marker icon
const createPOIIcon = () => {
  return L.divIcon({
    className: 'spv-marker spv-marker--poi',
    html: `
      <div class="spv-marker__pin">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
      </div>
    `,
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -36],
  });
};

/**
 * Create popup content for conflict/event
 */
function createConflictPopup(conflict) {
  const name = conflict.name || 'Événement historique';
  const dateText = formatConflictDate(conflict);
  const description = conflict.description
    ? (conflict.description.length > 120
      ? conflict.description.substring(0, 120) + '...'
      : conflict.description)
    : null;
  const slug = conflict.slug || conflict.id;

  return `
    <div class="spv-popup">
      <h3 class="spv-popup__title">${escapeHtml(name)}</h3>
      ${dateText ? `<p class="spv-popup__date">${escapeHtml(dateText)}</p>` : ''}
      ${description ? `<p class="spv-popup__description">${escapeHtml(description)}</p>` : '<p class="spv-popup__description spv-popup__description--empty">Détails à venir</p>'}
      <a href="/events/${slug}" class="spv-popup__link">Voir les détails →</a>
    </div>
  `;
}

/**
 * Create popup content for POI
 */
function createPOIPopup(poi) {
  const name = poi.name || 'Lieu';
  const type = poi.poi_type ? formatPOIType(poi.poi_type) : null;
  const description = poi.description
    ? (poi.description.length > 120
      ? poi.description.substring(0, 120) + '...'
      : poi.description)
    : null;
  const slug = poi.slug || poi.id;

  return `
    <div class="spv-popup">
      <h3 class="spv-popup__title">${escapeHtml(name)}</h3>
      ${type ? `<p class="spv-popup__type">${escapeHtml(type)}</p>` : ''}
      ${description ? `<p class="spv-popup__description">${escapeHtml(description)}</p>` : ''}
      <a href="/places/${slug}" class="spv-popup__link">En savoir plus →</a>
    </div>
  `;
}

function formatConflictDate(conflict) {
  if (conflict.date_text) return conflict.date_text;
  if (conflict.date) {
    const year = new Date(conflict.date).getFullYear();
    return `${year}`;
  }
  if (conflict.start_year) {
    return conflict.end_year && conflict.end_year !== conflict.start_year
      ? `${conflict.start_year} - ${conflict.end_year}`
      : `${conflict.start_year}`;
  }
  if (conflict.period) return conflict.period;
  return null;
}

function formatPOIType(type) {
  const typeLabels = {
    pond: 'Étang',
    chapel: 'Chapelle',
    church: 'Église',
    castle: 'Château',
    forge: 'Forge',
    mill: 'Moulin',
    monument: 'Monument',
    ruins: 'Ruines',
    nature: 'Site naturel',
  };
  return typeLabels[type?.toLowerCase()] || type;
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

export function VillageMap({ villageSlug, pois = [], center, showConflicts = true, showPOIs = true }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const [conflicts, setConflicts] = useState([]);
  const [layersVisible, setLayersVisible] = useState({
    conflicts: showConflicts,
    pois: showPOIs
  });

  useEffect(() => {
    if (showConflicts) {
      loadConflicts();
    }
  }, [villageSlug, showConflicts]);

  const loadConflicts = async () => {
    try {
      const response = await api.get(`/api/villages/${villageSlug}/conflicts`);
      const conflictsData = Array.isArray(response.data) ? response.data : [];
      // Only show conflicts that have descriptions or meaningful data
      const filteredConflicts = conflictsData.filter(c =>
        c.latitude && c.longitude && (c.description || c.name)
      );
      setConflicts(filteredConflicts);
    } catch (error) {
      console.error('Failed to load conflicts:', error);
      setConflicts([]);
    }
  };

  useEffect(() => {
    if (!mapRef.current) return;

    const mapCenter = center ? [center.lat, center.lng] : [46.2276, 2.2137];
    const map = L.map(mapRef.current, {
      zoomControl: false,
    }).setView(mapCenter, 13);

    // Add zoom control to bottom right
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Use CARTO Voyager tiles for consistent styling
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19,
    }).addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
    };
  }, []);

  useEffect(() => {
    if (!mapInstanceRef.current) return;

    const map = mapInstanceRef.current;

    // Clear existing markers
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer);
      }
    });

    // Add conflict markers
    const safeConflicts = Array.isArray(conflicts) ? conflicts : [];
    if (layersVisible.conflicts && safeConflicts.length > 0) {
      safeConflicts.forEach(conflict => {
        if (conflict.latitude && conflict.longitude) {
          L.marker([conflict.latitude, conflict.longitude], { icon: createConflictIcon() })
            .bindPopup(createConflictPopup(conflict), {
              className: 'spv-popup-container',
              maxWidth: 280,
              minWidth: 200,
            })
            .addTo(map);
        }
      });
    }

    // Add POI markers
    if (layersVisible.pois && pois.length > 0) {
      pois.forEach(poi => {
        if (poi.latitude && poi.longitude) {
          L.marker([poi.latitude, poi.longitude], { icon: createPOIIcon() })
            .bindPopup(createPOIPopup(poi), {
              className: 'spv-popup-container',
              maxWidth: 280,
              minWidth: 200,
            })
            .addTo(map);
        }
      });
    }
  }, [conflicts, pois, layersVisible]);

  const toggleLayer = (layerName) => {
    setLayersVisible(prev => ({
      ...prev,
      [layerName]: !prev[layerName]
    }));
  };

  return (
    <div className="spv-village-map">
      <div ref={mapRef} className="spv-village-map__map" />

      {/* Layer Controls */}
      <div className="spv-village-map__controls">
        <div className="spv-village-map__controls-title">Affichage</div>
        {showConflicts && (
          <label className="spv-village-map__control">
            <input
              type="checkbox"
              checked={layersVisible.conflicts}
              onChange={() => toggleLayer('conflicts')}
            />
            <span className="spv-village-map__control-marker spv-village-map__control-marker--conflict" />
            <span>Événements ({conflicts.length})</span>
          </label>
        )}
        {showPOIs && (
          <label className="spv-village-map__control">
            <input
              type="checkbox"
              checked={layersVisible.pois}
              onChange={() => toggleLayer('pois')}
            />
            <span className="spv-village-map__control-marker spv-village-map__control-marker--poi" />
            <span>Lieux ({pois.length})</span>
          </label>
        )}
      </div>
    </div>
  );
}
