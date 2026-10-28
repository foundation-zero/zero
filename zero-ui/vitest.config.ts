import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, import.meta.dirname, "");
  process.env = { ...process.env, ...env };

  return {
    plugins: [vue(), tailwindcss()],
    test: {
      clearMocks: true,
      globals: true,
      environment: "jsdom",
      coverage: {
        provider: "v8",
        include: ["**/*.ts"],
        exclude: ["**/*.spec.ts", "**/*.d.ts", "components/ui/**", "modules/domestic/gql/**"],
        reporter: ["text-summary"],
      },
    },

    root: resolve(import.meta.dirname, "src"),

    resolve: {
      alias: [
        { find: "@", replacement: resolve(import.meta.dirname, "src") },
        { find: "@env", replacement: resolve(import.meta.dirname, "src/settings/index.ts") },
        { find: "@common", replacement: resolve(import.meta.dirname, "src/modules/common") },
        { find: "@tests", replacement: resolve(import.meta.dirname, "tests") },
        { find: "@components", replacement: resolve(import.meta.dirname, "src/components/ui") },
        { find: "@modules", replacement: resolve(import.meta.dirname, "src/modules") },
      ],
    },
  };
});
