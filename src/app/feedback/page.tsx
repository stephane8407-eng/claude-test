/**
 * Feedback Page (/feedback)
 *
 * Allows users to upload artwork images and receive AI-powered feedback.
 * Currently uses mock AI (getMockFeedback), but clearly marked where to integrate real AI.
 *
 * 🔄 TO INTEGRATE REAL AI:
 * 1. Create an API route at /app/api/analyze-artwork/route.ts
 * 2. Call a vision AI model (OpenAI GPT-4V, Claude with vision, etc.)
 * 3. Replace getMockFeedback() call with fetch('/api/analyze-artwork')
 * 4. Handle loading and error states properly
 *
 * See /config/mockFeedback.ts for detailed integration instructions.
 */

'use client';

import { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import ImageUpload from '@/components/feedback/ImageUpload';
import FeedbackDisplay from '@/components/feedback/FeedbackDisplay';
import {
  ArtworkMetadata,
  ArtworkFeedback,
  FeedbackExperienceLevel,
  FeedbackStyle,
  FeedbackState,
} from '@/types/feedback';
import { getMockFeedback } from '@/config/mockFeedback';

export default function FeedbackPage() {
  const [state, setState] = useState<FeedbackState>('idle');
  const [metadata, setMetadata] = useState<ArtworkMetadata>({
    experienceLevel: 'just-starting',
    style: 'not-sure',
  });
  const [feedback, setFeedback] = useState<ArtworkFeedback | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');

  const handleImageSelected = (file: File, dataUrl: string) => {
    setMetadata((prev) => ({ ...prev, imageFile: file, imageDataUrl: dataUrl }));
    setImagePreview(dataUrl);
  };

  const handleAnalyze = async () => {
    if (!metadata.imageDataUrl) {
      alert('Please upload an image first');
      return;
    }

    setState('loading');

    try {
      /**
       * 🔄 REPLACE THIS SECTION WITH REAL AI API CALL
       *
       * Example of how to integrate a real AI vision model:
       *
       * const response = await fetch('/api/analyze-artwork', {
       *   method: 'POST',
       *   headers: { 'Content-Type': 'application/json' },
       *   body: JSON.stringify({
       *     image: metadata.imageDataUrl,
       *     experienceLevel: metadata.experienceLevel,
       *     style: metadata.style,
       *   }),
       * });
       *
       * if (!response.ok) {
       *   throw new Error('Failed to analyze artwork');
       * }
       *
       * const feedbackData = await response.json();
       * setFeedback(feedbackData);
       *
       * For now, we're using a mock function that simulates the AI response:
       */
      const feedbackData = await getMockFeedback(metadata);
      setFeedback(feedbackData);
      setState('success');
    } catch (error) {
      console.error('Error analyzing artwork:', error);
      setState('error');
      alert('Failed to analyze artwork. Please try again.');
    }
  };

  const handleReset = () => {
    setState('idle');
    setFeedback(null);
    setImagePreview('');
    setMetadata({
      experienceLevel: 'just-starting',
      style: 'not-sure',
    });
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="text-6xl mb-4">🖼️</div>
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Get Feedback on Your Artwork
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Upload a photo of your abstract painting and receive personalized feedback on what's
          working well and areas to explore.
        </p>
      </div>

      {/* Show feedback if analysis is complete */}
      {state === 'success' && feedback ? (
        <div>
          <FeedbackDisplay feedback={feedback} imagePreview={imagePreview} />

          <div className="mt-8 text-center">
            <Button size="lg" onClick={handleReset}>
              Analyze Another Painting
            </Button>
          </div>
        </div>
      ) : (
        /* Show upload and analysis form */
        <div className="space-y-8">
          {/* Image Upload */}
          <Card>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Upload Your Artwork</h2>
            <ImageUpload onImageSelected={handleImageSelected} />
          </Card>

          {/* Metadata Form */}
          <Card>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Tell Us About Your Work</h2>
            <p className="text-gray-600 mb-6">
              This helps us provide more relevant and helpful feedback.
            </p>

            <div className="space-y-6">
              {/* Experience Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Experience Level
                </label>
                <select
                  value={metadata.experienceLevel}
                  onChange={(e) =>
                    setMetadata((prev) => ({
                      ...prev,
                      experienceLevel: e.target.value as FeedbackExperienceLevel,
                    }))
                  }
                  className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none"
                >
                  <option value="just-starting">Just starting</option>
                  <option value="some-experience">Some experience</option>
                  <option value="confident">Confident</option>
                </select>
              </div>

              {/* Style */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Style or Technique
                </label>
                <select
                  value={metadata.style}
                  onChange={(e) =>
                    setMetadata((prev) => ({
                      ...prev,
                      style: e.target.value as FeedbackStyle,
                    }))
                  }
                  className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none"
                >
                  <option value="acrylic-pouring">Acrylic pouring</option>
                  <option value="palette-knife">Palette knife</option>
                  <option value="mixed-media">Mixed media</option>
                  <option value="not-sure">Not sure</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Analyze Button */}
          <div className="text-center">
            <Button
              size="lg"
              onClick={handleAnalyze}
              disabled={state === 'loading' || !metadata.imageDataUrl}
              className="min-w-[250px]"
            >
              {state === 'loading' ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin">⏳</span>
                  Analyzing...
                </span>
              ) : (
                'Analyze My Artwork'
              )}
            </Button>

            {state === 'loading' && (
              <p className="text-sm text-gray-600 mt-4">
                Our AI is carefully analyzing your artwork. This takes a few seconds...
              </p>
            )}
          </div>

          {/* Info Box */}
          <Card className="bg-blue-50 border-blue-200">
            <div className="flex gap-3">
              <div className="text-2xl">💡</div>
              <div>
                <h3 className="font-bold text-gray-900 mb-2">Tips for Best Results</h3>
                <ul className="space-y-1 text-sm text-gray-700">
                  <li>✓ Use natural lighting when photographing your work</li>
                  <li>✓ Take the photo straight-on, not at an angle</li>
                  <li>✓ Make sure the entire artwork is visible in the frame</li>
                  <li>✓ Avoid shadows or glare on the painting</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
