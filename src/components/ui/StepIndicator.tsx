/**
 * Step Indicator Component
 *
 * Shows progress through the quiz (e.g., "Step 2 of 6").
 * Visual progress bar helps users see how far along they are.
 */

import React from 'react';

interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

export default function StepIndicator({ currentStep, totalSteps }: StepIndicatorProps) {
  const progressPercentage = (currentStep / totalSteps) * 100;

  return (
    <div className="mb-8">
      {/* Text indicator */}
      <div className="text-sm font-medium text-gray-600 mb-2">
        Step {currentStep} of {totalSteps}
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-primary-600 transition-all duration-300 ease-out"
          style={{ width: `${progressPercentage}%` }}
        />
      </div>
    </div>
  );
}
