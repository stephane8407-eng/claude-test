/**
 * Step 1: Histoire & Patrimoine (History & Heritage)
 */
import '../IdentityAuditWizard.css';

const WAR_PERIODS = [
  { id: 'wwii', label: 'Seconde Guerre mondiale (1939-1945)' },
  { id: 'wwi', label: 'Première Guerre mondiale (1914-1918)' },
  { id: 'revolution', label: 'Révolution française (1789-1799)' },
  { id: 'religious_wars', label: 'Guerres de religion (XVIe siècle)' },
  { id: 'hundred_years', label: 'Guerre de Cent Ans (1337-1453)' },
  { id: 'medieval', label: 'Période médiévale' },
  { id: 'roman', label: 'Époque romaine' },
  { id: 'prehistoric', label: 'Préhistoire' },
];

const EVENT_TYPES = [
  { id: 'battles', label: 'Batailles' },
  { id: 'burned_villages', label: 'Villages brûlés' },
  { id: 'sieges', label: 'Sièges' },
  { id: 'raids', label: 'Raids / pillages' },
  { id: 'garrison', label: 'Garnison / occupation' },
  { id: 'resistance', label: 'Résistance' },
  { id: 'massacres', label: 'Massacres' },
  { id: 'liberation', label: 'Libération' },
];

export function Step1History({ data, onChange }) {
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
      {/* War Periods */}
      <div className="spv-form-group">
        <label className="spv-form-label">
          Périodes de guerre et conflits
        </label>
        <p className="spv-form-hint">
          Sélectionnez les périodes historiques qui ont marqué votre village
        </p>
        <div className="spv-checkbox-group">
          {WAR_PERIODS.map(period => (
            <label key={period.id} className="spv-checkbox">
              <input
                type="checkbox"
                className="spv-checkbox__input"
                checked={(data.warPeriods || []).includes(period.id)}
                onChange={() => handleCheckboxChange('warPeriods', period.id)}
              />
              <span className="spv-checkbox__label">{period.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Event Types */}
      <div className="spv-form-group">
        <label className="spv-form-label">
          Types d'événements
        </label>
        <p className="spv-form-hint">
          Quels types d'événements historiques ont eu lieu ?
        </p>
        <div className="spv-checkbox-group">
          {EVENT_TYPES.map(type => (
            <label key={type.id} className="spv-checkbox">
              <input
                type="checkbox"
                className="spv-checkbox__input"
                checked={(data.eventTypes || []).includes(type.id)}
                onChange={() => handleCheckboxChange('eventTypes', type.id)}
              />
              <span className="spv-checkbox__label">{type.label}</span>
            </label>
          ))}
        </div>
      </div>

      <hr className="spv-section-divider" />

      {/* Notable Monuments */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="monuments">
          Monuments et patrimoine notable
        </label>
        <p className="spv-form-hint">
          Église, château, mémoriaux, vestiges, bâtiments historiques...
        </p>
        <input
          type="text"
          id="monuments"
          className="spv-form-input"
          value={data.monuments || ''}
          onChange={(e) => handleTextChange('monuments', e.target.value)}
          placeholder="Ex: Église romane du XIIe siècle, ruines du château, monument aux morts..."
        />
      </div>

      {/* Legends & Folklore */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="legends">
          Légendes et folklore
        </label>
        <p className="spv-form-hint">
          Histoires locales, légendes, traditions orales, personnages célèbres...
        </p>
        <textarea
          id="legends"
          className="spv-form-textarea"
          value={data.legends || ''}
          onChange={(e) => handleTextChange('legends', e.target.value)}
          placeholder="Racontez les légendes et histoires transmises dans votre village..."
        />
      </div>

      {/* Other history */}
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="historyOther">
          Autre chose sur votre histoire ?
        </label>
        <p className="spv-form-hint">
          Tout ce qui n'entre pas dans les catégories ci-dessus
        </p>
        <textarea
          id="historyOther"
          className="spv-form-textarea"
          value={data.historyOther || ''}
          onChange={(e) => handleTextChange('historyOther', e.target.value)}
          placeholder="Événements particuliers, anecdotes historiques, archives locales..."
        />
      </div>
    </div>
  );
}
