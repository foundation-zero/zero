import vue from "@vitejs/plugin-vue";
import autoprefixer from "autoprefixer";
import { fileURLToPath, URL } from "node:url";
import tailwind from "tailwindcss";
import { defineConfig, loadEnv } from "vite";
import { nodePolyfills } from "vite-plugin-node-polyfills";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = { ...process.env, ...loadEnv(mode, process.cwd()) };

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
      },
    },
    css: {
      postcss: {
        plugins: [tailwind(), autoprefixer()],
      },
    },
    plugins: [
      vue(),
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
        "@tests": fileURLToPath(new URL("./tests", import.meta.url)),
        "@components": fileURLToPath(new URL("./src/components/ui", import.meta.url)),
        "@modules": fileURLToPath(new URL("./src/components/modules", import.meta.url)),
      },
    },
  };
});
