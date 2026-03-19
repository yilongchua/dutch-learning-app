import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, loadEnv } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig(({ mode }) => {
  // Load env file from the project root (..)
  const env = loadEnv(mode, '../', ''); 

  return {
    plugins: [tailwindcss(), reactRouter(), tsconfigPaths()],
    resolve: {
      dedupe: ['react', 'react-dom', 'react-router'],
    },
    server: {
      host: true,
      port: Number(env.FRONTEND_PORT) || 5173,
      allowedHosts: ['localhost', '.zrok.io'],
    },
  };
});
