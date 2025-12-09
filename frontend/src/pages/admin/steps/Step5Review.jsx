/**
 * Step 5: Révision & Génération (Review & Generate)
 */
import { useState } from 'react';
import '../IdentityAuditWizard.css';

// Labels for display
const LABELS = {
  warPeriods: {
    wwii: 'Seconde Guerre mondiale',
    wwi: 'Première Guerre mondiale',
    revolution: 'Révolution française',
    religious_wars: 'Guerres de religion',
    hundred_years: 'Guerre de Cent Ans',
    medieval: 'Période médiévale',
    roman: 'Époque romaine',
    prehistoric: 'Préhistoire',
  },
  eventTypes: {
    battles: 'Batailles',
    burned_villages: 'Villages brûlés',
    sieges: 'Sièges',
    raids: 'Raids',
    garrison: 'Garnison',
    resistance: 'Résistance',
    massacres: 'Massacres',
    liberation: 'Libération',
  },
  waterFeatures: {
    ponds: 'Étangs',
    river: 'Rivière',
    lake: 'Lac',
    springs: 'Sources',
    marshes: 'Marais',
    streams: 'Ruisseaux',
    wells: 'Puits',
    fountains: 'Fontaines',
  },
  landscape: {
    forest: 'Forêt',
    mountains: 'Montagnes',
    plateau: 'Plateau',
    valley: 'Vallée',
    plain: 'Plaine',
    coast: 'Côte',
    hills: 'Collines',
    bocage: 'Bocage',
    vineyards: 'Vignobles',
    meadows: 'Prairies',
  },
  localProducts: {
    cheese: 'Fromage',
    wine: 'Vin',
    honey: 'Miel',
    fish: 'Poisson',
    crafts: 'Artisanat',
    bread: 'Pain',
    meat: 'Charcuterie',
    vegetables: 'Légumes',
    fruits: 'Fruits',
    cider: 'Cidre',
    spirits: 'Spiritueux',
    pottery: 'Poterie',
    textiles: 'Textiles',
    wood: 'Travail du bois',
  },
  services: {
    school: 'École',
    shop: 'Commerce',
    cafe: 'Café',
    restaurant: 'Restaurant',
    post_office: 'Poste',
    medical: 'Médecin',
    pharmacy: 'Pharmacie',
    bank: 'Banque',
    library: 'Bibliothèque',
    sports: 'Sports',
    church: 'Église',
    internet: 'Internet',
  },
  villageVibe: {
    calm: 'Calme et paisible',
    lively: 'Animé',
    family: 'Familial',
    artistic: 'Artistique',
    eco: 'Écologique',
    remote: 'Isolé',
    touristic: 'Touristique',
    agricultural: 'Agricole',
    historic: 'Historique',
    dynamic: 'Dynamique',
  },
};

function getLabels(field, values) {
  if (!values || values.length === 0) return [];
  return values.map(v => LABELS[field]?.[v] || v);
}

function ReviewSection({ title, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="spv-review-section">
      <div
        className="spv-review-section__header"
        onClick={() => setIsOpen(!isOpen)}
      >
        <h3 className="spv-review-section__title">{title}</h3>
        <span className="spv-review-section__toggle">
          {isOpen ? '▼' : '▶'}
        </span>
      </div>
      {isOpen && (
        <div className="spv-review-section__content">
          {children}
        </div>
      )}
    </div>
  );
}

