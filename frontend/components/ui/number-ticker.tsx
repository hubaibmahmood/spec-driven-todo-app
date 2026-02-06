"use client";

import { useEffect, useRef, useState } from "react";

interface NumberTickerProps {
  target: number;
  duration?: number;
  className?: string;
  decimals?: number;
  formatter?: (n: number) => string;
}

export function NumberTicker({
  target,
  duration = 1500,
  className = "",
  decimals = 0,
  formatter,
}: NumberTickerProps) {
  const [display, setDisplay] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const animatedRef = useRef(false);

  const defaultFormatter = (n: number) =>
    decimals > 0 ? n.toFixed(decimals) : n.toLocaleString();
  const format = formatter || defaultFormatter;

  useEffect(() => {
    if (animatedRef.current) setDisplay(target);
  }, [target]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !animatedRef.current) {
          animatedRef.current = true;
          const start = performance.now();
          const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
          const animate = (now: number) => {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const current = easeOut(progress) * target;
            setDisplay(
              decimals > 0
                ? parseFloat(current.toFixed(decimals))
                : Math.round(current)
            );
            if (progress < 1) requestAnimationFrame(animate);
          };
          requestAnimationFrame(animate);
        }
      },
      { threshold: 0.3 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [target, duration, decimals]);

  return (
    <span ref={ref} className={className}>
      {format(display)}
    </span>
  );
}
