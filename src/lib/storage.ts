/**
 * LocalStorage Utilities
 *
 * Centralized functions for saving and retrieving data from localStorage.
 * This keeps all storage logic in one place for easy maintenance.
 */

import { UserProfile } from '@/types/quiz';

const STORAGE_KEYS = {
  USER_PROFILE: 'abstract-art-starter:user-profile',
  CHECKLIST: 'abstract-art-starter:checklist',
} as const;

/**
 * Save user profile to localStorage
 */
export function saveUserProfile(profile: UserProfile): void {
  try {
    localStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(profile));
  } catch (error) {
    console.error('Failed to save user profile:', error);
  }
}

/**
 * Load user profile from localStorage
 * Returns null if no profile exists
 */
export function loadUserProfile(): UserProfile | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.USER_PROFILE);
    if (!stored) return null;
    return JSON.parse(stored) as UserProfile;
  } catch (error) {
    console.error('Failed to load user profile:', error);
    return null;
  }
}

/**
 * Clear user profile from localStorage
 * Useful if user wants to retake the quiz
 */
export function clearUserProfile(): void {
  try {
    localStorage.removeItem(STORAGE_KEYS.USER_PROFILE);
  } catch (error) {
    console.error('Failed to clear user profile:', error);
  }
}

/**
 * Checklist item structure
 */
export interface ChecklistItem {
  id: string;
  label: string;
  completed: boolean;
}

/**
 * Save checklist state to localStorage
 */
export function saveChecklist(items: ChecklistItem[]): void {
  try {
    localStorage.setItem(STORAGE_KEYS.CHECKLIST, JSON.stringify(items));
  } catch (error) {
    console.error('Failed to save checklist:', error);
  }
}

/**
 * Load checklist state from localStorage
 * Returns default checklist if none exists
 */
export function loadChecklist(): ChecklistItem[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.CHECKLIST);
    if (!stored) return getDefaultChecklist();
    return JSON.parse(stored) as ChecklistItem[];
  } catch (error) {
    console.error('Failed to load checklist:', error);
    return getDefaultChecklist();
  }
}

/**
 * Default checklist items
 * These can be customized based on user's profile
 */
function getDefaultChecklist(): ChecklistItem[] {
  return [
    {
      id: 'checklist-1',
      label: 'Buy your starter materials',
      completed: false,
    },
    {
      id: 'checklist-2',
      label: 'Set up your painting space',
      completed: false,
    },
    {
      id: 'checklist-3',
      label: 'Complete your first practice piece',
      completed: false,
    },
    {
      id: 'checklist-4',
      label: 'Finish Week 1 of the learning plan',
      completed: false,
    },
    {
      id: 'checklist-5',
      label: 'Experiment with color mixing',
      completed: false,
    },
    {
      id: 'checklist-6',
      label: 'Complete Week 2 of the learning plan',
      completed: false,
    },
    {
      id: 'checklist-7',
      label: 'Create your first larger piece',
      completed: false,
    },
    {
      id: 'checklist-8',
      label: 'Complete Week 3 of the learning plan',
      completed: false,
    },
    {
      id: 'checklist-9',
      label: 'Learn to varnish your paintings',
      completed: false,
    },
    {
      id: 'checklist-10',
      label: 'Complete your 4-week journey!',
      completed: false,
    },
  ];
}

/**
 * Toggle a single checklist item
 */
export function toggleChecklistItem(items: ChecklistItem[], itemId: string): ChecklistItem[] {
  return items.map((item) =>
    item.id === itemId ? { ...item, completed: !item.completed } : item
  );
}
