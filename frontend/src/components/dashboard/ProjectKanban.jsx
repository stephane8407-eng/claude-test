// frontend/src/components/dashboard/ProjectKanban.jsx
/**
 * Phase E: Tableau Kanban de Gestion de Projets
 *
 * Affiche les projets du village en 5 colonnes :
 * À explorer | Planification | En cours | Terminé | Abandonné
 *
 * Fonctionnalités :
 * - Glisser-déposer entre colonnes
 * - Cartes de projet avec infos clés
 * - Cliquer sur une carte pour voir les détails
 * - Code couleur par priorité
 */

import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

const STATUS_COLUMNS = [
  { id: 'exploring', title: 'À explorer', emoji: '🔍', color: 'bg-gray-100', emptyText: 'Aucun projet à explorer' },
  { id: 'planning', title: 'Planification', emoji: '📋', color: 'bg-blue-100', emptyText: 'Aucun projet en planification' },
  { id: 'in_progress', title: 'En cours', emoji: '🚧', color: 'bg-yellow-100', emptyText: 'Aucun projet en cours' },
  { id: 'completed', title: 'Terminé', emoji: '✅', color: 'bg-green-100', emptyText: 'Aucun projet terminé' },
  { id: 'abandoned', title: 'Abandonné', emoji: '🗑️', color: 'bg-red-100', emptyText: 'Aucun projet abandonné' }
];

const STATUS_LABELS = {
  'exploring': 'À explorer',
  'planning': 'Planification',
  'in_progress': 'En cours',
  'completed': 'Terminé',
  'abandoned': 'Abandonné'
};

const PRIORITY_COLORS = {
  1: 'border-gray-300 bg-white',
  2: 'border-blue-300 bg-blue-50',
  3: 'border-yellow-300 bg-yellow-50',
  4: 'border-orange-300 bg-orange-50',
  5: 'border-red-300 bg-red-50'
};

const PRIORITY_LABELS = {
  1: 'Faible',
  2: 'Moyenne-Faible',
  3: 'Moyenne',
  4: 'Moyenne-Haute',
  5: 'Haute'
};

