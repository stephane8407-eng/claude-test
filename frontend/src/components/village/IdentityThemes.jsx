import { Link } from 'react-router-dom';
import { LightBulbIcon, SparklesIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

export function IdentityThemes({ themes, villageSlug }) {
  if (!themes || themes.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg">
        <p className="text-gray-500">No identity themes generated yet.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {themes.map((theme, index) => (
        <ThemeCard key={theme.id || index} theme={theme} villageSlug={villageSlug} />
      ))}
    </div>
  );
}

function ThemeCard({ theme, villageSlug }) {
  const confidenceColor = theme.confidence_score >= 0.8
    ? 'text-green-600 bg-green-100'
    : theme.confidence_score >= 0.6
    ? 'text-yellow-600 bg-yellow-100'
    : 'text-orange-600 bg-orange-100';

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition">
      {/* Theme Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
        <div className="flex items-start justify-between mb-4">
          <SparklesIcon className="h-8 w-8" />
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${confidenceColor}`}>
            {Math.round(theme.confidence_score * 100)}% confidence
          </span>
        </div>
        <h3 className="text-2xl font-bold mb-2">{theme.theme_name}</h3>
        <p className="text-blue-100 text-sm">Identity Theme #{theme.id}</p>
      </div>

      {/* Theme Content */}
      <div className="p-6 space-y-4">
        {/* Story */}
        <div>
          <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
            <LightBulbIcon className="h-5 w-5 mr-2 text-yellow-500" />
            Theme Story
          </h4>
          <p className="text-gray-700 text-sm leading-relaxed">
            {theme.theme_story}
          </p>
        </div>

        {/* Evidence Section */}
        {theme.evidence && (
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Historical Evidence</h4>
            <div className="bg-gray-50 rounded p-3 space-y-2 text-sm">
              {theme.evidence.conflicts && theme.evidence.conflicts.length > 0 && (
                <div>
                  <span className="font-medium text-gray-700">Conflicts:</span>
                  <ul className="list-disc list-inside text-gray-600 ml-2">
                    {theme.evidence.conflicts.slice(0, 3).map((conflict, i) => (
                      <li key={i} className="truncate">{conflict}</li>
                    ))}
                    {theme.evidence.conflicts.length > 3 && (
                      <li className="text-blue-600">+{theme.evidence.conflicts.length - 3} more...</li>
                    )}
                  </ul>
                </div>
              )}
              {theme.evidence.pois && theme.evidence.pois.length > 0 && (
                <div>
                  <span className="font-medium text-gray-700">Points of Interest:</span>
                  <ul className="list-disc list-inside text-gray-600 ml-2">
                    {theme.evidence.pois.slice(0, 3).map((poi, i) => (
                      <li key={i} className="truncate">{poi}</li>
                    ))}
                    {theme.evidence.pois.length > 3 && (
                      <li className="text-blue-600">+{theme.evidence.pois.length - 3} more...</li>
                    )}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Project Ideas */}
        {theme.project_ideas && theme.project_ideas.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Tourism Project Ideas</h4>
            <ul className="space-y-2">
              {theme.project_ideas.map((idea, i) => (
                <li key={i} className="flex items-start text-sm">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-gray-700">{idea.title}</span>
                    {idea.estimated_impact && (
                      <span className="ml-2 text-xs text-gray-500">
                        (Impact: {idea.estimated_impact})
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* View Details Link */}
        <Link
          to={`/villages/${villageSlug}/identity/${theme.id}`}
          className="block mt-4 px-4 py-2 text-center bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 transition font-medium"
        >
          View Full Analysis →
        </Link>
      </div>
    </div>
  );
}
