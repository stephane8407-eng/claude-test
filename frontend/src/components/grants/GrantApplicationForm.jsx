/**
 * GrantApplicationForm Component
 * Create a new grant application with AI-powered assistance
 *
 * Stage-by-Stage AI Help:
 * - Researching: AI analyzes eligibility and requirements
 * - Preparing: AI drafts the application
 * - Submitted: Manual tracking only
 *
 * API Endpoints:
 * - POST /api/grants/applications - Create application
 * - POST /api/grants/applications/research - AI research
 * - POST /api/grants/applications/draft - AI draft
 */

import React, { useState, useEffect } from 'react';
import './grants.css';

const STATUS_OPTIONS = [
  {
    value: 'draft',
    emoji: '🔍',
    title: 'Researching',
    description: 'Just exploring this funding option'
  },
  {
    value: 'preparing',
    emoji: '📝',
    title: 'Preparing',
    description: 'Gathering documents and information'
  },
  {
    value: 'submitted',
    emoji: '📤',
    title: 'Submitted',
    description: 'Application has been sent'
  }
];

const LOCAL_STORAGE_KEY = 'grant_application_draft';

export default function GrantApplicationForm({
  project,
  program,
  onClose,
  onSuccess
}) {
  const [status, setStatus] = useState('draft');
  const [notes, setNotes] = useState('');
  const [submissionDate, setSubmissionDate] = useState('');
  const [followUpDate, setFollowUpDate] = useState('');
  const [referenceNumber, setReferenceNumber] = useState('');
  const [documents, setDocuments] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [showAutoSaved, setShowAutoSaved] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);

  // AI Generation states
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiError, setAiError] = useState(null);
  const [aiGenerated, setAiGenerated] = useState(false);

  // Restore draft from localStorage
  useEffect(() => {
    const savedDraft = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (savedDraft) {
      try {
        const draft = JSON.parse(savedDraft);
        // Only restore if it's for the same project and program
        if (draft.projectId === project?.id && draft.programId === program?.program_id) {
          setStatus(draft.status || 'draft');
          setNotes(draft.notes || '');
          setSubmissionDate(draft.submissionDate || '');
          setFollowUpDate(draft.followUpDate || '');
          setReferenceNumber(draft.referenceNumber || '');
        }
      } catch (e) {
        console.error('Failed to restore draft:', e);
      }
    }
  }, [project?.id, program?.program_id]);

  // Auto-save to localStorage every 30 seconds
  useEffect(() => {
    const saveInterval = setInterval(() => {
      const draft = {
        projectId: project?.id,
        programId: program?.program_id,
        status,
        notes,
        submissionDate,
        followUpDate,
        referenceNumber,
        savedAt: new Date().toISOString()
      };
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(draft));
      setShowAutoSaved(true);
      setTimeout(() => setShowAutoSaved(false), 2000);
    }, 30000);

    return () => clearInterval(saveInterval);
  }, [project?.id, program?.program_id, status, notes, submissionDate, followUpDate, referenceNumber]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  // AI Research Generation
  const handleGenerateResearch = async () => {
    setAiGenerating(true);
    setAiError(null);

    try {
      const response = await fetch('/api/grants/applications/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: project.id,
          funding_program_id: program.program_id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate research');
      }

      const data = await response.json();
      setNotes(data.research_content);
      setAiGenerated(true);
    } catch (err) {
      setAiError(err.message);
      console.error('AI Research error:', err);
    } finally {
      setAiGenerating(false);
    }
  };

  // AI Draft Generation
  const handleGenerateDraft = async () => {
    setAiGenerating(true);
    setAiError(null);

    try {
      const response = await fetch('/api/grants/applications/draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: project.id,
          funding_program_id: program.program_id,
          research_notes: notes || null // Pass existing notes as context
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate draft');
      }

      const data = await response.json();
      setNotes(data.draft_content);
      setAiGenerated(true);
    } catch (err) {
      setAiError(err.message);
      console.error('AI Draft error:', err);
    } finally {
      setAiGenerating(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!status) {
      setError('Please select a status');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch('/api/grants/applications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: project.id,
          funding_program_id: program.program_id,
          status,
          notes: notes.trim() || null,
          submitted_date: submissionDate || null,
          documents: documents.length > 0 ? documents : null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create application');
      }

      // Clear saved draft
      localStorage.removeItem(LOCAL_STORAGE_KEY);

      // Check if this is the first application (show confetti)
      const existingApps = await fetch(`/api/grants/applications?project_id=${project.id}`);
      const appsData = await existingApps.json();

      if (appsData.applications?.length <= 1) {
        setShowConfetti(true);
        setTimeout(() => {
          setShowConfetti(false);
          onSuccess();
        }, 2000);
      } else {
        onSuccess();
      }
    } catch (err) {
      setError(err.message);
      console.error('Error creating application:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const addDocumentLink = () => {
    const url = prompt('Enter document URL (Google Drive, Dropbox, etc.):');
    if (url && url.trim()) {
      setDocuments([...documents, { type: 'link', url: url.trim(), name: url.trim() }]);
    }
  };

  const removeDocument = (index) => {
    setDocuments(documents.filter((_, i) => i !== index));
  };

  const projectTitle = project?.project_data?.title || 'Untitled Project';

  // Determine which AI button to show based on status
  const showResearchButton = status === 'draft';
  const showDraftButton = status === 'preparing';

  return (
    <div
      className="grant-modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="application-form-title"
    >
      <div
        className="grant-modal grant-modal-small"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="grant-modal-header">
          <h2 id="application-form-title">
            Start Grant Application
          </h2>
          {showAutoSaved && (
            <span style={{
              fontSize: '12px',
              color: '#059669',
              position: 'absolute',
              top: '24px',
              right: '60px'
            }}>
              Auto-saved
            </span>
          )}
          <button
            className="grant-modal-close"
            onClick={onClose}
            aria-label="Close modal"
          >
            x
          </button>
        </div>

        {/* Content */}
        <div className="grant-modal-content">
          {/* Project and Program info */}
          <div style={{
            background: '#F5F5F5',
            padding: '16px',
            borderRadius: '8px',
            marginBottom: '24px'
          }}>
            <div style={{ marginBottom: '8px' }}>
              <span style={{ fontSize: '14px', color: '#6B7280' }}>Project:</span>
              <div style={{ fontSize: '16px', fontWeight: 500, color: '#1F2937' }}>
                {projectTitle}
              </div>
            </div>
            <div>
              <span style={{ fontSize: '14px', color: '#6B7280' }}>Program:</span>
              <div style={{ fontSize: '16px', fontWeight: 500, color: '#1F2937' }}>
                {program.name}
              </div>
            </div>
          </div>

          <form className="grant-form" onSubmit={handleSubmit}>
            {/* Status Selection */}
            <div className="grant-form-group">
              <label className="grant-form-label">
                Current Status
              </label>
              <div className="grant-radio-group">
                {STATUS_OPTIONS.map(option => (
                  <label
                    key={option.value}
                    className={`grant-radio-option ${status === option.value ? 'selected' : ''}`}
                  >
                    <input
                      type="radio"
                      name="status"
                      value={option.value}
                      checked={status === option.value}
                      onChange={(e) => {
                        setStatus(e.target.value);
                        setAiGenerated(false); // Reset AI generated flag when status changes
                      }}
                    />
                    <div className="grant-radio-content">
                      <div className="grant-radio-title">
                        {option.emoji} {option.title}
                      </div>
                      <div className="grant-radio-description">
                        {option.description}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* AI Assistant Button - Stage-specific */}
            {(showResearchButton || showDraftButton) && (
              <div className="grant-form-group">
                <button
                  type="button"
                  className="grant-btn grant-btn-ai"
                  onClick={showResearchButton ? handleGenerateResearch : handleGenerateDraft}
                  disabled={aiGenerating}
                  style={{
                    width: '100%',
                    background: aiGenerating ? '#9CA3AF' : 'linear-gradient(135deg, #008080 0%, #00A3A3 100%)',
                    color: 'white',
                    border: 'none',
                    padding: '14px 24px',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontWeight: 500,
                    cursor: aiGenerating ? 'wait' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '10px',
                    transition: 'all 0.2s ease',
                    boxShadow: aiGenerating ? 'none' : '0 2px 8px rgba(0, 128, 128, 0.3)'
                  }}
                >
                  {aiGenerating ? (
                    <>
                      <span className="grant-loading-spinner" style={{ width: '18px', height: '18px' }} />
                      <span>L'IA analyse votre projet...</span>
                    </>
                  ) : (
                    <>
                      <span style={{ fontSize: '18px' }}>✨</span>
                      <span>
                        {showResearchButton
                          ? 'Analyser avec l\'IA'
                          : 'Rédiger avec l\'IA'
                        }
                      </span>
                    </>
                  )}
                </button>
                <p style={{
                  fontSize: '13px',
                  color: '#6B7280',
                  marginTop: '8px',
                  textAlign: 'center'
                }}>
                  {showResearchButton
                    ? 'L\'IA analysera l\'éligibilité et les exigences du programme'
                    : 'L\'IA rédigera un brouillon de candidature complet'
                  }
                </p>
              </div>
            )}

            {/* AI Error */}
            {aiError && (
              <div style={{
                padding: '12px',
                background: 'rgba(220, 38, 38, 0.1)',
                borderRadius: '8px',
                color: '#DC2626',
                fontSize: '14px',
                marginBottom: '16px'
              }}>
                Erreur IA: {aiError}
              </div>
            )}

            {/* Notes */}
            <div className="grant-form-group">
              <label className="grant-form-label" htmlFor="notes">
                {status === 'draft' && 'Notes de Recherche'}
                {status === 'preparing' && 'Brouillon de Candidature'}
                {status === 'submitted' && 'Notes de Suivi'}
                {!['draft', 'preparing', 'submitted'].includes(status) && 'Notes'}
                <span style={{ fontWeight: 400, color: '#6B7280', marginLeft: '8px' }}>
                  (Optional)
                </span>
              </label>

              {/* AI Generated Badge */}
              {aiGenerated && notes && (
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '4px 10px',
                  background: 'rgba(0, 128, 128, 0.1)',
                  color: '#008080',
                  fontSize: '12px',
                  fontWeight: 500,
                  borderRadius: '12px',
                  marginBottom: '8px'
                }}>
                  <span>✨</span>
                  <span>Généré par IA - À réviser et adapter</span>
                </div>
              )}

              <textarea
                id="notes"
                className="grant-form-textarea"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder={
                  status === 'draft'
                    ? "Cliquez sur 'Analyser avec l'IA' pour générer une analyse d'éligibilité, ou écrivez vos propres notes..."
                    : status === 'preparing'
                    ? "Cliquez sur 'Rédiger avec l'IA' pour générer un brouillon, ou écrivez votre candidature..."
                    : "Notes de suivi: dates de relance, réponses reçues, contacts..."
                }
                rows={notes && notes.length > 500 ? 12 : 6}
                style={{
                  fontFamily: notes && notes.includes('##') ? 'inherit' : 'inherit',
                  whiteSpace: 'pre-wrap'
                }}
              />
            </div>

            {/* Submitted-specific fields */}
            {status === 'submitted' && (
              <>
                <div className="grant-form-group">
                  <label className="grant-form-label" htmlFor="submissionDate">
                    Date de Soumission
                  </label>
                  <input
                    type="date"
                    id="submissionDate"
                    className="grant-form-input"
                    value={submissionDate}
                    onChange={(e) => setSubmissionDate(e.target.value)}
                  />
                </div>

                <div className="grant-form-group">
                  <label className="grant-form-label" htmlFor="referenceNumber">
                    Numéro de Référence
                    <span style={{ fontWeight: 400, color: '#6B7280', marginLeft: '8px' }}>
                      (Optional)
                    </span>
                  </label>
                  <input
                    type="text"
                    id="referenceNumber"
                    className="grant-form-input"
                    value={referenceNumber}
                    onChange={(e) => setReferenceNumber(e.target.value)}
                    placeholder="Ex: LEADER-2024-0042"
                  />
                </div>
              </>
            )}

            {/* Documents */}
            <div className="grant-form-group">
              <label className="grant-form-label">
                Documents
                <span style={{ fontWeight: 400, color: '#6B7280', marginLeft: '8px' }}>
                  (Optional)
                </span>
              </label>
              {documents.length > 0 && (
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: '0 0 12px 0',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px'
                }}>
                  {documents.map((doc, index) => (
                    <li key={index} style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      background: '#F5F5F5',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }}>
                      <span style={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        maxWidth: '80%'
                      }}>
                        {doc.name}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeDocument(index)}
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: '#6B7280',
                          padding: '4px'
                        }}
                      >
                        x
                      </button>
                    </li>
                  ))}
                </ul>
              )}
              {documents.length < 5 && (
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button
                    type="button"
                    className="grant-btn grant-btn-ghost grant-btn-small"
                    onClick={addDocumentLink}
                  >
                    + Add Link
                  </button>
                </div>
              )}
              {documents.length >= 5 && (
                <p style={{ fontSize: '14px', color: '#6B7280' }}>
                  Maximum 5 documents reached
                </p>
              )}
            </div>

            {/* Key Dates (for non-submitted status) */}
            {status !== 'submitted' && (
              <div className="grant-form-group">
                <label className="grant-form-label">
                  Dates Clés
                  <span style={{ fontWeight: 400, color: '#6B7280', marginLeft: '8px' }}>
                    (Optional)
                  </span>
                </label>
                <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                  <div style={{ flex: 1, minWidth: '200px' }}>
                    <label style={{ fontSize: '14px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                      Soumission prévue
                    </label>
                    <input
                      type="date"
                      className="grant-form-input"
                      value={submissionDate}
                      onChange={(e) => setSubmissionDate(e.target.value)}
                      style={{ width: '100%' }}
                    />
                  </div>
                  <div style={{ flex: 1, minWidth: '200px' }}>
                    <label style={{ fontSize: '14px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                      Prochaine relance
                    </label>
                    <input
                      type="date"
                      className="grant-form-input"
                      value={followUpDate}
                      onChange={(e) => setFollowUpDate(e.target.value)}
                      style={{ width: '100%' }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="grant-form-error" style={{ padding: '12px', background: 'rgba(220, 38, 38, 0.1)', borderRadius: '8px' }}>
                {error}
              </div>
            )}
          </form>
        </div>

        {/* Footer */}
        <div className="grant-modal-footer">
          <button
            type="button"
            className="grant-btn grant-btn-ghost"
            onClick={onClose}
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="grant-btn grant-btn-primary"
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? (
              <>
                <span className="grant-loading-spinner" style={{ width: '16px', height: '16px', marginRight: '8px' }} />
                Creating...
              </>
            ) : (
              'Create Application'
            )}
          </button>
        </div>

        {/* Confetti animation */}
        {showConfetti && (
          <div style={{
            position: 'fixed',
            inset: 0,
            pointerEvents: 'none',
            zIndex: 100,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <div style={{
              fontSize: '64px',
              animation: 'pulse 0.5s ease-in-out infinite'
            }}>
              🎉
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
