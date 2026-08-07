import type { NextConfig } from "next";

/**
 * next.config.ts — AI-Powered Study Buddy (Next.js 14)
 *
 * Key decisions:
 *  - API routes proxied to FastAPI backend (avoids CORS in dev)
 *  - Strict mode enabled for React best practices
 *  - Image optimisation configured for common domains
 */
const nextConfig: NextConfig = {
  // ── React strict mode — surface double-render issues in dev ─────────────
  reactStrictMode: true,

  // ── Proxy /api/* → FastAPI backend ──────────────────────────────────────
  // In production, set NEXT_PUBLIC_API_URL to your Render URL.
  async rewrites() {
    return [
      {
        source:      "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/:path*`,
      },
    ];
  },

  // ── Image domains allowed for next/image ────────────────────────────────
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "avatars.githubusercontent.com",
      },
    ],
  },

  // ── Experimental features ───────────────────────────────────────────────
  experimental: {
    // Typed route handlers (Next.js 14)
    typedRoutes: true,
  },
};

export default nextConfig;
