/**
 * StatusBadge Component
 * Displays colored status badges for grant applications
 */

import React from 'react';

const STATUS_CONFIG = {
  researching: {
    label: 'Recherche',
    emoji: '🔍',
    className: 'status-researching'
  },
  draft: {
    label: 'Brouillon',
    emoji: '📝',
    className: 'status-preparing'
  },
  preparing: {
    label: 'Préparation',
    emoji: '📝',
    className: 'status-preparing'
  },
  submitted: {
    label: 'Soumis',
    emoji: '📤',
    className: 'status-submitted'
  },
  under_review: {
    label: 'En cours d\'examen',
    emoji: '🔍',
    className: 'status-under_review'
  },
  approved: {
    label: 'Approuvé',
    emoji: '✅',
    className: 'status-approved'
  },
  rejected: {
    label: 'Refusé',
    emoji: '❌',
    className: 'status-rejected'
  },
  abandoned: {
    label: 'Abandonné',
    emoji: '🗑️',
    className: 'status-abandoned'
  }
};

const DEADLINE_CONFIG = {
  rolling: {
    label: 'Continu',
    className: 'grant-badge-rolling'
  },
  annual: {
    label: 'Annuel',
    className: 'grant-badge-annual'
  },
  deadline: {
    label: 'Date limite',
    className: 'grant-badge-deadline'
  }
};

export function StatusBadge({ status, showEmoji = true }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.researching;

  return (
    <span className={`grant-badge ${config.className}`}>
      {showEmoji && <span>{config.emoji}</span>}
      {config.label}
    </span>
  );
}

export function EligibilityBadge({ eligible }) {
  if (eligible) {
    return (
      <span className="grant-badge grant-badge-eligible">
        ✓ Éligible
      </span>
    );
  }
  return (
    <span className="grant-badge grant-badge-check">
      Vérifier l'éligibilité
    </span>
  );
}

export function DeadlineBadge({ deadlineType, deadlineDate }) {
  if (deadlineType === 'rolling') {
    return (
      <span className="grant-badge grant-badge-rolling">
        Candidature continue
      </span>
    );
  }

  if (deadlineType === 'annual') {
    return (
      <span className="grant-badge grant-badge-annual">
        Date limite annuelle
      </span>
    );
  }

  if (deadlineDate) {
    const date = new Date(deadlineDate);
    const formatted = date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
    return (
      <span className="grant-badge grant-badge-deadline">
        Date limite : {formatted}
      </span>
    );
  }

  return null;
}

export function ProgramTypeBadge({ type }) {
  const icons = {
    eu: '🌿',
    national: '🏛️',
    regional: '🗺️',
    foundation: '🏛️',
    grant: '💶'
  };

  const icon = icons[type?.toLowerCase()] || '💶';

  return (
    <span className="grant-program-icon">{icon}</span>
  );
}

export default StatusBadge;
