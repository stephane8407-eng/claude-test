// frontend/src/components/dashboard/GrantMatcher.jsx
/**
 * Phase E Week 2: Grant Matching Component
 *
 * Shows matching funding programs for a project and allows generating
 * grant applications via Claude API.
 */

import React, { useState, useEffect, useCallback } from 'react';

// API base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Level labels
const LEVEL_LABELS = {
  'European': { label: 'Europeen', color: 'bg-blue-600' },
  'National': { label: 'National', color: 'bg-red-600' },
  'Regional': { label: 'Regional', color: 'bg-orange-500' },
  'Departmental': { label: 'Departemental', color: 'bg-green-600' },
  'Intercommunal': { label: 'Intercommunal', color: 'bg-purple-600' }
};

// Status labels
const STATUS_LABELS = {
  'draft': { label: 'Brouillon', color: 'bg-gray-200 text-gray-800' },
  'submitted': { label: 'Soumis', color: 'bg-blue-200 text-blue-800' },
  'under_review': { label: 'En cours', color: 'bg-yellow-200 text-yellow-800' },
  'approved': { label: 'Approuve', color: 'bg-green-200 text-green-800' },
  'rejected': { label: 'Refuse', color: 'bg-red-200 text-red-800' },
  'abandoned': { label: 'Abandonne', color: 'bg-gray-300 text-gray-600' }
};

