import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Manually load env from one level up
  const env = loadEnv(mode, '../')

  return {
    plugins: [react()],
    define: {
      'import.meta.env.VITE_SERVER_IP': JSON.stringify(env.VITE_SERVER_IP),
    },
  }
})
