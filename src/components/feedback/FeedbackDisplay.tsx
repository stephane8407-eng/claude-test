/**
 * Feedback Display Component
 *
 * Displays AI feedback about the artwork in styled cards.
 * Shows summary, positives, improvements, and mini exercise.
 */

import React from 'react';
import Card from '../ui/Card';
import { ArtworkFeedback } from '@/types/feedback';

interface FeedbackDisplayProps {
  feedback: ArtworkFeedback;
  imagePreview?: string;
}

export default function FeedbackDisplay({ feedback, imagePreview }: FeedbackDisplayProps) {
  return (
    <div className="space-y-6">
      {/* Image preview (if provided) */}
      {imagePreview && (
        <Card>
          <img
            src={imagePreview}
            alt="Your artwork"
            className="w-full h-auto max-h-96 object-contain rounded-lg"
          />
        </Card>
      )}

      {/* Summary */}
      <Card>
        <div className="flex items-start gap-4">
          <div className="text-4xl">✨</div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Overall Assessment</h2>
            <p className="text-gray-700 leading-relaxed">{feedback.summary}</p>
          </div>
        </div>
      </Card>

      {/* Positives */}
      <Card>
        <div className="flex items-start gap-4">
          <div className="text-4xl">💚</div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">What's Working Well</h2>
            <div className="space-y-4">
              {feedback.positives.map((positive, index) => (
                <div key={index} className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h3 className="font-semibold text-green-900 mb-2">{positive.aspect}</h3>
                  <p className="text-green-800">{positive.comment}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Improvements */}
      <Card>
        <div className="flex items-start gap-4">
          <div className="text-4xl">🎯</div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Areas to Explore</h2>
            <div className="space-y-4">
              {feedback.improvements.map((improvement, index) => (
                <div key={index} className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h3 className="font-semibold text-blue-900 mb-2">{improvement.area}</h3>
                  <p className="text-blue-800 mb-2">{improvement.suggestion}</p>
                  {improvement.howTo && (
                    <div className="mt-3 p-3 bg-white rounded border border-blue-200">
                      <p className="text-sm text-blue-700">
                        <strong>How to try it:</strong> {improvement.howTo}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Mini Exercise */}
      <Card>
        <div className="flex items-start gap-4">
          <div className="text-4xl">🚀</div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Try This Exercise</h2>
            <div className="p-6 bg-gradient-to-br from-primary-50 to-accent-50 border-2 border-primary-200 rounded-lg">
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {feedback.miniExercise.title}
              </h3>
              <p className="text-gray-700 mb-4">{feedback.miniExercise.description}</p>

              {feedback.miniExercise.materials && feedback.miniExercise.materials.length > 0 && (
                <div className="mb-4">
                  <p className="font-semibold text-gray-800 mb-2">Materials needed:</p>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                    {feedback.miniExercise.materials.map((material, index) => (
                      <li key={index}>{material}</li>
                    ))}
                  </ul>
                </div>
              )}

              {feedback.miniExercise.estimatedTime && (
                <p className="text-sm text-gray-600">
                  ⏱ Estimated time: {feedback.miniExercise.estimatedTime}
                </p>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Encouragement */}
      <Card>
        <div className="p-6 bg-gradient-to-r from-accent-100 to-primary-100 border-2 border-accent-300 rounded-lg text-center">
          <p className="text-lg text-gray-800 font-medium italic">"{feedback.encouragement}"</p>
        </div>
      </Card>
    </div>
  );
}
