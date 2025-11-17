/**
 * Learning Plan Configuration
 *
 * This file contains 4-week learning plans for different styles.
 *
 * HOW TO EDIT:
 * - Modify tasks in existing weeks
 * - Add new weeks or tasks
 * - Create new plans for different styles
 * - Adjust estimatedTime based on timeAvailable from user profile
 *
 * The app will automatically select and customize the plan based on user's style choice.
 */

import { LearningPlan, StudioTip } from '@/types/plan';

/**
 * Acrylic Pouring 4-Week Plan
 */
export const ACRYLIC_POURING_PLAN: LearningPlan = {
  style: 'acrylic-pouring',
  weeks: [
    {
      weekNumber: 1,
      title: 'Foundations & First Pours',
      description: 'Learn the basics of paint consistency, simple pour techniques, and setup.',
      keyFocus: 'Understanding paint-to-medium ratios and basic pouring mechanics',
      tasks: [
        {
          id: 'ap-w1-t1',
          title: 'Set up your pouring station',
          description:
            'Organize your space with protective covering, elevate your canvas (use cups or small containers), and gather all materials within reach.',
          estimatedTime: '30 minutes',
        },
        {
          id: 'ap-w1-t2',
          title: 'Mix and test paint consistency',
          description:
            'Practice mixing 2-3 colors with pouring medium. Aim for "warm honey" consistency - it should flow off the stir stick in a smooth ribbon.',
          estimatedTime: '45 minutes',
        },
        {
          id: 'ap-w1-t3',
          title: 'Your first dirty pour',
          description:
            'Layer 3-4 colors in one cup and pour onto a small canvas board. Tilt gently to spread paint. Don\'t overthink it - just observe how the paint moves!',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'ap-w1-t4',
          title: 'Practice a simple flip cup',
          description:
            'Layer colors in a cup, place canvas on top, flip quickly. Lift the cup and let paint flow. Try 2-3 small boards to see variations.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'ap-w1-t5',
          title: 'Document and reflect',
          description:
            'Take photos of your pieces. Note what worked, what didn\'t, and which color combinations you liked. This reflection is crucial for learning.',
          estimatedTime: '15 minutes',
        },
      ],
    },
    {
      weekNumber: 2,
      title: 'Cells, Color Harmony & Technique Variations',
      description: 'Experiment with creating cells, explore color theory, and try new pouring methods.',
      keyFocus: 'Color mixing, creating cells with silicone, and expanding technique repertoire',
      tasks: [
        {
          id: 'ap-w2-t1',
          title: 'Experiment with silicone for cells',
          description:
            'Add 1-2 drops of silicone oil to some of your paint colors (not all). Pour and use a heat gun or torch to pop cells. Try different amounts to see the effect.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'ap-w2-t2',
          title: 'Try a tree ring pour',
          description:
            'Pour concentric circles of color in the center of your canvas, then use a straw or stick to drag lines from center outward, creating a mandala-like effect.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'ap-w2-t3',
          title: 'Explore complementary color schemes',
          description:
            'Choose a complementary pair (e.g., blue & orange, red & green) and create 2 small pours using those colors plus white. Notice how they interact.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'ap-w2-t4',
          title: 'Practice a swipe technique',
          description:
            'Apply paint to canvas, place one contrasting color on top, then swipe with a damp paper towel or palette knife. This creates beautiful flowing cells.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'ap-w2-t5',
          title: 'Review your progress',
          description:
            'Line up all your pieces from weeks 1-2. Identify your favorite, and note what techniques or colors you want to explore more.',
          estimatedTime: '20 minutes',
        },
      ],
    },
    {
      weekNumber: 3,
      title: 'Larger Pieces & Intentional Design',
      description: 'Move to bigger canvases, plan compositions, and refine your personal style.',
      keyFocus: 'Composition planning, scaling up, and developing artistic voice',
      tasks: [
        {
          id: 'ap-w3-t1',
          title: 'Plan a larger composition',
          description:
            'Choose a stretched canvas (30x40cm or larger). Decide on a color palette (3-5 colors). Sketch a rough idea of where you want colors to dominate.',
          estimatedTime: '30 minutes',
        },
        {
          id: 'ap-w3-t2',
          title: 'Execute your planned pour',
          description:
            'Mix larger quantities of paint (you\'ll need more for a big canvas). Pour using your chosen technique. Take your time and stay mindful of your composition plan.',
          estimatedTime: '2-3 hours',
        },
        {
          id: 'ap-w3-t3',
          title: 'Experiment with a Dutch pour',
          description:
            'Cover canvas with a base color, add blobs of other colors on top, then use a hair dryer or heat gun to blow the paint around, creating organic flowing shapes.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'ap-w3-t4',
          title: 'Try a resin-like finish (optional)',
          description:
            'If your budget allows, attempt a small resin pour over a dry acrylic pour piece, or use a high-gloss varnish for a similar glossy effect.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'ap-w3-t5',
          title: 'Refine your technique',
          description:
            'Identify one technique you love (dirty pour, flip cup, swipe, etc.) and do 2-3 variations to master it. Notice the subtle changes each variation brings.',
          estimatedTime: '2-3 hours',
        },
      ],
    },
    {
      weekNumber: 4,
      title: 'Finishing, Varnishing & Sharing',
      description: 'Complete final pieces, learn finishing techniques, photograph your work, and plan next steps.',
      keyFocus: 'Finishing touches, presentation, documentation, and building confidence',
      tasks: [
        {
          id: 'ap-w4-t1',
          title: 'Create your best piece yet',
          description:
            'Use everything you\'ve learned: your favorite colors, best technique, mindful composition. Aim for a piece you\'re proud to display or gift.',
          estimatedTime: '2-3 hours',
        },
        {
          id: 'ap-w4-t2',
          title: 'Learn to varnish properly',
          description:
            'Wait until your pieces are fully dry (72 hours minimum). Apply 2-3 thin coats of varnish with a soft brush or use spray varnish. Let each coat dry between applications.',
          estimatedTime: '1 hour (spread over multiple days)',
        },
        {
          id: 'ap-w4-t3',
          title: 'Photograph your artwork',
          description:
            'Use natural light near a window. Place your piece on a neutral background. Take photos straight-on (not at an angle). Edit brightness/contrast if needed.',
          estimatedTime: '30 minutes',
        },
        {
          id: 'ap-w4-t4',
          title: 'Reflect on your journey',
          description:
            'Write down what you learned, which techniques you enjoyed most, and what you want to explore next. Celebrate how far you\'ve come in 4 weeks!',
          estimatedTime: '20 minutes',
        },
        {
          id: 'ap-w4-t5',
          title: 'Share your work (optional)',
          description:
            'Post your favorite piece on social media or in an online art community. Tag relevant hashtags (#acrylicpouring, #fluidart). Connect with other artists!',
          estimatedTime: '15 minutes',
        },
      ],
    },
  ],
};

