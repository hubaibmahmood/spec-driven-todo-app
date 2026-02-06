"use client";

import React from "react";

interface AnimatedBorderProps {
  children: React.ReactNode;
  className?: string;
  speed?: number;
  opacity?: number;
}

export function AnimatedBorder({
  children,
  className = "",
  speed = 4,
  opacity = 0.6,
}: AnimatedBorderProps) {
  return (
    <div className={`relative ${className}`}>
      {/* Rotating gradient that peeks through as the border */}
      <div className="absolute inset-0 rounded-2xl overflow-hidden">
        <div
          className="absolute"
          style={{
            inset: "-100%",
            background:
              "conic-gradient(from 0deg at 50% 50%, #6366f1 0%, #a855f7 25%, #ec4899 50%, transparent 70%, transparent 100%)",
            animation: `spin ${speed}s linear infinite`,
            opacity,
          }}
        />
      </div>
      {/* White fill that leaves only the 1.5px border visible */}
      <div className="absolute inset-[1.5px] rounded-[14.5px] bg-white" />
      {/* Content sits on top with matching inset */}
      <div className="relative z-10 m-[1.5px]">{children}</div>
    </div>
  );
}
