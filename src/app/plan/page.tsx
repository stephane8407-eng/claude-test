/**
 * Plan / Results Page (/plan)
 *
 * Displays the personalized plan based on user's quiz answers.
 * Shows: summary, materials list, studio setup, learning plan, resources, and checklist.
 * Includes button to navigate to feedback page.
 *
 * If no user profile exists, prompts user to take the quiz first.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import MaterialsList from '@/components/plan/MaterialsList';
import StudioSetup from '@/components/plan/StudioSetup';
import LearningPlan from '@/components/plan/LearningPlan';
import Resources from '@/components/plan/Resources';
import Checklist from '@/components/plan/Checklist';
import { loadUserProfile, clearUserProfile } from '@/lib/storage';
import {
  generateSummary,
  getPersonalizedMaterials,
  getLearningPlan,
  getStudioTips,
  getRecommendedResources,
} from '@/lib/planGenerator';
import { UserProfile } from '@/types/quiz';

export default function PlanPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const loadedProfile = loadUserProfile();
    setProfile(loadedProfile);
    setMounted(true);
  }, []);

  const handleRetakeQuiz = () => {
    if (confirm('This will reset your current plan. Continue?')) {
      clearUserProfile();
      router.push('/quiz');
    }
  };

  // Show loading state during hydration
  if (!mounted) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <p className="text-gray-600">Loading your plan...</p>
        </div>
      </div>
    );
  }

  // If no profile, prompt user to take quiz
  if (!profile) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card>
          <div className="text-center py-12">
            <div className="text-6xl mb-6">🎨</div>
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              No Plan Yet!
            </h1>
            <p className="text-gray-600 mb-8">
              Take our quick quiz to get your personalized abstract art starter plan.
            </p>
            <Link href="/quiz">
              <Button size="lg">Start the Quiz →</Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  // Generate personalized content
  const summary = generateSummary(profile);
  const materialGroups = getPersonalizedMaterials(profile);
  const learningPlan = getLearningPlan(profile);
  const studioTips = getStudioTips(profile);
  const resources = getRecommendedResources(profile);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="text-6xl mb-4">🎉</div>
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Your Personalized Art Plan
        </h1>
        <p className="text-lg text-gray-600 mb-6">
          Everything you need to start your abstract art journey
        </p>

        <div className="flex flex-wrap gap-4 justify-center">
          <Link href="/feedback">
            <Button size="lg" variant="primary">
              🖼️ Get Feedback on My Painting
            </Button>
          </Link>
          <Button size="md" variant="outline" onClick={handleRetakeQuiz}>
            Retake Quiz
          </Button>
        </div>
      </div>

      {/* Summary Section */}
      <div className="mb-8">
        <Card>
          <div className="flex items-start gap-4">
            <div className="text-4xl">👤</div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 mb-3">Your Summary</h2>
              <p className="text-lg text-gray-700 leading-relaxed">{summary}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Content - Two Column Layout on Desktop */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column - Main Content */}
        <div className="lg:col-span-2 space-y-8">
          <MaterialsList materialGroups={materialGroups} />
          <StudioSetup tips={studioTips} />
          <LearningPlan plan={learningPlan} />
          <Resources resources={resources} />
        </div>

        {/* Right Column - Sidebar */}
        <div className="lg:col-span-1 space-y-8">
          <Checklist />

          {/* Call to action for feedback */}
          <Card className="bg-gradient-to-br from-accent-50 to-primary-50 border-accent-200">
            <div className="text-center">
              <div className="text-4xl mb-3">🖼️</div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                Created Your First Piece?
              </h3>
              <p className="text-sm text-gray-700 mb-4">
                Upload a photo and get personalized AI feedback on what's working well and areas to explore!
              </p>
              <Link href="/feedback">
                <Button fullWidth>Get Artwork Feedback</Button>
              </Link>
            </div>
          </Card>

          {/* Quick tips card */}
          <Card className="bg-blue-50 border-blue-200">
            <h3 className="font-bold text-gray-900 mb-3">💡 Quick Tips</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>✓ Start with essential materials, add more later</li>
              <li>✓ Practice on small surfaces first</li>
              <li>✓ Don't fear mistakes - they're learning opportunities</li>
              <li>✓ Take photos of your work to track progress</li>
              <li>✓ Join online communities for inspiration</li>
            </ul>
          </Card>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="mt-12 text-center">
        <Card className="bg-gradient-to-r from-primary-600 to-accent-600 text-white">
          <div className="py-8">
            <h2 className="text-2xl font-bold mb-4">Ready to Start Creating?</h2>
            <p className="text-lg mb-6 text-primary-50">
              Bookmark this page and return anytime for guidance. Your journey starts now!
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
              >
                <Button variant="secondary" size="lg">
                  Back to Top ↑
                </Button>
              </a>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
