/**
 * app/(auth)/layout.tsx — Premium Auth Shell
 * ============================================
 * Cinematic frosted card, glowing background, and clean branding.
 */

import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden"
      style={{ background: "#050505" }}
    >
      {/* Glow */}
      <div
        className="absolute top-[20%] left-[50%] -translate-x-1/2 w-[600px] h-[350px] rounded-full pointer-events-none"
        style={{
          background: "radial-gradient(ellipse, rgba(255,45,85,0.12) 0%, transparent 70%)",
          filter: "blur(60px)",
        }}
      />

      {/* Brand header */}
      <Link href="/" className="flex items-center gap-3 mb-8 relative z-10">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center text-lg"
          style={{ background: "#FF2D55", boxShadow: "0 0 25px rgba(255,45,85,0.4)" }}
        >
          🧠
        </div>
        <span className="text-base font-black tracking-tight" style={{ color: "#F1F3F8" }}>
          AI Study Buddy
        </span>
      </Link>

      {/* Card shell */}
      <div className="w-full max-w-md relative z-10">
        {children}
      </div>

      {/* Footer */}
      <p className="mt-8 text-2xs relative z-10" style={{ color: "#5C6070" }}>
        Protected by JWT Auth & AES Encryption · IBM SkillsBuild 2026
      </p>
    </div>
  );
}
