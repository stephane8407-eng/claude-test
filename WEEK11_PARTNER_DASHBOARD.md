# Week 11: Partner Dashboard - Implementation Guide

## Overview

The Partner Dashboard is a React-based admin UI where village partners manage their content, QR codes, and view analytics.

## ✅ Completed

### 1. API Service Layer (`frontend/src/services/api.js`)

Complete API client with:
- ✅ Axios instance with authentication headers
- ✅ Automatic token management (localStorage)
- ✅ Request/response interceptors
- ✅ Auto-logout on 401 errors
- ✅ All API endpoints organized by domain:
  - `authAPI` - Login, register, logout, forgot password
  - `villageAPI` - Get/update village, upload logo
  - `poiAPI` - Full CRUD for POIs
  - `qrCodeAPI` - Full CRUD for QR codes + stats
  - `identityAPI` - List themes, generate new themes
  - `analyticsAPI` - Dashboard stats, scan trends

### 2. Directory Structure

```
frontend/src/
├── services/
│   └── api.js ✅ (Complete - 267 lines)
├── components/
│   ├── dashboard/    (To implement)
│   ├── auth/         (To implement)
│   └── common/       (To implement)
├── pages/            (To implement)
├── hooks/            (To implement)
└── utils/            (To implement)
```

## 📋 Implementation Roadmap

### Phase 1: Authentication (Priority: HIGH)

#### A. Auth Context (`src/contexts/AuthContext.jsx`)

```jsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored user on mount
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const data = await authAPI.login(email, password);
    setUser(data.user);
    return data;
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

#### B. Protected Route (`src/components/auth/ProtectedRoute.jsx`)

```jsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="flex items-center justify-center h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  return user ? children : <Navigate to="/login" />;
}
```

#### C. Login Page (`src/pages/LoginPage.jsx`)

```jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Village Partner Login</h2>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
}
```

### Phase 2: Dashboard Layout (Priority: HIGH)

#### A. Dashboard Layout (`src/components/dashboard/DashboardLayout.jsx`)

```jsx
import { Outlet } from 'react-router-dom';
import { DashboardSidebar } from './DashboardSidebar';
import { DashboardHeader } from './DashboardHeader';

