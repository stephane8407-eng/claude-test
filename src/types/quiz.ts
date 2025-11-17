/**
 * Quiz and User Profile Types
 *
 * These types define the structure of the questionnaire and user profile.
 * Edit these if you want to add new questions or answer options.
 */

export type ExperienceLevel = 'complete-beginner' | 'dabbled-a-bit';

export type Goal = 'relaxing-hobby' | 'hobby-maybe-sell' | 'side-business';

export type Budget = 'under-100' | '100-250' | '250-plus';

export type Space = 'kitchen-table' | 'small-corner' | 'dedicated-room';

export type Style = 'acrylic-pouring' | 'palette-knife' | 'mixed-media' | 'not-sure';

export type TimeAvailable = '1-2-hours' | '3-5-hours' | '5-plus-hours';

/**
 * The complete user profile generated from quiz answers.
 * This is stored in localStorage and used to generate personalized content.
 */
export interface UserProfile {
  experienceLevel: ExperienceLevel;
  goal: Goal;
  budget: Budget;
  space: Space;
  style: Style;
  timeAvailable: TimeAvailable;
  completedAt: string; // ISO date string
}

/**
 * Individual question configuration
 */
export interface QuizQuestion {
  id: string;
  question: string;
  description?: string;
  options: Array<{
    value: string;
    label: string;
    description?: string;
  }>;
}
