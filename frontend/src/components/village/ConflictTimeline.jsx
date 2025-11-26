import { useState, useEffect } from 'react';
import axios from 'axios';

const PERIOD_COLORS = {
  'Ancient': 'bg-purple-500',
  'Roman': 'bg-red-500',
  'Medieval': 'bg-blue-500',
  'Early Modern': 'bg-green-500',
  'Modern': 'bg-yellow-500',
  'World War I': 'bg-orange-500',
  'World War II': 'bg-red-700',
  'Contemporary': 'bg-gray-500'
};

const PERIOD_RANGES = {
  'Ancient': { start: -500, end: 0 },
  'Roman': { start: 0, end: 500 },
  'Medieval': { start: 500, end: 1500 },
  'Early Modern': { start: 1500, end: 1800 },
  'Modern': { start: 1800, end: 1914 },
  'World War I': { start: 1914, end: 1918 },
  'World War II': { start: 1939, end: 1945 },
  'Contemporary': { start: 1945, end: 2024 }
};

function getPeriodFromYear(year) {
  for (const [period, range] of Object.entries(PERIOD_RANGES)) {
    if (year >= range.start && year <= range.end) {
      return period;
    }
  }
  return 'Contemporary';
}

export function ConflictTimeline({ villageSlug }) {
  const [conflicts, setConflicts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(null);
  const [expandedConflict, setExpandedConflict] = useState(null);

  useEffect(() => {
    loadConflicts();
  }, [villageSlug]);

  const loadConflicts = async () => {
    try {
      const response = await axios.get(`/api/villages/${villageSlug}/conflicts`);
      setConflicts(response.data);
    } catch (error) {
      console.error('Failed to load conflicts:', error);
    } finally {
      setLoading(false);
    }
  };

  const groupedConflicts = conflicts.reduce((acc, conflict) => {
    const period = getPeriodFromYear(conflict.start_year);
    if (!acc[period]) acc[period] = [];
    acc[period].push(conflict);
    return acc;
  }, {});

  const filteredPeriods = selectedPeriod
    ? { [selectedPeriod]: groupedConflicts[selectedPeriod] || [] }
    : groupedConflicts;

  if (loading) {
    return <div className="text-center py-8">Loading timeline...</div>;
  }

  return (
    <div className="space-y-8">
      {/* Period Filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedPeriod(null)}
          className={`px-4 py-2 rounded-md transition ${
            !selectedPeriod
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          All Periods
        </button>
        {Object.keys(PERIOD_RANGES).map((period) => (
          <button
            key={period}
            onClick={() => setSelectedPeriod(period)}
            className={`px-4 py-2 rounded-md transition ${
              selectedPeriod === period
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {period} ({groupedConflicts[period]?.length || 0})
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-8 top-0 bottom-0 w-1 bg-gray-300"></div>

        {/* Timeline items */}
        <div className="space-y-8">
          {Object.entries(filteredPeriods).map(([period, periodConflicts]) => (
            <div key={period} className="relative">
              {/* Period marker */}
              <div className="flex items-center mb-4">
                <div className={`w-16 h-16 rounded-full ${PERIOD_COLORS[period]} flex items-center justify-center text-white font-bold shadow-lg`}>
                  {periodConflicts.length}
                </div>
                <div className="ml-4">
                  <h3 className="text-2xl font-bold text-gray-800">{period}</h3>
                  <p className="text-gray-600">
                    {PERIOD_RANGES[period].start > 0 ? PERIOD_RANGES[period].start : `${Math.abs(PERIOD_RANGES[period].start)} BC`}
                    {' - '}
                    {PERIOD_RANGES[period].end > 0 ? PERIOD_RANGES[period].end : `${Math.abs(PERIOD_RANGES[period].end)} BC`}
                  </p>
                </div>
              </div>

              {/* Conflicts in this period */}
              <div className="ml-24 space-y-4">
                {periodConflicts.map((conflict) => (
                  <div
                    key={conflict.id}
                    className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer"
                    onClick={() => setExpandedConflict(
                      expandedConflict === conflict.id ? null : conflict.id
                    )}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="text-xl font-semibold text-gray-800 mb-2">
                          {conflict.name}
                        </h4>
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                          <span className="font-medium">
                            {conflict.start_year}
                            {conflict.end_year && conflict.end_year !== conflict.start_year
                              ? ` - ${conflict.end_year}`
                              : ''}
                          </span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${PERIOD_COLORS[period]} text-white`}>
                            {period}
                          </span>
                        </div>
                        <p className="text-gray-700 line-clamp-2">
                          {conflict.description}
                        </p>
                      </div>
                      <button className="ml-4 text-blue-600 hover:text-blue-800">
                        {expandedConflict === conflict.id ? '▼' : '▶'}
                      </button>
                    </div>

                    {/* Expanded Details */}
                    {expandedConflict === conflict.id && (
                      <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
                        <div>
                          <h5 className="font-semibold text-gray-700 mb-1">Full Description</h5>
                          <p className="text-gray-600">{conflict.description}</p>
                        </div>
                        {conflict.location_description && (
                          <div>
                            <h5 className="font-semibold text-gray-700 mb-1">Location</h5>
                            <p className="text-gray-600">{conflict.location_description}</p>
                          </div>
                        )}
                        {conflict.historical_importance && (
                          <div>
                            <h5 className="font-semibold text-gray-700 mb-1">Historical Importance</h5>
                            <p className="text-gray-600">{conflict.historical_importance}</p>
                          </div>
                        )}
                        {conflict.latitude && conflict.longitude && (
                          <div>
                            <a
                              href={`#map`}
                              className="inline-block mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
                            >
                              View on Map
                            </a>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {conflicts.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg">
          <p className="text-gray-500">No conflicts found for this village.</p>
        </div>
      )}
    </div>
  );
}
