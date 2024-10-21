import path from 'path'
import { defineConfig } from 'vite'

import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [{ find: '@', replacement: path.resolve(__dirname, 'src') }],
  },
  build: {
    assetsDir: 'static',
    rollupOptions: {
      output: {
        entryFileNames: `static/js/main.js`,
        chunkFileNames: `static/js/[name].js`,
        assetFileNames: ({ name }) => {
          if (name?.endsWith('.css')) {
            return `static/css/main.css`
          }
          return `static/[ext]/[name].[ext]`
        },
      },
    },
  },
})
