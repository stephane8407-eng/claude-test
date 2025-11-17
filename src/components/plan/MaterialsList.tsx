/**
 * Materials List Component
 *
 * Displays personalized materials grouped by category.
 * Shows essential items first, then recommended, then optional.
 */

import React from 'react';
import Card from '../ui/Card';
import { MaterialGroup } from '@/types/materials';

interface MaterialsListProps {
  materialGroups: MaterialGroup[];
}

export default function MaterialsList({ materialGroups }: MaterialsListProps) {
  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Materials List</h2>
      <p className="text-gray-600 mb-6">
        Here's what you'll need to get started. Essential items are listed first.
      </p>

      <div className="space-y-6">
        {materialGroups.map((group) => (
          <div key={group.category}>
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
              <span className="w-2 h-2 bg-primary-600 rounded-full mr-2" />
              {group.categoryLabel}
            </h3>

            <div className="space-y-3 ml-4">
              {group.items.map((item) => (
                <div
                  key={item.id}
                  className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900">{item.name}</span>
                        {item.priority === 'essential' && (
                          <span className="text-xs px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full font-medium">
                            Essential
                          </span>
                        )}
                        {item.priority === 'recommended' && (
                          <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium">
                            Recommended
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                      {item.estimatedCost && (
                        <p className="text-sm text-gray-500 mt-1">
                          Estimated cost: {item.estimatedCost}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900">
          <strong>Tip:</strong> You don't need to buy everything at once! Start with the
          essentials, then add more as you discover what you enjoy.
        </p>
      </div>
    </Card>
  );
}
