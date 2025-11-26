import { useAuth } from '../../contexts/AuthContext';

export function DashboardHeader() {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-800">
            {user?.village_name || 'Dashboard'}
          </h2>
          <p className="text-sm text-gray-500">{user?.subscription_tier || 'Free'} Plan</p>
        </div>

        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600">{user?.email}</span>
          <button
            onClick={logout}
            className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
