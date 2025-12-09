/**
 * Mock Identity Generator
 *
 * Returns realistic sample data for Phase C.
 * Will be replaced by real AI endpoint in production.
 */

export async function mockGenerateIdentity(formData) {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Build contextual responses based on form data
  const hasWW2 = formData.warPeriods?.includes('wwii');
  const hasBurnedVillages = formData.eventTypes?.includes('burned_villages');
  const hasPonds = formData.waterFeatures?.includes('ponds');
  const hasForest = formData.landscape?.includes('forest');
  const hasChurch = formData.monuments?.toLowerCase().includes('église');

  // Generate summary based on inputs
  let summaryIdentity = '';
  if (hasWW2 && hasBurnedVillages) {
    summaryIdentity = 'Village marqué par la Seconde Guerre mondiale, où la mémoire des villages brûlés forge une identité de résilience et de renouveau.';
  } else if (hasPonds) {
    summaryIdentity = 'Village paisible autour de ses étangs historiques, où l\'eau façonne le paysage et les traditions depuis des siècles.';
  } else if (hasForest) {
    summaryIdentity = 'Village forestier aux traditions rurales préservées, niché au cœur d\'un écrin de verdure.';
  } else {
    summaryIdentity = 'Village authentique aux racines profondes, gardien d\'un patrimoine vivant et d\'une communauté soudée.';
  }

  // Generate long identity
  let longIdentity = `Ce village incarne l'esprit de la ruralité française, où chaque pierre raconte une histoire et chaque chemin mène à une découverte. `;

  if (hasWW2) {
    longIdentity += `La mémoire de la Seconde Guerre mondiale reste vive dans les cœurs, témoignant de la résilience d'une communauté qui a su se relever et préserver son identité. `;
  }

  if (hasPonds) {
    longIdentity += `Les étangs qui parsèment le territoire offrent non seulement un écosystème riche mais aussi un potentiel touristique encore inexploité. `;
  }

  if (hasForest) {
    longIdentity += `La forêt environnante, poumon vert de la commune, invite à la randonnée et à la découverte d'une nature préservée. `;
  }

  longIdentity += `Aujourd'hui, le village cherche à valoriser ce patrimoine unique tout en construisant un avenir dynamique pour ses habitants.`;

  // Generate live here summary
  let liveHereSummary = formData.liveHereDescription || '';
  if (!liveHereSummary) {
    liveHereSummary = `Vivre ici, c'est choisir le calme et l'authenticité. `;
    if (formData.services?.includes('school')) {
      liveHereSummary += `L'école du village maintient une vie communautaire active. `;
    }
    if (formData.nearestTown) {
      liveHereSummary += `La proximité de ${formData.nearestTown.split(' ')[0]} offre un accès facile aux services et commerces. `;
    }
    liveHereSummary += `Les habitants cultivent l'entraide et le sens de la communauté, valeurs qui font la richesse de cette vie rurale.`;
  }

  // Generate themes
  const themes = [];

  if (hasWW2 || hasBurnedVillages) {
    themes.push({
      title: 'Forges de la Résilience',
      confidence: 0.82,
      description: [
        'Les conflits historiques ont forgé l\'identité du village',
        'La mémoire des villages brûlés crée un potentiel touristique patrimonial',
        'La communauté démontre un schéma de reconstruction et de renouveau',
      ],
      tourism_ideas: [
        'Créer un circuit mémoire reliant les lieux historiques avec des QR codes',
        'Organiser des événements de commémoration attirant des visiteurs régionaux',
      ],
    });
  }

  if (hasPonds) {
    themes.push({
      title: 'Eaux du Temps',
      confidence: 0.78,
      description: [
        'Le réseau d\'étangs historiques structure la géographie du village',
        'L\'eau a façonné les activités économiques traditionnelles',
        'Les plans d\'eau offrent des opportunités de tourisme durable',
      ],
      tourism_ideas: [
        'Développer la pêche touristique et l\'éducation écologique',
        'Créer un sentier écologique connectant les différents plans d\'eau',
      ],
    });
  }

  if (hasForest) {
    themes.push({
      title: 'Sentiers Verts',
      confidence: 0.75,
      description: [
        'La forêt constitue un patrimoine naturel majeur',
        'Les chemins forestiers offrent un potentiel de randonnée',
        'La biodiversité locale peut être mise en valeur',
      ],
      tourism_ideas: [
        'Aménager des sentiers de randonnée balisés',
        'Proposer des sorties nature guidées',
      ],
    });
  }

  // Ensure at least one theme
  if (themes.length === 0) {
    themes.push({
      title: 'Racines et Renouveau',
      confidence: 0.70,
      description: [
        'Le village préserve ses traditions tout en évoluant',
        'Le patrimoine bâti témoigne d\'une histoire riche',
        'La communauté locale reste le cœur vivant du village',
      ],
      tourism_ideas: [
        'Mettre en valeur le patrimoine architectural',
        'Développer des événements festifs traditionnels',
      ],
    });
  }

  // Generate suggested projects
  const suggested_projects = [];

  if (hasWW2 || hasBurnedVillages) {
    suggested_projects.push({
      title: 'Circuit Mémoire: Villages Brûlés',
      short_description: 'Créer un parcours de découverte reliant les sites historiques avec des panneaux interprétatifs et des QR codes',
      themes: ['ww2', 'patrimoine', 'tourisme'],
      difficulty: 'moderate',
      estimated_timeline_months: 12,
      estimated_budget_range: '30000-60000',
      inspired_by: null,
      potential_funding: [],
      first_steps: [],
    });
  }

  if (hasPonds) {
    suggested_projects.push({
      title: 'Valorisation des Étangs Historiques',
      short_description: 'Développer le tourisme de pêche et l\'éducation écologique autour des étangs',
      themes: ['etangs', 'eco', 'tourisme'],
      difficulty: 'easy',
      estimated_timeline_months: 6,
      estimated_budget_range: '10000-25000',
      inspired_by: null,
      potential_funding: [],
      first_steps: [],
    });
  }

  if (hasForest) {
    suggested_projects.push({
      title: 'Sentiers de Découverte Nature',
      short_description: 'Aménager et baliser des chemins de randonnée avec signalétique sur la faune et la flore',
      themes: ['nature', 'randonnee', 'famille'],
      difficulty: 'easy',
      estimated_timeline_months: 8,
      estimated_budget_range: '15000-40000',
      inspired_by: null,
      potential_funding: [],
      first_steps: [],
    });
  }

  // Always add a community project
  suggested_projects.push({
    title: 'Fête du Village Renouvelée',
    short_description: 'Revitaliser la fête annuelle avec des activités pour tous les âges et la promotion des produits locaux',
    themes: ['communaute', 'traditions', 'local'],
    difficulty: 'easy',
    estimated_timeline_months: 4,
    estimated_budget_range: '5000-15000',
    inspired_by: null,
    potential_funding: [],
    first_steps: [],
  });

  return {
    summaryIdentity,
    longIdentity,
    liveHereSummary,
    themes,
    suggested_projects,
  };
}
