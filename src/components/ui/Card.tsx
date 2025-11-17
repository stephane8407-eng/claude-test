/**
 * Card Component
 *
 * Reusable card container for consistent spacing and styling.
 * Used throughout the app for grouping related content.
 */

import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export default function Card({ children, className = '', noPadding = false }: CardProps) {
  const paddingStyle = noPadding ? '' : 'p-6';

  return (
    <div className={`bg-white rounded-xl shadow-md border border-gray-100 ${paddingStyle} ${className}`}>
      {children}
    </div>
  );
}
