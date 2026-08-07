/**
 * app/(auth)/layout.tsx — Auth Layout
 * =====================================
 * Shared layout for /login and /register pages.
 * Centered card on a clean background.
 */

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-[#0f1117] px-4">
      <div className="w-full max-w-md">
        {/* Brand mark */}
        <div className="text-center mb-8">
          <span className="text-4xl">🎓</span>
          <h1 className="text-xl font-bold text-slate-800 dark:text-white mt-2">
            AI Study Buddy
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            IBM SkillsBuild Final Project 2025
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
