import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

/*
 * App.jsx still contains the legacy browser-side Gemini implementation.
 * This pre-transform replaces it with a server-side /api/gemini call before
 * Vite exposes any VITE_* environment values to the client bundle.
 */
function serverSideGeminiPlugin() {
  return {
    name: 'server-side-gemini',
    enforce: 'pre',
    transform(code, id) {
      if (!id.replace(/\\/g, '/').endsWith('/src/App.jsx')) return null;

      const start = code.indexOf('/* ─── CONFIG');
      const end = code.indexOf('/**\n * Build a concise garment description', start);
      if (start === -1 || end === -1) {
        throw new Error('Unable to apply secure Gemini transform to src/App.jsx');
      }

      const secureService = `/* ─── SERVER-SIDE AI SERVICES ─────────────────────────────────── */
const FashionIntelligenceService = {
  async extractSpecification(prompt) {
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
    return { optimized_image_prompt: prompt };
  }
};

`;

      return {
        code: code.slice(0, start) + secureService + code.slice(end),
        map: null,
      };
    },
  };
}

export default defineConfig({
  plugins: [
    serverSideGeminiPlugin(),
    react(),
    tailwindcss(),
  ],
  server: {},
});
