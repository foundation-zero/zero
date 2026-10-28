import { afterEach, describe, expect, test, vi } from "vitest";

const loadIncludedApps = async (includeApps?: string) => {
  vi.resetModules();
  vi.doMock("./settings", () => ({ ENV: { VITE_INCLUDE_APPS: includeApps } }));

  const { INCLUDED_APPS } = await import("./apps");
  return INCLUDED_APPS;
};

describe("INCLUDED_APPS", () => {
  afterEach(() => {
    vi.doUnmock("./settings");
  });

  test("includes the apps listed in the environment", async () => {
    expect(await loadIncludedApps("thrsim,loads,powerTags")).toEqual([
      "thrsim",
      "loads",
      "powerTags",
    ]);
  });

  test("ignores whitespace, duplicates and unknown apps", async () => {
    expect(await loadIncludedApps(" thrs , unknown,thrs,grafana ")).toEqual(["thrs", "grafana"]);
  });

  test("falls back to the default apps when none are configured", async () => {
    expect(await loadIncludedApps()).toEqual(["loads", "thrs", "domestic"]);
  });

  test("falls back to the default apps when none of the configured apps are valid", async () => {
    expect(await loadIncludedApps("foo,bar")).toEqual(["loads", "thrs", "domestic"]);
  });
});
