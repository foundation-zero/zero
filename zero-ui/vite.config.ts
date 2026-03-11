import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";
import { defineConfig, loadEnv } from "vite";
import { nodePolyfills } from "vite-plugin-node-polyfills";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const baseEnv = { ...process.env, ...loadEnv(mode, process.cwd()) };
  const testEnv = process.env.PLAYWRIGHT_TEST_BASE_URL ? loadEnv("test", process.cwd()) : {};
  const env = { ...baseEnv, ...testEnv };

  return {
    server: {
      proxy: {
        "/graphql": {
          target: env.VITE_GRAPHQL_SERVER,
          changeOrigin: true,
        },
        "/graphql-ws": {
          target: env.VITE_GRAPHQL_WS_SERVER,
          ws: true,
          rewrite(path) {
            return path.replace(/^\/graphql-ws/, "graphql");
          },
        },
        "/thrs-ws": {
          target: env.VITE_THRS_WS_SERVER,
          ws: true,
          rewrite(path) {
            return path.replace(/^\/thrs-ws/, "");
          },
        },
        "/api/thrs": {
          target: env.VITE_THRS_API_SERVER,
          changeOrigin: true,
          rewrite(path) {
            return path.replace(/^\/api\/thrs/, "");
          },
        },
        "/api/loads": {
          target: env.VITE_LOADS_API_SERVER,
          changeOrigin: true,
          rewrite(path) {
            return path.replace(/^\/api\/loads/, "");
          },
        },
      },
    },
    plugins: [
      vue(),
      tailwindcss(),
      nodePolyfills({
        include: [],
        globals: {
          Buffer: true, // Buffer is used by @apidevtools/json-schema-ref-parser
        },
      }),
    ],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
        "@env": fileURLToPath(new URL("./src/settings", import.meta.url)),
        "@common": fileURLToPath(new URL("./src/modules/common", import.meta.url)),
        "@tests": fileURLToPath(new URL("./tests", import.meta.url)),
        "@components": fileURLToPath(new URL("./src/components/ui", import.meta.url)),
        "@modules": fileURLToPath(new URL("./src/modules", import.meta.url)),
      },
    },
  };
});