/**
 * Palette Knife / Textured Abstract 4-Week Plan
 */
export const PALETTE_KNIFE_PLAN: LearningPlan = {
  style: 'palette-knife',
  weeks: [
    {
      weekNumber: 1,
      title: 'Tool Familiarity & Texture Basics',
      description: 'Get comfortable with palette knives, learn basic strokes, and explore texture.',
      keyFocus: 'Understanding palette knife grip, pressure, and basic mark-making',
      tasks: [
        {
          id: 'pk-w1-t1',
          title: 'Explore your palette knives',
          description:
            'Try each knife on scrap paper or cardboard. Practice different grips (like holding a pencil vs. a spatula). Notice how angle and pressure change the marks.',
          estimatedTime: '30 minutes',
        },
        {
          id: 'pk-w1-t2',
          title: 'Create a texture study',
          description:
            'On a small canvas board, make different marks: smooth sweeps, short dabs, crosshatched lines, thick impasto. Use just one color to focus on texture, not color.',
          estimatedTime: '1 hour',
        },
        {
          id: 'pk-w1-t3',
          title: 'Paint a simple abstract landscape',
          description:
            'Divide your canvas into 2-3 horizontal bands (sky, land, foreground). Use palette knife to apply paint in broad, expressive strokes. Don\'t worry about realism.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'pk-w1-t4',
          title: 'Experiment with thick vs. thin paint',
          description:
            'Try painting with thick paint straight from the tube, then add a bit of medium to thin it. Notice how it changes the texture and blending.',
          estimatedTime: '1 hour',
        },
      ],
    },
    {
      weekNumber: 2,
      title: 'Color Mixing & Layering',
      description: 'Master color blending with palette knife, build layers, and create depth.',
      keyFocus: 'Color theory, optical mixing, and layering techniques',
      tasks: [
        {
          id: 'pk-w2-t1',
          title: 'Practice blending two colors',
          description:
            'Place two colors next to each other on canvas. Use the knife to gently blend where they meet, creating a soft gradient. Try warm colors (red to yellow) and cool colors (blue to green).',
          estimatedTime: '1 hour',
        },
        {
          id: 'pk-w2-t2',
          title: 'Create a color study',
          description:
            'Choose a limited palette (3-4 colors + white). Create an abstract composition focusing on color harmony. Mix colors directly on the canvas with your knife.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'pk-w2-t3',
          title: 'Build layers intentionally',
          description:
            'Apply a base layer, let it dry slightly, then add a second layer on top. Scrape through the top layer to reveal the color beneath. This creates visual interest and depth.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'pk-w2-t4',
          title: 'Try sgraffito technique',
          description:
            'Apply thick paint, then use the edge or tip of your knife to scratch lines, patterns, or shapes into the wet paint. Creates beautiful linear textures.',
          estimatedTime: '1 hour',
        },
      ],
    },
    {
      weekNumber: 3,
      title: 'Composition & Personal Style',
      description: 'Plan intentional compositions, explore abstraction, and find your artistic voice.',
      keyFocus: 'Composition principles, focal points, and developing unique style',
      tasks: [
        {
          id: 'pk-w3-t1',
          title: 'Study composition basics',
          description:
            'Look at abstract artworks you love (online or in books). Notice how artists use contrast, focal points, and balance. Sketch 2-3 simple composition ideas.',
          estimatedTime: '30 minutes',
        },
        {
          id: 'pk-w3-t2',
          title: 'Create a planned abstract piece',
          description:
            'Choose one of your sketched compositions. Use a larger canvas. Build it in layers: background, mid-tones, highlights, and final details with palette knife.',
          estimatedTime: '2-3 hours',
        },
        {
          id: 'pk-w3-t3',
          title: 'Experiment with mixed textures',
          description:
            'Combine palette knife with other tools: use a brush for thin lines, sponge for stippling, or your fingers for smoothing. Discover new texture combinations.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'pk-w3-t4',
          title: 'Work on a series',
          description:
            'Create 2-3 small pieces (same size) using a consistent color palette and technique. Working in a series helps develop cohesive style.',
          estimatedTime: '2-3 hours',
        },
      ],
    },
    {
      weekNumber: 4,
      title: 'Refinement & Completion',
      description: 'Finish strong pieces, learn when to stop, varnish, and document your progress.',
      keyFocus: 'Knowing when a piece is finished, final touches, and presentation',
      tasks: [
        {
          id: 'pk-w4-t1',
          title: 'Create your signature piece',
          description:
            'Choose your best canvas size and favorite colors. Take your time. This is your chance to showcase everything you\'ve learned. Trust your instincts.',
          estimatedTime: '3-4 hours',
        },
        {
          id: 'pk-w4-t2',
          title: 'Learn when to stop',
          description:
            'Practice stepping back from your work. Take a photo and look at it on your phone. This helps you see if the piece needs more work or if it\'s done. Overworking is common!',
          estimatedTime: '30 minutes',
        },
        {
          id: 'pk-w4-t3',
          title: 'Add finishing touches',
          description:
            'Look for areas that need a pop of light or shadow. Add small highlights or refine edges. These subtle details elevate the whole piece.',
          estimatedTime: '1 hour',
        },
        {
          id: 'pk-w4-t4',
          title: 'Varnish your best works',
          description:
            'Once fully dry (3-7 days), apply varnish to protect your paintings. Use gloss for vibrant colors or matte for a subtle finish.',
          estimatedTime: '1 hour',
        },
        {
          id: 'pk-w4-t5',
          title: 'Document and celebrate',
          description:
            'Photograph all your work from the month. Create a before/after comparison. Share with friends or online. Acknowledge your growth!',
          estimatedTime: '30 minutes',
        },
      ],
    },
  ],
};

