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
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Audit Identité', href: '/dashboard/identity-audit', icon: LightBulbIcon },
  { name: 'POIs', href: '/dashboard/pois', icon: MapPinIcon },
  { name: 'QR Codes', href: '/dashboard/qr-codes', icon: QrCodeIcon },
  { name: 'Analytics', href: '/dashboard/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/dashboard/settings', icon: CogIcon },
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
                Admin Platform
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
