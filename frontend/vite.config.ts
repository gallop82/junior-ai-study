import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    base: env.VITE_BASE_PATH || '/',
    plugins: [vue()],
    server: {
      port: 5173,
      proxy: {
        '/api': 'http://127.0.0.1:8001'
      }
    }
  }
})
