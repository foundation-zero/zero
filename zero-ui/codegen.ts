import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  schema: {
    [`${process.env.VITE_GRAPHQL_SERVER}`]: {
      headers: {
        Authorization: `Bearer ${process.env.VITE_GRAPHQL_TOKEN}`,
      },
    },
  },
  config: {
    namingConvention: { transformUnderscore: true },
  },
  documents: ["src/modules/domestic/graphql/**/*.ts", "src/modules/domestic/stores/**/*.ts"],
  ignoreNoDocuments: true, // for better experience with the watcher
  generates: {
    "./src/modules/domestic/gql/": {
      preset: "client",
      config: {
        useTypeImports: true,
      },
      plugins: [],
    },
  },
  hooks: { afterAllFileWrite: ["eslint --fix"] },
};

export default config;