export function DashboardLayout() {
  return (
    <div className="flex h-screen bg-gray-100">
      <DashboardSidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <DashboardHeader />

        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
```

#### B. Dashboard Sidebar (`src/components/dashboard/DashboardSidebar.jsx`)

```jsx
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
  { name: 'POIs', href: '/dashboard/pois', icon: MapPinIcon },
  { name: 'QR Codes', href: '/dashboard/qr-codes', icon: QrCodeIcon },
  { name: 'Analytics', href: '/dashboard/analytics', icon: ChartBarIcon },
  { name: 'Identity', href: '/dashboard/identity', icon: LightBulbIcon },
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
```

#### C. Dashboard Header (`src/components/dashboard/DashboardHeader.jsx`)

```jsx
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
```

### Phase 3: Dashboard Pages (Priority: HIGH)

#### A. Dashboard Home (`src/pages/DashboardHome.jsx`)

```jsx
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
```

#### B. POI Manager Page (`src/pages/POIManager.jsx`)

```jsx
import { useState, useEffect } from 'react';
import { poiAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export function POIManager() {
  const { user } = useAuth();
  const [pois, setPois] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadPOIs();
  }, []);

  const loadPOIs = async () => {
    try {
      const data = await poiAPI.list(user.village_slug);
      setPois(data);
    } catch (error) {
      console.error('Failed to load POIs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (poiId) => {
    if (!confirm('Delete this POI?')) return;

    try {
      await poiAPI.delete(user.village_slug, poiId);
      loadPOIs(); // Refresh list
    } catch (error) {
      alert('Failed to delete POI');
    }
  };

  if (loading) return <div>Loading POIs...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Points of Interest</h1>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Add POI
        </button>
      </div>

      {/* POI Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {pois.map((poi) => (
              <tr key={poi.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{poi.name}</div>
                  <div className="text-sm text-gray-500">{poi.address}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {poi.poi_type_id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    poi.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {poi.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button className="text-blue-600 hover:text-blue-900">Edit</button>
                  <button
                    onClick={() => handleDelete(poi.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pois.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg">
          <p className="text-gray-500">No POIs yet. Add your first one!</p>
        </div>
      )}
    </div>
  );
}
```

#### C. QR Code Manager (`src/pages/QRCodeManager.jsx`)

```jsx
import { useState, useEffect } from 'react';
import { qrCodeAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export function QRCodeManager() {
  const { user } = useAuth();
  const [qrCodes, setQRCodes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQRCodes();
  }, []);

  const loadQRCodes = async () => {
    try {
      const data = await qrCodeAPI.list(user.village_slug);
      setQRCodes(data);
    } catch (error) {
      console.error('Failed to load QR codes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (qrCode, size) => {
    const url = qrCodeAPI.downloadQR(user.village_slug, qrCode.code, size);
    window.open(url, '_blank');
  };

  if (loading) return <div>Loading QR codes...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">QR Codes</h1>
        <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
          Generate QR Code
        </button>
      </div>

      {/* QR Code Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {qrCodes.map((qr) => (
          <div key={qr.id} className="bg-white rounded-lg shadow p-6">
            {/* QR Image Preview */}
            {qr.qr_image_url && (
              <img
                src={qr.qr_image_url}
                alt={qr.name}
                className="w-full h-48 object-contain mb-4"
              />
            )}

            <h3 className="font-semibold text-lg mb-2">{qr.name}</h3>
            <p className="text-sm text-gray-600 mb-4">{qr.description}</p>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Scans:</span>
                <span className="font-semibold">{qr.scan_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Last scanned:</span>
                <span className="text-gray-700">
                  {qr.last_scanned_at
                    ? new Date(qr.last_scanned_at).toLocaleDateString()
                    : 'Never'}
                </span>
              </div>
            </div>

            {/* Download Buttons */}
            <div className="mt-4 pt-4 border-t space-y-2">
              <p className="text-xs text-gray-500 mb-2">Download:</p>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleDownload(qr, 'small')}
                  className="flex-1 px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
                >
                  Small
                </button>
                <button
                  onClick={() => handleDownload(qr, 'medium')}
                  className="flex-1 px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
                >
                  Medium
                </button>
                <button
                  onClick={() => handleDownload(qr, 'large')}
                  className="flex-1 px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
                >
                  Large
                </button>
              </div>
            </div>

            {/* View Stats Button */}
            <button className="w-full mt-4 px-4 py-2 text-sm text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50">
              View Statistics
            </button>
          </div>
        ))}
      </div>

      {qrCodes.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg">
          <p className="text-gray-500">No QR codes yet. Generate your first one!</p>
        </div>
      )}
    </div>
  );
}
```

### Phase 4: Routing Setup (Priority: HIGH)

#### App Router (`src/App.jsx`)

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { DashboardLayout } from './components/dashboard/DashboardLayout';
import { DashboardHome } from './pages/DashboardHome';
import { POIManager } from './pages/POIManager';
import { QRCodeManager } from './pages/QRCodeManager';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Dashboard Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardHome />} />
            <Route path="pois" element={<POIManager />} />
            <Route path="qr-codes" element={<QRCodeManager />} />
            <Route path="analytics" element={<AnalyticsDashboard />} />
            <Route path="identity" element={<IdentityThemes />} />
            <Route path="settings" element={<VillageSettings />} />
          </Route>

          {/* Redirect root to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

### Phase 5: Custom Hooks (Priority: MEDIUM)

#### useVillage Hook (`src/hooks/useVillage.js`)

```jsx
import { useState, useEffect } from 'react';
import { villageAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export function useVillage() {
  const { user } = useAuth();
  const [village, setVillage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user?.village_slug) {
      loadVillage();
    }
  }, [user]);

  const loadVillage = async () => {
    try {
      const data = await villageAPI.getBySlug(user.village_slug);
      setVillage(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const updateVillage = async (updates) => {
    try {
      const updated = await villageAPI.update(user.village_slug, updates);
      setVillage(updated);
      return updated;
    } catch (err) {
      throw err;
    }
  };

  return { village, loading, error, updateVillage, refresh: loadVillage };
}
```

## 🎨 Styling with Tailwind CSS

### Install Tailwind (if not already installed)

```bash
cd frontend
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Configure Tailwind (`tailwind.config.js`)

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2563eb',
        secondary: '#0f766e',
      },
    },
  },
  plugins: [],
}
```

### Add Tailwind to CSS (`src/index.css`)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## 📦 Required Dependencies

```bash
cd frontend
npm install react-router-dom axios @heroicons/react
```

## 🔒 Security Considerations

1. **Token Storage**: Tokens stored in localStorage (consider httpOnly cookies for production)
2. **XSS Protection**: React escapes output by default
3. **CSRF**: Backend handles CSRF tokens
4. **Rate Limiting**: Handled by backend
5. **Input Validation**: Validate on both frontend and backend

## 📱 Responsive Design Tips

- Use Tailwind's responsive prefixes: `md:`, `lg:`, `xl:`
- Mobile-first approach
- Test on various screen sizes
- Consider mobile navigation menu

## 🚀 Running the Dashboard

```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:5173

## ✅ Testing Checklist

- [ ] Login redirects to dashboard
- [ ] Protected routes require authentication
- [ ] Logout clears session
- [ ] Dashboard loads village stats
- [ ] POI list displays correctly
- [ ] Can add new POI
- [ ] Can delete POI
- [ ] QR code list displays with images
- [ ] Can download QR codes
- [ ] Scan statistics display
- [ ] Responsive on mobile devices

## 📊 Features Summary

### Implemented ✅
- API service layer with all endpoints
- Authentication flow
- Directory structure

### To Implement 🔨
- All React components (code provided above)
- Analytics charts (use Chart.js or Recharts)
- Map picker for POI location
- Image upload component
- Form validation
- Loading states
- Error handling
- Toast notifications

## 🎯 Next Steps

1. Copy all component code from this guide
2. Install dependencies
3. Test authentication flow
4. Add remaining pages (Analytics, Identity, Settings)
5. Add charts library for analytics
6. Implement image upload
7. Add form validation
8. Test on mobile devices

## 📝 Notes

- All API endpoints are ready in backend (Weeks 1-10)
- Frontend connects to `http://localhost:8000` by default
- Vite dev server runs on `http://localhost:5173`
- Update `.env` for production API URL
- Consider adding React Query for better data fetching
