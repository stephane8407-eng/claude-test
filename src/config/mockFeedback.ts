/**
 * Mock AI Feedback Generator
 *
 * This file simulates AI-powered artwork feedback.
 *
 * 🔄 HOW TO REPLACE WITH REAL AI:
 *
 * 1. Create an API route (e.g., /api/analyze-artwork)
 * 2. In that API route, call a vision AI model:
 *    - OpenAI GPT-4 Vision
 *    - Anthropic Claude with vision
 *    - Google Gemini Vision
 *    - Any other multimodal AI
 *
 * 3. Send the image (base64 or URL) + metadata to the AI
 * 4. Ask the AI to analyze and return JSON in this structure:
 *    {
 *      summary: string,
 *      positives: Array<{aspect: string, comment: string}>,
 *      improvements: Array<{area: string, suggestion: string, howTo?: string}>,
 *      miniExercise: {title: string, description: string, materials?: string[], estimatedTime?: string},
 *      encouragement: string
 *    }
 *
 * 5. Replace the call to getMockFeedback() in /feedback page with:
 *    const response = await fetch('/api/analyze-artwork', {
 *      method: 'POST',
 *      body: JSON.stringify({ image: imageDataUrl, metadata }),
 *    });
 *    const feedback = await response.json();
 *
 * EXAMPLE PROMPT FOR AI:
 * "You are an encouraging art instructor. Analyze this abstract painting.
 *  The artist is [experienceLevel] and working in [style] style.
 *  Provide: 1) A brief summary, 2) 2-3 positive aspects, 3) 2-3 constructive improvements,
 *  4) A mini practice exercise, 5) Encouraging closing words.
 *  Return response as JSON matching this structure: {...}"
 */

import {
  ArtworkFeedback,
  ArtworkMetadata,
  FeedbackExperienceLevel,
  FeedbackStyle,
} from '@/types/feedback';

/**
 * Mock feedback generator
 * Returns realistic-looking feedback based on user's metadata
 *
 * 🚀 REPLACE THIS FUNCTION with a real API call to an AI vision model
 */
export async function getMockFeedback(metadata: ArtworkMetadata): Promise<ArtworkFeedback> {
  // Simulate network delay (remove this when using real API)
  await new Promise((resolve) => setTimeout(resolve, 2000));

  const { experienceLevel, style } = metadata;

  // Generate contextual feedback based on metadata
  return generateContextualFeedback(experienceLevel, style);
}

/**
 * Internal helper: generate feedback based on context
 * This simulates different feedback for different user profiles
 */