export function Step5Review({ data, onGenerate, isGenerating, error }) {
  const hasWarPeriods = data.warPeriods?.length > 0;
  const hasEventTypes = data.eventTypes?.length > 0;
  const hasWaterFeatures = data.waterFeatures?.length > 0;
  const hasLandscape = data.landscape?.length > 0;
  const hasLocalProducts = data.localProducts?.length > 0;
  const hasServices = data.services?.length > 0;

  return (
    <div className="spv-step">
      <p className="spv-review-intro">
        Vérifiez les informations saisies avant de générer le profil identitaire de votre village.
      </p>

      {/* Step 1: History */}
      <ReviewSection title="1. Histoire & Patrimoine" defaultOpen={true}>
        {hasWarPeriods && (
          <div>
            <strong>Périodes historiques:</strong>
            <ul className="spv-review-section__list">
              {getLabels('warPeriods', data.warPeriods).map((label, i) => (
                <li key={i}>{label}</li>
              ))}
            </ul>
          </div>
        )}
        {hasEventTypes && (
          <div>
            <strong>Types d'événements:</strong>
            <ul className="spv-review-section__list">
              {getLabels('eventTypes', data.eventTypes).map((label, i) => (
                <li key={i}>{label}</li>
              ))}
            </ul>
          </div>
        )}
        {data.monuments && <p><strong>Monuments:</strong> {data.monuments}</p>}
        {data.legends && <p><strong>Légendes:</strong> {data.legends}</p>}
        {data.historyOther && <p><strong>Autre:</strong> {data.historyOther}</p>}
        {!hasWarPeriods && !hasEventTypes && !data.monuments && !data.legends && !data.historyOther && (
          <p className="spv-review-section__empty">Aucune information saisie</p>
        )}
      </ReviewSection>

      {/* Step 2: Environment */}
      <ReviewSection title="2. Environnement & Ressources">
        {hasWaterFeatures && (
          <div>
            <strong>Éléments aquatiques:</strong>
            <ul className="spv-review-section__list">
              {getLabels('waterFeatures', data.waterFeatures).map((label, i) => (
                <li key={i}>{label}</li>
              ))}
            </ul>
          </div>
        )}
        {hasLandscape && (
          <div>
            <strong>Paysage:</strong>
            <ul className="spv-review-section__list">
              {getLabels('landscape', data.landscape).map((label, i) => (
                <li key={i}>{label}</li>
              ))}
            </ul>
          </div>
        )}
        {data.agriculture && <p><strong>Agriculture:</strong> {data.agriculture}</p>}
        {data.naturalResources && <p><strong>Ressources:</strong> {data.naturalResources}</p>}
        {data.environmentDescription && <p><strong>Description:</strong> {data.environmentDescription}</p>}
        {!hasWaterFeatures && !hasLandscape && !data.agriculture && !data.naturalResources && !data.environmentDescription && (
          <p className="spv-review-section__empty">Aucune information saisie</p>
        )}
      </ReviewSection>

      {/* Step 3: Economy */}
      <ReviewSection title="3. Économie, Traditions & Vie">
        {hasLocalProducts && (
          <div>
            <strong>Produits locaux:</strong>
            <ul className="spv-review-section__list">
              {getLabels('localProducts', data.localProducts).map((label, i) => (
                <li key={i}>{label}</li>
              ))}
            </ul>
          </div>
        )}
        {data.potentialProducts && <p><strong>Potentiel:</strong> {data.potentialProducts}</p>}
        {data.festivals && <p><strong>Fêtes:</strong> {data.festivals}</p>}
        {hasServices && (
          <div>
            <strong>Services:</strong>
            <ul className="spv-review-section__list">
              {getLabels('services', data.services).map((label, i) => (
                <li key={i}>{label}</li>
              ))}
            </ul>
          </div>
        )}
        {data.villageVibe && <p><strong>Ambiance:</strong> {LABELS.villageVibe[data.villageVibe] || data.villageVibe}</p>}
        {data.nearestTown && <p><strong>Connexions:</strong> {data.nearestTown}</p>}
        {data.liveHereDescription && <p><strong>Vie quotidienne:</strong> {data.liveHereDescription}</p>}
        {!hasLocalProducts && !data.potentialProducts && !data.festivals && !hasServices && !data.villageVibe && !data.nearestTown && !data.liveHereDescription && (
          <p className="spv-review-section__empty">Aucune information saisie</p>
        )}
      </ReviewSection>

      {/* Step 4: Free form */}
      <ReviewSection title="4. Description Libre">
        {data.freeDescription ? (
          <p>{data.freeDescription}</p>
        ) : (
          <p className="spv-review-section__empty">Aucune description saisie</p>
        )}
      </ReviewSection>

      {/* Generate button */}
      <div className="spv-generate-section">
        <button
          type="button"
          className="spv-generate-btn"
          onClick={onGenerate}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <span className="spv-generate-loading">
              <span className="spv-generate-spinner" />
              Génération en cours...
            </span>
          ) : (
            "Générer l'identité"
          )}
        </button>

        {error && (
          <div className="spv-generate-error">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