/**
 * Mixed Media 4-Week Plan (can be adapted)
 */
export const MIXED_MEDIA_PLAN: LearningPlan = {
  style: 'mixed-media',
  weeks: [
    {
      weekNumber: 1,
      title: 'Explore Materials & Substrates',
      description: 'Discover different materials you can incorporate, test surfaces, and try basic collage.',
      keyFocus: 'Understanding what "mixed media" means and experimenting with materials',
      tasks: [
        {
          id: 'mm-w1-t1',
          title: 'Gather mixed media materials',
          description:
            'Collect magazine clippings, tissue paper, fabric scraps, old book pages, textured papers. Organize them in folders or envelopes for easy access.',
          estimatedTime: '30 minutes',
        },
        {
          id: 'mm-w1-t2',
          title: 'Test different surfaces',
          description:
            'Try painting on canvas, wood, thick cardboard, and watercolor paper. Notice how each surface absorbs or resists paint. This informs your material choices later.',
          estimatedTime: '1 hour',
        },
        {
          id: 'mm-w1-t3',
          title: 'Create a simple collage',
          description:
            'Use gel medium to adhere paper elements to a canvas board. Layer 3-5 pieces. Paint over some areas with transparent washes. Blend collage and paint together.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'mm-w1-t4',
          title: 'Experiment with texture paste',
          description:
            'Apply texture paste or modeling paste through a stencil or palette knife. Let it dry, then paint over it. Enjoy the dimensional effect!',
          estimatedTime: '1 hour',
        },
      ],
    },
    {
      weekNumber: 2,
      title: 'Layering & Building Depth',
      description: 'Learn to build complex layers, combine techniques, and create visual depth.',
      keyFocus: 'Layering transparency, opacity, and mixed techniques',
      tasks: [
        {
          id: 'mm-w2-t1',
          title: 'Build a layered background',
          description:
            'Start with a painted base, add collage elements, paint over them partially, add mark-making (doodles, stamps, stencils). Build at least 4-5 layers.',
          estimatedTime: '2 hours',
        },
        {
          id: 'mm-w2-t2',
          title: 'Try paint + ink + pencil',
          description:
            'Combine acrylic paint with ink (use a dip pen or brush), then add details with colored pencils or graphite. Notice how different media interact.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'mm-w2-t3',
          title: 'Create a textured abstract',
          description:
            'Use palette knife to apply thick paint, add sand or modeling paste for texture, scrape through layers, and finish with fine pen details.',
          estimatedTime: '2 hours',
        },
        {
          id: 'mm-w2-t4',
          title: 'Practice controlled chaos',
          description:
            'Let go of perfection. Drip paint, splatter, tear paper randomly, then find coherence by adding intentional marks or painting over areas. Embrace happy accidents.',
          estimatedTime: '1-2 hours',
        },
      ],
    },
    {
      weekNumber: 3,
      title: 'Developing a Theme',
      description: 'Choose a theme or concept, create a cohesive series, and tell a story through mixed media.',
      keyFocus: 'Conceptual thinking, narrative, and series work',
      tasks: [
        {
          id: 'mm-w3-t1',
          title: 'Choose a personal theme',
          description:
            'Select a theme that resonates: nature, urban life, emotions, memories, text/poetry. Gather images and materials related to this theme.',
          estimatedTime: '30 minutes',
        },
        {
          id: 'mm-w3-t2',
          title: 'Create the first piece in your series',
          description:
            'Use your theme as inspiration. Combine techniques you\'ve learned. Don\'t overthink it - let intuition guide your material choices.',
          estimatedTime: '2-3 hours',
        },
        {
          id: 'mm-w3-t3',
          title: 'Create 2-3 companion pieces',
          description:
            'Make 2-3 more pieces using a similar color palette, materials, or composition style. They don\'t need to match exactly, but should feel related.',
          estimatedTime: '3-4 hours',
        },
        {
          id: 'mm-w3-t4',
          title: 'Add text or found poetry',
          description:
            'Incorporate words: handwritten, stamped, or cut from magazines. Use text as a design element or to reinforce your theme.',
          estimatedTime: '1-2 hours',
        },
      ],
    },
    {
      weekNumber: 4,
      title: 'Final Pieces & Presentation',
      description: 'Complete your best mixed media work, seal and protect it, and share your journey.',
      keyFocus: 'Finishing techniques, sealing, and presentation',
      tasks: [
        {
          id: 'mm-w4-t1',
          title: 'Create a showpiece',
          description:
            'Pull out all the stops. Use a larger substrate. Combine your favorite techniques. This piece represents your 4-week journey - make it count!',
          estimatedTime: '3-5 hours',
        },
        {
          id: 'mm-w4-t2',
          title: 'Seal and varnish mixed media',
          description:
            'Mixed media needs protection! Use a matte or satin varnish (gloss can look too shiny on paper elements). Apply 2-3 thin coats, letting each dry.',
          estimatedTime: '1 hour (over several days)',
        },
        {
          id: 'mm-w4-t3',
          title: 'Frame or mount your favorites',
          description:
            'Choose 2-3 pieces to frame or mount on foam board. Presentation matters! Even a simple black frame elevates your work.',
          estimatedTime: '1 hour',
        },
        {
          id: 'mm-w4-t4',
          title: 'Photograph and document',
          description:
            'Take well-lit photos of all your pieces. Create a simple digital portfolio (folder on your computer or phone). Write a sentence about each piece.',
          estimatedTime: '45 minutes',
        },
        {
          id: 'mm-w4-t5',
          title: 'Plan your next steps',
          description:
            'Reflect on what you loved most. Do you want to go deeper into collage? Texture? Abstraction? Set one specific goal for the next month.',
          estimatedTime: '20 minutes',
        },
      ],
    },
  ],
};

