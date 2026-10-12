/**
 * ColorPalette Component
 * Visual reference for ORVENA design system colors
 * Use this for design system documentation and testing
 */

import React from 'react';

interface ColorSwatchProps {
  name: string;
  value: string;
  textColor?: string;
}

const ColorSwatch: React.FC<ColorSwatchProps> = ({ name, value, textColor = 'text-midnight-950' }) => (
  <div className="flex flex-col">
    <div 
      className="h-20 rounded-md border border-midnight-200 flex items-end p-3"
      style={{ backgroundColor: value }}
    >
      <span className={`text-xs font-medium ${textColor}`}>{name}</span>
    </div>
    <span className="text-xs text-midnight-600 mt-1 font-mono">{value}</span>
  </div>
);

interface ColorScaleProps {
  name: string;
  colors: Record<number, string>;
  description: string;
}

const ColorScale: React.FC<ColorScaleProps> = ({ name, colors, description }) => (
  <div className="space-y-3">
    <div>
      <h3 className="font-display text-display-sm text-midnight-950">{name}</h3>
      <p className="text-sm text-midnight-600">{description}</p>
    </div>
    <div className="grid grid-cols-5 gap-3">
      {Object.entries(colors).map(([shade, hex]) => (
        <ColorSwatch 
          key={shade}
          name={shade}
          value={hex}
          textColor={parseInt(shade) >= 600 ? 'text-ivory-50' : 'text-midnight-950'}
        />
      ))}
    </div>
  </div>
);

export const ColorPalette: React.FC = () => {
  const midnightColors = {
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
    950: '#142522',
  };

  const pathfinderColors = {
    50: '#f0fdfc',
    100: '#ccfbf6',
    200: '#99f6ed',
    300: '#5eede3',
    400: '#2dd9ce',
    500: '#168C83',
    600: '#0f9d94',
    700: '#137d76',
    800: '#15635f',
    900: '#16524f',
    950: '#063630',
  };

  const ivoryColors = {
    50: '#F7F5EF',
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
  };

  return (
    <div className="min-h-screen bg-ivory-50 p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="font-display text-display-xl text-midnight-950">
            ORVENA Design System
          </h1>
          <p className="text-lg text-midnight-700">
            Premium career intelligence platform — Color palette and visual identity
          </p>
        </div>

        {/* Core Colors */}
        <section className="space-y-8">
          <h2 className="font-display text-display-md text-midnight-950 border-b border-midnight-200 pb-2">
            Core Color Palette
          </h2>

          <ColorScale
            name="Midnight Ink"
            colors={midnightColors}
            description="Professional foundation — Primary text, navigation, section headers"
          />

          <ColorScale
            name="Pathfinder Teal"
            colors={pathfinderColors}
            description="Accent color — Progress, navigation, interactive elements, career discovery"
          />

          <ColorScale
            name="Warm Ivory"
            colors={ivoryColors}
            description="Background & surfaces — Page backgrounds, content areas, premium feel"
          />
        </section>

        {/* Semantic Usage */}
        <section className="space-y-6">
          <h2 className="font-display text-display-md text-midnight-950 border-b border-midnight-200 pb-2">
            Semantic Usage Examples
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Primary Button */}
            <div className="space-y-3">
              <h4 className="font-semibold text-midnight-900">Primary Button</h4>
              <button className="bg-pathfinder-500 hover:bg-pathfinder-600 text-ivory-50 px-6 py-3 rounded-md font-medium transition-colors">
                Start Your Journey
              </button>
              <code className="text-xs text-midnight-600 block">
                bg-pathfinder-500 hover:bg-pathfinder-600
              </code>
            </div>

            {/* Secondary Button */}
            <div className="space-y-3">
              <h4 className="font-semibold text-midnight-900">Secondary Button</h4>
              <button className="bg-midnight-950 hover:bg-midnight-900 text-ivory-50 px-6 py-3 rounded-md font-medium transition-colors">
                Learn More
              </button>
              <code className="text-xs text-midnight-600 block">
                bg-midnight-950 hover:bg-midnight-900
              </code>
            </div>

            {/* Card */}
            <div className="space-y-3">
              <h4 className="font-semibold text-midnight-900">Glass Card</h4>
              <div className="glass-card rounded-lg p-6">
                <p className="text-midnight-700">
                  Premium translucent card with backdrop blur
                </p>
              </div>
              <code className="text-xs text-midnight-600 block">
                .glass-card
              </code>
            </div>

            {/* Pathfinder Glow */}
            <div className="space-y-3">
              <h4 className="font-semibold text-midnight-900">Pathfinder Glow</h4>
              <div className="pathfinder-glow bg-pathfinder-500 text-ivory-50 rounded-full w-16 h-16 flex items-center justify-center font-bold">
                1
              </div>
              <code className="text-xs text-midnight-600 block">
                .pathfinder-glow
              </code>
            </div>
          </div>
        </section>

        {/* Typography Preview */}
        <section className="space-y-6">
          <h2 className="font-display text-display-md text-midnight-950 border-b border-midnight-200 pb-2">
            Typography Scale
          </h2>

          <div className="space-y-4">
            <div>
              <p className="text-xs text-midnight-600 mb-1">Display 2XL (Manrope 800)</p>
              <h1 className="font-display text-display-2xl text-midnight-950">Navigate Your Career</h1>
            </div>
            <div>
              <p className="text-xs text-midnight-600 mb-1">Display XL (Manrope 800)</p>
              <h1 className="font-display text-display-xl text-midnight-950">Career Intelligence</h1>
            </div>
            <div>
              <p className="text-xs text-midnight-600 mb-1">Display LG (Manrope 700)</p>
              <h2 className="font-display text-display-lg text-midnight-950">Pathfinder Dashboard</h2>
            </div>
            <div>
              <p className="text-xs text-midnight-600 mb-1">Display MD (Manrope 700)</p>
              <h3 className="font-display text-display-md text-midnight-950">Your Career Journey</h3>
            </div>
            <div>
              <p className="text-xs text-midnight-600 mb-1">Body XL (Inter 400)</p>
              <p className="font-sans text-xl text-midnight-700">
                ORVENA provides AI-powered career intelligence to help you navigate your professional journey.
              </p>
            </div>
            <div>
              <p className="text-xs text-midnight-600 mb-1">Body Base (Inter 400)</p>
              <p className="font-sans text-base text-midnight-700">
                Analyze your skills, discover opportunities, and chart your path with data-driven insights.
              </p>
            </div>
          </div>
        </section>

        {/* Gradients */}
        <section className="space-y-6">
          <h2 className="font-display text-display-md text-midnight-950 border-b border-midnight-200 pb-2">
            Premium Gradients
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="gradient-pathfinder rounded-lg p-8 text-center">
              <h3 className="font-display text-display-md text-ivory-50">Pathfinder Gradient</h3>
              <p className="text-ivory-100 mt-2">Perfect for hero sections and CTAs</p>
            </div>
            <div className="gradient-midnight rounded-lg p-8 text-center">
              <h3 className="font-display text-display-md text-ivory-50">Midnight Gradient</h3>
              <p className="text-ivory-100 mt-2">Professional, premium feel</p>
            </div>
          </div>

          <div className="bg-midnight-950 rounded-lg p-8 text-center">
            <h3 className="font-display text-display-lg text-gradient-pathfinder">
              Text Gradient Effect
            </h3>
            <p className="text-ivory-100 mt-2">Eye-catching for hero headlines</p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default ColorPalette;
