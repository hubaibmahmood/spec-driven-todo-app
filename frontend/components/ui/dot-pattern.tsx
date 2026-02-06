"use client";

import React from "react";

interface DotPatternProps {
  color?: string;
  opacity?: number;
  className?: string;
}

export function DotPattern({ color = "#6366f1", opacity = 0.15, className = "" }: DotPatternProps) {
  const id = React.useId().replace(/:/g, "");
  const patternId = `dot-pattern-${id}`;

  return (
    <div
      className={`absolute inset-0 pointer-events-none ${className}`}
      aria-hidden="true"
    >
      <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id={patternId} x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
            <circle cx="4" cy="4" r="1.5" fill={color} opacity={opacity} />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill={`url(#${patternId})`} />
      </svg>
    </div>
  );
}
