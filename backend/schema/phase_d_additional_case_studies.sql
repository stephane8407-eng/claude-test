-- =====================================================
-- Phase D: Additional Case Studies from Research + YouTube
-- Run after phase_d_rag_tables.sql
-- =====================================================

-- Update existing Saint-Pierre-de-Frugie with accurate data
UPDATE revival_case_studies
SET
  population_before = 360,
  population_after = 520,
  population_change_percent = 44.4,
  timeline_years = 13,
  strategy = 'Mayor Gilbert Chabaud implemented radical ecological strategy: banned pesticides completely, promoted organic farming and eco-construction, joined Périgord-Limousin natural park, created "écocentre" - training facility for ecological building. Attracted urban families ("néo-ruraux") seeking slow life and ecological transition',
  key_projects = ARRAY['Écocentre training facility', 'Pesticide ban (village-wide)', 'Organic farming conversion', 'Périgord-Limousin natural park partnership', 'Eco-construction promotion', 'Heritage and nature tourism'],
  outcomes = 'Population grew 44% (360→520) over 13 years - extremely rare growth for tiny rural commune. Village branded as "village bio". National media coverage (Le Monde). Became model for ecological transition in rural France',
  lessons_learned = 'Strong eco-branding works powerfully. "Village bio" narrative + training center + nature tourism = compelling combination. Radical ecological stance (complete pesticide ban) becomes unique selling point rather than liability. Long-term mayoral commitment essential (13+ years)',
  funding_sources = ARRAY['Natural park partnerships', 'LEADER rural development', 'Regional environmental grants', 'Eco-tourism revenue'],
  sources = ARRAY['https://www.lemonde.fr/en/france/article/2022/04/14/urban-exiles-find-their-eden-in-saint-pierre-de-frugie', 'Multiple French media coverage'],
  updated_at = CURRENT_TIMESTAMP
WHERE village_name = 'Saint-Pierre-de-Frugie';

-- Add population_change_percent column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='revival_case_studies' AND column_name='population_change_percent') THEN
        ALTER TABLE revival_case_studies ADD COLUMN population_change_percent DECIMAL(5,2);
    END IF;
END $$;

