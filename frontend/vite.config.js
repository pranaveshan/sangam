import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Relative paths so the built website works on Netlify/GitHub Pages/subfolders
  // (avoids blank page from missing /assets when not hosted at domain root)
  base: './',
  server: {
    port: 5180,
    strictPort: true,
    proxy: {
      '/api': 'http://localhost:8100',
      '/uploads': 'http://localhost:8100',
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    assetsDir: 'assets',
  },
});
