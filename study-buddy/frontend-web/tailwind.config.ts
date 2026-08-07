import type { Config } from "tailwindcss";

const config: Config = {
  // ── Scan all component/page files for class names ──────────────────────
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
  // ── Enable class-based dark mode (controlled by next-themes) ───────────
  darkMode: "class",
  theme: {
    extend: {
      // Brand colour palette — mirrors the Streamlit design system tokens
      colors: {
        brand: {
          50:  "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          900: "#1e3a8a",
        },
        surface: {
          light: "#f8fafc",
          dark:  "#0f1117",
          card:  "#1e2130",
        },
      },
      // Custom font stack
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          '"Segoe UI"',
          "Roboto",
          "sans-serif",
        ],
        mono: ['"JetBrains Mono"', '"Fira Code"', "monospace"],
      },
      // Custom border radius tokens
      borderRadius: {
        "4xl": "2rem",
      },
      // Keyframes for animations
      keyframes: {
        "fade-in-up": {
          "0%":   { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "flip-y": {
          "0%":   { transform: "rotateY(0deg)" },
          "100%": { transform: "rotateY(180deg)" },
        },
      },
      animation: {
        "fade-in-up": "fade-in-up 0.35s ease forwards",
        "fade-in":    "fade-in 0.2s ease forwards",
        shimmer:      "shimmer 1.5s infinite linear",
        "flip-y":     "flip-y 0.4s ease forwards",
      },
    },
  },
  plugins: [],
};

export default config;
