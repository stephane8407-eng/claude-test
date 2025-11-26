-- Insert POI types (shared across all villages)
INSERT INTO poi_types (name, name_plural, category, icon, color, description) VALUES
('pond', 'ponds', 'water', 'water', '#3B82F6', 'Natural or artificial pond'),
('church', 'churches', 'religious', 'church', '#DC2626', 'Church or chapel'),
('château', 'châteaux', 'heritage', 'castle', '#F59E0B', 'Castle or manor house'),
('mill', 'mills', 'heritage', 'industry', '#10B981', 'Water or wind mill'),
('fountain', 'fountains', 'water', 'fountain', '#06B6D4', 'Public fountain or spring'),
('cross', 'crosses', 'religious', 'cross', '#8B5CF6', 'Wayside cross or calvary'),
('wash_house', 'wash_houses', 'heritage', 'wash', '#6366F1', 'Traditional wash house'),
('war_memorial', 'war_memorials', 'heritage', 'memorial', '#EF4444', 'War memorial or monument');

-- Get village IDs
DO $$
DECLARE
    chirac_id INTEGER;
    manot_id INTEGER;
BEGIN
    SELECT id INTO chirac_id FROM villages WHERE slug = 'chirac';
    SELECT id INTO manot_id FROM villages WHERE slug = 'manot';

    -- Insert 15 ponds for Chirac
    INSERT INTO pois (village_id, poi_type_id, name, description, latitude, longitude, attributes, source) VALUES
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang de la Forge', 'Historic pond near the old forge', 45.9850, 0.5680, '{"surface_area_m2": 2500}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang du Moulin', 'Pond by the old mill', 45.9840, 0.5690, '{"surface_area_m2": 1800}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang des Prés', 'Meadow pond', 45.9830, 0.5650, '{"surface_area_m2": 3200}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang Neuf', 'New pond', 45.9860, 0.5670, '{"surface_area_m2": 1500}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang de Châtenet', 'Châtenet pond', 45.9820, 0.5640, '{"surface_area_m2": 2200}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang de la Lande', 'Heath pond', 45.9870, 0.5700, '{"surface_area_m2": 1900}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang de Beaumont', 'Beaumont pond', 45.9810, 0.5660, '{"surface_area_m2": 2800}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang du Bois', 'Forest pond', 45.9880, 0.5720, '{"surface_area_m2": 2100}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang de la Vallée', 'Valley pond', 45.9800, 0.5630, '{"surface_area_m2": 3500}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang Rond', 'Round pond', 45.9890, 0.5710, '{"surface_area_m2": 1200}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang de la Croix', 'Cross pond', 45.9790, 0.5620, '{"surface_area_m2": 2600}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang Saint-Martin', 'Saint Martin pond', 45.9900, 0.5730, '{"surface_area_m2": 1700}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang du Château', 'Castle pond', 45.9780, 0.5610, '{"surface_area_m2": 4000}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang de la Fontaine', 'Fountain pond', 45.9910, 0.5740, '{"surface_area_m2": 1400}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'pond'), 'Étang des Granges', 'Barn pond', 45.9770, 0.5600, '{"surface_area_m2": 2300}', 'manual_entry');

    -- Insert 3 churches for Chirac
    INSERT INTO pois (village_id, poi_type_id, name, description, latitude, longitude, attributes, source) VALUES
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'church'), 'Église Saint-Pierre', 'Main parish church, 12th century Romanesque', 45.9833, 0.5667, '{"construction_year": 1150, "style": "Romanesque", "protected": true}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'church'), 'Chapelle Notre-Dame', 'Chapel near the village center', 45.9845, 0.5655, '{"construction_year": 1600, "style": "Gothic"}', 'manual_entry'),
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'church'), 'Chapelle de la Forge', 'Small chapel by the forge', 45.9820, 0.5680, '{"construction_year": 1750}', 'manual_entry');

    -- Insert 1 château for Chirac
    INSERT INTO pois (village_id, poi_type_id, name, description, latitude, longitude, attributes, source) VALUES
    (chirac_id, (SELECT id FROM poi_types WHERE name = 'château'), 'Château de Chirac', 'Historic castle with Renaissance features', 45.9840, 0.5670, '{"construction_year": 1450, "style": "Renaissance", "protected": true, "open_to_public": false}', 'manual_entry');

END $$;

-- Verify counts
SELECT
    v.name as village,
    pt.name as poi_type,
    COUNT(p.id) as count
FROM villages v
LEFT JOIN pois p ON v.id = p.village_id
LEFT JOIN poi_types pt ON p.poi_type_id = pt.id
GROUP BY v.name, pt.name
ORDER BY v.name, pt.name;

-- Summary by village
SELECT
    v.name as village,
    COUNT(p.id) as total_pois
FROM villages v
LEFT JOIN pois p ON v.id = p.village_id
GROUP BY v.name
ORDER BY v.name;
