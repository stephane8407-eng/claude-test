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
import { GrantMatcher } from './GrantMatcher';

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

export function ProjectKanban({ villageSlug, showCreateModal = false, onCloseCreateModal }) {
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

      {/* Modal de création de projet */}
      {showCreateModal && (
        <ProjectCreateModal
          villageSlug={villageSlug}
          onClose={onCloseCreateModal}
          onCreated={loadProjects}
        />
      )}
    </div>
  );
}

// ============================================
// TABS POUR LE FORMULAIRE DE PROJET
// ============================================

const FORM_TABS = [
  { id: 'general', label: 'General', icon: '📋' },
  { id: 'budget', label: 'Budget', icon: '💰' },
  { id: 'planning', label: 'Planification', icon: '📅' },
  { id: 'context', label: 'Contexte', icon: '🏘️' }
];

// Options predefinies pour les partenaires
const PARTNER_OPTIONS = [
  'Communaute de communes',
  'Conseil departemental',
  'Conseil regional',
  'Prefecture',
  'CAUE (Architecture)',
  'ADEME',
  'Association locale',
  'Office de tourisme',
  'Chambre de commerce',
  'Chambre d\'agriculture',
  'Fondation du patrimoine',
  'Parc naturel regional'
];

// Options pour les defis
const CHALLENGE_OPTIONS = [
  'Attractivite territoriale',
  'Transition ecologique',
  'Revitalisation du centre-bourg',
  'Services a la population',
  'Mobilite',
  'Numerique',
  'Patrimoine',
  'Tourisme',
  'Agriculture locale',
  'Emploi et formation'
];

// ============================================
// MODAL DE DÉTAIL DU PROJET (ENHANCED)
// ============================================

