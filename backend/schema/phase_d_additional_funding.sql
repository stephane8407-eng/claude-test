-- =====================================================
-- Phase D: Additional Funding Programs (Innovation Focus)
-- Run after phase_d_rag_tables.sql
-- =====================================================

INSERT INTO funding_programs (
  name, provider, country, eligible_themes, eligible_population_max,
  funding_type, amount_min, amount_max, funding_percentage_max,
  application_url, deadline_type, process_summary, typical_timeline_months,
  tips, is_active, created_at, updated_at
) VALUES

-- France 2030
(
  'France 2030 - Innovation Territoriale',
  'État (Secrétariat général pour l''investissement)',
  'France',
  ARRAY['innovation', 'technology', 'digital', 'industry', 'sustainability', 'energy', 'research'],
  NULL,
  'grant',
  50000, 2000000, 70,
  'https://www.gouvernement.fr/france-2030',
  'rolling',
  'Grand plan d''investissement pour l''innovation territoriale. Soutient projets innovants en transition écologique, numérique, et industrielle. Favorise projets structurants pour les territoires',
  18,
  'Privilégie projets avec partenariats recherche/industrie. Impact territorial important. Dossier technique solide requis. Innovation réelle (pas incrémentale)',
  true,
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),

-- BPI France
(
  'BPI France - Aide à l''Innovation',
  'BPI France (Banque Publique d''Investissement)',
  'France',
  ARRAY['innovation', 'technology', 'digital', 'industry', 'research', 'startup'],
  NULL,
  'grant_loan_mix',
  30000, 3000000, 45,
  'https://www.bpifrance.fr/catalogue-offres/soutien-innovation',
  'rolling',
  'Soutient entreprises innovantes et projets R&D. Subventions + prêts innovation + accompagnement. Différents dispositifs selon maturité projet',
  12,
  'Pour projets avec fort potentiel innovation et commercial. Dossier technique détaillé requis. Démonstrateur ou prototype valorisé. Plan de développement commercial essentiel',
  true,
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),

-- ADEME Enhanced
(
  'ADEME - Transition Écologique et Innovation',
  'ADEME (Agence de la transition écologique)',
  'France',
  ARRAY['ecology', 'energy', 'circular_economy', 'innovation', 'sustainability', 'waste', 'climate'],
  NULL,
  'grant',
  10000, 500000, 70,
  'https://agirpourlatransition.ademe.fr/',
  'calls',
  'Appels à projets transition écologique. Économie circulaire, énergies renouvelables, mobilité, innovation environnementale. Projets pilotes et démonstrateurs favorisés',
  14,
  'Forte dimension innovation + environnement requis. Projets démonstrateurs ou réplicables favorisés. Impact carbone mesurable. Partenariats techniques valorisés',
  true,
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),

-- Regional Innovation
(
  'Région Nouvelle-Aquitaine - Innovation et Développement',
  'Conseil Régional Nouvelle-Aquitaine',
  'France',
  ARRAY['innovation', 'digital', 'agriculture', 'industry', 'tourism', 'services'],
  NULL,
  'grant',
  5000, 200000, 50,
  'https://les-aides.nouvelle-aquitaine.fr/',
  'rolling',
  'Soutien à l''innovation dans tous secteurs. Accompagne TPE/PME et associations innovantes. Dispositifs spécifiques selon secteur',
  10,
  'Ancrage territorial en Nouvelle-Aquitaine requis. Innovation produit/service/process valorisée. Co-financement souvent nécessaire',
  true,
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),

-- Cooperative financing
(
  'France Active - Financement Coopératif et Solidaire',
  'Réseau France Active',
  'France',
  ARRAY['social', 'cooperative', 'services', 'employment', 'solidarity_economy'],
  NULL,
  'loan_guarantee',
  5000, 50000, NULL,
  'https://www.franceactive.org/',
  'rolling',
  'Prêts et garanties pour projets d''économie sociale et solidaire. Soutien création d''activité, emploi, utilité sociale. Accompagnement inclus',
  6,
  'Pour structures ESS (associations, coopératives, entreprises sociales). Utilité sociale démontrée. Viabilité économique requise. Garanties bancaires facilitées',
  true,
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Verification query
-- SELECT name, provider, funding_type, amount_max FROM funding_programs ORDER BY created_at DESC LIMIT 10;
