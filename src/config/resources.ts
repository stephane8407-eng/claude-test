/**
 * Learning Resources Configuration
 *
 * This file contains recommended resources (videos, articles, books, courses).
 *
 * HOW TO EDIT:
 * - Add new resources to the RESOURCES array
 * - Set appropriate tags to match user profiles (style, experience level, goal)
 * - The app automatically filters and shows relevant resources
 *
 * Tags guide:
 * - Styles: 'acrylic-pouring', 'palette-knife', 'mixed-media', 'general'
 * - Levels: 'beginner', 'intermediate', 'advanced'
 * - Goals: 'hobby', 'selling', 'business'
 */

import { Resource } from '@/types/plan';

export const RESOURCES: Resource[] = [
  // ACRYLIC POURING RESOURCES
  {
    id: 'res-001',
    title: 'Beginner\'s Guide to Acrylic Pouring',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=acrylic+pouring+beginners+guide',
    description:
      'Comprehensive tutorial covering paint consistency, basic pour techniques, and troubleshooting common issues.',
    tags: ['acrylic-pouring', 'beginner', 'technique'],
    author: 'Various artists',
    duration: '15-30 minutes',
  },
  {
    id: 'res-002',
    title: 'How to Create Beautiful Cells in Acrylic Pouring',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=acrylic+pouring+cells+tutorial',
    description:
      'Learn how to use silicone oil, torch techniques, and paint consistency to create stunning cells in your pours.',
    tags: ['acrylic-pouring', 'beginner', 'intermediate', 'cells'],
    author: 'Various artists',
    duration: '10-20 minutes',
  },
  {
    id: 'res-003',
    title: 'Dirty Pour vs. Flip Cup: Which Technique Is Right for You?',
    type: 'article',
    url: 'https://www.google.com/search?q=dirty+pour+vs+flip+cup+acrylic+pouring',
    description:
      'Article comparing different pouring techniques, their effects, and when to use each method.',
    tags: ['acrylic-pouring', 'beginner', 'technique'],
  },
  {
    id: 'res-004',
    title: 'Swipe Technique Masterclass',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=acrylic+pouring+swipe+technique',
    description:
      'Step-by-step guide to mastering the swipe technique for beautiful flowing patterns and cells.',
    tags: ['acrylic-pouring', 'beginner', 'intermediate', 'technique'],
    duration: '12-25 minutes',
  },
  {
    id: 'res-005',
    title: 'Choosing the Right Pouring Medium',
    type: 'article',
    url: 'https://www.google.com/search?q=best+acrylic+pouring+medium+comparison',
    description:
      'Comparison of different pouring mediums (Floetrol, Liquitex, GAC 800) and budget alternatives like PVA glue.',
    tags: ['acrylic-pouring', 'beginner', 'materials'],
  },
  {
    id: 'res-006',
    title: 'Acrylic Pouring: From Hobby to Business',
    type: 'article',
    url: 'https://www.google.com/search?q=selling+acrylic+pouring+art+online',
    description:
      'Guide to pricing your work, selling on Etsy/Instagram, and building a sustainable art business.',
    tags: ['acrylic-pouring', 'selling', 'business', 'intermediate'],
  },

  // PALETTE KNIFE RESOURCES
  {
    id: 'res-007',
    title: 'Palette Knife Basics for Beginners',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=palette+knife+painting+for+beginners',
    description:
      'Learn basic palette knife grips, strokes, and how to create texture and dimension in abstract paintings.',
    tags: ['palette-knife', 'beginner', 'technique'],
    author: 'Various artists',
    duration: '15-25 minutes',
  },
  {
    id: 'res-008',
    title: 'Color Mixing with Palette Knife',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=palette+knife+color+mixing+tutorial',
    description:
      'Master the art of blending and mixing colors directly on the canvas using palette knives.',
    tags: ['palette-knife', 'beginner', 'intermediate', 'color-theory'],
    duration: '18-30 minutes',
  },
  {
    id: 'res-009',
    title: 'Impasto Technique & Texture Building',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=impasto+technique+palette+knife',
    description:
      'Create thick, sculptural paint textures using palette knives and gel mediums.',
    tags: ['palette-knife', 'intermediate', 'technique', 'texture'],
    duration: '20-35 minutes',
  },
  {
    id: 'res-010',
    title: 'Abstract Landscape with Palette Knife',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=abstract+landscape+palette+knife',
    description:
      'Step-by-step tutorial for creating expressive abstract landscapes using only palette knives.',
    tags: ['palette-knife', 'beginner', 'intermediate', 'landscape'],
    duration: '25-40 minutes',
  },
  {
    id: 'res-011',
    title: 'Sgraffito & Scratching Techniques',
    type: 'article',
    url: 'https://www.google.com/search?q=sgraffito+technique+acrylic+painting',
    description:
      'Learn how to scratch through layers of paint to create intricate patterns and linear details.',
    tags: ['palette-knife', 'intermediate', 'technique'],
  },

  // MIXED MEDIA RESOURCES
  {
    id: 'res-012',
    title: 'Introduction to Mixed Media Art',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=mixed+media+art+for+beginners',
    description:
      'Explore what mixed media is, materials you can use, and basic techniques for combining different mediums.',
    tags: ['mixed-media', 'beginner', 'technique'],
    author: 'Various artists',
    duration: '12-20 minutes',
  },
  {
    id: 'res-013',
    title: 'Collage Techniques in Mixed Media',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=mixed+media+collage+techniques',
    description:
      'Learn how to incorporate paper, fabric, and found objects into your abstract artworks.',
    tags: ['mixed-media', 'beginner', 'intermediate', 'collage'],
    duration: '15-30 minutes',
  },
  {
    id: 'res-014',
    title: 'Layering & Building Depth',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=mixed+media+layering+techniques',
    description:
      'Master the art of building complex, visually rich layers in your mixed media pieces.',
    tags: ['mixed-media', 'intermediate', 'technique', 'layering'],
    duration: '20-35 minutes',
  },
  {
    id: 'res-015',
    title: 'Texture Paste & Modeling Paste Techniques',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=texture+paste+mixed+media',
    description:
      'Create dimensional texture using pastes, stencils, and sculpting tools.',
    tags: ['mixed-media', 'beginner', 'intermediate', 'texture'],
    duration: '10-18 minutes',
  },
  {
    id: 'res-016',
    title: 'Adding Text & Mark-Making to Your Art',
    type: 'article',
    url: 'https://www.google.com/search?q=mixed+media+text+and+mark+making',
    description:
      'Explore creative ways to incorporate handwriting, stamps, stencils, and found text into your work.',
    tags: ['mixed-media', 'intermediate', 'technique'],
  },

  // GENERAL / CROSS-TECHNIQUE RESOURCES
  {
    id: 'res-017',
    title: 'Color Theory for Abstract Artists',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=color+theory+for+abstract+art',
    description:
      'Understand color harmonies, complementary colors, temperature, and how to create effective color palettes.',
    tags: ['general', 'beginner', 'intermediate', 'color-theory'],
    duration: '15-25 minutes',
  },
  {
    id: 'res-018',
    title: 'Composition Basics for Abstract Art',
    type: 'article',
    url: 'https://www.google.com/search?q=abstract+art+composition+principles',
    description:
      'Learn about focal points, balance, contrast, and the rule of thirds in abstract compositions.',
    tags: ['general', 'beginner', 'intermediate', 'composition'],
  },
  {
    id: 'res-019',
    title: 'How to Varnish Your Acrylic Paintings',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=how+to+varnish+acrylic+painting',
    description:
      'Step-by-step guide to applying varnish correctly for a professional finish and long-lasting protection.',
    tags: ['general', 'beginner', 'finishing'],
    duration: '8-15 minutes',
  },
  {
    id: 'res-020',
    title: 'Photographing Your Artwork for Social Media',
    type: 'article',
    url: 'https://www.google.com/search?q=how+to+photograph+artwork+for+instagram',
    description:
      'Tips on lighting, angles, and editing to showcase your art beautifully online.',
    tags: ['general', 'selling', 'business', 'photography'],
  },
  {
    id: 'res-021',
    title: 'Pricing Your Art: A Beginner\'s Guide',
    type: 'article',
    url: 'https://www.google.com/search?q=how+to+price+your+art+as+beginner',
    description:
      'Learn how to calculate fair prices based on materials, time, size, and your experience level.',
    tags: ['general', 'selling', 'business'],
  },
  {
    id: 'res-022',
    title: 'Building an Art Business on Instagram',
    type: 'article',
    url: 'https://www.google.com/search?q=selling+art+on+instagram+tips',
    description:
      'Strategies for growing your following, engaging with collectors, and making sales through social media.',
    tags: ['general', 'selling', 'business', 'social-media'],
  },
  {
    id: 'res-023',
    title: 'Etsy for Artists: Complete Setup Guide',
    type: 'article',
    url: 'https://www.google.com/search?q=how+to+sell+art+on+etsy+guide',
    description:
      'Everything you need to know about setting up an Etsy shop, listing products, and shipping artwork.',
    tags: ['general', 'selling', 'business', 'etsy'],
  },
  {
    id: 'res-024',
    title: 'Finding Your Unique Artistic Style',
    type: 'youtube',
    url: 'https://www.youtube.com/results?search_query=how+to+find+your+art+style',
    description:
      'Advice on experimentation, consistency, and developing a recognizable personal style.',
    tags: ['general', 'intermediate', 'inspiration'],
    duration: '10-20 minutes',
  },
  {
    id: 'res-025',
    title: 'Overcoming Creative Block',
    type: 'article',
    url: 'https://www.google.com/search?q=overcoming+creative+block+artists',
    description:
      'Practical exercises and mindset shifts to get unstuck and reignite your creativity.',
    tags: ['general', 'beginner', 'intermediate', 'inspiration'],
  },

  // BOOKS (optional, can be added as needed)
  {
    id: 'res-026',
    title: 'The Artist\'s Way by Julia Cameron',
    type: 'book',
    url: 'https://www.google.com/search?q=the+artists+way+julia+cameron',
    description:
      'Classic book on unlocking creativity and building a consistent creative practice.',
    tags: ['general', 'beginner', 'inspiration', 'mindset'],
    author: 'Julia Cameron',
  },
  {
    id: 'res-027',
    title: 'Abstract Art Painting: Expressions in Mixed Media',
    type: 'book',
    url: 'https://www.google.com/search?q=abstract+art+painting+expressions+in+mixed+media',
    description:
      'Comprehensive guide to abstract painting techniques, with step-by-step projects.',
    tags: ['mixed-media', 'palette-knife', 'beginner', 'intermediate'],
    author: 'Debora Stewart',
  },
];
