import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

const main = resolve(__dirname, 'index.html')
console.log(`main: ${main}`)
export default defineConfig({
  plugins: [react()],
  root: "./",
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      input: {
        main: main,
      },
    },
  },
})
