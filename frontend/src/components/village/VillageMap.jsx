import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../../services/api';

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

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
      // Ensure we always set an array
      const conflictsData = Array.isArray(response.data) ? response.data : [];
      setConflicts(conflictsData);
      console.log(`Loaded ${conflictsData.length} conflicts for ${villageSlug}`);
    } catch (error) {
      console.error('Failed to load conflicts:', error);
      setConflicts([]); // Set empty array on error
    }
  };

  useEffect(() => {
    if (!mapRef.current) return;

    // Initialize map with village center or fallback to default
    const mapCenter = center ? [center.lat, center.lng] : [46.2276, 2.2137]; // Default to France center
    const map = L.map(mapRef.current).setView(mapCenter, 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
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
      const conflictIcon = L.divIcon({
        className: 'conflict-marker',
        html: '<div style="background: #dc2626; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });

      safeConflicts.forEach(conflict => {
        if (conflict.latitude && conflict.longitude) {
          const marker = L.marker([conflict.latitude, conflict.longitude], { icon: conflictIcon })
            .bindPopup(`
              <div class="p-2">
                <h3 class="font-bold text-red-700">${conflict.name}</h3>
                <p class="text-sm text-gray-600">${conflict.start_year}${conflict.end_year ? ` - ${conflict.end_year}` : ''}</p>
                <p class="text-sm mt-2">${conflict.description?.substring(0, 100)}...</p>
              </div>
            `)
            .addTo(map);
        }
      });
    }

    // Add POI markers
    if (layersVisible.pois && pois.length > 0) {
      const poiIcon = L.divIcon({
        className: 'poi-marker',
        html: '<div style="background: #16a34a; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });

      pois.forEach(poi => {
        if (poi.latitude && poi.longitude) {
          const marker = L.marker([poi.latitude, poi.longitude], { icon: poiIcon })
            .bindPopup(`
              <div class="p-2">
                <h3 class="font-bold text-green-700">${poi.name}</h3>
                <p class="text-sm text-gray-600">${poi.address || ''}</p>
                <p class="text-sm mt-2">${poi.description?.substring(0, 100)}...</p>
              </div>
            `)
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
    <div className="relative h-full">
      <div ref={mapRef} className="h-full w-full"></div>

      {/* Layer Controls */}
      <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-3 space-y-2 z-[1000]">
        <div className="font-semibold text-sm text-gray-700 mb-2">Map Layers</div>
        {showConflicts && (
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={layersVisible.conflicts}
              onChange={() => toggleLayer('conflicts')}
              className="rounded"
            />
            <span className="flex items-center text-sm">
              <span className="w-3 h-3 rounded-full bg-red-600 mr-2"></span>
              Conflicts ({Array.isArray(conflicts) ? conflicts.length : 0})
            </span>
          </label>
        )}
        {showPOIs && (
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={layersVisible.pois}
              onChange={() => toggleLayer('pois')}
              className="rounded"
            />
            <span className="flex items-center text-sm">
              <span className="w-3 h-3 rounded-full bg-green-600 mr-2"></span>
              POIs ({pois.length})
            </span>
          </label>
        )}
      </div>
    </div>
  );
}
