/**
 * Question Card Component
 *
 * Displays a single quiz question with radio button options.
 * Used in the quiz page for each step.
 */

import React from 'react';
import Card from '../ui/Card';

interface Option {
  value: string;
  label: string;
  description?: string;
}

interface QuestionCardProps {
  question: string;
  description?: string;
  options: Option[];
  selectedValue: string;
  onSelect: (value: string) => void;
}

export default function QuestionCard({
  question,
  description,
  options,
  selectedValue,
  onSelect,
}: QuestionCardProps) {
  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">{question}</h2>
      {description && <p className="text-gray-600 mb-6">{description}</p>}

      <div className="space-y-3">
        {options.map((option) => (
          <label
            key={option.value}
            className={`
              block p-4 border-2 rounded-lg cursor-pointer transition-all duration-200
              ${
                selectedValue === option.value
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
              }
            `}
          >
            <div className="flex items-start">
              <input
                type="radio"
                name="question"
                value={option.value}
                checked={selectedValue === option.value}
                onChange={(e) => onSelect(e.target.value)}
                className="mt-1 mr-3 text-primary-600 focus:ring-primary-500"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900">{option.label}</div>
                {option.description && (
                  <div className="text-sm text-gray-600 mt-1">{option.description}</div>
                )}
              </div>
            </div>
          </label>
        ))}
      </div>
    </Card>
  );
}
