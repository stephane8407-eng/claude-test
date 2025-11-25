-- Insert Chirac (pilot village with real data)
INSERT INTO villages (
    name, slug, description,
    latitude, longitude, country, department, region,
    population, area_km2,
    subscription_tier, subscription_status,
    settings
) VALUES (
    'Chirac',
    'chirac',
    'Village in Charente with 119 conflicts over 2,500 years. Known for Forges de l''Âge and 1944 Villages Brûlés.',
    45.9833, 0.5667,
    'FR', 'Charente', 'Nouvelle-Aquitaine',
    800, 21.5,
    'flagship', 'trial',
    '{
        "brand_color": "#DC2626",
        "show_conflicts": true,
        "show_ponds": true,
        "show_routes": true,
        "public_page_enabled": true
    }'
);

-- Insert Manot (test village #2)
INSERT INTO villages (
    name, slug, description,
    latitude, longitude, country, department, region,
    population, area_km2,
    subscription_tier, subscription_status,
    settings
) VALUES (
    'Manot',
    'manot',
    'Village near Chirac. Known for Château Salignac-Fénelon and Roman road.',
    45.9167, 0.5833,
    'FR', 'Charente', 'Nouvelle-Aquitaine',
    600, 18.0,
    'partner', 'active',
    '{
        "brand_color": "#2563EB",
        "show_conflicts": true,
        "show_ponds": false,
        "show_routes": false,
        "public_page_enabled": false
    }'
);

-- Link existing Chirac conflicts to Chirac village
UPDATE local_conflicts
SET village_id = (SELECT id FROM villages WHERE slug = 'chirac')
WHERE village_id IS NULL;

-- Verify
SELECT
    v.name,
    v.subscription_tier,
    COUNT(lc.id) as conflict_count
FROM villages v
LEFT JOIN local_conflicts lc ON v.id = lc.village_id
GROUP BY v.id, v.name, v.subscription_tier
ORDER BY v.name;
