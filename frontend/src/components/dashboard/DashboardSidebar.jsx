import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  HomeIcon,
  MapPinIcon,
  QrCodeIcon,
  ChartBarIcon,
  CogIcon,
  LightBulbIcon,
  BookOpenIcon,
  CurrencyEuroIcon,
  FolderIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Tableau de bord', href: '/dashboard', icon: HomeIcon },
  { name: 'Gestion de Projets', href: '/dashboard/projects', icon: FolderIcon },
  { name: 'Audit Identité', href: '/dashboard/identity-audit', icon: LightBulbIcon },
  { name: 'Points d\'intérêt', href: '/dashboard/pois', icon: MapPinIcon, disabled: true, badge: 'À venir' },
  { name: 'QR Codes', href: '/dashboard/qr-codes', icon: QrCodeIcon, disabled: true, badge: 'À venir' },
  { name: 'Analyses', href: '/dashboard/analytics', icon: ChartBarIcon, disabled: true, badge: 'À venir' },
  { name: 'Paramètres', href: '/dashboard/settings', icon: CogIcon, disabled: true, badge: 'À venir' },
];

// Platform admin only pages
const adminNavigation = [
  { name: 'Études de cas', href: '/dashboard/case-studies', icon: BookOpenIcon },
  { name: 'Financements', href: '/dashboard/funding-programs', icon: CurrencyEuroIcon },
];

export function DashboardSidebar() {
  const location = useLocation();
  const { user } = useAuth();

  // Check if user is platform admin (for now, show to all authenticated users)
  const isPlatformAdmin = user?.role === 'platform_admin' || user?.role === 'village_admin';

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <h1 className="text-xl font-bold">SPV Treasure Map</h1>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;

          if (item.disabled) {
            return (
              <div
                key={item.name}
                className="flex items-center justify-between px-4 py-2 rounded-md text-gray-500 cursor-not-allowed"
              >
                <div className="flex items-center">
                  <item.icon className="h-5 w-5 mr-3" />
                  {item.name}
                </div>
                {item.badge && (
                  <span className="text-xs bg-gray-700 text-gray-400 px-2 py-0.5 rounded-full">
                    {item.badge}
                  </span>
                )}
              </div>
            );
          }

          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center px-4 py-2 rounded-md transition ${
                isActive
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <item.icon className="h-5 w-5 mr-3" />
              {item.name}
            </Link>
          );
        })}

        {/* Platform Admin Section */}
        {isPlatformAdmin && (
          <>
            <div className="pt-4 mt-4 border-t border-gray-800">
              <p className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Plateforme Admin
              </p>
            </div>
            {adminNavigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-4 py-2 rounded-md transition ${
                    isActive
                      ? 'bg-gray-800 text-white'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`}
                >
                  <item.icon className="h-5 w-5 mr-3" />
                  {item.name}
                </Link>
              );
            })}
          </>
        )}
      </nav>
    </div>
  );
}
