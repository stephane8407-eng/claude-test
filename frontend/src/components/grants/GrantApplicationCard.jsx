/**
 * GrantApplicationCard Component
 * Displays a single grant application in a card format
 */

import React from 'react';
import { StatusBadge } from './StatusBadge';
import './grants.css';

function getProgramIcon(application) {
  // Support both flat (from API) and nested (legacy) formats
  const org = (application.program_organization || application.funding_program?.organization || '').toLowerCase();

  if (org.includes('europ') || org.includes('commission')) return '🌿';
  if (org.includes('ministère') || org.includes('état')) return '🏛️';
  if (org.includes('région')) return '🗺️';
  if (org.includes('fondation')) return '🏛️';
  return '💶';
}

function formatAmount(min, max) {
  const formatNum = (n) => {
    if (!n) return null;
    if (n >= 1000000) return `€${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `€${Math.round(n / 1000)}K`;
    return `€${n}`;
  };

  const minStr = formatNum(min);
  const maxStr = formatNum(max);

  if (minStr && maxStr) return `${minStr} - ${maxStr}`;
  if (maxStr) return `Jusqu'à ${maxStr}`;
  if (minStr) return `À partir de ${minStr}`;
  return null;
}

function formatDate(dateString) {
  if (!dateString) return null;
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
}

export default function GrantApplicationCard({
  application,
  onViewDetails,
  onUpdateStatus
}) {
  // Support both flat (from API) and nested (legacy) formats
  const program = application.funding_program || {};
  const programName = application.program_name || program.name || 'Programme inconnu';
  const amountStr = formatAmount(program.amount_min, program.amount_max);
  const percentageStr = program.funding_percentage_max
    ? `Jusqu'à ${program.funding_percentage_max}%`
    : null;

  // Calculate expected decision date for submitted applications
  const getExpectedDecision = () => {
    if (application.status !== 'submitted' || !application.submitted_date) return null;
    const submittedDate = new Date(application.submitted_date);
    const monthsToAdd = program.typical_timeline_months || 6;
    submittedDate.setMonth(submittedDate.getMonth() + monthsToAdd);
    return submittedDate.toLocaleDateString('fr-FR', {
      month: 'short',
      year: 'numeric'
    });
  };

  // Calculate document progress
  const getDocumentProgress = () => {
    const required = program.required_documents?.length || 4;
    const completed = application.documents?.length || 0;
    return { completed, required };
  };

  const expectedDecision = getExpectedDecision();
  const docProgress = getDocumentProgress();

  return (
    <div className="grant-application-card">
      <div className="grant-application-header">
        <div className="grant-application-program">
          <span style={{ fontSize: '20px' }}>{getProgramIcon(application)}</span>
          <div>
            <h4>{programName}</h4>
            {amountStr && (
              <div className="grant-application-amount">
                {amountStr}
                {percentageStr && ` | ${percentageStr}`}
              </div>
            )}
          </div>
        </div>
        <StatusBadge status={application.status} />
      </div>

      <div className="grant-application-meta">
        {/* Status-specific info */}
        {application.status === 'submitted' && (
          <>
            {application.submitted_date && (
              <div className="grant-application-meta-item">
                📤 Soumis le : {formatDate(application.submitted_date)}
              </div>
            )}
            {expectedDecision && (
              <div className="grant-application-meta-item">
                🗓️ Décision attendue : {expectedDecision}
              </div>
            )}
          </>
        )}

        {application.status === 'preparing' && (
          <>
            {program.deadline_date && (
              <div className="grant-application-meta-item">
                ⏰ Prochaine date limite : {formatDate(program.deadline_date)}
              </div>
            )}
            <div className="grant-application-meta-item">
              📎 Documents : {docProgress.completed}/{docProgress.required} complétés
            </div>
          </>
        )}

        {(application.status === 'draft' || application.status === 'researching') && (
          <div className="grant-application-meta-item">
            🕐 Commencé le : {formatDate(application.created_at)}
          </div>
        )}

        {application.status === 'approved' && application.amount_approved && (
          <div className="grant-application-meta-item" style={{ color: '#059669', fontWeight: 500 }}>
            ✅ Approuvé : {application.amount_approved.toLocaleString()} €
          </div>
        )}

        {application.status === 'rejected' && application.decision_notes && (
          <div className="grant-application-meta-item">
            📝 Motif : {application.decision_notes}
          </div>
        )}
      </div>

      {/* Notes preview */}
      {application.notes && (
        <div style={{
          fontSize: '14px',
          color: '#6B7280',
          marginBottom: '16px',
          padding: '12px',
          background: '#F5F5F5',
          borderRadius: '8px',
          lineHeight: 1.5
        }}>
          {application.notes.length > 150
            ? `${application.notes.substring(0, 150)}...`
            : application.notes}
        </div>
      )}

      <div className="grant-application-actions">
        {onViewDetails && (
          <button
            className="grant-btn grant-btn-secondary grant-btn-small"
            onClick={() => onViewDetails(application)}
          >
            Voir les détails
          </button>
        )}
        {onUpdateStatus && (
          <button
            className="grant-btn grant-btn-ghost grant-btn-small"
            onClick={() => onUpdateStatus(application)}
          >
            Modifier le statut
          </button>
        )}
      </div>
    </div>
  );
}
