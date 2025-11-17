/**
 * Resources Component
 *
 * Displays recommended learning resources (videos, articles, books).
 * Filtered based on user's style and goals.
 */

import React from 'react';
import Card from '../ui/Card';
import { Resource } from '@/types/plan';

interface ResourcesProps {
  resources: Resource[];
}

export default function Resources({ resources }: ResourcesProps) {
  // Icon for resource type
  const getIcon = (type: string) => {
    switch (type) {
      case 'youtube':
        return '🎥';
      case 'article':
        return '📄';
      case 'book':
        return '📚';
      case 'course':
        return '🎓';
      case 'website':
        return '🌐';
      default:
        return '📌';
    }
  };

  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Recommended Resources</h2>
      <p className="text-gray-600 mb-6">
        Curated learning resources to help you on your journey. These are selected based on your
        chosen style and goals.
      </p>

      <div className="grid gap-4 md:grid-cols-2">
        {resources.map((resource) => (
          <a
            key={resource.id}
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 bg-gray-50 hover:bg-primary-50 border border-gray-200 hover:border-primary-300 rounded-lg transition-all duration-200 group"
          >
            <div className="flex items-start gap-3">
              <div className="text-2xl flex-shrink-0">{getIcon(resource.type)}</div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 group-hover:text-primary-700 mb-1">
                  {resource.title}
                </h3>
                <p className="text-sm text-gray-600 mb-2">{resource.description}</p>

                <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
                  <span className="capitalize">{resource.type}</span>
                  {resource.author && (
                    <>
                      <span>•</span>
                      <span>{resource.author}</span>
                    </>
                  )}
                  {resource.duration && (
                    <>
                      <span>•</span>
                      <span>{resource.duration}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </a>
        ))}
      </div>

      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-900">
          <strong>Note:</strong> Some links lead to search results so you can choose the specific
          tutorial that appeals to you. Explore and find creators whose teaching style resonates!
        </p>
      </div>
    </Card>
  );
}
