import vue from "@vitejs/plugin-vue";
import { resolve } from "path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [vue()],
  test: {
    clearMocks: true,
    globals: true,
    environment: "jsdom",
  },

  resolve: {
    alias: [{ find: "@", replacement: resolve(__dirname, "src") }],
  },
});
