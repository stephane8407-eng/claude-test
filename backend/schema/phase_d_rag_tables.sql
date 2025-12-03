-- ============================================================================
-- PHASE D: RAG Foundation Tables
-- Revival Case Studies + Funding Programs
-- ============================================================================

-- ============================================================================
-- TABLE 1: Revival Case Studies
-- Real-world examples of successful village revivals for AI context
-- ============================================================================

CREATE TABLE IF NOT EXISTS revival_case_studies (
    id SERIAL PRIMARY KEY,

    -- Village info
    village_name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(255),
    population_before INTEGER,
    population_after INTEGER,
    population_band VARCHAR(50),  -- 'under_100', '100_500', '500_1000', '1000_5000', '5000_plus'

    -- Revival details
    revival_type VARCHAR(100),  -- 'eco_village', 'artisan_hub', 'heritage_tourism', 'remote_work', 'agriculture'
    strategy TEXT NOT NULL,
    key_projects TEXT[],
    outcomes TEXT NOT NULL,
    lessons_learned TEXT,
    timeline_years INTEGER,

    -- Tags for matching
    themes TEXT[],
    geography_tags TEXT[],
    funding_sources TEXT[],

    -- Sources
    sources TEXT[],

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_case_studies_population_band ON revival_case_studies(population_band);
CREATE INDEX IF NOT EXISTS idx_case_studies_country ON revival_case_studies(country);
CREATE INDEX IF NOT EXISTS idx_case_studies_revival_type ON revival_case_studies(revival_type);
CREATE INDEX IF NOT EXISTS idx_case_studies_themes ON revival_case_studies USING GIN(themes);
CREATE INDEX IF NOT EXISTS idx_case_studies_geography ON revival_case_studies USING GIN(geography_tags);


-- ============================================================================
-- TABLE 2: Funding Programs
-- Grants and funding opportunities for village projects
-- ============================================================================

CREATE TABLE IF NOT EXISTS funding_programs (
    id SERIAL PRIMARY KEY,

    -- Basic info
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,

    -- Eligibility
    eligible_themes TEXT[],
    eligible_population_max INTEGER,

    -- Funding details
    funding_type VARCHAR(50),  -- 'grant', 'loan', 'subsidy', 'tax_credit', 'guarantee'
    amount_min INTEGER,
    amount_max INTEGER,
    funding_percentage_max INTEGER,

    -- Application info
    application_url TEXT,
    deadline_type VARCHAR(50),  -- 'rolling', 'annual', 'quarterly', 'one_time'
    deadline_date DATE,

    -- Process guidance
    process_summary TEXT,
    typical_timeline_months INTEGER,
    tips TEXT,

    -- Sources and status
    sources TEXT[],
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_funding_programs_country ON funding_programs(country);
CREATE INDEX IF NOT EXISTS idx_funding_programs_provider ON funding_programs(provider);
CREATE INDEX IF NOT EXISTS idx_funding_programs_themes ON funding_programs USING GIN(eligible_themes);
CREATE INDEX IF NOT EXISTS idx_funding_programs_active ON funding_programs(is_active);
CREATE INDEX IF NOT EXISTS idx_funding_programs_deadline ON funding_programs(deadline_date);


-- ============================================================================
-- SEED DATA: Revival Case Studies (15 examples)
-- ============================================================================

INSERT INTO revival_case_studies (
    village_name, country, region, population_before, population_after, population_band,
    revival_type, strategy, key_projects, outcomes, lessons_learned, timeline_years,
    themes, geography_tags, funding_sources, sources
) VALUES

-- 1. Saint-Pierre-de-Frugie (Dordogne, France)
(
    'Saint-Pierre-de-Frugie', 'France', 'Dordogne, Nouvelle-Aquitaine',
    75, 95, 'under_100',
    'eco_village',
    'Eco-village transformation focused on organic farming, renewable energy, and eco-tourism. The mayor led a comprehensive revival plan based on sustainable development principles.',
    ARRAY['Organic farming cooperative', 'Eco-tourism center', 'Renewable energy installations', 'Community gardens', 'Nature education programs'],
    'Population increased from 75 to 95 (+27%). Village became a model for rural ecological transition. Attracts 5,000+ visitors annually for eco-tourism. Featured in national media as example of successful rural revival.',
    'Start with quick wins to build momentum. Engage all generations. Nature assets are undervalued - they can anchor economic revival. Strong leadership from mayor was crucial.',
    8,
    ARRAY['ecology', 'agriculture', 'tourism', 'sustainability', 'community'],
    ARRAY['forest', 'streams', 'hills'],
    ARRAY['LEADER', 'FEADER', 'Région Nouvelle-Aquitaine'],
    ARRAY['https://www.saint-pierre-de-frugie.fr/', 'France 3 documentary']
),

-- 2. Montrol-Sénard (Haute-Vienne, France)
(
    'Montrol-Sénard', 'France', 'Haute-Vienne, Nouvelle-Aquitaine',
    180, 210, '100_500',
    'artisan_hub',
    'Artisan residency program that restored abandoned buildings for craftspeople workshops. Created an artist and artisan community that attracts visitors year-round.',
    ARRAY['Restored 6 historic buildings for artisan workshops', 'Annual craft fair (1,500+ visitors)', 'Artist residency program', 'Artisan school partnerships', 'Workshop tourism circuit'],
    'Population grew by 17%. Village now hosts 12 permanent artisan businesses. Annual craft fair attracts 1,500+ visitors. Featured in "Villages de Caractère" network.',
    'Heritage buildings are assets, not liabilities. Artisans attract other artisans - community effect. Tourism follows authentic experiences. Local partnerships with schools bring young energy.',
    5,
    ARRAY['artisan', 'heritage', 'tourism', 'craft', 'culture'],
    ARRAY['plateau', 'forest', 'rural'],
    ARRAY['Fondation du Patrimoine', 'Région Nouvelle-Aquitaine', 'Département Haute-Vienne'],
    ARRAY['https://www.montrol-senard.fr/']
),

-- 3. Châtel-Montagne (Allier, France)
(
    'Châtel-Montagne', 'France', 'Allier, Auvergne-Rhône-Alpes',
    290, 320, '100_500',
    'remote_work',
    'Remote work hub strategy with co-working space, high-speed internet infrastructure, and furnished apartments for digital nomads and remote workers.',
    ARRAY['Co-working space (15 desks)', 'Fiber optic deployment', 'Furnished apartments for remote workers', 'Monthly networking events', 'Partnership with Limoges tech companies'],
    'Attracted 25+ remote workers as new residents. Average age dropped by 8 years. New services opened (café, bike rental). Property values increased 15%.',
    'Infrastructure first - fast internet is non-negotiable. Target young families, not just individuals. Quality of life is the selling point. Create community events to integrate newcomers.',
    3,
    ARRAY['remote_work', 'digital', 'quality_of_life', 'young_families'],
    ARRAY['mountains', 'forest', 'valley'],
    ARRAY['France Relance', 'FEADER', 'Région Auvergne-Rhône-Alpes'],
    ARRAY['Les Échos article 2022']
),

-- 4. Marnay (Haute-Saône, France)
(
    'Marnay', 'France', 'Haute-Saône, Bourgogne-Franche-Comté',
    450, 520, '500_1000',
    'heritage_tourism',
    'Heritage restoration combined with wine tourism. Restored the château and created a wine trail connecting local producers with tourist accommodation.',
    ARRAY['Château restoration', 'Wine trail (12km)', 'Gîtes and B&Bs (6 properties)', 'Annual wine festival', 'Historic center pedestrianization'],
    'Tourism revenue increased 300%. 6 new accommodation businesses opened. Population grew 15%. Château hosts 8,000 visitors/year.',
    'Heritage and local products work together. Wine tourism attracts high-spending visitors. Restoration projects create local jobs. Partner with regional tourism boards.',
    6,
    ARRAY['heritage', 'wine', 'tourism', 'gastronomy', 'restoration'],
    ARRAY['vineyard', 'river', 'valley'],
    ARRAY['Fondation du Patrimoine', 'LEADER', 'Conseil Départemental'],
    ARRAY['Bourgogne Tourisme case study']
),

-- 5. Sainte-Croix (Switzerland)
(
    'Sainte-Croix', 'Switzerland', 'Vaud',
    450, 520, '500_1000',
    'heritage_tourism',
    'Music box heritage preservation combined with artisan tradition. Created a museum, artisan school, and annual music festival around the unique local craft.',
    ARRAY['Music Box Museum', 'Artisan school (watchmaking + music boxes)', 'Annual Fête de la Musique Mécanique', 'Restored historic workshops', 'Tourism circuit of ateliers'],
    'Became internationally known for music box heritage. Museum attracts 15,000 visitors/year. School trains 20 apprentices annually. Festival draws 5,000 visitors.',
    'Unique heritage is priceless - protect and promote it. Education ensures tradition survival. Festivals create annual peaks but year-round activities matter. International marketing works.',
    10,
    ARRAY['heritage', 'artisan', 'culture', 'tourism', 'education', 'music'],
    ARRAY['mountains', 'valley', 'jura'],
    ARRAY['Swiss Heritage Society', 'Canton de Vaud grants', 'Pro Helvetia'],
    ARRAY['https://www.sainte-croix.ch/', 'Musée CIMA']
),

-- 6. Albarracín (Spain)
(
    'Albarracín', 'Spain', 'Teruel, Aragón',
    1000, 1150, '1000_5000',
    'heritage_tourism',
    'Medieval heritage tourism strategy. Complete restoration of medieval walls and buildings, combined with cultural festivals and transformation of historic buildings into hotels.',
    ARRAY['Medieval walls restoration', 'Historic building hotels', 'Annual medieval festival', 'Guided heritage tours', 'Night lighting program', 'Artist residencies in historic center'],
    'Named "most beautiful village in Spain" by multiple surveys. Tourism increased 500%. Year-round occupation of historic hotels. Population stabilized and grew slightly.',
    'Authenticity is key - avoid over-restoration. Night lighting transforms the experience. Medieval festivals are popular across Europe. Balance tourism with livability.',
    15,
    ARRAY['heritage', 'medieval', 'tourism', 'culture', 'architecture'],
    ARRAY['mountains', 'rocky', 'river'],
    ARRAY['EU Heritage funds', 'Spanish Ministry of Culture', 'Aragón regional funds'],
    ARRAY['https://www.albarracin.es/', 'El País travel section']
),

-- 7. Colletta di Castelbianco (Italy)
(
    'Colletta di Castelbianco', 'Italy', 'Liguria',
    15, 45, 'under_100',
    'remote_work',
    'Pioneering telework village restoration. Completely restored abandoned medieval village with fiber optic infrastructure and remote work facilities.',
    ARRAY['Complete village restoration', 'Fiber optic deployment (1990s pioneer)', 'Remote work apartments', 'Conference facilities', 'Sustainable renovation'],
    'Village went from abandoned (15 elderly) to thriving community of 45 residents + visitors. Became early model for digital nomad villages. Featured in tech and architecture publications worldwide.',
    'Abandoned villages can be assets. Infrastructure investment pays off long-term. Design matters - hire good architects. Community rules essential for shared spaces.',
    7,
    ARRAY['remote_work', 'heritage', 'medieval', 'digital', 'architecture'],
    ARRAY['mountains', 'hilltop', 'mediterranean'],
    ARRAY['EU digital funds', 'Private investment', 'Liguria regional funds'],
    ARRAY['Wired magazine', 'Architectural Digest']
),

-- 8. Nohèdes (Pyrénées-Orientales, France)
(
    'Nohèdes', 'France', 'Pyrénées-Orientales, Occitanie',
    40, 65, 'under_100',
    'eco_village',
    'Eco-tourism combined with shepherd tradition revival. Created hiking trails, shepherd cheese production cooperative, and eco-lodges.',
    ARRAY['50km hiking trail network', 'Shepherd cheese cooperative', 'Eco-lodges (3 properties)', 'Nature interpretation center', 'Shepherd experience weekends'],
    'Population increased 60%. Cheese cooperative employs 8 people. 2,000+ overnight visitors/year. Featured in hiking guides as must-visit destination.',
    'Natural parks are allies - work with them. Traditional skills attract tourists. Hiking infrastructure has good ROI. Small population changes feel huge in tiny villages.',
    6,
    ARRAY['ecology', 'agriculture', 'tourism', 'tradition', 'hiking'],
    ARRAY['mountains', 'forest', 'valley', 'streams'],
    ARRAY['LEADER', 'Parc Naturel Régional des Pyrénées Catalanes', 'FEADER'],
    ARRAY['Parc Naturel des Pyrénées Catalanes']
),

-- 9. Rioja Alavesa wine villages (Spain)
(
    'Rioja Alavesa Villages', 'Spain', 'Álava, País Vasco',
    500, 600, '500_1000',
    'wine_tourism',
    'Wine architecture tourism strategy. Multiple villages collaborated to attract famous architects for winery buildings, creating a wine + architecture tourism circuit.',
    ARRAY['Marqués de Riscal winery (Frank Gehry)', 'Ysios winery (Calatrava)', 'Wine tourism routes', 'Luxury hotels in wineries', 'Collaborative regional marketing'],
    'Region became international wine tourism destination. Visitor numbers increased 400%. Property values doubled in some villages. Young winemakers moved to area.',
    'Collaboration between villages multiplies impact. Architecture as tourism magnet works. Luxury positioning attracts high-spending visitors. Wine tourism needs accommodation.',
    12,
    ARRAY['wine', 'architecture', 'tourism', 'luxury', 'gastronomy'],
    ARRAY['vineyard', 'valley', 'hills'],
    ARRAY['Basque Government', 'EU tourism funds', 'Private investment'],
    ARRAY['New York Times Travel', 'Lonely Planet']
),

-- 10. Camon (Ariège, France)
(
    'Camon', 'France', 'Ariège, Occitanie',
    140, 170, '100_500',
    'heritage_tourism',
    '"Plus Beaux Villages de France" certification strategy combined with rose festival. Restored abbey and developed rose gardens as unique attraction.',
    ARRAY['Abbey restoration', 'Rose gardens development', 'Annual Fête des Roses', 'Artist residencies', 'Gîtes in historic buildings', 'Photography weekends'],
    'Achieved "Plus Beaux Villages de France" label. Rose festival attracts 3,000 visitors. Year-round B&B occupation. Village featured in travel magazines.',
    'Certifications and labels matter for visibility. Unique theme (roses) creates identity. Festivals need year-round activities too. Photography tourism is growing segment.',
    8,
    ARRAY['heritage', 'culture', 'flowers', 'tourism', 'photography'],
    ARRAY['valley', 'river', 'pyrenees'],
    ARRAY['LEADER', 'Fondation du Patrimoine', 'Département Ariège'],
    ARRAY['Plus Beaux Villages de France', 'Géo magazine']
),

-- 11. Aubeterre-sur-Dronne (Charente, France)
(
    'Aubeterre-sur-Dronne', 'France', 'Charente, Nouvelle-Aquitaine',
    380, 420, '100_500',
    'heritage_tourism',
    'Underground church tourism combined with river activities. Leveraged unique monolithic church and Dronne river for heritage + outdoor tourism.',
    ARRAY['Underground church restoration and tourism', 'Kayak and canoe activities on Dronne', 'Beach on river (unique)', 'Plus Beaux Villages certification', 'Heritage interpretation center'],
    'Underground church attracts 50,000 visitors/year. River activities created 5 seasonal businesses. Population stabilized. Village regularly voted "most beautiful in France".',
    'Unique attractions need professional tourism management. River assets are underutilized in many villages. Summer activities need winter alternatives. Heritage + nature is powerful combination.',
    10,
    ARRAY['heritage', 'tourism', 'water', 'outdoor', 'religious'],
    ARRAY['river', 'valley', 'cliffs'],
    ARRAY['LEADER', 'Fondation du Patrimoine', 'Région Nouvelle-Aquitaine'],
    ARRAY['Plus Beaux Villages de France', 'Le Figaro travel']
),

-- 12. Lauzerte (Tarn-et-Garonne, France)
(
    'Lauzerte', 'France', 'Tarn-et-Garonne, Occitanie',
    1500, 1650, '1000_5000',
    'heritage_tourism',
    'Bastide heritage combined with Camino de Santiago pilgrimage route. Developed as key stop on the Via Podiensis with pilgrim services.',
    ARRAY['Pilgrim accommodation network', 'Heritage interpretation of bastide', 'Camino route infrastructure', 'Artisan market', 'Medieval festival'],
    'Receives 15,000 pilgrims annually. Year-round tourism from Camino. 10+ businesses focused on pilgrim services. Heritage tourism supplements pilgrim flow.',
    'Pilgrimage routes bring consistent visitors. Bastide heritage appeals to history lovers. Services for specific audiences (pilgrims) create niche economy. Walking tourism is growing.',
    8,
    ARRAY['heritage', 'pilgrimage', 'medieval', 'tourism', 'walking'],
    ARRAY['hilltop', 'valley', 'rural'],
    ARRAY['LEADER', 'Conseil Départemental', 'Région Occitanie'],
    ARRAY['Chemins de Compostelle', 'Plus Beaux Villages de France']
),

-- 13. Barfleur (Manche, France)
(
    'Barfleur', 'France', 'Manche, Normandie',
    600, 650, '500_1000',
    'heritage_tourism',
    'Maritime heritage tourism with fishing tradition. Developed tourism around historic port, lighthouse, and local fishing/seafood culture.',
    ARRAY['Lighthouse tourism development', 'Fishing heritage museum', 'Seafood festival', 'Port restoration', 'Boat trips', 'Plus Beaux Villages certification'],
    'Lighthouse receives 30,000 visitors/year. Seafood restaurants thriving. Population stable with seasonal growth. Featured in maritime tourism guides.',
    'Maritime heritage has strong appeal. Lighthouses are tourist magnets. Fishing culture is authentic attraction. Port villages need boat-related activities.',
    12,
    ARRAY['heritage', 'maritime', 'fishing', 'tourism', 'gastronomy'],
    ARRAY['coast', 'port', 'sea'],
    ARRAY['LEADER', 'Conservatoire du Littoral', 'Région Normandie'],
    ARRAY['Plus Beaux Villages de France', 'Normandie Tourisme']
),

-- 14. Conques (Aveyron, France)
(
    'Conques', 'France', 'Aveyron, Occitanie',
    270, 300, '100_500',
    'heritage_tourism',
    'Abbey and pilgrimage heritage combined with contemporary art. Unique strategy of installing Soulages stained glass windows in medieval abbey.',
    ARRAY['Soulages stained glass windows in abbey', 'Pilgrimage route stop', 'Medieval festival', 'Night illuminations', 'Artist residencies', 'Heritage center'],
    'Abbey attracts 600,000 visitors/year. Contemporary art drew international attention. Year-round tourism from Camino. Featured in art and architecture publications.',
    'Contemporary art in heritage sites can work brilliantly. Bold artistic choices create buzz. Pilgrimage + art attracts diverse audiences. Quality over quantity for small villages.',
    15,
    ARRAY['heritage', 'art', 'pilgrimage', 'religious', 'architecture'],
    ARRAY['valley', 'hills', 'river'],
    ARRAY['État (Monuments Historiques)', 'LEADER', 'Région Occitanie'],
    ARRAY['Le Monde', 'The Guardian travel', 'Plus Beaux Villages de France']
),

-- 15. Pérouges (Ain, France)
(
    'Pérouges', 'France', 'Ain, Auvergne-Rhône-Alpes',
    80, 110, 'under_100',
    'heritage_tourism',
    'Medieval village preservation with film location strategy. Restored fortified village became popular film location while developing heritage tourism.',
    ARRAY['Complete medieval village restoration', 'Film location services', 'Medieval heritage museum', 'Artisan workshops', 'Traditional galette bakery', 'Plus Beaux Villages certification'],
    'Village hosted 30+ film productions. 200,000 visitors/year. Traditional galette became regional specialty. Property values increased significantly.',
    'Film locations bring free marketing. Preserved villages are rare and valuable. Traditional food products extend the experience. Small population means careful crowd management needed.',
    20,
    ARRAY['heritage', 'medieval', 'film', 'tourism', 'gastronomy'],
    ARRAY['hilltop', 'plateau', 'fortified'],
    ARRAY['État (Monuments Historiques)', 'Département Ain', 'Région ARA'],
    ARRAY['Plus Beaux Villages de France', 'French Film Commission']
);


-- ============================================================================
-- SEED DATA: Funding Programs (15 French programs)
-- ============================================================================

INSERT INTO funding_programs (
    name, provider, country, eligible_themes, eligible_population_max,
    funding_type, amount_min, amount_max, funding_percentage_max,
    application_url, deadline_type, deadline_date,
    process_summary, typical_timeline_months, tips, sources, is_active
) VALUES

-- 1. LEADER (EU Rural Development)
(
    'LEADER', 'EU / État', 'France',
    ARRAY['rural_development', 'tourism', 'agriculture', 'heritage', 'ecology', 'artisan', 'local_products'],
    NULL,  -- No population limit
    'grant', 10000, 500000, 80,
    'https://www.europe-en-france.gouv.fr/fr/programmes-europeens/leader',
    'rolling', NULL,
    '1. Contact your local GAL (Groupe d''Action Locale). 2. Present project idea informally. 3. Submit full application with budget and timeline. 4. GAL committee reviews and votes. 5. If approved, sign convention and start project.',
    6,
    'Start 6 months before project start. Include local partnerships - GALs love collaboration. Saint-Pierre-de-Frugie waited 4 months. Focus on rural development impact, not just your village.',
    ARRAY['https://www.europe-en-france.gouv.fr/'],
    TRUE
),

-- 2. Petites Villes de Demain
(
    'Petites Villes de Demain', 'État (ANCT)', 'France',
    ARRAY['town_center', 'commerce', 'heritage', 'services', 'housing', 'mobility'],
    20000,
    'grant', 50000, 5000000, 80,
    'https://agence-cohesion-territoires.gouv.fr/petites-villes-de-demain-702',
    'rolling', NULL,
    '1. Municipality applies for program membership. 2. Once accepted, work with chef de projet. 3. Submit individual projects for funding. 4. Each project reviewed by ANCT.',
    12,
    'Requires multi-year action plan. Focus on tangible, visible projects. Having a dedicated chef de projet helps a lot. Combine with other funding sources.',
    ARRAY['https://agence-cohesion-territoires.gouv.fr/'],
    TRUE
),

-- 3. Fondation du Patrimoine
(
    'Fondation du Patrimoine', 'Fondation (private)', 'France',
    ARRAY['heritage', 'restoration', 'church', 'monument', 'historic_building', 'religious'],
    NULL,
    'grant', 5000, 100000, 30,
    'https://www.fondation-patrimoine.org/',
    'rolling', NULL,
    '1. Submit online application with photos and estimates. 2. Fondation reviews eligibility. 3. Site visit may be conducted. 4. Funding decision communicated. 5. Launch crowdfunding campaign (optional but recommended).',
    3,
    'Include community fundraising component - they love local engagement. Good for church restoration - they have specific programs. Estimates from heritage-certified contractors preferred.',
    ARRAY['https://www.fondation-patrimoine.org/'],
    TRUE
),

-- 4. FEADER (Rural Development Fund)
(
    'FEADER - Fonds Européen Agricole pour le Développement Rural', 'EU / État', 'France',
    ARRAY['agriculture', 'rural_development', 'ecology', 'forestry', 'local_products', 'agrotourism'],
    NULL,
    'grant', 10000, 500000, 80,
    'https://www.europe-en-france.gouv.fr/fr/fonds-europeens/fonds-europeen-agricole-pour-le-developpement-rural-FEADER',
    'rolling', NULL,
    '1. Contact regional agriculture authority (DDT or DRAAF). 2. Verify project fits regional program priorities. 3. Submit application with detailed budget. 4. Technical review. 5. Committee decision.',
    6,
    'Must fit regional rural development program priorities. Agricultural focus is key - even tourism projects need agriculture link. Partner with local farmers if possible.',
    ARRAY['https://www.europe-en-france.gouv.fr/'],
    TRUE
),

-- 5. DSIL (Dotation de Soutien à l''Investissement Local)
(
    'DSIL - Dotation de Soutien à l''Investissement Local', 'État', 'France',
    ARRAY['infrastructure', 'transition_energy', 'public_buildings', 'digital', 'environment'],
    NULL,
    'grant', 100000, 5000000, 50,
    'https://www.collectivites-locales.gouv.fr/',
    'annual', '2025-06-30',
    '1. Préfecture announces annual call. 2. Municipality submits project by deadline. 3. Préfecture reviews and prioritizes. 4. Funding allocated. 5. Project must start within 18 months.',
    9,
    'Prioritize projects with climate/energy impact - they score higher. Infrastructure projects preferred. Having co-financing helps. Submit early in the call period.',
    ARRAY['https://www.collectivites-locales.gouv.fr/'],
    TRUE
),

-- 6. France Relance - Rénovation Énergétique
(
    'France Relance - Rénovation Énergétique', 'État', 'France',
    ARRAY['energy', 'renovation', 'public_buildings', 'climate', 'insulation'],
    NULL,
    'grant', 50000, 2000000, 80,
    'https://france-relance.transformation.gouv.fr/',
    'rolling', NULL,
    '1. Identify public buildings for renovation. 2. Get energy audit. 3. Submit application with renovation plan. 4. ADEME or Préfecture reviews. 5. Funding decision.',
    4,
    'Energy audits are often required - budget for them. Focus on measurable energy savings. Schools and mairies are priority buildings. Can combine with other funding.',
    ARRAY['https://france-relance.transformation.gouv.fr/'],
    TRUE
),

-- 7. Fonds Vert
(
    'Fonds Vert', 'État', 'France',
    ARRAY['ecology', 'climate', 'biodiversity', 'water', 'nature', 'environment'],
    NULL,
    'grant', 10000, 1000000, 80,
    'https://www.ecologie.gouv.fr/fonds-vert',
    'rolling', NULL,
    '1. Check eligibility on Fonds Vert website. 2. Submit project via online platform. 3. Préfecture reviews. 4. Technical committee evaluates. 5. Funding decision.',
    4,
    'Climate and biodiversity projects are priorities. Water management projects do well. Include measurable environmental impact. Partner with environmental associations.',
    ARRAY['https://www.ecologie.gouv.fr/'],
    TRUE
),

-- 8. DETR (Dotation d''Équipement des Territoires Ruraux)
(
    'DETR - Dotation d''Équipement des Territoires Ruraux', 'État', 'France',
    ARRAY['rural_equipment', 'infrastructure', 'public_buildings', 'services'],
    20000,
    'grant', 20000, 500000, 50,
    'https://www.collectivites-locales.gouv.fr/',
    'annual', '2025-03-31',
    '1. Préfecture announces annual call. 2. Municipality submits project. 3. Local commission reviews. 4. Préfecture allocates funding. 5. Project execution.',
    6,
    'Small communes get priority. Rural equipment focus - practical projects. Submit multiple projects and prioritize them. Deadlines are strict.',
    ARRAY['https://www.collectivites-locales.gouv.fr/'],
    TRUE
),

-- 9. Région Nouvelle-Aquitaine - Ruralité
(
    'Région Nouvelle-Aquitaine - Contrat de Ruralité', 'Région Nouvelle-Aquitaine', 'France',
    ARRAY['rural_development', 'services', 'commerce', 'heritage', 'tourism', 'mobility'],
    NULL,
    'grant', 10000, 300000, 60,
    'https://les-aides.nouvelle-aquitaine.fr/',
    'rolling', NULL,
    '1. Check eligibility on regional website. 2. Contact local development officer. 3. Submit project application. 4. Regional committee reviews. 5. Convention signed if approved.',
    4,
    'Focus on services to population. Heritage projects with tourism angle do well. Partnership with EPCI helps. Mention regional priorities in application.',
    ARRAY['https://les-aides.nouvelle-aquitaine.fr/'],
    TRUE
),

-- 10. Mécénat (Corporate Sponsorship via Fondation)
(
    'Mécénat Entreprises', 'Fondations / Entreprises', 'France',
    ARRAY['heritage', 'culture', 'environment', 'education', 'social'],
    NULL,
    'grant', 5000, 200000, 100,
    'https://www.admical.org/',
    'rolling', NULL,
    '1. Identify potential corporate sponsors (local businesses, foundations). 2. Prepare compelling project dossier. 3. Contact sponsors directly or via foundations. 4. Negotiate terms. 5. Sign convention.',
    3,
    'Local businesses often interested in heritage projects. Banks and insurance companies have foundations. Visibility for sponsors is key selling point. Tax benefits make it attractive for companies.',
    ARRAY['https://www.admical.org/', 'https://www.fondationdefrance.org/'],
    TRUE
),

-- 11. Agence de l''Eau
(
    'Agence de l''Eau - Subventions', 'Agence de l''Eau', 'France',
    ARRAY['water', 'sanitation', 'ponds', 'rivers', 'wetlands', 'biodiversity'],
    NULL,
    'grant', 20000, 500000, 80,
    'https://www.lesagencesdeleau.fr/',
    'rolling', NULL,
    '1. Contact your local Agence de l''Eau. 2. Discuss project eligibility. 3. Submit application with technical details. 4. Technical review. 5. Funding decision.',
    4,
    'Water quality projects are priority. Pond restoration qualifies. Include biodiversity angle. Technical quality of project matters. Partner with water experts.',
    ARRAY['https://www.lesagencesdeleau.fr/'],
    TRUE
),

-- 12. Département - Aide aux Communes
(
    'Aide Départementale aux Communes', 'Département (varies)', 'France',
    ARRAY['rural_development', 'infrastructure', 'heritage', 'tourism', 'services'],
    NULL,
    'grant', 5000, 200000, 40,
    NULL,  -- Varies by department
    'annual', NULL,
    '1. Check department website for current programs. 2. Contact conseil départemental. 3. Submit application. 4. Department commission reviews. 5. Funding allocated.',
    4,
    'Every department has different programs - check yours. Small projects often easier to fund. Political relationships matter. Apply to multiple department programs.',
    ARRAY['Contact local Conseil Départemental'],
    TRUE
),

-- 13. MH - Monuments Historiques
(
    'Subvention Monuments Historiques', 'État (DRAC)', 'France',
    ARRAY['heritage', 'monument_historique', 'restoration', 'architecture'],
    NULL,
    'grant', 10000, 1000000, 50,
    'https://www.culture.gouv.fr/Aides-demarches/Protections-labels-et-டsignations/Monument-historique',
    'rolling', NULL,
    '1. Building must be classified or inscrit MH. 2. Submit restoration project to DRAC. 3. Architecte des Bâtiments de France reviews. 4. DRAC allocates funding. 5. Project executed under ABF supervision.',
    12,
    'Only for classified or inscrit monuments. ABF approval is mandatory. Use specialized heritage contractors. Long timeline but significant funding possible.',
    ARRAY['https://www.culture.gouv.fr/'],
    TRUE
),

-- 14. ADEME - Transition Écologique
(
    'ADEME - Aides à la Transition', 'ADEME', 'France',
    ARRAY['energy', 'climate', 'mobility', 'waste', 'circular_economy'],
    NULL,
    'grant', 20000, 500000, 70,
    'https://www.ademe.fr/collectivites-et-secteur-public/',
    'rolling', NULL,
    '1. Check ADEME website for current programs. 2. Contact regional ADEME office. 3. Discuss project eligibility. 4. Submit application. 5. Technical review and decision.',
    4,
    'Energy and mobility projects are priorities. Include measurable impact metrics. ADEME loves innovative approaches. Studies/audits can be funded separately.',
    ARRAY['https://www.ademe.fr/'],
    TRUE
),

-- 15. PAT - Projet Alimentaire Territorial
(
    'PAT - Projet Alimentaire Territorial', 'État / Région', 'France',
    ARRAY['agriculture', 'local_products', 'food', 'short_circuits', 'gastronomy'],
    NULL,
    'grant', 30000, 300000, 80,
    'https://agriculture.gouv.fr/pat-les-projets-alimentaires-territoriaux',
    'annual', '2025-09-30',
    '1. EPCI or commune initiates PAT project. 2. Conduct food system diagnosis. 3. Submit PAT application. 4. Ministry reviews and labels. 5. Access to funding for PAT actions.',
    8,
    'Partnership with EPCI often required. Local food system focus. Include all actors (producers, restaurants, cantines). Diagnostic phase can be funded separately.',
    ARRAY['https://agriculture.gouv.fr/'],
    TRUE
);


-- ============================================================================
-- UPDATE TRIGGER for updated_at columns
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for revival_case_studies
DROP TRIGGER IF EXISTS update_revival_case_studies_updated_at ON revival_case_studies;
CREATE TRIGGER update_revival_case_studies_updated_at
    BEFORE UPDATE ON revival_case_studies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for funding_programs
DROP TRIGGER IF EXISTS update_funding_programs_updated_at ON funding_programs;
CREATE TRIGGER update_funding_programs_updated_at
    BEFORE UPDATE ON funding_programs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================================

-- SELECT COUNT(*) as case_studies_count FROM revival_case_studies;
-- SELECT COUNT(*) as funding_programs_count FROM funding_programs;
-- SELECT village_name, country, revival_type FROM revival_case_studies;
-- SELECT name, provider, funding_type FROM funding_programs;
