import path from "node:path";
import { fileURLToPath } from "node:url";
import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, loadEnv } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig(({ mode }) => {
  const frontendDir = path.dirname(fileURLToPath(import.meta.url));
  const repoRootDir = path.resolve(frontendDir, "..");

  // Prefer frontend/.env (zrok writes here), then fall back to repo root .env.
  const env = {
    ...loadEnv(mode, repoRootDir, ""),
    ...loadEnv(mode, frontendDir, ""),
  };

  return {
    envDir: frontendDir,
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
