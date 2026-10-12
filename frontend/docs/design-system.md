# ORVENA Design System

**Version 1.0** | Premium Career Intelligence Platform

---

## Overview

The ORVENA design system creates a distinctive, premium visual identity centered around the **pathfinding metaphor** — guiding professionals through their career journey with clarity, intelligence, and confidence.

### Core Philosophy

- **Professional yet approachable**: Serious about careers, warm in guidance
- **Data-rich but clear**: Complex intelligence presented with visual clarity
- **Pathfinding visualization**: Career journey as an explorable network, not a linear list
- **Offline-first confidence**: Immediate, reliable intelligence without dependencies

---

## Color Palette

### Primary Colors

#### Midnight Ink `#142522`
**Role**: Professional foundation, primary text, navigation headers  
**Usage**: Main text, sidebar backgrounds, section headers  
**Palette**: `midnight-50` to `midnight-950`

The deepest shade of professional trust — conveys authority without coldness.

#### Pathfinder Teal `#168C83`
**Role**: Progress, navigation, interactive elements, career discovery  
**Usage**: Primary buttons, links, progress indicators, active states, pathfinder nodes  
**Palette**: `pathfinder-50` to `pathfinder-950`

Distinctive accent representing guidance and forward movement. Not corporate blue — this is ORVENA.

#### Warm Ivory `#F7F5EF`
**Role**: Primary background, content surfaces  
**Usage**: Page backgrounds, card backgrounds, light mode base  
**Palette**: `ivory-50` to `ivory-950`

Creates breathing room and premium feel. Softer than stark white, warmer than gray.

### Supporting Colors

- **Success**: `#22c55e` (Green) — Skills acquired, milestones achieved
- **Warning**: `#f59e0b` (Amber) — Skills to develop, attention needed
- **Error**: `#ef4444` (Red) — Gaps, blockers, critical items
- **Info**: `#3b82f6` (Blue) — Supplementary information, tooltips

---

## Typography

### Font Families

#### Manrope (Display)
**Weight**: 400-800  
**Usage**: Headings (h1-h6), hero text, marketing copy, CTAs  
**Character**: Modern, geometric, friendly but professional

```css
font-family: 'Manrope', system-ui, sans-serif;
```

#### Inter (UI)
**Weight**: 400-700  
**Usage**: Body text, UI components, forms, data displays  
**Character**: Highly legible, neutral, excellent for interfaces

```css
font-family: 'Inter', system-ui, sans-serif;
```

#### JetBrains Mono (Code)
**Usage**: Code snippets, technical data, API responses  
**Character**: Clear, developer-friendly

### Type Scale

| Size Class | Font Size | Line Height | Weight | Usage |
|------------|-----------|-------------|--------|-------|
| `display-2xl` | 72px (4.5rem) | 1.1 | 800 | Hero headlines |
| `display-xl` | 60px (3.75rem) | 1.1 | 800 | Page titles |
| `display-lg` | 48px (3rem) | 1.15 | 700 | Section headers |
| `display-md` | 36px (2.25rem) | 1.2 | 700 | Card titles |
| `display-sm` | 30px (1.875rem) | 1.25 | 700 | Subsection headers |
| `xl` | 20px (1.25rem) | 1.75 | 400 | Large body text |
| `lg` | 18px (1.125rem) | 1.75 | 400 | Emphasized body |
| `base` | 16px (1rem) | 1.5 | 400 | Default body text |
| `sm` | 14px (0.875rem) | 1.5 | 400 | Secondary text |
| `xs` | 12px (0.75rem) | 1.5 | 400 | Labels, captions |

### Usage Examples

```tsx
// Hero headline
<h1 className="font-display text-display-xl text-midnight-950">
  Navigate Your Career with Intelligence
</h1>

// Section header
<h2 className="font-display text-display-md text-midnight-900">
  Your Career Pathfinder
</h2>

// Body text
<p className="font-sans text-base text-midnight-700">
  ORVENA analyzes your skills and maps personalized growth paths...
</p>
```

---

## Spacing System

Based on 4px base unit for consistent rhythm:

| Token | Value | Usage |
|-------|-------|-------|
| `0` | 0 | Reset |
| `1` | 4px | Tight spacing |
| `2` | 8px | Small gaps |
| `3` | 12px | Default gaps |
| `4` | 16px | Medium spacing |
| `6` | 24px | Section spacing |
| `8` | 32px | Large spacing |
| `12` | 48px | Extra large spacing |
| `16` | 64px | Section breaks |
| `24` | 96px | Hero spacing |

---

## Shadows & Elevation

### Standard Shadows

```css
sm: 0 1px 2px 0 rgb(20 37 34 / 0.05)
base: 0 1px 3px 0 rgb(20 37 34 / 0.1), 0 1px 2px -1px rgb(20 37 34 / 0.1)
md: 0 4px 6px -1px rgb(20 37 34 / 0.1), 0 2px 4px -2px rgb(20 37 34 / 0.1)
lg: 0 10px 15px -3px rgb(20 37 34 / 0.1), 0 4px 6px -4px rgb(20 37 34 / 0.1)
xl: 0 20px 25px -5px rgb(20 37 34 / 0.1), 0 8px 10px -6px rgb(20 37 34 / 0.1)
```

### Pathfinder Glow

Special effect for interactive pathfinder elements:

```css
pathfinder: 0 0 20px rgba(22, 140, 131, 0.3)
pathfinder-lg: 0 0 40px rgba(22, 140, 131, 0.4)
```

**Usage**: Hover states on pathfinder nodes, active career paths, progress indicators

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `sm` | 4px | Small buttons, tags |
| `base` | 8px | Default buttons, inputs |
| `md` | 12px | Cards, panels |
| `lg` | 16px | Large cards, modals |
| `xl` | 24px | Hero sections, featured cards |
| `2xl` | 32px | Premium elements |
| `full` | 9999px | Pills, avatar borders |

