/**
 * Materials Configuration
 *
 * This file contains all material recommendations for different styles and budgets.
 *
 * HOW TO EDIT:
 * - Add new items to the MATERIALS array
 * - Set requiredFor to match the style(s) this item is needed for
 * - Set budgetLevel to control which budget tiers see this item
 * - Set priority to 'essential', 'recommended', or 'optional'
 *
 * The app will automatically filter and display items based on user's profile.
 */

import { Material } from '@/types/materials';

export const MATERIALS: Material[] = [
  // PAINTS
  {
    id: 'acrylic-paint-basic-set',
    name: 'Basic Acrylic Paint Set',
    category: 'paints',
    description: 'Student-grade set with primary colors, black, and white (6-8 colors)',
    estimatedCost: '£15-25',
    link: '#',
    requiredFor: ['acrylic-pouring', 'palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'essential',
  },
  {
    id: 'acrylic-paint-premium-set',
    name: 'Artist-Grade Acrylic Paint Set',
    category: 'paints',
    description: 'Higher pigment concentration, better color mixing (12+ colors)',
    estimatedCost: '£40-70',
    link: '#',
    requiredFor: ['acrylic-pouring', 'palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['100-250', '250-plus'],
    priority: 'recommended',
  },
  {
    id: 'white-paint-large',
    name: 'Large Titanium White Paint',
    category: 'paints',
    description: 'You\'ll use white the most - buy a larger tube or bottle',
    estimatedCost: '£8-15',
    link: '#',
    requiredFor: ['acrylic-pouring', 'palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['100-250', '250-plus'],
    priority: 'recommended',
  },

  // CANVASES
  {
    id: 'canvas-boards-small',
    name: 'Canvas Boards or Panels (A4-A5 size)',
    category: 'canvases',
    description: 'Pack of 5-10 small surfaces for practice',
    estimatedCost: '£10-18',
    link: '#',
    requiredFor: ['acrylic-pouring', 'palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'essential',
  },
  {
    id: 'stretched-canvas',
    name: 'Stretched Canvas (30x40cm or 40x50cm)',
    category: 'canvases',
    description: '2-3 canvases for larger finished pieces',
    estimatedCost: '£15-30',
    link: '#',
    requiredFor: ['acrylic-pouring', 'palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['100-250', '250-plus'],
    priority: 'recommended',
  },
  {
    id: 'wooden-panels',
    name: 'Wooden Panels or MDF Boards',
    category: 'canvases',
    description: 'Rigid surface excellent for palette knife work',
    estimatedCost: '£12-25',
    link: '#',
    requiredFor: ['palette-knife', 'mixed-media'],
    budgetLevel: ['100-250', '250-plus'],
    priority: 'recommended',
  },

  // MEDIUMS
  {
    id: 'pouring-medium',
    name: 'Acrylic Pouring Medium',
    category: 'mediums',
    description: 'Essential for fluid art - helps paint flow smoothly (500ml-1L)',
    estimatedCost: '£12-20',
    link: '#',
    requiredFor: ['acrylic-pouring'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'essential',
  },
  {
    id: 'pva-glue',
    name: 'PVA Glue (Elmers or similar)',
    category: 'mediums',
    description: 'Budget alternative to pouring medium for beginners',
    estimatedCost: '£4-8',
    link: '#',
    requiredFor: ['acrylic-pouring'],
    budgetLevel: ['under-100'],
    priority: 'recommended',
  },
  {
    id: 'silicone-oil',
    name: 'Silicone Oil',
    category: 'mediums',
    description: 'Creates cells in acrylic pouring (small bottle goes a long way)',
    estimatedCost: '£5-10',
    link: '#',
    requiredFor: ['acrylic-pouring'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'recommended',
  },
  {
    id: 'gel-medium',
    name: 'Gel Medium (Gloss or Matte)',
    category: 'mediums',
    description: 'Adds texture and body to paint for palette knife work',
    estimatedCost: '£8-15',
    link: '#',
    requiredFor: ['palette-knife', 'mixed-media'],
    budgetLevel: ['100-250', '250-plus'],
    priority: 'recommended',
  },
  {
    id: 'varnish',
    name: 'Acrylic Varnish (Spray or Brush-on)',
    category: 'mediums',
    description: 'Protects finished paintings - gloss, satin, or matte',
    estimatedCost: '£10-18',
    link: '#',
    requiredFor: ['acrylic-pouring', 'palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['100-250', '250-plus'],
    priority: 'recommended',
  },

  // TOOLS
  {
    id: 'palette-knives',
    name: 'Palette Knife Set',
    category: 'tools',
    description: 'Set of 3-5 different shapes and sizes',
    estimatedCost: '£8-18',
    link: '#',
    requiredFor: ['palette-knife', 'mixed-media'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'essential',
  },
  {
    id: 'plastic-cups',
    name: 'Plastic Cups & Mixing Sticks',
    category: 'tools',
    description: 'For mixing paint and pouring medium (reusable or disposable)',
    estimatedCost: '£3-8',
    link: '#',
    requiredFor: ['acrylic-pouring'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'essential',
  },
  {
    id: 'palette',
    name: 'Palette (Plastic or Wooden)',
    category: 'tools',
    description: 'For mixing colors - or use a ceramic plate',
    estimatedCost: '£5-12',
    link: '#',
    requiredFor: ['palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'essential',
  },
  {
    id: 'brushes-basic',
    name: 'Basic Brush Set',
    category: 'tools',
    description: 'A few flat and round brushes in various sizes',
    estimatedCost: '£8-15',
    link: '#',
    requiredFor: ['palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'recommended',
  },
  {
    id: 'apron',
    name: 'Apron or Old Clothes',
    category: 'tools',
    description: 'Acrylic paint is hard to remove once dry!',
    estimatedCost: '£8-15',
    link: '#',
    requiredFor: ['acrylic-pouring', 'palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'essential',
  },
  {
    id: 'heat-gun',
    name: 'Heat Gun or Torch',
    category: 'tools',
    description: 'Removes bubbles and helps create cells in pours',
    estimatedCost: '£15-30',
    link: '#',
    requiredFor: ['acrylic-pouring'],
    budgetLevel: ['100-250', '250-plus'],
    priority: 'recommended',
  },

  // PROTECTION
  {
    id: 'plastic-sheeting',
    name: 'Plastic Sheeting or Tarp',
    category: 'protection',
    description: 'Cover your work surface - essential for pours!',
    estimatedCost: '£5-12',
    link: '#',
    requiredFor: ['acrylic-pouring', 'palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'essential',
  },
  {
    id: 'gloves',
    name: 'Disposable Gloves',
    category: 'protection',
    description: 'Nitrile or vinyl gloves (box of 50-100)',
    estimatedCost: '£5-10',
    link: '#',
    requiredFor: ['acrylic-pouring', 'palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'recommended',
  },
  {
    id: 'paper-towels',
    name: 'Paper Towels or Rags',
    category: 'protection',
    description: 'For cleanup and wiping tools',
    estimatedCost: '£3-6',
    link: '#',
    requiredFor: ['acrylic-pouring', 'palette-knife', 'mixed-media', 'not-sure'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'essential',
  },

  // OPTIONAL
  {
    id: 'easel',
    name: 'Table Easel',
    category: 'optional',
    description: 'Helps with palette knife work - not needed for pouring',
    estimatedCost: '£15-35',
    link: '#',
    requiredFor: ['palette-knife', 'mixed-media'],
    budgetLevel: ['100-250', '250-plus'],
    priority: 'optional',
  },
  {
    id: 'spray-bottle',
    name: 'Spray Bottle with Water',
    category: 'optional',
    description: 'Keep paint workable longer',
    estimatedCost: '£2-5',
    link: '#',
    requiredFor: ['palette-knife', 'mixed-media'],
    budgetLevel: ['under-100', '100-250', '250-plus'],
    priority: 'optional',
  },
  {
    id: 'drying-rack',
    name: 'Canvas Drying Rack',
    category: 'optional',
    description: 'Useful if you\'re doing multiple pours - or use books/boxes',
    estimatedCost: '£20-40',
    link: '#',
    requiredFor: ['acrylic-pouring'],
    budgetLevel: ['250-plus'],
    priority: 'optional',
  },
];

/**
 * Helper function to get category label
 */
export function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    paints: 'Paints',
    canvases: 'Canvases & Surfaces',
    mediums: 'Mediums & Additives',
    tools: 'Tools & Equipment',
    protection: 'Protection & Cleanup',
    optional: 'Optional Extras',
  };
  return labels[category] || category;
}
