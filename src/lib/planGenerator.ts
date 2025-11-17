/**
 * Plan Generator
 *
 * This file contains logic to generate personalized plans based on user profile.
 * It filters materials, selects learning plans, chooses resources, and generates setup tips.
 */

import { UserProfile } from '@/types/quiz';
import { Material, MaterialGroup } from '@/types/materials';
import { LearningPlan, StudioTip, Resource } from '@/types/plan';
import { MATERIALS, getCategoryLabel } from '@/config/materials';
import {
  ACRYLIC_POURING_PLAN,
  PALETTE_KNIFE_PLAN,
  MIXED_MEDIA_PLAN,
  BEGINNER_GENERAL_PLAN,
  STUDIO_TIPS,
} from '@/config/learningPlan';
import { RESOURCES } from '@/config/resources';

/**
 * Generate a personalized summary based on user profile
 */
export function generateSummary(profile: UserProfile): string {
  const { experienceLevel, goal, style, timeAvailable } = profile;

  const experienceText =
    experienceLevel === 'complete-beginner'
      ? "You're starting your abstract art journey from scratch"
      : "You've dabbled with art before";

  const goalText =
    goal === 'relaxing-hobby'
      ? 'as a relaxing creative hobby'
      : goal === 'hobby-maybe-sell'
      ? 'as a hobby with potential to sell your work in the future'
      : 'with the goal of building a side business';

  const styleText =
    style === 'acrylic-pouring'
      ? 'acrylic pouring (fluid art)'
      : style === 'palette-knife'
      ? 'palette knife and textured abstract painting'
      : style === 'mixed-media'
      ? 'mixed media abstract art'
      : 'abstract painting (exploring different techniques)';

  const timeText =
    timeAvailable === '1-2-hours'
      ? 'With 1-2 hours per week, you\'ll make steady progress at a comfortable pace.'
      : timeAvailable === '3-5-hours'
      ? 'With 3-5 hours per week, you\'ll have time to practice multiple techniques and build skills quickly.'
      : 'With 5+ hours per week, you can dive deep, experiment extensively, and see rapid growth.';

  return `${experienceText} ${goalText}, focusing on ${styleText}. ${timeText}`;
}

/**
 * Filter and group materials based on user profile
 */
export function getPersonalizedMaterials(profile: UserProfile): MaterialGroup[] {
  const { style, budget } = profile;

  // Filter materials relevant to user's style and budget
  const filtered = MATERIALS.filter((material) => {
    // Check if material is relevant for this style
    const styleMatch =
      !material.requiredFor || material.requiredFor.length === 0 || material.requiredFor.includes(style);

    // Check if material fits budget
    const budgetMatch =
      !material.budgetLevel || material.budgetLevel.length === 0 || material.budgetLevel.includes(budget);

    return styleMatch && budgetMatch;
  });

  // Sort by priority (essential first, then recommended, then optional)
  const priorityOrder = { essential: 1, recommended: 2, optional: 3 };
  filtered.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

  // Group by category
  const grouped: Record<string, Material[]> = {};
  filtered.forEach((material) => {
    if (!grouped[material.category]) {
      grouped[material.category] = [];
    }
    grouped[material.category].push(material);
  });

  // Convert to array of MaterialGroup
  const result: MaterialGroup[] = [];
  const categoryOrder: string[] = ['paints', 'canvases', 'mediums', 'tools', 'protection', 'optional'];

  categoryOrder.forEach((category) => {
    if (grouped[category] && grouped[category].length > 0) {
      result.push({
        category: category as any,
        categoryLabel: getCategoryLabel(category),
        items: grouped[category],
      });
    }
  });

  return result;
}

/**
 * Get the appropriate learning plan based on style
 */
export function getLearningPlan(profile: UserProfile): LearningPlan {
  const { style } = profile;

  switch (style) {
    case 'acrylic-pouring':
      return ACRYLIC_POURING_PLAN;
    case 'palette-knife':
      return PALETTE_KNIFE_PLAN;
    case 'mixed-media':
      return MIXED_MEDIA_PLAN;
    case 'not-sure':
    default:
      return BEGINNER_GENERAL_PLAN;
  }
}

/**
 * Get studio setup tips relevant to user's space and style
 */
export function getStudioTips(profile: UserProfile): StudioTip[] {
  const { space, style } = profile;

  return STUDIO_TIPS.filter((tip) => {
    // If tip has no specific relevantFor, show it to everyone
    if (!tip.relevantFor || tip.relevantFor.length === 0) {
      return true;
    }

    // Show tip if it's relevant for this space
    return tip.relevantFor.includes(space);
  }).slice(0, 8); // Limit to 8 tips
}

/**
 * Get recommended resources based on style and goal
 */
export function getRecommendedResources(profile: UserProfile): Resource[] {
  const { style, goal } = profile;

  // Convert style to tag format
  const styleTags = [style, 'general', 'beginner'];

  // Add goal-related tags
  if (goal === 'hobby-maybe-sell' || goal === 'side-business') {
    styleTags.push('selling', 'business');
  }

  // Filter resources that match user's tags
  const filtered = RESOURCES.filter((resource) => {
    return resource.tags.some((tag) => styleTags.includes(tag));
  });

  // Prioritize resources that match the specific style first
  filtered.sort((a, b) => {
    const aStyleMatch = a.tags.includes(style) ? 1 : 0;
    const bStyleMatch = b.tags.includes(style) ? 1 : 0;
    return bStyleMatch - aStyleMatch;
  });

  // Return top 10 resources
  return filtered.slice(0, 10);
}
