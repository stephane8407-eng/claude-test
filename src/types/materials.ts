/**
 * Materials Types
 *
 * These types define the structure of materials recommendations.
 * Used in /config/materials.ts
 */

export type MaterialCategory =
  | 'paints'
  | 'canvases'
  | 'mediums'
  | 'tools'
  | 'protection'
  | 'optional';

/**
 * Individual material item
 * Add or edit items in /config/materials.ts
 */
export interface Material {
  id: string;
  name: string;
  category: MaterialCategory;
  description: string;
  estimatedCost?: string; // e.g., "£15-25"
  link?: string; // Placeholder or real link
  requiredFor?: string[]; // e.g., ['acrylic-pouring', 'palette-knife']
  budgetLevel?: string[]; // e.g., ['under-100', '100-250', '250-plus']
  priority: 'essential' | 'recommended' | 'optional';
}

/**
 * Grouped materials by category for display
 */
export interface MaterialGroup {
  category: MaterialCategory;
  categoryLabel: string;
  items: Material[];
}
