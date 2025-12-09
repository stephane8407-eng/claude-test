/**
 * HomePage - Landing Page
 *
 * Simple marketing homepage with hero, CTA, and communes section.
 * URL: /
 * Clean, white background, teal accents - NO map on this page.
 */
import { Link } from 'react-router-dom';
import { MainLayout } from '../components/layout/index';
import { Button } from '../components/ui';
import './HomePage.css';

export function HomePage() {
  return (
    <MainLayout>
      <div className="spv-landing">
        {/* Hero Section */}
        <section className="spv-landing__hero">
          <div className="spv-landing__hero-content">
            <h1 className="spv-landing__title">
              Découvrez le patrimoine caché des villages français
            </h1>
            <p className="spv-landing__subtitle">
              Explorez l'histoire, les légendes et les trésors oubliés de nos communes rurales.
              Une carte interactive pour redécouvrir la France authentique.
            </p>
            <div className="spv-landing__cta">
              <Link to="/explore">
                <Button variant="primary" size="lg">
                  <svg viewBox="0 0 20 20" fill="currentColor" className="spv-landing__cta-icon">
                    <path fillRule="evenodd" d="M12 1.586l-4 4v12.828l4-4V1.586zM3.707 3.293A1 1 0 002 4v10a1 1 0 00.293.707L6 18.414V5.586L3.707 3.293zM17.707 5.293L14 1.586v12.828l2.293 2.293A1 1 0 0018 16V6a1 1 0 00-.293-.707z" clipRule="evenodd" />
                  </svg>
                  Explorer la carte
                </Button>
              </Link>
            </div>
          </div>

          {/* Decorative map illustration */}
          <div className="spv-landing__hero-visual">
            <div className="spv-landing__map-preview">
              <svg viewBox="0 0 400 300" fill="none" className="spv-landing__map-svg">
                {/* Stylized France outline */}
                <path
                  d="M200 20 L280 60 L320 120 L340 200 L300 260 L220 280 L140 260 L80 200 L60 140 L100 80 L160 40 Z"
                  fill="var(--color-primary-light)"
                  stroke="var(--color-primary)"
                  strokeWidth="2"
                />
                {/* Village markers */}
                <circle cx="180" cy="140" r="8" fill="var(--color-primary)" />
                <circle cx="220" cy="180" r="8" fill="var(--color-primary)" />
                <circle cx="160" cy="200" r="8" fill="var(--color-primary)" />
                <circle cx="240" cy="120" r="6" fill="var(--color-secondary)" />
                <circle cx="140" cy="160" r="6" fill="var(--color-secondary)" />
              </svg>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="spv-landing__features">
          <div className="spv-landing__features-grid">
            <div className="spv-landing__feature">
              <div className="spv-landing__feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
              </div>
              <h3 className="spv-landing__feature-title">Villages historiques</h3>
              <p className="spv-landing__feature-text">
                Découvrez des siècles d'histoire locale, des batailles oubliées aux légendes méconnues.
              </p>
            </div>

            <div className="spv-landing__feature">
              <div className="spv-landing__feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                  <polyline points="9 22 9 12 15 12 15 22" />
                </svg>
              </div>
              <h3 className="spv-landing__feature-title">Patrimoine local</h3>
              <p className="spv-landing__feature-text">
                Châteaux, chapelles, moulins et forges : explorez les trésors architecturaux.
              </p>
            </div>

            <div className="spv-landing__feature">
              <div className="spv-landing__feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
              </div>
              <h3 className="spv-landing__feature-title">Parcours thématiques</h3>
              <p className="spv-landing__feature-text">
                Suivez des itinéraires de découverte adaptés à tous les publics.
              </p>
            </div>
          </div>
        </section>

        {/* Communes Section */}
        <section className="spv-landing__communes">
          <div className="spv-landing__communes-content">
            <div className="spv-landing__communes-text">
              <span className="spv-landing__communes-badge">Espace communes</span>
              <h2 className="spv-landing__communes-title">
                Vous êtes une commune ?
              </h2>
              <p className="spv-landing__communes-description">
                Valorisez l'identité et le patrimoine de votre village.
                Créez des parcours touristiques, gérez vos points d'intérêt
                et attirez de nouveaux visiteurs grâce à notre plateforme.
              </p>
              <Link to="/login">
                <Button variant="outline" size="lg">
                  Accéder à l'espace communes
                </Button>
              </Link>
            </div>
            <div className="spv-landing__communes-visual">
              <div className="spv-landing__communes-card">
                <div className="spv-landing__communes-card-header">
                  <span className="spv-landing__communes-card-icon">🏛️</span>
                  <span>Tableau de bord</span>
                </div>
                <div className="spv-landing__communes-card-stats">
                  <div className="spv-landing__stat">
                    <span className="spv-landing__stat-value">123</span>
                    <span className="spv-landing__stat-label">événements</span>
                  </div>
                  <div className="spv-landing__stat">
                    <span className="spv-landing__stat-value">19</span>
                    <span className="spv-landing__stat-label">lieux</span>
                  </div>
                  <div className="spv-landing__stat">
                    <span className="spv-landing__stat-value">5</span>
                    <span className="spv-landing__stat-label">parcours</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="spv-landing__footer">
          <div className="spv-landing__footer-content">
            <p className="spv-landing__footer-text">
              SPV Treasure Map — Révéler l'identité des villages français
            </p>
            <div className="spv-landing__footer-links">
              <Link to="/a-propos" className="spv-landing__footer-link">À propos</Link>
              <Link to="/login" className="spv-landing__footer-link">Connexion</Link>
            </div>
          </div>
        </footer>
      </div>
    </MainLayout>
  );
}
