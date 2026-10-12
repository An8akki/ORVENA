/**
 * PathfinderVisual Component
 * Animated SVG visualization representing career pathfinding
 * Used on login/auth pages to reinforce ORVENA's brand identity
 */

'use client'

import React, { useEffect, useRef, useState } from 'react'

interface PathfinderVisualProps {
  className?: string
  animated?: boolean
}

export const PathfinderVisual: React.FC<PathfinderVisualProps> = ({ 
  className = '', 
  animated = true 
}) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    if (animated) {
      setIsVisible(true)
    }
  }, [animated])

  return (
    <div className={`relative ${className}`}>
      <svg
        viewBox="0 0 600 600"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full"
      >
        {/* Background grid pattern */}
        <defs>
          <pattern
            id="grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="currentColor"
              strokeWidth="0.5"
              className="text-ivory-200 dark:text-midnight-800"
              opacity="0.3"
            />
          </pattern>

          {/* Pathfinder glow filter */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>

          {/* Gradient for paths */}
          <linearGradient id="pathGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#168C83" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#2dd9ce" stopOpacity="0.4" />
          </linearGradient>
        </defs>

        {/* Grid background */}
        <rect width="600" height="600" fill="url(#grid)" />

        {/* Career path network - main paths */}
        <g className="pathfinder-paths">
          {/* Path 1: Entry to Mid-level */}
          <path
            d="M 100 500 Q 200 400, 300 300"
            stroke="url(#pathGradient)"
            strokeWidth="3"
            fill="none"
            strokeLinecap="round"
            className={animated ? 'pathfinder-path' : ''}
            style={{ 
              animationDelay: '0s',
              strokeDasharray: animated ? 1000 : 'none',
              strokeDashoffset: animated ? 1000 : 0,
            }}
          />

          {/* Path 2: Mid to Senior */}
          <path
            d="M 300 300 Q 400 200, 500 150"
            stroke="url(#pathGradient)"
            strokeWidth="3"
            fill="none"
            strokeLinecap="round"
            className={animated ? 'pathfinder-path' : ''}
            style={{ 
              animationDelay: '0.3s',
              strokeDasharray: animated ? 1000 : 'none',
              strokeDashoffset: animated ? 1000 : 0,
            }}
          />

          {/* Path 3: Alternative route */}
          <path
            d="M 100 500 Q 150 350, 300 300"
            stroke="url(#pathGradient)"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
            opacity="0.5"
            className={animated ? 'pathfinder-path' : ''}
            style={{ 
              animationDelay: '0.5s',
              strokeDasharray: animated ? 1000 : 'none',
              strokeDashoffset: animated ? 1000 : 0,
            }}
          />

          {/* Path 4: Skill branch */}
          <path
            d="M 300 300 Q 350 250, 400 300"
            stroke="url(#pathGradient)"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
            opacity="0.5"
            className={animated ? 'pathfinder-path' : ''}
            style={{ 
              animationDelay: '0.7s',
              strokeDasharray: animated ? 1000 : 'none',
              strokeDashoffset: animated ? 1000 : 0,
            }}
          />

          {/* Path 5: Upper connections */}
          <path
            d="M 400 300 Q 450 225, 500 150"
            stroke="url(#pathGradient)"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
            opacity="0.5"
            className={animated ? 'pathfinder-path' : ''}
            style={{ 
              animationDelay: '0.9s',
              strokeDasharray: animated ? 1000 : 'none',
              strokeDashoffset: animated ? 1000 : 0,
            }}
          />
        </g>

        {/* Career nodes */}
        <g className="pathfinder-nodes">
          {/* Entry level - Current position (pulsing) */}
          <g className={animated ? 'pathfinder-node active' : 'pathfinder-node'}>
            <circle
              cx="100"
              cy="500"
              r="16"
              fill="#168C83"
              filter="url(#glow)"
              className={animated ? 'animate-pathfinder-pulse' : ''}
            />
            <circle
              cx="100"
              cy="500"
              r="12"
              fill="#F7F5EF"
              opacity="0.9"
            />
            <circle
              cx="100"
              cy="500"
              r="6"
              fill="#168C83"
            />
          </g>

          {/* Mid-level milestone */}
          <g className="pathfinder-node completed">
            <circle
              cx="300"
              cy="300"
              r="14"
              fill="#168C83"
              opacity="0.8"
            />
            <circle
              cx="300"
              cy="300"
              r="10"
              fill="#F7F5EF"
              opacity="0.9"
            />
            {/* Checkmark */}
            <path
              d="M 295 300 L 298 303 L 305 296"
              stroke="#168C83"
              strokeWidth="2"
              strokeLinecap="round"
              fill="none"
            />
          </g>

          {/* Skill branch node */}
          <g className="pathfinder-node locked">
            <circle
              cx="400"
              cy="300"
              r="12"
              fill="#adb8bf"
              opacity="0.6"
            />
            <circle
              cx="400"
              cy="300"
              r="8"
              fill="#F7F5EF"
              opacity="0.7"
            />
            <text
              x="400"
              y="305"
              fontSize="10"
              textAnchor="middle"
              fill="#5f707d"
              fontWeight="600"
            >
              ?
            </text>
          </g>

          {/* Senior/Goal position */}
          <g className="pathfinder-node locked">
            <circle
              cx="500"
              cy="150"
              r="16"
              fill="#adb8bf"
              opacity="0.5"
            />
            <circle
              cx="500"
              cy="150"
              r="12"
              fill="#F7F5EF"
              opacity="0.8"
            />
            <text
              x="500"
              y="156"
              fontSize="12"
              textAnchor="middle"
              fill="#5f707d"
              fontWeight="700"
            >
              ★
            </text>
          </g>

          {/* Additional exploration nodes */}
          <circle
            cx="200"
            cy="400"
            r="6"
            fill="#168C83"
            opacity="0.4"
          />
          <circle
            cx="350"
            cy="250"
            r="6"
            fill="#168C83"
            opacity="0.3"
          />
          <circle
            cx="450"
            cy="225"
            r="6"
            fill="#adb8bf"
            opacity="0.3"
          />
        </g>

        {/* Floating particles for depth */}
        {animated && (
          <g className="particles">
            <circle
              cx="150"
              cy="450"
              r="2"
              fill="#168C83"
              opacity="0.3"
              className="animate-pathfinder-pulse"
              style={{ animationDelay: '1s' }}
            />
            <circle
              cx="250"
              cy="350"
              r="2"
              fill="#168C83"
              opacity="0.3"
              className="animate-pathfinder-pulse"
              style={{ animationDelay: '1.5s' }}
            />
            <circle
              cx="380"
              cy="270"
              r="2"
              fill="#168C83"
              opacity="0.3"
              className="animate-pathfinder-pulse"
              style={{ animationDelay: '2s' }}
            />
          </g>
        )}
      </svg>

      {/* Overlay text labels */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="relative w-full h-full">
          {/* Current position label */}
          <div 
            className="absolute"
            style={{ left: '8%', top: '86%' }}
          >
            <div className="text-xs font-medium text-pathfinder-600 dark:text-pathfinder-400">
              You are here
            </div>
          </div>

          {/* Goal label */}
          <div 
            className="absolute"
            style={{ left: '76%', top: '20%' }}
          >
            <div className="text-xs font-medium text-midnight-500 dark:text-midnight-400">
              Your goals
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PathfinderVisual
