/**
 * Step 2: Environnement & Ressources (Environment & Resources)
 */
import '../IdentityAuditWizard.css';

const WATER_FEATURES = [
  { id: 'ponds', label: 'Étangs' },
  { id: 'river', label: 'Rivière' },
  { id: 'lake', label: 'Lac' },
  { id: 'springs', label: 'Sources' },
  { id: 'marshes', label: 'Marais / zones humides' },
  { id: 'streams', label: 'Ruisseaux' },
  { id: 'wells', label: 'Puits historiques' },
  { id: 'fountains', label: 'Fontaines' },
];

const LANDSCAPE_TYPES = [
  { id: 'forest', label: 'Forêt' },
  { id: 'mountains', label: 'Montagnes' },
  { id: 'plateau', label: 'Plateau' },
  { id: 'valley', label: 'Vallée' },
  { id: 'plain', label: 'Plaine' },
  { id: 'coast', label: 'Côte / littoral' },
  { id: 'hills', label: 'Collines' },
  { id: 'bocage', label: 'Bocage' },
  { id: 'vineyards', label: 'Vignobles' },
  { id: 'meadows', label: 'Prairies' },
];

export function Step2Environment({ data, onChange }) {
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
      {/* Water Features */}
      <div className="spv-form-group">
        <label className="spv-form-label">
          Éléments aquatiques
        </label>
        <p className="spv-form-hint">
          Sélectionnez les types d'eau présents sur votre territoire
        </p>
        <div className="spv-checkbox-group">
          {WATER_FEATURES.map(feature => (
            <label key={feature.id} className="spv-checkbox">
              <input
                type="checkbox"
                className="spv-checkbox__input"
                checked={(data.waterFeatures || []).includes(feature.id)}
                onChange={() => handleCheckboxChange('waterFeatures', feature.id)}
              />
              <span className="spv-checkbox__label">{feature.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Landscape */}
      <div className="spv-form-group">
        <label className="spv-form-label">
          Type de paysage
        </label>
        <p className="spv-form-hint">
          Caractéristiques géographiques de votre environnement
        </p>
        <div className="spv-checkbox-group">
          {LANDSCAPE_TYPES.map(type => (
            <label key={type.id} className="spv-checkbox">
              <input
                type="checkbox"
                className="spv-checkbox__input"
                checked={(data.landscape || []).includes(type.id)}
                onChange={() => handleCheckboxChange('landscape', type.id)}
              />
              <span className="spv-checkbox__label">{type.label}</span>
            </label>
          ))}
        </div>
      </div>

      <hr className="spv-section-divider" />

      {/* Agriculture */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="agriculture">
          Agriculture et élevage
        </label>
        <p className="spv-form-hint">
          Types d'animaux, cultures, pratiques agricoles présentes ou passées
        </p>
        <textarea
          id="agriculture"
          className="spv-form-textarea"
          value={data.agriculture || ''}
          onChange={(e) => handleTextChange('agriculture', e.target.value)}
          placeholder="Ex: Élevage bovin, cultures céréalières, apiculture, polyculture traditionnelle..."
        />
      </div>

      {/* Natural Resources */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="naturalResources">
          Ressources naturelles
        </label>
        <p className="spv-form-hint">
          Bois, pierre, granite, argile, métaux, tourbe, etc.
        </p>
        <textarea
          id="naturalResources"
          className="spv-form-textarea"
          value={data.naturalResources || ''}
          onChange={(e) => handleTextChange('naturalResources', e.target.value)}
          placeholder="Ex: Carrières de granite, forêts de chênes, gisements d'argile..."
        />
      </div>

      {/* Environment Description */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="environmentDescription">
          Décrivez votre environnement naturel
        </label>
        <p className="spv-form-hint">
          Ce qui rend votre cadre naturel unique ou remarquable
        </p>
        <textarea
          id="environmentDescription"
          className="spv-form-textarea"
          value={data.environmentDescription || ''}
          onChange={(e) => handleTextChange('environmentDescription', e.target.value)}
          placeholder="Décrivez la beauté de votre paysage, les points de vue remarquables, la faune et la flore..."
        />
      </div>
    </div>
  );
}
