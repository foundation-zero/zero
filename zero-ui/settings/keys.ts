export const ENV_KEYS = [
  "VITE_GRAPHQL_URL",
  "VITE_GRAPHQL_SERVER",
  "VITE_GRAPHQL_WS_URL",
  "VITE_GRAPHQL_WS_SERVER",
  "VITE_GRAPHQL_TOKEN",
  "PLAYWRIGHT_TEST_BASE_URL",
  "VITE_DEMO_MODE",
  "VITE_THRS_WS_SERVER",
  "VITE_THRS_API_SERVER",
  "VITE_LOADS_API_SERVER",
  "VITE_LOADS_API_SERVER_URL",
] as const;

export type EnvKey = (typeof ENV_KEYS)[number];

export type ZeroEnv = Record<EnvKey, string>;
