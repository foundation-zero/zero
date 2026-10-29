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
        exclude: [
          "**/*.spec.ts",
          "**/*.d.ts",
          "components/ui/**",
          "modules/domestic/gql/**",
          "modules/thrapp/mimics/data/**",
          "modules/**/*generated*.ts",
          // Barrels only re-export (enforced by eslint) and type files hold no runtime code.
          "**/*.consts.ts",
          "**/index.ts",
          "**/*.types.ts",
          // Files without logic: types and enums, query documents, route tables and constants.
          "main.ts",
          "settings/keys.ts",
          "modules/**/types/**",
          "modules/**/router/*.ts",
          "modules/**/graphql/queries/**",
          // Mock data for the development mock provider.
          "modules/**/*mock*.ts",
        ],
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
