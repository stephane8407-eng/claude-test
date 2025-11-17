# Abstract Art Starter

A personalized web app that helps beginners start modern abstract painting (acrylic pouring, palette knife, and mixed media) by generating a custom starter plan.

## Features

- **Personalized Quiz**: Answer 6 quick questions about experience, goals, budget, space, style, and time
- **Custom Materials List**: Get recommendations tailored to your style and budget
- **Studio Setup Tips**: Space-specific advice for kitchen tables, corners, or dedicated rooms
- **4-Week Learning Plan**: Structured roadmap with weekly tasks and techniques
- **Recommended Resources**: Curated YouTube videos, articles, and books
- **Progress Checklist**: Track your journey with localStorage persistence
- **AI Artwork Feedback** _(New!)_: Upload paintings to get personalized feedback and practice exercises

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React hooks + localStorage
- **No Backend**: Fully client-side (mock AI for feedback)

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
npm run build
npm run start
```

## Project Structure

```
src/
├── app/                    # Next.js pages (routes)
│   ├── page.tsx            # Landing page (/)
│   ├── quiz/page.tsx       # Quiz page (/quiz)
│   ├── plan/page.tsx       # Results page (/plan)
│   └── feedback/page.tsx   # Artwork feedback (/feedback)
│
├── components/             # Reusable React components
│   ├── ui/                 # Generic UI components
│   ├── quiz/               # Quiz-specific components
│   ├── plan/               # Plan page components
│   └── feedback/           # Feedback page components
│
├── config/                 # Content configuration files
│   ├── materials.ts        # Materials data
│   ├── learningPlan.ts     # 4-week plans
│   ├── resources.ts        # Learning resources
│   └── mockFeedback.ts     # Mock AI feedback generator
│
├── types/                  # TypeScript type definitions
│   ├── quiz.ts
│   ├── materials.ts
│   ├── plan.ts
│   └── feedback.ts
│
└── lib/                    # Utility functions
    ├── storage.ts          # localStorage helpers
    └── planGenerator.ts    # Plan generation logic
```

## How to Customize Content

### Add New Materials

Edit \`/src/config/materials.ts\`:

```typescript
{
  id: 'new-item',
  name: 'Item Name',
  category: 'paints',
  description: 'Description here',
  estimatedCost: '£10-20',
  requiredFor: ['acrylic-pouring'],
  budgetLevel: ['under-100', '100-250'],
  priority: 'essential',
}
```

### Modify Learning Plans

Edit \`/src/config/learningPlan.ts\`:
- Adjust tasks in existing weeks
- Add new weeks or modify descriptions
- Create plans for new styles

### Add Resources

Edit \`/src/config/resources.ts\` to add new learning resources.

### Add Quiz Questions

Edit \`/src/app/quiz/page.tsx\` (QUESTIONS array) and update types accordingly.

## Integrating Real AI for Artwork Feedback

Currently uses mock AI. To integrate real AI:

1. Create \`/src/app/api/analyze-artwork/route.ts\`
2. Call OpenAI GPT-4V, Claude, or other vision AI
3. Replace getMockFeedback() in \`/src/app/feedback/page.tsx\`

See \`/src/config/mockFeedback.ts\` for detailed integration instructions.

## License

MIT License - feel free to use and modify for your projects.

---

Built with ❤️ for aspiring abstract artists
