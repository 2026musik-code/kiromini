import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig} from 'vite';

const mockCounterPlugin = () => ({
  name: 'mock-counter-api',
  configureServer(server: any) {
    let mockCount = 1234;
    server.middlewares.use((req: any, res: any, next: any) => {
      if (req.url === '/api/counter') {
        if (req.method === 'POST') {
          mockCount++;
        }
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ count: mockCount }));
        return;
      }
      next();
    });
  }
});

export default defineConfig(() => {
  return {
    plugins: [react(), tailwindcss(), mockCounterPlugin()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modifyâfile watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
      // Disable file watching when DISABLE_HMR is true to save CPU during agent edits.
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
    },
  };
});
