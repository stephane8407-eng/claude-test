import { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';

export function DashboardHome() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
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
