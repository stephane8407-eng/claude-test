/**
 * Checklist Component
 *
 * Interactive checklist for tracking progress.
 * State is saved to localStorage so progress persists between sessions.
 */

'use client';

import React, { useState, useEffect } from 'react';
import Card from '../ui/Card';
import { ChecklistItem, loadChecklist, saveChecklist, toggleChecklistItem } from '@/lib/storage';

export default function Checklist() {
  const [items, setItems] = useState<ChecklistItem[]>([]);
  const [mounted, setMounted] = useState(false);

  // Load checklist from localStorage on mount
  useEffect(() => {
    setItems(loadChecklist());
    setMounted(true);
  }, []);

  // Save checklist to localStorage whenever it changes
  useEffect(() => {
    if (mounted) {
      saveChecklist(items);
    }
  }, [items, mounted]);

  const handleToggle = (itemId: string) => {
    setItems((prev) => toggleChecklistItem(prev, itemId));
  };

  const completedCount = items.filter((item) => item.completed).length;
  const progress = items.length > 0 ? (completedCount / items.length) * 100 : 0;

  if (!mounted) {
    return null; // Prevent hydration mismatch
  }

  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Progress Checklist</h2>
      <p className="text-gray-600 mb-4">
        Track your journey! Check off tasks as you complete them. Your progress is saved
        automatically.
      </p>

      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm font-medium text-primary-600">
            {completedCount} of {items.length}
          </span>
        </div>
        <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Checklist items */}
      <div className="space-y-2">
        {items.map((item) => (
          <label
            key={item.id}
            className={`
              flex items-start p-3 rounded-lg border-2 cursor-pointer transition-all
              ${
                item.completed
                  ? 'bg-green-50 border-green-300'
                  : 'bg-white border-gray-200 hover:border-primary-300 hover:bg-gray-50'
              }
            `}
          >
            <input
              type="checkbox"
              checked={item.completed}
              onChange={() => handleToggle(item.id)}
              className="mt-0.5 mr-3 w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
            />
            <span
              className={`flex-1 ${
                item.completed
                  ? 'text-gray-500 line-through'
                  : 'text-gray-900 font-medium'
              }`}
            >
              {item.label}
            </span>
          </label>
        ))}
      </div>

      {completedCount === items.length && items.length > 0 && (
        <div className="mt-6 p-4 bg-gradient-to-r from-primary-100 to-accent-100 border-2 border-primary-300 rounded-lg">
          <p className="text-center text-primary-900 font-semibold">
            🎉 Congratulations! You've completed your 4-week journey! Keep creating!
          </p>
        </div>
      )}
    </Card>
  );
}