// URL de base de l'API
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function ProjectKanban({ villageSlug }) {
  const [projects, setProjects] = useState([]);
  const [byStatus, setByStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);

  // Charger les projets au montage
  useEffect(() => {
    if (villageSlug) {
      loadProjects();
    }
  }, [villageSlug]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/api/villages/${villageSlug}/projects`);

      if (!response.ok) {
        throw new Error(`Échec du chargement des projets : ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Réponse API:', data);
      console.log('Projets:', data.projects);
      console.log('Par statut:', data.by_status);

      setProjects(data.projects || []);
      setByStatus(data.by_status || {
        exploring: [],
        planning: [],
        in_progress: [],
        completed: [],
        abandoned: []
      });
    } catch (err) {
      console.error('Échec du chargement des projets:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Gérer le glisser-déposer
  const onDragEnd = async (result) => {
    const { source, destination, draggableId } = result;

    // Déposé en dehors d'une colonne
    if (!destination) return;

    // Pas de changement de statut
    if (source.droppableId === destination.droppableId) return;

    const newStatus = destination.droppableId;
    const projectId = parseInt(draggableId);

    // Mise à jour optimiste de l'interface
    const updatedProjects = projects.map(p =>
      p.id === projectId ? { ...p, status: newStatus } : p
    );
    setProjects(updatedProjects);

    // Mettre à jour la vue groupée
    const newByStatus = { ...byStatus };
    const project = byStatus[source.droppableId].find(p => p.id === projectId);
    if (project) {
      newByStatus[source.droppableId] = newByStatus[source.droppableId].filter(p => p.id !== projectId);
      newByStatus[destination.droppableId] = [...(newByStatus[destination.droppableId] || []), { ...project, status: newStatus }];
      setByStatus(newByStatus);
    }

    // Appel API pour persister le changement
    try {
      const response = await fetch(`${API_BASE}/api/villages/${villageSlug}/projects/${projectId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      if (!response.ok) {
        throw new Error('Échec de la mise à jour du statut');
      }
    } catch (err) {
      console.error('Échec de la mise à jour du statut:', err);
      // Recharger pour annuler la mise à jour optimiste
      loadProjects();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Chargement des projets...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">
          <p className="font-semibold">Erreur lors du chargement des projets</p>
          <p className="text-sm">{error}</p>
          <button
            onClick={loadProjects}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full">
      <DragDropContext onDragEnd={onDragEnd}>
        <div className="flex gap-4 overflow-x-auto pb-4">
          {STATUS_COLUMNS.map(column => (
            <div key={column.id} className="flex-shrink-0 w-80">
              {/* En-tête de colonne */}
              <div className={`${column.color} rounded-t-lg p-3 border-b-2 border-gray-300`}>
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-800">
                    <span className="mr-2">{column.emoji}</span>
                    {column.title}
                  </h3>
                  <span className="text-sm font-medium text-gray-600">
                    {byStatus[column.id]?.length || 0}
                  </span>
                </div>
              </div>

              {/* Colonne déposable */}
              <Droppable droppableId={column.id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`min-h-[400px] p-3 ${
                      snapshot.isDraggingOver ? 'bg-blue-50' : 'bg-gray-50'
                    } rounded-b-lg border-2 border-gray-200`}
                  >
                    {(byStatus[column.id] || []).map((project, index) => (
                      <Draggable
                        key={project.id}
                        draggableId={project.id.toString()}
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            onClick={() => setSelectedProject(project)}
                            className={`mb-3 p-4 rounded-lg border-2 shadow-sm cursor-pointer transition-all hover:shadow-md ${
                              PRIORITY_COLORS[project.priority] || PRIORITY_COLORS[3]
                            } ${snapshot.isDragging ? 'opacity-50' : ''}`}
                          >
                            {/* Titre du projet */}
                            <h4 className="font-semibold text-gray-800 mb-2 line-clamp-2">
                              {project.project_data?.title || 'Projet sans titre'}
                            </h4>

                            {/* Budget */}
                            {(project.budget_estimated_min || project.budget_estimated_max) && (
                              <div className="text-sm text-gray-600 mb-2">
                                💰 {project.budget_estimated_min?.toLocaleString('fr-FR') || '?'} € - {project.budget_estimated_max?.toLocaleString('fr-FR') || '?'} €
                              </div>
                            )}

                            {/* Délai */}
                            {project.timeline_months && (
                              <div className="text-sm text-gray-600 mb-2">
                                ⏱️ {project.timeline_months} mois
                              </div>
                            )}

                            {/* Badge de priorité */}
                            <div className="flex items-center justify-between mt-2">
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                project.priority >= 4
                                  ? 'bg-red-200 text-red-800'
                                  : project.priority >= 3
                                  ? 'bg-yellow-200 text-yellow-800'
                                  : 'bg-gray-200 text-gray-800'
                              }`}>
                                ⭐ {PRIORITY_LABELS[project.priority] || 'Moyenne'}
                              </span>

                              {/* Badge inspiré par */}
                              {project.project_data?.inspired_by && (
                                <span className="text-xs text-gray-500">
                                  🏆 {project.project_data.inspired_by}
                                </span>
                              )}
                            </div>

                            {/* Badge de niveau */}
                            {project.project_data?.tier && (
                              <div className="mt-2">
                                <span className={`text-xs px-2 py-1 rounded ${
                                  project.project_data.tier === 'breakthrough'
                                    ? 'bg-purple-200 text-purple-800'
                                    : project.project_data.tier === 'innovation'
                                    ? 'bg-blue-200 text-blue-800'
                                    : 'bg-green-200 text-green-800'
                                }`}>
                                  {project.project_data.tier}
                                </span>
                              </div>
                            )}
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}

                    {/* État vide */}
                    {(!byStatus[column.id] || byStatus[column.id].length === 0) && (
                      <div className="text-center text-gray-400 py-8">
                        {column.emptyText}
                      </div>
                    )}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>

      {/* Modal de détail du projet */}
      {selectedProject && (
        <ProjectDetailModal
          project={selectedProject}
          villageSlug={villageSlug}
          onClose={() => setSelectedProject(null)}
          onUpdate={loadProjects}
        />
      )}
    </div>
  );
}

// ============================================
// MODAL DE DÉTAIL DU PROJET
// ============================================

function ProjectDetailModal({ project, villageSlug, onClose, onUpdate }) {
  const [notes, setNotes] = useState(project.notes || '');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API_BASE}/api/villages/${villageSlug}/projects/${project.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes })
      });

      if (!response.ok) {
        throw new Error('Échec de la sauvegarde');
      }

      onUpdate();
      onClose();
    } catch (err) {
      console.error('Échec de la sauvegarde du projet:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* En-tête */}
        <div className="sticky top-0 bg-white border-b p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {project.project_data?.title || 'Projet sans titre'}
              </h2>
              <div className="flex items-center gap-3">
                <span className={`text-sm px-3 py-1 rounded-full ${
                  project.status === 'completed' ? 'bg-green-200 text-green-800' :
                  project.status === 'in_progress' ? 'bg-yellow-200 text-yellow-800' :
                  project.status === 'planning' ? 'bg-blue-200 text-blue-800' :
                  project.status === 'abandoned' ? 'bg-red-200 text-red-800' :
                  'bg-gray-200 text-gray-800'
                }`}>
                  {STATUS_LABELS[project.status] || project.status}
                </span>
                {project.project_data?.tier && (
                  <span className="text-sm px-3 py-1 rounded bg-purple-200 text-purple-800">
                    {project.project_data.tier}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        {/* Contenu */}
        <div className="p-6 space-y-6">
          {/* Description */}
          {project.project_data?.description && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
              <p className="text-gray-700">{project.project_data.description}</p>
            </div>
          )}

          {/* Détails clés */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">Budget estimé</h4>
              <p className="text-gray-700">
                {project.budget_estimated_min?.toLocaleString('fr-FR') || '?'} € - {project.budget_estimated_max?.toLocaleString('fr-FR') || '?'} €
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">Durée estimée</h4>
              <p className="text-gray-700">{project.timeline_months || '?'} mois</p>
            </div>
            {project.project_data?.difficulty && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Difficulté</h4>
                <p className="text-gray-700">{project.project_data.difficulty}</p>
              </div>
            )}
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">Priorité</h4>
              <p className="text-gray-700">⭐ {PRIORITY_LABELS[project.priority] || 'Moyenne'}</p>
            </div>
          </div>

          {/* Inspiré par */}
          {project.project_data?.inspired_by && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Inspiré par</h3>
              <p className="text-gray-700">🏆 {project.project_data.inspired_by}</p>
            </div>
          )}

          {/* Sources de financement */}
          {project.project_data?.funding_sources && project.project_data.funding_sources.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Sources de financement</h3>
              <ul className="list-disc list-inside text-gray-700">
                {project.project_data.funding_sources.map((source, i) => (
                  <li key={i}>{source}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Prochaines étapes */}
          {project.next_steps && project.next_steps.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Prochaines étapes</h3>
              <ul className="space-y-2">
                {project.next_steps.map((step, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-blue-600">→</span>
                    <span className="text-gray-700">{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Étapes terminées */}
          {project.completed_steps && project.completed_steps.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Étapes terminées</h3>
              <ul className="space-y-2">
                {project.completed_steps.map((step, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-green-600">✓</span>
                    <span className="text-gray-700">{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Notes du maire */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Notes</h3>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full p-3 border rounded-lg resize-none"
              rows={4}
              placeholder="Ajouter des notes sur ce projet..."
            />
          </div>
        </div>

        {/* Pied de page */}
        <div className="sticky bottom-0 bg-gray-50 border-t p-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition"
          >
            Annuler
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            {saving ? 'Enregistrement...' : 'Enregistrer'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProjectKanban;
