/**
 * Image Upload Component
 *
 * Allows users to upload images via drag-and-drop or file selection.
 * Displays preview of the uploaded image.
 */

'use client';

import React, { useState, useCallback } from 'react';

interface ImageUploadProps {
  onImageSelected: (file: File, dataUrl: string) => void;
}

export default function ImageUpload({ onImageSelected }: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please upload an image file (JPEG, PNG, etc.)');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Image size should be less than 5MB');
        return;
      }

      // Create preview and data URL
      const reader = new FileReader();
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string;
        setPreview(dataUrl);
        onImageSelected(file, dataUrl);
      };
      reader.readAsDataURL(file);
    },
    [onImageSelected]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  return (
    <div>
      {!preview ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`
            border-2 border-dashed rounded-lg p-12 text-center transition-all
            ${
              isDragging
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 bg-gray-50 hover:border-primary-400'
            }
          `}
        >
          <div className="space-y-4">
            <div className="text-6xl">🎨</div>
            <div>
              <p className="text-lg font-medium text-gray-900 mb-2">
                Drag and drop your painting here
              </p>
              <p className="text-sm text-gray-600 mb-4">or</p>
              <label className="inline-block px-6 py-3 bg-primary-600 text-white font-medium rounded-lg cursor-pointer hover:bg-primary-700 transition-colors">
                Choose Image
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileInput}
                  className="hidden"
                />
              </label>
            </div>
            <p className="text-xs text-gray-500">
              Supports JPEG, PNG (max 5MB)
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="relative rounded-lg overflow-hidden border-2 border-gray-200">
            <img
              src={preview}
              alt="Your artwork preview"
              className="w-full h-auto max-h-96 object-contain bg-gray-100"
            />
          </div>

          <button
            onClick={() => {
              setPreview(null);
              onImageSelected(null as any, '');
            }}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            ← Choose a different image
          </button>
        </div>
      )}
    </div>
  );
}
