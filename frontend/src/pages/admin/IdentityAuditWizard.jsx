/**
 * IdentityAuditWizard
 *
 * 5-step wizard for village identity audit.
 * Collects history, environment, economy data and generates identity via AI.
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Step1History } from './steps/Step1History';
import { Step2Environment } from './steps/Step2Environment';
import { Step3Economy } from './steps/Step3Economy';
import { Step4FreeForm } from './steps/Step4FreeForm';
import { Step5Review } from './steps/Step5Review';
import { IdentityResults } from './IdentityResults';
import { identityAPI } from '../../services/api';
import { mockGenerateIdentity } from '../../services/mockIdentityGenerator';
import './IdentityAuditWizard.css';

const STEPS = [
  { id: 1, title: 'Histoire & Patrimoine', shortTitle: 'Histoire' },
  { id: 2, title: 'Environnement & Ressources', shortTitle: 'Environnement' },
  { id: 3, title: 'Économie, Traditions & Vie', shortTitle: 'Économie' },
  { id: 4, title: 'Description Libre', shortTitle: 'Description' },
  { id: 5, title: 'Révision & Génération', shortTitle: 'Révision' },
];

const STORAGE_KEY = 'spv_identity_audit_draft';

const initialFormData = {
  // Step 1: History
  warPeriods: [],
  eventTypes: [],
  monuments: '',
  legends: '',
  historyOther: '',

  // Step 2: Environment
  waterFeatures: [],
  landscape: [],
  agriculture: '',
  naturalResources: '',
  environmentDescription: '',

  // Step 3: Economy
  localProducts: [],
  potentialProducts: '',
  festivals: '',
  services: [],
  villageVibe: '',
  nearestTown: '',
  liveHereDescription: '',

  // Step 4: Free form
  freeDescription: '',
};

export function IdentityAuditWizard() {
  const { user } = useAuth();
  const villageSlug = user?.village_slug;

  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState(initialFormData);
  const [generatedResults, setGeneratedResults] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  // Load saved draft from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setFormData(parsed.formData || initialFormData);
        setCurrentStep(parsed.currentStep || 1);
      } catch (e) {
        console.error('Failed to load draft:', e);
      }
    }
  }, []);

  // Save draft to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      formData,
      currentStep,
    }));
  }, [formData, currentStep]);

  const updateFormData = (updates) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  const goToStep = (step) => {
    if (step >= 1 && step <= 5) {
      setCurrentStep(step);
    }
  };

  const goNext = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1);
    }
  };

  const goPrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);

    // Check if village_slug is available
    if (!villageSlug) {
      setError('Village non associé à votre compte. Veuillez contacter l\'administrateur.');
      setIsGenerating(false);
      return;
    }

    try {
      // Try real API first, fallback to mock if API key not configured
      let results;
      try {
        // Transform formData to match API schema
        const auditData = {
          warPeriods: formData.warPeriods,
          eventTypes: formData.eventTypes,
          monuments: formData.monuments,
          legends: formData.legends,
          historyNotes: formData.historyOther,
          waterFeatures: formData.waterFeatures,
          landscape: formData.landscape,
          agriculture: formData.agriculture,
          naturalResources: formData.naturalResources,
          environmentNotes: formData.environmentDescription,
          localProducts: formData.localProducts,
          potentialProducts: formData.potentialProducts,
          festivals: formData.festivals,
          services: formData.services,
          vibe: formData.villageVibe,
          nearestTown: formData.nearestTown,
          livingDescription: formData.liveHereDescription,
          freeDescription: formData.freeDescription,
        };

        // Call real AI API (3 options for 3-tier system)
        results = await identityAPI.generateIdentity(villageSlug, auditData, 3);

        // Transform API response to match expected format
        if (results.options) {
          results = {
            summaryIdentity: results.options[0]?.summary_identity || '',
            longIdentity: results.options[0]?.identity_narrative || '',
            liveHereSummary: results.options[0]?.live_here_summary || '',
            themes: results.options.map((opt, index) => ({
              id: opt.identity_title.toLowerCase().replace(/\s+/g, '_'),
              name: opt.identity_title,
              confidence: opt.confidence,
              description: opt.identity_narrative,
              tourismIdeas: opt.projects.map(p => p.title),
              // 3-tier system fields
              tier: opt.tier || (index + 1),
              tier_label: opt.tier_label || ['Parcours Prouvé', 'Innovation Ciblée', 'Vision Transformatrice'][index],
              projects: opt.projects,
            })),
            suggested_projects: results.options.flatMap(opt =>
              opt.projects.map(p => ({
                title: p.title,
                description: p.description,
                themes: opt.themes,
                difficulty: p.difficulty,
                estimated_timeline: `${p.timeline_months} mois`,
                estimated_budget: `€${p.budget_min.toLocaleString()} - €${p.budget_max.toLocaleString()}`,
                inspired_by: p.inspired_by?.village_name || null,
                potential_funding: p.potential_funding.map(f => f.program_name),
                first_steps: p.first_steps,
              }))
            ),
            metadata: results.metadata,
          };
        }
      } catch (apiError) {
        console.warn('Real API failed, falling back to mock:', apiError.message);
        // Fallback to mock generator
        results = await mockGenerateIdentity(formData);
      }

      setGeneratedResults(results);
    } catch (err) {
      console.error('Generation failed:', err);
      setError('Échec de la génération. Veuillez réessayer.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRegenerate = () => {
    setGeneratedResults(null);
    handleGenerate();
  };

  const handleBackToEdit = () => {
    setGeneratedResults(null);
    setCurrentStep(1);
  };

  const clearDraft = () => {
    localStorage.removeItem(STORAGE_KEY);
    setFormData(initialFormData);
    setCurrentStep(1);
    setGeneratedResults(null);
  };

  // Show results page if we have generated results
  if (generatedResults) {
    return (
      <IdentityResults
        results={generatedResults}
        villageSlug={villageSlug}
        onRegenerate={handleRegenerate}
        onBackToEdit={handleBackToEdit}
      />
    );
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Step1History
            data={formData}
            onChange={updateFormData}
          />
        );
      case 2:
        return (
          <Step2Environment
            data={formData}
            onChange={updateFormData}
          />
        );
      case 3:
        return (
          <Step3Economy
            data={formData}
            onChange={updateFormData}
          />
        );
      case 4:
        return (
          <Step4FreeForm
            data={formData}
            onChange={updateFormData}
          />
        );
      case 5:
        return (
          <Step5Review
            data={formData}
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
            error={error}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="spv-wizard">
      <div className="spv-wizard__header">
        <h1 className="spv-wizard__title">Audit d'identité</h1>
        <p className="spv-wizard__subtitle">
          Partagez les informations sur votre village pour générer son profil identitaire.
        </p>
      </div>

      {/* Stepper */}
      <div className="spv-wizard__stepper">
        {STEPS.map((step) => (
          <button
            key={step.id}
            className={`spv-wizard__step ${currentStep === step.id ? 'spv-wizard__step--active' : ''} ${currentStep > step.id ? 'spv-wizard__step--completed' : ''}`}
            onClick={() => goToStep(step.id)}
            type="button"
          >
            <span className="spv-wizard__step-number">{step.id}</span>
            <span className="spv-wizard__step-title">{step.shortTitle}</span>
          </button>
        ))}
      </div>

      {/* Current step title */}
      <div className="spv-wizard__step-header">
        <h2 className="spv-wizard__step-heading">
          Étape {currentStep}: {STEPS[currentStep - 1].title}
        </h2>
      </div>

      {/* Step content */}
      <div className="spv-wizard__content">
        {renderStep()}
      </div>

      {/* Navigation buttons */}
      {currentStep < 5 && (
        <div className="spv-wizard__nav">
          <button
            type="button"
            className="spv-wizard__btn spv-wizard__btn--secondary"
            onClick={goPrevious}
            disabled={currentStep === 1}
          >
            Précédent
          </button>
          <button
            type="button"
            className="spv-wizard__btn spv-wizard__btn--primary"
            onClick={goNext}
          >
            Suivant
          </button>
        </div>
      )}
    </div>
  );
}
