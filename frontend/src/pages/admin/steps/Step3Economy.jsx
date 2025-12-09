/**
 * Step 3: Économie, Traditions & Vie (Economy, Traditions & Life)
 */
import '../IdentityAuditWizard.css';

const LOCAL_PRODUCTS = [
  { id: 'cheese', label: 'Fromage' },
  { id: 'wine', label: 'Vin' },
  { id: 'honey', label: 'Miel' },
  { id: 'fish', label: 'Poisson' },
  { id: 'crafts', label: 'Artisanat' },
  { id: 'bread', label: 'Pain / boulangerie' },
  { id: 'meat', label: 'Charcuterie / viande' },
  { id: 'vegetables', label: 'Légumes / maraîchage' },
  { id: 'fruits', label: 'Fruits' },
  { id: 'cider', label: 'Cidre' },
  { id: 'spirits', label: 'Spiritueux' },
  { id: 'pottery', label: 'Poterie' },
  { id: 'textiles', label: 'Textiles' },
  { id: 'wood', label: 'Travail du bois' },
];

const SERVICES = [
  { id: 'school', label: 'École' },
  { id: 'shop', label: 'Commerce alimentaire' },
  { id: 'cafe', label: 'Café / bar' },
  { id: 'restaurant', label: 'Restaurant' },
  { id: 'post_office', label: 'Bureau de poste' },
  { id: 'medical', label: 'Médecin / infirmier' },
  { id: 'pharmacy', label: 'Pharmacie' },
  { id: 'bank', label: 'Banque / distributeur' },
  { id: 'library', label: 'Bibliothèque' },
  { id: 'sports', label: 'Équipements sportifs' },
  { id: 'church', label: 'Église (services réguliers)' },
  { id: 'internet', label: 'Internet haut débit' },
];

const VILLAGE_VIBES = [
  { id: 'calm', label: 'Calme et paisible' },
  { id: 'lively', label: 'Animé et vivant' },
  { id: 'family', label: 'Familial' },
  { id: 'artistic', label: 'Artistique / créatif' },
  { id: 'eco', label: 'Écologique / durable' },
  { id: 'remote', label: 'Isolé / préservé' },
  { id: 'touristic', label: 'Touristique' },
  { id: 'agricultural', label: 'Rural / agricole' },
  { id: 'historic', label: 'Historique / patrimonial' },
  { id: 'dynamic', label: 'Dynamique / en renouveau' },
];

export function Step3Economy({ data, onChange }) {
  const handleCheckboxChange = (field, value) => {
    const current = data[field] || [];
    const updated = current.includes(value)
      ? current.filter(v => v !== value)
      : [...current, value];
    onChange({ [field]: updated });
  };

  const handleTextChange = (field, value) => {
    onChange({ [field]: value });
  };

  return (
    <div className="spv-step">
      {/* Local Products */}
      <div className="spv-form-group">
        <label className="spv-form-label">
          Produits locaux existants
        </label>
        <p className="spv-form-hint">
          Productions locales actuellement commercialisées
        </p>
        <div className="spv-checkbox-group">
          {LOCAL_PRODUCTS.map(product => (
            <label key={product.id} className="spv-checkbox">
              <input
                type="checkbox"
                className="spv-checkbox__input"
                checked={(data.localProducts || []).includes(product.id)}
                onChange={() => handleCheckboxChange('localProducts', product.id)}
              />
              <span className="spv-checkbox__label">{product.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Potential Products */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="potentialProducts">
          Produits potentiels non encore développés
        </label>
        <p className="spv-form-hint">
          Ce qui pourrait être valorisé mais ne l'est pas encore
        </p>
        <textarea
          id="potentialProducts"
          className="spv-form-textarea"
          value={data.potentialProducts || ''}
          onChange={(e) => handleTextChange('potentialProducts', e.target.value)}
          placeholder="Ex: Champignons sauvages, plantes médicinales, anciens savoir-faire..."
        />
      </div>

      <hr className="spv-section-divider" />

      {/* Festivals */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="festivals">
          Fêtes et événements annuels
        </label>
        <p className="spv-form-hint">
          Dates, types d'événements, fréquentation estimée
        </p>
        <textarea
          id="festivals"
          className="spv-form-textarea"
          value={data.festivals || ''}
          onChange={(e) => handleTextChange('festivals', e.target.value)}
          placeholder="Ex: Fête patronale le 15 août (~200 personnes), marché de Noël, foire aux bestiaux..."
        />
      </div>

      <hr className="spv-section-divider" />

      {/* Services */}
      <div className="spv-form-group">
        <label className="spv-form-label">
          Services présents dans le village
        </label>
        <p className="spv-form-hint">
          Infrastructures et services disponibles
        </p>
        <div className="spv-checkbox-group">
          {SERVICES.map(service => (
            <label key={service.id} className="spv-checkbox">
              <input
                type="checkbox"
                className="spv-checkbox__input"
                checked={(data.services || []).includes(service.id)}
                onChange={() => handleCheckboxChange('services', service.id)}
              />
              <span className="spv-checkbox__label">{service.label}</span>
            </label>
          ))}
        </div>
      </div>

      <hr className="spv-section-divider" />

      {/* Village Vibe */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="villageVibe">
          Ambiance du village
        </label>
        <p className="spv-form-hint">
          Comment décririez-vous l'atmosphère générale ?
        </p>
        <select
          id="villageVibe"
          className="spv-form-select"
          value={data.villageVibe || ''}
          onChange={(e) => handleTextChange('villageVibe', e.target.value)}
        >
          <option value="">Sélectionnez une ambiance...</option>
          {VILLAGE_VIBES.map(vibe => (
            <option key={vibe.id} value={vibe.id}>
              {vibe.label}
            </option>
          ))}
        </select>
      </div>

      {/* Nearest Town */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="nearestTown">
          Ville la plus proche et connexions
        </label>
        <p className="spv-form-hint">
          Distance, moyens de transport disponibles
        </p>
        <input
          type="text"
          id="nearestTown"
          className="spv-form-input"
          value={data.nearestTown || ''}
          onChange={(e) => handleTextChange('nearestTown', e.target.value)}
          placeholder="Ex: Confolens à 15 km (voiture), gare SNCF à Limoges (45 min)"
        />
      </div>

      {/* What's it like to live here */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="liveHereDescription">
          Comment est la vie ici au quotidien ?
        </label>
        <p className="spv-form-hint">
          Ce qui fait le charme (ou les difficultés) de la vie quotidienne
        </p>
        <textarea
          id="liveHereDescription"
          className="spv-form-textarea"
          value={data.liveHereDescription || ''}
          onChange={(e) => handleTextChange('liveHereDescription', e.target.value)}
          placeholder="Décrivez le quotidien : tranquillité, entraide, accès aux services, activités..."
        />
      </div>
    </div>
  );
}
