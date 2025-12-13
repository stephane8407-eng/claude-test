import { useState, useEffect } from 'react';
import { analyticsAPI, identityAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';

export function DashboardHome() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [savedIdentity, setSavedIdentity] = useState(null);
  const [identityLoading, setIdentityLoading] = useState(true);

  useEffect(() => {
    loadStats();
    loadIdentity();
  }, []);

  const loadStats = async () => {
    try {
      const data = await analyticsAPI.getDashboardStats(user.village_slug);
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadIdentity = async () => {
    try {
      const data = await identityAPI.getIdentity(user.village_slug);
      setSavedIdentity(data);
    } catch (error) {
      // No identity found - that's OK
      setSavedIdentity(null);
    } finally {
      setIdentityLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Welcome back!</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Total POIs"
          value={stats?.totalPOIs || 0}
          color="blue"
        />
        <StatCard
          title="QR Codes"
          value={stats?.totalQRCodes || 0}
          color="green"
        />
        <StatCard
          title="Total Scans"
          value={stats?.totalScans || 0}
          color="purple"
        />
      </div>

      {/* Village Identity Widget */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          Mon Identité Village
        </h2>

        {identityLoading ? (
          <p className="text-gray-500">Chargement...</p>
        ) : savedIdentity ? (
          <div>
            <p className="text-sm text-gray-500 mb-2">
              Dernière mise à jour: {new Date(savedIdentity.updated_at).toLocaleDateString('fr-FR')}
            </p>

            <p className="text-gray-700 line-clamp-3 mb-4">
              {savedIdentity.identity_summary?.substring(0, 200)}
              {savedIdentity.identity_summary?.length > 200 ? '...' : ''}
            </p>

            {savedIdentity.selected_themes?.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {savedIdentity.selected_themes.slice(0, 3).map((theme, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-teal-100 text-teal-700 text-xs rounded-full"
                  >
                    {theme.theme_name}
                  </span>
                ))}
              </div>
            )}

            <div className="flex gap-2 mt-4">
              <button
                onClick={() => navigate(`/villages/${user.village_slug}`)}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition text-sm"
              >
                Voir la page village
              </button>
              <button
                onClick={() => navigate('/dashboard/identity-audit')}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition text-sm"
              >
                Régénérer
              </button>
            </div>
          </div>
        ) : (
          <div>
            <p className="text-gray-600 mb-4">
              Aucune identité générée pour votre village.
            </p>
            <button
              onClick={() => navigate('/dashboard/identity-audit')}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition text-sm"
            >
              Créer mon identité
            </button>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            to="/dashboard/pois?action=create"
            className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 transition"
          >
            <h3 className="font-semibold text-blue-600">Add New POI</h3>
            <p className="text-sm text-gray-600">Create a point of interest</p>
          </Link>
          <Link
            to="/dashboard/qr-codes?action=generate"
            className="p-4 border border-gray-200 rounded-lg hover:border-green-500 transition"
          >
            <h3 className="font-semibold text-green-600">Generate QR Code</h3>
            <p className="text-sm text-gray-600">Create trackable QR code</p>
          </Link>
        </div>
      </div>

      {/* Recent QR Codes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent QR Codes</h2>
        <div className="space-y-2">
          {stats?.recentQRCodes?.map((qr) => (
            <div key={qr.id} className="flex items-center justify-between p-3 border-b">
              <div>
                <p className="font-medium">{qr.name}</p>
                <p className="text-sm text-gray-500">{qr.scan_count} scans</p>
              </div>
              <Link
                to={`/dashboard/qr-codes/${qr.id}`}
                className="text-blue-600 hover:text-blue-800"
              >
                View →
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, color }) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      <p className={`text-3xl font-bold mt-2 ${colors[color]}`}>{value}</p>
    </div>
  );
}
