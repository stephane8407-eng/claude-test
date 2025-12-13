import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { qrCodeAPI, poiAPI } from '../../services/api';
import {
  QrCodeIcon,
  PlusIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  ChartBarIcon,
  XMarkIcon,
  EyeIcon,
  MapPinIcon,
} from '@heroicons/react/24/outline';

export default function QRCodesPage() {
  const { user } = useAuth();
  const [qrCodes, setQrCodes] = useState([]);
  const [pois, setPois] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [selectedQR, setSelectedQR] = useState(null);
  const [stats, setStats] = useState(null);
  const [creating, setCreating] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    target_url: '',
    poi_id: '',
  });

  const villageSlug = user?.village_slug;

  useEffect(() => {
    if (villageSlug) {
      fetchQRCodes();
      fetchPOIs();
    }
  }, [villageSlug]);

  const fetchQRCodes = async () => {
    try {
      const data = await qrCodeAPI.list(villageSlug);
      setQrCodes(data || []);
    } catch (error) {
      console.error('Error fetching QR codes:', error);
      setQrCodes([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchPOIs = async () => {
    try {
      const data = await poiAPI.list(villageSlug);
      setPois(data || []);
    } catch (error) {
      console.error('Error fetching POIs:', error);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);

    try {
      const data = {
        name: formData.name,
        description: formData.description || null,
        target_url: formData.target_url,
        poi_id: formData.poi_id ? parseInt(formData.poi_id) : null,
      };

      await qrCodeAPI.create(villageSlug, data);
      await fetchQRCodes();
      setShowCreateModal(false);
      setFormData({ name: '', description: '', target_url: '', poi_id: '' });
    } catch (error) {
      console.error('Error creating QR code:', error);
      alert(error.response?.data?.detail || 'Erreur lors de la création');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (qrId) => {
    if (!confirm('Supprimer ce QR code ? Cette action est irréversible.')) return;

    try {
      await qrCodeAPI.delete(villageSlug, qrId);
      await fetchQRCodes();
    } catch (error) {
      console.error('Error deleting QR code:', error);
      alert('Erreur lors de la suppression');
    }
  };

  const handleViewStats = async (qr) => {
    setSelectedQR(qr);
    setShowStatsModal(true);

    try {
      const statsData = await qrCodeAPI.getStats(villageSlug, qr.id);
      setStats(statsData);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setStats(null);
    }
  };

  const downloadQR = (qr) => {
    // Handle both base64 data URLs and file paths
    if (qr.qr_image_url) {
      const link = document.createElement('a');
      // Check if it's a base64 data URL or a file path
      if (qr.qr_image_url.startsWith('data:')) {
        link.href = qr.qr_image_url;
      } else {
        link.href = `http://localhost:8000${qr.qr_image_url}`;
      }
      link.download = `qr-${qr.code}.png`;
      link.click();
    } else {
      alert('Image QR non disponible');
    }
  };

  const totalScans = qrCodes.reduce((sum, qr) => sum + (qr.scan_count || 0), 0);
  const avgScans = qrCodes.length > 0 ? Math.round(totalScans / qrCodes.length) : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des QR codes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-12 sm:px-16 lg:px-20 py-10">

        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-3">QR Codes</h1>
              <p className="text-gray-600 leading-relaxed">Générez et suivez les QR codes pour vos points d'intérêt</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-8 py-4 bg-teal-600 text-white rounded-xl hover:bg-teal-700 transition-colors font-medium cursor-pointer flex items-center gap-3 shadow-md"
            >
              <PlusIcon className="w-5 h-5" />
              Créer un QR Code
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mb-14">
          <div className="bg-white rounded-2xl shadow-md p-12 hover:shadow-lg transition-all border border-transparent hover:border-teal-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-3">Total QR Codes</p>
                <p className="text-4xl font-bold text-gray-900">{qrCodes.length}</p>
                <p className="text-sm text-gray-400 mt-3">codes générés</p>
              </div>
              <div className="w-20 h-20 bg-teal-100 rounded-2xl flex items-center justify-center ml-6">
                <QrCodeIcon className="w-10 h-10 text-teal-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-md p-12 hover:shadow-lg transition-all border border-transparent hover:border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-3">Scans totaux</p>
                <p className="text-4xl font-bold text-gray-900">{totalScans}</p>
                <p className="text-sm text-gray-400 mt-3">visiteurs</p>
              </div>
              <div className="w-20 h-20 bg-purple-100 rounded-2xl flex items-center justify-center ml-6">
                <EyeIcon className="w-10 h-10 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-md p-12 hover:shadow-lg transition-all border border-transparent hover:border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-3">Moyenne / QR</p>
                <p className="text-4xl font-bold text-gray-900">{avgScans}</p>
                <p className="text-sm text-gray-400 mt-3">scans par code</p>
              </div>
              <div className="w-20 h-20 bg-blue-100 rounded-2xl flex items-center justify-center ml-6">
                <ChartBarIcon className="w-10 h-10 text-blue-600" />
              </div>
            </div>
          </div>
        </div>

        {/* QR Codes Grid */}
        {qrCodes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
            {qrCodes.map((qr) => (
              <div key={qr.id} className="bg-white rounded-2xl shadow-md p-12 hover:shadow-lg transition-all">

                {/* QR Image */}
                <div className="bg-gray-100 rounded-xl p-10 mb-8 flex items-center justify-center">
                  {qr.qr_image_url ? (
                    <img
                      src={qr.qr_image_url.startsWith('data:') ? qr.qr_image_url : `http://localhost:8000${qr.qr_image_url}`}
                      alt={qr.name}
                      className="w-48 h-48 object-contain"
                    />
                  ) : (
                    <QrCodeIcon className="w-48 h-48 text-gray-300" />
                  )}
                </div>

                {/* Details */}
                <h3 className="font-bold text-gray-900 text-xl mb-4">{qr.name}</h3>
                {qr.description && (
                  <p className="text-sm text-gray-600 mb-6 line-clamp-2 leading-relaxed">{qr.description}</p>
                )}

                <p className="text-xs text-gray-400 mb-6 font-mono truncate">{qr.code}</p>

                <div className="flex items-center gap-3 mb-8 flex-wrap">
                  <span className="px-4 py-2 bg-teal-100 text-teal-700 rounded-full text-sm font-medium">
                    {qr.poi_id ? 'POI' : qr.battle_id ? 'Bataille' : 'URL'}
                  </span>
                  <span className="px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                    {qr.scan_count || 0} scans
                  </span>
                  {qr.is_active ? (
                    <span className="px-4 py-2 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                      Actif
                    </span>
                  ) : (
                    <span className="px-4 py-2 bg-gray-100 text-gray-500 rounded-full text-sm font-medium">
                      Inactif
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-4">
                  <button
                    onClick={() => downloadQR(qr)}
                    className="flex-1 px-8 py-4 bg-teal-50 text-teal-600 rounded-xl hover:bg-teal-100 transition-colors font-medium cursor-pointer flex items-center justify-center gap-3"
                  >
                    <ArrowDownTrayIcon className="w-5 h-5" />
                    Télécharger
                  </button>
                  <button
                    onClick={() => handleViewStats(qr)}
                    className="px-6 py-4 bg-blue-50 text-blue-600 rounded-xl hover:bg-blue-100 transition-colors cursor-pointer"
                    title="Voir les statistiques"
                  >
                    <ChartBarIcon className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(qr.id)}
                    className="px-6 py-4 bg-red-50 text-red-600 rounded-xl hover:bg-red-100 transition-colors cursor-pointer"
                    title="Supprimer"
                  >
                    <TrashIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Empty State */
          <div className="bg-white rounded-2xl shadow-md p-16 text-center">
            <QrCodeIcon className="w-24 h-24 text-gray-300 mx-auto mb-8" />
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Aucun QR code</h3>
            <p className="text-gray-600 mb-10 max-w-md mx-auto leading-relaxed">
              Créez votre premier QR code pour permettre aux visiteurs d'accéder facilement à vos points d'intérêt.
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-10 py-4 bg-teal-600 text-white rounded-xl hover:bg-teal-700 transition-colors font-medium cursor-pointer inline-flex items-center gap-3"
            >
              <PlusIcon className="w-5 h-5" />
              Créer mon premier QR Code
            </button>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
          <div className="bg-white rounded-2xl p-10 max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Créer un QR Code</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-3 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer"
              >
                <XMarkIcon className="w-6 h-6 text-gray-500" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Nom du QR Code *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-5 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="Ex: Église Saint-Pierre"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-5 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="Description optionnelle..."
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  URL de destination *
                </label>
                <input
                  type="url"
                  value={formData.target_url}
                  onChange={(e) => setFormData({ ...formData, target_url: e.target.value })}
                  className="w-full px-5 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  placeholder="https://votre-site.com/page"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Lier à un POI (optionnel)
                </label>
                <select
                  value={formData.poi_id}
                  onChange={(e) => setFormData({ ...formData, poi_id: e.target.value })}
                  className="w-full px-5 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-transparent cursor-pointer"
                >
                  <option value="">-- Aucun POI --</option>
                  {pois.map((poi) => (
                    <option key={poi.id} value={poi.id}>
                      {poi.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex gap-4 pt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-8 py-4 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors font-medium cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="flex-1 px-8 py-4 bg-teal-600 text-white rounded-xl hover:bg-teal-700 transition-colors font-medium cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
                >
                  {creating ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Création...
                    </>
                  ) : (
                    <>
                      <QrCodeIcon className="w-5 h-5" />
                      Générer le QR Code
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Stats Modal */}
      {showStatsModal && selectedQR && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
          <div className="bg-white rounded-2xl p-10 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Statistiques: {selectedQR.name}</h2>
              <button
                onClick={() => { setShowStatsModal(false); setStats(null); }}
                className="p-3 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer"
              >
                <XMarkIcon className="w-6 h-6 text-gray-500" />
              </button>
            </div>

            {stats ? (
              <div className="space-y-8">
                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-6">
                  <div className="bg-teal-50 rounded-xl p-8">
                    <p className="text-sm text-teal-600 font-medium mb-2">Total scans</p>
                    <p className="text-4xl font-bold text-teal-700">{stats.total_scans}</p>
                  </div>
                  <div className="bg-purple-50 rounded-xl p-8">
                    <p className="text-sm text-purple-600 font-medium mb-2">Visiteurs uniques</p>
                    <p className="text-4xl font-bold text-purple-700">{stats.unique_visitors}</p>
                  </div>
                </div>

                {/* Device Breakdown */}
                {Object.keys(stats.scans_by_device || {}).length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-4">Par appareil</h3>
                    <div className="space-y-3">
                      {Object.entries(stats.scans_by_device).map(([device, count]) => (
                        <div key={device} className="flex items-center justify-between bg-gray-50 px-6 py-4 rounded-lg">
                          <span className="capitalize text-gray-700">{device}</span>
                          <span className="font-medium text-gray-900">{count} scans</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recent Scans */}
                {stats.recent_scans?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-4">Scans récents</h3>
                    <div className="space-y-3 max-h-60 overflow-y-auto">
                      {stats.recent_scans.map((scan, idx) => (
                        <div key={idx} className="flex items-center justify-between bg-gray-50 px-6 py-4 rounded-lg text-sm">
                          <div>
                            <span className="text-gray-700 capitalize">{scan.device_type}</span>
                            {scan.browser && <span className="text-gray-400 ml-2">• {scan.browser}</span>}
                          </div>
                          <span className="text-gray-500">
                            {new Date(scan.scanned_at).toLocaleString('fr-FR')}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-10 h-10 border-4 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Chargement des statistiques...</p>
              </div>
            )}

            <div className="mt-8 pt-8 border-t border-gray-200">
              <button
                onClick={() => { setShowStatsModal(false); setStats(null); }}
                className="w-full px-8 py-4 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors font-medium cursor-pointer"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
