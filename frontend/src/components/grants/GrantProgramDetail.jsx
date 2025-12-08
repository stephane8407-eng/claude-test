/**
 * GrantProgramDetail Drawer Component
 * Shows detailed information about a funding program
 *
 * Trigger: "Learn More" on program card
 * Slides in from right
 */

import React, { useEffect } from 'react';
import './grants.css';

function getProgramIcon(program) {
  const orgLower = (program.organization || '').toLowerCase();
  const levelLower = (program.level || '').toLowerCase();

  if (orgLower.includes('europ') || orgLower.includes('commission') || levelLower === 'eu') {
    return '🌿';
  }
  if (orgLower.includes('ministère') || orgLower.includes('état') || levelLower === 'national') {
    return '🏛️';
  }
  if (orgLower.includes('région') || orgLower.includes('regional') || levelLower === 'regional') {
    return '🗺️';
  }
  if (orgLower.includes('fondation')) {
    return '🏛️';
  }
  return '💶';
}

function formatAmount(amount) {
  if (!amount) return null;
  if (amount >= 1000000) return `€${(amount / 1000000).toFixed(1)}M`;
  if (amount >= 1000) return `€${Math.round(amount / 1000).toLocaleString()}K`;
  return `€${amount.toLocaleString()}`;
}

function formatAmountRange(min, max) {
  const minStr = formatAmount(min);
  const maxStr = formatAmount(max);

  if (minStr && maxStr) return `${minStr} - ${maxStr}`;
  if (maxStr) return `Up to ${maxStr}`;
  if (minStr) return `From ${minStr}`;
  return 'Amount varies';
}

function formatPercentageRange(min, max) {
  if (min && max && min !== max) return `${min}% - ${max}%`;
  if (max) return `Up to ${max}%`;
  if (min) return `${min}%+`;
  return null;
}

function getProgramType(program) {
  const org = (program.organization || '').toLowerCase();
  if (org.includes('europ') || org.includes('commission')) return 'European Grant';
  if (org.includes('ministère') || org.includes('état')) return 'National Grant';
  if (org.includes('région')) return 'Regional Grant';
  if (org.includes('fondation')) return 'Foundation Grant';
  return program.program_type || 'Grant';
}

