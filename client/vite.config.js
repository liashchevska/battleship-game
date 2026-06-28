import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        proxy: {
            '/random-board': {
                target: 'http://server:8000',
                changeOrigin: true
            },
            '/ws': {
                target: 'ws://server:8000',
                ws: true
            }
        }
    }
})