/**
 * Default plan for "not sure" style - combines elements from all styles
 */
export const BEGINNER_GENERAL_PLAN: LearningPlan = {
  style: 'not-sure',
  weeks: [
    {
      weekNumber: 1,
      title: 'Discover Your Preferences',
      description: 'Try multiple techniques to see what resonates with you.',
      keyFocus: 'Exploration and finding what you enjoy',
      tasks: [
        {
          id: 'gen-w1-t1',
          title: 'Try a simple acrylic pour',
          description:
            'Mix 2-3 colors with water or PVA glue to a flowing consistency. Pour onto a small canvas board and tilt to spread. See if you enjoy this fluid approach.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'gen-w1-t2',
          title: 'Experiment with palette knife',
          description:
            'Use a palette knife (or old credit card) to apply thick paint in bold strokes. Create an abstract piece with texture. Notice if you like this tactile method.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'gen-w1-t3',
          title: 'Try collage and layering',
          description:
            'Glue magazine clippings or tissue paper onto a board, paint over them, add marks with pencil or pen. See if you enjoy the layering process.',
          estimatedTime: '1-2 hours',
        },
        {
          id: 'gen-w1-t4',
          title: 'Reflect on what you enjoyed',
          description:
            'Look at your three experiments. Which felt most satisfying? Which do you want to try again? Your instinct will guide you to the right technique.',
          estimatedTime: '15 minutes',
        },
      ],
    },
    {
      weekNumber: 2,
      title: 'Go Deeper into Your Favorite',
      description: 'Choose the technique you enjoyed most and explore it further.',
      keyFocus: 'Focused practice on your preferred technique',
      tasks: [
        {
          id: 'gen-w2-t1',
          title: 'Choose your primary technique',
          description:
            'Based on week 1, pick the technique you want to focus on: pouring, palette knife, or mixed media. Commit to it for this week.',
          estimatedTime: '5 minutes',
        },
        {
          id: 'gen-w2-t2',
          title: 'Research your chosen technique',
          description:
            'Watch 2-3 YouTube tutorials on your chosen method. Note tips, color palettes, and approaches that inspire you.',
          estimatedTime: '45 minutes',
        },
        {
          id: 'gen-w2-t3',
          title: 'Practice technique variations',
          description:
            'Try 3 different variations of your chosen technique. For pouring: dirty pour, flip cup, swipe. For palette knife: smooth blending, impasto, sgraffito. For mixed media: collage focus, texture focus, layering focus.',
          estimatedTime: '3-4 hours',
        },
        {
          id: 'gen-w2-t4',
          title: 'Start a favorites folder',
          description:
            'Save images of artworks that inspire you (Pinterest, Instagram, art books). Notice patterns in what you\'re drawn to - colors, compositions, textures.',
          estimatedTime: '30 minutes',
        },
      ],
    },
    {
      weekNumber: 3,
      title: 'Build Confidence & Style',
      description: 'Create larger pieces, develop your personal style, and refine your skills.',
      keyFocus: 'Consistency, confidence, and personal expression',
      tasks: [
        {
          id: 'gen-w3-t1',
          title: 'Plan a larger piece',
          description:
            'Choose a bigger canvas or board. Plan your color palette (3-5 colors). Sketch a rough composition idea. Preparation boosts confidence!',
          estimatedTime: '30 minutes',
        },
        {
          id: 'gen-w3-t2',
          title: 'Execute your planned piece',
          description:
            'Take your time. Use your favorite technique. Don\'t rush. Remember: mistakes are part of the process. You can always paint over or adjust.',
          estimatedTime: '2-3 hours',
        },
        {
          id: 'gen-w3-t3',
          title: 'Create a mini-series',
          description:
            'Make 2-3 smaller pieces using the same colors and technique. Working in a series builds consistency and helps develop your unique style.',
          estimatedTime: '2-3 hours',
        },
        {
          id: 'gen-w3-t4',
          title: 'Get feedback (optional)',
          description:
            'Share your work with a friend, family member, or online community. Ask what they see, what they feel. Outside perspectives can be encouraging and insightful.',
          estimatedTime: '30 minutes',
        },
      ],
    },
    {
      weekNumber: 4,
      title: 'Complete & Celebrate',
      description: 'Finish your best work, learn to varnish, document your journey, and plan next steps.',
      keyFocus: 'Completion, presentation, and reflection',
      tasks: [
        {
          id: 'gen-w4-t1',
          title: 'Create your best piece yet',
          description:
            'Use everything you\'ve learned. Choose your favorite colors and technique. Make something you\'re proud to hang on your wall or give as a gift.',
          estimatedTime: '3-4 hours',
        },
        {
          id: 'gen-w4-t2',
          title: 'Learn to varnish',
          description:
            'Wait for paintings to dry fully (3-7 days). Apply 2-3 thin coats of varnish (spray or brush-on). This protects your work and makes colors pop.',
          estimatedTime: '1 hour (over multiple days)',
        },
        {
          id: 'gen-w4-t3',
          title: 'Photograph your work',
          description:
            'Use natural light, place art on a neutral surface, take photos straight-on. Good documentation helps you track your progress and share your work.',
          estimatedTime: '30 minutes',
        },
        {
          id: 'gen-w4-t4',
          title: 'Reflect on your journey',
          description:
            'Look back at week 1. Notice your growth! Write down 3 things you learned and 3 things you want to explore next. Celebrate how far you\'ve come.',
          estimatedTime: '20 minutes',
        },
        {
          id: 'gen-w4-t5',
          title: 'Plan your next month',
          description:
            'Decide if you want to continue with your current technique or try something new. Set one specific goal: master cells, improve color mixing, try resin, etc.',
          estimatedTime: '15 minutes',
        },
      ],
    },
  ],
};

