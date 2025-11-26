import { useState, useEffect } from 'react';
import { poiAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export function POIManager() {
  const { user } = useAuth();
  const [pois, setPois] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadPOIs();
  }, []);

  const loadPOIs = async () => {
    try {
      const data = await poiAPI.list(user.village_slug);
      setPois(data);
    } catch (error) {
      console.error('Failed to load POIs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (poiId) => {
    if (!confirm('Delete this POI?')) return;

    try {
      await poiAPI.delete(user.village_slug, poiId);
      loadPOIs(); // Refresh list
    } catch (error) {
      alert('Failed to delete POI');
    }
  };

  if (loading) return <div>Loading POIs...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Points of Interest</h1>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Add POI
        </button>
      </div>

      {/* POI Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {pois.map((poi) => (
              <tr key={poi.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{poi.name}</div>
                  <div className="text-sm text-gray-500">{poi.address}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {poi.poi_type_id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    poi.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {poi.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button className="text-blue-600 hover:text-blue-900">Edit</button>
                  <button
                    onClick={() => handleDelete(poi.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pois.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg">
          <p className="text-gray-500">No POIs yet. Add your first one!</p>
        </div>
      )}
    </div>
  );
}
