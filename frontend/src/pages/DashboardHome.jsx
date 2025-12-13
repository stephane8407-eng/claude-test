import { useState, useEffect } from 'react';
import { analyticsAPI, identityAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import {
  MapPinIcon,
  QrCodeIcon,
  ChartBarIcon,
  PlusIcon,
  ArrowRightIcon,
  SparklesIcon,
  EyeIcon,
  ArrowPathIcon,
  ClockIcon,
  DocumentTextIcon,
  CurrencyEuroIcon,
  FolderIcon,
} from '@heroicons/react/24/outline';

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
      setSavedIdentity(null);
    } finally {
      setIdentityLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const getTodayGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Bonjour';
    if (hour < 18) return 'Bon après-midi';
    return 'Bonsoir';
  };

  const getUserFirstName = () => {
    if (user?.name) {
      return user.name.split(' ')[0];
    }
    return user?.email?.split('@')[0] || 'Admin';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement du tableau de bord...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Header with Greeting */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {getTodayGreeting()}, {getUserFirstName()} 👋
          </h1>
          <p className="text-gray-600">
            {new Date().toLocaleDateString('fr-FR', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* POIs Card */}
          <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-all duration-200 border border-transparent hover:border-teal-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Points d'intérêt</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.totalPOIs || 0}</p>
                <p className="text-xs text-gray-400 mt-1">lieux référencés</p>
              </div>
              <div className="w-14 h-14 bg-teal-100 rounded-xl flex items-center justify-center">
                <MapPinIcon className="w-7 h-7 text-teal-600" />
              </div>
            </div>
          </div>

          {/* QR Codes Card */}
          <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-all duration-200 border border-transparent hover:border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">QR Codes</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.totalQRCodes || 0}</p>
                <p className="text-xs text-gray-400 mt-1">codes générés</p>
              </div>
              <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center">
                <QrCodeIcon className="w-7 h-7 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Scans Card */}
          <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-all duration-200 border border-transparent hover:border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Scans totaux</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.totalScans || 0}</p>
                <p className="text-xs text-gray-400 mt-1">visiteurs</p>
              </div>
              <div className="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center">
                <ChartBarIcon className="w-7 h-7 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">

          {/* Identity Widget - Takes 2 columns */}
          <div className="lg:col-span-2 bg-gradient-to-br from-teal-50 to-white rounded-xl shadow-md p-6 border border-teal-100">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-12 h-12 bg-teal-600 rounded-xl flex items-center justify-center shadow-md">
                <span className="text-2xl">🎭</span>
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">Mon Identité Village</h3>
                <p className="text-sm text-gray-500">Profil identitaire de votre commune</p>
              </div>
            </div>

            {identityLoading ? (
              <div className="flex items-center gap-3 py-8">
                <div className="w-5 h-5 border-2 border-teal-600 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-gray-500">Chargement...</p>
              </div>
            ) : savedIdentity ? (
              <>
                <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
                  <ClockIcon className="w-4 h-4" />
                  <span>Dernière mise à jour: {formatDate(savedIdentity.updated_at)}</span>
                </div>

                <div className="bg-white rounded-lg p-4 mb-4 border border-gray-100">
                  <p className="text-gray-700 leading-relaxed line-clamp-3">
                    {savedIdentity.identity_summary || 'Identité générée avec succès.'}
                  </p>
                </div>

                {savedIdentity.selected_themes?.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-5">
                    {savedIdentity.selected_themes.slice(0, 4).map((theme, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1.5 bg-teal-100 text-teal-700 rounded-full text-sm font-medium"
                      >
                        {theme.theme_name}
                      </span>
                    ))}
                    {savedIdentity.selected_themes.length > 4 && (
                      <span className="px-3 py-1.5 bg-gray-100 text-gray-600 rounded-full text-sm">
                        +{savedIdentity.selected_themes.length - 4}
                      </span>
                    )}
                  </div>
                )}

                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={() => navigate(`/villages/${user.village_slug}`)}
                    className="flex items-center gap-2 px-5 py-2.5 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium shadow-sm"
                  >
                    <EyeIcon className="w-4 h-4" />
                    Voir la page village
                  </button>
                  <button
                    onClick={() => navigate('/dashboard/identity-audit')}
                    className="flex items-center gap-2 px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:border-teal-500 hover:text-teal-600 transition-colors font-medium bg-white"
                  >
                    <ArrowPathIcon className="w-4 h-4" />
                    Régénérer
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center py-6">
                <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <SparklesIcon className="w-8 h-8 text-teal-600" />
                </div>
                <p className="text-gray-600 mb-4">
                  Créez l'identité unique de votre village grâce à notre assistant IA
                </p>
                <button
                  onClick={() => navigate('/dashboard/identity-audit')}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium shadow-sm"
                >
                  <SparklesIcon className="w-5 h-5" />
                  Créer mon identité
                </button>
              </div>
            )}
          </div>

          {/* Recent QR Codes - Takes 1 column */}
          <div className="bg-white rounded-xl shadow-md p-6 border border-transparent hover:border-gray-200 transition-all">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-gray-900">QR Codes récents</h3>
              <Link
                to="/dashboard/qr-codes"
                className="text-sm text-teal-600 hover:text-teal-700 font-medium flex items-center gap-1"
              >
                Voir tous
                <ArrowRightIcon className="w-4 h-4" />
              </Link>
            </div>

            {stats?.recentQRCodes?.length > 0 ? (
              <div className="space-y-3">
                {stats.recentQRCodes.slice(0, 4).map((qr) => (
                  <Link
                    key={qr.id}
                    to={`/dashboard/qr-codes/${qr.id}`}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <QrCodeIcon className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 text-sm">{qr.name}</p>
                        <p className="text-xs text-gray-500">{qr.scan_count} scans</p>
                      </div>
                    </div>
                    <ArrowRightIcon className="w-4 h-4 text-gray-400 group-hover:text-teal-600 transition-colors" />
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <QrCodeIcon className="w-6 h-6 text-gray-400" />
                </div>
                <p className="text-sm text-gray-500 mb-3">Aucun QR code créé</p>
                <Link
                  to="/dashboard/qr-codes?action=generate"
                  className="text-sm text-teal-600 hover:text-teal-700 font-medium"
                >
                  Créer un QR code →
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Actions rapides</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Add POI */}
            <Link
              to="/dashboard/pois?action=create"
              className="bg-white rounded-xl shadow-md p-5 hover:shadow-lg border border-transparent hover:border-teal-300 transition-all duration-200 group"
            >
              <div className="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-teal-200 transition-colors">
                <MapPinIcon className="w-6 h-6 text-teal-600" />
              </div>
              <p className="font-semibold text-gray-900 mb-1">Ajouter un POI</p>
              <p className="text-sm text-gray-500">Créer un point d'intérêt</p>
            </Link>

            {/* Generate QR */}
            <Link
              to="/dashboard/qr-codes?action=generate"
              className="bg-white rounded-xl shadow-md p-5 hover:shadow-lg border border-transparent hover:border-blue-300 transition-all duration-200 group"
            >
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-blue-200 transition-colors">
                <QrCodeIcon className="w-6 h-6 text-blue-600" />
              </div>
              <p className="font-semibold text-gray-900 mb-1">Générer QR Code</p>
              <p className="text-sm text-gray-500">Créer un code traçable</p>
            </Link>

            {/* Projects - Coming Soon */}
            <div className="relative">
              <div className="bg-white rounded-xl shadow-md p-5 opacity-60 border border-gray-100">
                <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center mb-4">
                  <FolderIcon className="w-6 h-6 text-orange-600" />
                </div>
                <p className="font-semibold text-gray-900 mb-1">Mes Projets</p>
                <p className="text-sm text-gray-500">Gérer les projets village</p>
              </div>
              <span className="absolute top-3 right-3 px-2 py-1 bg-gray-200 text-gray-600 text-xs rounded-full font-medium">
                À venir
              </span>
            </div>

            {/* Funding - Coming Soon */}
            <div className="relative">
              <div className="bg-white rounded-xl shadow-md p-5 opacity-60 border border-gray-100">
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
                  <CurrencyEuroIcon className="w-6 h-6 text-green-600" />
                </div>
                <p className="font-semibold text-gray-900 mb-1">Financements</p>
                <p className="text-sm text-gray-500">Trouver des subventions</p>
              </div>
              <span className="absolute top-3 right-3 px-2 py-1 bg-gray-200 text-gray-600 text-xs rounded-full font-medium">
                À venir
              </span>
            </div>
          </div>
        </div>

        {/* Help Section */}
        <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-xl shadow-lg p-6 text-white">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center">
                <DocumentTextIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-lg">Besoin d'aide ?</h3>
                <p className="text-gray-300 text-sm">Consultez notre guide de démarrage rapide</p>
              </div>
            </div>
            <button className="px-5 py-2.5 bg-white text-gray-900 rounded-lg hover:bg-gray-100 transition-colors font-medium text-sm whitespace-nowrap">
              Voir le guide
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
