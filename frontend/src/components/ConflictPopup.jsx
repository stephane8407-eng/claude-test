import React, { useState } from 'react';
import './ConflictPopup.css';

const ConflictPopup = ({ conflict }) => {
  const [showImpact, setShowImpact] = useState(false);

  if (!conflict) return null;

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Date unknown';
    return dateStr;
  };

  const getParticipantsByCategory = (participants) => {
    if (!participants || participants.length === 0) return null;

    const grouped = participants.reduce((acc, p) => {
      if (!acc[p.side]) {
        acc[p.side] = [];
      }
      acc[p.side].push(p);
      return acc;
    }, {});

    return grouped;
  };

  const formatCasualties = (casualties) => {
    if (!casualties) return 'Unknown';
    if (typeof casualties === 'string') return casualties;

    const parts = [];
    if (casualties.side1 && casualties.side1 !== 'unknown') {
      parts.push(`Side 1: ${casualties.side1}`);
    }
    if (casualties.side2 && casualties.side2 !== 'unknown') {
      parts.push(`Side 2: ${casualties.side2}`);
    }
    if (casualties.civilians && casualties.civilians !== 'unknown') {
      parts.push(`Civilians: ${casualties.civilians}`);
    }

    return parts.length > 0 ? parts.join(', ') : 'Unknown';
  };

  const participantsByCategory = getParticipantsByCategory(conflict.participants);

  const impactCategories = [
    { key: 'infrastructure', icon: '🏗️', label: 'Infrastructure' },
    { key: 'economy', icon: '💰', label: 'Economy' },
    { key: 'identity', icon: '🎭', label: 'Identity' },
    { key: 'demographics', icon: '👥', label: 'Demographics' },
    { key: 'governance', icon: '🏛️', label: 'Governance' },
    { key: 'tourism', icon: '🏛️', label: 'Tourism' }
  ];

  return (
    <div className="conflict-popup">
      <div className="popup-header">
        <h3>{conflict.name}</h3>
        <span className="conflict-badge">{conflict.conflict_type}</span>
      </div>

      <div className="popup-details">
        <div className="detail-row">
          <span className="label">📅 Date:</span>
          <span className="value">{formatDate(conflict.date_str || conflict.date)}</span>
        </div>

        <div className="detail-row">
          <span className="label">📍 Location:</span>
          <span className="value">{conflict.location}</span>
        </div>

        <div className="detail-row">
          <span className="label">⏳ Period:</span>
          <span className="value">{conflict.period ? conflict.period.toUpperCase() : 'Unknown'}</span>
        </div>

        {conflict.duration && (
          <div className="detail-row">
            <span className="label">⏱️ Duration:</span>
            <span className="value">{conflict.duration}</span>
          </div>
        )}

        {conflict.outcome && (
          <div className="detail-row outcome">
            <span className="label">🎯 Outcome:</span>
            <span className="value">{conflict.outcome}</span>
          </div>
        )}

        {conflict.casualties && (
          <div className="detail-row">
            <span className="label">💔 Casualties:</span>
            <span className="value">{formatCasualties(conflict.casualties)}</span>
          </div>
        )}

        {participantsByCategory && (
          <div className="participants-section">
            <div className="label">⚔️ Participants:</div>
            {Object.entries(participantsByCategory).map(([side, participants]) => (
              <div key={side} className="participant-group">
                <div className="participant-side">{side}:</div>
                <ul className="participant-list">
                  {participants.map((p, idx) => (
                    <li key={idx}>
                      <strong>{p.name}</strong> ({p.role})
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}

        {conflict.confidence_score && (
          <div className="detail-row confidence">
            <span className="label">✓ Confidence:</span>
            <span className="value">
              {conflict.confidence_score}/100
              <div className="confidence-bar">
                <div
                  className="confidence-fill"
                  style={{ width: `${conflict.confidence_score}%` }}
                />
              </div>
            </span>
          </div>
        )}

        {/* Impact Today Framework Toggle */}
        {conflict.impact_today && (
          <div className="impact-section">
            <button
              className="impact-toggle"
              onClick={() => setShowImpact(!showImpact)}
            >
              {showImpact ? '▼' : '▶'} Impact Today Framework
            </button>

            {showImpact && (
              <div className="impact-categories">
                {impactCategories.map(({ key, icon, label }) => {
                  const impactText = conflict.impact_today?.[key];
                  if (!impactText) return null;

                  return (
                    <div key={key} className="impact-category">
                      <div className="impact-header">
                        <span className="impact-icon">{icon}</span>
                        <span className="impact-label">{label}</span>
                      </div>
                      <div className="impact-text">{impactText}</div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {conflict.sources && conflict.sources.length > 0 && (
          <div className="sources-section">
            <div className="label">📚 Sources:</div>
            <ul className="sources-list">
              {conflict.sources.slice(0, 3).map((source, idx) => (
                <li key={idx}>{source}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConflictPopup;
