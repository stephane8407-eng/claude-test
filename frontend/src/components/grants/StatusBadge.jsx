/**
 * StatusBadge Component
 * Displays colored status badges for grant applications
 */

import React from 'react';

const STATUS_CONFIG = {
  researching: {
    label: 'Researching',
    emoji: '🔍',
    className: 'status-researching'
  },
  draft: {
    label: 'Draft',
    emoji: '📝',
    className: 'status-preparing'
  },
  preparing: {
    label: 'Preparing',
    emoji: '📝',
    className: 'status-preparing'
  },
  submitted: {
    label: 'Submitted',
    emoji: '📤',
    className: 'status-submitted'
  },
  under_review: {
    label: 'Under Review',
    emoji: '🔍',
    className: 'status-under_review'
  },
  approved: {
    label: 'Approved',
    emoji: '✅',
    className: 'status-approved'
  },
  rejected: {
    label: 'Rejected',
    emoji: '❌',
    className: 'status-rejected'
  },
  abandoned: {
    label: 'Abandoned',
    emoji: '🗑️',
    className: 'status-abandoned'
  }
};

const DEADLINE_CONFIG = {
  rolling: {
    label: 'Rolling',
    className: 'grant-badge-rolling'
  },
  annual: {
    label: 'Annual',
    className: 'grant-badge-annual'
  },
  deadline: {
    label: 'Deadline',
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
        ✓ Eligible
      </span>
    );
  }
  return (
    <span className="grant-badge grant-badge-check">
      Check eligibility
    </span>
  );
}

export function DeadlineBadge({ deadlineType, deadlineDate }) {
  if (deadlineType === 'rolling') {
    return (
      <span className="grant-badge grant-badge-rolling">
        Rolling applications
      </span>
    );
  }

  if (deadlineType === 'annual') {
    return (
      <span className="grant-badge grant-badge-annual">
        Annual deadline
      </span>
    );
  }

  if (deadlineDate) {
    const date = new Date(deadlineDate);
    const formatted = date.toLocaleDateString('en-GB', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
    return (
      <span className="grant-badge grant-badge-deadline">
        Deadline: {formatted}
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
