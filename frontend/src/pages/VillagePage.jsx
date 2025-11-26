import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { villageAPI, poiAPI, identityAPI } from '../services/api';
import { ConflictTimeline } from '../components/village/ConflictTimeline';
import { IdentityThemes } from '../components/village/IdentityThemes';
import { VillageMap } from '../components/village/VillageMap';
import { POIGallery } from '../components/village/POIGallery';

export function VillagePage() {
  const { slug } = useParams();
  const [village, setVillage] = useState(null);
  const [pois, setPois] = useState([]);
  const [themes, setThemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadVillageData();
  }, [slug]);

  const loadVillageData = async () => {
    try {
      setLoading(true);
      const [villageData, poisData, themesData] = await Promise.all([
        villageAPI.getBySlug(slug),
        poiAPI.list(slug),
        identityAPI.listThemes(slug)
      ]);

      setVillage(villageData);
      setPois(poisData);
      setThemes(themesData);
    } catch (err) {
      console.error('Failed to load village data:', err);
      setError('Failed to load village information');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">Oops!</h1>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!village) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">Village Not Found</h1>
          <p className="text-gray-600">The village you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-blue-900 to-blue-700 text-white">
        <div className="container mx-auto px-6 py-20">
          <div className="max-w-4xl">
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              {village.name}
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 mb-8">
              {village.tagline || 'Discover the hidden history of our village'}
            </p>

            {/* Key Stats Banner */}
            <div className="grid grid-cols-3 gap-6 mt-12">
              <div className="text-center">
                <div className="text-4xl font-bold">{village.conflict_count || 123}</div>
                <div className="text-blue-200 mt-2">Historical Conflicts</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold">{pois.length}</div>
                <div className="text-blue-200 mt-2">Points of Interest</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold">2500+</div>
                <div className="text-blue-200 mt-2">Years of History</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Navigation */}
      <section className="bg-white border-b">
        <div className="container mx-auto px-6">
          <nav className="flex space-x-8 py-4">
            <a href="#map" className="text-gray-700 hover:text-blue-600 transition">Map</a>
            <a href="#timeline" className="text-gray-700 hover:text-blue-600 transition">Timeline</a>
            <a href="#identity" className="text-gray-700 hover:text-blue-600 transition">Identity</a>
            <a href="#pois" className="text-gray-700 hover:text-blue-600 transition">Places</a>
            <Link to={`/villages/${slug}/routes`} className="text-gray-700 hover:text-blue-600 transition">
              Tourism Routes
            </Link>
          </nav>
        </div>
      </section>

      {/* Interactive Map Section */}
      <section id="map" className="py-16 bg-white">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-800 mb-8">Explore {village.name}</h2>
          <div className="h-[600px] rounded-lg overflow-hidden shadow-lg">
            <VillageMap
              villageSlug={slug}
              pois={pois}
              center={village.location}
              showConflicts={true}
              showPOIs={true}
            />
          </div>
          <div className="mt-4 flex space-x-4">
            <Link
              to={`/villages/${slug}/conflicts`}
              className="px-6 py-3 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
            >
              View All Conflicts
            </Link>
            <Link
              to={`/villages/${slug}/pois`}
              className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition"
            >
              View All Places
            </Link>
          </div>
        </div>
      </section>

      {/* Identity Themes Section */}
      {themes.length > 0 && (
        <section id="identity" className="py-16 bg-gray-50">
          <div className="container mx-auto px-6">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-800 mb-4">
                Village Identity & Heritage
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                AI-powered analysis of {village.name}'s historical conflicts reveals unique
                cultural themes and heritage patterns.
              </p>
            </div>
            <IdentityThemes themes={themes} villageSlug={slug} />
          </div>
        </section>
      )}

      {/* Conflict Timeline Section */}
      <section id="timeline" className="py-16 bg-white">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-800 mb-8">Historical Timeline</h2>
          <p className="text-gray-600 mb-8">
            From ancient times to the present day, explore the conflicts that shaped {village.name}.
          </p>
          <ConflictTimeline villageSlug={slug} />
        </div>
      </section>

      {/* POI Gallery Section */}
      {pois.length > 0 && (
        <section id="pois" className="py-16 bg-gray-50">
          <div className="container mx-auto px-6">
            <h2 className="text-3xl font-bold text-gray-800 mb-8">
              Discover Local Treasures
            </h2>
            <POIGallery pois={pois} villageSlug={slug} />
          </div>
        </section>
      )}

      {/* Tourism Routes Section */}
      <section className="py-16 bg-blue-900 text-white">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-4">Tourism & Walking Routes</h2>
          <p className="text-blue-100 text-lg mb-8 max-w-2xl mx-auto">
            Discover {village.name} through guided walking routes with QR codes at each stop.
            Learn the history as you explore.
          </p>
          <Link
            to={`/villages/${slug}/routes`}
            className="inline-block px-8 py-4 bg-white text-blue-900 font-semibold rounded-md hover:bg-blue-50 transition"
          >
            Explore Routes
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 py-8">
        <div className="container mx-auto px-6 text-center">
          <p className="mb-2">
            Powered by{' '}
            <Link to="/" className="text-blue-400 hover:text-blue-300">
              SPV Treasure Map
            </Link>
          </p>
          <p className="text-sm text-gray-400">
            Bringing history to life through AI and geospatial technology
          </p>
        </div>
      </footer>
    </div>
  );
}
