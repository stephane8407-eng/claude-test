/**
 * Learning Plan Component
 *
 * Displays the 4-week learning plan with collapsible weeks.
 * Each week shows tasks and estimated time.
 */

import React, { useState } from 'react';
import Card from '../ui/Card';
import { LearningPlan as LearningPlanType } from '@/types/plan';

interface LearningPlanProps {
  plan: LearningPlanType;
}

export default function LearningPlan({ plan }: LearningPlanProps) {
  const [expandedWeeks, setExpandedWeeks] = useState<number[]>([1]); // Week 1 open by default

  const toggleWeek = (weekNumber: number) => {
    if (expandedWeeks.includes(weekNumber)) {
      setExpandedWeeks(expandedWeeks.filter((w) => w !== weekNumber));
    } else {
      setExpandedWeeks([...expandedWeeks, weekNumber]);
    }
  };

  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Your 4-Week Learning Plan</h2>
      <p className="text-gray-600 mb-6">
        Follow this structured plan to build your skills week by week. Click each week to expand.
      </p>

      <div className="space-y-4">
        {plan.weeks.map((week) => {
          const isExpanded = expandedWeeks.includes(week.weekNumber);

          return (
            <div
              key={week.weekNumber}
              className="border-2 border-gray-200 rounded-lg overflow-hidden"
            >
              {/* Week header - clickable */}
              <button
                onClick={() => toggleWeek(week.weekNumber)}
                className="w-full p-4 bg-gray-50 hover:bg-gray-100 transition-colors text-left flex items-center justify-between"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                      {week.weekNumber}
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900">{week.title}</h3>
                      <p className="text-sm text-gray-600">{week.description}</p>
                    </div>
                  </div>
                </div>
                <div className="ml-4">
                  <svg
                    className={`w-6 h-6 text-gray-600 transition-transform ${
                      isExpanded ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
              </button>

              {/* Week tasks - expandable */}
              {isExpanded && (
                <div className="p-4 bg-white border-t border-gray-200">
                  <div className="mb-3 px-3 py-2 bg-primary-50 rounded-lg">
                    <p className="text-sm font-medium text-primary-900">
                      <strong>Key Focus:</strong> {week.keyFocus}
                    </p>
                  </div>

                  <div className="space-y-3">
                    {week.tasks.map((task, index) => (
                      <div key={task.id} className="flex gap-3">
                        <div className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-medium mt-0.5">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{task.title}</h4>
                          <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                          {task.estimatedTime && (
                            <p className="text-xs text-gray-500 mt-1">
                              ⏱ {task.estimatedTime}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 p-4 bg-accent-50 border border-accent-200 rounded-lg">
        <p className="text-sm text-accent-900">
          <strong>Remember:</strong> This is a guide, not a rigid schedule. Go at your own pace,
          revisit tasks as needed, and most importantly - enjoy the creative process!
        </p>
      </div>
    </Card>
  );
}
