import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  test: {
    clearMocks: true,
    globals: true,
    environment: "jsdom",
  },

  root: resolve(__dirname, "src"),

  resolve: {
    alias: [
      { find: "@", replacement: resolve(__dirname, "src") },
      { find: "@tests", replacement: resolve(__dirname, "tests") },
      { find: "@components", replacement: resolve(__dirname, "src/components/ui") },
      { find: "@modules", replacement: resolve(__dirname, "src/components/modules") },
    ],
  },
});
