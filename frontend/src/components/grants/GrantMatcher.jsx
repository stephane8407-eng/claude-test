/**
 * GrantMatcher Modal Component
 * Shows funding programs that match a project
 *
 * Trigger: "Explore Funding Options" button on project card
 * API: POST /api/grants/projects/{project_id}/match
 */

import React, { useState, useEffect, useCallback } from 'react';
import { EligibilityBadge, DeadlineBadge, ProgramTypeBadge } from './StatusBadge';
import GrantProgramDetail from './GrantProgramDetail';
import GrantApplicationForm from './GrantApplicationForm';
import './grants.css';

const PROGRAM_ICONS = {
  eu: '🌿',
  european: '🌿',
  national: '🏛️',
  regional: '🗺️',
  foundation: '🏛️',
  local: '🏘️'
};

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

function formatAmount(min, max) {
  const formatNum = (n) => {
    if (n >= 1000000) return `€${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `€${Math.round(n / 1000)}K`;
    return `€${n}`;
  };

  if (min && max) {
    return `${formatNum(min)} - ${formatNum(max)}`;
  }
  if (max) return `Up to ${formatNum(max)}`;
  if (min) return `From ${formatNum(min)}`;
  return 'Amount varies';
}

function formatPercentage(min, max) {
  if (min && max && min !== max) {
    return `${min}% - ${max}%`;
  }
  if (max) return `Up to ${max}%`;
  if (min) return `${min}%+`;
  return null;
}

export default function GrantMatcher({
  project,
  isOpen,
  onClose,
  onApplicationCreated
}) {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('best');
  const [showAll, setShowAll] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [applicationProgram, setApplicationProgram] = useState(null);

  // Fetch matching programs
  useEffect(() => {
    if (isOpen && project?.id) {
      fetchMatches();
    }
  }, [isOpen, project?.id]);

  const fetchMatches = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/grants/projects/${project.id}/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          village_population: project.village_population || project.project_data?.village_population || 5000,
          village_region: project.village_region || project.project_data?.village_region || null,
          limit: 20,
          min_score: 0
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch matching programs');
      }

      const data = await response.json();
      setMatches(data.matches || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching grant matches:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle keyboard escape
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        if (applicationProgram) {
          setApplicationProgram(null);
        } else if (selectedProgram) {
          setSelectedProgram(null);
        } else {
          onClose();
        }
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, selectedProgram, applicationProgram, onClose]);

  // Filter and sort programs
  const filteredPrograms = matches
    .filter(program => {
      if (filter === 'all') return true;
      const org = (program.organization || '').toLowerCase();
      const level = (program.level || '').toLowerCase();

      switch (filter) {
        case 'eu':
          return org.includes('europ') || org.includes('commission') || level === 'eu';
        case 'national':
          return org.includes('ministère') || org.includes('état') || level === 'national';
        case 'regional':
          return org.includes('région') || level === 'regional';
        default:
          return true;
      }
    })
    .sort((a, b) => {
      switch (sort) {
        case 'amount':
          return (b.amount_max || 0) - (a.amount_max || 0);
        case 'deadline':
          if (!a.deadline_date && !b.deadline_date) return 0;
          if (!a.deadline_date) return 1;
          if (!b.deadline_date) return -1;
          return new Date(a.deadline_date) - new Date(b.deadline_date);
        case 'alpha':
          return (a.name || '').localeCompare(b.name || '');
        case 'best':
        default:
          // Sort by score, then by funding percentage
          const scoreA = a.score || 0;
          const scoreB = b.score || 0;
          if (scoreA !== scoreB) return scoreB - scoreA;
          return (b.funding_percentage_max || 0) - (a.funding_percentage_max || 0);
      }
    });

  const displayedPrograms = showAll ? filteredPrograms : filteredPrograms.slice(0, 5);
  const hasMore = filteredPrograms.length > 5;

  if (!isOpen) return null;

  const projectTitle = project?.project_data?.title || 'Untitled Project';

  return (
    <>
      <div
        className="grant-modal-overlay"
        onClick={onClose}
        role="dialog"
        aria-modal="true"
        aria-labelledby="grant-matcher-title"
      >
        <div
          className="grant-modal"
          onClick={e => e.stopPropagation()}
        >
          {/* Header */}
          <div className="grant-modal-header">
            <h2 id="grant-matcher-title">
              💰 Funding Opportunities
            </h2>
            <p className="subtitle">{projectTitle}</p>
            <button
              className="grant-modal-close"
              onClick={onClose}
              aria-label="Close modal"
            >
              ×
            </button>
          </div>

          {/* Content */}
          <div className="grant-modal-content">
            {loading ? (
              <div className="grant-loading">
                <div className="grant-loading-spinner" />
                Finding matching programs...
              </div>
            ) : error ? (
              <div className="grant-empty-state">
                <div className="grant-empty-state-icon">⚠️</div>
                <h4>Unable to load programs</h4>
                <p>{error}</p>
                <button className="grant-btn grant-btn-primary" onClick={fetchMatches}>
                  Try Again
                </button>
              </div>
            ) : filteredPrograms.length === 0 ? (
              <div className="grant-empty-state">
                <div className="grant-empty-state-icon">🔍</div>
                <h4>No matching programs found</h4>
                <p>
                  {filter !== 'all'
                    ? 'Try changing your filter to see more programs.'
                    : "We're continuously adding new programs. Check back soon!"}
                </p>
                {filter !== 'all' && (
                  <button
                    className="grant-btn grant-btn-secondary"
                    onClick={() => setFilter('all')}
                  >
                    Show All Programs
                  </button>
                )}
              </div>
            ) : (
              <>
                {/* Match count and filters */}
                <div className="grant-match-count">
                  <span>✨ {filteredPrograms.length}</span> programs may help fund your project
                </div>

                <div className="grant-filters">
                  <select
                    className="grant-select"
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    aria-label="Filter programs"
                  >
                    <option value="all">All Programs</option>
                    <option value="eu">EU Programs</option>
                    <option value="national">National Programs</option>
                    <option value="regional">Regional Programs</option>
                  </select>

                  <select
                    className="grant-select"
                    value={sort}
                    onChange={(e) => setSort(e.target.value)}
                    aria-label="Sort programs"
                  >
                    <option value="best">Best Match</option>
                    <option value="amount">Highest Amount</option>
                    <option value="deadline">Deadline Soon</option>
                    <option value="alpha">Alphabetical</option>
                  </select>
                </div>

                {/* Program list */}
                <div className="grant-programs-list">
                  {displayedPrograms.map(program => (
                    <div
                      key={program.program_id}
                      className="grant-program-card"
                    >
                      <div className="grant-program-card-header">
                        <span className="grant-program-icon">
                          {getProgramIcon(program)}
                        </span>
                        <div className="grant-program-title">
                          <h3>{program.name}</h3>
                          <p className="organization">{program.organization}</p>
                        </div>
                      </div>

                      <div className="grant-program-details">
                        <span className="grant-program-amount">
                          {formatAmount(program.amount_min, program.amount_max)}
                        </span>
                        {formatPercentage(program.funding_percentage_min, program.funding_percentage_max) && (
                          <span className="grant-program-percentage">
                            | {formatPercentage(program.funding_percentage_min, program.funding_percentage_max)}
                          </span>
                        )}
                      </div>

                      <div className="grant-program-badges">
                        <EligibilityBadge eligible={program.score >= 80} />
                        <DeadlineBadge
                          deadlineType={program.deadline_type}
                          deadlineDate={program.deadline_date}
                        />
                      </div>

                      <div className="grant-program-actions">
                        <button
                          className="grant-btn grant-btn-secondary grant-btn-small"
                          onClick={() => setSelectedProgram(program)}
                        >
                          Learn More
                        </button>
                        <button
                          className="grant-btn grant-btn-primary grant-btn-small"
                          onClick={() => setApplicationProgram(program)}
                        >
                          Start Application
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Show more button */}
                {hasMore && !showAll && (
                  <div style={{ textAlign: 'center', marginTop: '24px' }}>
                    <button
                      className="grant-btn grant-btn-ghost"
                      onClick={() => setShowAll(true)}
                    >
                      Show {filteredPrograms.length - 5} more programs...
                    </button>
                  </div>
                )}

                {showAll && hasMore && (
                  <div style={{ textAlign: 'center', marginTop: '24px' }}>
                    <button
                      className="grant-btn grant-btn-ghost"
                      onClick={() => setShowAll(false)}
                    >
                      Show less
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Program Detail Drawer */}
      {selectedProgram && (
        <GrantProgramDetail
          program={selectedProgram}
          project={project}
          onClose={() => setSelectedProgram(null)}
          onStartApplication={() => {
            setApplicationProgram(selectedProgram);
            setSelectedProgram(null);
          }}
        />
      )}

      {/* Application Form Modal */}
      {applicationProgram && (
        <GrantApplicationForm
          project={project}
          program={applicationProgram}
          onClose={() => setApplicationProgram(null)}
          onSuccess={() => {
            setApplicationProgram(null);
            if (onApplicationCreated) {
              onApplicationCreated();
            }
          }}
        />
      )}
    </>
  );
}
