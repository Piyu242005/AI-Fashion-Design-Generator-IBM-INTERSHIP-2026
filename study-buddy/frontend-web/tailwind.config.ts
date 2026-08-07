import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      // ── Brand Color Tokens ──────────────────────────────────────────────
      colors: {
        /* Deep brand palette */
        brand: {
          DEFAULT: "#FF2D55",
          hover:   "#FF1744",
          dim:     "rgba(255,45,85,0.12)",
          glow:    "rgba(255,45,85,0.35)",
          50:  "rgba(255,45,85,0.05)",
          100: "rgba(255,45,85,0.10)",
          200: "rgba(255,45,85,0.20)",
          300: "rgba(255,45,85,0.30)",
          400: "#FF6B8A",
          500: "#FF2D55",
          600: "#FF1744",
          700: "#E00040",
          800: "#B20035",
          900: "#800025",
        },
        /* Surface layers */
        surface: {
          base:     "#050505",
          DEFAULT:  "#0F1115",
          elevated: "#161820",
          overlay:  "#1C1E28",
          hover:    "#22242F",
        },
        /* Status */
        success: { DEFAULT: "#10B981", dim: "rgba(16,185,129,0.12)" },
        warning: { DEFAULT: "#F59E0B", dim: "rgba(245,158,11,0.12)"  },
        danger:  { DEFAULT: "#EF4444", dim: "rgba(239,68,68,0.12)"   },
      },

      // ── Typography ───────────────────────────────────────────────────────
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", '"Segoe UI"', "sans-serif"],
        mono: ['"JetBrains Mono"', '"Fira Code"', "monospace"],
      },
      fontSize: {
        "2xs": ["0.65rem",  { lineHeight: "1rem" }],
        xs:    ["0.75rem",  { lineHeight: "1.125rem" }],
        sm:    ["0.8125rem",{ lineHeight: "1.375rem" }],
        base:  ["0.9375rem",{ lineHeight: "1.625rem" }],
        lg:    ["1.0625rem",{ lineHeight: "1.75rem" }],
        xl:    ["1.1875rem",{ lineHeight: "1.875rem" }],
        "2xl": ["1.375rem", { lineHeight: "1.875rem" }],
        "3xl": ["1.625rem", { lineHeight: "2.125rem" }],
        "4xl": ["2rem",     { lineHeight: "2.5rem" }],
        "5xl": ["2.5rem",   { lineHeight: "3rem" }],
        "6xl": ["3.25rem",  { lineHeight: "3.75rem" }],
        "7xl": ["4rem",     { lineHeight: "4.5rem" }],
        "8xl": ["5rem",     { lineHeight: "5.5rem" }],
      },
      letterSpacing: {
        tightest: "-0.04em",
        tighter:  "-0.03em",
        tight:    "-0.02em",
        normal:   "0",
        wide:     "0.02em",
        wider:    "0.05em",
        widest:   "0.1em",
      },

      // ── Spacing ───────────────────────────────────────────────────────────
      spacing: {
        "4.5": "1.125rem",
        "5.5": "1.375rem",
        "13":  "3.25rem",
        "15":  "3.75rem",
        "18":  "4.5rem",
        "22":  "5.5rem",
        "26":  "6.5rem",
        "30":  "7.5rem",
        "60":  "15rem",
        "72":  "18rem",
        "80":  "20rem",
        "96":  "24rem",
      },

      // ── Border Radius ────────────────────────────────────────────────────
      borderRadius: {
        "xl":  "12px",
        "2xl": "16px",
        "3xl": "20px",
        "4xl": "24px",
        "5xl": "32px",
      },

      // ── Box Shadow ───────────────────────────────────────────────────────
      boxShadow: {
        "xs":      "0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.3)",
        "sm":      "0 2px 8px rgba(0,0,0,0.5), 0 1px 3px rgba(0,0,0,0.3)",
        "md":      "0 4px 24px rgba(0,0,0,0.6), 0 2px 8px rgba(0,0,0,0.4)",
        "lg":      "0 20px 60px rgba(0,0,0,0.7), 0 8px 24px rgba(0,0,0,0.5)",
        "brand":   "0 0 30px rgba(255,45,85,0.25), 0 4px 14px rgba(255,45,85,0.4)",
        "brand-lg":"0 0 60px rgba(255,45,85,0.15), 0 8px 24px rgba(255,45,85,0.2)",
        "glow":    "0 0 80px rgba(255,45,85,0.15)",
        "inner-brand": "inset 0 1px 0 rgba(255,45,85,0.15)",
      },

      // ── Keyframes ────────────────────────────────────────────────────────
      keyframes: {
        "fade-in-up": {
          "0%":   { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in-down": {
          "0%":   { opacity: "0", transform: "translateY(-16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "scale-in": {
          "0%":   { opacity: "0", transform: "scale(0.94)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "slide-in-left": {
          "0%":   { opacity: "0", transform: "translateX(-20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        "slide-in-right": {
          "0%":   { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 20px rgba(255,45,85,0.2)" },
          "50%":       { boxShadow: "0 0 40px rgba(255,45,85,0.5)" },
        },
        "bounce-subtle": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%":       { transform: "translateY(-4px)" },
        },
        "rotate-slow": {
          from: { transform: "rotate(0deg)" },
          to:   { transform: "rotate(360deg)" },
        },
        "thinking-dot": {
          "0%, 80%, 100%": { transform: "scale(0.6)", opacity: "0.4" },
          "40%":            { transform: "scale(1)",   opacity: "1" },
        },
        "flip-y": {
          "0%":   { transform: "rotateY(0deg)" },
          "100%": { transform: "rotateY(180deg)" },
        },
        "streak-flame": {
          "0%, 100%": { transform: "scaleY(1) rotate(-3deg)" },
          "50%":       { transform: "scaleY(1.15) rotate(3deg)" },
        },
        "gradient-shift": {
          "0%":   { backgroundPosition: "0% 50%" },
          "50%":  { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
      },

      // ── Animations ───────────────────────────────────────────────────────
      animation: {
        "fade-in-up":    "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) forwards",
        "fade-in-down":  "fade-in-down 0.4s cubic-bezier(0.16,1,0.3,1) forwards",
        "fade-in":       "fade-in 0.25s ease forwards",
        "scale-in":      "scale-in 0.35s cubic-bezier(0.16,1,0.3,1) forwards",
        "slide-in-left": "slide-in-left 0.4s cubic-bezier(0.16,1,0.3,1) forwards",
        "slide-in-right":"slide-in-right 0.4s cubic-bezier(0.16,1,0.3,1) forwards",
        shimmer:         "shimmer 1.6s infinite linear",
        "pulse-glow":    "pulse-glow 2.5s ease-in-out infinite",
        "bounce-subtle": "bounce-subtle 2s ease-in-out infinite",
        "rotate-slow":   "rotate-slow 8s linear infinite",
        "thinking-dot":  "thinking-dot 1.2s ease-in-out infinite",
        "flip-y":        "flip-y 0.55s cubic-bezier(0.4,0,0.2,1) forwards",
        "streak-flame":  "streak-flame 0.8s ease-in-out infinite",
        "gradient-shift":"gradient-shift 4s ease infinite",
      },

      // ── Background size for shimmer ──────────────────────────────────────
      backgroundSize: {
        "200%": "200% 100%",
      },
    },
  },
  plugins: [],
};

export default config;
