import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    // In local dev, proxy /api/* to the FastAPI backend so that relative
    // fetch('/api/try-on') and fetch('/api/design') work without setting
    // VITE_BACKEND_URL.  The Vercel deployment handles this via vercel.json rewrites.
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
