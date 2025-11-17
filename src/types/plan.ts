/**
 * Learning Plan Types
 *
 * These types define the structure of the 4-week learning plan.
 * Used in /config/learningPlan.ts
 */

/**
 * Individual task within a week
 */
export interface WeekTask {
  id: string;
  title: string;
  description: string;
  estimatedTime?: string; // e.g., "30 minutes", "1-2 hours"
  resources?: string[]; // Links to specific resources or techniques
}

/**
 * Single week in the learning plan
 */
export interface WeekPlan {
  weekNumber: number;
  title: string;
  description: string;
  tasks: WeekTask[];
  keyFocus: string; // e.g., "Color mixing and basic techniques"
}

/**
 * Complete 4-week learning plan
 */
export interface LearningPlan {
  style: string; // The primary style this plan is for
  weeks: WeekPlan[];
}

/**
 * Studio setup tip
 */
export interface StudioTip {
  id: string;
  title: string;
  description: string;
  relevantFor?: string[]; // e.g., ['kitchen-table', 'small-corner']
}

/**
 * Learning resource (video, article, book, etc.)
 */
export interface Resource {
  id: string;
  title: string;
  type: 'youtube' | 'article' | 'book' | 'course' | 'website';
  url: string;
  description: string;
  tags: string[]; // e.g., ['acrylic-pouring', 'beginner', 'palette-knife']
  author?: string;
  duration?: string; // For videos/courses
}
