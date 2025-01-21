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
    },
  },
  {
    ignores: ["node_modules", ".nuxt", ".output", "dist"],
  },
  // prettier
  prettier,
];
