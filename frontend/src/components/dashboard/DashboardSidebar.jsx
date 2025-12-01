import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  MapPinIcon,
  QrCodeIcon,
  ChartBarIcon,
  CogIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Audit Identité', href: '/dashboard/identity-audit', icon: LightBulbIcon },
  { name: 'POIs', href: '/dashboard/pois', icon: MapPinIcon },
  { name: 'QR Codes', href: '/dashboard/qr-codes', icon: QrCodeIcon },
  { name: 'Analytics', href: '/dashboard/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/dashboard/settings', icon: CogIcon },
];

export function DashboardSidebar() {
  const location = useLocation();

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
      </nav>
    </div>
  );
}
