import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
    dedupe: ['react', 'react-dom', 'react-router-dom'],
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-dom/client',
      'react-router-dom',
      'recharts',
      'use-sync-external-store/shim/with-selector',
      'use-sync-external-store/shim',
      // CORREÇÃO: Inclui o Leaflet para ser otimizado corretamente
      'leaflet',
      'react-leaflet',
    ],
    noDiscovery: true,
    exclude: ['jsbarcode'],
    // REMOVIDO: O exclude do Leaflet (não é mais necessário)
  },
  server: {
    host: true,
    port: 3000,
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'https://frotabrv-api.onrender.com',
        changeOrigin: true,
        secure: true,
      },
    },
  },
});
