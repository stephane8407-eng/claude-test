/**
 * Quiz Page (/quiz)
 *
 * Multi-step questionnaire that collects user information.
 * On completion, saves profile to localStorage and redirects to /plan.
 *
 * HOW TO EDIT QUESTIONS:
 * - Modify the QUESTIONS array below
 * - Add new questions or change options
 * - Update the UserProfile type in /types/quiz.ts if you add new fields
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import StepIndicator from '@/components/ui/StepIndicator';
import QuestionCard from '@/components/quiz/QuestionCard';
import Button from '@/components/ui/Button';
import { UserProfile, QuizQuestion } from '@/types/quiz';
import { saveUserProfile } from '@/lib/storage';

// Define all quiz questions
const QUESTIONS: QuizQuestion[] = [
  {
    id: 'experienceLevel',
    question: "What's your experience with art?",
    description: 'Be honest - this helps us tailor the plan to your skill level.',
    options: [
      {
        value: 'complete-beginner',
        label: 'Complete beginner',
        description: "I've never really painted before or it's been many years",
      },
      {
        value: 'dabbled-a-bit',
        label: "I've dabbled a bit",
        description: "I've tried painting or drawing before, but not seriously",
      },
    ],
  },
  {
    id: 'goal',
    question: "What's your goal with abstract art?",
    options: [
      {
        value: 'relaxing-hobby',
        label: 'Relaxing creative hobby',
        description: 'Just for fun, relaxation, and personal enjoyment',
      },
      {
        value: 'hobby-maybe-sell',
        label: 'Hobby with potential to sell',
        description: 'Mainly a hobby, but I might sell some pieces in the future',
      },
      {
        value: 'side-business',
        label: 'Build a side business',
        description: 'I want to sell my work and potentially earn income',
      },
    ],
  },
  {
    id: 'budget',
    question: "What's your budget for starter materials?",
    description: 'This helps us recommend the right materials without overspending.',
    options: [
      {
        value: 'under-100',
        label: 'Under £100',
        description: 'Looking for budget-friendly essentials',
      },
      {
        value: '100-250',
        label: '£100 - £250',
        description: 'Willing to invest in quality starter materials',
      },
      {
        value: '250-plus',
        label: '£250+',
        description: 'Want to get the best materials from the start',
      },
    ],
  },
  {
    id: 'space',
    question: 'How much space do you have for painting?',
    options: [
      {
        value: 'kitchen-table',
        label: 'Kitchen table',
        description: 'Shared space that needs quick setup and pack-away',
      },
      {
        value: 'small-corner',
        label: 'Small corner or desk',
        description: 'A dedicated spot, but compact',
      },
      {
        value: 'dedicated-room',
        label: 'Dedicated room or large area',
        description: 'Plenty of space to spread out and leave things set up',
      },
    ],
  },
  {
    id: 'style',
    question: 'Which abstract style interests you most?',
    description: "Don't worry if you're not sure - you can explore multiple styles later!",
    options: [
      {
        value: 'acrylic-pouring',
        label: 'Acrylic pouring (fluid art)',
        description: 'Creating flowing, organic patterns with poured paint and mediums',
      },
      {
        value: 'palette-knife',
        label: 'Palette knife / textured abstract',
        description: 'Bold, thick paint applied with palette knives for texture and dimension',
      },
      {
        value: 'mixed-media',
        label: 'Mixed media',
        description: 'Combining paint, collage, texture paste, and various materials',
      },
      {
        value: 'not-sure',
        label: 'Not sure yet',
        description: 'I want to try different techniques and see what I enjoy',
      },
    ],
  },
  {
    id: 'timeAvailable',
    question: 'How much time can you dedicate per week?',
    description: 'This helps us calibrate your learning plan.',
    options: [
      {
        value: '1-2-hours',
        label: '1-2 hours',
        description: 'Steady pace, fitting art around a busy schedule',
      },
      {
        value: '3-5-hours',
        label: '3-5 hours',
        description: 'Regular practice with time for experimentation',
      },
      {
        value: '5-plus-hours',
        label: '5+ hours',
        description: 'Deep dive - ready to immerse myself in learning',
      },
    ],
  },
];

export default function QuizPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const currentQuestion = QUESTIONS[currentStep];
  const isLastStep = currentStep === QUESTIONS.length - 1;
  const canGoNext = answers[currentQuestion.id] !== undefined;

  const handleAnswer = (value: string) => {
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: value }));
  };

  const handleNext = () => {
    if (isLastStep) {
      // Create user profile and save to localStorage
      const profile: UserProfile = {
        experienceLevel: answers.experienceLevel as any,
        goal: answers.goal as any,
        budget: answers.budget as any,
        space: answers.space as any,
        style: answers.style as any,
        timeAvailable: answers.timeAvailable as any,
        completedAt: new Date().toISOString(),
      };

      saveUserProfile(profile);

      // Redirect to plan page
      router.push('/plan');
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8 text-center">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
          Let's Create Your Personalized Plan
        </h1>
        <p className="text-gray-600">
          Answer a few quick questions to get started. Takes about 2 minutes.
        </p>
      </div>

      <StepIndicator currentStep={currentStep + 1} totalSteps={QUESTIONS.length} />

      <QuestionCard
        question={currentQuestion.question}
        description={currentQuestion.description}
        options={currentQuestion.options}
        selectedValue={answers[currentQuestion.id] || ''}
        onSelect={handleAnswer}
      />

      <div className="flex gap-4 mt-8">
        <Button
          variant="outline"
          onClick={handleBack}
          disabled={currentStep === 0}
          className="flex-1"
        >
          ← Back
        </Button>

        <Button onClick={handleNext} disabled={!canGoNext} className="flex-1">
          {isLastStep ? 'See My Plan →' : 'Next →'}
        </Button>
      </div>

      {/* Progress indicator */}
      <div className="mt-8 text-center text-sm text-gray-500">
        Question {currentStep + 1} of {QUESTIONS.length}
      </div>
    </div>
  );
}
