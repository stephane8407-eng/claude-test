import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { HomePage } from './pages/HomePage';
import { ExplorePage } from './pages/ExplorePage';
import { VillagePage } from './pages/VillagePage';
import { DashboardLayout } from './components/dashboard/DashboardLayout';
import { DashboardHome } from './pages/DashboardHome';
import { POIManager } from './pages/POIManager';
import { QRCodeManager } from './pages/QRCodeManager';
import { DesignSystemPage } from './pages/DesignSystemPage';
import { IdentityAuditWizard, CaseStudiesPage, FundingProgramsPage, ProjectKanbanPage } from './pages/admin';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/explore" element={<ExplorePage />} />
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
            <Route path="identity-audit" element={<IdentityAuditWizard />} />
            <Route path="pois" element={<POIManager />} />
            <Route path="qr-codes" element={<QRCodeManager />} />
            {/* Phase D: Platform Admin Pages */}
            <Route path="case-studies" element={<CaseStudiesPage />} />
            <Route path="funding-programs" element={<FundingProgramsPage />} />
            {/* Phase E: Project Management Dashboard */}
            <Route path="projects" element={<ProjectKanbanPage />} />
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
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-background)' }}>
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-4" style={{ color: 'var(--color-text)' }}>404</h1>
        <p className="text-xl mb-8" style={{ color: 'var(--color-text-muted)' }}>Page non trouvée</p>
        <a
          href="/"
          className="px-6 py-3 rounded-lg transition"
          style={{ backgroundColor: 'var(--color-primary)', color: 'white' }}
        >
          Retour à l'accueil
        </a>
      </div>
    </div>
  );
}

export default App;
