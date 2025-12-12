/**
 * GrantApplicationDetail Component
 * Full view for viewing and editing a grant application
 *
 * Shows:
 * - Application info (program, project, status)
 * - AI Research content (if available)
 * - AI Draft content (if available)
 * - Notes
 * - Documents
 * - Action buttons (generate AI content, update status, etc.)
 */

import React, { useState, useEffect } from 'react';
import './grants.css';

const STATUS_CONFIG = {
  draft: { label: 'Recherche', emoji: '🔍', color: '#008080' },
  researching: { label: 'Recherche', emoji: '🔍', color: '#008080' },
  preparing: { label: 'Préparation', emoji: '📝', color: '#D97706' },
  submitted: { label: 'Soumis', emoji: '📤', color: '#7C3AED' },
  under_review: { label: 'En cours d\'examen', emoji: '🔍', color: '#6B7280' },
  approved: { label: 'Approuvé', emoji: '✅', color: '#059669' },
  rejected: { label: 'Refusé', emoji: '❌', color: '#DC2626' },
  abandoned: { label: 'Abandonné', emoji: '🗑️', color: '#9CA3AF' }
};

export default function GrantApplicationDetail({
  application,
  project,
  onClose,
  onUpdate
}) {
  const [loading, setLoading] = useState(true);
  const [fullApplication, setFullApplication] = useState(null);
  const [error, setError] = useState(null);
  const [editingNotes, setEditingNotes] = useState(false);
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiError, setAiError] = useState(null);

  // Fetch full application data
  useEffect(() => {
    if (application?.id) {
      fetchApplication();
    }
  }, [application?.id]);

  const fetchApplication = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/grants/applications/${application.id}`);
      if (!response.ok) {
        throw new Error('Échec du chargement du dossier');
      }
      const data = await response.json();
      setFullApplication(data);
      setNotes(data.notes || '');
    } catch (err) {
      setError(err.message);
      console.error('Error fetching application:', err);
    } finally {
      setLoading(false);
    }
  };

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

  const handleSaveNotes = async () => {
    setSaving(true);
    try {
      const response = await fetch(`/api/grants/applications/${application.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes })
      });

      if (!response.ok) {
        throw new Error('Échec de la sauvegarde');
      }

      setFullApplication({ ...fullApplication, notes });
      setEditingNotes(false);
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error('Error saving notes:', err);
      alert('Échec de la sauvegarde des notes');
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateResearch = async () => {
    setAiGenerating(true);
    setAiError(null);

    try {
      const response = await fetch('/api/grants/applications/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: fullApplication.project_id,
          funding_program_id: fullApplication.funding_program_id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Échec de la génération');
      }

      const data = await response.json();
      setFullApplication({
        ...fullApplication,
        ai_research: data.research_content
      });
      if (onUpdate) onUpdate();
    } catch (err) {
      setAiError(err.message);
      console.error('AI Research error:', err);
    } finally {
      setAiGenerating(false);
    }
  };

  const handleGenerateDraft = async () => {
    setAiGenerating(true);
    setAiError(null);

    try {
      const response = await fetch('/api/grants/applications/draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: fullApplication.project_id,
          funding_program_id: fullApplication.funding_program_id,
          research_notes: fullApplication.ai_research || null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Échec de la génération');
      }

      const data = await response.json();
      setFullApplication({
        ...fullApplication,
        ai_draft: data.draft_content,
        status: 'preparing'
      });
      if (onUpdate) onUpdate();
    } catch (err) {
      setAiError(err.message);
      console.error('AI Draft error:', err);
    } finally {
      setAiGenerating(false);
    }
  };

  const handleUpdateStatus = async (newStatus) => {
    setSaving(true);
    try {
      const response = await fetch(`/api/grants/applications/${application.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      if (!response.ok) {
        throw new Error('Échec de la mise à jour');
      }

      setFullApplication({ ...fullApplication, status: newStatus });
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error('Error updating status:', err);
      alert('Échec de la mise à jour du statut');
    } finally {
      setSaving(false);
    }
  };

  const statusConfig = STATUS_CONFIG[fullApplication?.status] || STATUS_CONFIG.draft;

  if (loading) {
    return (
      <div className="grant-modal-overlay" onClick={onClose}>
        <div className="grant-modal" onClick={e => e.stopPropagation()}>
          <div className="grant-loading">
            <div className="grant-loading-spinner" />
            Chargement du dossier...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="grant-modal-overlay" onClick={onClose}>
        <div className="grant-modal" onClick={e => e.stopPropagation()}>
          <div className="grant-empty-state">
            <div className="grant-empty-state-icon">⚠️</div>
            <h4>Erreur</h4>
            <p>{error}</p>
            <button className="grant-btn grant-btn-primary" onClick={onClose}>
              Fermer
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grant-modal-overlay" onClick={onClose}>
      <div
        className="grant-modal"
        onClick={e => e.stopPropagation()}
        style={{ maxWidth: '900px', maxHeight: '90vh' }}
      >
        {/* Header */}
        <div className="grant-modal-header">
          <div>
            <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '12px' }}>
              📋 {fullApplication?.program_name || 'Dossier de subvention'}
            </h2>
            <p style={{ color: '#6B7280', margin: '4px 0 0 0', fontSize: '14px' }}>
              {fullApplication?.project_title || 'Projet sans titre'}
            </p>
          </div>
          <button className="grant-modal-close" onClick={onClose}>×</button>
        </div>

        {/* Content */}
        <div className="grant-modal-content" style={{ maxHeight: '60vh', overflowY: 'auto' }}>
          {/* Status bar */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px',
            background: '#F5F5F5',
            borderRadius: '8px',
            marginBottom: '24px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '20px' }}>{statusConfig.emoji}</span>
              <span style={{ fontWeight: 600, color: statusConfig.color }}>
                {statusConfig.label}
              </span>
            </div>
            <select
              value={fullApplication?.status || 'draft'}
              onChange={(e) => handleUpdateStatus(e.target.value)}
              disabled={saving}
              className="grant-form-input"
              style={{ width: 'auto', minWidth: '150px' }}
            >
              <option value="draft">🔍 Recherche</option>
              <option value="preparing">📝 Préparation</option>
              <option value="submitted">📤 Soumis</option>
              <option value="under_review">🔍 En cours d'examen</option>
              <option value="approved">✅ Approuvé</option>
              <option value="rejected">❌ Refusé</option>
              <option value="abandoned">🗑️ Abandonné</option>
            </select>
          </div>

          {/* AI Actions */}
          <div style={{
            display: 'flex',
            gap: '12px',
            marginBottom: '24px',
            flexWrap: 'wrap'
          }}>
            <button
              className="grant-btn grant-btn-ai"
              onClick={handleGenerateResearch}
              disabled={aiGenerating}
              style={{
                flex: 1,
                minWidth: '200px',
                background: aiGenerating ? '#9CA3AF' : 'linear-gradient(135deg, #008080 0%, #00A3A3 100%)',
                color: 'white',
                border: 'none',
                padding: '12px 20px',
                borderRadius: '8px',
                fontWeight: 500,
                cursor: aiGenerating ? 'wait' : 'pointer'
              }}
            >
              {aiGenerating ? (
                <>
                  <span className="grant-loading-spinner" style={{ width: '16px', height: '16px', marginRight: '8px' }} />
                  Génération...
                </>
              ) : (
                <>✨ Analyser avec l'IA</>
              )}
            </button>
            <button
              className="grant-btn grant-btn-ai"
              onClick={handleGenerateDraft}
              disabled={aiGenerating}
              style={{
                flex: 1,
                minWidth: '200px',
                background: aiGenerating ? '#9CA3AF' : 'linear-gradient(135deg, #7C3AED 0%, #9061F9 100%)',
                color: 'white',
                border: 'none',
                padding: '12px 20px',
                borderRadius: '8px',
                fontWeight: 500,
                cursor: aiGenerating ? 'wait' : 'pointer'
              }}
            >
              {aiGenerating ? (
                <>
                  <span className="grant-loading-spinner" style={{ width: '16px', height: '16px', marginRight: '8px' }} />
                  Génération...
                </>
              ) : (
                <>✨ Rédiger avec l'IA</>
              )}
            </button>
          </div>

          {/* AI Error */}
          {aiError && (
            <div style={{
              padding: '12px',
              background: 'rgba(220, 38, 38, 0.1)',
              borderRadius: '8px',
              color: '#DC2626',
              fontSize: '14px',
              marginBottom: '24px'
            }}>
              Erreur IA: {aiError}
            </div>
          )}

          {/* AI Research Section */}
          {fullApplication?.ai_research && (
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{
                fontSize: '16px',
                fontWeight: 600,
                color: '#1F2937',
                marginBottom: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                🔍 Analyse d'éligibilité (IA)
                <span style={{
                  fontSize: '12px',
                  padding: '2px 8px',
                  background: 'rgba(0, 128, 128, 0.1)',
                  color: '#008080',
                  borderRadius: '12px',
                  fontWeight: 400
                }}>
                  Généré par IA
                </span>
              </h3>
              <div style={{
                background: '#FAFAFA',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                padding: '16px',
                whiteSpace: 'pre-wrap',
                fontSize: '14px',
                lineHeight: 1.6,
                maxHeight: '300px',
                overflowY: 'auto'
              }}>
                {fullApplication.ai_research}
              </div>
            </div>
          )}

          {/* AI Draft Section */}
          {fullApplication?.ai_draft && (
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{
                fontSize: '16px',
                fontWeight: 600,
                color: '#1F2937',
                marginBottom: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                📝 Brouillon de candidature (IA)
                <span style={{
                  fontSize: '12px',
                  padding: '2px 8px',
                  background: 'rgba(124, 58, 237, 0.1)',
                  color: '#7C3AED',
                  borderRadius: '12px',
                  fontWeight: 400
                }}>
                  Généré par IA
                </span>
              </h3>
              <div style={{
                background: '#FAFAFA',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                padding: '16px',
                whiteSpace: 'pre-wrap',
                fontSize: '14px',
                lineHeight: 1.6,
                maxHeight: '400px',
                overflowY: 'auto'
              }}>
                {fullApplication.ai_draft}
              </div>
            </div>
          )}

          {/* Notes Section */}
          <div style={{ marginBottom: '24px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '12px'
            }}>
              <h3 style={{
                fontSize: '16px',
                fontWeight: 600,
                color: '#1F2937',
                margin: 0
              }}>
                📝 Notes personnelles
              </h3>
              {!editingNotes && (
                <button
                  className="grant-btn grant-btn-ghost grant-btn-small"
                  onClick={() => setEditingNotes(true)}
                >
                  Modifier
                </button>
              )}
            </div>

            {editingNotes ? (
              <>
                <textarea
                  className="grant-form-textarea"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={6}
                  placeholder="Ajoutez vos notes, rappels, contacts..."
                  style={{ width: '100%', marginBottom: '12px' }}
                />
                <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                  <button
                    className="grant-btn grant-btn-ghost"
                    onClick={() => {
                      setNotes(fullApplication?.notes || '');
                      setEditingNotes(false);
                    }}
                  >
                    Annuler
                  </button>
                  <button
                    className="grant-btn grant-btn-primary"
                    onClick={handleSaveNotes}
                    disabled={saving}
                  >
                    {saving ? 'Sauvegarde...' : 'Enregistrer'}
                  </button>
                </div>
              </>
            ) : (
              <div style={{
                background: '#FAFAFA',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                padding: '16px',
                minHeight: '80px',
                fontSize: '14px',
                color: fullApplication?.notes ? '#1F2937' : '#9CA3AF',
                whiteSpace: 'pre-wrap'
              }}>
                {fullApplication?.notes || 'Aucune note pour le moment. Cliquez sur "Modifier" pour ajouter des notes.'}
              </div>
            )}
          </div>

          {/* Metadata */}
          <div style={{
            background: '#F5F5F5',
            borderRadius: '8px',
            padding: '16px',
            fontSize: '14px',
            color: '#6B7280'
          }}>
            <div style={{ marginBottom: '8px' }}>
              <strong>Créé le :</strong> {fullApplication?.created_at ? new Date(fullApplication.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) : 'N/A'}
            </div>
            {fullApplication?.updated_at && (
              <div style={{ marginBottom: '8px' }}>
                <strong>Mis à jour le :</strong> {new Date(fullApplication.updated_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
              </div>
            )}
            {fullApplication?.submitted_date && (
              <div style={{ marginBottom: '8px' }}>
                <strong>Soumis le :</strong> {new Date(fullApplication.submitted_date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
              </div>
            )}
            {fullApplication?.amount_requested && (
              <div>
                <strong>Montant demandé :</strong> {fullApplication.amount_requested.toLocaleString()} €
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="grant-modal-footer">
          <button className="grant-btn grant-btn-ghost" onClick={onClose}>
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
}
