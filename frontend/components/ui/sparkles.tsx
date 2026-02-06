"use client";

import React, { useEffect, useRef, useCallback } from "react";

interface Sparkle {
  x: number;
  y: number;
  size: number;
  opacity: number;
  speedX: number;
  speedY: number;
  life: number;
  maxLife: number;
}

interface SparklesProps {
  className?: string;
  children?: React.ReactNode;
  count?: number;
}

export function Sparkles({ className = "", children, count = 40 }: SparklesProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sparklesRef = useRef<Sparkle[]>([]);
  const animFrameRef = useRef<number>(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const createSparkle = useCallback((width: number, height: number): Sparkle => {
    const maxLife = 60 + Math.random() * 60;
    return {
      x: Math.random() * width,
      y: Math.random() * height,
      size: 1 + Math.random() * 2.5,
      opacity: 0,
      speedX: (Math.random() - 0.5) * 0.6,
      speedY: -0.2 - Math.random() * 0.4,
      life: Math.random() * maxLife,
      maxLife,
    };
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const resize = () => {
      canvas.width = container.offsetWidth;
      canvas.height = container.offsetHeight;
    };
    resize();

    sparklesRef.current = Array.from({ length: count }, () =>
      createSparkle(canvas.width, canvas.height)
    );

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      sparklesRef.current.forEach((s, i) => {
        s.life += 1;
        if (s.life >= s.maxLife) {
          sparklesRef.current[i] = createSparkle(canvas.width, canvas.height);
          return;
        }
        const progress = s.life / s.maxLife;
        s.opacity = progress < 0.3 ? progress / 0.3 : 1 - (progress - 0.3) / 0.7;
        s.x += s.speedX;
        s.y += s.speedY;

        ctx.save();
        ctx.globalAlpha = s.opacity * 0.7;
        ctx.fillStyle = i % 2 === 0 ? "#6366f1" : "#a855f7";
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });
      animFrameRef.current = requestAnimationFrame(animate);
    };
    animate();

    const observer = new ResizeObserver(resize);
    observer.observe(container);

    return () => {
      cancelAnimationFrame(animFrameRef.current);
      observer.disconnect();
    };
  }, [count, createSparkle]);

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
