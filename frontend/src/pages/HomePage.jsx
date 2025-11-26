import { Link } from 'react-router-dom';
import { MapIcon, SparklesIcon, ChartBarIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

export function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-purple-900 text-white">
        <div className="container mx-auto px-6 py-24">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Discover Your Village's
              <span className="block text-yellow-400">Hidden History</span>
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 mb-12 leading-relaxed">
              Transform centuries of historical conflicts into engaging tourism experiences
              with AI-powered insights and interactive maps.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/villages/chirac"
                className="px-8 py-4 bg-yellow-400 text-blue-900 font-bold rounded-lg hover:bg-yellow-300 transition text-lg shadow-xl"
              >
                Explore Chirac Demo
              </Link>
              <a
                href="#demo"
                className="px-8 py-4 bg-white/10 backdrop-blur text-white font-semibold rounded-lg hover:bg-white/20 transition text-lg border-2 border-white/30"
              >
                Request Demo
              </a>
            </div>
          </div>
        </div>

        {/* Decorative wave */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" className="w-full h-auto">
            <path
              fill="#ffffff"
              d="M0,64L80,69.3C160,75,320,85,480,80C640,75,800,53,960,48C1120,43,1280,53,1360,58.7L1440,64L1440,120L1360,120C1280,120,1120,120,960,120C800,120,640,120,480,120C320,120,160,120,80,120L0,120Z"
            ></path>
          </svg>
        </div>
      </section>

      {/* Value Proposition - 3 Key Benefits */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">
              Why SPV Treasure Map?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Three powerful features that transform historical data into tourism revenue
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            {/* Benefit 1 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 rounded-full mb-6">
                <SparklesIcon className="h-10 w-10 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-800 mb-4">
                AI-Powered Identity Analysis
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Our AI analyzes your village's 123 historical conflicts to reveal unique
                cultural themes and heritage patterns. Automatically generates engaging
                stories and tourism project ideas.
              </p>
            </div>

            {/* Benefit 2 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
                <MapIcon className="h-10 w-10 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-800 mb-4">
                Interactive Geospatial Maps
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Beautiful, interactive maps showing conflicts and points of interest.
                Create walking routes with QR codes. Visitors explore history at their
                own pace.
              </p>
            </div>

            {/* Benefit 3 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-purple-100 rounded-full mb-6">
                <ChartBarIcon className="h-10 w-10 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-800 mb-4">
                Tourism Analytics & Monetization
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Track QR code scans, visitor engagement, and popular routes. Generate
                branded QR codes for signage. Turn history into measurable tourism revenue.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Chirac Case Study */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <span className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
                FEATURED CASE STUDY
              </span>
              <h2 className="text-4xl font-bold text-gray-800 mt-6 mb-4">
                Chirac: A Village Transformed
              </h2>
              <p className="text-xl text-gray-600">
                2,500 years of history brought to life in one beautiful platform
              </p>
            </div>

            <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
              <div className="grid md:grid-cols-2">
                <div className="p-12 space-y-6">
                  <h3 className="text-2xl font-bold text-gray-800">The Challenge</h3>
                  <p className="text-gray-600 leading-relaxed">
                    Chirac had 123 documented historical conflicts spanning from 500 BC
                    to present day, but no way to showcase this rich heritage to visitors
                    or generate tourism revenue.
                  </p>

                  <h3 className="text-2xl font-bold text-gray-800 mt-8">The Solution</h3>
                  <div className="space-y-3">
                    <div className="flex items-start">
                      <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-1" />
                      <span className="text-gray-700">
                        <strong>123 conflicts</strong> mapped and categorized
                      </span>
                    </div>
                    <div className="flex items-start">
                      <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-1" />
                      <span className="text-gray-700">
                        <strong>19 POIs</strong> with photos and descriptions
                      </span>
                    </div>
                    <div className="flex items-start">
                      <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-1" />
                      <span className="text-gray-700">
                        <strong>3 AI-generated identity themes</strong> revealing unique heritage
                      </span>
                    </div>
                    <div className="flex items-start">
                      <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-1" />
                      <span className="text-gray-700">
                        <strong>QR-enabled walking routes</strong> for self-guided tours
                      </span>
                    </div>
                  </div>

                  <Link
                    to="/villages/chirac"
                    className="inline-block mt-8 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
                  >
                    View Chirac Demo →
                  </Link>
                </div>

                <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-12 flex items-center justify-center">
                  <div className="text-white text-center">
                    <div className="text-6xl font-bold mb-4">123</div>
                    <div className="text-xl mb-8">Historical Conflicts</div>
                    <div className="text-6xl font-bold mb-4">19</div>
                    <div className="text-xl mb-8">Points of Interest</div>
                    <div className="text-6xl font-bold mb-4">2500+</div>
                    <div className="text-xl">Years of History</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      <section id="demo" className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600 mb-12">
              One price. Everything included.
            </p>

            <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-12 border-2 border-blue-200">
              <div className="text-6xl font-bold text-blue-900 mb-4">€500</div>
              <div className="text-2xl text-gray-700 mb-8">per year</div>

              <ul className="text-left max-w-md mx-auto space-y-4 mb-12">
                <li className="flex items-start">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-gray-700">Unlimited historical conflicts mapping</span>
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-gray-700">Up to 100 points of interest</span>
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-gray-700">AI-powered identity theme generation</span>
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-gray-700">Unlimited QR codes with analytics</span>
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-gray-700">Custom village branding</span>
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-1" />
                  <span className="text-gray-700">Tourism route creation tools</span>
                </li>
              </ul>

              <a
                href="mailto:contact@spvtreasurehunt.com?subject=Demo Request"
                className="inline-block px-8 py-4 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition text-lg shadow-xl"
              >
                Request a Demo
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="text-white font-bold text-xl mb-4">SPV Treasure Map</h3>
              <p className="text-gray-400">
                Bringing village history to life through AI and geospatial technology.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2">
                <li><Link to="/villages/chirac" className="hover:text-white transition">Chirac Demo</Link></li>
                <li><Link to="/login" className="hover:text-white transition">Partner Login</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Contact</h4>
              <p className="text-gray-400">
                Email: contact@spvtreasurehunt.com
              </p>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400 text-sm">
            <p>© 2024 SPV Treasure Map. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
