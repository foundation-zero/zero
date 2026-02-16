import { EnvKey, ZeroEnv } from "./keys";

const loadEnvFromPublic = async (): Promise<ZeroEnv> => {
  const response = await fetch(`/env.json`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to load env.json (${response.status})`);
  }

  return (await response.json()) as ZeroEnv;
};

const ENV =
  import.meta.env?.MODE === "development" || import.meta.env?.VITEST
    ? import.meta.env
    : await loadEnvFromPublic();

export const env = {
  get: (name: EnvKey): string => ENV[name],
};
