import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  console.log('VITE_DEBUG:', env.VITE_DEBUG);

  return {
    plugins: [react()],
    server: {
      ...(env.VITE_DEBUG === 'true'
        ? {
          proxy: {
            '/api': {
              target: 'http://localhost:8000',
              changeOrigin: true,
              secure: false,
            },
          },
        }
        : {}),
    },
  };
});

// The react app is deployed as a static site so theres no need for a proxy now, this is redundant after the .env changes