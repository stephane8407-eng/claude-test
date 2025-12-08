// frontend/src/components/ProjectKanban.jsx
/**
 * Phase E: Project Management Kanban Board
 *
 * Displays village projects in 5 columns:
 * Exploring | Planning | In Progress | Completed | Abandoned
 *
 * Features:
 * - Drag and drop between columns
 * - Project cards with key info
 * - Click card to see details
 * - Color-coded by priority
 * - Grant application tracking (Phase E Week 2)
 */

import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { GrantMatcher, GrantApplicationList } from '../grants';
import '../grants/grants.css';
import './ProjectKanban.css';

const STATUS_COLUMNS = [
  { id: 'exploring', title: 'Exploring', emoji: '🔍', color: 'bg-gray-100' },
  { id: 'planning', title: 'Planning', emoji: '📋', color: 'bg-blue-100' },
  { id: 'in_progress', title: 'In Progress', emoji: '🚧', color: 'bg-yellow-100' },
  { id: 'completed', title: 'Completed', emoji: '✅', color: 'bg-green-100' },
  { id: 'abandoned', title: 'Abandoned', emoji: '🗑️', color: 'bg-red-100' }
];

const PRIORITY_COLORS = {
  1: 'border-gray-300 bg-white',
  2: 'border-blue-300 bg-blue-50',
  3: 'border-yellow-300 bg-yellow-50',
  4: 'border-orange-300 bg-orange-50',
  5: 'border-red-300 bg-red-50'
};

const PRIORITY_LABELS = {
  1: 'Low',
  2: 'Medium-Low',
  3: 'Medium',
  4: 'Medium-High',
  5: 'High'
};