export function GrantMatcher({
  projectId,
  projectTitle,
  villageName,
  villagePopulation,
  villageRegion = 'Nouvelle-Aquitaine',
  villageDepartment = 'Charente',
  maireName = null,
  onClose
}) {
  const [matches, setMatches] = useState([]);
  const [applications, setApplications] = useState([]);
  const [currentApplication, setCurrentApplication] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedProgramId, setSelectedProgramId] = useState(null);
  const [error, setError] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const [activeTab, setActiveTab] = useState('programmes');

  useEffect(() => {
    if (projectId) {
      loadMatches();
      loadApplications();
    }
  }, [projectId]);

  const loadMatches = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/grants/projects/${projectId}/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          village_population: villagePopulation,
          village_region: villageRegion,
          limit: 15,
          min_score: 20
        })
      });

      if (!response.ok) {
        throw new Error('Echec du chargement des programmes');
      }

      const data = await response.json();
      setMatches(data.matches || []);
    } catch (err) {
      console.error('Erreur chargement programmes:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadApplications = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/grants/projects/${projectId}/applications`);
      if (response.ok) {
        const data = await response.json();
        setApplications(data.applications || []);
      }
    } catch (err) {
      console.error('Erreur chargement historique:', err);
    }
  };

  const generateApplication = async (programId) => {
    setGenerating(true);
    setSelectedProgramId(programId);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/grants/projects/${projectId}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          program_id: programId,
          village_name: villageName,
          village_population: villagePopulation,
          village_region: villageRegion,
          village_department: villageDepartment,
          maire_name: maireName
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Echec de la generation');
      }

      const data = await response.json();
      setCurrentApplication({
        id: data.application_id,
        text: data.text,
        program_name: data.program_name,
        status: data.status,
        amount_requested: data.amount_requested
      });

      await loadApplications();
      setActiveTab('programmes');
    } catch (err) {
      console.error('Erreur generation:', err);
      setError(err.message);
    } finally {
      setGenerating(false);
      setSelectedProgramId(null);
    }
  };

  const loadApplication = async (applicationId) => {
    try {
      const response = await fetch(`${API_BASE}/api/grants/applications/${applicationId}`);
      if (response.ok) {
        const data = await response.json();
        setCurrentApplication({
          id: data.id,
          text: data.text,
          program_name: data.program_name,
          status: data.status,
          amount_requested: data.amount_requested
        });
      }
    } catch (err) {
      console.error('Erreur chargement dossier:', err);
    }
  };

  const copyToClipboard = useCallback(async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Erreur copie:', err);
    }
  }, []);

  const downloadAsText = useCallback((text, filename) => {
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, []);

  const getScoreBadge = (score) => {
    if (score >= 80) return { bg: 'bg-green-100', text: 'text-green-800', label: 'Excellent' };
    if (score >= 60) return { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Bon' };
    if (score >= 40) return { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Moyen' };
    return { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Faible' };
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-7xl h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-teal-600 to-teal-700 text-white">
          <div>
            <h2 className="text-xl font-bold flex items-center gap-2">
              Recherche de Subventions
            </h2>
            <p className="text-teal-100 text-sm mt-1">
              {projectTitle} - {villageName} ({villagePopulation} hab.)
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-teal-800 rounded-full p-2 transition"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mx-4 mt-4 p-3 bg-red-100 text-red-800 rounded-lg flex items-center gap-2">
            <span>!</span>
            <span>{error}</span>
            <button onClick={() => setError(null)} className="ml-auto hover:bg-red-200 rounded p-1">x</button>
          </div>
        )}

        {/* Main content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left panel: Programs */}
          <div className="w-1/3 border-r flex flex-col">
            {/* Tabs */}
            <div className="flex border-b">
              <button
                onClick={() => setActiveTab('programmes')}
                className={`flex-1 py-3 px-4 text-sm font-medium ${
                  activeTab === 'programmes'
                    ? 'bg-teal-50 text-teal-700 border-b-2 border-teal-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                Programmes ({matches.length})
              </button>
              <button
                onClick={() => setActiveTab('historique')}
                className={`flex-1 py-3 px-4 text-sm font-medium ${
                  activeTab === 'historique'
                    ? 'bg-teal-50 text-teal-700 border-b-2 border-teal-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                Historique ({applications.length})
              </button>
            </div>

            {/* Tab content */}
            <div className="flex-1 overflow-y-auto p-3 space-y-3">
              {activeTab === 'programmes' ? (
                <>
                  {loading && (
                    <div className="text-center py-8 text-gray-500">
                      <div className="animate-spin w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full mx-auto mb-2"></div>
                      Recherche des programmes compatibles...
                    </div>
                  )}

                  {!loading && matches.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      Aucun programme compatible trouve.
                      <button
                        onClick={loadMatches}
                        className="block mx-auto mt-4 px-4 py-2 bg-teal-600 text-white rounded hover:bg-teal-700"
                      >
                        Relancer la recherche
                      </button>
                    </div>
                  )}

                  {matches.map((match) => {
                    const scoreBadge = getScoreBadge(match.score);
                    const levelInfo = LEVEL_LABELS[match.level] || { label: match.level, color: 'bg-gray-500' };

                    return (
                      <div
                        key={match.program_id}
                        className="border rounded-lg p-3 hover:shadow-md transition bg-white"
                      >
                        {/* Card header */}
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`text-xs px-2 py-0.5 rounded ${levelInfo.color} text-white`}>
                                {levelInfo.label}
                              </span>
                              <span className={`text-xs px-2 py-0.5 rounded font-bold ${scoreBadge.bg} ${scoreBadge.text}`}>
                                {match.score}%
                              </span>
                            </div>
                            <h4 className="font-semibold text-sm text-gray-900 line-clamp-2">
                              {match.program_name}
                            </h4>
                            <p className="text-xs text-gray-500 mt-1">{match.provider}</p>
                          </div>
                        </div>

                        {/* Amounts */}
                        <div className="text-sm font-medium text-teal-700 mb-2">
                          {match.amount_min?.toLocaleString('fr-FR')}EUR - {match.amount_max?.toLocaleString('fr-FR')}EUR
                          <span className="text-xs text-gray-500 ml-1">
                            ({match.funding_percentage_min || '?'}% - {match.funding_percentage_max || '?'}%)
                          </span>
                        </div>

                        {/* Compatibility reasons */}
                        <div className="space-y-1 mb-3">
                          {match.reasons?.slice(0, 2).map((reason, idx) => (
                            <div key={idx} className="flex items-start gap-1 text-xs text-green-700">
                              <span>+</span>
                              <span>{reason}</span>
                            </div>
                          ))}
                          {match.warnings?.slice(0, 1).map((warning, idx) => (
                            <div key={idx} className="flex items-start gap-1 text-xs text-orange-600">
                              <span>!</span>
                              <span>{warning}</span>
                            </div>
                          ))}
                        </div>

                        {/* Generate button */}
                        <button
                          onClick={() => generateApplication(match.program_id)}
                          disabled={generating && selectedProgramId === match.program_id}
                          className="w-full py-2 px-3 bg-teal-600 text-white text-sm rounded hover:bg-teal-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
                        >
                          {generating && selectedProgramId === match.program_id ? (
                            <span className="flex items-center justify-center gap-2">
                              <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                              Generation en cours...
                            </span>
                          ) : (
                            'Generer le dossier'
                          )}
                        </button>
                      </div>
                    );
                  })}
                </>
              ) : (
                <>
                  {applications.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      Aucun dossier genere pour ce projet.
                    </div>
                  ) : (
                    applications.map((app) => {
                      const statusInfo = STATUS_LABELS[app.status] || STATUS_LABELS['draft'];
                      return (
                        <div
                          key={app.id}
                          onClick={() => loadApplication(app.id)}
                          className="border rounded-lg p-3 hover:shadow-md hover:border-teal-300 transition bg-white cursor-pointer"
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-semibold text-sm">Dossier #{app.id}</p>
                              <p className="text-xs text-gray-600">{app.program_name}</p>
                              {app.amount_requested && (
                                <p className="text-xs text-teal-600 mt-1">
                                  {app.amount_requested.toLocaleString('fr-FR')}EUR demandes
                                </p>
                              )}
                            </div>
                            <span className={`text-xs px-2 py-1 rounded ${statusInfo.color}`}>
                              {statusInfo.label}
                            </span>
                          </div>
                          <p className="text-xs text-gray-400 mt-2">
                            {new Date(app.created_at).toLocaleDateString('fr-FR', {
                              day: 'numeric',
                              month: 'short',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>
                      );
                    })
                  )}
                </>
              )}
            </div>
          </div>

          {/* Right panel: Application preview */}
          <div className="flex-1 flex flex-col bg-gray-50">
            {currentApplication ? (
              <>
                {/* Application header */}
                <div className="p-4 bg-white border-b flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {currentApplication.program_name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      Dossier #{currentApplication.id} -
                      <span className={`ml-2 px-2 py-0.5 rounded text-xs ${STATUS_LABELS[currentApplication.status]?.color || 'bg-gray-200'}`}>
                        {STATUS_LABELS[currentApplication.status]?.label || currentApplication.status}
                      </span>
                      {currentApplication.amount_requested && (
                        <span className="ml-2 text-teal-600 font-medium">
                          {currentApplication.amount_requested.toLocaleString('fr-FR')}EUR
                        </span>
                      )}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => copyToClipboard(currentApplication.text)}
                      className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm transition"
                    >
                      {copySuccess ? 'Copie !' : 'Copier'}
                    </button>
                    <button
                      onClick={() => downloadAsText(
                        currentApplication.text,
                        `dossier_${currentApplication.id}_${currentApplication.program_name.replace(/\s+/g, '_')}.txt`
                      )}
                      className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm transition"
                    >
                      Telecharger
                    </button>
                  </div>
                </div>

                {/* Application content */}
                <div className="flex-1 overflow-y-auto p-6">
                  <div className="bg-white rounded-lg shadow-sm border p-6 max-w-4xl mx-auto">
                    <pre className="whitespace-pre-wrap font-sans text-sm text-gray-800 leading-relaxed">
                      {currentApplication.text}
                    </pre>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <div className="text-6xl mb-4">+</div>
                  <p className="text-lg font-medium">Selectionnez un programme</p>
                  <p className="text-sm">et generez un dossier de demande de subvention</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default GrantMatcher;
