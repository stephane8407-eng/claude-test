/**
 * Landing Page (/)
 *
 * Main entry point of the app. Introduces the concept and directs users to start the quiz.
 * Includes hero section, features, and "How it works" explanation.
 */

'use client';

import Link from 'next/link';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';

export default function HomePage() {
  const scrollToHowItWorks = () => {
    document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-20">
        <div className="text-6xl mb-6">🎨</div>
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
          Start Your Modern Abstract Art Journey
        </h1>
        <p className="text-xl md:text-2xl text-gray-600 mb-4 max-w-3xl mx-auto">
          Personalized guidance for beginners exploring acrylic pouring, palette knife painting,
          and mixed media
        </p>
        <p className="text-lg text-gray-500 mb-10 max-w-2xl mx-auto">
          Answer a few questions and get a custom starter plan: materials list, studio setup
          tips, and a 4-week learning roadmap tailored to your goals and budget.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/quiz">
            <Button size="lg" className="min-w-[200px]">
              Start Your Plan →
            </Button>
          </Link>
          <Button variant="outline" size="lg" onClick={scrollToHowItWorks}>
            How It Works
          </Button>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-20">
        <Card>
          <div className="text-4xl mb-4">📋</div>
          <h3 className="text-xl font-bold text-gray-900 mb-3">Personalized Materials List</h3>
          <p className="text-gray-600">
            Get exactly what you need based on your chosen style and budget - no guesswork, no
            wasted money on unnecessary supplies.
          </p>
        </Card>

        <Card>
          <div className="text-4xl mb-4">🏠</div>
          <h3 className="text-xl font-bold text-gray-900 mb-3">Space-Specific Setup Tips</h3>
          <p className="text-gray-600">
            Whether you have a kitchen table or dedicated studio, get practical advice for
            setting up your creative space.
          </p>
        </Card>

        <Card>
          <div className="text-4xl mb-4">📅</div>
          <h3 className="text-xl font-bold text-gray-900 mb-3">4-Week Learning Plan</h3>
          <p className="text-gray-600">
            Structured yet flexible roadmap with weekly tasks, techniques to practice, and
            progress milestones.
          </p>
        </Card>
      </div>

      {/* How It Works Section */}
      <div id="how-it-works" className="scroll-mt-20">
        <Card className="bg-gradient-to-br from-primary-50 to-accent-50 border-primary-200">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">How It Works</h2>

          <div className="space-y-6 max-w-2xl mx-auto">
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  Answer 6 Quick Questions
                </h3>
                <p className="text-gray-700">
                  Tell us about your experience level, goals, budget, available space, preferred
                  style, and time commitment. Takes just 2 minutes.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  Get Your Custom Plan
                </h3>
                <p className="text-gray-700">
                  Instantly receive a personalized starter plan with materials recommendations,
                  studio setup tips, and a week-by-week learning roadmap.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  Start Creating!
                </h3>
                <p className="text-gray-700">
                  Follow your plan at your own pace. Track your progress with our checklist, and
                  revisit recommended resources whenever you need guidance.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-accent-600 text-white rounded-full flex items-center justify-center font-bold">
                +
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  Get AI Feedback (New!)
                </h3>
                <p className="text-gray-700">
                  Upload photos of your paintings to get personalized feedback on what's working
                  well and areas to explore. Includes custom practice exercises!
                </p>
              </div>
            </div>
          </div>

          <div className="text-center mt-10">
            <Link href="/quiz">
              <Button size="lg">Get Started Now →</Button>
            </Link>
          </div>
        </Card>
      </div>

      {/* Testimonial / Encouragement Section */}
      <div className="mt-20 text-center max-w-3xl mx-auto">
        <div className="text-5xl mb-6">✨</div>
        <blockquote className="text-2xl font-medium text-gray-800 italic mb-6">
          "The hardest part of starting is not knowing where to begin. We make it simple."
        </blockquote>
        <p className="text-lg text-gray-600 mb-8">
          No more endless YouTube rabbit holes or buying the wrong supplies. Get clear,
          actionable guidance designed specifically for your situation.
        </p>
        <Link href="/quiz">
          <Button size="lg" variant="primary">
            Create My Plan →
          </Button>
        </Link>
      </div>
    </div>
  );
}
