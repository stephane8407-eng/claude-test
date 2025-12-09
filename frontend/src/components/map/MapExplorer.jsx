/**
 * MapExplorer Component
 *
 * Interactive Leaflet map showing village markers.
 * Click marker to show preview card.
 */
import { useEffect, useRef, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MapExplorer.css';

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom village marker icon (36x48 for 28-32px visual diameter)
const createVillageIcon = (isSelected = false) => {
  return L.divIcon({
    className: 'spv-map-marker',
    html: `
      <div class="spv-map-marker__pin ${isSelected ? 'spv-map-marker__pin--selected' : ''}">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
      </div>
    `,
    iconSize: [36, 48],
    iconAnchor: [18, 48],
    popupAnchor: [0, -48],
  });
};

export function MapExplorer({
  villages = [],
  selectedVillage,
  onVillageSelect,
  center = { lat: 46.2276, lng: 2.2137 }, // Default: France center
  zoom = 6,
}) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef({});

  // Initialize map
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    const map = L.map(mapRef.current, {
      center: [center.lat, center.lng],
      zoom: zoom,
      zoomControl: false,
    });

    // Add zoom control to bottom right
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Add tile layer with custom styling
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19,
    }).addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update markers when villages change
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear existing markers
    Object.values(markersRef.current).forEach((marker) => {
      map.removeLayer(marker);
    });
    markersRef.current = {};

    // Add village markers
    villages.forEach((village) => {
      if (!village.latitude || !village.longitude) return;

      const isSelected = selectedVillage?.id === village.id;
      const marker = L.marker([village.latitude, village.longitude], {
        icon: createVillageIcon(isSelected),
      });

      marker.on('click', () => {
        onVillageSelect(village);
      });

      marker.addTo(map);
      markersRef.current[village.id] = marker;
    });

    // Fit bounds if we have villages
    if (villages.length > 0) {
      const validVillages = villages.filter((v) => v.latitude && v.longitude);
      if (validVillages.length > 0) {
        const bounds = L.latLngBounds(
          validVillages.map((v) => [v.latitude, v.longitude])
        );
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
      }
    }
  }, [villages, onVillageSelect]);

  // Update selected marker styling
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    Object.entries(markersRef.current).forEach(([id, marker]) => {
      const isSelected = selectedVillage?.id === parseInt(id);
      marker.setIcon(createVillageIcon(isSelected));
    });

    // Pan to selected village
    if (selectedVillage?.latitude && selectedVillage?.longitude) {
      map.panTo([selectedVillage.latitude, selectedVillage.longitude], {
        animate: true,
        duration: 0.5,
      });
    }
  }, [selectedVillage]);

  return (
    <div className="spv-map-explorer">
      <div ref={mapRef} className="spv-map-explorer__map" />
    </div>
  );
}