export default function ProjectKanban({ villageSlug }) {
  const [projects, setProjects] = useState([]);
  const [byStatus, setByStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState(null);
  const [grantMatcherProject, setGrantMatcherProject] = useState(null);

  // Load projects on mount
  useEffect(() => {
    loadProjects();
  }, [villageSlug]);

  const loadProjects = async () => {
    try {
      const response = await fetch(`/api/villages/${villageSlug}/projects`);
      const data = await response.json();

      setProjects(data.projects);
      setByStatus(data.by_status);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load projects:', error);
      setLoading(false);
    }
  };

  // Handle drag and drop
  const onDragEnd = async (result) => {
    const { source, destination, draggableId } = result;

    // Dropped outside a column
    if (!destination) return;

    // No status change
    if (source.droppableId === destination.droppableId) return;

    const newStatus = destination.droppableId;
    const projectId = parseInt(draggableId);

    // Optimistically update UI
    const updatedProjects = projects.map(p =>
      p.id === projectId ? { ...p, status: newStatus } : p
    );
    setProjects(updatedProjects);

    // Update grouped view
    const newByStatus = { ...byStatus };
    const project = byStatus[source.droppableId].find(p => p.id === projectId);
    newByStatus[source.droppableId] = newByStatus[source.droppableId].filter(p => p.id !== projectId);
    newByStatus[destination.droppableId] = [...newByStatus[destination.droppableId], { ...project, status: newStatus }];
    setByStatus(newByStatus);

    // API call to persist change
    try {
      await fetch(`/api/villages/${villageSlug}/projects/${projectId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
    } catch (error) {
      console.error('Failed to update project status:', error);
      // Reload to revert optimistic update
      loadProjects();
    }
  };

  // Open grant matcher for a project
  const openGrantMatcher = (project, e) => {
    e.stopPropagation();
    setGrantMatcherProject(project);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading projects...</div>
      </div>
    );
  }

  return (
    <div className="w-full h-full">
      <DragDropContext onDragEnd={onDragEnd}>
        <div className="kanban-board">
          {STATUS_COLUMNS.map(column => (
            <div
              key={column.id}
              className={`kanban-column ${column.id === 'in_progress' ? 'in-progress' : column.id}`}
            >
              {/* Column Header */}
              <div className="column-header">
                <span className="column-title">
                  {column.emoji} {column.title}
                </span>
                <span className="column-count">
                  {byStatus[column.id]?.length || 0}
                </span>
              </div>

              {/* Droppable Column */}
              <Droppable droppableId={column.id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    style={{
                      minHeight: '400px',
                      background: snapshot.isDraggingOver ? 'rgba(0, 128, 128, 0.05)' : 'transparent',
                      borderRadius: '8px',
                      transition: 'background 0.2s ease'
                    }}
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
                            className="project-card"
                            style={{
                              ...provided.draggableProps.style,
                              opacity: snapshot.isDragging ? 0.8 : 1
                            }}
                          >
                            {/* Project Title */}
                            <h4 className="project-card-title">
                              {project.project_data.title}
                            </h4>

                            {/* Badges */}
                            <div className="project-badges">
                              {/* Priority Badge */}
                              <span className={`priority-badge ${
                                project.priority >= 4 ? 'priority-high' :
                                project.priority >= 3 ? 'priority-medium' :
                                'priority-low'
                              }`}>
                                {PRIORITY_LABELS[project.priority]}
                              </span>

                              {/* Tier badge */}
                              <span className={`tier-badge ${
                                project.project_data.tier === 'breakthrough' ? 'tier-breakthrough' :
                                project.project_data.tier === 'innovation' ? 'tier-innovation' :
                                'tier-proven'
                              }`}>
                                {project.project_data.tier}
                              </span>
                            </div>

                            {/* Meta Info */}
                            <div className="project-meta">
                              <div className="meta-row">
                                💰 €{project.budget_estimated_min?.toLocaleString()} - €{project.budget_estimated_max?.toLocaleString()}
                              </div>
                              <div className="meta-row">
                                ⏱️ {project.timeline_months} months
                              </div>
                            </div>

                            {/* Grant Applications Badge */}
                            {project.grant_applications_count > 0 ? (
                              <div className="project-grant-badge" style={{ marginBottom: '12px' }}>
                                💰 {project.grant_applications_count} Grant{project.grant_applications_count > 1 ? 's' : ''}
                                {project.has_approved_grant && <span style={{ marginLeft: '6px', color: '#10B981' }}>✓</span>}
                              </div>
                            ) : (
                              <div className="project-grant-badge no-grants" style={{ marginBottom: '12px' }}>
                                💰 No grants yet
                              </div>
                            )}

                            {/* Explore Funding Button */}
                            <button
                              onClick={(e) => openGrantMatcher(project, e)}
                              className="explore-funding-btn"
                            >
                              Explore Funding
                            </button>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}

                    {/* Empty state */}
                    {(!byStatus[column.id] || byStatus[column.id].length === 0) && (
                      <div className="column-empty-state">
                        <p>No projects in {column.title.toLowerCase()}</p>
                      </div>
                    )}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>

      {/* Project Detail Modal */}
      {selectedProject && (
        <ProjectDetailModal
          project={selectedProject}
          villageSlug={villageSlug}
          onClose={() => setSelectedProject(null)}
          onUpdate={loadProjects}
          onOpenGrantMatcher={() => {
            setGrantMatcherProject(selectedProject);
          }}
        />
      )}

      {/* Grant Matcher Modal */}
      {grantMatcherProject && (
        <GrantMatcher
          project={grantMatcherProject}
          isOpen={!!grantMatcherProject}
          onClose={() => setGrantMatcherProject(null)}
          onApplicationCreated={() => {
            loadProjects();
          }}
        />
      )}
    </div>
  );
}

// ============================================
// PROJECT DETAIL MODAL WITH GRANTS TAB
// ============================================

function ProjectDetailModal({ project, villageSlug, onClose, onUpdate, onOpenGrantMatcher }) {
  const [notes, setNotes] = useState(project.notes || '');
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('details');
  const [grantCount, setGrantCount] = useState(project.grant_applications_count || 0);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch(`/api/villages/${villageSlug}/projects/${project.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes })
      });
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to save project:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div
        className="project-detail-modal w-full overflow-y-auto"
        style={{
          maxWidth: '900px',
          height: '85vh',
          maxHeight: '85vh'
        }}
      >
        {/* Header */}
        <div className="panel-header sticky top-0 bg-white z-10">
          <h2 className="panel-title">
            {project.project_data.title}
          </h2>
          <div className="panel-status-badges">
            <span className="panel-status-badge status">
              {project.status === 'in_progress' ? 'In Progress' :
               project.status.charAt(0).toUpperCase() + project.status.slice(1)}
            </span>
            <span className="panel-status-badge tier">
              {project.project_data.tier}
            </span>
          </div>
          <button
            onClick={onClose}
            className="panel-close-btn"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        <div className="panel-tabs">
          <button
            className={`panel-tab ${activeTab === 'details' ? 'active' : ''}`}
            onClick={() => setActiveTab('details')}
          >
            Details
          </button>
          <button
            className={`panel-tab ${activeTab === 'media' ? 'active' : ''}`}
            onClick={() => setActiveTab('media')}
          >
            Media
          </button>
          <button
            className={`panel-tab ${activeTab === 'grants' ? 'active' : ''}`}
            onClick={() => setActiveTab('grants')}
          >
            Grants {grantCount > 0 && <span className="tab-badge">{grantCount}</span>}
          </button>
        </div>

        {/* Content */}
        <div className="panel-content">
          {activeTab === 'details' && (
            <div>
              {/* Description */}
              <div className="detail-section">
                <div className="detail-label">Description</div>
                <div className="detail-value description">{project.project_data.description}</div>
              </div>

              {/* Key Details Grid */}
              <div className="details-grid">
                <div className="detail-section">
                  <div className="detail-label">Budget</div>
                  <div className="budget-display">
                    💰 €{project.budget_estimated_min?.toLocaleString()} - €{project.budget_estimated_max?.toLocaleString()}
                  </div>
                </div>
                <div className="detail-section">
                  <div className="detail-label">Timeline</div>
                  <div className="timeline-display">
                    ⏱️ {project.timeline_months} months
                  </div>
                </div>
                <div className="detail-section">
                  <div className="detail-label">Difficulty</div>
                  <div className="detail-value">{project.project_data.difficulty}</div>
                </div>
                <div className="detail-section">
                  <div className="detail-label">Priority</div>
                  <div className={`priority-display ${
                    project.priority === 5 ? 'high' :
                    project.priority === 4 ? 'medium-high' :
                    project.priority === 3 ? 'medium' :
                    project.priority === 2 ? 'medium-low' : 'low'
                  }`}>
                    ⭐ {PRIORITY_LABELS[project.priority]}
                  </div>
                </div>
              </div>

              {/* Inspired By */}
              {project.project_data.inspired_by && (
                <div className="detail-section">
                  <div className="detail-label">Inspired By</div>
                  <div className="detail-value">🏆 {project.project_data.inspired_by}</div>
                </div>
              )}

              {/* Funding Sources */}
              {project.project_data.funding_sources && project.project_data.funding_sources.length > 0 && (
                <div className="detail-section">
                  <div className="detail-label">Suggested Funding Sources</div>
                  <div className="detail-value">
                    <ul style={{ listStyle: 'disc', paddingLeft: '20px' }}>
                      {project.project_data.funding_sources.map((source, i) => (
                        <li key={i}>{source}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Next Steps */}
              {project.next_steps && project.next_steps.length > 0 && (
                <div className="detail-section">
                  <div className="detail-label">Next Steps</div>
                  <div className="detail-value">
                    {project.next_steps.map((step, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', marginBottom: '8px' }}>
                        <span style={{ color: '#008080', fontWeight: '600' }}>→</span>
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Mayor's Notes */}
              <div className="mayors-notes">
                <span className="mayors-notes-label">Mayor's Notes</span>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="mayors-notes-textarea"
                  placeholder="Add notes about this project..."
                />
              </div>
            </div>
          )}

          {activeTab === 'media' && (
            <div className="panel-empty-state">
              <div className="panel-empty-state-icon">📷</div>
              <h4>No media yet</h4>
              <p>Photos and documents for this project will appear here.</p>
            </div>
          )}

          {activeTab === 'grants' && (
            <GrantApplicationList
              projectId={project.id}
              project={project}
              onApplicationCountChange={setGrantCount}
            />
          )}
        </div>

        {/* Footer - only show for details tab */}
        {activeTab === 'details' && (
          <div className="panel-footer">
            <div className="panel-actions-left">
              <button
                onClick={onOpenGrantMatcher}
                className="panel-action-btn secondary"
              >
                💰 Explore Funding
              </button>
            </div>
            <div className="panel-actions-right">
              <button
                onClick={onClose}
                className="panel-action-btn ghost"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="panel-action-btn primary"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
