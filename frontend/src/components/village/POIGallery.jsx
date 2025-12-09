import { useState } from 'react';
import { Link } from 'react-router-dom';
import { MapPinIcon, PhotoIcon } from '@heroicons/react/24/outline';

export function POIGallery({ pois, villageSlug }) {
  const [filter, setFilter] = useState('all');

  if (!pois || pois.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg">
        <PhotoIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">No points of interest available.</p>
      </div>
    );
  }

  const poiTypes = ['all', ...new Set(pois.map(p => p.poi_type).filter(Boolean))];
  const filteredPOIs = filter === 'all' ? pois : pois.filter(p => p.poi_type === filter);

  return (
    <div className="space-y-6">
      {/* Filter Buttons */}
      <div className="flex flex-wrap gap-2">
        {poiTypes.map(type => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-4 py-2 rounded-md transition ${
              filter === type
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {type === 'all' ? 'All' : type}
            {type === 'all' && ` (${pois.length})`}
            {type !== 'all' && ` (${pois.filter(p => p.poi_type === type).length})`}
          </button>
        ))}
      </div>

      {/* POI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPOIs.map(poi => (
          <POICard key={poi.id} poi={poi} villageSlug={villageSlug} />
        ))}
      </div>

      {filteredPOIs.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg">
          <p className="text-gray-500">No POIs match the selected filter.</p>
        </div>
      )}
    </div>
  );
}

function POICard({ poi, villageSlug }) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition">
      {/* POI Image */}
      {poi.image_url ? (
        <img
          src={poi.image_url}
          alt={poi.name}
          className="w-full h-48 object-cover"
        />
      ) : (
        <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
          <PhotoIcon className="h-16 w-16 text-blue-400" />
        </div>
      )}

      {/* POI Content */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-xl font-bold text-gray-800">{poi.name}</h3>
          {poi.poi_type && (
            <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
              {poi.poi_type}
            </span>
          )}
        </div>

        {poi.address && (
          <div className="flex items-center text-sm text-gray-600 mb-3">
            <MapPinIcon className="h-4 w-4 mr-1" />
            {poi.address}
          </div>
        )}

        <p className="text-gray-700 text-sm mb-4 line-clamp-3">
          {poi.description || 'No description available.'}
        </p>

        {/* Historical Info */}
        {poi.historical_period && (
          <div className="text-sm text-gray-600 mb-4">
            <span className="font-medium">Period:</span> {poi.historical_period}
          </div>
        )}

        {/* Actions */}
        <div className="flex space-x-2">
          <Link
            to={`/villages/${villageSlug}/pois/${poi.id}`}
            className="flex-1 px-4 py-2 bg-blue-600 text-white text-center rounded-md hover:bg-blue-700 transition text-sm"
          >
            Learn More
          </Link>
          <a
            href="#map"
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition text-sm"
          >
            Map
          </a>
        </div>
      </div>
    </div>
  );
}
