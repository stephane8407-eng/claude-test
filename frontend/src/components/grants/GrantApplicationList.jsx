/**
 * GrantApplicationList Component
 * Shows all grant applications for a project
 *
 * Location: Tab in Project Detail Modal
 * API: GET /api/grants/applications?project_id={id}
 */

import React, { useState, useEffect } from 'react';
import GrantApplicationCard from './GrantApplicationCard';
import GrantMatcher from './GrantMatcher';
import GrantProgramDetail from './GrantProgramDetail';
import './grants.css';

const STATUS_ORDER = ['draft', 'preparing', 'submitted', 'under_review', 'approved', 'rejected', 'abandoned'];

export default function GrantApplicationList({
  projectId,
  project,
  onApplicationCountChange
}) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showMatcher, setShowMatcher] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [statusUpdateApp, setStatusUpdateApp] = useState(null);
  const [newStatus, setNewStatus] = useState('');
  const [updating, setUpdating] = useState(false);

  // Fetch applications
  useEffect(() => {
    if (projectId) {
      fetchApplications();
    }
  }, [projectId]);

  const fetchApplications = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/grants/applications?project_id=${projectId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch applications');
      }
      const data = await response.json();

      // Sort by status priority
      const sorted = (data.applications || []).sort((a, b) => {
        const orderA = STATUS_ORDER.indexOf(a.status);
        const orderB = STATUS_ORDER.indexOf(b.status);
        if (orderA !== orderB) return orderA - orderB;
        // Then by date (most recent first)
        return new Date(b.created_at) - new Date(a.created_at);
      });

      setApplications(sorted);

      // Notify parent of count change
      if (onApplicationCountChange) {
        onApplicationCountChange(sorted.length);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching applications:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApplicationCreated = () => {
    fetchApplications();
    setShowMatcher(false);
  };

  const handleViewDetails = (application) => {
    // Open program detail drawer
    setSelectedApplication(application);
  };

  const handleUpdateStatus = (application) => {
    setStatusUpdateApp(application);
    setNewStatus(application.status);
  };

  const submitStatusUpdate = async () => {
    if (!statusUpdateApp || !newStatus) return;

    setUpdating(true);
    try {
      const response = await fetch(`/api/grants/applications/${statusUpdateApp.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      if (!response.ok) {
        throw new Error('Failed to update status');
      }

      await fetchApplications();
      setStatusUpdateApp(null);
    } catch (err) {
      console.error('Error updating status:', err);
      alert('Failed to update status. Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  // Calculate summary stats
  const stats = {
    total: applications.length,
    inProgress: applications.filter(a => ['draft', 'preparing'].includes(a.status)).length,
    submitted: applications.filter(a => ['submitted', 'under_review'].includes(a.status)).length,
    approved: applications.filter(a => a.status === 'approved').length,
    totalApproved: applications
      .filter(a => a.status === 'approved')
      .reduce((sum, a) => sum + (a.amount_approved || 0), 0)
  };

  if (loading) {
    return (
      <div className="grant-loading">
        <div className="grant-loading-spinner" />
        Loading applications...
      </div>
    );
  }

  if (error) {
    return (
      <div className="grant-empty-state">
        <div className="grant-empty-state-icon">⚠️</div>
        <h4>Unable to load applications</h4>
        <p>{error}</p>
        <button className="grant-btn grant-btn-primary" onClick={fetchApplications}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="grant-applications-header">
        <h3>
          💰 Grant Applications
          <span className="grant-applications-count">
            ({applications.length})
          </span>
        </h3>
        <button
          className="grant-btn grant-btn-primary"
          onClick={() => setShowMatcher(true)}
        >
          + Explore Funding Options
        </button>
      </div>

      {/* Summary stats (if any applications exist) */}
      {applications.length > 0 && (
        <div style={{
          display: 'flex',
          gap: '24px',
          marginBottom: '24px',
          flexWrap: 'wrap'
        }}>
          <div style={{
            padding: '12px 16px',
            background: 'rgba(0, 128, 128, 0.1)',
            borderRadius: '8px',
            fontSize: '14px'
          }}>
            <span style={{ color: '#008080', fontWeight: 600 }}>{stats.inProgress}</span>
            <span style={{ color: '#6B7280' }}> in progress</span>
          </div>
          <div style={{
            padding: '12px 16px',
            background: 'rgba(139, 92, 246, 0.1)',
            borderRadius: '8px',
            fontSize: '14px'
          }}>
            <span style={{ color: '#7C3AED', fontWeight: 600 }}>{stats.submitted}</span>
            <span style={{ color: '#6B7280' }}> submitted</span>
          </div>
          {stats.approved > 0 && (
            <div style={{
              padding: '12px 16px',
              background: 'rgba(16, 185, 129, 0.1)',
              borderRadius: '8px',
              fontSize: '14px'
            }}>
              <span style={{ color: '#059669', fontWeight: 600 }}>€{stats.totalApproved.toLocaleString()}</span>
              <span style={{ color: '#6B7280' }}> approved</span>
            </div>
          )}
        </div>
      )}

      {/* Applications list */}
      {applications.length === 0 ? (
        <div className="grant-empty-state">
          <div className="grant-empty-state-icon">📋</div>
          <h4>No funding applications yet</h4>
          <p>Start by exploring funding opportunities that match this project!</p>
          <button
            className="grant-btn grant-btn-primary"
            onClick={() => setShowMatcher(true)}
          >
            Explore Funding Options
          </button>
        </div>
      ) : (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          maxHeight: '600px',
          overflowY: 'auto',
          overflowX: 'hidden',
          paddingRight: '8px',
          paddingBottom: '40px'
        }}>
          {applications.map(application => (
            <div
              key={application.id}
              style={{
                background: '#fff',
                border: '1px solid #E5E7EB',
                borderRadius: '12px',
                padding: '20px',
                marginBottom: '20px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '20px' }}>
                    {application.funding_program?.organization?.toLowerCase().includes('europ') ? '🌿' : '🏛️'}
                  </span>
                  <div>
                    <h4 style={{ fontSize: '16px', fontWeight: 600, color: '#1F2937', margin: 0 }}>
                      {application.funding_program?.name || 'Unknown Program'}
                    </h4>
                    <div style={{ fontSize: '14px', color: '#6B7280' }}>
                      {application.funding_program?.organization || ''}
                    </div>
                  </div>
                </div>
                <span style={{
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontWeight: 500,
                  background: application.status === 'draft' ? 'rgba(0, 128, 128, 0.1)' :
                             application.status === 'preparing' ? 'rgba(245, 158, 11, 0.1)' :
                             application.status === 'submitted' ? 'rgba(139, 92, 246, 0.1)' :
                             'rgba(156, 163, 175, 0.1)',
                  color: application.status === 'draft' ? '#008080' :
                         application.status === 'preparing' ? '#D97706' :
                         application.status === 'submitted' ? '#7C3AED' :
                         '#6B7280'
                }}>
                  {application.status === 'draft' ? '🔍 Researching' :
                   application.status === 'preparing' ? '📝 Preparing' :
                   application.status === 'submitted' ? '📤 Submitted' :
                   application.status}
                </span>
              </div>
              <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '12px' }}>
                Created: {new Date(application.created_at).toLocaleDateString()}
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  className="grant-btn grant-btn-secondary grant-btn-small"
                  onClick={() => handleViewDetails(application)}
                  style={{
                    padding: '8px 16px',
                    fontSize: '14px',
                    border: '1px solid #008080',
                    borderRadius: '8px',
                    background: '#fff',
                    color: '#008080',
                    cursor: 'pointer'
                  }}
                >
                  View Details
                </button>
                <button
                  className="grant-btn grant-btn-ghost grant-btn-small"
                  onClick={() => handleUpdateStatus(application)}
                  style={{
                    padding: '8px 16px',
                    fontSize: '14px',
                    border: 'none',
                    borderRadius: '8px',
                    background: 'transparent',
                    color: '#6B7280',
                    cursor: 'pointer'
                  }}
                >
                  Update Status
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Grant Matcher Modal */}
      {showMatcher && (
        <GrantMatcher
          project={project}
          isOpen={showMatcher}
          onClose={() => setShowMatcher(false)}
          onApplicationCreated={handleApplicationCreated}
        />
      )}

      {/* Program Detail Drawer */}
      {selectedApplication && (
        <GrantProgramDetail
          program={{
            ...selectedApplication.funding_program,
            program_id: selectedApplication.funding_program_id
          }}
          project={project}
          onClose={() => setSelectedApplication(null)}
          onStartApplication={() => setSelectedApplication(null)}
        />
      )}

      {/* Status Update Modal */}
      {statusUpdateApp && (
        <div
          className="grant-modal-overlay"
          onClick={() => setStatusUpdateApp(null)}
        >
          <div
            className="grant-modal grant-modal-small"
            onClick={e => e.stopPropagation()}
            style={{ maxWidth: '400px' }}
          >
            <div className="grant-modal-header">
              <h2>Update Status</h2>
              <button
                className="grant-modal-close"
                onClick={() => setStatusUpdateApp(null)}
              >
                ×
              </button>
            </div>
            <div className="grant-modal-content">
              <div className="grant-form-group">
                <label className="grant-form-label">New Status</label>
                <select
                  className="grant-form-input"
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  style={{ width: '100%' }}
                >
                  <option value="draft">🔍 Researching</option>
                  <option value="preparing">📝 Preparing</option>
                  <option value="submitted">📤 Submitted</option>
                  <option value="under_review">🔍 Under Review</option>
                  <option value="approved">✅ Approved</option>
                  <option value="rejected">❌ Rejected</option>
                  <option value="abandoned">🗑️ Abandoned</option>
                </select>
              </div>
            </div>
            <div className="grant-modal-footer">
              <button
                className="grant-btn grant-btn-ghost"
                onClick={() => setStatusUpdateApp(null)}
              >
                Cancel
              </button>
              <button
                className="grant-btn grant-btn-primary"
                onClick={submitStatusUpdate}
                disabled={updating}
              >
                {updating ? 'Updating...' : 'Update Status'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
