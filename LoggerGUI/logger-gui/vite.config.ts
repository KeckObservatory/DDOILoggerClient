import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

const main = resolve(__dirname, 'index.html')
// const main = '/index.html'
console.log(`main: ${main}`)
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: "./",
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      //external: ["react", "react-router", "react-router-dom", "react-redux"],
       //external: ["react", "react-router", "react-router-dom", "react-redux"],
      input: {
        main: main,
      },
      // output: {
      //   globals: {
      //     react: "React",
      //   },
      // },
    },
  },
})