function ProjectDetailModal({ project, villageSlug, onClose, onUpdate }) {
  const [activeTab, setActiveTab] = useState('general');
  const [saving, setSaving] = useState(false);
  const [showGrantMatcher, setShowGrantMatcher] = useState(false);

  // Form state - initialize from project data
  const [formData, setFormData] = useState(() => {
    const pd = project.project_data || {};
    return {
      // General
      title: pd.title || '',
      description: pd.description || '',
      notes: project.notes || '',
      priority: project.priority || 3,

      // Budget
      budget_estimated_min: project.budget_estimated_min || 0,
      budget_estimated_max: project.budget_estimated_max || 0,
      budget_breakdown: pd.budget_breakdown || {
        infrastructure: 0,
        equipment: 0,
        studies: 0,
        communication: 0,
        other: 0
      },
      secured_funding: pd.secured_funding || [],

      // Planning
      timeline_months: project.timeline_months || 12,
      planned_start_date: pd.planned_start_date || '',
      planned_end_date: pd.planned_end_date || '',
      milestones: pd.milestones || [],
      required_permits: pd.required_permits || [],

      // Specifics
      location_address: pd.location_address || '',
      project_area_m2: pd.project_area_m2 || '',
      beneficiaries_count: pd.beneficiaries_count || '',
      partners: pd.partners || [],
      stakeholders: pd.stakeholders || '',

      // Context
      village_area_hectares: pd.village_area_hectares || '',
      challenges_addressed: pd.challenges_addressed || [],
      past_similar_projects: pd.past_similar_projects || '',
      available_resources: pd.available_resources || ''
    };
  });

  // Update form field
  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Update nested object field (for budget_breakdown)
  const updateNestedField = (parent, field, value) => {
    setFormData(prev => ({
      ...prev,
      [parent]: { ...prev[parent], [field]: value }
    }));
  };

  // Add item to array field
  const addToArray = (field, value) => {
    if (value && !formData[field].includes(value)) {
      setFormData(prev => ({ ...prev, [field]: [...prev[field], value] }));
    }
  };

  // Remove item from array field
  const removeFromArray = (field, index) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  // Save all data
  const handleSave = async () => {
    setSaving(true);
    try {
      // Build project_data object with all extended fields
      const projectDataUpdate = {
        title: formData.title,
        description: formData.description,
        budget_breakdown: formData.budget_breakdown,
        secured_funding: formData.secured_funding,
        planned_start_date: formData.planned_start_date,
        planned_end_date: formData.planned_end_date,
        milestones: formData.milestones,
        required_permits: formData.required_permits,
        location_address: formData.location_address,
        project_area_m2: formData.project_area_m2,
        beneficiaries_count: formData.beneficiaries_count,
        partners: formData.partners,
        stakeholders: formData.stakeholders,
        village_area_hectares: formData.village_area_hectares,
        challenges_addressed: formData.challenges_addressed,
        past_similar_projects: formData.past_similar_projects,
        available_resources: formData.available_resources
      };

      const response = await fetch(`${API_BASE}/api/villages/${villageSlug}/projects/${project.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notes: formData.notes,
          priority: formData.priority,
          budget_estimated_min: parseInt(formData.budget_estimated_min) || 0,
          budget_estimated_max: parseInt(formData.budget_estimated_max) || 0,
          timeline_months: parseInt(formData.timeline_months) || 12,
          project_data: projectDataUpdate
        })
      });

      if (!response.ok) {
        throw new Error('Echec de la sauvegarde');
      }

      onUpdate();
      onClose();
    } catch (err) {
      console.error('Echec de la sauvegarde du projet:', err);
      alert('Erreur lors de la sauvegarde. Veuillez reessayer.');
    } finally {
      setSaving(false);
    }
  };

  // Calculate total budget from breakdown
  const totalBudgetBreakdown = Object.values(formData.budget_breakdown).reduce((a, b) => a + (parseInt(b) || 0), 0);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden">
        {/* En-tete */}
        <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-4">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold mb-1">
                {formData.title || 'Projet sans titre'}
              </h2>
              <div className="flex items-center gap-2 text-teal-100 text-sm">
                <span className={`px-2 py-0.5 rounded-full text-xs ${
                  project.status === 'completed' ? 'bg-green-500/30' :
                  project.status === 'in_progress' ? 'bg-yellow-500/30' :
                  project.status === 'planning' ? 'bg-blue-500/30' :
                  project.status === 'abandoned' ? 'bg-red-500/30' :
                  'bg-white/20'
                }`}>
                  {STATUS_LABELS[project.status] || project.status}
                </span>
                {project.project_data?.tier && (
                  <span className="px-2 py-0.5 rounded-full bg-purple-500/30 text-xs">
                    {project.project_data.tier}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white text-2xl leading-none"
            >
              x
            </button>
          </div>
        </div>

        {/* Onglets */}
        <div className="flex border-b bg-gray-50">
          {FORM_TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-3 px-4 text-sm font-medium transition ${
                activeTab === tab.id
                  ? 'bg-white border-b-2 border-teal-600 text-teal-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Contenu des onglets */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Onglet General */}
          {activeTab === 'general' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Titre du projet *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => updateField('title', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                  placeholder="Ex: Renovation de la place du village"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description detaillee
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => updateField('description', e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={4}
                  placeholder="Decrivez le projet, ses objectifs et son impact attendu..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Localisation / Adresse
                  </label>
                  <input
                    type="text"
                    value={formData.location_address}
                    onChange={(e) => updateField('location_address', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                    placeholder="Ex: Place de la Mairie, Rue principale"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Surface concernee (m2)
                  </label>
                  <input
                    type="number"
                    value={formData.project_area_m2}
                    onChange={(e) => updateField('project_area_m2', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                    placeholder="Ex: 500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre de beneficiaires directs
                  </label>
                  <input
                    type="number"
                    value={formData.beneficiaries_count}
                    onChange={(e) => updateField('beneficiaries_count', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                    placeholder="Ex: 350"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priorite
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => updateField('priority', parseInt(e.target.value))}
                    className="w-full p-3 border rounded-lg"
                  >
                    {[1, 2, 3, 4, 5].map(p => (
                      <option key={p} value={p}>{PRIORITY_LABELS[p]}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes internes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => updateField('notes', e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={3}
                  placeholder="Notes pour usage interne (non incluses dans les dossiers)..."
                />
              </div>
            </div>
          )}

          {/* Onglet Budget */}
          {activeTab === 'budget' && (
            <div className="space-y-6">
              {/* Budget global */}
              <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
                <h3 className="font-semibold text-teal-800 mb-3">Budget global estime *</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-teal-700 mb-1">Minimum (euros)</label>
                    <input
                      type="number"
                      value={formData.budget_estimated_min}
                      onChange={(e) => updateField('budget_estimated_min', e.target.value)}
                      className="w-full p-3 border border-teal-300 rounded-lg text-lg font-semibold"
                      placeholder="25000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-teal-700 mb-1">Maximum (euros)</label>
                    <input
                      type="number"
                      value={formData.budget_estimated_max}
                      onChange={(e) => updateField('budget_estimated_max', e.target.value)}
                      className="w-full p-3 border border-teal-300 rounded-lg text-lg font-semibold"
                      placeholder="35000"
                    />
                  </div>
                </div>
              </div>

              {/* Repartition du budget */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">
                  Repartition par poste (optionnel)
                  {totalBudgetBreakdown > 0 && (
                    <span className="ml-2 text-sm font-normal text-gray-500">
                      Total: {totalBudgetBreakdown.toLocaleString('fr-FR')} euros
                    </span>
                  )}
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { key: 'infrastructure', label: 'Travaux / Infrastructure' },
                    { key: 'equipment', label: 'Equipement / Materiel' },
                    { key: 'studies', label: 'Etudes / Maitrise d\'oeuvre' },
                    { key: 'communication', label: 'Communication / Signalisation' },
                    { key: 'other', label: 'Autres depenses' }
                  ].map(item => (
                    <div key={item.key}>
                      <label className="block text-sm text-gray-600 mb-1">{item.label}</label>
                      <input
                        type="number"
                        value={formData.budget_breakdown[item.key] || ''}
                        onChange={(e) => updateNestedField('budget_breakdown', item.key, e.target.value)}
                        className="w-full p-2 border rounded-lg"
                        placeholder="0"
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Financements deja securises */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Financements deja securises</h3>
                <div className="space-y-2">
                  {formData.secured_funding.map((funding, index) => (
                    <div key={index} className="flex items-center gap-2 bg-green-50 p-2 rounded">
                      <span className="flex-1 text-green-800">{funding.source}: {funding.amount?.toLocaleString('fr-FR')} euros</span>
                      <button
                        onClick={() => removeFromArray('secured_funding', index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        x
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2 mt-2">
                  <input
                    type="text"
                    id="newFundingSource"
                    className="flex-1 p-2 border rounded-lg"
                    placeholder="Source (ex: Autofinancement)"
                  />
                  <input
                    type="number"
                    id="newFundingAmount"
                    className="w-32 p-2 border rounded-lg"
                    placeholder="Montant"
                  />
                  <button
                    onClick={() => {
                      const source = document.getElementById('newFundingSource').value;
                      const amount = parseInt(document.getElementById('newFundingAmount').value);
                      if (source && amount) {
                        setFormData(prev => ({
                          ...prev,
                          secured_funding: [...prev.secured_funding, { source, amount }]
                        }));
                        document.getElementById('newFundingSource').value = '';
                        document.getElementById('newFundingAmount').value = '';
                      }
                    }}
                    className="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Onglet Planification */}
          {activeTab === 'planning' && (
            <div className="space-y-6">
              {/* Dates */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duree estimee (mois)
                  </label>
                  <input
                    type="number"
                    value={formData.timeline_months}
                    onChange={(e) => updateField('timeline_months', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                    placeholder="12"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date de debut prevue
                  </label>
                  <input
                    type="date"
                    value={formData.planned_start_date}
                    onChange={(e) => updateField('planned_start_date', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date de fin prevue
                  </label>
                  <input
                    type="date"
                    value={formData.planned_end_date}
                    onChange={(e) => updateField('planned_end_date', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                  />
                </div>
              </div>

              {/* Jalons */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Jalons cles</h3>
                <div className="space-y-2">
                  {formData.milestones.map((milestone, index) => (
                    <div key={index} className="flex items-center gap-2 bg-blue-50 p-2 rounded">
                      <span className="flex-1 text-blue-800">{milestone}</span>
                      <button
                        onClick={() => removeFromArray('milestones', index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        x
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2 mt-2">
                  <input
                    type="text"
                    id="newMilestone"
                    className="flex-1 p-2 border rounded-lg"
                    placeholder="Ex: Depot du permis de construire"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        addToArray('milestones', e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={() => {
                      const input = document.getElementById('newMilestone');
                      addToArray('milestones', input.value);
                      input.value = '';
                    }}
                    className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Autorisations */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Autorisations / Permis requis</h3>
                <div className="space-y-2">
                  {formData.required_permits.map((permit, index) => (
                    <div key={index} className="flex items-center gap-2 bg-orange-50 p-2 rounded">
                      <span className="flex-1 text-orange-800">{permit}</span>
                      <button
                        onClick={() => removeFromArray('required_permits', index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        x
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2 mt-2">
                  <input
                    type="text"
                    id="newPermit"
                    className="flex-1 p-2 border rounded-lg"
                    placeholder="Ex: Permis d'amenager, DT/DICT"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        addToArray('required_permits', e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={() => {
                      const input = document.getElementById('newPermit');
                      addToArray('required_permits', input.value);
                      input.value = '';
                    }}
                    className="px-3 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Partenaires */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Partenaires impliques</h3>
                <div className="flex flex-wrap gap-2 mb-2">
                  {formData.partners.map((partner, index) => (
                    <span key={index} className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                      {partner}
                      <button
                        onClick={() => removeFromArray('partners', index)}
                        className="text-purple-500 hover:text-purple-700 ml-1"
                      >
                        x
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <select
                    id="partnerSelect"
                    className="flex-1 p-2 border rounded-lg"
                    onChange={(e) => {
                      if (e.target.value) {
                        addToArray('partners', e.target.value);
                        e.target.value = '';
                      }
                    }}
                  >
                    <option value="">Choisir un partenaire...</option>
                    {PARTNER_OPTIONS.filter(p => !formData.partners.includes(p)).map(partner => (
                      <option key={partner} value={partner}>{partner}</option>
                    ))}
                  </select>
                  <input
                    type="text"
                    id="customPartner"
                    className="w-48 p-2 border rounded-lg"
                    placeholder="Autre partenaire"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && e.target.value) {
                        addToArray('partners', e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                </div>
              </div>

              {/* Acteurs cles */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Acteurs cles / Soutiens
                </label>
                <textarea
                  value={formData.stakeholders}
                  onChange={(e) => updateField('stakeholders', e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={2}
                  placeholder="Ex: Conseiller departemental M. Dupont, President de l'association des commercants..."
                />
              </div>
            </div>
          )}

          {/* Onglet Contexte */}
          {activeTab === 'context' && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-700">
                  Ces informations enrichissent le contexte pour la generation de dossiers de subvention plus precis et pertinents.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Superficie de la commune (hectares)
                </label>
                <input
                  type="number"
                  value={formData.village_area_hectares}
                  onChange={(e) => updateField('village_area_hectares', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                  placeholder="Ex: 1250"
                />
              </div>

              {/* Defis adresses */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Enjeux / Defis adresses par ce projet</h3>
                <div className="flex flex-wrap gap-2 mb-3">
                  {formData.challenges_addressed.map((challenge, index) => (
                    <span key={index} className="inline-flex items-center gap-1 px-3 py-1 bg-teal-100 text-teal-800 rounded-full text-sm">
                      {challenge}
                      <button
                        onClick={() => removeFromArray('challenges_addressed', index)}
                        className="text-teal-500 hover:text-teal-700 ml-1"
                      >
                        x
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2">
                  {CHALLENGE_OPTIONS.filter(c => !formData.challenges_addressed.includes(c)).map(challenge => (
                    <button
                      key={challenge}
                      onClick={() => addToArray('challenges_addressed', challenge)}
                      className="px-3 py-1 border border-gray-300 rounded-full text-sm text-gray-600 hover:bg-gray-100 hover:border-gray-400"
                    >
                      + {challenge}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Projets similaires realises dans la commune
                </label>
                <textarea
                  value={formData.past_similar_projects}
                  onChange={(e) => updateField('past_similar_projects', e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={3}
                  placeholder="Ex: Renovation de la salle des fetes en 2019 (45 000 euros, subvention DETR a 40%)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ressources disponibles (equipements, locaux, benevoles...)
                </label>
                <textarea
                  value={formData.available_resources}
                  onChange={(e) => updateField('available_resources', e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={3}
                  placeholder="Ex: Local technique municipal, equipe technique de 2 agents, association de benevoles (15 membres actifs)"
                />
              </div>
            </div>
          )}
        </div>

        {/* Pied de page */}
        <div className="bg-gray-50 border-t p-4 flex justify-between items-center">
          <button
            onClick={() => setShowGrantMatcher(true)}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition flex items-center gap-2"
          >
            Rechercher des subventions
          </button>
          <div className="flex gap-3">
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

      {/* Modal de recherche de subventions */}
      {showGrantMatcher && (
        <GrantMatcher
          projectId={project.id}
          projectTitle={formData.title || 'Projet sans titre'}
          villageName={villageSlug}
          villagePopulation={800}
          villageRegion="Nouvelle-Aquitaine"
          villageDepartment="Charente"
          onClose={() => setShowGrantMatcher(false)}
        />
      )}
    </div>
  );
}


// ============================================
// MODAL DE CRÉATION DE PROJET
// ============================================

function ProjectCreateModal({ villageSlug, onClose, onCreated }) {
  const [activeTab, setActiveTab] = useState('general');
  const [saving, setSaving] = useState(false);

  // Form state - empty initial values
  const [formData, setFormData] = useState({
    // General
    title: '',
    description: '',
    notes: '',
    priority: 3,

    // Budget
    budget_estimated_min: '',
    budget_estimated_max: '',
    budget_breakdown: {
      infrastructure: 0,
      equipment: 0,
      studies: 0,
      communication: 0,
      other: 0
    },
    secured_funding: [],

    // Planning
    timeline_months: 12,
    planned_start_date: '',
    planned_end_date: '',
    milestones: [],
    required_permits: [],

    // Specifics
    location_address: '',
    project_area_m2: '',
    beneficiaries_count: '',
    partners: [],
    stakeholders: '',

    // Context
    village_area_hectares: '',
    challenges_addressed: [],
    past_similar_projects: '',
    available_resources: ''
  });

  // Update form field
  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Update nested object field (for budget_breakdown)
  const updateNestedField = (parent, field, value) => {
    setFormData(prev => ({
      ...prev,
      [parent]: { ...prev[parent], [field]: value }
    }));
  };

  // Add item to array field
  const addToArray = (field, value) => {
    if (value && !formData[field].includes(value)) {
      setFormData(prev => ({ ...prev, [field]: [...prev[field], value] }));
    }
  };

  // Remove item from array field
  const removeFromArray = (field, index) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  // Create project
  const handleCreate = async () => {
    if (!formData.title.trim()) {
      alert('Veuillez saisir un titre pour le projet');
      return;
    }

    setSaving(true);
    try {
      // Build project_data object
      const projectData = {
        title: formData.title,
        description: formData.description,
        budget_breakdown: formData.budget_breakdown,
        secured_funding: formData.secured_funding,
        planned_start_date: formData.planned_start_date,
        planned_end_date: formData.planned_end_date,
        milestones: formData.milestones,
        required_permits: formData.required_permits,
        location_address: formData.location_address,
        project_area_m2: formData.project_area_m2 ? parseInt(formData.project_area_m2) : null,
        beneficiaries_count: formData.beneficiaries_count ? parseInt(formData.beneficiaries_count) : null,
        partners: formData.partners,
        stakeholders: formData.stakeholders,
        village_area_hectares: formData.village_area_hectares ? parseInt(formData.village_area_hectares) : null,
        challenges_addressed: formData.challenges_addressed,
        past_similar_projects: formData.past_similar_projects,
        available_resources: formData.available_resources,
        budget_min: parseInt(formData.budget_estimated_min) || 0,
        budget_max: parseInt(formData.budget_estimated_max) || 0,
        timeline_months: parseInt(formData.timeline_months) || 12
      };

      const response = await fetch(`${API_BASE}/api/villages/${villageSlug}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_data: projectData,
          priority: formData.priority,
          notes: formData.notes
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Echec de la creation');
      }

      onCreated();
      onClose();
    } catch (err) {
      console.error('Echec de la creation du projet:', err);
      alert('Erreur lors de la creation: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  // Calculate total budget from breakdown
  const totalBudgetBreakdown = Object.values(formData.budget_breakdown).reduce((a, b) => a + (parseInt(b) || 0), 0);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden">
        {/* En-tete */}
        <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-4">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold mb-1">
                Nouveau Projet
              </h2>
              <p className="text-teal-100 text-sm">
                Creez un nouveau projet pour votre commune
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white text-2xl leading-none"
            >
              x
            </button>
          </div>
        </div>

        {/* Onglets */}
        <div className="flex border-b bg-gray-50">
          {FORM_TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-3 px-4 text-sm font-medium transition ${
                activeTab === tab.id
                  ? 'bg-white border-b-2 border-teal-600 text-teal-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Contenu des onglets */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Onglet General */}
          {activeTab === 'general' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Titre du projet *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => updateField('title', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                  placeholder="Ex: Renovation de la place du village"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description detaillee
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => updateField('description', e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={4}
                  placeholder="Decrivez le projet, ses objectifs et son impact attendu..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Localisation / Adresse
                  </label>
                  <input
                    type="text"
                    value={formData.location_address}
                    onChange={(e) => updateField('location_address', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                    placeholder="Ex: Place de la Mairie, Rue principale"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Surface concernee (m2)
                  </label>
                  <input
                    type="number"
                    value={formData.project_area_m2}
                    onChange={(e) => updateField('project_area_m2', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                    placeholder="Ex: 500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre de beneficiaires directs
                  </label>
                  <input
                    type="number"
                    value={formData.beneficiaries_count}
                    onChange={(e) => updateField('beneficiaries_count', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                    placeholder="Ex: 350"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priorite
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => updateField('priority', parseInt(e.target.value))}
                    className="w-full p-3 border rounded-lg"
                  >
                    {[1, 2, 3, 4, 5].map(p => (
                      <option key={p} value={p}>{PRIORITY_LABELS[p]}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes internes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => updateField('notes', e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={3}
                  placeholder="Notes pour usage interne (non incluses dans les dossiers)..."
                />
              </div>
            </div>
          )}

          {/* Onglet Budget */}
          {activeTab === 'budget' && (
            <div className="space-y-6">
              {/* Budget global */}
              <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
                <h3 className="font-semibold text-teal-800 mb-3">Budget global estime *</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-teal-700 mb-1">Minimum (euros)</label>
                    <input
                      type="number"
                      value={formData.budget_estimated_min}
                      onChange={(e) => updateField('budget_estimated_min', e.target.value)}
                      className="w-full p-3 border border-teal-300 rounded-lg text-lg font-semibold"
                      placeholder="25000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-teal-700 mb-1">Maximum (euros)</label>
                    <input
                      type="number"
                      value={formData.budget_estimated_max}
                      onChange={(e) => updateField('budget_estimated_max', e.target.value)}
                      className="w-full p-3 border border-teal-300 rounded-lg text-lg font-semibold"
                      placeholder="35000"
                    />
                  </div>
                </div>
              </div>

              {/* Repartition du budget */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">
                  Repartition par poste (optionnel)
                  {totalBudgetBreakdown > 0 && (
                    <span className="ml-2 text-sm font-normal text-gray-500">
                      Total: {totalBudgetBreakdown.toLocaleString('fr-FR')} euros
                    </span>
                  )}
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { key: 'infrastructure', label: 'Travaux / Infrastructure' },
                    { key: 'equipment', label: 'Equipement / Materiel' },
                    { key: 'studies', label: 'Etudes / Maitrise d\'oeuvre' },
                    { key: 'communication', label: 'Communication / Signalisation' },
                    { key: 'other', label: 'Autres depenses' }
                  ].map(item => (
                    <div key={item.key}>
                      <label className="block text-sm text-gray-600 mb-1">{item.label}</label>
                      <input
                        type="number"
                        value={formData.budget_breakdown[item.key] || ''}
                        onChange={(e) => updateNestedField('budget_breakdown', item.key, e.target.value)}
                        className="w-full p-2 border rounded-lg"
                        placeholder="0"
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Financements deja securises */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Financements deja securises</h3>
                <div className="space-y-2">
                  {formData.secured_funding.map((funding, index) => (
                    <div key={index} className="flex items-center gap-2 bg-green-50 p-2 rounded">
                      <span className="flex-1 text-green-800">{funding.source}: {funding.amount?.toLocaleString('fr-FR')} euros</span>
                      <button
                        onClick={() => removeFromArray('secured_funding', index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        x
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2 mt-2">
                  <input
                    type="text"
                    id="createNewFundingSource"
                    className="flex-1 p-2 border rounded-lg"
                    placeholder="Source (ex: Autofinancement)"
                  />
                  <input
                    type="number"
                    id="createNewFundingAmount"
                    className="w-32 p-2 border rounded-lg"
                    placeholder="Montant"
                  />
                  <button
                    onClick={() => {
                      const source = document.getElementById('createNewFundingSource').value;
                      const amount = parseInt(document.getElementById('createNewFundingAmount').value);
                      if (source && amount) {
                        setFormData(prev => ({
                          ...prev,
                          secured_funding: [...prev.secured_funding, { source, amount }]
                        }));
                        document.getElementById('createNewFundingSource').value = '';
                        document.getElementById('createNewFundingAmount').value = '';
                      }
                    }}
                    className="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Onglet Planification */}
          {activeTab === 'planning' && (
            <div className="space-y-6">
              {/* Dates */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duree estimee (mois)
                  </label>
                  <input
                    type="number"
                    value={formData.timeline_months}
                    onChange={(e) => updateField('timeline_months', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                    placeholder="12"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date de debut prevue
                  </label>
                  <input
                    type="date"
                    value={formData.planned_start_date}
                    onChange={(e) => updateField('planned_start_date', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date de fin prevue
                  </label>
                  <input
                    type="date"
                    value={formData.planned_end_date}
                    onChange={(e) => updateField('planned_end_date', e.target.value)}
                    className="w-full p-3 border rounded-lg"
                  />
                </div>
              </div>

              {/* Jalons */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Jalons cles</h3>
                <div className="space-y-2">
                  {formData.milestones.map((milestone, index) => (
                    <div key={index} className="flex items-center gap-2 bg-blue-50 p-2 rounded">
                      <span className="flex-1 text-blue-800">{milestone}</span>
                      <button
                        onClick={() => removeFromArray('milestones', index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        x
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2 mt-2">
                  <input
                    type="text"
                    id="createNewMilestone"
                    className="flex-1 p-2 border rounded-lg"
                    placeholder="Ex: Depot du permis de construire"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        addToArray('milestones', e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={() => {
                      const input = document.getElementById('createNewMilestone');
                      addToArray('milestones', input.value);
                      input.value = '';
                    }}
                    className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Autorisations */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Autorisations / Permis requis</h3>
                <div className="space-y-2">
                  {formData.required_permits.map((permit, index) => (
                    <div key={index} className="flex items-center gap-2 bg-orange-50 p-2 rounded">
                      <span className="flex-1 text-orange-800">{permit}</span>
                      <button
                        onClick={() => removeFromArray('required_permits', index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        x
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2 mt-2">
                  <input
                    type="text"
                    id="createNewPermit"
                    className="flex-1 p-2 border rounded-lg"
                    placeholder="Ex: Permis d'amenager, DT/DICT"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        addToArray('required_permits', e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={() => {
                      const input = document.getElementById('createNewPermit');
                      addToArray('required_permits', input.value);
                      input.value = '';
                    }}
                    className="px-3 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Partenaires */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Partenaires impliques</h3>
                <div className="flex flex-wrap gap-2 mb-2">
                  {formData.partners.map((partner, index) => (
                    <span key={index} className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                      {partner}
                      <button
                        onClick={() => removeFromArray('partners', index)}
                        className="text-purple-500 hover:text-purple-700 ml-1"
                      >
                        x
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <select
                    id="createPartnerSelect"
                    className="flex-1 p-2 border rounded-lg"
                    onChange={(e) => {
                      if (e.target.value) {
                        addToArray('partners', e.target.value);
                        e.target.value = '';
                      }
                    }}
                  >
                    <option value="">Choisir un partenaire...</option>
                    {PARTNER_OPTIONS.filter(p => !formData.partners.includes(p)).map(partner => (
                      <option key={partner} value={partner}>{partner}</option>
                    ))}
                  </select>
                  <input
                    type="text"
                    id="createCustomPartner"
                    className="w-48 p-2 border rounded-lg"
                    placeholder="Autre partenaire"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && e.target.value) {
                        addToArray('partners', e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                </div>
              </div>

              {/* Acteurs cles */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Acteurs cles / Soutiens
                </label>
                <textarea
                  value={formData.stakeholders}
                  onChange={(e) => updateField('stakeholders', e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={2}
                  placeholder="Ex: Conseiller departemental M. Dupont, President de l'association des commercants..."
                />
              </div>
            </div>
          )}

          {/* Onglet Contexte */}
          {activeTab === 'context' && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-700">
                  Ces informations enrichissent le contexte pour la generation de dossiers de subvention plus precis et pertinents.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Superficie de la commune (hectares)
                </label>
                <input
                  type="number"
                  value={formData.village_area_hectares}
                  onChange={(e) => updateField('village_area_hectares', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                  placeholder="Ex: 1250"
                />
              </div>

              {/* Defis adresses */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Enjeux / Defis adresses par ce projet</h3>
                <div className="flex flex-wrap gap-2 mb-3">
                  {formData.challenges_addressed.map((challenge, index) => (
                    <span key={index} className="inline-flex items-center gap-1 px-3 py-1 bg-teal-100 text-teal-800 rounded-full text-sm">
                      {challenge}
                      <button
                        onClick={() => removeFromArray('challenges_addressed', index)}
                        className="text-teal-500 hover:text-teal-700 ml-1"
                      >
                        x
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2">
                  {CHALLENGE_OPTIONS.filter(c => !formData.challenges_addressed.includes(c)).map(challenge => (
                    <button
                      key={challenge}
                      onClick={() => addToArray('challenges_addressed', challenge)}
                      className="px-3 py-1 border border-gray-300 rounded-full text-sm text-gray-600 hover:bg-gray-100 hover:border-gray-400"
                    >
                      + {challenge}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Projets similaires realises dans la commune
                </label>
                <textarea
                  value={formData.past_similar_projects}
                  onChange={(e) => updateField('past_similar_projects', e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={3}
                  placeholder="Ex: Renovation de la salle des fetes en 2019 (45 000 euros, subvention DETR a 40%)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ressources disponibles (equipements, locaux, benevoles...)
                </label>
                <textarea
                  value={formData.available_resources}
                  onChange={(e) => updateField('available_resources', e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={3}
                  placeholder="Ex: Local technique municipal, equipe technique de 2 agents, association de benevoles (15 membres actifs)"
                />
              </div>
            </div>
          )}
        </div>

        {/* Pied de page */}
        <div className="bg-gray-50 border-t p-4 flex justify-end items-center gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition"
          >
            Annuler
          </button>
          <button
            onClick={handleCreate}
            disabled={saving || !formData.title.trim()}
            className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition disabled:opacity-50 font-medium"
          >
            {saving ? 'Creation...' : 'Creer le projet'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProjectKanban;
