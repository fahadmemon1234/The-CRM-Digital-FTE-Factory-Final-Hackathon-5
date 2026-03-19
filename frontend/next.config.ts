import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Ignore hydration warnings - these are typically caused by:
  // 1. Browser extensions (Grammarly, ColorZilla, etc.)
  // 2. Client-side only data (Date.now, random values)
  // 3. Dynamic content from APIs
  // The app works correctly, this is just a development warning
  reactStrictMode: true,
};

export default nextConfig;
