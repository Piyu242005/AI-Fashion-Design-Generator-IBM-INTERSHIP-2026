import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

/* Keep Gemini server-side without deleting unrelated App.jsx declarations. */
function serverSideGeminiPlugin() {
  return {
    name: 'server-side-gemini',
    enforce: 'pre',
    transform(code, id) {
      const normalizedId = id.split('?')[0].replace(/\\/g, '/');
      if (!normalizedId.endsWith('/src/App.jsx')) return null;

      const configStart = code.indexOf('/* ─── CONFIG');
      const storageStart = code.indexOf('/* ─── STORAGE', configStart + 1);
      const cleanJsonStart = code.indexOf('const cleanJSON', storageStart + 1);
      const aiServicesStart = code.indexOf('/* ─── AI SERVICES', cleanJsonStart + 1);
      const aiServicesEnd = code.indexOf('/**', aiServicesStart + 1);

      if ([configStart, storageStart, cleanJsonStart, aiServicesStart, aiServicesEnd].some(v => v < 0)) return null;

      const secureService = `/* ─── SECURE AI SERVICES ─────────────────────────────────────── */
const GEMINI_MODEL = import.meta.env.VITE_GEMINI_MODEL || 'gemini-2.5-flash';

const FashionIntelligenceService = {
  async extractSpecification(prompt) {
    const fallback = { optimized_image_prompt: String(prompt || '') };
    try {
      const res = await fetch('/api/gemini', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: String(prompt || '').trim() }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.success && data.specification) return data.specification;
      console.warn('[Gemini] API error:', data?.error?.code || res.status);
    } catch (error) {
      console.warn('[Gemini] /api/gemini unreachable:', error?.message || error);
    }
    return fallback;
  }
};

`;

      // Preserve StorageService and cleanJSON exactly as authored in App.jsx.
      // Remove only the old CONFIG and browser-side Gemini service.
      const transformed =
        code.slice(0, configStart) +
        secureService +
        code.slice(storageStart, aiServicesStart) +
        code.slice(aiServicesEnd);

      return { code: transformed, map: null };
    },
  };
}

export default defineConfig({
  plugins: [serverSideGeminiPlugin(), react(), tailwindcss()],
});
