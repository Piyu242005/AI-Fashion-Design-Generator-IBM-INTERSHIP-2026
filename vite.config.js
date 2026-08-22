import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

/*
 * Keep Gemini server-side. App.jsx contains an older Gemini implementation;
 * this transform replaces only that service during the build. It is deliberately
 * fail-safe so a formatting change in App.jsx can never make the whole app blank.
 */
function serverSideGeminiPlugin() {
  return {
    name: 'server-side-gemini',
    enforce: 'pre',
    transform(code, id) {
      const normalizedId = id.split('?')[0].replace(/\\/g, '/');
      if (!normalizedId.endsWith('/src/App.jsx')) return null;

      const start = code.indexOf('/* ─── CONFIG');
      const end = code.indexOf('/**', start + 1);
      if (start < 0 || end < 0 || end <= start) return null;

      const secureService = `/* ─── SERVER-SIDE AI SERVICES ─────────────────────────────────── */
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
});
