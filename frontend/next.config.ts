import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for optimized Docker images
  output: "standalone",
  // Removed rewrites as they were not taking effect.
};

export default nextConfig;