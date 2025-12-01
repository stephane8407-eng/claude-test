/**
 * Step 4: Description Libre (Free Description)
 */
import '../IdentityAuditWizard.css';

export function Step4FreeForm({ data, onChange }) {
  const handleTextChange = (value) => {
    onChange({ freeDescription: value });
  };

  const charCount = (data.freeDescription || '').length;

  return (
    <div className="spv-step">
      <div className="spv-form-group">
        <label className="spv-form-label" htmlFor="freeDescription">
          Racontez votre village avec vos mots
        </label>
        <p className="spv-form-hint">
          Ce que vous aimez, ce qui vous inquiète, ce que vous aimeriez voir dans 10 ans.
          C'est l'occasion de partager votre vision personnelle du village.
        </p>
        <textarea
          id="freeDescription"
          className="spv-form-textarea spv-form-textarea--large"
          value={data.freeDescription || ''}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder="Parlez librement de votre village...

Par exemple:
- Ce qui rend votre village unique
- Les défis auxquels vous faites face
- Vos rêves pour l'avenir
- Les projets en cours ou souhaités
- Ce qui fait la fierté des habitants
- Les traditions que vous souhaitez préserver"
          style={{ minHeight: '250px' }}
        />
        <div className="spv-char-count">
          <span className={charCount > 100 ? 'spv-char-count--good' : ''}>
            {charCount} caractères
          </span>
          {charCount < 100 && (
            <span className="spv-char-count__hint">
              (minimum recommandé : 100 caractères)
            </span>
          )}
        </div>
      </div>

      <div className="spv-free-form-tips">
        <h4 className="spv-free-form-tips__title">Quelques idées pour vous inspirer</h4>
        <ul className="spv-free-form-tips__list">
          <li>Quel est votre souvenir préféré de ce village ?</li>
          <li>Qu'est-ce qui manque le plus aux habitants ?</li>
          <li>Si vous pouviez montrer une seule chose à un visiteur, ce serait quoi ?</li>
          <li>Y a-t-il des projets dont vous rêvez mais qui semblent impossibles ?</li>
          <li>Qu'est-ce que les anciens racontaient sur ce village ?</li>
        </ul>
      </div>
    </div>
  );
}
