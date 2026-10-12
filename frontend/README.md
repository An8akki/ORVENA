# ORVENA Frontend

Next.js-based frontend application for the ORVENA career intelligence platform.

## Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix primitives)
- **Forms**: React Hook Form + Zod
- **Icons**: Lucide React
- **API Client**: Custom fetch wrapper

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── globals.css        # Global styles and Tailwind
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Landing page
├── components/
│   ├── ui/                # Base UI components (shadcn)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── alert.tsx
│   │   ├── progress.tsx
│   │   ├── separator.tsx
│   │   ├── label.tsx
│   │   └── textarea.tsx
│   └── shared/            # Shared components
│       ├── LoadingSpinner.tsx
│       ├── ErrorState.tsx
│       └── EmptyState.tsx
├── lib/
│   ├── utils.ts           # Utility functions
│   └── api-client.ts      # API client with error handling
└── types/
    └── index.ts           # TypeScript type definitions
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.local.example .env.local
# Edit .env.local with your values
```

3. Run development server:
```bash
npm run dev
```

4. Open http://localhost:3000

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Generate test coverage report

## Environment Variables

Required variables in `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Design System

### Colors

The application uses a professional color scheme with:
- Primary: Blue (`hsl(221.2 83.2% 53.3%)`)
- Background: White/Dark
- Muted: Subtle grays for secondary content

### Typography

- Font: Inter (Google Fonts)
- Base size: 16px
- Scale: Tailwind's default type scale

### Spacing

Following Tailwind's spacing scale (4px base unit)

### Components

All UI components follow shadcn/ui patterns with:
- Consistent API across components
- Full TypeScript support
- Accessible by default (Radix UI)
- Customizable through className prop

## API Integration

API calls use the centralized client in `lib/api-client.ts`:

```typescript
import api from '@/lib/api-client'

// GET request
const profile = await api.get('/api/v1/profile', token)

// POST request
const result = await api.post('/api/v1/career/recommendations', data, token)

// File upload
const response = await api.upload('/api/v1/resumes', formData, token)
```

## Error Handling

Errors are handled through:
1. API client throws `APIError` with status, code, and message
2. Components catch and display using `ErrorState` component
3. Forms show field-level errors via React Hook Form

## Next Steps

- [ ] Implement authentication pages
- [ ] Create dashboard layout
- [ ] Build feature modules (career, resume, jobs, interviews)
- [ ] Add form validation schemas (Zod)
- [ ] Implement Supabase Auth integration
- [ ] Add tests for components and utilities
- [ ] Implement responsive navigation
- [ ] Add dark mode support (optional)

## Development Guidelines

1. **Components**: Create reusable components in `components/shared`
2. **Pages**: Use App Router in `app/` directory
3. **Types**: Add TypeScript types to `types/index.ts`
4. **Utils**: Add utility functions to `lib/utils.ts`
5. **API**: Use the centralized API client
6. **Styling**: Use Tailwind CSS classes, avoid custom CSS
7. **Accessibility**: Ensure WCAG 2.2 AA compliance

## Browser Support

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Performance

- Server Components by default
- Client Components only when needed
- Image optimization via Next.js Image
- Code splitting automatic via Next.js

---

Built with Next.js 14 and TypeScript
