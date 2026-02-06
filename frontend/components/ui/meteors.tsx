"use client";

import React, { useState, useEffect } from "react";

interface MeteorData {
  id: number;
  delay: number;
  duration: number;
  left: number;
  top: number;
  height: number;
}

interface MeteorsProps {
  count?: number;
  className?: string;
}

export function Meteors({ count = 20, className = "" }: MeteorsProps) {
  const [meteors, setMeteors] = useState<MeteorData[]>([]);

  useEffect(() => {
    setMeteors(
      Array.from({ length: count }, (_, i) => ({
        id: i,
        delay: Math.random() * 5,
        duration: 1 + Math.random() * 2,
        left: Math.random() * 100,
        top: -10 + Math.random() * 20,
        height: 60 + Math.random() * 80,
      }))
    );
  }, [count]);

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`} aria-hidden="true">
      {meteors.map(({ id, delay, duration, left, top, height }) => (
        <div
          key={id}
          className="absolute"
          style={{
            left: `${left}%`,
            top: `${top}%`,
            width: "2px",
            height: `${height}px`,
            background: "linear-gradient(to bottom, rgba(255,255,255,0.9), rgba(255,255,255,0.3), transparent)",
            transform: "rotate(35deg)",
            animation: `meteor ${duration}s linear ${delay}s infinite`,
            opacity: 0,
          }}
        />
      ))}
    </div>
  );
}
