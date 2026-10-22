/**
 * ORVENA Design System - Core Design Tokens
 * Premium career intelligence platform with pathfinding visualization concept
 */

export const designTokens = {
  // === COLOR PALETTE ===
  colors: {
    // Primary: Midnight ink - Deep, professional foundation
    midnight: {
      50: '#f7f8f8',
      100: '#eef0f1',
      200: '#d4dade',
      300: '#adb8bf',
      400: '#7f8f9a',
      500: '#5f707d',
      600: '#4a5966',
      700: '#3d4953',
      800: '#353e47',
      900: '#2f373e',
      950: '#142522', // Core midnight ink
    },

    // Accent: Pathfinder teal - Navigation, progress, discovery
    pathfinder: {
      50: '#f0fdfc',
      100: '#ccfbf6',
      200: '#99f6ed',
      300: '#5eede3',
      400: '#2dd9ce',
      500: '#168C83', // Core pathfinder teal
      600: '#0f9d94',
      700: '#137d76',
      800: '#15635f',
      900: '#16524f',
      950: '#063630',
    },

    // Neutral: Warm ivory - Backgrounds, surfaces
    ivory: {
      50: '#F7F5EF', // Core warm ivory
      100: '#f2efe6',
      200: '#e8e3d4',
      300: '#dcd4bc',
      400: '#cdc0a0',
      500: '#c0b08b',
      600: '#b3a07e',
      700: '#958569',
      800: '#7a6d59',
      900: '#645a4a',
      950: '#342e26',
    },

    // Supporting colors
    success: {
      50: '#f0fdf4',
      500: '#22c55e',
      700: '#15803d',
    },
    warning: {
      50: '#fffbeb',
      500: '#f59e0b',
      700: '#b45309',
    },
    error: {
      50: '#fef2f2',
      500: '#ef4444',
      700: '#b91c1c',
    },
    info: {
      50: '#eff6ff',
      500: '#3b82f6',
      700: '#1d4ed8',
    },
  },

  // === TYPOGRAPHY ===
  typography: {
    fontFamily: {
      // Display: Manrope - Modern, geometric, friendly (headings, hero text)
      display: ['Manrope', 'system-ui', 'sans-serif'],
      
      // UI: Inter - Clean, highly legible (body, UI elements)
      sans: ['Inter', 'system-ui', 'sans-serif'],
      
      // Monospace: For code, data
      mono: ['JetBrains Mono', 'Consolas', 'Monaco', 'monospace'],
    },

    fontSize: {
      // Display sizes (Manrope)
      'display-2xl': ['4.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '800' }], // 72px
      'display-xl': ['3.75rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '800' }], // 60px
      'display-lg': ['3rem', { lineHeight: '1.15', letterSpacing: '-0.01em', fontWeight: '700' }], // 48px
      'display-md': ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em', fontWeight: '700' }], // 36px
      'display-sm': ['1.875rem', { lineHeight: '1.25', letterSpacing: '-0.005em', fontWeight: '700' }], // 30px

      // Body sizes (Inter)
      'xl': ['1.25rem', { lineHeight: '1.75', fontWeight: '400' }], // 20px
      'lg': ['1.125rem', { lineHeight: '1.75', fontWeight: '400' }], // 18px
      'base': ['1rem', { lineHeight: '1.5', fontWeight: '400' }], // 16px
      'sm': ['0.875rem', { lineHeight: '1.5', fontWeight: '400' }], // 14px
      'xs': ['0.75rem', { lineHeight: '1.5', fontWeight: '400' }], // 12px
    },

    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
    },
  },

  // === SPACING ===
  spacing: {
    0: '0',
    1: '0.25rem', // 4px
    2: '0.5rem',  // 8px
    3: '0.75rem', // 12px
    4: '1rem',    // 16px
    5: '1.25rem', // 20px
    6: '1.5rem',  // 24px
    8: '2rem',    // 32px
    10: '2.5rem', // 40px
    12: '3rem',   // 48px
    16: '4rem',   // 64px
    20: '5rem',   // 80px
    24: '6rem',   // 96px
    32: '8rem',   // 128px
  },

  // === SHADOWS ===
  shadows: {
    sm: '0 1px 2px 0 rgb(20 37 34 / 0.05)',
    base: '0 1px 3px 0 rgb(20 37 34 / 0.1), 0 1px 2px -1px rgb(20 37 34 / 0.1)',
    md: '0 4px 6px -1px rgb(20 37 34 / 0.1), 0 2px 4px -2px rgb(20 37 34 / 0.1)',
    lg: '0 10px 15px -3px rgb(20 37 34 / 0.1), 0 4px 6px -4px rgb(20 37 34 / 0.1)',
    xl: '0 20px 25px -5px rgb(20 37 34 / 0.1), 0 8px 10px -6px rgb(20 37 34 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(20 37 34 / 0.25)',
    inner: 'inset 0 2px 4px 0 rgb(20 37 34 / 0.05)',
    
    // Pathfinder glow for interactive elements
    pathfinder: '0 0 20px rgba(22, 140, 131, 0.3)',
    'pathfinder-lg': '0 0 40px rgba(22, 140, 131, 0.4)',
  },

  // === BORDER RADIUS ===
  borderRadius: {
    none: '0',
    sm: '0.25rem',  // 4px
    base: '0.5rem', // 8px
    md: '0.75rem',  // 12px
    lg: '1rem',     // 16px
    xl: '1.5rem',   // 24px
    '2xl': '2rem',  // 32px
    full: '9999px',
  },

  // === ANIMATION ===
  animation: {
    timing: {
      fast: '150ms',
      base: '250ms',
      slow: '350ms',
      slower: '500ms',
    },
    easing: {
      default: 'cubic-bezier(0.4, 0, 0.2, 1)',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },

  // === BREAKPOINTS ===
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
} as const;

// === SEMANTIC COLOR MAPPINGS ===
export const semanticColors = {
  // Backgrounds
  bg: {
    primary: designTokens.colors.ivory[50],
    secondary: designTokens.colors.ivory[100],
    tertiary: designTokens.colors.ivory[200],
    inverse: designTokens.colors.midnight[950],
    elevated: '#FFFFFF',
  },

  // Text
  text: {
    primary: designTokens.colors.midnight[950],
    secondary: designTokens.colors.midnight[700],
    tertiary: designTokens.colors.midnight[500],
    inverse: designTokens.colors.ivory[50],
    disabled: designTokens.colors.midnight[400],
  },

  // Borders
  border: {
    default: designTokens.colors.midnight[200],
    subtle: designTokens.colors.midnight[100],
    strong: designTokens.colors.midnight[300],
    accent: designTokens.colors.pathfinder[500],
  },

  // Interactive states
  interactive: {
    primary: designTokens.colors.pathfinder[500],
    primaryHover: designTokens.colors.pathfinder[600],
    primaryActive: designTokens.colors.pathfinder[700],
    secondary: designTokens.colors.midnight[950],
    secondaryHover: designTokens.colors.midnight[900],
    secondaryActive: designTokens.colors.midnight[800],
  },

  // Status
  status: {
    success: designTokens.colors.success[500],
    warning: designTokens.colors.warning[500],
    error: designTokens.colors.error[500],
    info: designTokens.colors.info[500],
  },
} as const;

// Type exports
export type ColorToken = typeof designTokens.colors;
export type SpacingToken = typeof designTokens.spacing;
export type TypographyToken = typeof designTokens.typography;