---

## Animation & Timing

### Duration

- **Fast**: 150ms — Small UI feedback (hover, focus)
- **Base**: 250ms — Standard transitions (dropdowns, tooltips)
- **Slow**: 350ms — Complex transitions (modals, drawers)
- **Slower**: 500ms — Pathfinder animations, data visualizations

### Easing

```css
default: cubic-bezier(0.4, 0, 0.2, 1) /* ease-in-out */
in: cubic-bezier(0.4, 0, 1, 1)       /* ease-in */
out: cubic-bezier(0, 0, 0.2, 1)      /* ease-out */
```

### Special Animations

#### Pathfinder Pulse
```css
@keyframes pathfinder-pulse {
  0%, 100% { opacity: 1 }
  50% { opacity: 0.5 }
}
```

**Usage**: Active career node, current position indicator

#### Pathfinder Glow
```css
@keyframes pathfinder-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(22, 140, 131, 0.3) }
  50% { box-shadow: 0 0 40px rgba(22, 140, 131, 0.6) }
}
```

**Usage**: Hover on interactive pathfinder elements

#### Path Drawing
```css
@keyframes draw-path {
  to { stroke-dashoffset: 0 }
}
```

**Usage**: Revealing career paths, showing connections

---

## Component Patterns

### Glass Card Effect

Premium translucent cards with backdrop blur:

```tsx
<div className="glass-card rounded-lg p-6">
  {/* Content */}
</div>
```

**CSS**:
```css
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(20, 37, 34, 0.1);
}
```

### Pathfinder Glow Effect

For interactive elements in career visualization:

```tsx
<button className="pathfinder-glow rounded-full">
  Explore Path
</button>
```

### Gradient Backgrounds

```tsx
{/* Pathfinder gradient */}
<div className="gradient-pathfinder">

{/* Midnight gradient */}
<div className="gradient-midnight">

{/* Text gradient for hero elements */}
<h1 className="text-gradient-pathfinder">
  ORVENA
</h1>
```

---

## Semantic Color Usage

### Backgrounds

- **Primary**: `bg-ivory-50` — Main page background
- **Secondary**: `bg-ivory-100` — Nested sections
- **Elevated**: `bg-white` — Cards, modals, dropdowns
- **Inverse**: `bg-midnight-950` — Dark sections, footer

### Text

- **Primary**: `text-midnight-950` — Main content
- **Secondary**: `text-midnight-700` — Supporting text
- **Tertiary**: `text-midnight-500` — Subtle text, placeholders
- **Inverse**: `text-ivory-50` — Text on dark backgrounds

### Interactive Elements

- **Primary**: `bg-pathfinder-500` with `hover:bg-pathfinder-600`
- **Secondary**: `bg-midnight-950` with `hover:bg-midnight-900`
- **Ghost**: Transparent with `hover:bg-ivory-100`

### Borders

- **Default**: `border-midnight-200` — Standard borders
- **Subtle**: `border-midnight-100` — Dividers, separators
- **Strong**: `border-midnight-300` — Emphasized borders
- **Accent**: `border-pathfinder-500` — Focus, active states

---

## Dark Mode

ORVENA supports dark mode with midnight ink as the base:

**Light mode**: Warm ivory base → Midnight ink text  
**Dark mode**: Midnight ink base → Warm ivory text

Pathfinder teal remains consistent as the accent across both themes.

### Implementation

```tsx
// Automatic with Tailwind's dark: modifier
<div className="bg-ivory-50 dark:bg-midnight-950">
  <p className="text-midnight-950 dark:text-ivory-50">
    Content that adapts to theme
  </p>
</div>
```

---

## Accessibility

### Color Contrast

All text/background combinations meet **WCAG AA standards** (4.5:1 for normal text, 3:1 for large text):

- Midnight-950 on Ivory-50: ✅ 14.2:1
- Pathfinder-500 on Ivory-50: ✅ 4.8:1
- Ivory-50 on Midnight-950: ✅ 14.2:1

### Focus States

All interactive elements have visible focus indicators using pathfinder teal:

```tsx
<button className="focus:ring-2 focus:ring-pathfinder-500 focus:ring-offset-2">
  Interactive Element
</button>
```

### Motion

Respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Usage in Code

### Import Design Tokens

```tsx
import { designTokens, semanticColors } from '@/lib/design-tokens'

// Access specific tokens
const primaryColor = designTokens.colors.pathfinder[500]
const displayFont = designTokens.typography.fontFamily.display
```

### Tailwind Classes

```tsx
// Colors
<div className="bg-midnight-950 text-ivory-50">
<button className="bg-pathfinder-500 hover:bg-pathfinder-600">

// Typography
<h1 className="font-display text-display-xl">
<p className="font-sans text-base">

// Spacing
<div className="p-6 space-y-4">

// Shadows
<div className="shadow-lg hover:shadow-pathfinder">

// Animations
<div className="animate-pathfinder-pulse">
```

---

## Implementation Checklist

### ✅ Phase B Complete
- [x] Design tokens defined (`lib/design-tokens.ts`)
- [x] Tailwind config updated with ORVENA palette
- [x] Global CSS with custom properties and themes
- [x] Typography system (Manrope + Inter)
- [x] Pathfinder animations and effects
- [x] Glass card component styles
- [x] Dark mode support

### Next: Phase C - Login Redesign
- [ ] Split-screen layout with branded visual
- [ ] Pathfinder welcome illustration
- [ ] Premium form styling

---

**Design System Owner**: ORVENA Frontend Team  
**Last Updated**: 2026-10-11  
**Status**: Foundation Complete, Ready for Component Implementation