-- Correns: First 100% Organic Village
INSERT INTO revival_case_studies (
  village_name, country, region, population_before, population_after,
  population_band, revival_type, strategy,
  key_projects, outcomes, lessons_learned, timeline_years,
  themes, geography_tags, funding_sources, sources,
  created_at, updated_at
) VALUES (
  'Correns', 'France', 'Var (Provence-Alpes-Côte d''Azur)', 850, 920,
  '500_1000', 'organic_transition',
  'Under Mayor Michael Latz (from 1995), coordinated conversion of ALL village farming to organic, especially wine. Branded as "Premier village bio de France". Combined eco-identity with cultural heritage (Château Miraval - Pink Floyd recordings, Brad Pitt/Angelina Jolie connection). 100% organic viticulture achieved',
  ARRAY['100% organic viticulture conversion', 'All farming organic certified', 'Château Miraval cultural tourism', 'Organic terroir wine branding', 'Eco-wine tourism routes', 'Organic certification support'],
  'First fully organic village in France (100% of farming). All agriculture converted to organic. Celebrity-adjacent heritage (Château Miraval) combined with eco-identity attracted visitors and new residents. Model for local ecological transition widely cited nationally',
  '100% organic label is powerful differentiator. Combining agriculture + culture + celebrity creates unique identity impossible to replicate. Wine terroir + organic certification = premium positioning. Long-term mayoral vision essential (28+ years)',
  28,
  ARRAY['agriculture', 'organic', 'wine', 'culture', 'tourism', 'terroir'],
  ARRAY['rural', 'vineyard', 'provence', 'mediterranean', 'wine_region'],
  ARRAY['Regional agricultural support', 'Organic certification programs', 'Wine tourism development', 'Cultural heritage funds'],
  ARRAY['Widely documented as France first fully organic village', 'Model for organic transition'],
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Loos-en-Gohelle: Coal to Sustainability
INSERT INTO revival_case_studies (
  village_name, country, region, population_before, population_after,
  population_band, revival_type, strategy,
  key_projects, outcomes, lessons_learned, timeline_years,
  themes, geography_tags, funding_sources, sources,
  created_at, updated_at
) VALUES (
  'Loos-en-Gohelle', 'France', 'Pas-de-Calais (Hauts-de-France)', 6800, 7000,
  '5000_plus', 'industrial_transition',
  'Former coal mining town devastated by mine closures. Mayor Jean-François Caron led 25-year transformation into "ville pilote du développement durable". Reused old mine site (Base 11/19) as hub for eco-activities and sustainable businesses. Big rollout of solar roofs through local company partly owned by residents. Very strong citizen participation and storytelling about "coal to climate" transition',
  ARRAY['Coal waste terrils into UNESCO World Heritage sites', 'Base 11/19 eco-business hub', 'Community-owned solar roof company', 'Renewable energy projects', 'Circular economy initiatives', 'Innovation center creation', 'Industrial heritage cultural valorization'],
  'From dying coal town to sustainable development model. UNESCO World Heritage listing for industrial heritage (terrils). ADEME recognition as pilot sustainable city (2014). National and international recognition. Attracted green businesses and innovation projects. Citizen participation model',
  'Industrial heritage can become asset, not liability. Bold 25+ year vision + long-term mayoral commitment + strong partnerships = transformation. Innovation economy can replace extractive industry. Citizen ownership (solar company) creates buy-in. Storytelling essential: "coal to climate" narrative',
  25,
  ARRAY['industrial_heritage', 'energy_transition', 'innovation', 'sustainability', 'circular_economy', 'unesco', 'citizen_participation'],
  ARRAY['former_mining', 'post_industrial', 'northern_france', 'urban', 'industrial'],
  ARRAY['ADEME', 'EU structural funds', 'National sustainable development programs', 'UNESCO', 'Regional innovation funds'],
  ARRAY['https://www.socioeco.org/bdf_fiche-publication-1702_en.html', 'Widely documented as sustainable development model'],
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Pesmes: Architecture as Revival
INSERT INTO revival_case_studies (
  village_name, country, region, population_before, population_after,
  population_band, revival_type, strategy,
  key_projects, outcomes, lessons_learned, timeline_years,
  themes, geography_tags, funding_sources, sources,
  created_at, updated_at
) VALUES (
  'Pesmes', 'France', 'Haute-Saône (Bourgogne-Franche-Comté)', NULL, NULL,
  '500_1000', 'architecture_participatory',
  'Medieval village labeled "Plus Beau Village de France" but suffering depopulation and closure of cafés/bars. Architect Bernard Quirot created association "Avenir radieux" running summer architecture seminars with students + residents. Live experiment imagining concrete projects: turning farmhouse into municipal bar, re-thinking main street. Using architecture, design and cooperative renovation to revive social life and commerce',
  ARRAY['Avenir radieux architecture association', 'Summer seminars (students + residents)', 'Farmhouse to municipal bar conversion', 'Main street redesign', 'Participatory architecture workshops', 'Cultural events'],
  'Architecture and design as tools for social revival. Bringing students and residents together creates energy. Concrete projects (not just plans) essential. Municipal bar reopening from old farmhouse shows creative reuse',
  'Built heritage needs creative reuse, not just preservation. Participatory design creates ownership. Architecture students bring fresh energy. Design labs can be economic activity. Cultural events attract attention',
  5,
  ARRAY['architecture', 'heritage', 'participatory', 'design', 'culture', 'social'],
  ARRAY['rural', 'medieval', 'plus_beau_village', 'historic'],
  ARRAY['Fondation du Patrimoine (likely)', 'Regional cultural grants', 'Plus Beaux Villages label benefits'],
  ARRAY['Association Avenir radieux documented case'],
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Oxelaëre: Flemish Baker + Olympics + Multi-Service
INSERT INTO revival_case_studies (
  village_name, country, region, population_before, population_after,
  population_band, revival_type, strategy,
  key_projects, outcomes, lessons_learned, timeline_years,
  themes, geography_tags, funding_sources, sources,
  created_at, updated_at
) VALUES (
  'Oxelaëre', 'France', 'Nord (Hauts-de-France)', 500, 565,
  '500_1000', 'multi_service_social',
  'Small Flemish village. Mayor Stéphane Diezard (dairy farmer, 53) implemented comprehensive service retention strategy over 15 years. Commune purchased and renovated €1M restaurant building (€200k commune, €800k region/department). Low rent €800/month for 400m² to tenant restaurateurs. Restaurant serves school lunches 4x/week. Mayor personally supports baker (Fournil des Flandres) with all subsidy paperwork. Organizes 4-day "Jeux Olympiques flamands" festival. Built €2M maison de santé (70% public funding). Affordable housing in renovated town hall (€535/month, 30% below market)',
  ARRAY['Restaurant in renovated building (€1M)', 'School lunches at restaurant (18 students)', 'Baker support and expansion (€300k investment, 10 employees)', 'Jeux Olympiques flamands (4-day festival)', 'Maison de santé with intern apartment (€2M)', 'Affordable housing in town hall', 'Low-rent business spaces'],
  'Population growth +13% in 15 years while neighbors stagnate. Village Olympics attracted 2,000 people (4× village population). Baker expanded dramatically (bought 400m² space, doubled employees). Restaurant serves as social anchor. Strengthened Flemish cultural identity. Combat social isolation successfully',
  'Mayor as active facilitator, not passive administrator. Multi-service strategy more powerful than single intervention. Low rents to businesses = survival enabler. Cultural identity events (Olympics) = pride builder. Combining services (school lunches + restaurant) = financial sustainability. Mayor knows every resident personally ("Je connais le village sur le bout des doigts"). 15-year commitment essential',
  15,
  ARRAY['services', 'social', 'culture', 'bakery', 'restaurant', 'healthcare', 'housing', 'flemish_identity', 'festivals'],
  ARRAY['rural', 'flemish', 'northern_france', 'small_village'],
  ARRAY['Regional co-financing (€800k of €1M restaurant)', 'Department co-financing', 'Public subsidies 70% of maison de santé (€1.4M)', 'Commune investment (€200k+)', 'Festival partially self-funded (ticket sales)'],
  ARRAY['French TV documentary on village revival'],
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Saint-Saud-la-Coussière: British Residents + Cooperative Gas Station
INSERT INTO revival_case_studies (
  village_name, country, region, population_before, population_after,
  population_band, revival_type, strategy,
  key_projects, outcomes, lessons_learned, timeline_years,
  themes, geography_tags, funding_sources, sources,
  created_at, updated_at
) VALUES (
  'Saint-Saud-la-Coussière', 'France', 'Dordogne (Nouvelle-Aquitaine)', 1500, 1000,
  '500_1000', 'international_residents_services',
  'Village declined from 1,500 (1960s) to 900, lost 20 of 30 shops. Mayor Pierre Duval (80 years) implemented multi-pronged survival strategy. Attracted ~100 British residents (15% of population) with quality of life and 30% cheaper housing (trend started 1980s, continued despite Brexit). Mayor actively subsidizes critical services: lends low-rent space (€300/month free for 1 year) to physiotherapist in commune-purchased maison de santé. Opened cooperative gas station (only one within 20km): 34 residents financed €290k (€169k raised in 10 days from shareholders aged 20-95, €115k bank loan). Built shared senior residence (8 people). Mayor gives municipal land to attract businesses',
  ARRAY['Cooperative gas station (34 shareholders, €290k)', 'British resident attraction (100 people)', 'Subsidized healthcare space', 'Shared senior residence (€40k land donation)', 'Hair salon via TV show recruitment', 'Jérôme Garon meat processing facility (10 employees)', 'Active pharmacy retention efforts'],
  'Critical mass of services maintained despite 33% population decline. British residents provide economic base (high purchasing power, consume locally). Gas station as "acte militant" - residents intentionally support it. Cooperative shareholder model mobilized €169k in 10 days. Next generation returning (Jérôme from Poitiers, Émilie from Nancy). School stable at 36 students',
  'International residents (British) = economic lifeline. Cooperative financing works (gas station: 34 villagers pooled €169k). Mayor actively giving land attracts businesses. Services viewed as survival necessity. "Acte militant" framing = community buy-in. Pharmacy vulnerability shows limits - some services need external solutions. Multi-generational strategy: support next gen to return',
  15,
  ARRAY['international_residents', 'british', 'cooperative', 'services', 'gas_station', 'healthcare', 'senior_housing', 'meat_processing'],
  ARRAY['rural', 'perigord', 'dordogne', 'declining'],
  ARRAY['Cooperative shareholder model (€169k local)', 'Bank loan (€115k)', 'Commune land donations (€40k+)', 'Self-financed businesses (Jérôme)'],
  ARRAY['French TV documentary', 'TV show SOS Village (TF1)'],
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Pettorano sul Gizio: Bear Smart Community
INSERT INTO revival_case_studies (
  village_name, country, region, population_before, population_after,
  population_band, revival_type, strategy,
  key_projects, outcomes, lessons_learned, timeline_years,
  themes, geography_tags, funding_sources, sources,
  created_at, updated_at
) VALUES (
  'Pettorano sul Gizio', 'Italy', 'Abruzzo', NULL, NULL,
  '500_1000', 'rewilding_ecotourism',
  'Tiny medieval village shrinking badly. Became Italy''s first "Bear Smart Community" coexisting with critically endangered Marsican brown bear. After conflicts with bears raiding livestock, installed bear-proof bins, electric fencing, modified water tanks, road warning devices. Ran big public education campaign. Damage dropped ~99% by 2017, no incidents since 2020',
  ARRAY['Bear-proof infrastructure (bins, fencing, tanks)', 'Road warning devices', 'Public education campaign', 'Bear-themed tourism experiences', 'Nature-based local business support'],
  'Turned human-wildlife conflict into eco-tourism opportunity. Visitor numbers and new residents increased. Local businesses offering bear-themed, nature experiences. Model for "living with wildlife". Rewilding narrative attracts specific tourism segment',
  'Flagship species (bears) = powerful story. Technical solutions (bear-proof infrastructure) enable coexistence. Education changes attitudes. Wildlife can be economic asset, not just cost. Rewilding attracts urban visitors seeking nature. Science + local participation essential',
  8,
  ARRAY['rewilding', 'ecotourism', 'wildlife', 'bears', 'conservation', 'nature'],
  ARRAY['rural', 'medieval', 'mountains', 'italian', 'apennines'],
  ARRAY['Conservation grants', 'Wildlife protection programs', 'Eco-tourism development', 'Research partnerships'],
  ARRAY['The Guardian 2025', 'The Atlantic', 'WorldHeritageOutlook.iucn.org'],
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Candela: Financial Incentives Italy
INSERT INTO revival_case_studies (
  village_name, country, region, population_before, population_after,
  population_band, revival_type, strategy,
  key_projects, outcomes, lessons_learned, timeline_years,
  themes, geography_tags, funding_sources, sources,
  created_at, updated_at
) VALUES (
  'Candela', 'Italy', 'Puglia', 8000, 2700,
  '1000_5000', 'financial_incentives',
  'Population fell from 8,000 to 2,700. Mayor launched offer of up to €2,000 for newcomers (different amounts for singles, couples, families) IF they live full-time and have job or start business. Part of broader Italian trend of "incentive villages"',
  ARRAY['€2,000 cash incentives for newcomers', 'Job/business requirement', 'Cheap housing availability', 'Business startup support'],
  'Direct financial incentives attract attention but require economic foundation (jobs). Similar schemes across Italy and Sardinia. Combined with cheap housing. Success depends on quality of life + economic opportunity, not just money',
  'Money alone insufficient - must have jobs/business opportunities. €2,000 attracts interest but retention needs more. Cheap housing important draw. Business support essential. Works best when combined with quality of life improvements',
  3,
  ARRAY['incentives', 'financial', 'housing', 'business_support'],
  ARRAY['rural', 'italian', 'southern_italy', 'declining'],
  ARRAY['Municipal budget for incentives', 'Regional business support'],
  ARRAY['Relocate.World', 'Expatriate Group', 'Widely covered in international media'],
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Ponga: Baby Bonuses Spain
INSERT INTO revival_case_studies (
  village_name, country, region, population_before, population_after,
  population_band, revival_type, strategy,
  key_projects, outcomes, lessons_learned, timeline_years,
  themes, geography_tags, funding_sources, sources,
  created_at, updated_at
) VALUES (
  'Ponga', 'Spain', 'Asturias', 600, 600,
  '500_1000', 'demographic_incentives',
  'Village of ~600. Offers €3,000 per baby born + €3,000/year for next 3 years. Requirement: parents must stay in village. Direct demographic intervention',
  ARRAY['€3,000 baby bonus', '€3,000/year for 3 years', 'Residency requirement'],
  'Birth rate increased from ~3/year to 8-10/year. Families motivated to stay. Direct demographic impact measurable. Relatively low cost per family (€12,000 over 3 years) vs value of retaining young families',
  'Baby bonuses work when families already considering village life. Retention of young families has multiplier effects (school, services, vitality). €12k over 3 years = reasonable investment. Must combine with jobs and services',
  5,
  ARRAY['demographic', 'families', 'babies', 'incentives'],
  ARRAY['rural', 'spanish', 'mountains', 'asturias'],
  ARRAY['Municipal budget', 'Regional support'],
  ARRAY['Widely covered as innovative demographic policy'],
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Benarrabá: Digital Nomad Hub
INSERT INTO revival_case_studies (
  village_name, country, region, population_before, population_after,
  population_band, revival_type, strategy,
  key_projects, outcomes, lessons_learned, timeline_years,
  themes, geography_tags, funding_sources, sources,
  created_at, updated_at
) VALUES (
  'Benarrabá', 'Spain', 'Andalusia', 500, 500,
  '100_500', 'digital_nomad_remote_work',
  'Village of ~500. Partnered with remote work platforms. Offers free coworking space + accommodation for digital nomads to test living in Spanish village. Targets remote workers and freelancers',
  ARRAY['Free coworking space', 'Free/subsidized accommodation trials', 'Remote work platform partnerships', 'Digital infrastructure (fiber)'],
  'Steady stream of young professionals visiting and testing village life. Some stayed permanently and started businesses. Successfully attracted young demographic. Model for tapping into remote work trend',
  'Remote work trend = opportunity for villages. Free trials let people test before committing. Digital infrastructure (fiber) essential. Partnerships with platforms bring visibility. Young professionals bring economic activity + energy',
  3,
  ARRAY['digital_nomad', 'remote_work', 'coworking', 'young_professionals'],
  ARRAY['rural', 'spanish', 'andalusia', 'mountain_village'],
  ARRAY['EU digital village programs', 'Regional tourism', 'Platform partnerships'],
  ARRAY['Featured in remote work media', 'Digital nomad platforms'],
  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Verification query
-- SELECT village_name, country, revival_type, timeline_years FROM revival_case_studies ORDER BY created_at DESC;