function generateContextualFeedback(
  experienceLevel: FeedbackExperienceLevel,
  style: FeedbackStyle
): ArtworkFeedback {
  // Base feedback templates - mix and match based on context
  const summaries = {
    'just-starting': {
      'acrylic-pouring':
        'This is a great start to your acrylic pouring journey! Your paint consistency looks good, and you\'re starting to understand how colors interact in a pour. There\'s clear potential here.',
      'palette-knife':
        'Excellent first steps with the palette knife! You\'re showing good instinct for texture and bold strokes. Your confidence is already beginning to show through the work.',
      'mixed-media':
        'What a wonderful exploration of mixed media! You\'re experimenting with layers and different materials, which is exactly the right approach for a beginner. Keep exploring!',
      'not-sure':
        'This piece shows curiosity and willingness to experiment - exactly what you need as a beginner! You\'re building foundational skills that will serve you well as you discover your preferred style.',
    },
    'some-experience': {
      'acrylic-pouring':
        'Your understanding of acrylic pouring is developing nicely. The paint flow shows control, and you\'re making thoughtful decisions about color placement. Ready to take it to the next level!',
      'palette-knife':
        'Your palette knife technique is maturing beautifully. There\'s intentionality in your mark-making, and you\'re starting to develop a recognizable approach. The texture work is particularly strong.',
      'mixed-media':
        'Your mixed media layering shows confidence and experimentation. You\'re combining materials thoughtfully, and there\'s a growing sense of composition and balance in your work.',
      'not-sure':
        'This piece demonstrates solid foundational skills and growing confidence. You\'re past the complete beginner stage and starting to make more intentional artistic choices.',
    },
    confident: {
      'acrylic-pouring':
        'This is confident, controlled pouring work. Your mastery of paint consistency and flow is evident, and you\'re making sophisticated color choices. The technique execution is strong.',
      'palette-knife':
        'Your palette knife work shows maturity and confidence. The texture, composition, and color harmony all demonstrate a developed skill set. You\'re clearly comfortable with the medium.',
      'mixed-media':
        'Strong, confident mixed media work with thoughtful layering and material choices. You\'re balancing complexity with coherence, and your artistic voice is coming through clearly.',
      'not-sure':
        'This is accomplished work that shows technical confidence and artistic maturity. You have a solid grasp of fundamentals and are making intentional creative decisions.',
    },
  };

  const positiveAspects = {
    'acrylic-pouring': [
      {
        aspect: 'Color harmony',
        comment:
          'Your color choices work well together. The palette feels cohesive, and the colors complement rather than compete with each other.',
      },
      {
        aspect: 'Paint consistency',
        comment:
          'The flow of your paint suggests you\'ve got the paint-to-medium ratio dialed in nicely. This is crucial for successful pours!',
      },
      {
        aspect: 'Cell formation',
        comment:
          'Beautiful cells throughout the piece! You\'re using silicone effectively and applying heat at the right moments.',
      },
    ],
    'palette-knife': [
      {
        aspect: 'Texture variation',
        comment:
          'Excellent range of textures - from smooth blended areas to thick impasto. This creates visual interest and dimension.',
      },
      {
        aspect: 'Bold mark-making',
        comment:
          'Your strokes are confident and decisive. This energy translates into a dynamic, engaging piece.',
      },
      {
        aspect: 'Color mixing',
        comment:
          'Nice color transitions and blending directly on the canvas. This shows good control of the palette knife technique.',
      },
    ],
    'mixed-media': [
      {
        aspect: 'Layering complexity',
        comment:
          'The layers build beautifully on each other, creating depth and visual intrigue. You\'re balancing transparency and opacity well.',
      },
      {
        aspect: 'Material integration',
        comment:
          'Your choice of materials (paper, paint, texture) works harmoniously. Nothing feels forced or out of place.',
      },
      {
        aspect: 'Composition balance',
        comment:
          'Good eye for composition - the piece feels balanced without being too symmetrical. There\'s movement and flow.',
      },
    ],
    'not-sure': [
      {
        aspect: 'Color choices',
        comment:
          'Your color palette is pleasing and shows good instinct for what works together.',
      },
      {
        aspect: 'Willingness to experiment',
        comment:
          'The piece shows you\'re not afraid to try things, which is essential for growth as an artist.',
      },
      {
        aspect: 'Composition',
        comment:
          'There\'s an intuitive sense of balance and flow in how you\'ve arranged elements.',
      },
    ],
  };

  const improvementAreas = {
    'just-starting': [
      {
        area: 'Composition planning',
        suggestion:
          'Consider planning your color placement before pouring. Even a rough mental map can help create more intentional compositions.',
        howTo:
          'Before your next piece, decide which 2-3 colors you want to dominate and where. Sketch a simple diagram if helpful.',
      },
      {
        area: 'Contrast',
        suggestion:
          'Experiment with adding more contrast - either through color (light vs. dark) or texture (smooth vs. rough).',
        howTo:
          'Try including one very light and one very dark color in your next piece, or mix thick and thin paint application.',
      },
    ],
    'some-experience': [
      {
        area: 'Focal point',
        suggestion:
          'The piece could benefit from a stronger focal point - an area that draws the eye first.',
        howTo:
          'Try reserving your brightest color or most contrasting element for one specific area rather than distributing it evenly.',
      },
      {
        area: 'Depth and dimension',
        suggestion:
          'Push the sense of depth by creating more distinction between foreground, middle ground, and background.',
        howTo:
          'Use darker, cooler colors to recede and brighter, warmer colors to come forward. Layer intentionally to build dimension.',
      },
    ],
    confident: [
      {
        area: 'Risk-taking',
        suggestion:
          'You have strong technical skills - now push yourself to take more creative risks and break your own rules.',
        howTo:
          'Try a technique or color combination that feels uncomfortable or "wrong" to you. Sometimes breaking our patterns leads to breakthroughs.',
      },
      {
        area: 'Refinement',
        suggestion:
          'Consider where subtle refinements could elevate the piece - small additions of highlights, shadows, or details.',
        howTo:
          'Step back and identify 2-3 small areas where a touch of light, a bit more contrast, or a refined edge would enhance the overall impact.',
      },
    ],
  };

  const miniExercises = {
    'acrylic-pouring': {
      title: 'Controlled Color Placement Exercise',
      description:
        'Create three small pours (on A5 boards) where you intentionally control where each color goes. For one, keep all blues on the left and warm colors on the right. For another, create a color gradient from light to dark. For the third, aim for one dominant color with small pops of contrast. This builds intentionality.',
      materials: ['3 small canvas boards', '3-5 paint colors', 'Pouring medium'],
      estimatedTime: '1-2 hours',
    },
    'palette-knife': {
      title: 'Texture Study in Monochrome',
      description:
        'Using only white paint (or one color + white), create a small abstract piece focusing entirely on texture variation. Use different knife sizes and angles. Make some areas smooth, some heavily textured, some with visible knife marks. This exercise helps you see texture independent of color.',
      materials: ['Canvas board', 'White paint (or one color)', 'Multiple palette knives'],
      estimatedTime: '1 hour',
    },
    'mixed-media': {
      title: 'Layer Reveal Exercise',
      description:
        'Start with a collaged layer of papers and magazine clippings. Paint over 80% of it. Then selectively scrape, sand, or tear through the paint layer to reveal the collage beneath. This teaches you about controlling reveal and concealment in mixed media work.',
      materials: ['Canvas or thick paper', 'Collage materials', 'Acrylic paint', 'Sandpaper'],
      estimatedTime: '1-2 hours',
    },
    'not-sure': {
      title: 'Three-Technique Exploration',
      description:
        'Create three small pieces, each using a different technique: one pour, one palette knife, one mixed media/collage. Use the same color palette for all three. This helps you discover which technique feels most natural and enjoyable while maintaining consistency.',
      materials: ['3 small surfaces', 'One cohesive color palette', 'Various tools and mediums'],
      estimatedTime: '2-3 hours',
    },
  };

  // Select appropriate feedback based on user profile
  const summary = summaries[experienceLevel][style];
  const positives = positiveAspects[style].slice(0, 3);
  const improvements =
    experienceLevel === 'just-starting'
      ? improvementAreas['just-starting']
      : experienceLevel === 'some-experience'
      ? improvementAreas['some-experience']
      : improvementAreas['confident'];
  const miniExercise = miniExercises[style];

  const encouragementMessages = [
    'Keep creating, keep experimenting, and most importantly - keep enjoying the process. You\'re on a wonderful creative journey!',
    'Remember: every piece you create is a step forward in your artistic development. Celebrate your progress!',
    'Your willingness to learn and grow as an artist is evident. Trust the process and keep painting!',
    'Art is not about perfection - it\'s about expression and exploration. You\'re doing beautifully!',
    'Each brushstroke, each pour, each layer teaches you something new. Embrace the learning journey!',
  ];

  const encouragement =
    encouragementMessages[Math.floor(Math.random() * encouragementMessages.length)];

  return {
    summary,
    positives,
    improvements: improvements.slice(0, 2),
    miniExercise,
    encouragement,
  };
}

/**
 * 🔄 EXAMPLE: How to call a real AI API
 *
 * export async function getRealAIFeedback(metadata: ArtworkMetadata): Promise<ArtworkFeedback> {
 *   const response = await fetch('/api/analyze-artwork', {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json' },
 *     body: JSON.stringify({
 *       image: metadata.imageDataUrl,
 *       experienceLevel: metadata.experienceLevel,
 *       style: metadata.style,
 *     }),
 *   });
 *
 *   if (!response.ok) {
 *     throw new Error('Failed to analyze artwork');
 *   }
 *
 *   return response.json();
 * }
 *
 * Then in /app/api/analyze-artwork/route.ts:
 *
 * export async function POST(request: Request) {
 *   const { image, experienceLevel, style } = await request.json();
 *
 *   // Call OpenAI, Claude, or other vision AI
 *   const aiResponse = await callVisionAI(image, experienceLevel, style);
 *
 *   return Response.json(aiResponse);
 * }
 */
