import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  schema: {
    [`${process.env.VITE_GRAPHQL_SERVER}${process.env.VITE_GRAPHQL_URL}`]: {
      headers: {
        Authorization: `Bearer ${process.env.VITE_GRAPHQL_TOKEN}`,
      },
    },
  },
  config: {
    namingConvention: { transformUnderscore: true },
  },
  documents: ["src/graphql/**/*.ts", "src/stores/**/*.ts"],
  ignoreNoDocuments: true, // for better experience with the watcher
  generates: {
    "./src/gql/": {
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
