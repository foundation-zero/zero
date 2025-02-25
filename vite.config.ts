import vue from "@vitejs/plugin-vue";
import autoprefixer from "autoprefixer";
import { fileURLToPath, URL } from "node:url";
import tailwind from "tailwindcss";
import { defineConfig, loadEnv } from "vite";

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
      },
    },
    css: {
      postcss: {
        plugins: [tailwind(), autoprefixer()],
      },
    },
    plugins: [vue()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
  };
});
