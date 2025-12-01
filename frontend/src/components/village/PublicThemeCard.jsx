/**
 * PublicThemeCard Component
 *
 * Friendly display of identity themes for public village page.
 * NO confidence scores, NO "Theme #1/#2" labels, NO AI terminology.
 * Shows: title, story bullets, project ideas, explore link.
 */
import { Link } from 'react-router-dom';
import './PublicThemeCard.css';

export function PublicThemeCard({ theme, villageSlug }) {
  // Extract key points from the theme story (split into bullet points)
  const storyPoints = extractStoryPoints(theme.theme_story);

  // Get 1-2 project ideas
  const projectIdeas = (theme.project_ideas || []).slice(0, 2);

  return (
    <article className="spv-theme-card">
      <header className="spv-theme-card__header">
        <h3 className="spv-theme-card__title">{theme.theme_name}</h3>
      </header>

      <div className="spv-theme-card__content">
        {/* Story points */}
        {storyPoints.length > 0 && (
          <ul className="spv-theme-card__story">
            {storyPoints.map((point, index) => (
              <li key={index} className="spv-theme-card__story-item">
                {point}
              </li>
            ))}
          </ul>
        )}

        {/* Project ideas */}
        {projectIdeas.length > 0 && (
          <div className="spv-theme-card__ideas">
            <h4 className="spv-theme-card__ideas-title">Idées à explorer</h4>
            <ul className="spv-theme-card__ideas-list">
              {projectIdeas.map((idea, index) => (
                <li key={index} className="spv-theme-card__idea">
                  <svg viewBox="0 0 20 20" fill="currentColor" className="spv-theme-card__idea-icon">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>{idea.title || idea}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <footer className="spv-theme-card__footer">
        <Link
          to={`/themes/${theme.slug || theme.id}`}
          className="spv-theme-card__link"
        >
          Explorer ce thème
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </Link>
      </footer>
    </article>
  );
}

/**
 * Extract 2-3 key bullet points from a theme story paragraph
 */
function extractStoryPoints(story) {
  if (!story) return [];

  // If the story already has bullet points or numbered items, use those
  const bulletMatch = story.match(/[•\-\*]\s*[^•\-\*\n]+/g);
  if (bulletMatch && bulletMatch.length >= 2) {
    return bulletMatch.slice(0, 3).map(s => s.replace(/^[•\-\*]\s*/, '').trim());
  }

  // Otherwise split by sentences and take key ones
  const sentences = story
    .split(/[.!?]+/)
    .map(s => s.trim())
    .filter(s => s.length > 20 && s.length < 200);

  return sentences.slice(0, 3);
}
