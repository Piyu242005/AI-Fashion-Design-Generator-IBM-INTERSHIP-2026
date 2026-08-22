import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

/*
 * Keep Gemini server-side and preserve every other App.jsx declaration.
 * The previous transform replaced the whole CONFIG -> JSDoc section, which
 * accidentally removed StorageService from the compiled bundle and caused:
 *   ReferenceError: StorageService is not defined
 */
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

      if ([configStart, storageStart, cleanJsonStart, aiServicesStart, aiServicesEnd].some(v => v < 0)) {
        return null;
      }

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

      // Keep the existing StorageService and cleanJSON declarations intact.
      // Replace only the browser-side Gemini config/service.
      const transformed =
        code.slice(0, configStart) +
        secureService +
        code.slice(aiServicesEnd);

      return { code: transformed, map: null };
    },
  };
}

export default defineConfig({
  plugins: [
    serverSideGeminiPlugin(),
    react(),
    tailwindcss(),
  ],
});
