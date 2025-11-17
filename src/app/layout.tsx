/**
 * Root Layout
 *
 * Main layout component that wraps all pages.
 * Sets up metadata, fonts, and global styles.
 */

import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Abstract Art Starter - Begin Your Modern Abstract Art Journey',
  description:
    'Personalized guidance for beginners starting with modern abstract painting. Get your custom materials list, studio setup tips, and 4-week learning plan.',
  keywords: 'abstract art, acrylic pouring, palette knife painting, mixed media, art for beginners',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {/* Simple header */}
        <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <a href="/" className="flex items-center gap-3 group">
                <div className="text-3xl">🎨</div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                    Abstract Art Starter
                  </h1>
                  <p className="text-xs text-gray-600">Your creative journey begins here</p>
                </div>
              </a>

              <nav className="hidden md:flex items-center gap-6">
                <a
                  href="/"
                  className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
                >
                  Home
                </a>
                <a
                  href="/quiz"
                  className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
                >
                  Start Quiz
                </a>
                <a
                  href="/plan"
                  className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
                >
                  My Plan
                </a>
                <a
                  href="/feedback"
                  className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
                >
                  Get Feedback
                </a>
              </nav>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="min-h-screen">{children}</main>

        {/* Simple footer */}
        <footer className="bg-white border-t border-gray-200 mt-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <p className="text-center text-sm text-gray-600">
              © 2024 Abstract Art Starter. Start creating beautiful abstract art today.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
