import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // 允许从任何 IP 访问
    port: 3000,      // 端口号
    strictPort: true, // 如果端口被占用则报错，而不是尝试下一个可用端口
    cors: true,       // 启用 CORS
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
