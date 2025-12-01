/**
 * MainLayout Component
 *
 * Top navigation bar for public pages.
 * Logo | Explorer la carte | À propos | Espace communes
 */
import { Link, useLocation } from 'react-router-dom';
import './MainLayout.css';

export function MainLayout({ children }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div className="spv-layout">
      <header className="spv-header">
        <nav className="spv-nav">
          {/* Logo */}
          <Link to="/" className="spv-nav__logo">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="spv-nav__logo-icon"
            >
              <path d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l5.447 2.724A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <span className="spv-nav__logo-text">SPV Treasure Map</span>
          </Link>

          {/* Navigation Links */}
          <div className="spv-nav__links">
            <Link
              to="/explore"
              className={`spv-nav__link ${isActive('/explore') ? 'spv-nav__link--active' : ''}`}
            >
              <svg viewBox="0 0 20 20" fill="currentColor" className="spv-nav__link-icon">
                <path fillRule="evenodd" d="M12 1.586l-4 4v12.828l4-4V1.586zM3.707 3.293A1 1 0 002 4v10a1 1 0 00.293.707L6 18.414V5.586L3.707 3.293zM17.707 5.293L14 1.586v12.828l2.293 2.293A1 1 0 0018 16V6a1 1 0 00-.293-.707z" clipRule="evenodd" />
              </svg>
              Explorer la carte
            </Link>
            <Link
              to="/a-propos"
              className={`spv-nav__link ${isActive('/a-propos') ? 'spv-nav__link--active' : ''}`}
            >
              À propos
            </Link>
            <Link
              to="/login"
              className="spv-nav__link spv-nav__link--cta"
            >
              Espace communes
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button className="spv-nav__mobile-toggle" aria-label="Menu">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </nav>
      </header>

      <main className="spv-main">
        {children}
      </main>
    </div>
  );
}
