// frontend/src/pages/admin/ProjectKanbanPage.jsx
/**
 * Phase E: Tableau de bord de gestion de projets
 *
 * Affiche un tableau Kanban pour gérer les projets du village.
 * Accessible via la route /dashboard/projects.
 */

import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { ProjectKanban } from '../../components/dashboard/ProjectKanban';

export function ProjectKanbanPage() {
  const { user } = useAuth();
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Récupérer le slug du village associé à l'utilisateur
  // Utiliser 'chirac' par défaut pour les tests si aucun village n'est défini
  const villageSlug = user?.village?.slug || user?.villageSlug || 'chirac';

  return (
    <div className="p-6">
      {/* En-tête de page */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Gestion de Projets
          </h1>
          <p className="text-gray-600 mt-2">
            Suivez et gérez vos projets villageois par glisser-déposer
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition shadow-sm"
        >
          <span className="text-xl leading-none">+</span>
          <span className="font-medium">Nouveau Projet</span>
        </button>
      </div>

      {/* Tableau Kanban */}
      <ProjectKanban
        villageSlug={villageSlug}
        showCreateModal={showCreateModal}
        onCloseCreateModal={() => setShowCreateModal(false)}
      />
    </div>
  );
}

export default ProjectKanbanPage;