/**
 * Studio Setup Tips - context-aware based on user's space
 *
 * HOW TO EDIT:
 * - Add new tips to the array
 * - Set relevantFor to match the space types where this tip applies
 * - Tips with no relevantFor will show to everyone
 */
export const STUDIO_TIPS: StudioTip[] = [
  {
    id: 'tip-protection',
    title: 'Protect your surfaces',
    description:
      'Use plastic sheeting, bin bags, or an old shower curtain to cover your work area. Acrylic paint is permanent once dry!',
    relevantFor: ['kitchen-table', 'small-corner', 'dedicated-room'],
  },
  {
    id: 'tip-lighting',
    title: 'Good lighting is essential',
    description:
      'Work near a window for natural light, or use a bright white LED bulb. Good lighting helps you see true colors and details.',
    relevantFor: ['kitchen-table', 'small-corner', 'dedicated-room'],
  },
  {
    id: 'tip-ventilation',
    title: 'Ensure proper ventilation',
    description:
      'Open windows when using pouring mediums, varnishes, or resin. Fresh air helps fumes disperse and speeds drying.',
    relevantFor: ['kitchen-table', 'small-corner', 'dedicated-room'],
  },
  {
    id: 'tip-elevation',
    title: 'Elevate your canvas for pouring',
    description:
      'Use plastic cups, bottle caps, or small containers to lift your canvas off the surface. This lets excess paint drip off the edges.',
    relevantFor: ['kitchen-table', 'small-corner', 'dedicated-room'],
  },
  {
    id: 'tip-quick-setup',
    title: 'Create a quick-setup kit',
    description:
      'Store all your materials in a plastic box or tote bag. Lay out a plastic sheet, work, then pack everything away quickly. Perfect for shared spaces.',
    relevantFor: ['kitchen-table'],
  },
  {
    id: 'tip-drying-space',
    title: 'Designate a drying area',
    description:
      'Find a flat surface where wet paintings can dry undisturbed for 24-72 hours (shelf, spare table, top of a bookcase). Dust-free is ideal.',
    relevantFor: ['kitchen-table', 'small-corner'],
  },
  {
    id: 'tip-storage',
    title: 'Organize materials for easy access',
    description:
      'Use drawer organizers, jars, or small bins to sort paints, brushes, mediums. Label everything. A well-organized space makes creating more enjoyable.',
    relevantFor: ['small-corner', 'dedicated-room'],
  },
  {
    id: 'tip-dedicated-drying-rack',
    title: 'Invest in a canvas drying rack',
    description:
      'If you have space, a drying rack lets you work on multiple pieces without waiting for each to dry. Stack canvases safely and save space.',
    relevantFor: ['dedicated-room'],
  },
  {
    id: 'tip-cleanup',
    title: 'Keep cleanup simple',
    description:
      'Have paper towels, rags, and a container of water nearby. Clean brushes and tools immediately after use. Dried acrylic is hard to remove!',
    relevantFor: ['kitchen-table', 'small-corner', 'dedicated-room'],
  },
  {
    id: 'tip-apron',
    title: 'Wear an apron or old clothes',
    description:
      'Acrylic paint stains clothing permanently. An apron, old t-shirt, or smock protects your clothes and lets you create freely without worry.',
    relevantFor: ['kitchen-table', 'small-corner', 'dedicated-room'],
  },
  {
    id: 'tip-inspiration-board',
    title: 'Create an inspiration board',
    description:
      'Pin up images, color swatches, and sketches that inspire you. Seeing your ideas displayed can spark creativity and help with composition planning.',
    relevantFor: ['small-corner', 'dedicated-room'],
  },
  {
    id: 'tip-comfortable-seating',
    title: 'Set up comfortable seating or standing area',
    description:
      'You might spend 1-3 hours painting. Make sure your chair or standing position is comfortable. Adjust table/easel height to avoid neck and back strain.',
    relevantFor: ['kitchen-table', 'small-corner', 'dedicated-room'],
  },
];
