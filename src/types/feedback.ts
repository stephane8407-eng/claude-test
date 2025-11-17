/**
 * Artwork Feedback Types
 *
 * These types define the structure for the artwork feedback feature.
 * Used in the /feedback page and mock AI response generator.
 */

/**
 * Experience level for feedback context
 */
export type FeedbackExperienceLevel = 'just-starting' | 'some-experience' | 'confident';

/**
 * Style for feedback context
 */
export type FeedbackStyle = 'acrylic-pouring' | 'palette-knife' | 'mixed-media' | 'not-sure';

/**
 * Metadata about the artwork being analyzed
 */
export interface ArtworkMetadata {
  experienceLevel: FeedbackExperienceLevel;
  style: FeedbackStyle;
  imageDataUrl?: string; // Base64 data URL of the image
  imageFile?: File; // The original file (not serializable, for upload only)
}

/**
 * Individual positive point about the artwork
 */
export interface FeedbackPositive {
  aspect: string; // e.g., "Color harmony", "Texture variation"
  comment: string;
}

/**
 * Individual improvement suggestion
 */
export interface FeedbackImprovement {
  area: string; // e.g., "Composition", "Contrast"
  suggestion: string;
  howTo?: string; // Optional tip on how to improve this area
}

/**
 * Mini exercise suggestion to practice
 */
export interface MiniExercise {
  title: string;
  description: string;
  materials?: string[];
  estimatedTime?: string;
}

/**
 * Complete AI feedback response
 * This is what the mock function returns (and what a real AI API should return)
 */
export interface ArtworkFeedback {
  summary: string; // Overall assessment, 2-3 sentences
  positives: FeedbackPositive[];
  improvements: FeedbackImprovement[];
  miniExercise: MiniExercise;
  encouragement: string; // Motivational closing message
}

/**
 * State of the feedback request
 */
export type FeedbackState = 'idle' | 'loading' | 'success' | 'error';
