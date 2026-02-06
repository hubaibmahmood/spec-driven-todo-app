import React from "react";

interface ShimmerTextProps {
  children: React.ReactNode;
  className?: string;
  duration?: number;
}

export function ShimmerText({ children, className = "", duration = 3 }: ShimmerTextProps) {
  return (
    <span
      className={`text-transparent bg-clip-text ${className}`}
      style={{
        backgroundImage:
          "linear-gradient(90deg, #6366f1 0%, #a855f7 25%, #ec4899 50%, #6366f1 75%, #a855f7 100%)",
        backgroundSize: "200% auto",
        animation: `shimmer-text ${duration}s linear infinite`,
      }}
    >
      {children}
    </span>
  );
}
