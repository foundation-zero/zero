import pluginJs from "@eslint/js";
import vueConfigPrettier from "@vue/eslint-config-prettier";
import vueConfigTypescript from "@vue/eslint-config-typescript";
import prettier from "eslint-plugin-prettier/recommended";
import pluginVue from "eslint-plugin-vue";
import globals from "globals";
import tseslint from "typescript-eslint";

/** @type {import('eslint').Linter.Config[]} */
export default [
  {
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
    },
  },
  pluginJs.configs.recommended,
  {
    rules: {
      "no-unused-vars": [
        "warn",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
      "no-undef": "off",
    },
  },
  ...tseslint.configs.recommended,
  {
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "warn",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
      "@typescript-eslint/no-explicit-any": "warn",
    },
  },
  ...pluginVue.configs["flat/recommended"],
  {
    files: ["**/*.{js,mjs,cjs,ts,vue}"],
    languageOptions: {
      parserOptions: { parser: tseslint.parser },
    },
  },
  {
    rules: {
      ...vueConfigTypescript.rules,
      ...vueConfigPrettier.rules,
      "vue/multi-word-component-names": "off",
      "vue/require-default-prop": "off",
      "@typescript-eslint/no-require-imports": "off",
      // Folders resolve to their index file, so import the folder itself.
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              regex: "/index\\.(ts|js)$",
              message: "Import the folder instead of its index file.",
            },
          ],
        },
      ],
    },
  },
  {
    // Barrel files only re-export, so they need no test coverage. Generated shadcn components, the
    // mimic data aggregates and route records (excluded from coverage as a whole) are exempt.
    files: ["src/**/index.ts"],
    ignores: [
      "src/components/ui/**",
      "src/modules/thrapp/mimics/data/**",
      "src/modules/**/router/**",
    ],
    rules: {
      "no-restricted-syntax": [
        "warn",
        {
          selector: "Program > :not(ExportNamedDeclaration[source], ExportAllDeclaration)",
          message:
            "Barrel files may only re-export. Move types to {name}.types.ts, constants to {name}.consts.ts and logic to {name}.utils.ts.",
        },
      ],
    },
  },
  {
    ignores: ["node_modules", ".nuxt", ".output", "dist", ".vite", "docs/dist", "docs/.vitepress"],
  },
  // prettier
  prettier,
];