function getDeadlineText(program) {
  if (program.deadline_type === 'rolling') {
    return 'Rolling (apply anytime)';
  }
  if (program.deadline_type === 'annual') {
    return 'Annual deadline';
  }
  if (program.deadline_date || program.next_deadline) {
    const date = new Date(program.deadline_date || program.next_deadline);
    return date.toLocaleDateString('en-GB', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  }
  return 'Check with program';
}

export default function GrantProgramDetail({
  program,
  project,
  onClose,
  onStartApplication,
  onSaveForLater
}) {
  // Handle escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  // Mock eligibility data (in production, would come from API)
  const eligibilityCriteria = [
    {
      name: 'Population',
      description: program.eligible_population_bands?.[0] || '<10,000 habitants',
      met: true
    },
    {
      name: 'Region',
      description: program.eligible_regions?.[0] || 'All regions',
      met: true
    },
    {
      name: 'Themes',
      description: program.eligible_themes?.join(', ') || 'Heritage, Tourism, Rural Development',
      met: true
    },
    {
      name: 'Entity',
      description: 'Commune',
      met: true
    }
  ];

  const metCount = eligibilityCriteria.filter(c => c.met).length;
  const eligibilityPercentage = Math.round((metCount / eligibilityCriteria.length) * 100);

  // Parse requirements
  const requirements = program.requirements
    ? program.requirements.split('\n').filter(r => r.trim())
    : program.required_documents || [
        'Délibération conseil municipal',
        'Devis détaillés',
        'Plan de financement'
      ];

  // Tips
  const tips = program.tips || program.process_summary ||
    "Contact the program administrator early - they can guide you through the process. Multi-year projects often get higher funding percentages.";

  return (
    <>
      {/* Overlay */}
      <div
        className="grant-drawer-overlay"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer */}
      <div
        className="grant-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="program-detail-title"
      >
        {/* Header */}
        <div className="grant-drawer-header">
          <button
            className="grant-drawer-back"
            onClick={onClose}
          >
            ← Back to Matches
          </button>

          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <span style={{ fontSize: '32px', lineHeight: 1 }}>
              {getProgramIcon(program)}
            </span>
            <div>
              <h2 id="program-detail-title" style={{
                fontSize: '24px',
                fontWeight: 700,
                color: '#1F2937',
                margin: 0,
                lineHeight: 1.3
              }}>
                {program.name}
              </h2>
              <p style={{
                fontSize: '16px',
                color: '#6B7280',
                margin: '4px 0 0 0'
              }}>
                {program.organization}
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="grant-drawer-content">
          {/* Funding Details */}
          <div className="grant-drawer-section">
            <h3>💶 Funding Details</h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              <li style={{ padding: '8px 0', display: 'flex', alignItems: 'flex-start' }}>
                <span style={{ marginRight: '12px', color: '#008080' }}>•</span>
                <span>
                  <strong>Amount:</strong> {formatAmountRange(program.amount_min, program.amount_max)}
                </span>
              </li>
              {formatPercentageRange(program.funding_percentage_min, program.funding_percentage_max) && (
                <li style={{ padding: '8px 0', display: 'flex', alignItems: 'flex-start' }}>
                  <span style={{ marginRight: '12px', color: '#008080' }}>•</span>
                  <span>
                    <strong>Coverage:</strong> {formatPercentageRange(program.funding_percentage_min, program.funding_percentage_max)} of project cost
                  </span>
                </li>
              )}
              <li style={{ padding: '8px 0', display: 'flex', alignItems: 'flex-start' }}>
                <span style={{ marginRight: '12px', color: '#008080' }}>•</span>
                <span>
                  <strong>Type:</strong> {getProgramType(program)}
                </span>
              </li>
            </ul>
          </div>

          <div className="grant-drawer-divider" />

          {/* Eligibility */}
          <div className="grant-drawer-section">
            <h3>
              📋 Eligibility
              <span style={{
                fontSize: '14px',
                fontWeight: 400,
                marginLeft: '12px',
                color: eligibilityPercentage === 100 ? '#059669' : '#6B7280'
              }}>
                ({metCount}/{eligibilityCriteria.length} criteria {eligibilityPercentage === 100 ? '✅' : ''})
              </span>
            </h3>

            {/* Progress bar */}
            <div className="grant-eligibility-progress">
              <div className="grant-eligibility-bar">
                <div
                  className="grant-eligibility-bar-fill"
                  style={{ width: `${eligibilityPercentage}%` }}
                />
              </div>
              <span>{eligibilityPercentage}%</span>
            </div>

            {/* Criteria list */}
            {eligibilityCriteria.map((criterion, index) => (
              <div
                key={index}
                className={`grant-eligibility-item ${criterion.met ? 'met' : 'not-met'}`}
              >
                <span>{criterion.met ? '✅' : '❌'}</span>
                <span>
                  <strong>{criterion.name}:</strong> {criterion.description}
                </span>
              </div>
            ))}
          </div>

          <div className="grant-drawer-divider" />

          {/* Timeline */}
          <div className="grant-drawer-section">
            <h3>📅 Timeline</h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              <li style={{ padding: '8px 0', display: 'flex', alignItems: 'flex-start' }}>
                <span style={{ marginRight: '12px', color: '#008080' }}>•</span>
                <span>
                  <strong>Applications:</strong> {getDeadlineText(program)}
                </span>
              </li>
              {program.typical_timeline_months && (
                <li style={{ padding: '8px 0', display: 'flex', alignItems: 'flex-start' }}>
                  <span style={{ marginRight: '12px', color: '#008080' }}>•</span>
                  <span>
                    <strong>Decision time:</strong> {program.typical_timeline_months} months typically
                  </span>
                </li>
              )}
            </ul>
          </div>

          <div className="grant-drawer-divider" />

          {/* Requirements */}
          <div className="grant-drawer-section">
            <h3>📚 Requirements</h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {(Array.isArray(requirements) ? requirements : [requirements]).map((req, index) => (
                <li key={index} style={{ padding: '8px 0', display: 'flex', alignItems: 'flex-start' }}>
                  <span style={{ marginRight: '12px', color: '#008080' }}>•</span>
                  <span>{req}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="grant-drawer-divider" />

          {/* Tips */}
          <div className="grant-drawer-section">
            <h3>💡 Insider Tips</h3>
            <p>{tips}</p>
          </div>

          <div className="grant-drawer-divider" />

          {/* Links */}
          <div className="grant-drawer-section">
            <h3>🔗 Links</h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {program.website_url && (
                <li style={{ padding: '8px 0' }}>
                  <a
                    href={program.website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="grant-link"
                  >
                    Official site →
                  </a>
                </li>
              )}
              {program.application_url && (
                <li style={{ padding: '8px 0' }}>
                  <a
                    href={program.application_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="grant-link"
                  >
                    Application portal →
                  </a>
                </li>
              )}
              {!program.website_url && !program.application_url && (
                <li style={{ padding: '8px 0', color: '#6B7280' }}>
                  Links not available - check program name for official resources
                </li>
              )}
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="grant-drawer-footer">
          <button
            className="grant-btn grant-btn-primary"
            onClick={onStartApplication}
            style={{ flex: 1 }}
          >
            ✨ Start Application
          </button>
          {onSaveForLater && (
            <button
              className="grant-btn grant-btn-secondary"
              onClick={onSaveForLater}
            >
              📎 Save for Later
            </button>
          )}
        </div>
      </div>
    </>
  );
}
