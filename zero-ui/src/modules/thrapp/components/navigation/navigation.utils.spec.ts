import { describe, expect, it, vi } from "vitest";
import { reactive } from "vue";
import { RouteLocationNormalizedLoaded } from "vue-router";
import { useThrappNavigation } from "./navigation.utils";

const route = reactive({
  name: "thrs/mimics",
  params: { module: "dhw" } as Record<string, string>,
});

vi.mock(import("vue-router"), async (importOriginal) => ({
  ...(await importOriginal()),
  useRoute: () => route as unknown as RouteLocationNormalizedLoaded,
}));

vi.mock(import("@/modules/thrapp/router/mimics"), async (importOriginal) => ({
  ...(await importOriginal()),
  MIMICS: { dhw: {}, "pvt-owners": {} } as never,
}));

vi.mock(import("@/modules/thrapp/router/parameters"), () => ({
  PARAMETERS: { dhw: {} } as never,
}));

vi.mock(import("@/modules/thrapp/router/documentation"), () => ({
  DOCUMENTATION: { dhw: async () => "", pvt: async () => "" },
}));

const navigate = (name: string, module?: string) => {
  route.name = name;
  route.params = module ? { module } : {};
};

describe("useThrappNavigation", () => {
  it("marks the tab of the current route as active", () => {
    navigate("thrs/control", "dhw");
    const { tabs, documentation } = useThrappNavigation();

    expect(tabs.value.map(({ name, active }) => [name, active])).toEqual([
      ["thrs/mimics", false],
      ["thrs/control", true],
    ]);
    expect(documentation.value.active).toBe(false);
  });

  it("keeps the current module on tabs that have a view for it, else falls back to dhw", () => {
    navigate("thrs/mimics", "pvt-owners");
    const { tabs } = useThrappNavigation();

    expect(tabs.value.map(({ to }) => to)).toEqual([
      { name: "thrs/mimics", params: { module: "pvt-owners" } },
      { name: "thrs/control", params: { module: "dhw" } },
    ]);
  });

  it("links documentation to the current module and marks it active on its own page", () => {
    navigate("thrs/documentation", "pvt");
    const { tabs, documentation } = useThrappNavigation();

    expect(documentation.value).toEqual({
      to: { name: "thrs/documentation", params: { module: "pvt" } },
      active: true,
    });
    expect(tabs.value.some(({ active }) => active)).toBe(false);
  });

  it("falls back to dhw documentation for modules without a manual", () => {
    navigate("thrs/mimics", "pvt-owners");
    const { documentation } = useThrappNavigation();

    expect(documentation.value.to).toEqual({
      name: "thrs/documentation",
      params: { module: "dhw" },
    });
  });

  it("falls back to dhw documentation without a module", () => {
    navigate("thrs");
    const { documentation } = useThrappNavigation();

    expect(documentation.value.to).toEqual({
      name: "thrs/documentation",
      params: { module: "dhw" },
    });
  });
});
