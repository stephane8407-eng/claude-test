import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  HomeIcon,
  MapPinIcon,
  QrCodeIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  SparklesIcon,
  BookOpenIcon,
  CurrencyEuroIcon,
  FolderIcon,
} from '@heroicons/react/24/outline';

const mainNavigation = [
  { name: 'Tableau de bord', href: '/dashboard', icon: HomeIcon },
  { name: 'Gestion de Projets', href: '/dashboard/projects', icon: FolderIcon },
  { name: 'Audit Identité', href: '/dashboard/identity-audit', icon: SparklesIcon },
  { name: 'QR Codes', href: '/dashboard/qr-codes', icon: QrCodeIcon },
];

const comingSoonNavigation = [
  { name: 'Points d\'intérêt', href: '/dashboard/pois', icon: MapPinIcon },
  { name: 'Analyses', href: '/dashboard/analytics', icon: ChartBarIcon },
  { name: 'Paramètres', href: '/dashboard/settings', icon: Cog6ToothIcon },
];

const adminNavigation = [
  { name: 'Études de cas', href: '/dashboard/case-studies', icon: BookOpenIcon },
  { name: 'Financements', href: '/dashboard/funding-programs', icon: CurrencyEuroIcon },
];

export function DashboardSidebar() {
  const location = useLocation();
  const { user } = useAuth();

  const isPlatformAdmin = user?.role === 'platform_admin' || user?.role === 'village_admin';

  const NavLink = ({ item, disabled = false }) => {
    const isActive = location.pathname === item.href;

    if (disabled) {
      return (
        <div className="flex items-center justify-between px-4 py-3 rounded-lg text-gray-500 cursor-not-allowed">
          <div className="flex items-center gap-3">
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.name}</span>
          </div>
          <span className="text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded">
            À venir
          </span>
        </div>
      );
    }

    return (
      <Link
        to={item.href}
        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors cursor-pointer ${
          isActive
            ? 'bg-teal-600 text-white'
            : 'text-gray-300 hover:bg-gray-800 hover:text-white'
        }`}
      >
        <item.icon className="w-5 h-5" />
        <span className="font-medium">{item.name}</span>
      </Link>
    );
  };

  return (
    <div className="h-screen w-64 bg-gray-900 text-white flex flex-col">
      {/* Logo Section */}
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-xl font-bold text-white mb-1">SPV Treasure Map</h1>
        <p className="text-sm text-gray-400">{user?.village_name || 'Dashboard'}</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 overflow-y-auto">
        {/* Principal Section */}
        <div className="mb-8">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4 px-4">
            Principal
          </p>
          <div className="space-y-1">
            {mainNavigation.map((item) => (
              <NavLink key={item.name} item={item} />
            ))}
          </div>
        </div>

        {/* Coming Soon Section */}
        <div className="mb-8">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4 px-4">
            À venir
          </p>
          <div className="space-y-1">
            {comingSoonNavigation.map((item) => (
              <NavLink key={item.name} item={item} disabled />
            ))}
          </div>
        </div>

        {/* Platform Admin Section */}
        {isPlatformAdmin && (
          <div className="pt-6 border-t border-gray-800">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4 px-4">
              Plateforme Admin
            </p>
            <div className="space-y-1">
              {adminNavigation.map((item) => (
                <NavLink key={item.name} item={item} />
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* Footer */}
      <div className="p-6 border-t border-gray-800">
        <p className="text-xs text-gray-500">Version 1.0.0</p>
        <p className="text-xs text-gray-600 mt-1">© 2025 SPV Treasure Map</p>
      </div>
    </div>
  );
}
