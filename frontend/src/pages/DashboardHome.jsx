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
          <p className="text-gray-600 leading-relaxed">Chargement du tableau de bord...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

        {/* Header with Greeting */}
        <div className="mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-3">
            {getTodayGreeting()}, {getUserFirstName()} 👋
          </h1>
          <p className="text-gray-600 text-lg leading-relaxed">
            {new Date().toLocaleDateString('fr-FR', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {/* POIs Card */}
          <div className="bg-white rounded-xl shadow-md p-10 hover:shadow-lg transition-all duration-200 border border-transparent hover:border-teal-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-3">Points d'intérêt</p>
                <p className="text-5xl font-bold text-gray-900 mb-2">{stats?.totalPOIs || 0}</p>
                <p className="text-sm text-gray-400 mt-3">lieux référencés</p>
              </div>
              <div className="w-20 h-20 bg-teal-100 rounded-2xl flex items-center justify-center">
                <MapPinIcon className="w-10 h-10 text-teal-600" />
              </div>
            </div>
          </div>

          {/* QR Codes Card */}
          <div className="bg-white rounded-xl shadow-md p-10 hover:shadow-lg transition-all duration-200 border border-transparent hover:border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-3">QR Codes</p>
                <p className="text-5xl font-bold text-gray-900 mb-2">{stats?.totalQRCodes || 0}</p>
                <p className="text-sm text-gray-400 mt-3">codes générés</p>
              </div>
              <div className="w-20 h-20 bg-blue-100 rounded-2xl flex items-center justify-center">
                <QrCodeIcon className="w-10 h-10 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Scans Card */}
          <div className="bg-white rounded-xl shadow-md p-10 hover:shadow-lg transition-all duration-200 border border-transparent hover:border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-3">Scans totaux</p>
                <p className="text-5xl font-bold text-gray-900 mb-2">{stats?.totalScans || 0}</p>
                <p className="text-sm text-gray-400 mt-3">visiteurs</p>
              </div>
              <div className="w-20 h-20 bg-purple-100 rounded-2xl flex items-center justify-center">
                <ChartBarIcon className="w-10 h-10 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">

          {/* Identity Widget - Takes 2 columns */}
          <div className="lg:col-span-2 bg-gradient-to-br from-teal-50 to-white rounded-xl shadow-md p-10 border border-teal-100">
            <div className="flex items-center gap-5 mb-8">
              <div className="w-16 h-16 bg-teal-600 rounded-xl flex items-center justify-center shadow-md">
                <span className="text-3xl">🎭</span>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Mon Identité Village</h3>
                <p className="text-base text-gray-500 leading-relaxed">Profil identitaire de votre commune</p>
              </div>
            </div>

            {identityLoading ? (
              <div className="flex items-center gap-4 py-12">
                <div className="w-6 h-6 border-2 border-teal-600 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-gray-500 leading-relaxed">Chargement...</p>
              </div>
            ) : savedIdentity ? (
              <>
                <div className="flex items-center gap-3 text-sm text-gray-500 mb-6">
                  <ClockIcon className="w-5 h-5" />
                  <span>Dernière mise à jour: {formatDate(savedIdentity.updated_at)}</span>
                </div>

                <div className="bg-white rounded-xl p-6 mb-6 border border-gray-100">
                  <p className="text-gray-700 text-base leading-relaxed line-clamp-3">
                    {savedIdentity.identity_summary || 'Identité générée avec succès.'}
                  </p>
                </div>

                {savedIdentity.selected_themes?.length > 0 && (
                  <div className="flex flex-wrap gap-3 mb-8">
                    {savedIdentity.selected_themes.slice(0, 4).map((theme, idx) => (
                      <span
                        key={idx}
                        className="px-5 py-2.5 bg-teal-100 text-teal-700 rounded-full text-sm font-medium"
                      >
                        {theme.theme_name}
                      </span>
                    ))}
                    {savedIdentity.selected_themes.length > 4 && (
                      <span className="px-5 py-2.5 bg-gray-100 text-gray-600 rounded-full text-sm">
                        +{savedIdentity.selected_themes.length - 4}
                      </span>
                    )}
                  </div>
                )}

                <div className="flex flex-wrap gap-4">
                  <button
                    onClick={() => navigate(`/villages/${user.village_slug}`)}
                    className="flex items-center gap-3 px-8 py-4 bg-teal-600 text-white rounded-xl hover:bg-teal-700 transition-colors font-medium shadow-sm cursor-pointer text-base"
                  >
                    <EyeIcon className="w-5 h-5" />
                    Voir la page village
                  </button>
                  <button
                    onClick={() => navigate('/dashboard/identity-audit')}
                    className="flex items-center gap-3 px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-xl hover:border-teal-500 hover:text-teal-600 transition-colors font-medium bg-white cursor-pointer text-base"
                  >
                    <ArrowPathIcon className="w-5 h-5" />
                    Régénérer
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center py-10">
                <div className="w-24 h-24 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <SparklesIcon className="w-12 h-12 text-teal-600" />
                </div>
                <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                  Créez l'identité unique de votre village grâce à notre assistant IA
                </p>
                <button
                  onClick={() => navigate('/dashboard/identity-audit')}
                  className="inline-flex items-center gap-3 px-10 py-5 bg-teal-600 text-white rounded-xl hover:bg-teal-700 transition-colors font-medium shadow-sm cursor-pointer text-lg"
                >
                  <SparklesIcon className="w-6 h-6" />
                  Créer mon identité
                </button>
              </div>
            )}
          </div>

          {/* Recent QR Codes - Takes 1 column */}
          <div className="bg-white rounded-xl shadow-md p-8 border border-transparent hover:border-gray-200 transition-all">
            <div className="flex items-center justify-between mb-8">
              <h3 className="text-xl font-bold text-gray-900">QR Codes récents</h3>
              <Link
                to="/dashboard/qr-codes"
                className="text-sm text-teal-600 hover:text-teal-700 font-medium flex items-center gap-2 cursor-pointer"
              >
                Voir tous
                <ArrowRightIcon className="w-4 h-4" />
              </Link>
            </div>

            {stats?.recentQRCodes?.length > 0 ? (
              <div className="space-y-4">
                {stats.recentQRCodes.slice(0, 4).map((qr) => (
                  <Link
                    key={qr.id}
                    to={`/dashboard/qr-codes/${qr.id}`}
                    className="flex items-center justify-between p-5 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors group cursor-pointer"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center">
                        <QrCodeIcon className="w-7 h-7 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 text-base">{qr.name}</p>
                        <p className="text-sm text-gray-500 mt-1">{qr.scan_count} scans</p>
                      </div>
                    </div>
                    <ArrowRightIcon className="w-5 h-5 text-gray-400 group-hover:text-teal-600 transition-colors" />
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-5">
                  <QrCodeIcon className="w-8 h-8 text-gray-400" />
                </div>
                <p className="text-base text-gray-500 mb-5 leading-relaxed">Aucun QR code créé</p>
                <Link
                  to="/dashboard/qr-codes?action=generate"
                  className="text-base text-teal-600 hover:text-teal-700 font-medium cursor-pointer"
                >
                  Créer un QR code →
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions - HORIZONTAL GRID */}
        <div className="mb-12">
          <h3 className="text-xl font-bold text-gray-900 mb-8">Actions rapides</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">

            {/* Add POI */}
            <button
              onClick={() => navigate('/dashboard/pois?action=create')}
              className="bg-white rounded-xl shadow-md p-8 hover:shadow-lg border-2 border-transparent hover:border-teal-400 transition-all duration-200 group cursor-pointer text-left"
            >
              <div className="w-16 h-16 bg-teal-100 rounded-xl flex items-center justify-center mb-5 group-hover:bg-teal-200 transition-colors">
                <MapPinIcon className="w-8 h-8 text-teal-600" />
              </div>
              <p className="font-semibold text-gray-900 text-lg mb-3">Ajouter un POI</p>
              <p className="text-sm text-gray-500 leading-relaxed">Créer un point d'intérêt</p>
            </button>

            {/* Generate QR */}
            <button
              onClick={() => navigate('/dashboard/qr-codes?action=generate')}
              className="bg-white rounded-xl shadow-md p-8 hover:shadow-lg border-2 border-transparent hover:border-blue-400 transition-all duration-200 group cursor-pointer text-left"
            >
              <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center mb-5 group-hover:bg-blue-200 transition-colors">
                <QrCodeIcon className="w-8 h-8 text-blue-600" />
              </div>
              <p className="font-semibold text-gray-900 text-lg mb-3">Générer QR Code</p>
              <p className="text-sm text-gray-500 leading-relaxed">Créer un code traçable</p>
            </button>

            {/* Projects */}
            <button
              onClick={() => navigate('/dashboard/projects')}
              className="bg-white rounded-xl shadow-md p-8 hover:shadow-lg border-2 border-transparent hover:border-orange-400 transition-all duration-200 group cursor-pointer text-left"
            >
              <div className="w-16 h-16 bg-orange-100 rounded-xl flex items-center justify-center mb-5 group-hover:bg-orange-200 transition-colors">
                <FolderIcon className="w-8 h-8 text-orange-600" />
              </div>
              <p className="font-semibold text-gray-900 text-lg mb-3">Mes Projets</p>
              <p className="text-sm text-gray-500 leading-relaxed">Gérer les projets village</p>
            </button>

            {/* Funding */}
            <button
              onClick={() => navigate('/dashboard/funding-programs')}
              className="bg-white rounded-xl shadow-md p-8 hover:shadow-lg border-2 border-transparent hover:border-green-400 transition-all duration-200 group cursor-pointer text-left"
            >
              <div className="w-16 h-16 bg-green-100 rounded-xl flex items-center justify-center mb-5 group-hover:bg-green-200 transition-colors">
                <CurrencyEuroIcon className="w-8 h-8 text-green-600" />
              </div>
              <p className="font-semibold text-gray-900 text-lg mb-3">Financements</p>
              <p className="text-sm text-gray-500 leading-relaxed">Trouver des subventions</p>
            </button>

          </div>
        </div>

        {/* Help Section */}
        <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-xl shadow-lg p-10 text-white">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex items-center gap-6">
              <div className="w-16 h-16 bg-white/10 rounded-xl flex items-center justify-center">
                <DocumentTextIcon className="w-8 h-8 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-2xl mb-2">Besoin d'aide ?</h3>
                <p className="text-gray-300 text-base leading-relaxed">Consultez notre guide de démarrage rapide</p>
              </div>
            </div>
            <button className="px-8 py-4 bg-white text-gray-900 rounded-xl hover:bg-gray-100 transition-colors font-medium text-base whitespace-nowrap cursor-pointer">
              Voir le guide
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
