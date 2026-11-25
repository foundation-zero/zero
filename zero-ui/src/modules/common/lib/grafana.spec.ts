import { describe, expect, it } from "vitest";
import { GRAFANA_DASHBOARDS, grafanaUrl } from "./grafana";

describe("grafanaUrl", () => {
  const base = "https://grafana.example.com";

  it("resolves a named dashboard against the Grafana base URL", () => {
    expect(grafanaUrl("commissioning", base)).toBe(`${base}${GRAFANA_DASHBOARDS.commissioning}`);
  });

  it("ignores a trailing slash on the base URL", () => {
    expect(grafanaUrl("hydrogeneration", `${base}/`)).toBe(
      `${base}${GRAFANA_DASHBOARDS.hydrogeneration}`,
    );
  });

  it.each([undefined, "", "unknown", "toString"])("falls back to Grafana home for %o", (name) => {
    expect(grafanaUrl(name, base)).toBe(base);
  });

  it("is empty when Grafana isn't configured", () => {
    expect(grafanaUrl("commissioning", " ")).toBe("");
  });
});
