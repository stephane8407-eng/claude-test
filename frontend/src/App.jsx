import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { HomePage } from './pages/HomePage';
import { VillagePage } from './pages/VillagePage';
import { DashboardLayout } from './components/dashboard/DashboardLayout';
import { DashboardHome } from './pages/DashboardHome';
import { POIManager } from './pages/POIManager';
import { QRCodeManager } from './pages/QRCodeManager';
import { DesignSystemPage } from './pages/DesignSystemPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />

          {/* Public Village Routes */}
          <Route path="/villages/:slug" element={<VillagePage />} />

          {/* Design System Preview */}
          <Route path="/design-system" element={<DesignSystemPage />} />

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
          </Route>

          {/* 404 - Not Found */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

// 404 Page Component
function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-800 mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-8">Page not found</p>
        <a href="/" className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition">
          Go Home
        </a>
      </div>
    </div>
  );
}

export default App;
