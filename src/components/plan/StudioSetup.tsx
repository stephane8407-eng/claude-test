/**
 * Studio Setup Component
 *
 * Displays personalized studio setup tips based on user's available space.
 */

import React from 'react';
import Card from '../ui/Card';
import { StudioTip } from '@/types/plan';

interface StudioSetupProps {
  tips: StudioTip[];
}

export default function StudioSetup({ tips }: StudioSetupProps) {
  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Studio Setup Tips</h2>
      <p className="text-gray-600 mb-6">
        Set up your creative space for success. These tips are tailored to your available space.
      </p>

      <div className="grid gap-4 md:grid-cols-2">
        {tips.map((tip) => (
          <div
            key={tip.id}
            className="p-4 bg-gradient-to-br from-primary-50 to-accent-50 rounded-lg border border-primary-100"
          >
            <h3 className="font-semibold text-gray-900 mb-2">{tip.title}</h3>
            <p className="text-sm text-gray-700">{tip.description}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
